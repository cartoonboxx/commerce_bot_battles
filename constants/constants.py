from enum import Enum

class Status(Enum):
    CREATED = 1
    ENDROUND = 3
    NEXTROUND = 2
    Error = 4
    FINAL = 5