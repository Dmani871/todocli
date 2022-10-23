from enum import Enum, auto


class Code(Enum):
    SUCCESS = auto()
    ID_ERROR = auto()
    OS_ERROR = "An OS ERROR has occured"
    DB_ERROR = auto()
