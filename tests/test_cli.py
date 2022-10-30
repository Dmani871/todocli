import configparser
import json
from unittest.mock import patch

import pytest
from typer.testing import CliRunner

from todocli import __app_name__, __version__, cli, config
from todocli import todo_manager as tm
from todocli.return_codes import Code

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


@patch("todocli.cli.get_todoer")
@pytest.mark.parametrize(
    "todo_task,todo_priority,todo_due_date_str,return_todo",
    list(generate_todos(1)),
)
def test_add_todo(
    mock_get_todoer,
    todo_task,
    todo_priority,
    todo_due_date_str,
    return_todo,
    todo_manager,
):
    mock_get_todoer.return_value = todo_manager
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
    read_todos, _ = todo_manager.read_todos()
    assert read_todos == [return_todo]
    assert result.exit_code == 0


@patch("todocli.cli.get_todoer")
@pytest.mark.parametrize(
    "todo_task,todo_priority,todo_due_date_str,return_todo",
    tuple(generate_todos(1, todo_priority=10))
    + tuple(generate_todos(1, todo_priority=0)),
)
def test_add_todo_priority(
    mock_get_todoer,
    todo_task,
    todo_priority,
    todo_due_date_str,
    return_todo,
    todo_manager,
):
    mock_get_todoer.return_value = todo_manager
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


@patch("todocli.cli.get_todoer")
@pytest.mark.parametrize(
    "todo_task,todo_priority,todo_due_date_str,return_todo",
    tuple(generate_todos(1, todo_priority=1)),
)
def test_add_todo_priority_default(
    mock_get_todoer,
    todo_task,
    todo_priority,
    todo_due_date_str,
    return_todo,
    todo_manager,
):
    mock_get_todoer.return_value = todo_manager
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
    read_todos, _ = todo_manager.read_todos()
    assert read_todos == [return_todo]
    assert result.exit_code == 0


@patch("todocli.cli.get_todoer")
@pytest.mark.parametrize(
    "todo_task,todo_priority,todo_due_date_str,return_todo",
    tuple(generate_todos(1, include_due_date=False)),
)
def test_add_todo_wo_due(
    mock_get_todoer,
    todo_task,
    todo_priority,
    todo_due_date_str,
    return_todo,
    todo_manager,
):
    mock_get_todoer.return_value = todo_manager
    result = runner.invoke(
        cli.app,
        ["add", todo_task, "--priority", todo_priority],
    )
    read_todos, _ = todo_manager.read_todos()
    assert read_todos == [return_todo]
    assert result.exit_code == 0


@patch("todocli.cli.get_todoer")
def test_todo_saved_multiple(mock_get_todoer, todo_manager):
    expected_todos = []
    mock_get_todoer.return_value = todo_manager
    for todo in generate_todos(10):
        todo_task, todo_priority, todo_due_date_str, return_todo = todo
        runner.invoke(
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
        expected_todos.append(return_todo)
    with todo_manager._db_path.open("r") as db:
        assert list(json.load(db)) == expected_todos


@patch("todocli.cli.get_todoer")
@pytest.mark.parametrize(
    "todo_task,todo_priority,todo_due_date_str,return_todo",
    list(generate_todos(1)),
)
def test_add_todo_success_return(
    mock_get_todoer,
    todo_task,
    todo_priority,
    todo_due_date_str,
    return_todo,
    todo_manager,
):
    mock_get_todoer.return_value = todo_manager
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
    read_todos, _ = todo_manager.read_todos()
    assert read_todos == [return_todo]
    assert result.exit_code == 0
    assert (
        f'to-do: "{todo_task}" was added with priority: {todo_priority}'
        in result.stdout
    )


@patch("todocli.cli.get_todoer")
@patch("todocli.todo_manager.TodoManager.read_todos")
@pytest.mark.parametrize(
    "todo_task,todo_priority,todo_due_date_str,return_todo",
    list(generate_todos(1)),
)
@pytest.mark.parametrize(
    "error_code",
    [Code.DB_READ_ERROR, Code.JSON_ERROR],
)
def test_add_todo_read_error_return(
    mock_read_todos,
    mock_get_todoer,
    todo_task,
    todo_priority,
    todo_due_date_str,
    return_todo,
    todo_manager,
    error_code,
):
    mock_read_todos.return_value = tm.DBResponse([], error_code)
    mock_get_todoer.return_value = todo_manager
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
    assert f'Adding to-do failed with "{error_code.value}"' in result.stdout
    assert result.exit_code == 1


@patch("todocli.cli.get_todoer")
@patch("todocli.todo_manager.TodoManager._write_todos")
@pytest.mark.parametrize(
    "todo_task,todo_priority,todo_due_date_str,return_todo",
    list(generate_todos(1)),
)
def test_add_todo_write_error_return(
    mock_write_todos,
    mock_get_todoer,
    todo_task,
    todo_priority,
    todo_due_date_str,
    return_todo,
    todo_manager,
):
    mock_write_todos.return_value = tm.DBResponse([], Code.DB_WRITE_ERROR)
    mock_get_todoer.return_value = todo_manager
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
        f'Adding to-do failed with "{ Code.DB_WRITE_ERROR.value}"'
        in result.stdout
    )
    assert result.exit_code == 1


