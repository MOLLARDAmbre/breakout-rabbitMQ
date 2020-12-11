from enum import IntEnum

class event_type(IntEnum):
    """
    Represents the different types of commands to be forwarded
    """
    MOVE_LEFT = 0
    MOVE_RIGHT = 1
    QUIT = 2
