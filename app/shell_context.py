import os


class ShellContext:
    hist_appended_items: int
    _env: dict[str, str]
    env_HISTFILE: str

    @classmethod
    def init(cls):
        cls.hist_appended_items = 0
        cls._env = os.environ.copy()
        cls.env_HISTFILE = cls._env.get(
            "HISTFILE", os.path.expanduser("~/.shell_history")
        )
