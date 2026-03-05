from enum import Enum
from sys import exit
import sys
import os
import readline


class BuiltinCommands(Enum):
    CD = "cd"
    EXIT = "exit"
    ECHO = "echo"
    TYPE = "type"
    EXEC = "exec"
    PWD = "pwd"
    HISTORY = "history"


def handle_invalid_command(cmd: str):
    sys.stderr.write(f"{cmd}: command not found\n")
    sys.stderr.flush()


def is_builtin_command(cmd_name: str | None) -> bool:
    if not cmd_name:
        return False
    return cmd_name in [bc.value for bc in BuiltinCommands]


def handle_builtin_command(cmd: str, args: list[str]) -> bool:

    match cmd:
        case BuiltinCommands.EXIT.value:
            shell_exit()
        case BuiltinCommands.ECHO.value:
            shell_echo(args)
        case BuiltinCommands.TYPE.value:
            shell_type(args)
        case BuiltinCommands.PWD.value:
            shell_pwd()
        case BuiltinCommands.CD.value:
            shell_cd(args[0] if args else "")
        case BuiltinCommands.HISTORY.value:
            shell_history()
        case _:
            return False
    return True


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
            os.execvp(cmd_abs_path, args)

        else:
            os.waitpid(pid, 0)


def shell_pwd():
    """Prints the shell's current working directory."""
    print(os.getcwd())


def shell_cd(path: str | bytes | os.PathLike[str] | os.PathLike[bytes]):
    expanded_path = os.path.expanduser(path)
    try:
        os.chdir(expanded_path)
    except OSError:
        print(f"cd: {expanded_path}: No such file or directory")


def shell_history(args: list[str]):

    if "-r" in args:
        try:
            i = args.index("-r")
            f = None if i + 1 >= len(args) else args[i + 1]
            readline.read_history_file(f)  # must be a readline-created history file?

        except ValueError:
            pass
        except FileNotFoundError:
            pass
        except OSError:
            pass

        return

    if "-w" in args:
        try:
            i = args.index("-w")
            f = None if i + 1 >= len(args) else args[i + 1]
            readline.write_history_file(f)  # must be a readline-created history file?

        except ValueError:
            pass
        except FileNotFoundError:
            pass
        except OSError:
            pass

        return

    l = readline.get_current_history_length() + 1

    start = int(next(filter(lambda x: x.isnumeric(), args), l))  # history <n>

    # print cmd index and input
    for i in range(l - start, l):  # 1-indexed
        hist_cmd: str | None = readline.get_history_item(
            i
        )  # can return None despite type hinting
        if hist_cmd:
            print(f"{i} {hist_cmd}")
