import pysh.builtin_commands as bc


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