@patch("todocli.cli.get_todoer")
@pytest.mark.parametrize(
    "todo_task,todo_priority,todo_due_date_str,return_todo",
    list(generate_todos(1)),
)
def test_set_done_todo(
    mock_get_todoer,
    todo_task,
    todo_priority,
    todo_due_date_str,
    return_todo,
    todo_manager,
):
    mock_get_todoer.return_value = todo_manager
    todo_manager.add(todo_task, todo_priority, todo_due_date_str)
    result = runner.invoke(
        cli.app,
        ["complete", "1"],
    )
    read_todos, _ = todo_manager.read_todos()
    return_todo["Done"] = True
    assert read_todos == [return_todo]
    assert result.exit_code == 0


@patch("todocli.cli.get_todoer")
def test_set_done_todo_invalid_type(
    mock_get_todoer,
    todo_manager,
):
    mock_get_todoer.return_value = todo_manager
    result = runner.invoke(
        cli.app,
        ["complete", "one"],
    )
    assert (
        "Error: Invalid value for 'TODO_ID': one is not a valid integer"
        in result.stdout
    )
    assert result.exit_code == 2


@patch("todocli.cli.get_todoer")
def test_set_todo_done_no_todo(
    mock_get_todoer,
    todo_manager,
):
    mock_get_todoer.return_value = todo_manager
    result = runner.invoke(
        cli.app,
        ["complete", "1"],
    )
    assert (
        f'Completing to-do failed with "{ Code.ID_ERROR.value}"'
        in result.stdout
    )
    assert result.exit_code == 1


@patch("todocli.cli.get_todoer")
@pytest.mark.parametrize(
    "todo_task,todo_priority,todo_due_date_str,return_todo",
    list(generate_todos(1)),
)
def test_set_done_todo_success_return(
    mock_get_todoer,
    todo_task,
    todo_priority,
    todo_due_date_str,
    return_todo,
    todo_manager,
):
    mock_get_todoer.return_value = todo_manager
    todo_manager.add(todo_task, todo_priority, todo_due_date_str)
    result = runner.invoke(
        cli.app,
        ["complete", "1"],
    )
    assert result.exit_code == 0
    assert f'to-do: "{todo_task}" was completed' in result.stdout


@patch("todocli.cli.get_todoer")
@patch("todocli.todo_manager.TodoManager.read_todos")
@pytest.mark.parametrize(
    "error_code",
    [Code.DB_READ_ERROR, Code.JSON_ERROR],
)
def test_set_todo_read_error_return(
    mock_read_todos,
    mock_get_todoer,
    todo_manager,
    error_code,
):
    mock_read_todos.return_value = tm.DBResponse([], error_code)
    mock_get_todoer.return_value = todo_manager
    result = runner.invoke(
        cli.app,
        ["complete", "1"],
    )
    assert (
        f'Completing to-do failed with "{ error_code.value}"' in result.stdout
    )
    assert result.exit_code == 1


