import pytest

from todocli import todo_manager as tm


@pytest.fixture
def mock_json_file(tmp_path):
    db_file = tmp_path / "todo.json"
    return db_file


@pytest.fixture
def todo_manager(mock_json_file):
    todo_manager = tm.TodoManager(mock_json_file)
    yield todo_manager
