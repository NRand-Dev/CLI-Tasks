# ntasks

A small command-line task tracker written in Python. Tasks are stored in a local JSON file, and the only dependency is the standard library.

```console
$ ntasks -a "Buy milk"
Added task 1: Buy milk
$ ntasks -a "Walk dog"
Added task 2: Walk dog
$ ntasks -c 1
Completed task 1: Buy milk
$ ntasks -l
--- TASK LIST ---
ID: 1 - [x] Buy milk
ID: 2 - [ ] Walk dog
```

## Requirements

- Python 3.10 or newer

## Installation

Clone the repository and install it with pip (a virtual environment is recommended):

```sh
git clone https://github.com/NRand-Dev/CLI-Tasks.git
cd CLI-Tasks
python3 -m venv .venv
source .venv/bin/activate
pip install .
```

This puts the `ntasks` command on your `PATH`. Use `pip install -e .` instead if you plan to edit the code.

To install it for your user without a virtual environment, you can use [pipx](https://pipx.pypa.io/): `pipx install .`

You can also run it from a checkout without installing it:

```sh
PYTHONPATH=src python3 -m ntasks -l
```

## Usage

```
ntasks [-v | -a TITLE | -l | -c ID | -d ID]
```

| Flag | Long form | Description |
| --- | --- | --- |
| `-a TITLE` | `--add TITLE` | Add a task. Quote the title if it contains spaces. |
| `-l` | `--list` | List all tasks, ordered by ID. |
| `-c ID` | `--complete ID` | Mark a task as completed. |
| `-d ID` | `--delete ID` | Delete a task. |
| `-v` | `--version` | Print the version. |
| `-h` | `--help` | Show help. |

Only one command can be given at a time. Running `ntasks` with no arguments prints the help text.

### Task IDs

Each new task gets the next available ID. IDs of deleted tasks are not reused while other tasks still exist. Once the list is empty, numbering starts again at 1.

### Exit codes

| Code | Meaning |
| --- | --- |
| `0` | Success |
| `1` | Task error, such as an unknown ID, a blank title, or an unreadable or invalid tasks file |
| `2` | Invalid usage, such as an unknown flag, a non-numeric ID, or two commands at once |

Error messages are written to stderr.

## Data storage

Tasks are saved to:

1. `$NTASKS_DATA_FILE`, if set
2. otherwise `$XDG_DATA_HOME/ntasks/tasks.json`, if `XDG_DATA_HOME` is set
3. otherwise `~/.local/share/ntasks/tasks.json`

The file and its parent directories are created on first use. Saves go to a temporary file that then replaces the original, so an interrupted write cannot leave a half-written tasks file. If the file is corrupt or has an unexpected structure, ntasks reports an error and leaves it untouched.

The file looks like this:

```json
{
  "next_id": 3,
  "tasks": [
    {
      "id": 1,
      "title": "Buy milk",
      "done": true,
      "created_at": "2026-11-09T14:02:11Z"
    },
    {
      "id": 2,
      "title": "Walk dog",
      "done": false,
      "created_at": "2026-11-09T14:02:15Z"
    }
  ]
}
```

To keep a separate list, for example per project, point `NTASKS_DATA_FILE` at a different file:

```sh
NTASKS_DATA_FILE=./project-tasks.json ntasks -l
```

## Development

### Project layout

```
src/ntasks/
├── __init__.py   # package version
├── __main__.py   # entry point for `python -m ntasks`
├── cli.py        # argument parsing and command output
├── models.py     # Task dataclass
└── store.py      # loading and saving the JSON tasks file
tests/
├── test_cli.py   # end-to-end tests for the CLI
└── test_store.py # tests for the storage layer
```

### Running tests

The tests use the standard library's `unittest` and write to a temporary data file, so they never touch your real tasks.

```sh
PYTHONPATH=src python3 -m unittest discover -s tests
```

If the package is installed (for example with `pip install -e .`), you can leave out `PYTHONPATH=src`.
