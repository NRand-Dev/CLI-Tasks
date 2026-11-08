import contextlib
import io
import os
import tempfile
import unittest
from pathlib import Path
from unittest import mock

from ntasks import __version__
from ntasks.cli import main


class MainTests(unittest.TestCase):
    def setUp(self):
        temp_dir = tempfile.TemporaryDirectory()
        self.addCleanup(temp_dir.cleanup)
        self.data_file = Path(temp_dir.name) / "tasks.json"

        env = mock.patch.dict(os.environ, {"NTASKS_DATA_FILE": str(self.data_file)})
        env.start()
        self.addCleanup(env.stop)

    def run_cli(self, *argv):
        stdout = io.StringIO()
        stderr = io.StringIO()
        with contextlib.redirect_stdout(stdout), contextlib.redirect_stderr(stderr):
            code = main(list(argv))
        return code, stdout.getvalue(), stderr.getvalue()

    def test_list_with_no_tasks(self):
        self.assertEqual(self.run_cli("list"), (0, "No tasks.\n", ""))

    def test_add_prints_new_task(self):
        self.assertEqual(self.run_cli("add", "Buy milk"), (0, "Added task 1: Buy milk\n", ""))

    def test_list_shows_status_and_id(self):
        self.run_cli("add", "Buy milk")
        self.run_cli("add", "Walk dog")
        self.run_cli("done", "1")

        self.assertEqual(self.run_cli("list"), (0, "[x] 1  Buy milk\n[ ] 2  Walk dog\n", ""))

    def test_done_prints_task(self):
        self.run_cli("add", "Buy milk")

        self.assertEqual(self.run_cli("done", "1"), (0, "Completed task 1: Buy milk\n", ""))

    def test_delete_prints_task(self):
        self.run_cli("add", "Buy milk")

        self.assertEqual(self.run_cli("delete", "1"), (0, "Deleted task 1: Buy milk\n", ""))
        self.assertEqual(self.run_cli("list"), (0, "No tasks.\n", ""))

    def test_unknown_id_prints_error_and_returns_1(self):
        for command in ("done", "delete"):
            with self.subTest(command=command):
                code, stdout, stderr = self.run_cli(command, "99")

                self.assertEqual(code, 1)
                self.assertEqual(stdout, "")
                self.assertIn("no task with ID 99", stderr)

    def test_blank_title_prints_error_and_returns_1(self):
        code, stdout, stderr = self.run_cli("add", "   ")

        self.assertEqual(code, 1)
        self.assertEqual(stdout, "")
        self.assertIn("blank", stderr)

    def test_corrupt_file_prints_error_and_returns_1(self):
        self.data_file.write_text("{not json", encoding="utf-8")

        code, stdout, stderr = self.run_cli("list")

        self.assertEqual(code, 1)
        self.assertEqual(stdout, "")
        self.assertIn("not a valid tasks file", stderr)

    def test_non_numeric_id_exits_with_status_2(self):
        with contextlib.redirect_stderr(io.StringIO()):
            with self.assertRaises(SystemExit) as caught:
                main(["done", "abc"])

        self.assertEqual(caught.exception.code, 2)

    def test_version_prints_version(self):
        stdout = io.StringIO()
        with contextlib.redirect_stdout(stdout):
            code = main(["version"])

        self.assertEqual(code, 0)
        self.assertEqual(stdout.getvalue().strip(), f"ntasks-v: {__version__}")

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
