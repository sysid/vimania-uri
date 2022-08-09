from __future__ import print_function

import json
import logging
import os.path
import re
import subprocess
import sys
import webbrowser
from dataclasses import dataclass
from pathlib import Path
from typing import Callable, NewType, Optional, Tuple

from vimania.bms.handler import add_twbm
from vimania.environment import config
from vimania.pattern import URL_PATTERN

try:
    from urllib.parse import urlparse
except ImportError:
    # noinspection PyUnresolvedReferences
    from urlparse import urlparse

URI = NewType("URI", str)

_log = logging.getLogger("vimania-plugin.md.mdnav")


@dataclass
class ParsedPath(object):
    path: str
    line: int = None
    anchor: str = None
    scheme: str = None

    @property
    def fullpath(self) -> str:
        if self.scheme is not None:
            return self.path
        return str(Path(os.path.expandvars(self.path)).expanduser().absolute())


def parse_uri(uri: URI) -> ParsedPath:
    """Parse a uri with optional line number of anchor into its parts.

    For example::

        parse_path('foo.md:30') == ParsedPath('foo.md', line=30)
        parse_path('foo.md#anchor') == ParsedPath('foo.md', anchor='anchor')

    """
    line, anchor, ext = None, None, None
    if uri is None:
        return ParsedPath(path="")
    if has_scheme(uri):
        scheme, netloc, p, params, query, fragment = urlparse(uri)
        return ParsedPath(scheme=scheme, path=uri)

    p = Path(uri)
    path = p.stem
    ext = p.suffix
    if "#" in p.suffix:
        ext, anchor = p.suffix.rsplit("#", 1)

    elif ":" in p.suffix:
        ext, line = p.suffix.rsplit(":", 1)

    path = f"{p.parent}/{path}{ext}"
    return ParsedPath(
        path=path,
        line=line,
        anchor=anchor,
    )


def open_uri(target: URI, open_in_vim_extensions: set = None, save_twbm=False) -> Callable:
    """
    :returns: a callable that encapsulates the action to perform
    """
    if open_in_vim_extensions is None:
        open_in_vim_extensions = set()

    if target is not None:
        target = URI(target.strip())

    if not target:
        _log.info("no target")
        return NoOp(target)

    if target.startswith("#"):
        return JumpToAnchor(target)

    if save_twbm and config.is_installed_twbm:
        id_ = add_twbm(str(target))
        if id_ != -1:
            return_message = f"new added twbm url: {id_=}"
            _log.info(f"twbm added: {id_}")

    if has_scheme(target):
        _log.info("has scheme -> open in browser")
        return BrowserOpen(target)

    if not has_extension(target, open_in_vim_extensions):
        _log.info("has no extension for opening in vim")
        return OSOpen(target)

    if target.startswith("|filename|"):
        target = target[len("|filename|"):]

    if target.startswith("{filename}"):
        target = target[len("{filename}"):]

    return VimOpen(target)


def has_extension(path, extensions):
    if not extensions:
        return True  # TODO: Why??

    path = parse_uri(path)
    _, ext = os.path.splitext(path.path)
    return ext in extensions


def has_scheme(target) -> bool:
    scheme, netloc, path, params, query, fragment = urlparse(target)
    if scheme and path.isdigit():
        return False
    # not working with 3.10: https://stackoverflow.com/questions/1737575/are-colons-allowed-in-urls
    # return bool(urlparse(target).scheme)
    return bool(scheme)


@dataclass
class Action:
    target: Optional[URI]


class NoOp(Action):
    def __call__(self):
        print("<mdnav: no link>")


class BrowserOpen(Action):
    def __call__(self):
        print("<mdnav: open browser tab>")
        webbrowser.open_new_tab(self.target)


class OSOpen(Action):
    def __call__(self):
        p = parse_uri(self.target)

        if sys.platform.startswith("linux"):
            call(["xdg-open", p.fullpath])
        elif sys.platform.startswith("darwin"):
            call(["open", p.fullpath])
        else:
            os.startfile(p.fullpath)


class VimOpen(Action):
    def __call__(self):
        # noinspection PyUnresolvedReferences
        import vim

        path = parse_uri(self.target)

        # TODO: make space handling more robust?
        vim.command("e {}".format(path.fullpath.replace(" ", "\\ ")))
        if path.line is not None:
            try:
                line = int(path.line)
            except ValueError:
                print("invalid line number")
                return

            else:
                vim.current.window.cursor = (line, 0)

        if path.anchor is not None:
            JumpToAnchor(URI(path.anchor))()


