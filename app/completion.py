import rlcompleter
from typing import override
from app.builtin_commands import BuiltinCommands


class ShellCompleter(rlcompleter.Completer):
    @override
    def global_matches(self, text: str) -> list[str]:
        """Compute matches when text is a simple name.

        Return a list of all keywords, built-in functions and names currently
        defined in self.namespace that match.

        """
        matches: list[str] = []
        seen = {"__builtins__"}
        for word in [e.value for e in BuiltinCommands]:
            if word.startswith(text):
                seen.add(word)
                matches.append(word)

        return matches
