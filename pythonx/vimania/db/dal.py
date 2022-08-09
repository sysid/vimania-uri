import logging
from datetime import datetime
from enum import IntEnum
from typing import Optional, Sequence

import sqlalchemy as sa
from pure_sql import pure_sql
from pydantic import BaseModel
from sqlalchemy import ForeignKey, create_engine
from sqlalchemy.engine import Connection, Engine

# from twbm.environment import Environment
from vimania.environment import ROOT_DIR

_log = logging.getLogger("vimania-plugin.dal")
logging.getLogger("sqlalchemy.engine").setLevel(logging.DEBUG)

metadata = sa.MetaData()

sim_results_table = sa.Table(
    "vimania_todos",
    metadata,
    sa.Column("id", sa.Integer, primary_key=True),
    sa.Column("parent_id", sa.Integer, ForeignKey("vimania_todos.id"), nullable=True),
    sa.Column("todo", sa.String(), nullable=False, unique=True),
    sa.Column("metadata", sa.String(), default=""),
    sa.Column("tags", sa.String(), default=""),
    sa.Column("desc", sa.String(), default=""),
    sa.Column("path", sa.String(), default=""),
    sa.Column("flags", sa.Integer(), default=0),
    sa.Column(
        "last_update_ts", sa.DateTime(), server_default=sa.func.current_timestamp()
    ),
    sa.Column("created_at", sa.DateTime()),
)


# if not flags are set: value=0, allows boolean operations
class TodoStatus(IntEnum):
    OPEN = 1
    PROGRESS = 2
    DONE = 4
    TODELETE = 8


class Todo(BaseModel):
    id: int = None
    parent_id: int = None
    todo: str = ""
    metadata: str = ""
    tags: str = ",,"
    desc: str = ""
    path: str = ""  # file location
    flags: int = 0  # TodoStatus
    last_update_ts: datetime = datetime.utcnow()
    created_at: datetime = None

    @property
    def split_tags(self) -> Sequence[str]:
        return [tag for tag in self.tags.split(",") if tag != ""]


