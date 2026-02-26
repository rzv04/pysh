# Source - https://stackoverflow.com/a/69349450
# Posted by Peter Mitrano
# Retrieved 2026-02-26, License - CC BY-SA 4.0

#!/usr/bin/python

import pathlib
import readline


def complete_path(text, state):
    incomplete_path = pathlib.Path(text)
    if incomplete_path.is_dir():
        completions = [p.as_posix() for p in incomplete_path.iterdir()]
    elif incomplete_path.exists():
        completions = [incomplete_path]
    else:
        exists_parts = pathlib.Path(".")
        for part in incomplete_path.parts:
            test_next_part = exists_parts / part
            if test_next_part.exists():
                exists_parts = test_next_part

        completions = []
        for p in exists_parts.iterdir():
            p_str = p.as_posix()
            if p_str.startswith(text):
                completions.append(p_str)
    return completions[state]


# we want to treat '/' as part of a word, so override the delimiters
readline.set_completer_delims(" \t\n;")
# Source - https://stackoverflow.com/a/75696616
# Posted by Klaus Wik
# Retrieved 2026-02-26, License - CC BY-SA 4.0

if "libedit" in readline.__doc__:
    readline.parse_and_bind("bind ^I rl_complete")
else:
    readline.parse_and_bind("tab: complete")

readline.set_completer(complete_path)
print(input("tab complete a filename: "))
