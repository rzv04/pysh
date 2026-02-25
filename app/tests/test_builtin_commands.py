import unittest
from app.main import main, preprocess_args
import sys
from io import StringIO
import os


def _write_stdin_reset_cursor(raw_str: str):
    sys.stdin.write(raw_str)
    sys.stdin.seek(0)


def _run_shell_suppress_exit(raw_str: str) -> str:
    """Runs the shell program by writing the raw str in its format inside (mocked) stdin,
    collects the stdout contents then resets stdin and stdout.
    The chain should not contain the 'exit' command, as it is inserted by this function.

    Args:
        raw_str (str): The command or chain of commands to be tested

    Returns:
        str: The collected output from stdout
    """
    _write_stdin_reset_cursor(raw_str + "\nexit\n")
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

    def setUp(self):
        _clear_io()

    def test_shell_exit(self):
        sys.stdin.write("exit")
        sys.stdin.seek(0)  # Reposition cursor at beginning of command
        self.assertRaises(SystemExit, main)

    def test_shell_echo(self):
        with self.subTest("test whitespace echo"):
            out = _run_shell_suppress_exit("echo ")
            # self.assertIs(bool(out), False, f"out={out}")
            self.assertEqual("$ \n$ ", out)

    def test_shell_type(self):

        with self.subTest("test type of builtin command"):
            # collect stdout contents
            collected_output = _run_shell_suppress_exit("type cd")
            line = collected_output
            # first test: type cd returns builtin
            self.assertIn("shell builtin", line)

    def test_shell_pwd(self):
        correct_cwd = os.getcwd()
        out_result = _run_shell_suppress_exit("pwd")
        self.assertIn(correct_cwd, out_result)

    def test_shell_cd(self):
        initial_cwd = os.getcwd()
        with self.subTest("test empty cd"):
            # passes if exits with no other exception
            _ = _run_shell_suppress_exit("cd ")
        with self.subTest("test non-existing directory cd"):
            out = _run_shell_suppress_exit("cd /bla-bla-bla/")
            self.assertIn("No such file or directory", out)
            subtest_cwd = os.getcwd()
            self.assertEqual(initial_cwd, subtest_cwd)
        with self.subTest("test parent cd"):
            out = _run_shell_suppress_exit("cd ../")
            subtest_cwd = os.getcwd()
            self.assertNotEqual(initial_cwd, subtest_cwd)

    @unittest.skip("deprecated")
    def test_preprocess_args(self):
        with self.subTest("test simple single quoted arg"):
            args = "'hello  world'"
            processed_args = preprocess_args(args)
            self.assertEqual(processed_args, ["hello  world"])

        with self.subTest("test no quoted arg"):
            args = "hello world"
            processed_args = preprocess_args(args)
            self.assertEqual(processed_args, ["hello", "world"])

        with self.subTest("test quoted arg with double quotes inside"):
            args = "'hello''world'"
            processed_args = preprocess_args(args)
            self.assertEqual(processed_args, ["helloworld"])

        with self.subTest("test complex quoted arg"):
            args = "'example     hello' 'world''test' shell''script"
            processed_args = preprocess_args(args)
            self.assertEqual(
                processed_args, ["example     hello worldtest shellscript"]
            )


if __name__ == "__main__":
    unittest.main()
