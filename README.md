# pysh

![build-passing](https://img.shields.io/badge/build-passing-brightgreen)
![tests-passing](https://img.shields.io/badge/tests-passing-brightgreen)
[![required-python-version](https://img.shields.io/python/required-version-toml?tomlFilePath=https%3A%2F%2Fraw.githubusercontent.com%2Frzv04%2Fpysh%2Fmain%2Fpyproject.toml)](https://github.com/rzv04/pysh)

> A Python shell featuring command auto-completion, auto-suggestion, and syntax highlighting

---

## Usage

---

![example-usage-1](example-images/demo.gif)

Usage is pretty similar to your regular shell, such as Bash, or zsh, like:

- _exit_ (_or CTRL+D_) to exit the shell! (_duh_)
- Tab for autocomplete while typing a command
- Up-Down arrow keys for navigating through the command history
- Right arrow for using the given auto-suggestion (_in faded font_)
- CTRL-C to cancel the typed command and to begin a new one

## Install

TODO install instructions

## Running

```bash
$ pysh

# Inside pysh:
$ <command> <options> <arguments> <ENTER>

# Command result appears here
...

$ exit
# OR
$ <CTRL+D>
```

## Roadmap

- [ ] Integrate Bash scripting
- [x] Prettier packaging

> Courtesy of [codecrafters](https://app.codecrafters.io/courses/shell/overview) and [python-prompt-toolkit](https://github.com/prompt-toolkit/python-prompt-toolkit) for massively helping to build this project!
