from enum import Enum, auto


class Code(Enum):
    SUCCESS = auto()
    ID_ERROR = "An ID ERORR:Unable to find todo with ID"
    CONFIG_READ_ERROR = "A CONFIG READ ERORR:Unable to read config file"
    OS_ERROR = "An OS ERROR has occured"
    DB_INIT_ERROR = (
        "A database initialization ERORR:Failed to initialise database"
    )
    DB_WRITE_ERROR = "A database write ERORR:Failed to write from database"
    DB_READ_ERROR = "A database read ERORR:Failed to read from database"
    JSON_ERROR = "A JSON decode ERORR:Failed to decode json"
