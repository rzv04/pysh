from prompt_toolkit.completion import Completer, Completion
from app.builtin_commands import BuiltinCommands
import os
import pathlib
import shlex


class ShellCompleter(Completer):
    def get_completions(self, document, complete_event):
        line = document.text_before_cursor
        current = document.get_word_before_cursor(WORD=True)

        tokens = self._safe_split(line)
        is_command_position = self._is_command_position(tokens, current)

        if is_command_position:
            for item in self._command_matches(current):
                yield Completion(
                    text=item,
                    start_position=-len(current),
                    display=item,
                )
        else:
            for item in self._path_matches(current):
                yield Completion(
                    text=item,
                    start_position=-len(current),
                    display=item,
                )

    def _safe_split(self, line: str) -> list[str]:
        try:
            return shlex.split(line)
        except ValueError:
            # Unclosed quote etc. Fall back to whitespace split for completion.
            return line.split()

    def _is_command_position(self, tokens: list[str], current: str) -> bool:
        if not tokens:
            return True
        # If cursor is on first token prefix, still completing command.
        if len(tokens) == 1 and tokens[0].startswith(current):
            return True
        return False

    def _command_matches(self, prefix: str) -> list[str]:
        builtins = [e.value for e in BuiltinCommands if e.value.startswith(prefix)]
        externals = self._external_matches(prefix)
        # Keep order stable and deduplicate.
        seen = set()
        out = []
        for item in builtins + externals:
            if item not in seen:
                seen.add(item)
                out.append(item)
        return out

    def _external_matches(self, prefix: str) -> list[str]:
        out: list[str] = []
        for p in str(os.environ.get("PATH", "")).split(os.pathsep):
            try:
                for name in os.listdir(p):
                    full = os.path.join(p, name)
                    if (
                        name.startswith(prefix)
                        and os.access(full, os.X_OK)
                        and name not in out
                    ):
                        out.append(name)
            except OSError:
                continue
        return out

    def _path_matches(self, prefix: str) -> list[str]:
        p = pathlib.Path(prefix)
        base = p.parent if str(p.parent) != "." else pathlib.Path(".")
        name_prefix = p.name

        out: list[str] = []
        try:
            for name in os.listdir(base):
                if not name.startswith(name_prefix):
                    continue
                candidate = str(base / name) if str(base) != "." else name
                if os.path.isdir(base / name):
                    candidate += "/"
                out.append(candidate)
        except OSError:
            return []
        return out
