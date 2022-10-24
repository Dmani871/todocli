import random

import pytest
from faker import Faker

from todocli import todo_manager as tm


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