@patch("todocli.cli.get_todoer")
@patch("todocli.todo_manager.TodoManager._write_todos")
@patch("todocli.todo_manager.TodoManager.read_todos")
@pytest.mark.parametrize(
    "todo_task,todo_priority,todo_due_date_str,return_todo",
    list(generate_todos(1)),
)
def test_set_done_todo_write_error_return(
    mock_read_todos,
    mock_write_todos,
    mock_get_todoer,
    todo_task,
    todo_priority,
    todo_due_date_str,
    return_todo,
    todo_manager,
):
    mock_read_todos.return_value = tm.DBResponse([return_todo], Code.SUCCESS)
    mock_write_todos.return_value = tm.DBResponse([], Code.DB_WRITE_ERROR)
    mock_get_todoer.return_value = todo_manager

    result = runner.invoke(
        cli.app,
        ["complete", "1"],
    )
    assert (
        f'Completing to-do failed with "{Code.DB_WRITE_ERROR.value}"'
        in result.stdout
    )
    assert result.exit_code == 1


@patch("todocli.cli.get_todoer")
@pytest.mark.parametrize(
    "todo_task,todo_priority,todo_due_date_str,return_todo",
    list(generate_todos(1)),
)
def test_remove_todo(
    mock_get_todoer,
    todo_task,
    todo_priority,
    todo_due_date_str,
    return_todo,
    todo_manager,
):
    mock_get_todoer.return_value = todo_manager
    todo_manager.add(todo_task, todo_priority, todo_due_date_str)
    result = runner.invoke(
        cli.app,
        ["remove", "1"],
    )
    read_todos, _ = todo_manager.read_todos()
    assert read_todos == []
    assert result.exit_code == 0


@patch("todocli.cli.get_todoer")
def test_remove_todo_invalid_type(
    mock_get_todoer,
    todo_manager,
):
    mock_get_todoer.return_value = todo_manager
    result = runner.invoke(
        cli.app,
        ["remove", "one"],
    )
    assert (
        "Error: Invalid value for 'TODO_ID': one is not a valid integer"
        in result.stdout
    )
    assert result.exit_code == 2


@patch("todocli.cli.get_todoer")
def test_remove_done_no_todo(
    mock_get_todoer,
    todo_manager,
):
    mock_get_todoer.return_value = todo_manager
    result = runner.invoke(
        cli.app,
        ["remove", "1"],
    )
    assert (
        f'Removing to-do failed with "{ Code.ID_ERROR.value}"' in result.stdout
    )
    assert result.exit_code == 1


@patch("todocli.cli.get_todoer")
@pytest.mark.parametrize(
    "todo_task,todo_priority,todo_due_date_str,return_todo",
    list(generate_todos(1)),
)
def test_remove_todo_success_return(
    mock_get_todoer,
    todo_task,
    todo_priority,
    todo_due_date_str,
    return_todo,
    todo_manager,
):
    mock_get_todoer.return_value = todo_manager
    todo_manager.add(todo_task, todo_priority, todo_due_date_str)
    result = runner.invoke(
        cli.app,
        ["remove", "1"],
    )
    assert result.exit_code == 0
    assert f'to-do: "{todo_task}" was removed' in result.stdout


@patch("todocli.cli.get_todoer")
@patch("todocli.todo_manager.TodoManager.read_todos")
@pytest.mark.parametrize(
    "error_code",
    [Code.DB_READ_ERROR, Code.JSON_ERROR],
)
def test_remove_read_error_return(
    mock_read_todos,
    mock_get_todoer,
    todo_manager,
    error_code,
):
    mock_read_todos.return_value = tm.DBResponse([], error_code)
    mock_get_todoer.return_value = todo_manager
    result = runner.invoke(
        cli.app,
        ["remove", "1"],
    )
    assert f'Removing to-do failed with "{ error_code.value}"' in result.stdout
    assert result.exit_code == 1


