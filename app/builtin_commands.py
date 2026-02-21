from enum import Enum
from sys import exit


class BuiltinCommands(Enum):
    CD = "cd"
    EXIT = "exit"


def shell_exit():
    exit(0)


__all__ = ["BuiltinCommands", "shell_exit"]
