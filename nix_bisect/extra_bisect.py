"""Bisect runner with that little extra"""

import sys
import argparse
import subprocess
from nix_bisect import bisect_runner, git


def _main():
    parser = argparse.ArgumentParser(description="git-bisect with extra features")

    subparsers = parser.add_subparsers(
        title="subcommands", description="valid subcommands", help="additional help"
    )

    good_parser = subparsers.add_parser("good")
    good_parser.add_argument(
        "rev",
        type=str,
        default="HEAD",
        help="Revision that will be marked as good",
        nargs="?",
    )

    def _handle_good(args):
        print("Good")
        bisect_runner.bisect_good(args.rev)
        git.checkout(bisect_runner.BisectRunner().get_next())
        return 0

    good_parser.set_defaults(func=_handle_good)

    bad_parser = subparsers.add_parser("bad")
    bad_parser.add_argument(
        "rev",
        type=str,
        default="HEAD",
        help="Revision that will be marked as bad",
        nargs="?",
    )

    def _handle_bad(args):
        bisect_runner.bisect_bad(args.rev)
        git.checkout(bisect_runner.BisectRunner().get_next())
        return 0

    bad_parser.set_defaults(func=_handle_bad)

    skip_parser = subparsers.add_parser("skip")
    skip_parser.add_argument(
        "rev",
        type=str,
        default="HEAD",
        help="Revision that will be marked as belonging to the skip range",
        nargs="?",
    )
    skip_parser.add_argument(
        "--name",
        type=str,
        default="default",
        help="Name of the skip range, purely for display",
    )

    def _handle_skip(args):
        patchset = bisect_runner.read_patchset()
        bisect_runner.named_skip(args.name, patchset, args.rev)
        git.checkout(bisect_runner.BisectRunner().get_next())
        return 0

    skip_parser.set_defaults(func=_handle_skip)

    env_parser = subparsers.add_parser("env")
    env_parser.add_argument(
        "cmd", type=str, help="Command to run", default="bash", nargs="?",
    )
    env_parser.add_argument(
        "args", type=str, nargs=argparse.REMAINDER,
    )

    def _handle_env(args):
        patchset = bisect_runner.read_patchset()
        arg_list = bisect_runner.bisect_env_args(patchset)
        arg_list.append(args.cmd)
        arg_list.extend(args.args)
        return subprocess.call(["bisect-env"] + arg_list)

    env_parser.set_defaults(func=_handle_env)

    args = parser.parse_args()
    if not hasattr(args, "func"):
        parser.print_usage()
        return 128
    return args.func(args)


if __name__ == "__main__":
    sys.exit(_main())
