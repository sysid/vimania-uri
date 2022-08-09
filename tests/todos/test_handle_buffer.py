import textwrap

import pytest

from vimania.db.dal import TodoStatus, DAL
from vimania.environment import config
from vimania.todos.handle_buffer import VimTodo, Line, handle_it, delete_todo_


# full integration test
@pytest.mark.parametrize(
    ("text", "result"),
    (
            ("- [ ] bla bub ()", "-%13% [ ] bla bub ()"),

            # Bug: trailing single quote
            ("- [ ] bla bub '()'", "-%13% [ ] bla bub '()'"),
            ("'- [ ] invalid single quote'", "'- [ ] invalid single quote'"),

            ("- [b] xxxx: invalid", "- [b] xxxx: invalid"),
            ("[ ] xxxx: invalid", "[ ] xxxx: invalid"),

            ("- [ ] todoa ends () hiere.", "-%13% [ ] todoa ends () hiere."),
            (
                    "- [x] this is a text describing a task",
                    "-%13% [x] this is a text describing a task",
            ),
            ("-%15% [x] this is a non existing task", ""),
            (
                    "- [x] this is a text describing a task %123%",
                    "-%13% [x] this is a text describing a task %123%",
            ),
            ("-%123% [d] should be deleted", ""),
            ("- [D] should be deleted", ""),
            ("   - [ ] bla bub ()", "   -%13% [ ] bla bub ()"),
            ("   - [x] completed task test", "   -%13% [x] completed task test"),
    ),
)
def test_handle_it(dal, text, result):
    lines = text.split("\n")
    new_lines = handle_it(lines, path="testpath")
    new_text = "\n".join(new_lines)
    assert new_text == result


@pytest.mark.parametrize(
    ("text", "result"),
    (
            ("   - [x] completed task test", "   -%13% [x] completed task test"),
    ),
)
def test_handle_write_and_read(dal, text, result):
    # BUG: Complete flag (4) not set, also tested by vader test
    lines = text.split("\n")
    handled_lines = handle_it(lines, path="testpath", read=False)
    new_lines = handle_it(handled_lines, path="testpath", read=True)
    new_text = "\n".join(new_lines)
    assert new_text == result


def test_handle_hierarchy(dal):
    tab = "\t"
    text = textwrap.dedent(
        f"""
    - [ ] x1
    - [ ] xx1
    {tab}- [ ] x2
    {tab}- [ ] x3
    {tab}{tab}- [ ] depth 2
    - [ ] no parent %%123%%
    
    {tab}{tab}- [ ] this should have no parent
    """
    )
    result = textwrap.dedent(
        f"""
    -%13% [ ] x1
    -%14% [ ] xx1
    {tab}-%15% [ ] x2
    {tab}-%16% [ ] x3
    {tab}{tab}-%17% [ ] depth 2
    -%18% [ ] no parent %%123%%
    
    {tab}{tab}-%19% [ ] this should have no parent
    """
    )
    lines = text.split("\n")
    new_lines = handle_it(lines, path="testpath")
    new_text = "\n".join(new_lines)
    assert new_text == result

    with DAL(env_config=config) as dal:
        todo = dal.get_todo_by_id(15)
        assert todo.parent_id == 14

        todo = dal.get_todo_by_id(17)
        assert todo.parent_id == 16

        todo = dal.get_todo_by_id(19)
        assert todo.parent_id == None

    update = textwrap.dedent(
        f"""
    -%13% [ ] x1
    -%14% [ ] xx1
    {tab}-%15% [ ] x2
    {tab}-%16% [ ] x3
    {tab}-%17% [ ] depth 2
    -%18% [ ] no parent %%123%%

    -%18% [ ] this should have no parent
    """
    )
    lines = update.split("\n")
    new_lines = handle_it(lines, path="testpath")
    new_text = "\n".join(new_lines)
    assert new_text == update

    with DAL(env_config=config) as dal:
        todo = dal.get_todo_by_id(17)
        assert todo.parent_id == 14

        todo = dal.get_todo_by_id(19)
        assert todo.parent_id == None


def test_handle_it_code_fence(dal):
    text = textwrap.dedent(
        """
    ```bash
    - [ ] with a todo
    ```
    - [ ] bla bub ()
    """
    )
    result = textwrap.dedent(
        """
    ```bash
    - [ ] with a todo
    ```
    -%13% [ ] bla bub ()
    """
    )
    lines = text.split("\n")
    new_lines = handle_it(lines, path="testpath")
    new_text = "\n".join(new_lines)
    assert new_text == result


def test_delete_todo_(dal):
    text = "- %1% [ ] todo 1"
    id_ = delete_todo_(text, "testpath")
    assert id_ == 1


class TestLine:
    def test_line(self):
        l = Line("-%123% [x] this is a text describing a task ", path="testpath")
        print(l.line)
        assert l.line == l._line

    @pytest.mark.parametrize(
        ("todo_text", "result"),
        (
                (
                        "-%1% [x] todo 1",
                        "-%1% [x] todo 1",
                ),
                (
                        "- [x] this is a text describing a task {t:py,todo}",
                        "-%13% [x] this is a text describing a task {t:py,todo}",
                ),
                (
                        "-%13% [d] this is a text for deletion",
                        None,
                ),
        ),
    )
    def test_handle(self, dal, todo_text, result):
        l = Line(todo_text, path="testpath")
        print(l.line)
        new_line = l.handle()
        _ = None
        assert new_line == result

    def test_handle_update(self, dal):
        todo_text = "- [x] this is a text describing a task"
        l = Line(todo_text, path="testpath")
        new_line = l.handle()  # add to db

        # when soemthing changes
        l.todo.todo = "xxxxxxxxxx"
        new_line = l.handle()
        assert new_line == "-%13% [x] xxxxxxxxxx"

    def test_handle_read_update_buffer(self, dal):
        todo_text = "-%1% [x] this is a text describing a task"
        l = Line(todo_text, path="testpath")
        new_line = l.handle_read()  # update from DB

        assert new_line == "-%1% [ ] todo 1"

    @pytest.mark.parametrize(
        ("text", "result"),
        (
                ("- [ ] bla bub ()", "- [ ] bla bub ()"),
                (
                        "- [x] this is a text describing a task",
                        "- [x] this is a text describing a task",
                ),
                (
                        "- [x] this is a text describing a task %123%",
                        "- [x] this is a text describing a task %123%",
                ),
                ("-%9% [ ] with tags {t:todo,py}", "-%9% [ ] with tags {t:todo,py}"),
        ),
    )
    def test_parse_vim_todo(self, text, result):
        l = Line(text, path="testpath")
        vtd = l.parse_vim_todo()
        _ = None
        assert vtd.vim_line == result


class TestVimTodo:
    def test_status(self):
        vtd = VimTodo(
            raw_code="",
            todo="todo string",
            raw_status="[ ]",
            match_="- [ ] todo string",
        )
        assert vtd.status is TodoStatus.OPEN

    def test_tags(self):
        vtd = VimTodo(
            raw_code="",
            todo="todo string",
            raw_status="[ ]",
            raw_tags="{t:py,todo}",
            match_="- [ ] todo string",
        )
        assert vtd.tags == ["py", "todo"]
        assert vtd.tags_db_formatted == ",py,todo,"
        _ = None
