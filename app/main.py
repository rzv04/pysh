import sys
import app.builtin_commands as bc
import re
import logging
import warnings
import shlex
import os


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

    # begin repl with unprivileged user tag
    while True:
        redirects: dict[str, int] = {}
        sys.stdout.write("$ ")
        # read user input
        full_cmd = input()

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

        if "stdout" in redirects:
            os.dup2(redirects["stdout"], sys.stdout.fileno())

        if "stderr" in redirects:
            os.dup2(redirects["stderr"], sys.stderr.fileno())


def handle_builtin_command(cmd: str, args: list[str]) -> bool:

    match cmd:
        case bc.BuiltinCommands.EXIT.value:
            bc.shell_exit()
        case bc.BuiltinCommands.ECHO.value:
            bc.shell_echo(args)
        case bc.BuiltinCommands.TYPE.value:
            bc.shell_type(args)
        case bc.BuiltinCommands.PWD.value:
            bc.shell_pwd()
        case bc.BuiltinCommands.CD.value:
            bc.shell_cd(args[0] if args else "")

        case _:
            return False
    return True


def handle_external_command(cmd: str, args: list[str]) -> bool:
    is_exec_cmd = "exec" in cmd
    if is_exec_cmd:
        # actual command should be the second word
        cmd_abs_path = bc.search_for_cmd_file(args[0] if args else "")
    else:
        cmd_abs_path = bc.search_for_cmd_file(cmd)

    if cmd_abs_path:
        bc.shell_exec(cmd_abs_path, [cmd] + args)  # args[0] is cmd name
    else:
        # handle_invalid_command(cmd)
        return False
    return True


def handle_invalid_command(cmd: str):
    print(f"{cmd}: command not found")


if __name__ == "__main__":
    main()
