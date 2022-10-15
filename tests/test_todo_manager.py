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


def test_todo_manager_creation(todo_manager):
    assert isinstance(todo_manager, tm.TodoManager)


def test_add_todo(todo_manager):
    faker = Faker()
    todo_task = faker.sentence()
    todo_priority = random.randint(1, 3)
    todo_due_date = faker.date_this_decade(after_today=True)
    todo_due_date_str = todo_due_date.strftime("%Y-%m-%d")
    todo = todo_manager.add(todo_task, todo_priority, todo_due_date_str)
    return_todo = {
        "Description": todo_task,
        "Priority": todo_priority,
        "Due": todo_due_date_str,
        "Done": False,
    }
    assert todo == CurrentTodo(return_todo, Code.SUCCESS)


def test_add_todo_returns_type(todo_manager):
    faker = Faker()
    todo_task = faker.sentence()
    todo_priority = random.randint(1, 3)
    todo_due_date = faker.date_this_decade(after_today=True)
    todo_due_date_str = todo_due_date.strftime("%Y-%m-%d")
    todo = todo_manager.add(todo_task, todo_priority, todo_due_date_str)
    assert isinstance(todo, CurrentTodo)
