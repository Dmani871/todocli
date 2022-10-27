import json
from pathlib import Path
from typing import Any, List, NamedTuple

from todocli.current_todo import CurrentTodo
from todocli.return_codes import Code


class DBResponse(NamedTuple):
    todo_list: List[Any]
    return_code: Code


class TodoManager:
    def __init__(self, db_path: Path) -> None:
        self._db_path = db_path

    def _write_todos(self, todos: list) -> DBResponse:
        """Writes todos."""
        try:
            with self._db_path.open("w") as db:
                json.dump(todos, db, indent=4)
            return DBResponse(todos, Code.SUCCESS)
        except OSError:
            return DBResponse([], Code.DB_WRITE_ERROR)

    def read_todos(self) -> DBResponse:
        """Reads todos."""
        try:
            with self._db_path.open("r") as db:
                try:
                    return DBResponse(json.load(db), Code.SUCCESS)
                except json.JSONDecodeError:
                    return DBResponse([], Code.JSON_ERROR)
        except OSError:
            return DBResponse([], Code.DB_READ_ERROR)

    def add(
        self, description: str, priority: int, due: str = None
    ) -> CurrentTodo:
        """Add todo."""
        todo_json = {
            "Description": description,
            "Priority": priority,
            "Due": due,
            "Done": False,
        }
        todos, read_error = self.read_todos()
        if read_error != Code.SUCCESS:
            return CurrentTodo(todo_json, read_error)
        todos.append(todo_json)
        todos, write_error = self._write_todos(todos)
        if write_error != Code.SUCCESS:
            return CurrentTodo(todo_json, write_error)
        return CurrentTodo(
            todo_json,
            Code.SUCCESS,
        )

    def set_done(self, todo_id: int) -> CurrentTodo:
        """Set a to-do as done."""
        todos, read_error = self.read_todos()
        if read_error != Code.SUCCESS:
            return CurrentTodo({}, read_error)
        try:
            todo = todos[todo_id - 1]
        except IndexError:
            return CurrentTodo({}, Code.ID_ERROR)
        todo["Done"] = True
        self._write_todos(todos)
        return CurrentTodo(todo, Code.SUCCESS)

    def remove(self, todo_id: int) -> CurrentTodo:
        """Removes todo."""
        todos, read_error = self.read_todos()
        if read_error != Code.SUCCESS:
            return CurrentTodo({}, read_error)
        try:
            todo = todos.pop(todo_id - 1)
        except IndexError:
            return CurrentTodo({}, Code.ID_ERROR)
        todos, write_error = self._write_todos(todos)
        if write_error != Code.SUCCESS:
            return CurrentTodo({}, write_error)
        return CurrentTodo(todo, Code.SUCCESS)

    def remove_all(self) -> CurrentTodo:
        """Removes all todos."""
        _, write_error = self._write_todos([])
        if write_error != Code.SUCCESS:
            return CurrentTodo({}, write_error)
        return CurrentTodo({}, Code.SUCCESS)
