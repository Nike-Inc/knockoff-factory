# Copyright 2021-present, Nike, Inc.
# All rights reserved.
#
# This source code is licensed under the Apache-2.0 license found in
# the LICENSE file in the root directory of this source tree.


import argparse
import sys
import logging

from knockoff.utilities.ioc import get_container
from knockoff.sdk.db import KnockoffDB, DefaultDatabaseService
from knockoff.sdk.blueprint import Blueprint
from knockoff.tempdb.db import TempDatabaseService

logger = logging.getLogger(__name__)


def testable_input(prompt=None, **kwargs):
    """pass through input so this can be unit tested"""
    input(prompt)


def run(knockoff_db: KnockoffDB,
        blueprint: Blueprint,
        temp_db: TempDatabaseService = None):

    if temp_db:
        temp_url = temp_db.start()
        logger.info("TempDatabaseService created temp database:\n"
                    f"{temp_url}")

    dfs, knockoff_db = blueprint.construct(knockoff_db)
    knockoff_db.insert()
    logger.info("knockoff data successfully loaded into database.")

    if temp_db:
        try:
            testable_input(
                "Press Enter when finished to destroy temp database.",
                # the following kwargs can be used by a mock for assertions
                test_temp_url=temp_url,
                test_temp_db=temp_db,
                test_blueprint=blueprint,
                test_knockoff_db=knockoff_db,
            )
        finally:
            temp_db.stop()

    logger.info("knockoff done.")


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
    parser.add_argument("--ephemeral",
                        action="store_true",
                        help="flag to run interactively with an ephemeral database")
    parser.add_argument("--tempdb-container",
                        default="knockoff.tempdb.container:TempDBContainer",
                        help="Default TempDBContainer")
    parser.add_argument("-s", "--seed", type=int,
                        help="Set seed")
    return parser.parse_args(argv)


def main(argv=None):
    args = parse_args(argv)

    if args.seed:
        seed(args.seed)

    container = get_container(args.container, args.yaml_config)
    knockoff_db = container.knockoff_db()
    blueprint = container.blueprint()
    temp_db = None

    if args.ephemeral:
        tempdb_container = get_container(args.tempdb_container, args.yaml_config)
        temp_db = tempdb_container.temp_db()

    run(knockoff_db, blueprint, temp_db=temp_db)


if __name__ == "__main__":
    sys.exit(main())
