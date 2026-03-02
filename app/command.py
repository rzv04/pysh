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
            self.original_fd_redirects["stderr"] = os.dup(sys.stderr.fileno())
            # dup file to stdout
            r = open(self.path_redirects["stderr"], "w")
            os.dup2(r.fileno(), sys.stderr.fileno())

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
        redirect_tokens = [">", "1>", ">>", "1>>", "2>", "2>>"]

        cmd_list: list[ParsedCommand] = []
        new_cmd: ParsedCommand = ParsedCommand()

        cursor = 0
        while cursor < len(preprocessed_str):
            token: str = preprocessed_str[cursor]

            if token in cmd_sep_tokens:
                new_cmd.cmd_bind_token = token
                cmd_list.append(new_cmd)
                new_cmd = ParsedCommand()
                cursor += 1
                continue

            if token in redirect_tokens:
                redirect_path = (
                    None
                    if cursor + 1 >= len(preprocessed_str)
                    else preprocessed_str[cursor + 1]
                )

                match token:
                    case ">" | "1>":
                        new_cmd.cmd_file_redirects["stdout"] = redirect_path
                    case ">>" | "1>>":
                        new_cmd.cmd_file_redirects["append_stdout"] = redirect_path
                    case "2>":
                        new_cmd.cmd_file_redirects["stderr"] = redirect_path
                    case "2>>":
                        new_cmd.cmd_file_redirects["append_stderr"] = redirect_path
                    case _:
                        pass

                cursor += 2  # IMPORTANT: skip the redirect target
                continue

            # normal word: cmd name or arg
            if not new_cmd.cmd_name:
                new_cmd.cmd_name = token
            else:
                new_cmd.cmd_args.append(token)

            cursor += 1

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
        def _to_command(pc: ParsedCommand) -> Command | None:
            if not pc.cmd_name:
                return None

            redirects: dict[str, str] = {
                k: v for k, v in pc.cmd_file_redirects.items() if isinstance(v, str)
            }

            if bc.is_builtin_command(pc.cmd_name):
                return BuiltinCommand(pc.cmd_name, pc.cmd_args, redirects)

            if not bc.search_for_cmd_file(pc.cmd_name):
                return InvalidCommand(pc.cmd_name, pc.cmd_args, redirects)
            return ExternalCommand(pc.cmd_name, pc.cmd_args, redirects)

        results: list[Command] = []
        parsed = CommandFactory._process_input(raw_input)

        current_pipeline: list[Command] = []
        for pc in parsed:
            cmd = _to_command(pc)
            if cmd is None:
                continue

            current_pipeline.append(cmd)

            # If this command is piped to the next, keep accumulating
            if pc.cmd_bind_token == "|":
                continue

            # Pipeline ends here (or it's just a single command)
            if len(current_pipeline) == 1:
                results.append(current_pipeline[0])
            else:
                results.append(PipelineCommand(current_pipeline))

            current_pipeline = []

        # If input ended with a pipeline (dangling '|'), finalize what we have
        if current_pipeline:
            if len(current_pipeline) == 1:
                results.append(current_pipeline[0])
            else:
                results.append(PipelineCommand(current_pipeline))

        return results


class BuiltinCommand(Command):
    def __init__(
        self, cmd: str, args: list[str], path_redirects: dict[str, str]
    ) -> None:
        super().__init__(cmd, args, path_redirects)

    def execute(self):
        # should execute from the same process
        self._redirect_streams()
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
            case bc.BuiltinCommands.HISTORY.value:
                bc.shell_history(self.args)
            case _:
                bc.handle_invalid_command(self.cmd)
                self._restore_streams()
                return False
        self._restore_streams()
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
                os.execvp(cmd_abs_path, [self.cmd] + self.args)

            else:
                os.waitpid(pid, 0)
        else:
            # handle_invalid_command(cmd)
            return False

        return True


class PipelineCommand(Command):
    def __init__(self, commands: list[Command]) -> None:
        super().__init__(cmd="|", args=[], path_redirects={})
        self.commands = commands

    def execute(self) -> bool:
        if not self.commands:
            return True

        n = len(self.commands)
        if n == 1:
            return self.commands[0].execute()

        pipes: list[tuple[int, int]] = [os.pipe() for _ in range(n - 1)]
        pids: list[int] = []

        for i, stage in enumerate(self.commands):
            pid = os.fork()
            if pid == 0:
                # Child: wire stdin/stdout to the pipeline
                try:
                    if i > 0:
                        os.dup2(pipes[i - 1][0], sys.stdin.fileno())
                    if i < n - 1:
                        os.dup2(pipes[i][1], sys.stdout.fileno())

                    # Close all pipe fds in child after dup2
                    for r, w in pipes:
                        try:
                            os.close(r)
                        except OSError:
                            pass
                        try:
                            os.close(w)
                        except OSError:
                            pass

                    # Execute stage without creating another fork layer
                    if isinstance(stage, BuiltinCommand):
                        stage._redirect_streams()
                        ok = stage.execute()
                        stage._restore_streams()
                        os._exit(0 if ok else 1)

                    if isinstance(stage, ExternalCommand):
                        cmd_abs_path = bc.search_for_cmd_file(stage.cmd)
                        if not cmd_abs_path:
                            sys.stderr.write(f"{stage.cmd}: command not found\n")
                            sys.stderr.flush()
                            os._exit(127)

                        stage._redirect_streams()
                        os.execv(cmd_abs_path, [stage.cmd] + stage.args)

                    # Unknown Command subtype
                    os._exit(1)

                except Exception:
                    os._exit(1)

            # Parent
            pids.append(pid)

        # Parent: close pipe fds
        for r, w in pipes:
            try:
                os.close(r)
            except OSError:
                pass
            try:
                os.close(w)
            except OSError:
                pass

        # Parent: wait for all children; pipeline success == last command success (common shell behavior)
        last_status = 1
        for pid in pids:
            _, status = os.waitpid(pid, 0)
            if pid == pids[-1]:
                last_status = status

        return os.WIFEXITED(last_status) and os.WEXITSTATUS(last_status) == 0


class InvalidCommand(Command):
    def __init__(
        self, cmd: str, args: list[str] = [], path_redirects: dict[str, str] = {}
    ) -> None:
        super().__init__(cmd, args, path_redirects)

    def execute(self) -> bool:
        self._redirect_streams()
        bc.handle_invalid_command(self.cmd)
        self._restore_streams()
        return False
