import logging
from datetime import datetime
from pathlib import Path
from typing import List, Match, Optional

from pydantic import BaseModel
from vimania.db.dal import DAL, Todo, TodoStatus
from vimania.environment import config
from vimania.pattern import TODO_PATTERN, MatchEnum

_log = logging.getLogger("vimania-plugin.todos.handle_buffer")
ROOT_DIR = Path(__file__).parent.absolute()


class VimTodo(BaseModel):
    raw_code: str = ""
    todo: str = ""
    raw_status: str = " "
    raw_tags: str = ""
    match_: str = ""

    @property
    def status(self) -> TodoStatus:
        status = self.raw_status.strip().strip("[").strip("]").lower()
        if status == " ":
            return TodoStatus.OPEN
        elif status == "-":
            return TodoStatus.PROGRESS
        elif status == "x":
            return TodoStatus.DONE
        elif status == "d":
            return TodoStatus.TODELETE

    # @status.setter
    def set_status(self, value):
        if value == 1:
            self.raw_status = "[ ]"
        elif value == 2:
            self.raw_status = "[-]"
        elif value == 4:
            self.raw_status = "[x]"

    @property
    def tags(self) -> str:
        return (
            self.raw_tags.strip("{t:").strip("}").strip().split(",")
            if self.raw_tags is not None
            else ""
        )

    @property
    def tags_db_formatted(self) -> str:
        return f",{','.join(self.tags)},"

    @property
    def code(self) -> str:
        return self.raw_code.strip("%") if self.raw_code is not None else None

    def add_code(self, code: str) -> "VimTodo":
        self.raw_code = f"%{code}%"
        return self

    @property
    def vim_line(self) -> str:
        return f"-{self.raw_code} {self.raw_status} {self.todo}{self.raw_tags}"


