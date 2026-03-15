import rlcompleter
from typing import override
from app.builtin_commands import BuiltinCommands
import os
import sys
import pathlib
from app.shell_context import ShellContext
import shlex


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
        """Compute matches when text is a simple (file)name, a path, or a nested path with a partial filename.

        Args:
            text(str): The partial text to be matched with external commands in $PATH, or with filenames in the current directory,
            or with filenames in a nested path.

            A partial path is a path with a partial filename, eg. "src/ma" is a partial path with "src" as the
            path component and "ma" as the partial filename component.
            This can be completed only when it is an argument to a command, eg. "ls src/ma" should be completed to "ls src/main.py" if "src/main.py" exists,
            but "src/ma" alone should not be completed since it is not an argument to a command.

        Returns:
            list[str]: Return a list of all keywords, built-in shell functions that match.
        """
        # matches = (
        #     self._builtin_matches(text)
        #     or self._external_matches(text)
        #     or self._local_filename_matches(text)
        #     or self._nested_path_filename_matches(text)
        # )
        matches: list[str] = []
        buf = ShellContext.get_input_buffer()
        # Run partial shlex to determine if the text is an argument to a command or not
        partial_tokens = shlex.split(buf)
        if partial_tokens:
            # find text position in the input buffer split
            text_pos = partial_tokens.index(text) if text in partial_tokens else -1
            if text_pos > 0:  # check if previous token is not a special symbol
                prev_token = partial_tokens[text_pos - 1]
                if prev_token not in ["|", "&&", "||"]:
                    # text is an argument to a command; check for filename matches first
                    matches = self._nested_path_filename_matches(
                        text
                    ) or self._local_filename_matches(text)
                else:
                    matches = self._builtin_matches(text) or self._external_matches(
                        text
                    )

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

    def _dirs_matches(self, text: str, paths: list[str]) -> list[str]:
        """Compute matches when text is a simple name, searching inside all given paths.

        Args:
            text (str): The partial text (not a path part) to be matched with.
            paths (list[str]): A list of directories to search for matches in.

        Returns:
            list[str]: Return a list of all keywords found in all given directories that match.
        """
        matches: list[str] = []

        if matches:
            if len(matches) == 1:
                matches[0] += " "  # append a whitespace after each concrete candidate
            return matches  # all previously cached paths should already be inside

        try:
            for a_path in paths:
                for word in os.listdir(a_path):
                    if word.startswith(text) and word not in matches:
                        matches.append(word)

        except FileNotFoundError:
            pass

        return self._handle_prefix_matches(matches, text)

    def _external_matches(self, text: str) -> list[str]:
        """Compute matches when text is a simple name.

        Return a list of all keywords, external shell functions that match.

        """
        path_var: list[str] = str(os.environ.get("PATH", [])).split(os.pathsep)

        return self._dirs_matches(text, path_var)

    def _longest_common_prefix(self, matches: list[str]) -> str:
        if not matches:
            return ""

        prefix = min(matches)
        for match in matches:
            while not match.startswith(prefix):
                prefix = prefix[:-1:]

        return prefix

    def _local_filename_matches(self, text: str) -> list[str]:
        """Compute matches when text is a filename inside the current directory.

        Return a list of all keywords, filenames in the current directory that match.

        """
        return self._dirs_matches(text, ["."])

    def _nested_path_filename_matches(self, text: str) -> list[str]:
        """Compute matches when text is a (partial) filename with nested absolute/relative path.
        eg. for text = "src/ma", if "src/main.py" exists, it should be a match.

        Return a list of all keywords, filenames in the given current directory that match.

        For a completion to be made, the given directory must exist, be it absolute or relative.
        """
        matches: list[str] = []

        if matches:
            if len(matches) == 1:
                matches[0] += " "  # append a whitespace after each concrete candidate
            return matches  # all previously cached paths should already be inside

        # extract path component and filename component from text
        p = pathlib.Path(text)
        path_component = p.parent
        filename_component = p.name

        # find filename matches inside the given path component
        filename_matches = self._dirs_matches(filename_component, [str(path_component)])

        # append the path component to the found filename matches
        for match in filename_matches:
            matches.append(str(path_component / match))

        return matches
