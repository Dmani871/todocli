"""Tests for `TodoManager` class."""

import json
import random

import pytest
from faker import Faker

from todocli import todo_manager as tm
from todocli.current_todo import CurrentTodo
from todocli.return_codes import Code


@pytest.fixture
def mock_json_file(tmp_path):
    db_file = tmp_path / "todo.json"
    return db_file


@pytest.fixture
def todo_manager(mock_json_file):
    todo_manager = tm.TodoManager(mock_json_file)
    yield todo_manager


def generate_todos(num, include_due_date=True):
    faker = Faker()
    for _ in range(num):
        todo_task = faker.sentence()
        todo_priority = random.randint(1, 3)
        todo_due_date = faker.date_this_decade(after_today=True)
        todo_due_date_str = (
            todo_due_date.strftime("%Y-%m-%d") if include_due_date else None
        )
        return_todo = {
            "Description": todo_task,
            "Priority": todo_priority,
            "Due": todo_due_date_str,
            "Done": False,
        }
        yield (todo_task, todo_priority, todo_due_date_str, return_todo)


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
