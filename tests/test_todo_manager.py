"""Tests for `TodoManager` class."""

import json
from pathlib import Path
from unittest.mock import patch

import pytest

from todocli import todo_manager as tm
from todocli.current_todo import CurrentTodo
from todocli.return_codes import Code

from .helper import generate_todos


def test_todo_manager_creation(todo_manager):
    assert isinstance(todo_manager, tm.TodoManager)


@pytest.mark.parametrize(
    "todo_task,todo_priority,todo_due_date_str,return_todo",
    list(generate_todos(1)),
)
def test_add_todo(
    todo_task, todo_priority, todo_due_date_str, return_todo, todo_manager
):
    todo = todo_manager.add(todo_task, todo_priority, todo_due_date_str)
    assert todo == CurrentTodo(return_todo, Code.SUCCESS)


@pytest.mark.parametrize(
    "todo_task,todo_priority,todo_due_date_str,return_todo",
    list(generate_todos(1)),
)
def test_add_todo_returns_type(
    todo_task, todo_priority, todo_due_date_str, return_todo, todo_manager
):
    todo = todo_manager.add(todo_task, todo_priority, todo_due_date_str)
    assert isinstance(todo, CurrentTodo)


@pytest.mark.parametrize(
    "todo_task,todo_priority,todo_due_date_str,return_todo",
    list(generate_todos(1, False)),
)
def test_add_todo_without_date(
    todo_task, todo_priority, todo_due_date_str, return_todo, todo_manager
):
    todo = todo_manager.add(todo_task, todo_priority, todo_due_date_str)
    assert todo == CurrentTodo(return_todo, Code.SUCCESS)


@pytest.mark.parametrize(
    "todo_task,todo_priority,todo_due_date_str,return_todo",
    list(generate_todos(10)),
)
def test_add_multiple_todo(
    todo_task, todo_priority, todo_due_date_str, return_todo, todo_manager
):
    todo = todo_manager.add(todo_task, todo_priority, todo_due_date_str)
    assert todo == CurrentTodo(return_todo, Code.SUCCESS)


@pytest.mark.parametrize(
    "todo_task,todo_priority,todo_due_date_str,return_todo",
    list(generate_todos(1)),
)
def test_todo_saved(
    todo_task, todo_priority, todo_due_date_str, return_todo, todo_manager
):
    todo_manager.add(todo_task, todo_priority, todo_due_date_str)
    with todo_manager._db_path.open("r") as db:
        assert list(json.load(db)) == [return_todo]


def test_todo_saved_multiple(todo_manager):
    expected_todos = []
    for todo in generate_todos(10):
        todo_task, todo_priority, todo_due_date_str, return_todo = todo
        todo_manager.add(todo_task, todo_priority, todo_due_date_str)
        expected_todos.append(return_todo)
    with todo_manager._db_path.open("r") as db:
        assert list(json.load(db)) == expected_todos


def test_list_todos(todo_manager):
    todos = []
    for todo in generate_todos(10):
        todo_task, todo_priority, todo_due_date_str, return_todo = todo
        todo_manager.add(todo_task, todo_priority, todo_due_date_str)
        todos.append(return_todo)
    read_todos, _ = todo_manager.read_todos()
    assert len(read_todos) == 10
    assert read_todos == todos


def test_write_todos_valid_file(todo_manager):
    res = todo_manager._write_todos([])
    assert res == tm.DBResponse([], Code.SUCCESS)
    with todo_manager._db_path.open("r") as db:
        assert list(json.load(db)) == []


def test_write_todos_invalid_file(todo_manager):
    todo_manager._db_path = Path("/")
    res = todo_manager._write_todos([])
    assert res == tm.DBResponse([], Code.DB_WRITE_ERROR)


def test_list_todos_invalid_file(todo_manager):
    todo_manager._db_path = Path("/")
    res = todo_manager.read_todos()
    assert res == tm.DBResponse([], Code.DB_READ_ERROR)


def test_list_todos_invalid_json(todo_manager):
    with todo_manager._db_path.open("w") as f:
        f.write("[{]")
    res = todo_manager.read_todos()
    assert res == tm.DBResponse([], Code.JSON_ERROR)


@pytest.mark.parametrize(
    "todo_task,todo_priority,todo_due_date_str,return_todo",
    list(generate_todos(1)),
)
def test_add_read_invalid_file(
    todo_task, todo_priority, todo_due_date_str, return_todo, todo_manager
):
    with patch("todocli.todo_manager.TodoManager.read_todos") as mock_requests:
        mock_requests.return_value = tm.DBResponse([], Code.DB_READ_ERROR)
        todo = todo_manager.add(todo_task, todo_priority, todo_due_date_str)
        assert mock_requests.called
        assert todo == CurrentTodo({}, Code.DB_READ_ERROR)


@pytest.mark.parametrize(
    "todo_task,todo_priority,todo_due_date_str,return_todo",
    list(generate_todos(1)),
)
def test_add_write_invalid_file(
    todo_task, todo_priority, todo_due_date_str, return_todo, todo_manager
):
    with patch(
        "todocli.todo_manager.TodoManager._write_todos"
    ) as mock_requests:
        mock_requests.return_value = tm.DBResponse([], Code.DB_WRITE_ERROR)
        todo = todo_manager.add(todo_task, todo_priority, todo_due_date_str)
        assert mock_requests.called
        assert todo == CurrentTodo({}, Code.DB_WRITE_ERROR)


