import os


class ShellContext:
    hist_appended_items: int
    _env: dict[str, str]
    env_HISTFILE: str
    # readline.get_line_buffer()

    @staticmethod
    def get_input_buffer() -> str:
        import readline

        return readline.get_line_buffer()

    @classmethod
    def init(cls):
        cls.hist_appended_items = 0
        cls._env = os.environ.copy()
        cls.env_HISTFILE = cls._env.get(
            "HISTFILE", os.path.expanduser("~/.shell_history")
        )

    def __init__(self) -> None:
        raise NotImplementedError(
            "ShellContext is a singleton class; use ShellContext.init() instead"
        )
