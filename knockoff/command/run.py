# Copyright 2021-present, Nike, Inc.
# All rights reserved.
#
# This source code is licensed under the Apache-2.0 license found in
# the LICENSE file in the root directory of this source tree.

import os
import argparse
import sys
import logging

from knockoff.utilities.environ import clear_env_vars
from knockoff.utilities.ioc import get_container
from knockoff.sdk.db import KnockoffDB, DefaultDatabaseService
from knockoff.sdk.blueprint import Blueprint

logger = logging.getLogger(__name__)


DEFAULT_KNOCKOFF_CONTAINER = "knockoff.sdk.container.default:KnockoffContainer"
DEFAULT_TEMPDB_CONTAINER = "knockoff.tempdb.container:TempDBContainer"

KNOCKOFF_RUN_DB_URL_ENV = "KNOCKOFF_RUN_DB_URL"
KNOCKOFF_RUN_BLUEPRINT_PLAN_ENV = "KNOCKOFF_RUN_BLUEPRINT_PLAN"


def clear_run_env_vars():
    clear_env_vars([
        KNOCKOFF_RUN_DB_URL_ENV,
        KNOCKOFF_RUN_BLUEPRINT_PLAN_ENV
    ])


def testable_input(prompt=None, **kwargs):
    """pass through input so this can be unit tested"""
    input(prompt)


def run(knockoff_db: KnockoffDB,
        blueprint: Blueprint):
    dfs, knockoff_db = blueprint.construct(knockoff_db)
    knockoff_db.insert()
    logger.info("knockoff data successfully loaded into database.")


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


def default_config(container_package):
    return {
        DEFAULT_KNOCKOFF_CONTAINER: {
            "database_service": {
                "url": os.getenv(
                    KNOCKOFF_RUN_DB_URL_ENV,
                    "postgresql://postgres@localhost:5432/postgres"
                )
            },
            "blueprint": {
                "plan": {
                    "package": os.getenv(
                        KNOCKOFF_RUN_BLUEPRINT_PLAN_ENV,
                        "knockoff.sdk.blueprint:noplan"
                    )
                }
            }
        },
        DEFAULT_TEMPDB_CONTAINER: {
            "tempdb": {
                "url": os.getenv(
                    KNOCKOFF_RUN_DB_URL_ENV,
                    "postgresql://postgres@localhost:5432/postgres"
                ),
                "setup_teardown": {
                    "package": "knockoff.tempdb.setup_teardown:postgres_setup_teardown"
                }
            }
        }
    }.get(container_package)


def parse_args(argv=None):
    parser = argparse.ArgumentParser(
        usage='''knockoff run [<args>]'''
    )
    parser.add_argument("-c", "--container",
                        default=DEFAULT_KNOCKOFF_CONTAINER,
                        help="Default KnockoffContainer")
    parser.add_argument("--yaml-config",
                        help="Container configuration")
    parser.add_argument("--ephemeral",
                        action="store_true",
                        help="flag to run interactively with an ephemeral database")
    parser.add_argument("--tempdb-container",
                        default=DEFAULT_TEMPDB_CONTAINER,
                        help="Default TempDBContainer")
    parser.add_argument("-s", "--seed", type=int,
                        help="Set seed")
    return parser.parse_args(argv)


def main(argv=None):
    args = parse_args(argv)

    if args.seed:
        seed(args.seed)

    override_dict = None

    if args.ephemeral:
        tempdb_container = get_container(
            args.tempdb_container,
            config_path=args.yaml_config,
            default_dict=default_config(args.tempdb_container)
        )

        temp_db = tempdb_container.temp_db()
        temp_url = temp_db.start()
        logger.info("TempDatabaseService created temp database:\n"
                    f"{temp_url}")

        # this overrides the configured url for the database service
        # with temp_url
        override_dict = {"database_service": {"url": temp_url}}

    container = get_container(
        args.container,
        config_path=args.yaml_config,
        default_dict=default_config(args.container),
        override_dict=override_dict
    )

    knockoff_db = container.knockoff_db()
    blueprint = container.blueprint()

    run(knockoff_db, blueprint)

    if args.ephemeral:
        try:
            testable_input(
                "Press Enter when finished to destroy temp database.",
                # the following kwargs are used by a mock for assertions
                test_temp_url=temp_url,
                test_temp_db=temp_db,
                test_blueprint=blueprint,
                test_knockoff_db=knockoff_db,
            )
        finally:
            temp_db.stop()

    logger.info("knockoff done.")


if __name__ == "__main__":
    sys.exit(main())