@pytest.mark.parametrize(
    "todo_task,todo_priority,todo_due_date_str,return_todo",
    list(generate_todos(1)),
)
def test_add_invalid_json(
    todo_task, todo_priority, todo_due_date_str, return_todo, todo_manager
):
    with patch("todocli.todo_manager.TodoManager.read_todos") as mock_requests:
        mock_requests.return_value = tm.DBResponse([], Code.JSON_ERROR)
        todo = todo_manager.add(todo_task, todo_priority, todo_due_date_str)
        assert mock_requests.called
        assert todo == CurrentTodo({}, Code.JSON_ERROR)


@pytest.mark.parametrize(
    "todo_task,todo_priority,todo_due_date_str,return_todo",
    list(generate_todos(1)),
)
def test_set_todo_done(
    todo_task, todo_priority, todo_due_date_str, return_todo, todo_manager
):
    todo_manager.add(todo_task, todo_priority, todo_due_date_str)
    todo = todo_manager.set_done(1)
    return_todo["Done"] = True
    assert todo == CurrentTodo(return_todo, Code.SUCCESS)


def test_set_todo_done_no_todo(todo_manager):
    todo = todo_manager.set_done(1)
    assert todo == CurrentTodo({}, Code.ID_ERROR)


@pytest.mark.parametrize(
    "todo_task,todo_priority,todo_due_date_str,return_todo",
    list(generate_todos(1)),
)
def test_set_remove_todo(
    todo_task, todo_priority, todo_due_date_str, return_todo, todo_manager
):
    todo_manager.add(todo_task, todo_priority, todo_due_date_str)
    todo = todo_manager.remove(1)
    assert todo == CurrentTodo(return_todo, Code.SUCCESS)


def test_set_remove_todo_empty(todo_manager):
    todo = todo_manager.remove(1)
    assert todo == CurrentTodo({}, Code.ID_ERROR)


def test_remove_invalid_json(todo_manager):
    with patch("todocli.todo_manager.TodoManager.read_todos") as mock_requests:
        mock_requests.return_value = tm.DBResponse([], Code.JSON_ERROR)
        todo = todo_manager.remove(1)
        assert todo == CurrentTodo({}, Code.JSON_ERROR)


def test_remove_read_invalid_file(todo_manager):
    with patch("todocli.todo_manager.TodoManager.read_todos") as mock_requests:
        mock_requests.return_value = tm.DBResponse([], Code.DB_READ_ERROR)
        todo = todo_manager.remove(1)
        assert todo == CurrentTodo({}, Code.DB_READ_ERROR)


@pytest.mark.parametrize(
    "todo_task,todo_priority,todo_due_date_str,return_todo",
    list(generate_todos(1)),
)
def test_remove_write_invalid_file(
    todo_task, todo_priority, todo_due_date_str, return_todo, todo_manager
):
    todo_manager.add(todo_task, todo_priority, todo_due_date_str)
    with patch(
        "todocli.todo_manager.TodoManager._write_todos"
    ) as mock_requests:
        mock_requests.return_value = tm.DBResponse([], Code.DB_WRITE_ERROR)
        todo = todo_manager.remove(1)
        assert todo == CurrentTodo({}, Code.DB_WRITE_ERROR)


def test_remove_todos(todo_manager):
    for todo in generate_todos(10):
        todo_task, todo_priority, todo_due_date_str, return_todo = todo
        todo_manager.add(todo_task, todo_priority, todo_due_date_str)
    read_todos, _ = todo_manager.read_todos()
    assert len(read_todos) == 10
    todo_manager.remove_all()
    read_todos, _ = todo_manager.read_todos()
    assert len(read_todos) == 0


def test_remove_all_write(todo_manager):
    with patch(
        "todocli.todo_manager.TodoManager._write_todos"
    ) as mock_requests:
        mock_requests.return_value = tm.DBResponse([], Code.DB_WRITE_ERROR)
        todo = todo_manager.remove_all()
        assert todo == CurrentTodo({}, Code.DB_WRITE_ERROR)


def test_set_done_invalid_json(todo_manager):
    with patch("todocli.todo_manager.TodoManager.read_todos") as mock_requests:
        mock_requests.return_value = tm.DBResponse([], Code.JSON_ERROR)
        todo = todo_manager.set_done(1)
        assert todo == CurrentTodo({}, Code.JSON_ERROR)


def test_set_done_read_invalid_file(todo_manager):
    with patch("todocli.todo_manager.TodoManager.read_todos") as mock_requests:
        mock_requests.return_value = tm.DBResponse([], Code.DB_READ_ERROR)
        todo = todo_manager.set_done(1)
        assert todo == CurrentTodo({}, Code.DB_READ_ERROR)


@pytest.mark.parametrize(
    "todo_task,todo_priority,todo_due_date_str,return_todo",
    list(generate_todos(1)),
)
def test_set_done_write_invalid_file(
    todo_task, todo_priority, todo_due_date_str, return_todo, todo_manager
):
    todo_manager.add(todo_task, todo_priority, todo_due_date_str)
    with patch(
        "todocli.todo_manager.TodoManager._write_todos"
    ) as mock_requests:
        mock_requests.return_value = tm.DBResponse([], Code.DB_WRITE_ERROR)
        todo = todo_manager.set_done(1)
        assert todo == CurrentTodo({}, Code.DB_WRITE_ERROR)