class JumpToAnchor(Action):
    HEADING_PATTERN = re.compile(r"^#+(?P<title>.*)$")
    ATTR_LIST_PATTERN = re.compile(r"{:\s+#(?P<id>\S+)\s")

    def __call__(self):
        # noinspection PyUnresolvedReferences
        import vim

        line = self.find_anchor(self.target, vim.current.buffer)

        if line is None:
            return

        vim.current.window.cursor = (line + 1, 0)

    @classmethod
    def find_anchor(cls, target, buffer):
        needle = cls.norm_target(target)

        for (idx, line) in enumerate(buffer):
            m = cls.HEADING_PATTERN.match(line)
            if m is not None and cls.title_to_anchor(m.group("title")) == needle:
                return idx

            m = cls.ATTR_LIST_PATTERN.search(line)
            if m is not None and needle == m.group("id"):
                return idx

    @staticmethod
    def title_to_anchor(title):
        return "-".join(fragment.lower() for fragment in title.split())

    @staticmethod
    def norm_target(target):
        if target.startswith("#"):
            target = target[1:]

        return target.lower()


def call(args):
    """If available use vims shell mechanism to work around display issues"""
    try:
        import vim

    except ImportError:
        subprocess.call(args)

    else:
        args = ["shellescape(" + json.dumps(arg) + ")" for arg in args]
        vim.command('execute "! " . ' + ' . " " . '.join(args))


def parse_line(cursor, lines) -> URI | None:
    """Extract URI under cursor from text line"""
    row, column = cursor
    line = lines[row]

    _log.info("handle line %s (%s, %s)", line, row, column)

    # TODO: this only matches last URl in line with several URLs
    m = URL_PATTERN.match(line)
    if m is not None:
        return m.group(1).strip()

    # [.strip_me.](....)
    m = reference_definition_pattern.match(line)
    if m is not None:
        return URI(m.group("link").strip())

    link_text, rel_column = select_from_start_of_link(line, column)

    if not link_text:
        _log.info("could not find link text")
        return None

    m = link_pattern.match(link_text)

    if not m:
        _log.info("does not match link pattern")
        return None

    if m.end("link") <= rel_column:
        _log.info("cursor outside link")
        return None

    _log.info("found match: %s", m.groups())
    assert (m.group("direct") is None) != (m.group("indirect") is None)

    if m.group("direct") is not None:
        _log.info("found direct link: %s", m.group("direct"))
        return m.group("direct")

    _log.info("follow indirect link %s", m.group("indirect"))
    indirect_ref = m.group("indirect")
    if not indirect_ref:
        indirect_ref = m.group("text")

    indirect_link_pattern = re.compile(r"^\[" + re.escape(indirect_ref) + r"\]:(.*)$")

    for line in lines:
        m = indirect_link_pattern.match(line)

        if m:
            return URI(m.group(1).strip())

    _log.info("could not match for indirect link")
    return None


reference_definition_pattern = re.compile(
    r"""
    ^
        \[[^\]]*\]:             # reference def at start of line
        (?P<link>.*)            # interpret everything else as link text
    $
""",
    re.VERBOSE,
)

link_pattern = re.compile(
    r"""
    ^
    (?P<link>
        \[                      # start of link text
            (?P<text>[^\]]*)    # link text
        \]                      # end of link text
        (?:
            \(                  # start of target
                (?P<direct>
                    [^\)]*
                )
            \)                  # collect
            |
            \[
                (?P<indirect>
                    [^\]]*
                )
            \]
        )
    )
    .*                  # any non matching characters
    $
""",
    re.VERBOSE,
)


def select_from_start_of_link(line, pos) -> Tuple[str | None, int]:
    """Return the start of the link string and the new cursor"""
    if pos < len(line) and line[pos] == "[":
        start = pos

    else:
        start = line[:pos].rfind("[")

    # TODO: handle escapes

    if start < 0:
        return None, pos

    # check for indirect links
    if start != 0 and line[start - 1] == "]":
        alt_start = line[:start].rfind("[")
        if alt_start >= 0:
            start = alt_start

    return line[start:], pos - start
