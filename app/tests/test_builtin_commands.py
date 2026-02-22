import unittest
from app.main import main
import sys
from io import StringIO


def write_stdin_reset_cursor(raw_str: str):
    sys.stdin.write(raw_str)
    sys.stdin.seek(0)


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
        # Clear stdin and stdout
        sys.stdin.truncate(0)
        sys.stdout.truncate(0)
        sys.stdin.seek(0)
        sys.stdout.seek(0)

    def test_shell_exit(self):
        sys.stdin.write("exit")
        sys.stdin.seek(0)  # Reposition cursor at beginning of command
        self.assertRaises(SystemExit, main)

    def test_shell_type(self):
        
        with self.subTest("test type of builtin command"):
            write_stdin_reset_cursor("""type cd
                                    exit
                                    """)
            self.assertRaises(SystemExit, main)

            # collect stdout contents
            sys.stdout.seek(0)
            collected_output = sys.stdout.read()
            line = collected_output
            # first test: type cd returns builtin
            self.assertIn("shell builtin", line)

        

if __name__ == "__main__":
    unittest.main()
