import argparse
import sys

from ntasks import __version__, store


def cmd_version(args):
    print(f"ntasks-v: {__version__}")
    return 0


def cmd_add(args):
    task = store.add_task(args.add)
    print(f"Added task {task.id}: {task.title}")
    return 0


def cmd_list(args):
    tasks = store.list_tasks()
    if not tasks:
        print("No tasks.")
    for task in tasks:
        checkbox = "[x]" if task.done else "[ ]"
        print(f"{checkbox} {task.id}  {task.title}")
    return 0


def cmd_complete(args):
    task = store.complete_task(args.complete)
    print(f"Completed task {task.id}: {task.title}")
    return 0


def cmd_delete(args):
    task = store.delete_task(args.delete)
    print(f"Deleted task {task.id}: {task.title}")
    return 0


def _set_command(func):
    """Build an argparse action that stores the flag's value and records which command to run."""

    class SetCommand(argparse.Action):
        def __call__(self, parser, namespace, values, option_string=None):
            setattr(namespace, self.dest, values)
            namespace.func = func

    return SetCommand


def build_parser():
    parser = argparse.ArgumentParser(prog="ntasks", description="Track tasks from the command line.")
    commands = parser.add_argument_group("commands").add_mutually_exclusive_group()

    commands.add_argument(
        "-v", "--version", nargs=0, action=_set_command(cmd_version), help="print the version"
    )
    commands.add_argument(
        "-a", "--add", metavar="TITLE", action=_set_command(cmd_add),
        help="add a task (put the title in quotes if it has spaces)",
    )
    commands.add_argument(
        "-l", "--list", nargs=0, action=_set_command(cmd_list), help="list all tasks"
    )
    commands.add_argument(
        "-c", "--complete", metavar="ID", type=int, action=_set_command(cmd_complete),
        help="mark a task as completed",
    )
    commands.add_argument(
        "-d", "--delete", metavar="ID", type=int, action=_set_command(cmd_delete),
        help="delete a task",
    )

    return parser


def main(argv=None):
    parser = build_parser()
    args = parser.parse_args(argv)

    if not hasattr(args, "func"):
        parser.print_help()
        return 0

    try:
        return args.func(args)
    except store.StoreError as error:
        print(f"ntasks: error: {error}", file=sys.stderr)
        return 1
