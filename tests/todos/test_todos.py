import pytest

from vimania.todos.model import (
    Todos,
    parse_tags,
    check_tags,
    match_all_tags,
    match_any_tag,
    clean_tags,
    match_exact_tags,
)


@pytest.mark.parametrize(
    (
        "fts_query",
        "tags_all",
        "tags_all_not",
        "tags_any",
        "tags_any_not",
        "tags_exact",
        "result",
    ),
    (
        ("", None, None, None, None, "aaa,bbb", 2),
        ("xxxxx", None, None, None, None, None, 1),
        ("xxxxx", "ccc,vimania,yyy", None, None, None, None, 1),
        ("xxxxx", "vimania,yyy", None, None, None, None, 1),
        ("xxxxx", "vimania,yyy", "not1,not2", "vimania", None, "ccc,vimania,yyy", 1),
        ("xxxxx", "wrong", None, None, None, None, 0),
    ),
)
class TestBookmarks:
    def test_search_tags_exact(
        self,
        fts_query,
        tags_all,
        tags_all_not,
        tags_any,
        tags_any_not,
        tags_exact,
        result,
    ):
        todos = Todos(fts_query=fts_query).filter(
            tags_all=tags_all,
            tags_all_not=tags_all_not,
            tags_any=tags_any,
            tags_any_not=tags_any_not,
            tags_exact=tags_exact,
        )
        assert len(todos) == result


@pytest.mark.parametrize(
    ("tags", "result"),
    (
        (("tag1", "tag2"), ",tag1,tag2,"),
        (("tag2", "tag1"), ",tag1,tag2,"),
        ((), ",,"),
    ),
)
def test_parse_tags(tags, result):
    assert parse_tags(tags) == result


@pytest.mark.parametrize(
    ("tags", "result"),
    (
        (("a", "b"), ["a", "b"]),
        (("vimania", "yyy"), []),
        (
            ("vimania", "yyy", "zzz"),
            [
                "zzz",
            ],
        ),
        ((), []),
    ),
)
def test_check_tags(dal, tags, result):
    # res = match_all_tags(('a', 'b'), ('a', 'b', 'c', 'd'))
    unknown_tags = check_tags(tags)
    assert unknown_tags == result
    _ = None


@pytest.mark.parametrize(
    ("tags", "todo_tags", "result"),
    (
        (("a", "b"), ("a", "b", "c", "d"), True),
        (("a", "b"), ("b", "c", "d"), False),
        (("a", "b"), ("b", "a"), True),
        (("a", "b"), ("a",), False),
    ),
)
def test_match_all_tags(tags, todo_tags, result):
    # res = match_all_tags(('a', 'b'), ('a', 'b', 'c', 'd'))
    assert match_all_tags(tags, todo_tags) is result


@pytest.mark.parametrize(
    ("tags", "todo_tags", "result"),
    (
        (("a", "b"), ("a", "b", "c", "d"), True),
        (("a", "b", "x"), ("a", "b", "c", "d"), True),
        (("a", "b", "x"), ("a",), True),
        (("a", "b"), ("x", "y"), False),
    ),
)
def test_match_any_tag(tags, todo_tags, result):
    # res = match_all_tags(('a', 'b'), ('a', 'b', 'c', 'd'))
    assert match_any_tag(tags, todo_tags) is result


def test_match_all(dal):
    todos = dal.get_todos(fts_query="")
    tags = ("aaa", "ccc")
    # filtered = [todo for todo in todos if 'web' in todo.tags.split(',')]
    filtered = [todo for todo in todos if match_all_tags(tags, todo.split_tags)]
    assert len(filtered) >= 1


def test_match_any(dal):
    todos = dal.get_todos(fts_query="")
    tags = ("aaa", "vimania")
    # filtered = [todo for todo in todos if 'web' in todo.tags.split(',')]
    filtered = [todo for todo in todos if match_any_tag(tags, todo.split_tags)]
    assert len(filtered) >= 4


@pytest.mark.parametrize(
    ("tags", "result"),
    (
        (("a", "b"), ["a", "b"]),
        (("b", "a"), ["a", "b"]),
        (("a", ",b"), ["a", "b"]),
        (("a,", ",b"), ["a", "b"]),
        (("a,vimania", ",b"), ["a", "b", "vimania"]),
        ((), []),
        (("a,", ",b", "A"), ["a", "b"]),
        (("a,A", ",b", "A"), ["a", "b"]),
    ),
)
def test_clean_tags(tags, result):
    # res = match_all_tags(('a', 'b'), ('a', 'b', 'c', 'd'))
    assert clean_tags(tags) == result


@pytest.mark.parametrize(
    ("tags", "todo_tags", "result"),
    (
        (("a", "b"), ("a", "b"), True),
        ((), (), True),
        (("a", "b"), ("a",), False),
    ),
)
def test_match_exact_tags(tags, todo_tags, result):
    # res = match_all_tags(('a', 'b'), ('a', 'b', 'c', 'd'))
    assert match_exact_tags(tags, todo_tags) is result
