import json
from pathlib import Path

from todocli.current_todo import CurrentTodo
from todocli.return_codes import Code


class TodoManager:
    def __init__(self, db_path: Path) -> None:
        self._db_path = db_path

    def add(
        self, description: str, priority: int, due: str = None
    ) -> CurrentTodo:
        """Add todo."""
        todos = self.read_todos()
        todo_json = {
            "Description": description,
            "Priority": priority,
            "Due": due,
            "Done": False,
        }
        todos.append(todo_json)
        self._write_todos(todos)
        return CurrentTodo(
            todo_json,
            Code.SUCCESS,
        )

    def _write_todos(self, todos: list) -> None:
        """Writes todos."""
        with self._db_path.open("w") as db:
            json.dump(todos, db, indent=4)

    def read_todos(self) -> list:
        """Reads todos."""
        with self._db_path.open("r") as db:
            return json.load(db)

    def set_done(self, todo_id: int) -> CurrentTodo:
        """Set a to-do as done."""
        todos = self.read_todos()
        try:
            todo = todos[todo_id - 1]
        except IndexError:
            return CurrentTodo({}, Code.ID_ERROR)
        todo["Done"] = True
        self._write_todos(todos)
        return CurrentTodo(todo, Code.SUCCESS)

    def remove(self, todo_id: int) -> CurrentTodo:
        """Removes todo."""
        todos = self.read_todos()
        try:
            todo = todos.pop(todo_id - 1)
        except IndexError:
            return CurrentTodo({}, Code.ID_ERROR)
        self._write_todos(todos)
        return CurrentTodo(todo, Code.SUCCESS)

    def remove_all(self) -> None:
        """Removes all todos."""
        self._write_todos([])
