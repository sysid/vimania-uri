import pytest

from vimania_uri.bms.handler import delete_twbm
from vimania_uri.md import open_uri
from vimania_uri.md.mdnav import URI


# @pytest.mark.skip(reason="deprecated, will be removed in next release")
class TestSaveTwbm:
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
        mocker.patch("vimania_uri.environment.config.twbm_db_url", new=None)
        mocked = mocker.patch("vimania_uri.md.mdnav.add_twbm", return_value=9999)
        open_uri(URI(uri))
        mocked.assert_not_called()

    @pytest.mark.parametrize(
        ("uri",),
        (("./tests/data/test.md",),),
    )
    def test_do_vimania_with_twbm(self, mocker, uri):
        mocker.patch("vimania_uri.environment.config.twbm_db_url", new="some_uri")
        mocked = mocker.patch("vimania_uri.md.mdnav.add_twbm", return_value=9999)
        open_uri(URI(uri), save_twbm=True, twbm_integrated=True)
        mocked.assert_called_once()

    def test_delete_twbm_not_managed_by_vimania(self, mocker):
        mocker.patch("vimania_uri.environment.config.twbm_db_url", new="test_vimania_uri_twbm.db")
        # mocked_buku = mocker.patch("vimania_uri.bms.handler.BukuDb", autospec=True)
        mocked_buku = mocker.patch("vimania_uri.bms.handler.BukuDb.get_rec_id", return_value=1)
        mocked_buku = mocker.patch("vimania_uri.bms.handler.BukuDb.get_rec_by_id", return_value=(
            1, 'http://example.com', 'example title', ',not-managed,', 'randomdesc', 0))
        urls = delete_twbm("http://example.com")
        assert len(urls) == 1
        assert urls[0][0] == 1
        assert 'http://example.com' in urls[0][1]
        assert 'no deletion' in urls[0][1]
        _ = None
