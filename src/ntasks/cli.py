import argparse

from ntasks import __version__


def cmd_version(args):
    print(__version__)
    return 0


def build_parser():
    parser = argparse.ArgumentParser(prog="ntasks", description="Track tasks from the command line.")
    subparsers = parser.add_subparsers(title="commands")

    version_parser = subparsers.add_parser("version", help="print the version")
    version_parser.set_defaults(func=cmd_version)

    return parser


def main(argv=None):
    parser = build_parser()
    args = parser.parse_args(argv)

    if not hasattr(args, "func"):
        parser.print_help()
        return 0

    return args.func(args)
