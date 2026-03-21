import unittest
from pysh.main import main
import sys
from io import StringIO
import os
from unittest.mock import patch


def _run_shell_suppress_exit() -> str:
    """Runs the shell program by writing the raw str in its format inside (mocked) stdin,
    collects the stdout contents then resets stdin and stdout.
    The chain should not contain the 'exit' command, as it is inserted by this function.

    Returns:
        str: The collected output from stdout
    """
    # _write_stdin_reset_cursor(raw_str, "exit")
    try:
        main()
    except SystemExit:
        pass

    sys.stdout.seek(0)
    out = sys.stdout.read()
    _clear_io()
    return out


def _clear_io():
    # Clear stdin and stdout
    sys.stdin.truncate(0)
    sys.stdout.truncate(0)
    sys.stdin.seek(0)
    sys.stdout.seek(0)


class TestBuiltinCommands(unittest.TestCase):
    """Test case for the builtin commands."""

    @classmethod
    def setUpClass(cls):
        # redirect stdin and stdout
        sys.stdin = StringIO()
        sys.stdout = StringIO()

    @classmethod
    def tearDownClass(cls) -> None:
        sys.stdin = sys.__stdin__
        sys.stdout = sys.__stdout__

        return super().tearDownClass()

    def prepare_input(self, *args: str):
        """Prepares the input, finally writing 'exit' at the end of the input chain."""

        self.session.prompt.side_effect = [*args, "exit"]

    def setUp(self):
        _clear_io()
        # prepare prompt input patcher
        self.patcher = patch("app.main.PromptSession")
        self.MockPromptSession = self.patcher.start()
        self.addCleanup(self.patcher.stop)
        self.session = self.MockPromptSession.return_value

    def test_shell_exit(self):
        self.prepare_input()
        self.assertRaises(SystemExit, main)

    def test_shell_echo(self):
        # patch the input
        with self.subTest("test whitespace echo"):
            self.prepare_input("echo hello world")
            out = _run_shell_suppress_exit()
            self.assertIn("hello world", out)

    def test_shell_type(self):

        with self.subTest("test type of builtin command"):
            self.prepare_input("type cd")
            # collect stdout contents
            out = _run_shell_suppress_exit()
            # first test: type cd returns builtin
            self.assertIn("shell builtin", out)

    def test_shell_pwd(self):
        correct_cwd = os.getcwd()
        self.prepare_input("pwd")
        out = _run_shell_suppress_exit()
        self.assertIn(correct_cwd, out)

    def test_shell_cd(self):
        initial_cwd = os.getcwd()
        with self.subTest("test empty cd"):
            # passes if exits with no other exception
            self.prepare_input("cd ")
            _ = _run_shell_suppress_exit()
        with self.subTest("test non-existing directory cd"):
            self.prepare_input("cd /bla-bla-bla/")
            out = _run_shell_suppress_exit()
            self.assertIn("No such file or directory", out)
            subtest_cwd = os.getcwd()
            self.assertEqual(initial_cwd, subtest_cwd)
        with self.subTest("test parent cd"):
            self.prepare_input("cd ../")
            _ = _run_shell_suppress_exit()
            subtest_cwd = os.getcwd()
            self.assertNotEqual(initial_cwd, subtest_cwd)


if __name__ == "__main__":
    unittest.main()
