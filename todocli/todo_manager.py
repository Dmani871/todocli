from todocli.return_codes import Code


class TodoManager:
    def add(self, description: str, priority: int, due: str):
        return (
            {
                "Description": description,
                "Priority": priority,
                "Due": due,
                "Done": False,
            },
            Code.SUCCESS,
        )
