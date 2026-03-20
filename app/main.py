from app.completion import ShellCompleter
from app.command import Command, CommandFactory

# import readline
from prompt_toolkit import PromptSession


from app.shell_context import ShellContext
from app.builtin_commands import shell_history


def main():
    # init context with history
    ShellContext.init()

    session = PromptSession(history=ShellContext.history)

    # read history on startup if available
    shell_history(["-r", ShellContext.env_HISTFILE])

    # begin repl with unprivileged user tag
    while True:
        # read user input
        full_cmd = session.prompt(message="$ ")
        # readline.add_history(full_cmd)

        cmd_list: list[Command] = CommandFactory.build(full_cmd)

        # execute the commands
        for cmd in cmd_list:
            cmd.execute()


if __name__ == "__main__":
    main()
