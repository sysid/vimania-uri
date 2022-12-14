import os
from pathlib import Path

import pytest

from vimania_uri.environment import ROOT_DIR
from vimania_uri.md import mdnav
from vimania_uri.md.mdnav import URI

# NOTE: the cursor is indicated with ^, the cursor will be placed on the
# following character
parse_link_cases = [
    # default cases
    (["foo ^[bar](baz.md)"], "baz.md"),
    (["foo [b^ar](baz.md)"], "baz.md"),
    (["foo [b^ar](baz.md) [bar](bar.md)"], "baz.md"),
    (["foo [b^ar][bar]", "[bar]: baz.md"], "baz.md"),
    (["foo [b^ar][bar]", "[bar]: |filename|./baz.md"], "|filename|./baz.md"),
    (["foo [b^ar][bar] [bar][baz]", "[bar]: |filename|./baz.md"], "|filename|./baz.md"),
    (["foo [b^ar][bar] [bar][baz]", "[bar]: {filename}./baz.md"], "{filename}./baz.md"),
    # empty link target
    (["foo [b^ar][]", "[bar]: baz.md"], "baz.md"),
    (["foo [@b^ar][]", "[@bar]: baz.md"], "baz.md"),
    (["foo [^@bar][]", "[@bar]: baz.md"], "baz.md"),
    # cursor outside link area
    (["foo^  [bar](baz.md) "], None),
    (["foo ^ [bar](baz.md) "], None),
    (["foo [bar](baz.md) ^ "], None),
    (["foo [bar](baz.md)^  "], None),
    # cursor inside target part
    (["foo [bar][b^ar]", "[bar]: baz.md"], "baz.md"),
    (["foo [bar](b^az.md) [bar](bar.md)"], "baz.md"),
    (["foo [bar](baz.md) [bar](^bar.md)"], "bar.md"),
    # malformed links
    (["][b^ar](bar.md)"], "bar.md"),
    # empty line
    (["^"], None),
    # multiple [] pairs across multiple lines (reference style links)
    (["- [ ] checkout [la^bel][target] abs", "[target]: example.com"], "example.com"),
    (["- [ ] checkout [label]^[target] abs", "[target]: example.com"], "example.com"),
    (["- [ ] checkout [label][tar^get] abs", "[target]: example.com"], "example.com"),
    # reference definitions
    (["[f^oo]: test.md"], "test.md"),
    (["[foo]: test.md^"], "test.md"),
    (["[foo]: ^test.md"], "test.md"),
    (["^[foo]: test.md"], "test.md"),
    # blank URLs
    (["https://^www.google.com"], "https://www.google.com"),
    (
        ["some other stuff, not &%$ https://^www.google.com   .. and more"],
        "https://www.google.com",
    ),
    # With Variables
    (["[md-doc]($HO^ME/vimwiki/help.md)"], "$HOME/vimwiki/help.md"),
]


@pytest.mark.parametrize("lines, expected", parse_link_cases)
def test_parse_line(lines, expected):
    cursor, mod_lines = _find_cursor(lines)
    actual = mdnav.parse_line(cursor, mod_lines)
    assert actual == expected


def _find_cursor(lines):
    lines_without_cursor = []
    cursor = None

    for (row, line) in enumerate(lines):
        pos = line.find("^")

        if pos < 0:
            lines_without_cursor.append(line)

        else:
            cursor = (row, pos)
            lines_without_cursor.append(line[:pos] + line[pos + 1 :])

    return cursor, lines_without_cursor


open_uri_cases = [
    (None, {}, mdnav.NoOp(None)),
    ("baz.md", {}, mdnav.VimOpen(URI("baz.md"))),
    ("baz.md:20", {}, mdnav.VimOpen(URI("baz.md:20"))),
    ("baz.MD", {"open_in_vim_extensions": [".md"]}, mdnav.OSOpen(URI("baz.MD"))),
    ("baz.md", {"open_in_vim_extensions": [".md"]}, mdnav.VimOpen(URI("baz.md"))),
    ("baz.md:20", {"open_in_vim_extensions": [".md"]}, mdnav.VimOpen(URI("baz.md:20"))),
    ("|filename|/foo/baz.md", {}, mdnav.VimOpen(URI("/foo/baz.md"))),
    ("{filename}/foo/baz.md", {}, mdnav.VimOpen(URI("/foo/baz.md"))),
    ("/foo/bar.md", {}, mdnav.VimOpen(URI("/foo/bar.md"))),
    ("http://example.com", {}, mdnav.BrowserOpen(URI("http://example.com"))),
    (
        "http://example.com",
        {"open_in_vim_extensions": [".md"]},
        mdnav.BrowserOpen(URI("http://example.com")),
    ),
]


