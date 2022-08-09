import logging
import os
from pathlib import Path

import pure_sql

import pytest
from alembic import command
from alembic.config import Config

from vimania.db.dal import DAL
from vimania.environment import config, ROOT_DIR

_log = logging.getLogger(__name__)
log_fmt = r"%(asctime)-15s %(levelname)s %(name)s %(funcName)s:%(lineno)d %(message)s"
datefmt = "%Y-%m-%d %H:%M:%S"
logging.basicConfig(format=log_fmt, level=logging.DEBUG, datefmt=datefmt)


@pytest.fixture()
def init_db():
    # TWBM_DB_URL=sqlite:///test/tests_data/bm_test.db
    dsn = os.environ.get(
        "TW_VIMANIA_DB_URL", "sqlite:///tests/data/vimania_todos_test.db"
    )
    (Path(__file__).parent / "data/vimania_todos_test.db").unlink(missing_ok=True)
    alembic_root = Path(__file__).parent.parent / "pythonx/vimania/db"

    alembic_cfg = Config(str(alembic_root / "alembic.ini"))
    alembic_cfg.set_main_option("script_location", str(alembic_root / "alembic"))
    alembic_cfg.set_main_option("sqlalchemy.url", dsn)

    command.upgrade(alembic_cfg, "head")
    _ = None


# TODO: remove aiosql
@pytest.fixture()
def dal(init_db):
    dal = DAL(env_config=config)
    with dal as dal:
        q = pure_sql.get_query_by_name(
            "load_testdata", str(Path(__file__).parent.absolute() / "sql/load_testdata.sql")
        )
        result = dal.conn.execute(q.sql)
        assert result.lastrowid >= 12  # 12 entries in DB expected
        dal.conn.connection.commit()
        yield dal
