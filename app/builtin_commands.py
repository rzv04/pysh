from enum import Enum
from sys import exit
import sys
import os

# import readline
from prompt_toolkit.history import FileHistory
from app.shell_context import ShellContext


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


def shell_exit(status: int):
    """Exits the shell.

    Since history is saved line by line on disk every time,
    it should already be updated without explicitly appending to the history file.
    """
    exit(status)


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


def shell_history(args: list[str]) -> int:
    """A builtin command similar to Bash's 'history' command.

    Currently, the history shows up in reversed order compared to Bash's version (most recent items first)

    Args:
        args (list[str]): Arguments to be received by the command.

    Returns:
        int: The number of added history items to the history file (if any).
    """
    l = len(list(ShellContext.history.load_history_strings()))

    if "-r" in args:
        try:
            i = args.index("-r")
            f = None if i + 1 >= len(args) else args[i + 1]
            if f:
                ShellContext.history = FileHistory(f)

            return 0

        except ValueError:
            pass
        except FileNotFoundError:
            pass
        except OSError:
            pass

        return 0

    if "-w" in args:
        try:
            i = args.index("-w")
            f = None if i + 1 >= len(args) else args[i + 1]
            if f:
                # Overwrite the target file with the current history, matching
                # readline.write_history_file semantics.
                try:
                    with open(f, "w", encoding="utf-8") as hist_file:
                        for line in ShellContext.history.load_history_strings():
                            # Ensure each history entry is written on its own line.
                            if line.endswith("\n"):
                                hist_file.write(line)
                            else:
                                hist_file.write(line + "\n")
                except OSError:
                    # On write error, indicate that nothing was successfully recorded.
                    return 0
                return l

            return 0

        except ValueError:
            pass
        except FileNotFoundError:
            pass
        except OSError:
            pass

        return l

    if "-a" in args:
        # append current history length - last appended items to history file
        filename = (
            args[args.index("-a") + 1] if len(args) > args.index("-a") + 1 else None
        )
        if not filename:
            return 0  # no file specified; do nothing
        # try:
        if l - ShellContext.hist_appended_items - 1 > 0:
            # readline.append_history_file(
            #     l - ShellContext.hist_appended_items, filename
            # )
            save_history = FileHistory(filename)
            # TODO
            s = ShellContext.history.get_strings()
            for line in s[l - ShellContext.hist_appended_items :]:
                save_history.store_string(line)

        return l - ShellContext.hist_appended_items

    if "-c" in args:
        open(ShellContext.env_HISTFILE, "w").close()
        return 0

    n = int(next(filter(lambda x: x.isnumeric(), args), l))  # history <n>

    items = list(ShellContext.history.load_history_strings())
    # print cmd index and input
    num_to_print = min(l, n)
    for i in range(num_to_print):  # 1-indexed
        hist_cmd = items[i]
        print(f"{i} {hist_cmd}")

    # no items are appended to the history file
    return 0
