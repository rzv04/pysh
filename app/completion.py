import rlcompleter
from typing import override
from app.builtin_commands import BuiltinCommands


class ShellCompleter(rlcompleter.Completer):
    @override
    def global_matches(self, text: str) -> list[str]:
        """Compute matches when text is a simple name.

        Return a list of all keywords, built-in shell functions that match.

        """
        matches: list[str] = []
        seen = {"__builtins__"}
        for word in [e.value for e in BuiltinCommands]:
            if word.startswith(text):
                seen.add(word)
                matches.append(word)

        if len(matches) == 1:
            matches[0] += " "

        return matches
