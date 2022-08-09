import os

from vimania.environment import config


class TestTwbmIntegration:
    def test_twbm_not_installed(self, mocker):
        mocker.patch("vimania.environment.config.twbm_db_url", new=None)
        print(config.dbfile_twbm)
        assert config.dbfile_twbm is None
        assert not config.is_installed_twbm

    def test_twbm_installed(self, mocker):
        mocker.patch("vimania.environment.config.twbm_db_url", new="something")
        print(config.dbfile_twbm)
        assert config.dbfile_twbm == "something"
        assert config.is_installed_twbm