# noinspection PyPropertyAccess
class DAL:
    _sql_alchemy_db_engine: Engine
    _conn: Connection

    is_simulated_environment: bool

    def __init__(self, env_config: "Environment"):
        self.bm_db_url = env_config.tw_vimania_db_url
        _log.debug(f"Using database: {self.bm_db_url}")

    def __enter__(self):
        self._sql_alchemy_db_engine: Engine = create_engine(self.bm_db_url)
        self._conn = self._sql_alchemy_db_engine.connect()
        return self

    def __exit__(self, exc_type, exc_value, exc_traceback):
        self._conn.close()
        self._sql_alchemy_db_engine.dispose()

    @property
    def conn(self):
        return self._conn

    def get_overall_status(self, id_: int) -> Optional[int]:
        """returns the minimal flag of all children,
        None if no children, or not found
        """
        q = pure_sql.get_query_by_name(
            "get_overall_status", f"{ROOT_DIR}/db/sql/hierarchy.sql"
        )
        result = self.conn.execute(q.sql, id_=id_).all()
        _log.debug(f"{id_=}, {result=}")
        self.conn.connection.commit()
        try:
            return result[0][0]
        except IndexError:
            _log.error(f"Index Error.")
            return None

    def get_depth(self, id_: int) -> int:
        q = pure_sql.get_query_by_name("get_depth", f"{ROOT_DIR}/db/sql/hierarchy.sql")
        result = self.conn.execute(q.sql, id_=id_).all()
        _log.debug(f"{id_=}, {result=}")
        self.conn.connection.commit()
        try:
            return result[0][0]
        except IndexError:
            return 0

    def get_todo_parent(self, id_: int, depth: int) -> Todo:
        q = pure_sql.get_query_by_name(
            "get_todo_parent", f"{ROOT_DIR}/db/sql/hierarchy.sql"
        )
        result = self.conn.execute(q.sql, id_=id_, depth=depth).all()
        assert len(result) == 1, f"Ambigouus parents: {result=}, {id_=}"
        self.conn.connection.commit()
        return result[0]

    def delete_todo(self, id: int) -> int:
        query = """
            delete from vimania_todos where id = :id_
            -- returning *  -- not working!
            ;
        """
        result = self.conn.execute(
            query, id_=id
        )  # TODO: check result and returning clause
        self.conn.connection.commit()
        return result

    def insert_todo(self, todo: Todo) -> int:
        query = """
            -- name: insert_todo<!
            -- record_class: Todo
            insert into vimania_todos (parent_id, todo, metadata, tags, desc, path, flags, created_at)
            values (:parent_id, :todo, :metadata, :tags, :desc, :path, :flags, :created_at)
            returning *;
        """
        q = pure_sql.get_query_by_name("insert_todo", f"{ROOT_DIR}/db/sql/crud.sql")
        result = self.conn.execute(
            q.sql,
            # query,
            parent_id=todo.parent_id,
            todo=todo.todo,
            metadata=todo.metadata,
            tags=todo.tags,
            desc=todo.desc,
            path=todo.path,
            flags=todo.flags,
            created_at=datetime.utcnow(),
        ).lastrowid
        self.conn.connection.commit()
        return result

    def update_todo(self, todo: Todo) -> int:
        query = """
            -- name: update_todo<!
            update vimania_todos
            set parent_id = :parent_id, todo = :todo, metadata = :metadata, tags = :tags, flags = :flags, desc = :desc, path = :path 
            where id = :id
            returning *;
        """
        result = self.conn.execute(
            # q.sql,
            query,
            id=todo.id,
            parent_id=todo.parent_id,
            todo=todo.todo,
            metadata=todo.metadata,
            tags=todo.tags,
            flags=todo.flags,
            desc=todo.desc,
            path=todo.path,
        ).all()
        self.conn.connection.commit()
        # return result  # shows the last used id
        # TODO: handling non existing todo
        return result[0][0]

    def get_todo_by_id(self, id_: int) -> Todo:
        q = pure_sql.get_query_by_name("get_todo_by_id", f"{ROOT_DIR}/db/sql/crud.sql")
        sql_result = self.conn.execute(q.sql, id=id_).all()
        if not sql_result:
            # noinspection PyRedundantParentheses
            return Todo()
        return Todo(**(sql_result[0]))

    def get_todos(self, fts_query: str) -> Sequence[Todo]:
        # Example query
        # noinspection SqlResolve
        if fts_query != "":
            query = """
                -- name: get_todos
                -- record_class: Todo
                select *
                from vimania_todos_fts
                where vimania_todos_fts match :fts_query
                order by rank;
            """
            sql_result = self.conn.execute(query, fts_query=fts_query).all()
        else:  # TODO: make normal query
            query = """
                -- name: get_todos
                -- record_class: Todo
                select *
                from vimania_todos_fts
                order by rank;
            """
            sql_result = self.conn.execute(query, fts_query=fts_query).all()

        if not sql_result:
            # noinspection PyRedundantParentheses
            return (Todo(),)
        return [Todo(**todo) for todo in sql_result]

    def get_related_tags(self, tag: str):
        tag_query = f"%,{tag},%"
        q = pure_sql.get_query_by_name(
            "get_related_tags", f"{ROOT_DIR}/db/sql/crud.sql"
        )
        sql_result = self.conn.execute(
            q.sql,
            tag_query=tag_query,
        ).all()
        return [tags[0] for tags in sql_result]

    def get_all_tags(self):
        # noinspection SqlResolve
        q = pure_sql.get_query_by_name("get_all_tags", f"{ROOT_DIR}/db/sql/crud.sql")
        sql_result = self.conn.execute(q.sql).all()
        return [tags[0] for tags in sql_result]
