# Copyright 2021-present, Nike, Inc.
# All rights reserved.
#
# This source code is licensed under the Apache-2.0 license found in
# the LICENSE file in the root directory of this source tree.


import pandas as pd
from sqlalchemy.pool import NullPool

from .utilities.orm.sql import EngineBuilder
from .utilities.environ import clear_env_vars


KNOCKOFF_DB_URI = 'KNOCKOFF_DB_URI'
KNOCKOFF_DB_USER = 'KNOCKOFF_DB_USER'
KNOCKOFF_DB_PASSWORD = 'KNOCKOFF_DB_PASSWORD'
KNOCKOFF_DB_HOST = 'KNOCKOFF_DB_HOST'
KNOCKOFF_DB_PORT = 'KNOCKOFF_DB_PORT'
KNOCKOFF_DB_NAME = 'KNOCKOFF_DB_NAME'
KNOCKOFF_DB_DIALECT = 'KNOCKOFF_DB_DIALECT'
KNOCKOFF_DB_DRIVER = 'KNOCKOFF_DB_DRIVER'


def execute(sql, engine=None):
    engine = engine or get_engine()
    with engine.connect() as conn:
        conn.execute("commit")
        conn.execute(sql)


def create_database(database, engine=None):
    engine = engine or get_engine()
    execute("create database {};".format(database),
            engine=engine)


def create_user(user, password, engine=None):
    engine = engine or get_engine()
    execute("create user {} with encrypted password '{}';"
            .format(user, password),
            engine=engine)


DEFAULT_BUILDER = (EngineBuilder()
                   .uri(env_var=KNOCKOFF_DB_URI)
                   .host(env_var=KNOCKOFF_DB_HOST)
                   .port(env_var=KNOCKOFF_DB_PORT)
                   .user(env_var=KNOCKOFF_DB_USER)
                   .password(env_var=KNOCKOFF_DB_PASSWORD)
                   .database(env_var=KNOCKOFF_DB_NAME)
                   .dialect(env_var=KNOCKOFF_DB_DIALECT)
                   .driver(env_var=KNOCKOFF_DB_DRIVER))


ENGINE_BUILDERS = {
    "default": DEFAULT_BUILDER
}


def clear_default_env_vars():
    clear_env_vars([KNOCKOFF_DB_URI,
                    KNOCKOFF_DB_USER,
                    KNOCKOFF_DB_PASSWORD,
                    KNOCKOFF_DB_HOST,
                    KNOCKOFF_DB_PORT,
                    KNOCKOFF_DB_DIALECT,
                    KNOCKOFF_DB_DRIVER,
                    KNOCKOFF_DB_NAME,
                    KNOCKOFF_DB_URI])


def register_engine(name, config):
    global ENGINE_BUILDERS
    ENGINE_BUILDERS[name] = EngineBuilder.from_config(config, build='builder',
                                                      poolclass=NullPool)


def reset_engines():
    global ENGINE_BUILDERS
    ENGINE_BUILDERS = {
        "default": DEFAULT_BUILDER
    }


def get_engine(name=None, build='engine', **kwargs):
    assert build in {'engine', 'builder'}
    kwargs.setdefault('poolclass', NullPool)
    name = name or "default"
    if build == 'engine':
        return ENGINE_BUILDERS[name].build(**kwargs)
    if build == 'builder':
        return ENGINE_BUILDERS[name]


def get_connection(database=None):
    engine = get_engine(database)
    return engine.connect()


def get_child_tables(partitioned_table_name, engine=None):
    """get child tables for partitioned postgres table"""
    sql = (
        "SELECT "
        "nmsp_parent.nspname AS parent_schema, "
        "parent.relname      AS parent, "
        "nmsp_child.nspname  AS child_schema, "
        "child.relname       AS child "
        "FROM pg_inherits "
        "JOIN pg_class parent            ON pg_inherits.inhparent = parent.oid "
        "JOIN pg_class child             ON pg_inherits.inhrelid   = child.oid "
        "JOIN pg_namespace nmsp_parent   ON nmsp_parent.oid  = parent.relnamespace "
        "JOIN pg_namespace nmsp_child    ON nmsp_child.oid   = child.relnamespace "
        "WHERE parent.relname='{table}';"
    ).format(table=partitioned_table_name)
    engine = engine or get_engine()
    with engine.connect() as conn:
        df = pd.read_sql_query(sql, conn)
    return df["child"].tolist()
