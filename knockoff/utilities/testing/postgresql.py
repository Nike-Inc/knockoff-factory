# Copyright 2021-present, Nike, Inc.
# All rights reserved.
#
# This source code is licensed under the Apache-2.0 license found in
# the LICENSE file in the root directory of this source tree.

import os
import testing.postgresql

from .base import ExternalDB, TEST_USE_EXTERNAL_DB, TRUTH_VALUES


DEFAULT_URL = "postgresql://postgres@localhost:5432/postgres"

TEST_POSTGRES_ENABLED = os.getenv(
    "TEST_POSTGRES_ENABLED",
    "1"
).lower() in TRUTH_VALUES


def postgres_create_db(engine, db_name):
    with engine.connect() as conn:
        conn.execute("commit")
        conn.execute(f"CREATE DATABASE {db_name};")


def postgres_drop_db(engine, db_name):
    terminate_connections_sql = (
        f"SELECT pg_terminate_backend(pid) "
        f"FROM pg_stat_activity "
        f"WHERE datname ='{db_name}'"
    )

    with engine.connect() as conn:
        conn.execute("commit")
        conn.execute(terminate_connections_sql)
        conn.execute("DROP DATABASE {};".format(db_name))


class ExternalPostgresql(ExternalDB):
    def __init__(self,
                 url=DEFAULT_URL,
                 db_name=None):
        super().__init__(url,
                         postgres_create_db,
                         postgres_drop_db,
                         db_name=db_name)


def get_postgresql(url=DEFAULT_URL):

    if TEST_USE_EXTERNAL_DB:
        return ExternalPostgresql(url=url)

    return testing.postgresql.Postgresql()
