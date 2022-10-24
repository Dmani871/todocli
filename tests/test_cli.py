import configparser
from unittest.mock import patch

import pytest
from typer.testing import CliRunner

from todocli import __app_name__, __version__, cli, config

from .helper import generate_todos

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


def test_init(mock_json_file):
    result = runner.invoke(
        cli.app,
        ["init"],
        input=f"{mock_json_file}\n",
    )
    assert result.exit_code == 0
    assert f'The to-do database is "{mock_json_file}"' in result.stdout
    cfg = configparser.ConfigParser()
    cfg.read(config.CONFIG_FILE_PATH)
    assert cfg["General"]["database"] == str(mock_json_file)


def test_init_invalid_filepath():
    result = runner.invoke(cli.app, ["init"], input="/\n")
    assert result.exit_code == 1
    assert (
        'Creating config file failed with "An OS ERROR has occured"'
        in result.stdout
    )


@pytest.mark.parametrize(
    "todo_task,todo_priority,todo_due_date_str,return_todo",
    list(generate_todos(1)),
)
def test_add_todo(
    todo_task,
    todo_priority,
    todo_due_date_str,
    return_todo,
    todo_manager,
):
    with patch("todocli.cli.get_todoer") as mock_requests:
        mock_requests.return_value = todo_manager
        result = runner.invoke(
            cli.app,
            [
                "add",
                todo_task,
                "--priority",
                todo_priority,
                "--due",
                todo_due_date_str,
            ],
        )
        assert todo_manager.read_todos() == [return_todo]
        assert result.exit_code == 0


@pytest.mark.parametrize(
    "todo_task,todo_priority,todo_due_date_str,return_todo",
    tuple(generate_todos(1, todo_priority=10))
    + tuple(generate_todos(1, todo_priority=0)),
)
def test_add_todo_priority(
    todo_task,
    todo_priority,
    todo_due_date_str,
    return_todo,
    todo_manager,
):
    with patch("todocli.cli.get_todoer") as mock_requests:
        mock_requests.return_value = todo_manager
        result = runner.invoke(
            cli.app,
            [
                "add",
                todo_task,
                "--priority",
                todo_priority,
                "--due",
                todo_due_date_str,
            ],
        )
        assert (
            f"Error: Invalid value for '--priority': {todo_priority} is not in the valid range of 1 to 3."  # noqa: E501
            in result.stdout
        )
        assert result.exit_code == 2


@pytest.mark.parametrize(
    "todo_task,todo_priority,todo_due_date_str,return_todo",
    tuple(generate_todos(1, todo_priority=1)),
)
def test_add_todo_priority_default(
    todo_task,
    todo_priority,
    todo_due_date_str,
    return_todo,
    todo_manager,
):
    with patch("todocli.cli.get_todoer") as mock_requests:
        mock_requests.return_value = todo_manager
        result = runner.invoke(
            cli.app,
            [
                "add",
                todo_task,
                "--due",
                todo_due_date_str,
            ],
        )
        return_todo["Priority"] = 2
        assert todo_manager.read_todos() == [return_todo]
        assert result.exit_code == 0


@pytest.mark.parametrize(
    "todo_task,todo_priority,todo_due_date_str,return_todo",
    tuple(generate_todos(1, include_due_date=False)),
)
def test_add_todo_wo_due(
    todo_task,
    todo_priority,
    todo_due_date_str,
    return_todo,
    todo_manager,
):
    with patch("todocli.cli.get_todoer") as mock_requests:
        mock_requests.return_value = todo_manager
        result = runner.invoke(
            cli.app,
            ["add", todo_task, "--priority", todo_priority],
        )
        assert result.exit_code == 0
        assert todo_manager.read_todos() == [return_todo]
