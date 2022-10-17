from pathlib import Path

import typer

from todocli import __app_name__
from todocli.return_codes import Code

CONFIG_DIR_PATH = Path(typer.get_app_dir(__app_name__))
CONFIG_FILE_PATH = CONFIG_DIR_PATH / "config.ini"


def _init_config_file():
    try:
        CONFIG_DIR_PATH.mkdir(exist_ok=True)
        CONFIG_FILE_PATH.touch(exist_ok=True)
    except OSError:
        return Code.OS_ERROR
    return Code.SUCCESS
