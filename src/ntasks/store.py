import json
import os
import tempfile
from dataclasses import asdict
from datetime import datetime, timezone
from pathlib import Path

from ntasks.models import Task


class StoreError(Exception):
    """A task could not be read, saved, or created."""


class TaskNotFoundError(StoreError):
    """No task has the requested ID."""


def add_task(title):
    title = title.strip()
    if not title:
        raise StoreError("task title cannot be blank")

    next_id, tasks = _load()
    created_at = datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")
    task = Task(id=next_id, title=title, done=False, created_at=created_at)
    tasks.append(task)
    _save(next_id + 1, tasks)
    return task


def list_tasks():
    _, tasks = _load()
    return sorted(tasks, key=lambda task: task.id)


def complete_task(task_id):
    next_id, tasks = _load()
    task = _find(tasks, task_id)
    if not task.done:
        task.done = True
        _save(next_id, tasks)
    return task


def delete_task(task_id):
    next_id, tasks = _load()
    task = _find(tasks, task_id)
    tasks.remove(task)
    _save(next_id, tasks)
    return task


def _find(tasks, task_id):
    for task in tasks:
        if task.id == task_id:
            return task
    raise TaskNotFoundError(f"no task with ID {task_id}")


def _data_file():
    override = os.environ.get("NTASKS_DATA_FILE")
    if override:
        return Path(override)

    xdg_data_home = os.environ.get("XDG_DATA_HOME")
    data_home = Path(xdg_data_home) if xdg_data_home else Path.home() / ".local" / "share"
    return data_home / "ntasks" / "tasks.json"


def _load():
    path = _data_file()
    try:
        data = json.loads(path.read_text(encoding="utf-8"))
        next_id = data["next_id"]
        tasks = [Task(**item) for item in data["tasks"]]
    except FileNotFoundError:
        return 1, []
    except OSError as error:
        raise StoreError(f"could not read {path}: {error}") from error
    except (ValueError, KeyError, TypeError) as error:
        raise StoreError(f"{path} is not a valid tasks file") from error

    if not isinstance(next_id, int):
        raise StoreError(f"{path} is not a valid tasks file")
    return next_id, tasks


def _save(next_id, tasks):
    path = _data_file()
    data = {"next_id": next_id, "tasks": [asdict(task) for task in tasks]}
    temp_name = None
    try:
        path.parent.mkdir(parents=True, exist_ok=True)
        # Write to a temporary file first, so a crash can't leave a half-written tasks file.
        fd, temp_name = tempfile.mkstemp(dir=path.parent, prefix=f".{path.name}.")
        with os.fdopen(fd, "w", encoding="utf-8") as temp_file:
            json.dump(data, temp_file, indent=2)
            temp_file.write("\n")
            temp_file.flush()
            os.fsync(temp_file.fileno())
        os.replace(temp_name, path)
    except OSError as error:
        if temp_name is not None:
            Path(temp_name).unlink(missing_ok=True)
        raise StoreError(f"could not save {path}: {error}") from error
