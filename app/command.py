import abc
import app.builtin_commands as bc
import os
import sys


class Command(abc.ABC):
    def __init__(
        self, cmd: str, args: list[str], path_redirects: dict[str, str]
    ) -> None:
        """Init a command out of a whole user inputted shell command.

        Args:
            cmd (str): The command name or full path to be executed.
            args (list[str]): The command's arguments (excepting the redirecting/pipeing tokens)
            path_redirects (dict[str, str]): The file paths for the streams to be redirected to.
            Accepted in the format: "stdin" | "stdout" | "stderr" -> absolute_file_path
        """
        self.cmd = cmd
        self.args = args
        self.path_redirects = path_redirects
        self.fd_redirects: dict[str, int] = {}

    @abc.abstractmethod
    def execute(self) -> bool:
        pass

    def _redirect_stdout(self, args: list[str]):
        # get first file path that is after the '>' character
        out_file_path = args[-1] if args else ""
        idx = -1
        try:
            idx = args.index(">")

        except ValueError:
            idx = args.index("1>")

        try:
            # dup original stdout to new fd
            self.fd_redirects["stdout"] = os.dup(sys.stdout.fileno())
            # dup file to stdout
            r = open(out_file_path, "w")
            os.dup2(r.fileno(), sys.stdout.fileno())

        except FileNotFoundError:
            pass
        # cut args to before token
        # args = args[:idx]
        del args[idx:]

    def _redirect_stderr(self, args: list[str]):
        # get first file path that is after the '>' character
        out_file_path = args[-1] if args else ""
        idx = args.index("2>")

        try:
            # dup original stderr to new fd
            self.fd_redirects["stderr"] = os.dup(sys.stderr.fileno())
            r = open(out_file_path, "w")
            os.dup2(r.fileno(), sys.stderr.fileno())

        except FileNotFoundError:
            pass
        # cut args to before token
        # args = args[:idx]
        del args[idx:]

    def _append_stdout(self, args: list[str]):
        # get first file path that is after the '>' character
        out_file_path = args[-1] if args else ""
        idx = -1
        try:
            idx = args.index(">>")

        except ValueError:
            idx = args.index("1>>")

        try:
            # dup original stdout to new fd
            self.fd_redirects["stdout"] = os.dup(sys.stdout.fileno())
            r = open(out_file_path, "a+")
            os.dup2(r.fileno(), sys.stdout.fileno())

        except FileNotFoundError:
            pass
        # cut args to before token
        # args = args[:idx]
        del args[idx:]

    def _append_stderr(self, args: list[str]):
        # get first file path that is after the '>' character
        out_file_path = args[-1] if args else ""
        idx = -1
        idx = args.index("2>>")

        try:
            # dup original stderr
            self.fd_redirects["stderr"] = os.dup(sys.stderr.fileno())
            r = open(out_file_path, "a+")
            os.dup2(r.fileno(), sys.stderr.fileno())

        except FileNotFoundError:
            pass
        # cut args to before token
        # args = args[:idx]
        del args[idx:]


class BuiltinCommand(Command):
    def __init__(
        self, cmd: str, args: list[str], path_redirects: dict[str, str]
    ) -> None:
        super().__init__(cmd, args, path_redirects)

    @abc.abstractmethod
    def execute(self):
        match self.cmd:
            case bc.BuiltinCommands.EXIT.value:
                bc.shell_exit()
            case bc.BuiltinCommands.ECHO.value:
                bc.shell_echo(self.args)
            case bc.BuiltinCommands.TYPE.value:
                bc.shell_type(self.args)
            case bc.BuiltinCommands.PWD.value:
                bc.shell_pwd()
            case bc.BuiltinCommands.CD.value:
                bc.shell_cd(self.args[0] if self.args else "")
            case _:
                return False

        return True


class ExternalCommand(Command):
    def __init__(
        self, cmd: str, args: list[str], path_redirects: dict[str, str]
    ) -> None:
        super().__init__(cmd, args, path_redirects)

    @abc.abstractmethod
    def execute(self):
        is_exec_cmd = "exec" in self.cmd
        if is_exec_cmd:
            # actual command should be the second word
            cmd_abs_path = bc.search_for_cmd_file(self.args[0] if self.args else "")
        else:
            cmd_abs_path = bc.search_for_cmd_file(self.cmd)

        if cmd_abs_path:
            bc.shell_exec(cmd_abs_path, [self.cmd] + self.args)  # args[0] is cmd name
        else:
            # handle_invalid_command(cmd)
            return False
        return True
