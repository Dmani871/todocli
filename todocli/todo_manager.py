from todocli.current_todo import CurrentTodo
from todocli.return_codes import Code


class TodoManager:
    def add(
        self, description: str, priority: int, due: str = None
    ) -> CurrentTodo:
        return CurrentTodo(
            {
                "Description": description,
                "Priority": priority,
                "Due": due,
                "Done": False,
            },
            Code.SUCCESS,
        )
