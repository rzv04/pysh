from enum import Enum
from sys import exit


class BuiltinCommands(Enum):
    CD = "cd"
    EXIT = "exit"
    ECHO = "echo"


def shell_exit():
    """Exits the shell."""
    exit(0)


def shell_echo(args: list[str]):
    """Emulates a shell's builtin 'echo' command.

    Args:
        args (list[str]): The arguments, stripped of in-between whitespaces.
    """

    to_print = " ".join(args)
    print(to_print)
