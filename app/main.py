import sys
import logging
import shlex
import os
from app.completion import ShellCompleter
from app.builtin_commands import handle_builtin_command
from app.external_commands import handle_external_command
import readline


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
