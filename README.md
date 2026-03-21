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

### Installing from repository

With [Python 3.10+](https://www.python.org/downloads/release/python-3100/) and [pipx](https://pipx.pypa.io/stable/) installed,
run the following command:

```bash
$ pipx install "pysh @ git+https://github.com/rzv04/pysh.git@v0.1.0"
```

You can now simply run it with:

```bash
$ pysh
```

### Installing from source/distribution packaging

Other common distribution formats (.tar.gz, wheels) are available at the [Releases](https://github.com/rzv04/pysh/releases) section.
To manually build them from the source, clone the repository and run the following:

```bash
~$ git clone https://github.com/rzv04/pysh.git

~$ cd

~/pysh/$ uv build

~/pysh/$ cd dist/; ls

```

You will need [uv](https://docs.astral.sh/uv/#installation) to run _uv build_.

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
