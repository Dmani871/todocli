"""Tests for `TodoManager` class."""

import random

import pytest
from faker import Faker

from todocli import todo_manager as tm
from todocli.current_todo import CurrentTodo
from todocli.return_codes import Code


@pytest.fixture
def todo_manager():
    todo_manager = tm.TodoManager()
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
