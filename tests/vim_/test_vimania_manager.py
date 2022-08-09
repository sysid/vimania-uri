import pytest

from vimania.vim_.vimania_manager import split_path


@pytest.mark.parametrize(
    ("args", "path", "suffix"),
    (
        ("/home/user/bla", "/home/user/bla", ""),
        ("/home/user/bla#foo", "/home/user/bla", "foo"),
        ("/home/user/bla.md#foo", "/home/user/bla.md", "#foo"),
        ("/home/user/bla.md#foo##blub", "/home/user/bla.md", "#foo##blub"),
        ("/home/user/bla.md#foo##blub blank", "/home/user/bla.md", "#foo##blub blank"),
    ),
)
def test_split_path(args, path, suffix):
    assert split_path(args) == (path, suffix)
