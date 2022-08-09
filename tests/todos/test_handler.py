import pytest

from vimania.todos.handler import (
    create_todo_,
    parse_todo_str,
)


@pytest.mark.parametrize(
    ("uri", "todo_status", "todo"),
    (
        ("- [ ] bla blub", 0, "bla blub"),
        ("- [-] bla blub", 1, "bla blub"),
        ("- [x] bla blub", 2, "bla blub"),
        ("- [X] bla blub", 2, "bla blub"),
    ),
)
def test_parse_todo_str(uri, todo_status, todo):
    under_test = parse_todo_str(uri)
    assert under_test.flags == todo_status
    assert under_test.todo == todo
    _ = None


@pytest.mark.parametrize(
    ("uri", "path", "result"),
    (("- [ ] todo 5", "testpath", "two active todos already exist, DB inconsistenty"),),
)
def test_create_invalid_todo_db_inconsistency(uri, path, result):
    with pytest.raises(ValueError):
        create_todo_(uri, path)


@pytest.mark.parametrize(
    ("uri", "path", "result"),
    (("- [ ] todo yyy", "testpath", "new todo"),),
)
def test_create_todo(dal, uri, path, result):
    result = create_todo_(uri, path)
    assert result == 13


# @pytest.mark.parametrize(
#     ("uri", "path", "result"),
#     (("- [ ] todo 6", "testpath", "update existing todo"),),
# )
# def test_update_todo(uri, path, result):
#     create_todo_(uri, path)  # TODO assert missing
