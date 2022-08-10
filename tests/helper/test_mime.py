import pytest

from vimania_uri.helper.mime import get_mime_type


@pytest.mark.parametrize(
    ("uri", "result"),
    (
        ("/Users/Q187392/dev/vim/vimania-todos/tests/data/vimania.pdf", "application/pdf"),
        ("/Users/Q187392/dev/vim/vimania-todos/tests/data/x.html", "text/html"),
        ("/Users/Q187392/dev/vim/vimania-todos/tests/data/tsl-handshake.png", "image/png"),
        ("/Users/Q187392/dev/vim/vimania-todos/tests/data/test.md", "text/plain"),
        ("https://www.google.com", "application/x-msdownload"),
        ("mailto:xxx@bla.com", "application/x-msdownload"),
    ),
)
def test_get_mimetype(uri, result):
    # arg = "$HOME/dev/vim/vim-textobj-uri/test/vimania-todos//vimania-todos.pdf"
    print(get_mime_type(uri))
    assert get_mime_type(uri) == result
