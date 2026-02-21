from enum import Enum
from sys import exit
import os


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
            found = False
            # not a builtin; check for executable file inside all directories of $PATH
            path_var: list[str] = str(os.environ.get("PATH", [])).split(os.pathsep)
            for a_path in path_var:
                try:
                    if cmd in os.listdir(a_path) and os.access(
                        f"{a_path}/{cmd}", os.X_OK
                    ):
                        # check if file is executable
                        print(f"{cmd} is {a_path}/{cmd}")
                        found = True
                        break

                except FileNotFoundError:
                    # path not on disk; continue
                    continue

            # Unknown command
            if not found:
                print(f"{cmd}: not found")
