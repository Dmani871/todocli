from typing import Any, Dict, NamedTuple

from todocli.return_codes import Code


class CurrentTodo(NamedTuple):
    todo: Dict[str, Any]
    code: Code
