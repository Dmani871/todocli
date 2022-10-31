import configparser
from pathlib import Path
from typing import Union

from todocli.return_codes import Code

CONFIG_DIR_PATH = Path.cwd()
CONFIG_FILE_PATH = CONFIG_DIR_PATH / "config.ini"
DEFAULT_DB_FILE_PATH = CONFIG_DIR_PATH / "todo.json"


def _make_config_file():
    try:
        CONFIG_DIR_PATH.mkdir(exist_ok=True)
        CONFIG_FILE_PATH.touch(exist_ok=True)
    except OSError:
        return Code.OS_ERROR
    return Code.SUCCESS


def _init_config_file(db_path: Path):
    config_parser = configparser.ConfigParser()
    try:
        db_path.parent.mkdir(exist_ok=True)
        db_path.touch(exist_ok=True)
    except OSError:
        return Code.OS_ERROR
    config_parser["General"] = {"database": str(db_path)}
    try:
        with CONFIG_FILE_PATH.open("w") as file:
            config_parser.write(file)
    except OSError:
        return Code.OS_ERROR
    return Code.SUCCESS


def init_database(db_path: Path) -> Code:
    """Create the to-do database."""
    try:
        db_path.write_text("[]")
        return Code.SUCCESS
    except OSError:
        return Code.DB_INIT_ERROR


def init_app(db_path: Path):
    made_config_files = _make_config_file()
    if made_config_files is not Code.SUCCESS:
        return made_config_files
    init_config = _init_config_file(db_path)
    if init_config is not Code.SUCCESS:
        return init_config
    init_db = init_database(db_path)
    if init_db is not Code.SUCCESS:
        return init_db
    return Code.SUCCESS


def get_db_path() -> Union[Path, Code]:
    cfg = configparser.ConfigParser()
    cfg.read(CONFIG_FILE_PATH)
    try:
        return Path(cfg["General"]["database"])
    except KeyError:
        return Code.CONFIG_READ_ERROR
