from enum import Enum
from sys import exit


class BuiltinCommands(Enum):
    CD = "cd"
    EXIT = "exit"
    ECHO = "echo"
    TYPE = "type"


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


def shell_type(args: list[str]):
    """(Partially) Emulates a shell's 'type' builtin command.

    Args:
        args (str): List of arguments, denoting the sequence of commands to be tested.
    """

    for cmd in args:
        if cmd in [bc.value for bc in BuiltinCommands]:
            print(f"{cmd} is a shell builtin")
        else:
            # TODO handle other commands
            # Unknown command
            print(f"{cmd}: not found")
