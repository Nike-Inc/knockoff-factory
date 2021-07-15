# Copyright 2021-present, Nike, Inc.
# All rights reserved.
#
# This source code is licensed under the Apache-2.0 license found in
# the LICENSE file in the root directory of this source tree.


import argparse
import inspect
import sys
import logging

from dependency_injector import containers

from knockoff.utilities.importlib_utils import resolve_package_name
from knockoff.sdk.db import KnockoffDB, DefaultDatabaseService


logger = logging.getLogger(__name__)


def run(knockoff_db: KnockoffDB,
        blueprint):
    dfs, knockoff_db = blueprint.construct(knockoff_db)
    knockoff_db.insert()
    logger.info("knockoff done.")


def _validate_container_class(cls, package_name):
    if not inspect.isclass(cls) or not issubclass(cls, containers.DeclarativeContainer):
        raise TypeError(f"{package_name} resolves to "
                         f"{cls} instead of "
                         f"a subclass of dependency_injector"
                         f".containers.DeclarativeContainer")


def seed(i):
    """TODO: move this to a utility module?"""
    import random
    import numpy as np
    from faker import Faker
    Faker.seed(i)
    np.random.seed(i)
    random.seed(i)
    logger.info(f"Seeds for Faker, Numpy, and random "
                f"modules have been set to {i}")


def parse_args(argv=None):
    parser = argparse.ArgumentParser(
        usage='''knockoff run [<args>]'''
    )
    parser.add_argument("-c", "--container",
                        default="knockoff.sdk.container.default:KnockoffContainer",
                        help="Default KnockoffContainer")
    parser.add_argument("--yaml-config",
                        help="Container configuration")
    parser.add_argument("-s", "--seed", type=int,
                        help="Set seed")
    return parser.parse_args(argv)


def main(argv=None):
    """
    TODO:
            - Add ephemeral flag for spinning up temporary database that's destroyed
              after program completion (with interactive program)
    """
    args = parse_args(argv)

    KnockoffContainer = resolve_package_name(args.container)
    _validate_container_class(KnockoffContainer, args.container)
    container = KnockoffContainer()
    container.init_resources()
    if args.yaml_config:
        container.config.from_yaml(args.yaml_config)
    container.wire(modules=[sys.modules[__name__]])

    if args.seed:
        seed(args.seed)

    knockoff_db = container.knockoff_db()
    blueprint = container.blueprint()
    run(knockoff_db, blueprint)


if __name__ == "__main__":
    sys.exit(main())
