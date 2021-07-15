# Copyright 2021-present, Nike, Inc.
# All rights reserved.
#
# This source code is licensed under the Apache-2.0 license found in
# the LICENSE file in the root directory of this source tree.


import os
import sys
import pipes
import argparse
import yaml
import subprocess
import logging

import sqlalchemy_utils
from sqlalchemy import create_engine
from sqlalchemy.exc import ProgrammingError

from knockoff.utilities.functools import call_with_args_kwargs
from .utilities.orm.sql import EngineBuilder

from . import orm, __version__
from .io import ReaderFactory
from .knockoff import Knockoff
from .cli_v2 import setup_logger


logger = logging.getLogger(__name__)


def shlex_join(cmd):
    return " ".join(map(pipes.quote, cmd))


def _add_flag_from_env(env_var, flag, cmd):
    if env_var in os.environ:
        cmd.append(flag)
        cmd.append(os.environ[env_var])


def assert_supported_db_action(db_type):
    assert db_type in {'postgres'}, ("database.type={} "
                                     "is not supported"
                                     "for this operation."
                                     .format(db_type))


def create_databases(create_database_configs):
    for config in create_database_configs:
        db_type = config.get('type')
        engine_config = config.get('config')
        if engine_config:
            engine = EngineBuilder.from_config(engine_config)
        else:
            engine = orm.get_engine()
        assert_supported_db_action(db_type)

        parts = str(engine.url).split('/')
        url = '/'.join(parts[:-1] + [config['name']])

        if sqlalchemy_utils.database_exists(url):
            logger.info("{} already exists. Skipping creation."
                        .format(config["name"]))
        else:
            # the following two lines remove configuration to specific db
            url = '/'.join(parts[:-1])
            engine = create_engine(url)
            orm.create_database(config['name'], engine=engine)
        for user_config in config.get('users', []):
            assert_supported_db_action(db_type)
            password = os.environ[user_config['password_env']]
            try:
                orm.create_user(user_config['user'], password,
                                engine=engine)
                orm.execute("grant all privileges on database {} to {};"
                            .format(config['name'], user_config['user']),
                            engine=engine)
            except ProgrammingError as e:
                logger.error(e)
                logger.warning("Error creating user. Most likely exists."
                               "Skipping this step.")


def load_schemas(yamltodb_configs):
    for config in yamltodb_configs:
        logger.info("Loading tables from {} to database: {}"
                    .format(config['path'], config['database']))
        cmd = []
        if orm.KNOCKOFF_DB_PASSWORD in os.environ:
            cmd.append("{}={}".format('PGPASSWORD',
                                      os.environ[orm
                                                 .KNOCKOFF_DB_PASSWORD]))
        cmd.append("yamltodb")
        _add_flag_from_env(orm.KNOCKOFF_DB_HOST, "-H", cmd)
        _add_flag_from_env(orm.KNOCKOFF_DB_USER, "-U", cmd)
        cmd.append(config['database'])
        cmd.append(config['path'])
        cmd.append("--update")
        subprocess.check_call(shlex_join(cmd), shell=True)
        logger.info("Loaded tables from {} to database: {}"
                    .format(config['path'], config['database']))


def load_df_from_source(source):
    reader = ReaderFactory().get_resource(source['reader'])
    args = source.get('args')
    kwargs = source.get('kwargs')

    return call_with_args_kwargs(reader, args, kwargs)


def parse_args(argv=None):
    parser = argparse.ArgumentParser()
    parser.add_argument("-c", "--config",
                        default=os.environ.get('KNOCKOFF_CONFIG',
                                               'knockoff.yaml'),
                        help="path to knockoff config")
    parser.add_argument("-s", "--seed",
                        type=int,
                        default=os.environ.get('KNOCKOFF_SEED'),
                        help="path to knockoff config")
    parser.add_argument("-v", "--verbose",
                        action="store_true",
                        help="verbose logging")
    parser.add_argument("--version",
                        action="store_true",
                        help="print knockoff version")
    args = parser.parse_args(argv)
    return args


def main(argv=None):
    args = parse_args(argv)

    if args.version:
        print(__version__)
        sys.exit(0)

    setup_logger(args.verbose)

    with open(args.config, 'rb') as configfile:
        config = yaml.safe_load(configfile)

    create_databases(config.get('create-databases', []))

    if 'yamltodb' in config:
        load_schemas(config['yamltodb'])

    Knockoff(config, seed=args.seed)


if __name__ == "__main__":
    main()
