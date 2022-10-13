"""Tests for `TodoManager` class."""

import pytest

from todocli import todo_manager as tm


@pytest.fixture
def todo_manager():
    todo_manager = tm.TodoManager()
    yield todo_manager


def test_todo_manager_creation(todo_manager):
    assert isinstance(todo_manager, tm.TodoManager)
