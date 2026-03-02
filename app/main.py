from app.completion import ShellCompleter
from app.command import Command, CommandFactory
import readline


def main():
    readline.set_auto_history(True)
    # init completer
    if "libedit" in readline.__doc__:  # alternative to python3.13 'backend' function
        readline.parse_and_bind("bind ^I rl_complete")
        readline.parse_and_bind("set bell-style audible")
    else:
        readline.parse_and_bind("tab: complete")
    readline.set_completer(ShellCompleter().complete)

    # begin repl with unprivileged user tag
    while True:
        # read user input
        full_cmd = input("$ ")
        # readline.add_history(full_cmd)

        cmd_list: list[Command] = CommandFactory.build(full_cmd)

        # execute the commands
        for cmd in cmd_list:
            cmd.execute()


if __name__ == "__main__":
    main()
