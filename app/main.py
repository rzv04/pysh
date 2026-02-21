import sys
from builtin_commands import *


def main():
    # begin repl with unprivileged user tag
    while True:
        sys.stdout.write("$ ")
        # read user input
        cmd = input()
        # TODO handle all types of commands
        # handle_invalid_command(cmd)
        handle_builtin_commands(cmd)


def handle_builtin_commands(cmd: str):
    match cmd:
        case BuiltinCommands.EXIT.value:
            shell_exit()
        case _:
            handle_invalid_command(cmd)


def handle_invalid_command(cmd: str):
    print(f"{cmd}: command not found")


if __name__ == "__main__":
    main()
