# This only runs once via re-sourcing
import sys
import os
import logging
from pprint import pprint
from vimania_uri.vim_.vimania_manager import VimaniaManager

try:
    # import vim  # relevant for debugging, but gives error when run with main
    # noinspection PyUnresolvedReferences
    import vim
except:  # noqa
    print("-E- No vim module available outside vim")
    raise

if int(vim.eval('g:twvim_debug')) == 1:
    LOG_LEVEL = logging.DEBUG
else:
    LOG_LEVEL = logging.INFO

_log = logging.getLogger("vimania-uri")

if not _log.handlers:  # avoid adding multiple handler via re-sourcing
    handler = logging.StreamHandler(sys.stdout)
    handler.setFormatter(logging.Formatter(
        '%(asctime)-15s %(levelname)s %(name)s %(funcName)s:%(lineno)d %(message)s',
        datefmt='%Y-%m-%d %H:%M:%S')
    )
    _log.addHandler(handler)

_log.setLevel(LOG_LEVEL)

# GOTCHA: activates other venvs as well
# this is not necessary any more with proper pythonx installation
if 'VIRTUAL_ENV' in os.environ:
    _log.debug(f"Running in VENV: {os.environ['VIRTUAL_ENV']}")
    project_base_dir = os.environ['VIRTUAL_ENV']
    activate_this = os.path.join(project_base_dir, 'bin/activate_this.py')
    exec(open(activate_this).read(), {'__file__': activate_this})

_log.debug("------------------------------ Begin Python Init -------------------------------")
plugin_root_dir = vim.eval('s:script_dir')
_log.debug(f"{plugin_root_dir=}")
if LOG_LEVEL == logging.DEBUG:
    pprint(sys.path)
    print(f"{sys.version_info=}")
    print(f"{sys.prefix=}")
    print(f"{sys.executable=}")

if int(vim.eval("exists('g:vimania#Extensions')")):
    extensions = vim.eval('g:vimania#Extensions')
    extensions = [ext.strip() for ext in extensions.split(',')]
else:
    extensions = None

xMgr = VimaniaManager(
    plugin_root_dir=plugin_root_dir,
    extensions=extensions,
)

_log.debug("------------------------------ End Python Init -------------------------------")
