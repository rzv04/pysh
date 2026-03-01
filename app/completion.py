import rlcompleter
from typing import override
from app.builtin_commands import BuiltinCommands
import os
import sys


class ShellCompleter(rlcompleter.Completer):
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

    def _handle_prefix_matches(self, matches: list[str], text: str):
        """Internal function to get the longest common prefix and to handle 'bell alert' cases.

        Args:
            matches (list[str]): The found matches to the text 'text'
            text (str): The text (prefix) to be matched with external commands in $PATH.

        Returns:
            str: The original list of matches if no common prefix, else a list of only the longest common prefix between matches.
        """
        if len(matches) == 1:
            return [
                matches[0] + " "
            ]  # append a whitespace after each concrete candidate

        if len(matches) > 1:
            lcp = self._longest_common_prefix(matches)
            if lcp and len(lcp) > len(text):
                return [lcp]

            self._ring_bell()
            return matches

        self._ring_bell()

        return matches

    def _builtin_matches(self, text: str) -> list[str]:
        """Compute builtin matches when text is a simple name.

        Return a list of all keywords, built-in shell functions that match.

        """
        matches: list[str] = []
        for word in [e.value for e in BuiltinCommands]:
            if word.startswith(text):
                matches.append(word)

        return self._handle_prefix_matches(matches, text)

    def _ring_bell(self):
        sys.stdout.write("\a")
        sys.stdout.flush()

    def _external_matches(self, text: str) -> list[str]:
        """Compute matches when text is a simple name.

        Return a list of all keywords, external shell functions that match.

        """
        matches: list[str] = []
        path_var: list[str] = str(os.environ.get("PATH", [])).split(os.pathsep)

        if matches:
            if len(matches) == 1:
                matches[0] += " "  # append a whitespace after each concrete candidate
            return matches  # all previously cached paths should already be inside

        try:
            for a_path in path_var:
                for word in os.listdir(a_path):
                    if word.startswith(text) and word not in matches:
                        matches.append(word)

        except FileNotFoundError:
            pass

        return self._handle_prefix_matches(matches, text)

    def _longest_common_prefix(self, matches: list[str]) -> str:
        if not matches:
            return ""

        prefix = min(matches)
        for match in matches:
            while not match.startswith(prefix):
                prefix = prefix[:-1:]

        return prefix
