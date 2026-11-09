import json
import os
import tempfile
import unittest
from pathlib import Path
from unittest import mock

from ntasks import store


class StoreTestCase(unittest.TestCase):
    def setUp(self):
        temp_dir = tempfile.TemporaryDirectory()
        self.addCleanup(temp_dir.cleanup)
        self.data_dir = Path(temp_dir.name)
        self.data_file = self.data_dir / "nested" / "tasks.json"

        env = mock.patch.dict(os.environ, {"NTASKS_DATA_FILE": str(self.data_file)})
        env.start()
        self.addCleanup(env.stop)


class TaskOperationTests(StoreTestCase):
    def test_missing_file_means_no_tasks(self):
        self.assertEqual(store.list_tasks(), [])
        self.assertFalse(self.data_file.exists())

    def test_add_creates_file_and_parent_directories(self):
        task = store.add_task("Buy milk")

        self.assertEqual(task.id, 1)
        self.assertEqual(task.title, "Buy milk")
        self.assertFalse(task.done)
        self.assertRegex(task.created_at, r"^\d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2}Z$")

        data = json.loads(self.data_file.read_text(encoding="utf-8"))
        self.assertEqual(data["next_id"], 2)
        self.assertEqual(data["tasks"][0]["title"], "Buy milk")

    def test_tasks_persist_between_calls(self):
        store.add_task("Buy milk")
        store.add_task("Walk dog")

        self.assertEqual([task.title for task in store.list_tasks()], ["Buy milk", "Walk dog"])

    def test_blank_title_is_rejected(self):
        with self.assertRaises(store.StoreError):
            store.add_task("   ")

        self.assertFalse(self.data_file.exists())

    def test_complete_marks_only_that_task(self):
        store.add_task("Buy milk")
        store.add_task("Walk dog")

        store.complete_task(1)

        self.assertEqual([task.done for task in store.list_tasks()], [True, False])

    def test_completing_twice_leaves_task_completed(self):
        store.add_task("Buy milk")

        store.complete_task(1)
        task = store.complete_task(1)

        self.assertTrue(task.done)

    def test_delete_removes_only_that_task(self):
        store.add_task("Buy milk")
        store.add_task("Walk dog")

        store.delete_task(1)

        self.assertEqual([task.title for task in store.list_tasks()], ["Walk dog"])

    def test_deleted_id_is_not_reused(self):
        store.add_task("Buy milk")
        store.add_task("Walk dog")
        store.delete_task(2)

        task = store.add_task("Read")

        self.assertEqual(task.id, 3)

    def test_ids_restart_at_1_when_list_is_empty(self):
        store.add_task("Buy milk")
        store.add_task("Walk dog")
        store.delete_task(1)
        store.delete_task(2)

        task = store.add_task("Read")

        self.assertEqual(task.id, 1)

    def test_unknown_id_raises_not_found(self):
        store.add_task("Buy milk")

        with self.assertRaises(store.TaskNotFoundError):
            store.complete_task(99)
        with self.assertRaises(store.TaskNotFoundError):
            store.delete_task(99)


class FileSafetyTests(StoreTestCase):
    def assert_rejected_and_unchanged(self, contents):
        self.data_file.parent.mkdir(parents=True)
        self.data_file.write_text(contents, encoding="utf-8")

        with self.assertRaises(store.StoreError):
            store.add_task("Buy milk")

        self.assertEqual(self.data_file.read_text(encoding="utf-8"), contents)

    def test_corrupt_json_gives_error_and_file_is_unchanged(self):
        self.assert_rejected_and_unchanged("{not json")

    def test_wrong_structure_gives_error_and_file_is_unchanged(self):
        self.assert_rejected_and_unchanged('{"tasks": []}')

    def test_non_integer_next_id_gives_error_and_file_is_unchanged(self):
        self.assert_rejected_and_unchanged('{"next_id": "2", "tasks": []}')

    def test_failed_save_keeps_original_file_and_removes_temp_file(self):
        store.add_task("Buy milk")
        original = self.data_file.read_text(encoding="utf-8")

        with mock.patch("ntasks.store.os.replace", side_effect=OSError("disk full")):
            with self.assertRaises(store.StoreError):
                store.add_task("Walk dog")

        self.assertEqual(self.data_file.read_text(encoding="utf-8"), original)
        self.assertEqual([path.name for path in self.data_file.parent.iterdir()], ["tasks.json"])


class DataFileLocationTests(unittest.TestCase):
    def test_xdg_data_home_is_used_when_no_override_is_set(self):
        env = {"NTASKS_DATA_FILE": "", "XDG_DATA_HOME": "/xdg"}
        with mock.patch.dict(os.environ, env):
            self.assertEqual(store._data_file(), Path("/xdg/ntasks/tasks.json"))

    def test_falls_back_to_local_share(self):
        env = {"NTASKS_DATA_FILE": "", "XDG_DATA_HOME": "", "HOME": "/home/someone"}
        with mock.patch.dict(os.environ, env):
            self.assertEqual(
                store._data_file(), Path("/home/someone/.local/share/ntasks/tasks.json")
            )


if __name__ == "__main__":
    unittest.main()
