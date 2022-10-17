from todocli import config
from todocli.return_codes import Code


def test_config_file_created(tmp_path):
    config.CONFIG_DIR_PATH = tmp_path
    config.CONFIG_FILE_PATH = tmp_path / "config.ini"
    assert config._init_config_file() == Code.SUCCESS
    assert config.CONFIG_FILE_PATH.exists()
