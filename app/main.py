from app.completion import ShellCompleter
from app.command import Command, CommandFactory
from pygments.lexers.shell import BashLexer
from prompt_toolkit.lexers import PygmentsLexer
from prompt_toolkit import PromptSession
from prompt_toolkit.styles.pygments import style_from_pygments_cls
from pygments.styles import get_style_by_name
from prompt_toolkit.auto_suggest import AutoSuggestFromHistory

from app.shell_context import ShellContext
from app.builtin_commands import shell_history


def main():
    # init context with history
    ShellContext.init()

    style = style_from_pygments_cls(get_style_by_name("monokai"))
    session = PromptSession(
        history=ShellContext.history,
        completer=ShellCompleter(),
        complete_while_typing=False,
        auto_suggest=AutoSuggestFromHistory(),
    )

    # begin repl with unprivileged user tag
    while True:
        # read user input
        full_cmd: str = session.prompt(
            message="$ ",
            lexer=PygmentsLexer(BashLexer),
            style=style,
            include_default_pygments_style=False,
        )

        cmd_list: list[Command] = CommandFactory.build(full_cmd)

        # execute the commands
        for cmd in cmd_list:
            cmd.execute()


if __name__ == "__main__":
    main()
