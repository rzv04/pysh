from enum import Enum
from sys import exit
import os


class BuiltinCommands(Enum):
    CD = "cd"
    EXIT = "exit"
    ECHO = "echo"
    TYPE = "type"
    EXEC = "exec"


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


def search_for_cmd_file(cmd: str) -> str:
    """Search for the absolute path of a command in the $PATH system environment variable.

    Args:
        cmd (str): The command (file) to look for

    Returns:
        str: The absolute path, if it exists, else ""
    """
    # not a builtin; check for executable file inside all directories of $PATH
    path_var: list[str] = str(os.environ.get("PATH", [])).split(os.pathsep)
    for a_path in path_var:
        try:
            if cmd in os.listdir(a_path) and os.access(f"{a_path}/{cmd}", os.X_OK):
                # check if file is executable
                # print(f"{cmd} is {a_path}/{cmd}")
                # break
                return f"{a_path}/{cmd}"

        except FileNotFoundError:
            # path not on disk; continue
            continue
    return ""


def shell_type(args: list[str]):
    """(Partially) Emulates a shell's 'type' builtin command.

    Args:
        args (str): List of arguments, denoting the sequence of commands to be tested.
    """

    for cmd in args:
        if cmd in [bc.value for bc in BuiltinCommands]:
            print(f"{cmd} is a shell builtin")
        else:
            cmd_path = search_for_cmd_file(cmd)
            if cmd_path:
                print(f"{cmd} is {cmd_path}")

            # Unknown command
            else:
                print(f"{cmd}: not found")


def shell_exec(cmd_abs_path: str, args: list[str]):
    """Executes the given external command, if it exists.

    Args:
        cmd (str): The external command's name (not shell builtin) (ls, cd, etc.)
        args (list[str]): The command's argument list
    """

    if cmd_abs_path:
        # fork the process and execute the command
        pid = os.fork()
        if pid == 0:
            # child process
            os.execvp(cmd_abs_path, [cmd_abs_path] + args)  # args[0] is cmd name

        else:
            os.waitpid(pid, 0)
