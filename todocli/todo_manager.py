import json
from pathlib import Path

from todocli.current_todo import CurrentTodo
from todocli.return_codes import Code


class TodoManager:
    def __init__(self, db_path: Path) -> None:
        if not db_path.exists():
            db_path.write_text("[]")
        self._db_path = db_path

    def add(
        self, description: str, priority: int, due: str = None
    ) -> CurrentTodo:
        todo_json = {
            "Description": description,
            "Priority": priority,
            "Due": due,
            "Done": False,
        }
        self._write_todos([todo_json])
        return CurrentTodo(
            todo_json,
            Code.SUCCESS,
        )

    def _write_todos(self, todos: list) -> None:
        with self._db_path.open("w") as db:
            json.dump(todos, db, indent=4)
