import configparser
from pathlib import Path

from todocli import config
from todocli.return_codes import Code


def test_config_file_created(tmp_path):
    config.CONFIG_DIR_PATH = tmp_path
    config.CONFIG_FILE_PATH = tmp_path / "config.ini"
    assert config._make_config_file() == Code.SUCCESS
    assert config.CONFIG_FILE_PATH.exists()


def test_config_file_not_created():
    config.CONFIG_DIR_PATH = Path("/")
    config.CONFIG_FILE_PATH = Path("/") / "config.ini"
    assert config._make_config_file() == Code.OS_ERROR
    assert config.CONFIG_FILE_PATH.exists() is False


def test_config_file_file_db(tmp_path):
    config.CONFIG_DIR_PATH = tmp_path
    config.CONFIG_FILE_PATH = tmp_path / "config.ini"
    db_path = str(tmp_path / "todo.json")
    assert config._make_config_file() == Code.SUCCESS
    assert config._init_config_file(db_path) == Code.SUCCESS
    cfg = configparser.ConfigParser()
    cfg.read(config.CONFIG_FILE_PATH)
    assert "General" in cfg
    assert cfg["General"] == {"database": db_path}