class Line:
    def __init__(self, line, path, running_todos: List["Line"] = None):
        self._line: str = line
        self.is_todo = False
        if running_todos is not None:
            self.running_todos = running_todos
        else:
            self.running_todos = list()
        self.depth: int = 0  # number of tabs (positive number)
        self.parent_id: Optional[int] = None
        self.path: str = path
        self.match: Match = TODO_PATTERN.match(line)
        if self.match is not None:
            self.is_todo = True
            self.todo = self.parse_vim_todo()
            self.depth = self.match.group(MatchEnum.LEVEL).count("\t")
        else:
            self.todo = None
        _ = None

    @property
    def line(self) -> str:
        if self.match is not None:
            _log.debug(f"Match: {self.match}")
            if self.match.group(MatchEnum.FILL1).startswith(" "):
                insert_code = self.todo.raw_code
            else:
                insert_code = f"{self.todo.raw_code} "

            line = (
                # self.match.group(MatchEnum.LEVEL.value)
                f"\t" * abs(self.depth)  # read from db for existing todos
                + self.match.group(MatchEnum.FILL0).rstrip()
                + insert_code
                + self.match.group(MatchEnum.FILL1)
                + self.todo.raw_status
                + self.match.group(MatchEnum.FILL2)
                + self.todo.todo
                + self.todo.raw_tags
            )
            return line
        else:
            return self._line

    def __repr__(self):
        return self.line

    def handle_read(self) -> Optional[str]:
        """handles a vim buffer line in read mode and updates todos from DB

        creation in DB should only happen, if a md-file has been re-initialized. Otherwise, all todos should exist
        with id and only be updated from DB

        returns updated line or None for deletion in buffer
        """
        if self.todo is not None:
            if self.todo.status is TodoStatus.TODELETE:
                raise NotImplementedError("Should not happen.")
                # return None  # remove from vim-buffer
            elif self.todo.code == "":  # should not happen, just in case
                _log.debug(
                    f"Creating [{self.todo.todo}] in read mode. Should only happen when re-initializing a re-set file"
                )
                code = self.create_todo()
                self.todo.add_code(code)
            else:
                todo = self.update_buffer_from_db()  # update from DB
                if todo is None:
                    return None
        return self.line

    def handle(self) -> Optional[str]:
        """handles a vim buffer line

        1. Determines the parent id if applicable
        2. updates the DB accordingly:
            - creates new entry if new todos
            - updates existing entry if changes in existing todos (id unchanged)

        returns updated line or None for deletion in buffer
        """
        if self.todo is not None:
            self.calc_parent_id()
            if self.todo.status is TodoStatus.TODELETE:
                self.delete_todo()
                return None  # remove from vim-buffer
            elif self.todo.code == "":
                code = self.create_todo()
                self.todo.add_code(code)
            else:
                todo = self.update_todo()  # update DB
                if todo is None:
                    return None
        return self.line

    def calc_parent_id(self):
        self.parent_id = None

        with DAL(env_config=config) as dal:
            if len(self.running_todos) > 0:
                prev_line = self.running_todos[-1]
                _log.debug(f"{self=}:{self.depth}, {prev_line=}:{prev_line.depth}")

                if self.depth == 0:  # no parent_id
                    return

                if self.depth > prev_line.depth:
                    self.parent_id = prev_line.todo.code
                elif self.depth == prev_line.depth:
                    todo = dal.get_todo_by_id(prev_line.todo.code)
                    self.parent_id = todo.parent_id
                else:
                    relative_depth = dal.get_depth(prev_line.todo.code)
                    effective_depth = relative_depth + self.depth
                    parent_todo = dal.get_todo_parent(
                        prev_line.todo.code, effective_depth
                    )
                    _log.debug(
                        f"{self.todo}: {relative_depth=}, {effective_depth=}, {parent_todo=}"
                    )
                    self.parent_id = parent_todo.parent_id

    def create_todo(self) -> str:
        todo = Todo(
            parent_id=self.parent_id,
            todo=self.todo.todo,
            path=self.path,
            # flags=TodoStatus.OPEN,
            flags=self.todo.status,
            created_at=datetime.utcnow(),
            tags=self.todo.tags_db_formatted,
        )
        with DAL(env_config=config) as dal:
            todos = dal.get_todos(fts_query=f'"{todo.todo}"')
            if len(todos) >= 1:
                active_todos = [
                    todo
                    for todo in todos
                    if todo.flags < TodoStatus.DONE and todo.id is not None
                ]
                if len(active_todos) > 0:
                    raise ValueError(
                        f"Same active todo already exists: {[td.id for td in active_todos]}. Clear DB inconsistency"
                    )
                else:
                    _log.debug(f"Creating todo: {todo.todo}")
                    id_ = dal.insert_todo(todo)
        return str(id_)

    def delete_todo(self):
        _log.debug(f"{self=}")
        if self.todo.code is None or self.todo.code == "":
            return  # nothing to do, not in DB yet
        with DAL(env_config=config) as dal:
            _log.debug(f"Deleting: {self.todo.code}")
            dal.delete_todo(int(self.todo.code))

    def update_todo(self) -> Optional[Todo]:
        """update existing todo_, if not found in DB delete it in vim-buffer"""
        with DAL(env_config=config) as dal:
            todo = dal.get_todo_by_id(int(self.todo.code))
            if todo.id is None:
                _log.info(f"Cannot update non existing todo: {self.todo.code}")
                _log.info(f"Deleting from vim")
                return None
            todo.todo = self.todo.todo
            todo.flags = self.todo.status
            todo.path = self.path
            todo.parent_id = self.parent_id
            todo.tags = self.todo.tags_db_formatted
            _log.debug(f"Updating in DB: {self.todo}")
            dal.update_todo(todo)
            return todo

    def update_buffer_from_db(self) -> Optional[Todo]:
        """update existing todo_, if not found in DB delete it in vim-buffer"""
        with DAL(env_config=config) as dal:
            todo = dal.get_todo_by_id(int(self.todo.code))
            if todo.id is None:
                _log.info(f"Cannot update non existing todo: {self.todo.code}")
                _log.info(f"Deleting from vim")
                return None
            self.todo.todo = todo.todo
            self.todo.set_status(
                todo.flags
            )  # https://github.com/samuelcolvin/pydantic/issues/1577
            self.depth = dal.get_depth(todo.id)
            _log.debug(f"Updating in buffer: {self.todo}, {self.depth=}")
            return todo

    def parse_vim_todo(self) -> VimTodo:
        match = self.match
        self.todo = VimTodo(
            raw_code=match.group(MatchEnum.CODE) if match.group(MatchEnum.CODE) else "",
            raw_status=match.group(MatchEnum.STATUS),
            todo=match.group(MatchEnum.TODO),
            raw_tags=match.group(MatchEnum.TAGS) if match.group(MatchEnum.TAGS) else "",
            match_=match.group(MatchEnum.ALL),
        )
        return self.todo


def handle_it(lines: List[str], path: str, read: bool = False) -> List[str]:
    new_lines: List[str] = list()
    running_todos: List[Line] = list()
    is_in_code_fence = False

    for _line in lines:

        # do not evaluate text within code fences
        if _line.strip().startswith("```"):
            is_in_code_fence = True if is_in_code_fence is False else False
        if is_in_code_fence:
            new_lines.append(_line)
            continue

        # line = Line(l.strip("'"), path=path, running_todos=running_todos)  # TODO: BUG single quote
        line = Line(_line, path=path, running_todos=running_todos)
        if read:
            new_line = line.handle_read()
        else:
            new_line = line.handle()

        if new_line is not None:
            new_lines.append(new_line)

        if line.is_todo:
            running_todos.append(line)
        else:  # reset
            running_todos = list()

    return new_lines


def delete_todo_(text: str, path: str) -> int:
    line = Line(text.strip("'"), path=path)
    if line.match is None:
        return -1
    line.delete_todo()
    return int(line.todo.code)
