# Copyright 2021-present, Nike, Inc.
# All rights reserved.
#
# This source code is licensed under the Apache-2.0 license found in
# the LICENSE file in the root directory of this source tree.


import os
import argparse
import logging
import sys

from .utilities.mixin import ResourceLocatorMixin


logger = logging.getLogger(__name__)


class KnockoffCLI(ResourceLocatorMixin):
    entry_point_group = "knockoff.cli.command"

    @property
    def usage(self):
        _usage = ["knockoff <command> [<args>]",
                  "The most commonly used knockoff commands are:"]

        description = {
            "legacy": ("Load data into a database "
                       "based on the legacy yaml "
                       "configuration"),
            "run": "Load data into a database given "
                   "a knockoff_db path",
            "version": "Print knockoff version",
        }

        for key in sorted(self.get_resource_names()):
            try:
                _usage.append("{command}\t\t{description}".format(
                    command=key, description=description[key]
                ))
            except KeyError:
                raise TypeError(f"Missing usage description for {key}")

        return "\n".join(_usage)

    def __init__(self, argv=None):
        parser = argparse.ArgumentParser(
            description="knockoff cli",
            usage=self.usage
        )
        parser.add_argument('command',
                            choices=self.get_resource_names(),
                            help="Subcommand to run",
                            metavar="COMMAND")
        # parse_args defaults to [1:] for args, but you need to
        # exclude the rest of the args too, or validation will fail
        argv = argv or sys.argv
        args = parser.parse_args(argv[1:2])
        command = self.get_resource(args.command)
        command(argv[2:])


def setup_logger(verbose=False):
    level = logging.DEBUG if verbose else (os.environ
                                             .get('KNOCKOFF_LOG_LEVEL',
                                                  'INFO').upper())
    format_ = os.environ.get('KNOCKOFF_LOG_FORMAT',
                            ('[%(asctime)s] [%(name)s] [%(processName)s]'
                             ' [%(levelname)s]: %(message)s'))
    logging.basicConfig(format=format_,
                        level=level)


def main(argv=None):
    setup_logger()
    KnockoffCLI(argv=argv)


if __name__ == "__main__":
    sys.exit(main())