@patch("todocli.cli.get_todoer")
@patch("todocli.todo_manager.TodoManager._write_todos")
@patch("todocli.todo_manager.TodoManager.read_todos")
@pytest.mark.parametrize(
    "todo_task,todo_priority,todo_due_date_str,return_todo",
    list(generate_todos(1)),
)
def test_remove_todo_write_error_return(
    mock_read_todos,
    mock_write_todos,
    mock_get_todoer,
    todo_task,
    todo_priority,
    todo_due_date_str,
    return_todo,
    todo_manager,
):
    mock_read_todos.return_value = tm.DBResponse([return_todo], Code.SUCCESS)
    mock_write_todos.return_value = tm.DBResponse([], Code.DB_WRITE_ERROR)
    mock_get_todoer.return_value = todo_manager

    result = runner.invoke(
        cli.app,
        ["remove", "1"],
    )
    assert (
        f'Removing to-do failed with "{Code.DB_WRITE_ERROR.value}"'
        in result.stdout
    )
    assert result.exit_code == 1


@patch("todocli.cli.get_todoer")
@pytest.mark.parametrize(
    "todo_task,todo_priority,todo_due_date_str,return_todo",
    list(generate_todos(1)),
)
def test_clear(
    mock_get_todoer,
    todo_task,
    todo_priority,
    todo_due_date_str,
    return_todo,
    todo_manager,
):
    mock_get_todoer.return_value = todo_manager
    todo_manager.add(todo_task, todo_priority, todo_due_date_str)
    result = runner.invoke(
        cli.app,
        ["clear"],
    )
    read_todos, _ = todo_manager.read_todos()
    assert read_todos == []
    assert result.exit_code == 0


@patch("todocli.cli.get_todoer")
def test_clear_no_todos(
    mock_get_todoer,
    todo_manager,
):
    mock_get_todoer.return_value = todo_manager
    result = runner.invoke(
        cli.app,
        ["clear"],
    )
    read_todos, _ = todo_manager.read_todos()
    assert read_todos == []
    assert result.exit_code == 0


@patch("todocli.cli.get_todoer")
def test_clear_multiple_todos(
    mock_get_todoer,
    todo_manager,
):
    mock_get_todoer.return_value = todo_manager
    for todo in generate_todos(10):
        todo_task, todo_priority, todo_due_date_str, return_todo = todo
        todo_manager.add(todo_task, todo_priority, todo_due_date_str)
    result = runner.invoke(
        cli.app,
        ["clear"],
    )
    read_todos, _ = todo_manager.read_todos()
    assert read_todos == []
    assert result.exit_code == 0


@patch("todocli.todo_manager.TodoManager._write_todos")
@patch("todocli.cli.get_todoer")
def test_clear_write_error(
    mock_get_todoer,
    mock_write_todos,
    todo_manager,
):
    mock_write_todos.return_value = tm.DBResponse([], Code.DB_WRITE_ERROR)
    mock_get_todoer.return_value = todo_manager
    result = runner.invoke(
        cli.app,
        ["clear"],
    )
    read_todos, _ = todo_manager.read_todos()
    assert read_todos == []
    assert result.exit_code == 1
    assert "Failed to clear to-do database" in result.stdout


@patch("todocli.cli.get_todoer")
def test_clear_success_return(
    mock_get_todoer,
    todo_manager,
):
    mock_get_todoer.return_value = todo_manager

    result = runner.invoke(
        cli.app,
        ["clear"],
    )
    assert result.exit_code == 0
    assert "Cleared all todos" in result.stdout


@patch("todocli.cli.get_todoer")
def test_list_no_todos(
    mock_get_todoer,
    todo_manager,
):
    mock_get_todoer.return_value = todo_manager
    result = runner.invoke(
        cli.app,
        ["list"],
    )
    assert "There are no tasks in the to-do list yet" in result.stdout


@patch("todocli.cli.get_todoer")
@patch("todocli.todo_manager.TodoManager.read_todos")
@pytest.mark.parametrize(
    "error_code",
    [Code.DB_READ_ERROR, Code.JSON_ERROR],
)
def test_list_read_error_return(
    mock_read_todos,
    mock_get_todoer,
    todo_manager,
    error_code,
):
    mock_read_todos.return_value = tm.DBResponse([], error_code)
    mock_get_todoer.return_value = todo_manager
    result = runner.invoke(
        cli.app,
        ["list"],
    )
    assert f'Listing to-do failed with "{ error_code.value}"' in result.stdout
    assert result.exit_code == 1
