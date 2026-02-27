import rlcompleter
from typing import override
from app.builtin_commands import BuiltinCommands
import os


class ShellCompleter(rlcompleter.Completer):
    _hit_external_cmds: set[str] = set()

    @override
    def complete(self, text: str, state: int):
        """Return the next possible completion for 'text'.

        This is called successively with state == 0, 1, 2, ... until it
        returns None.  The completion should begin with 'text'.

        """
        if not text.strip():  # empty string/spaces only
            if state == 0:
                return ""
            else:
                return None

        if state == 0:
            self.matches = self.global_matches(text)
        try:
            return self.matches[state]
        except IndexError:
            return None

    @override
    def global_matches(self, text: str) -> list[str]:
        """Compute matches when text is a simple name.

        Return a list of all keywords, built-in shell functions that match.

        """
        matches = self._builtin_matches(text)
        if not matches:
            matches = self._external_matches(text)

        return matches

    def _builtin_matches(self, text: str) -> list[str]:
        """Compute builtin matches when text is a simple name.

        Return a list of all keywords, built-in shell functions that match.

        """
        matches: list[str] = []
        for word in [e.value for e in BuiltinCommands]:
            if word.startswith(text):
                matches.append(word)

        # TODO add longest common prefix completion to multiple matches
        lcp = self._longest_common_prefix(matches)
        if lcp:
            # overwrite matches to only 1 element with common prefix
            matches = [lcp]

        if len(matches) == 1 and not lcp:
            matches[0] += " "  # append a whitespace after each concrete candidate
        return matches

    def _external_matches(self, text: str) -> list[str]:
        """Compute matches when text is a simple name.

        Return a list of all keywords, external shell functions that match.
        Adds the hit resolved path to an internal set.

        """
        matches: list[str] = []
        path_var: list[str] = str(os.environ.get("PATH", [])).split(os.pathsep)

        # search in hit set first
        for word in ShellCompleter._hit_external_cmds:
            if word.startswith(text):
                matches.append(word)

        if matches:
            if len(matches) == 1:
                matches[0] += " "  # append a whitespace after each concrete candidate
            return matches  # all previously cached paths should already be inside

        try:
            for a_path in path_var:
                for word in os.listdir(a_path):
                    if word.startswith(text) and word not in matches:
                        matches.append(word)
                        ShellCompleter._hit_external_cmds.add(word)

        except FileNotFoundError:
            pass

        if len(matches) == 1:
            matches[0] += " "  # append a whitespace after each concrete candidate

        # TODO add longest common prefix completion to multiple matches
        lcp = self._longest_common_prefix(matches)
        if lcp:
            # overwrite matches to only 1 element with common prefix
            matches = [lcp]

        return matches

    def _longest_common_prefix(self, matches: list[str]) -> str:
        if not matches:
            return ""

        prefix = min(matches)
        for match in matches:
            while not match.startswith(prefix):
                prefix = prefix[:-1:]

        return prefix
