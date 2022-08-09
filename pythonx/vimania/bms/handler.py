import logging
from typing import Tuple

from vimania.buku import BukuDb
from vimania.environment import config
from vimania.exception import VimaniaException
from vimania.pattern import URL_PATTERN

_log = logging.getLogger("vimania-uri.bms")


def add_twbm(url: str) -> int:
    id_ = BukuDb(dbfile=config.dbfile_twbm).add_rec(
        url=url,
        # title_in=title,
        tags_in=",vimania,",
        # desc=desc,
        # immutable=0,
        delay_commit=False,
        # fetch=(not nofetch),
    )
    if id_ == -1:
        # raise SystemError(f"Error adding {url=} to DB {config.dbfile_twbm}")
        _log.error(
            f"Error adding {url=} to DB {config.dbfile_twbm}"
        )  # TODO: buku.py error handling
    else:
        _log.debug(f"Added twbm: {id_=} - {url} to DB {config.dbfile_twbm}")
    return id_


def delete_twbm(line: str) -> Tuple[int, str]:
    """Delete bookmarks, managed by vimania (tag: vimania)"""
    match = URL_PATTERN.match(line)
    if match is None:
        _log.warning(f"Cannot extract url from: {line}")
        raise VimaniaException(f"Cannot extract url from: {line}")

    url = match.group(1)
    id_ = BukuDb(dbfile=config.dbfile_twbm).get_rec_id(url=url)  # exact match
    if id_ == -1:
        _log.info(f"{url=} not in DB {config.dbfile_twbm}")
        url = ""
    else:
        # (1, 'http://example.com', 'example title', ',tags1,', 'randomdesc', 0))
        bm_var = BukuDb(dbfile=config.dbfile_twbm).get_rec_by_id(id_)

        if "vimania" in bm_var[3]:
            _log.debug(f"Deleting twbm: {url}")
            if not BukuDb(dbfile=config.dbfile_twbm).delete_rec(
                index=id_, delay_commit=False
            ):
                raise VimaniaException(
                    f"Cannot delete {url=} from: {config.dbfile_twbm}"
                )
        else:
            _log.debug(f"{url=} not managed by vimania, no deletion.")
            url = "{url=} not managed by vimania, no deletion."

    return id_, url
