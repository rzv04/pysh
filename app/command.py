import abc
import app.builtin_commands as bc
import os
import sys
import shlex
import logging
from dataclasses import dataclass, field


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
        self.path_redirects = path_redirects  # "stdin": abs_redirect_file_path
        self.original_fd_redirects: dict[str, int] = {}  # "stdin": duped_original_stdin

    @abc.abstractmethod
    def execute(self) -> bool:
        """Executes the command with its args and optional redirects and pipeing.

        Returns:
            bool: True is successful, False otherwise.
        """
        pass

    def _redirect_stdout(self):
        # get first file path that is after the '>' character
        try:
            # dup original stdout to new fd
            self.original_fd_redirects["stdout"] = os.dup(sys.stdout.fileno())
            # dup file to stdout
            r = open(self.path_redirects["stdout"], "w")
            os.dup2(r.fileno(), sys.stdout.fileno())

        except FileNotFoundError:
            pass

    def _redirect_stderr(self):
        # get first file path that is after the '>' character
        try:
            # dup original stdout to new fd
            self.original_fd_redirects["stderr"] = os.dup(sys.stdout.fileno())
            # dup file to stdout
            r = open(self.path_redirects["stderr"], "w")
            os.dup2(r.fileno(), sys.stdout.fileno())

        except FileNotFoundError:
            pass

    def _append_stdout(self):

        try:
            # dup original stdout to new fd
            self.original_fd_redirects["stdout"] = os.dup(sys.stdout.fileno())
            r = open(self.path_redirects["append_stdout"], "a+")
            os.dup2(r.fileno(), sys.stdout.fileno())

        except FileNotFoundError:
            pass

    def _append_stderr(self):
        try:
            # dup original stderr
            self.original_fd_redirects["stderr"] = os.dup(sys.stderr.fileno())
            r = open(self.path_redirects["append_stderr"], "a+")
            os.dup2(r.fileno(), sys.stderr.fileno())

        except FileNotFoundError:
            pass

    def _redirect_streams(self):
        # Redirect streams
        if "stdout" in self.path_redirects:
            self._redirect_stdout()

        if "stderr" in self.path_redirects:
            self._redirect_stderr()

        if "append_stdout" in self.path_redirects:
            self._append_stdout()

        if "append_stderr" in self.path_redirects:
            self._append_stderr()

    def _restore_streams(self):
        # restore streams
        if "stdout" in self.original_fd_redirects:
            os.dup2(self.original_fd_redirects["stdout"], sys.stdout.fileno())

        if "stderr" in self.original_fd_redirects:
            os.dup2(self.original_fd_redirects["stderr"], sys.stderr.fileno())


@dataclass
class ParsedCommand:
    #     ParsedCommand = Tuple[
    #     str, list[str], Tuple[str,str], str
    # ]  # cmd_name, cmd_args, cmd_redirects, cmd_bind
    cmd_name: str | None = None
    cmd_args: list[str] = field(default_factory=lambda: [])
    cmd_file_redirects: dict[str, str | None] = field(default_factory=lambda: {})
    cmd_bind_token: str | None = None


class CommandFactory:
    @staticmethod
    def _extract_cmd_list(
        preprocessed_str: list[str],
    ) -> list[ParsedCommand]:
        # [cmd args redirects pipe]
        if not preprocessed_str:
            return [ParsedCommand()]

        cmd_sep_tokens = [";", "|", "&&"]
        redirect_tokens = [">>", "1>>", "2>", "2>>"]

        cmd_list: list[ParsedCommand] = []
        new_cmd: ParsedCommand = ParsedCommand()

        for cursor in range(len(preprocessed_str)):
            token: str = preprocessed_str[cursor]
            if token in cmd_sep_tokens:
                # add sep to cmd
                new_cmd.cmd_bind_token = token
                cmd_list.append(new_cmd)
                new_cmd = ParsedCommand()
            else:
                if token not in redirect_tokens and token not in cmd_sep_tokens:
                    # add to new cmd
                    if not new_cmd.cmd_name:
                        new_cmd.cmd_name = token
                    else:
                        # add arg to list
                        new_cmd.cmd_args += [token]

                elif token in redirect_tokens:
                    # get redirect path
                    redirect_path = (
                        None
                        if cursor + 1 >= len(preprocessed_str)
                        else preprocessed_str[cursor + 1]
                    )

                    match redirect_tokens.index(token):
                        case 0:
                            new_cmd.cmd_file_redirects["stdout"] = redirect_path
                        case 1:
                            new_cmd.cmd_file_redirects["append_stdout"] = redirect_path
                        case 2:
                            new_cmd.cmd_file_redirects["stderr"] = redirect_path
                        case 3:
                            new_cmd.cmd_file_redirects["append_stderr"] = redirect_path
                        case _:
                            pass

        cmd_list.append(new_cmd)

        return cmd_list

    @staticmethod
    def _process_input(raw_input: str) -> list[ParsedCommand]:
        preprocessed_input = shlex.split(raw_input)
        logging.log(level=logging.INFO, msg=preprocessed_input)

        parsed_cmd_list = CommandFactory._extract_cmd_list(preprocessed_input)
        return parsed_cmd_list

    @classmethod
    def build(cls, raw_input: str) -> list[Command]:
        results: list[Command] = []
        cmd_list = CommandFactory._process_input(raw_input)
        # separate builtin from separate
        for cmd in cmd_list:
            if bc.is_builtin_command(cmd.cmd_name):
                # TODO handle none
                results.append(
                    BuiltinCommand(cmd.cmd_name, cmd.cmd_args, cmd.cmd_file_redirects)
                )
            else:
                results.append(
                    ExternalCommand(cmd.cmd_name, cmd.cmd_args, cmd.cmd_file_redirects)
                )

        return results


class BuiltinCommand(Command):
    def __init__(
        self, cmd: str, args: list[str], path_redirects: dict[str, str]
    ) -> None:
        super().__init__(cmd, args, path_redirects)

    def execute(self):
        # should execute from the same process
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

    def execute(self):

        cmd_abs_path = bc.search_for_cmd_file(self.cmd)

        if cmd_abs_path:
            # bc.shell_exec(cmd_abs_path, [self.cmd] + self.args)  # args[0] is cmd name
            # fork the process and execute the command
            pid = os.fork()
            if pid == 0:
                # child process
                # redirect streams
                self._redirect_streams()
                os.execvp(cmd_abs_path, self.args)

            else:
                os.waitpid(pid, 0)
        else:
            # handle_invalid_command(cmd)
            return False

        return True
