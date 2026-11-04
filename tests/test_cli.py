import contextlib
import io
import unittest

from ntasks import __version__
from ntasks.cli import main


class MainTests(unittest.TestCase):
    def test_version_prints_version(self):
        stdout = io.StringIO()
        with contextlib.redirect_stdout(stdout):
            code = main(["version"])

        self.assertEqual(code, 0)
        self.assertEqual(stdout.getvalue().strip(), __version__)

    def test_no_arguments_prints_help(self):
        stdout = io.StringIO()
        with contextlib.redirect_stdout(stdout):
            code = main([])

        self.assertEqual(code, 0)
        self.assertIn("usage: ntasks", stdout.getvalue())

    def test_unknown_command_exits_with_status_2(self):
        with contextlib.redirect_stderr(io.StringIO()):
            with self.assertRaises(SystemExit) as caught:
                main(["nonsense"])

        self.assertEqual(caught.exception.code, 2)


if __name__ == "__main__":
    unittest.main()
