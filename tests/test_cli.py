import configparser

import pytest
from typer.testing import CliRunner

from todocli import __app_name__, __version__, cli, config

runner = CliRunner()


@pytest.fixture
def mock_json_file(tmp_path):
    db_file = tmp_path / "todo.json"
    return db_file


def test_creation():
    """Tests app creation."""
    result = runner.invoke(cli.app)
    assert result.exit_code == 0


def test_version():
    """Tests app shows version."""
    result = runner.invoke(cli.app, ["--version"])
    assert result.exit_code == 0
    assert f"{__app_name__} v{__version__}\n" in result.stdout


def test_version_short_opt():
    """Tests app shows version shorthand."""
    result = runner.invoke(cli.app, ["-v"])
    assert result.exit_code == 0
    assert f"{__app_name__} v{__version__}\n" in result.stdout


def test_version_multiple_opt():
    """Tests app shows version with multiple flags."""
    result = runner.invoke(cli.app, ["--help", "-v"])
    assert result.exit_code == 0
    assert f"{__app_name__} v{__version__}\n" in result.stdout


def test_init_db(mock_json_file):
    result = runner.invoke(cli.app, ["init"], input=f"{mock_json_file}\n")
    assert result.exit_code == 0
    assert f'The to-do database is "{mock_json_file}"' in result.stdout
    cfg = configparser.ConfigParser()
    cfg.read(config.CONFIG_FILE_PATH)
    assert cfg["General"]["database"] == str(mock_json_file)
