# Copyright 2021-present, Nike, Inc.
# All rights reserved.
#
# This source code is licensed under the Apache-2.0 license found in
# the LICENSE file in the root directory of this source tree.


import os
import re
import testing.postgresql
from uuid import uuid4
from sqlalchemy import create_engine
from sqlalchemy.pool import NullPool


TRUTH_VALUES =  {'1', 't', 'true'}

TEST_POSTGRES_ENABLED = os.getenv("TEST_POSTGRES_ENABLED",
                                  '1').lower() in TRUTH_VALUES

TEST_USE_EXTERNAL_DB = os.getenv('TEST_USE_EXTERNAL_DB',
                                 '1').lower() in TRUTH_VALUES


DEFAULT_URL = "postgresql://postgres@localhost:5432/postgres"


class ExternalPostgresql(object):
    def __init__(self, url=DEFAULT_URL,
                 db_name=None):

        self.db_name = db_name or 'test_' + str(uuid4()).replace('-', '')

        self.engine = create_engine(url)
        with self.engine.connect() as conn:
            conn.execute("commit")
            conn.execute("CREATE DATABASE {};".format(self.db_name))

    def url(self):
        # Substitute db name in URI with generated db
        url = re.sub(
            "(?:/[A-Za-z0-9_]+)$", "/{}".format(self.db_name), str(self.engine.url)
        )
        engine = create_engine(url, pool=NullPool)
        url = engine.url
        url = str(url)
        return url

    def __enter__(self):
        return self

    def __exit__(self, exception_type, exception_value, traceback):
        self.stop()

    def stop(self):
        terminate_connections_sql = (
            "SELECT pg_terminate_backend(pid) "
            "FROM pg_stat_activity "
            "WHERE datname ='{}'"
        ).format(self.db_name)

        with self.engine.connect() as conn:
            conn.execute("commit")
            conn.execute(terminate_connections_sql)
            conn.execute("DROP DATABASE {};".format(self.db_name))
        self.engine.dispose()


def get_postgresql(url=DEFAULT_URL):

    if TEST_USE_EXTERNAL_DB:
        return ExternalPostgresql(url=url)

    return testing.postgresql.Postgresql()
