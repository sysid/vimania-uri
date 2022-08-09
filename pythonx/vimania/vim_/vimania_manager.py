import logging
import tempfile
import traceback
from functools import wraps
from pathlib import Path
from pprint import pprint
from typing import Dict, Tuple

from vimania import md
from vimania.bms.handler import delete_twbm
from vimania.exception import VimaniaException
from vimania.todos.handle_buffer import delete_todo_, handle_it
from vimania.todos.handler import create_todo_, load_todos_
from vimania.vim_ import vim_helper
from vimania.vim_.vim_helper import feedkeys

""" Python VIM Interface Wrapper """

_log = logging.getLogger("vimania-plugin.vimania_manager")
ROOT_DIR = Path(__file__).parent.absolute()

try:
    # import vim  # relevant for debugging, but gives error when run with main
    # noinspection PyUnresolvedReferences
    import vim
except:  # noqa
    _log.debug("No vim module available outside vim")
    pass


def split_path(args: str) -> Tuple[str, str]:
    if "#" not in args:
        return args, ""
    path, *suffix = args.split("#", 1)
    suffix = "".join(suffix)
    if Path(path).suffix == ".md":
        suffix = f"#{suffix}"  # add the leading heading marker back again
    return path, suffix


def err_to_scratch_buffer(func):
    """Decorator that will catch any Exception that 'func' throws and displays
    it in a new Vim scratch buffer."""

    # Gotcha: static function, so now 'self'
    @wraps(func)
    def wrapper(*args, **kwds):
        # noinspection PyBroadException
        try:
            return func(*args, **kwds)
        except Exception as e:  # pylint: disable=bare-except
            msg = """An error occured.

Following is the full stack trace:
"""
            msg += traceback.format_exc()
            vim_helper.new_scratch_buffer(msg)

    return wrapper


def warn_to_scratch_buffer(func):
    """Decorator that will catch any Exception that 'func' throws and displays
    it in a new Vim scratch buffer."""

    # Gotcha: static function, so now 'self'
    @wraps(func)
    def wrapper(*args, **kwds):
        try:
            return func(*args, **kwds)
        except VimaniaException as e:  # pylint: disable=bare-except
            msg = str(e)
            vim_helper.new_scratch_buffer(msg)

    return wrapper


