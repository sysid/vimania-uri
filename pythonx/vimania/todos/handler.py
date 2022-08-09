import logging
import re
from datetime import datetime
from typing import Sequence

from vimania.db.dal import DAL, Todo, TodoStatus
from vimania.environment import config
from vimania.md.handler import handle
from vimania.todos.handle_buffer import VimTodo

""" Implementation independent of vim """

_log = logging.getLogger("vimania-plugin.core")


def create_todo_(args: str, path: str) -> int:
    todo = parse_todo_str(args)
    todo.path = path

    with DAL(env_config=config) as dal:
        todos = dal.get_todos(fts_query=todo.todo)
        _ = None
        if len(todos) >= 1:
            active_todos = [todo for todo in todos if todo.flags < TodoStatus.DONE]
            if len(active_todos) > 1:
                raise ValueError(
                    f"Same active todo already exists: {[td.id for td in active_todos]}. Clear DB inconsistency"
                )
            elif len(active_todos) == 1 and active_todos[0].id is not None:
                _log.debug(f"Updating todo: {todo.todo}")
                id_ = dal.update_todo(todo)
            else:
                _log.debug(f"Creating todo: {todo.todo}")
                id_ = dal.insert_todo(todo)
        return id_


def parse_todo_str(args: str) -> Todo:
    pattern = re.compile(r"""(- \[.+])(.*)""", re.MULTILINE)
    todo_status, todo = pattern.findall(args)[0]
    if todo_status == "- [ ]":
        flag = 0
    elif todo_status == "- [-]":
        flag = 1
    elif todo_status == "- [x]" or todo_status == "- [X]":
        flag = 2
    else:
        flag = 99  # unknown status
    todo = Todo(
        todo=todo.strip(),
        flags=flag,
        created_at=datetime.utcnow(),
    )
    return todo


def load_todos_() -> Sequence[str]:
    with DAL(env_config=config) as dal:
        todos = dal.get_todos(fts_query="")
        vtds = list()

        for todo in todos:
            vtd = VimTodo(
                raw_code=f"%%{todo.id}%%",
                todo=todo.todo,
            )
            vtd.set_status(todo.flags)
            vtds.append(vtd)
    return [vtd.vim_line for vtd in vtds]


if __name__ == "__main__":
    arg = "$HOME/dev/vim/vim-textobj-uri/test/vimania//vimania.pdf"
    handle("my-args-given")
