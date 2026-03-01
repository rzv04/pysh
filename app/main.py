import sys
import re
import logging
import warnings
import shlex
import os
from app.completion import ShellCompleter
from app.builtin_commands import handle_builtin_command
from app.external_commands import handle_external_command
import readline


@warnings.deprecated("s")
def preprocess_args(args_str: str) -> list[str]:
    if not args_str:
        return []

    # TODO change special meanings for chars inside ""
    args = [match.group(0) for match in re.finditer(r"'.*'|\".*\"|[^\s]+", args_str)]

    def remove_quotes(s: str) -> str:
        try:
            l = s.index("'")
            r = s.rindex("'")
            return s[0:l] + s[l + 1 : r] + s[r + 1 :]
        except ValueError:
            return s

    for i, arg in enumerate(args):
        while arg != remove_quotes(arg):
            arg = remove_quotes(arg)
        args[i] = arg

    return args


def redirect_stdout(args: list[str], redirects: dict[str, int]):
    # get first file path that is after the '>' character
    out_file_path = args[-1] if args else ""
    idx = -1
    try:
        idx = args.index(">")

    except ValueError:
        idx = args.index("1>")

    try:
        # dup original stdout
        redirects["stdout"] = os.dup(sys.stdout.fileno())
        # dup file to stdout
        r = open(out_file_path, "w")
        os.dup2(r.fileno(), sys.stdout.fileno())

    except FileNotFoundError:
        pass
    # cut args to before token
    # args = args[:idx]
    del args[idx:]


def redirect_stderr(args: list[str], redirects: dict[str, int]):
    # get first file path that is after the '>' character
    out_file_path = args[-1] if args else ""
    idx = args.index("2>")

    try:
        # dup original stderr
        redirects["stderr"] = os.dup(sys.stderr.fileno())
        r = open(out_file_path, "w")
        os.dup2(r.fileno(), sys.stderr.fileno())

    except FileNotFoundError:
        pass
    # cut args to before token
    # args = args[:idx]
    del args[idx:]


def append_stdout(args: list[str], redirects: dict[str, int]):
    # get first file path that is after the '>' character
    out_file_path = args[-1] if args else ""
    idx = -1
    try:
        idx = args.index(">>")

    except ValueError:
        idx = args.index("1>>")

    try:
        # dup original stdout
        redirects["stdout"] = os.dup(sys.stdout.fileno())
        r = open(out_file_path, "a+")
        os.dup2(r.fileno(), sys.stdout.fileno())

    except FileNotFoundError:
        pass
    # cut args to before token
    # args = args[:idx]
    del args[idx:]


def append_stderr(args: list[str], redirects: dict[str, int]):
    # get first file path that is after the '>' character
    out_file_path = args[-1] if args else ""
    idx = -1
    idx = args.index("2>>")

    try:
        # dup original stderr
        redirects["stderr"] = os.dup(sys.stderr.fileno())
        r = open(out_file_path, "a+")
        os.dup2(r.fileno(), sys.stderr.fileno())

    except FileNotFoundError:
        pass
    # cut args to before token
    # args = args[:idx]
    del args[idx:]


def main():
    # init completer
    if "libedit" in readline.__doc__:  # alternative to python3.13 'backend' function
        readline.parse_and_bind("bind ^I rl_complete")
        readline.parse_and_bind("set bell-style audible")
    else:
        readline.parse_and_bind("tab: complete")
    readline.set_completer(ShellCompleter().complete)

    # begin repl with unprivileged user tag
    while True:
        redirects: dict[str, int] = {}
        # read user input
        full_cmd = input("$ ")

        preprocessed_input = shlex.split(full_cmd)
        logging.log(level=logging.INFO, msg=preprocessed_input)
        # extract its args
        cmd: str = preprocessed_input[0] if preprocessed_input else ""
        args: list[str] = preprocessed_input[1:] if len(preprocessed_input) >= 2 else []

        # Redirect streams
        if ">" in args or "1>" in args:
            redirect_stdout(args, redirects)

        if "2>" in args:
            redirect_stderr(args, redirects)

        if ">>" in args or "1>>" in args:
            append_stdout(args, redirects)

        if "2>>" in args:
            append_stderr(args, redirects)

        if not handle_builtin_command(cmd, args) and not handle_external_command(
            cmd, args
        ):
            handle_invalid_command(cmd)

        # restore streams
        if "stdout" in redirects:
            os.dup2(redirects["stdout"], sys.stdout.fileno())

        if "stderr" in redirects:
            os.dup2(redirects["stderr"], sys.stderr.fileno())


def handle_invalid_command(cmd: str):
    print(f"{cmd}: command not found")


if __name__ == "__main__":
    main()