class VimaniaManager:
    def __init__(
        self,
        *,
        extensions=None,
        plugin_root_dir=None,
    ):
        self.extensions = extensions
        self.plugin_root_dir = plugin_root_dir
        _log.debug(f"{extensions=}, {plugin_root_dir=}")

    def __repr__(self):
        return "{self.__class__.__name__}"  # subclassing!

    @staticmethod
    def _get_locals() -> Dict[str, any]:
        locals = {
            "window": vim.current.window,
            "buffer": vim.current.buffer,
            "line": vim.current.window.cursor[0] - 1,
            "column": vim.current.window.cursor[1] - 1,
            "cursor": vim.current.window.cursor,
        }
        if _log.getEffectiveLevel() == logging.DEBUG:
            # print(vim.vars.keys())
            # print(vim.VIM_SPECIAL_PATH)
            # print(vim._get_paths())
            pprint(locals)
        return locals

    @err_to_scratch_buffer
    @warn_to_scratch_buffer
    def call_handle_md2(self, save_twbm: str):
        _log.debug(f"{save_twbm=}")

        row, col = vim.current.window.cursor
        cursor = (row - 1, col)
        lines = vim.current.buffer

        current_file = vim.eval("expand('%:p')"),
        target = md.parse_line(
            cursor, lines
        )
        _log.info(f"open {target=} from {current_file=}")
        action = md.open_uri(
            target,
            open_in_vim_extensions=self.extensions,
            save_twbm=False if int(save_twbm) == 0 else True
        )
        action()

    @staticmethod
    @err_to_scratch_buffer
    @warn_to_scratch_buffer
    def call_handle_md(args: str, save_twbm: str):
        _log.debug(f"{args=}, {save_twbm=}")
        assert isinstance(args, str), f"Error: input must be string, got {type(args)}."

        # https://vim.fandom.com/wiki/User_input_from_a_script
        return_message = md.handle(args, False if int(save_twbm) == 0 else True)
        if return_message != "":
            vim.command(f"echom '{return_message}'")

    @staticmethod
    @err_to_scratch_buffer
    def edit_vimania(args: str):
        """Edits text files and jumps to first position of pattern
        pattern is extracted via separator: '#'
        """
        assert isinstance(args, str), f"Error: input must be string, got {type(args)}."

        path, suffix = split_path(args)
        _log.debug(f"{args=}, {path=}, {suffix=}")
        vim.command(f"tabnew {path}")
        if suffix != "":
            vim.command(f"/{suffix}")

    @staticmethod
    @err_to_scratch_buffer
    def create_todo(args: str, path: str):
        _log.debug(f"{args=}, {path=}")
        locals = VimaniaManager._get_locals()
        assert isinstance(args, str), f"Error: input must be string, got {type(args)}."
        assert isinstance(path, str), f"Error: input must be string, got {type(path)}."
        id_ = create_todo_(args, path)
        vim.command(f"echom 'created/updated: {args} {id_=}'")

    @staticmethod
    @err_to_scratch_buffer
    def load_todos():
        lineno = 10
        # vim_helper.buf[lineno] = vim_helper.buf[lineno].rstrip()
        current = vim.current

        todos = load_todos_()

        temp_path = f"{tempfile.gettempdir()}/todo_tmp.md"
        _log.debug(f"{temp_path=}")

        # scratch buffer
        vim.command(f"edit {temp_path}")
        # vim.command("set buftype=nofile")

        vim.current.buffer[:] = todos

        feedkeys(r"\<Esc>")
        feedkeys(r"\<c-w>\<down>")
        vim.command("set ft=markdown")
        _log.info("Done")

    @staticmethod
    @err_to_scratch_buffer
    def debug():
        current = vim.current

        locals = VimaniaManager._get_locals()
        # add line at end of buffer
        current.buffer[-1:0] = ["New line at end."]

    @staticmethod
    @err_to_scratch_buffer
    def handle_todos(args: str):
        # path = vim.eval("@%")  # relative path
        path = vim.eval("expand('%:p')")
        _log.debug(f"{args=}, {path=}")
        if args == "read":  # autocmd bufread
            new_text = handle_it(vim.current.buffer[:], path, read=True)
        else:  # autocmd bufwrite
            new_text = handle_it(vim.current.buffer[:], path, read=False)

        # Bug: Vista buffer is not modifiable
        is_modifiable = vim.current.buffer.options["modifiable"]
        if is_modifiable:
            vim.current.buffer[:] = new_text
        else:
            _log.warning(
                f"Current buffer {vim.current.buffer.name}:{vim.current.buffer.number} = {is_modifiable=}"
            )

    @staticmethod
    @err_to_scratch_buffer
    def delete_todo(args: str, path: str):
        _log.debug(f"{args=}, {path=}")
        locals = VimaniaManager._get_locals()
        assert isinstance(args, str), f"Error: input must be string, got {type(args)}."
        # id_ = create_todo_(args, path)
        id_ = delete_todo_(args, path)
        vim.command(f"echom 'deleted: {args} {id_=}'")

    @staticmethod
    # https://github.com/vim/vim/issues/6017: cannot create error buffer
    # @err_to_scratch_buffer
    # @warn_to_scratch_buffer
    def delete_twbm(args: str):
        _log.debug(f"{args=}")
        assert isinstance(args, str), f"Error: input must be string, got {type(args)}."
        try:
            id_, url = delete_twbm(args)
        except VimaniaException as e:
            vim.command(
                f"echohl WarningMsg | echom 'Cannot extract url from: {args}' | echohl None"
            )
            return
        vim.command(f"echom 'deleted twbm: {url} {id_=}'")

    @staticmethod
    @err_to_scratch_buffer
    def throw_error(args: str, path: str):
        _log.debug(f"{args=}, {path=}")
        raise Exception(f"Exception Test")