@pytest.mark.parametrize("target, open_link_kwargs, expected", open_uri_cases)
def test_open_link(target, open_link_kwargs, expected):
    actual = mdnav.open_uri(URI(target), **open_link_kwargs)
    assert actual == expected


jump_to_anchor_cases = [
    ("#foo", ["a", "# foo", "b"], 1),
    ("#foo-bar-baz", ["a", "#  Foo  BAR  Baz", "b"], 1),
    # be more lenient and allow not only anchors but also headings
    (
        "Battle of the datacontainers, Serialization",
        ["a", "### Battle of the datacontainers, Serialization", "b"],
        1,
    ),
    (
        "Battle of the datacontainers Serialization",
        ["a", "### Battle of the datacontainers, Serialization", "b"],
        1,
    ),
    (
        "Battle of the datacontainers, Serialization",
        ["a", "### Battle of the datacontainers, Serialization and more", "b"],
        1,
    ),
    ("#foo", ["a", "#  Bar", "b"], None),
    ("#Foo-Bar-Baz", ["a", "### Foo Bar Baz", "b"], 1),
    # use attr-lists to define custom ids
    ("#hello-world", ["a", "### Foo Bar Baz {: #hello-world } ", "b"], 1),
    # first match wins
    ("#hello-world", ["# hello world", "### Foo Bar Baz {: #hello-world } ", "b"], 0),
]


@pytest.mark.parametrize("target, buffer, expected", jump_to_anchor_cases)
def test_jump_to_anchor(target, buffer, expected):
    actual = mdnav.JumpToAnchor.find_anchor(target, buffer)
    assert actual == expected


@pytest.mark.parametrize(
    "path, expected_path, expected_line, expected_anchor, expected_scheme, expected_fullpath",
    [
        (None, "", None, None, None, ""),
        (
            "foo.md",
            "./foo.md",
            None,
            None,
            None,
            str(ROOT_DIR.parent.parent / "foo.md"),
        ),
        ("foo:bar.md", "foo:bar.md", None, None, "foo", "foo:bar.md"),
        (
            "foo.md:30",
            "./foo.md",
            "30",
            None,
            None,
            str(ROOT_DIR.parent.parent / "foo.md"),
        ),
        (
            "foo.md#hello-world",
            "./foo.md",
            None,
            "hello-world",
            None,
            str(ROOT_DIR.parent.parent / "foo.md"),
        ),
        (
            "foo.md#happy:)",
            "./foo.md",
            None,
            "happy:)",
            None,
            str(ROOT_DIR.parent.parent / "foo.md"),
        ),
        (
            "/home/xxx/foo.md#hello-world",
            "/home/xxx/foo.md",
            None,
            "hello-world",
            None,
            "/home/xxx/foo.md",
        ),
        (
            "~/foo.md#hello-world",
            "~/foo.md",
            None,
            "hello-world",
            None,
            str(Path.home() / "foo.md"),
        ),
        (
            "https://www.google.com/bla/blub",
            "https://www.google.com/bla/blub",
            None,
            None,
            "https",
            "https://www.google.com/bla/blub",
        ),
        ("xxx://aything", "xxx://aything", None, None, "xxx", "xxx://aything"),
        (
            "./xxx://yyy",
            "xxx:/yyy",
            None,
            None,
            None,
            str(ROOT_DIR.parent.parent / "xxx:/yyy"),
        ),
        (
            "./xxx/yyy",
            "xxx/yyy",
            None,
            None,
            None,
            str(ROOT_DIR.parent.parent / "xxx/yyy"),
        ),
    ],
)
def test_parse_uri(
    path,
    expected_path,
    expected_line,
    expected_anchor,
    expected_scheme,
    expected_fullpath,
):
    path = mdnav.parse_uri(path)

    assert path.path == expected_path
    assert path.line == expected_line
    assert path.anchor == expected_anchor
    assert path.scheme == expected_scheme
    assert path.fullpath == expected_fullpath


def test_full_path(mocker):
    _ = mocker.patch.dict(os.environ, {"HOME": "/home/xxx"}, clear=True)
    path = mdnav.parse_uri("~/foo.md#hello-world")
    assert path.fullpath == "/home/xxx/foo.md"

    _ = mocker.patch.dict(os.environ, {"XXX": "/xxx"}, clear=True)
    path = mdnav.parse_uri("$XXX/foo.md#hello-world")
    assert path.fullpath == "/xxx/foo.md"

    path = mdnav.parse_uri("$XXX_NOT_EXIST/foo.md#hello-world")
    assert "$XXX_NOT_EXIST/foo.md" in path.fullpath
