import re

import pytest
from vimania.md import open_uri
from vimania.md.handler import handle, get_fqp
from vimania.md.mdnav import URI


class TestSaveBm:
    @pytest.mark.parametrize(
        ("uri",),
        (
                # ("/Users/Q187392/dev/vim/vimania/tests/data/vimania.pdf",),
                # ("$HOME/dev/vim/vimania/tests/data/vimania.pdf",),
                # ("/Users/Q187392/dev/vim/vimania/tests/data///vimania.pdf",),
                # ("https://www.google.com",),
                # ("./tests/data/tsl-handshake.png",),
                ("./tests/data/test.md",),
        ),
    )
    def test_do_vimania_without_twbm(self, mocker, uri):
        mocker.patch("vimania.environment.config.twbm_db_url", new=None)
        mocked = mocker.patch("vimania.md.mdnav.add_twbm", return_value=9999)
        open_uri(URI(uri))
        mocked.assert_not_called()

    @pytest.mark.parametrize(
        ("uri",),
        (("./tests/data/test.md",),),
    )
    def test_do_vimania_with_twbm(self, mocker, uri):
        mocker.patch("vimania.environment.config.twbm_db_url", new="some_uri")
        mocked = mocker.patch("vimania.md.mdnav.add_twbm", return_value=9999)
        open_uri(URI(uri), save_twbm=True)
        mocked.assert_called_once()


