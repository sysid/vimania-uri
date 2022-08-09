import logging
import os
import subprocess
import sys
from pathlib import Path
from typing import Tuple

from vimania.bms.handler import add_twbm
from vimania.environment import config
from vimania.exception import VimaniaException

_log = logging.getLogger("vimania-uri.md")

if sys.platform.startswith("win32"):
    OS_OPEN = "explorer.exe"
elif sys.platform.startswith("linux"):
    OS_OPEN = "xdg-open"
# Linux-specific code here...
elif sys.platform.startswith("darwin"):
    OS_OPEN = "open"
else:
    OS_OPEN = None


def handle(args: str, save_twbm: bool = False) -> str:
    """Handler for protocol URI calls
    save_twbm will be set by vim
    returns the message to display in vim
    """
    return_message = ""  # return message for vim: echom
    if OS_OPEN is None:
        _log.error(f"Unknown OS architecture: {sys.platform}")
        return ""

    if not isinstance(args, str):
        _log.error(f"wrong args type: {type(args)}")
        return f"wrong args type: {type(args)}"

    _log.info(f"{args=}")
    p, return_message = get_fqp(args)

    # https://vim.fandom.com/wiki/User_input_from_a_script

    if save_twbm and config.is_installed_twbm:
        id_ = add_twbm(str(p))
        if id_ != -1:
            return_message = f"new added twbm url: {id_=}"
            _log.debug(f"twbm added: {id_}")

    _log.info(f"Opening: {p}")
    subprocess.run([OS_OPEN, p])
    return return_message


def get_fqp(args: str) -> Tuple[str, str]:
    p = Path.home()  # default setting
    if args.startswith("http"):
        _log.debug(f"Http Link")
        p = args
    # next elif needed to group all possible pathes
    elif (
        args[0] in "/.~$0123456789abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ"
    ):
        if args.startswith("/"):
            _log.debug(f"Absolute path.")
            p = Path(args)
        elif args.startswith("~"):
            _log.debug(f"Path with prefix tilde.")
            p = Path(args).expanduser().absolute()
        elif args.startswith("$"):
            _log.debug(f"Path with environment prefix.")
            p = Path(args)
            env_path = os.getenv(p.parts[0].strip("$"), None)
            if env_path is None:
                _log.warning(f"{p.parts[0]} not set in environment. Cannot proceed.")
                return str(p), f"{p.parts[0]} not set in environment. Cannot proceed."
            p = Path(env_path) / Path(*p.parts[1:])
        else:
            _log.debug(f"Relative path: {args}, working dir: {os.getcwd()}")
            p = Path(args).absolute()

        if not p.exists():
            _log.error(f"{p} does not exists.")
            raise VimaniaException(f"{p} does not exists")
    else:
        _log.error(f"Unknown protocol: {args=}")
        raise VimaniaException(f"Unknown protocol: {args=}")

    return str(p), ""
