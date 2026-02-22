import sys
import app.builtin_commands as bc


def main():
    # begin repl with unprivileged user tag
    while True:
        sys.stdout.write("$ ")
        # read user input
        full_cmd = input().strip().split()

        # extract its args
        cmd: str = full_cmd[0] if full_cmd else ""
        args: list[str] = full_cmd[1:] if len(full_cmd) >= 2 else []

        # TODO handle all types of commands
        handle_builtin_command(cmd, args)
        # handle_invalid_command(cmd)


def handle_builtin_command(cmd: str, args: list[str]):

    match cmd:
        case bc.BuiltinCommands.EXIT.value:
            bc.shell_exit()
        case bc.BuiltinCommands.ECHO.value:
            bc.shell_echo(args)
        case bc.BuiltinCommands.TYPE.value:
            bc.shell_type(args)
        case bc.BuiltinCommands.EXEC.value:
            handle_external_command(cmd, args)
        case _:
            handle_external_command(cmd, args)


def handle_external_command(cmd: str, args: list[str]):
    is_exec_cmd = "exec" in cmd
    if is_exec_cmd:
        # actual command should be the second word
        cmd_abs_path = bc.search_for_cmd_file(args[0] if args else "")
    else:
        cmd_abs_path = bc.search_for_cmd_file(cmd)

    if cmd_abs_path:
        bc.shell_exec(cmd_abs_path, args)
    else:
        handle_invalid_command(cmd)


def handle_invalid_command(cmd: str):
    print(f"{cmd}: command not found")


if __name__ == "__main__":
    main()
