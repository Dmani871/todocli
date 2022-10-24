"""Tests for `TodoManager` class."""

import json

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
    for todo in generate_todos(10):
        todo_task, todo_priority, todo_due_date_str, _ = todo
        todo_manager.add(todo_task, todo_priority, todo_due_date_str)
    assert len(todo_manager.read_todos()) == 10


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


def test_remove_todos(todo_manager):
    for todo in generate_todos(10):
        todo_task, todo_priority, todo_due_date_str, return_todo = todo
        todo_manager.add(todo_task, todo_priority, todo_due_date_str)
    assert len(todo_manager.read_todos()) == 10
    todo_manager.remove_all()
    assert len(todo_manager.read_todos()) == 0
