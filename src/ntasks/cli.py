import argparse
import sys

from ntasks import __version__, store


def cmd_version(args):
    print(f"ntasks-v: {__version__}")
    return 0


def cmd_add(args):
    task = store.add_task(args.title)
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


def cmd_done(args):
    task = store.complete_task(args.id)
    print(f"Completed task {task.id}: {task.title}")
    return 0


def cmd_delete(args):
    task = store.delete_task(args.id)
    print(f"Deleted task {task.id}: {task.title}")
    return 0


def build_parser():
    parser = argparse.ArgumentParser(prog="ntasks", description="Track tasks from the command line.")
    subparsers = parser.add_subparsers(title="commands")

    version_parser = subparsers.add_parser("version", help="print the version")
    version_parser.set_defaults(func=cmd_version)

    add_parser = subparsers.add_parser("add", help="add a task")
    add_parser.add_argument("title", help="the task title, in quotes if it has spaces")
    add_parser.set_defaults(func=cmd_add)

    list_parser = subparsers.add_parser("list", help="list all tasks")
    list_parser.set_defaults(func=cmd_list)

    done_parser = subparsers.add_parser("done", help="mark a task as completed")
    done_parser.add_argument("id", type=int, help="the task ID")
    done_parser.set_defaults(func=cmd_done)

    delete_parser = subparsers.add_parser("delete", help="delete a task")
    delete_parser.add_argument("id", type=int, help="the task ID")
    delete_parser.set_defaults(func=cmd_delete)

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
