# Copyright 2021-present, Nike, Inc.
# All rights reserved.
#
# This source code is licensed under the Apache-2.0 license found in
# the LICENSE file in the root directory of this source tree.


import os
from .base import ExternalDB, TRUTH_VALUES

DEFAULT_URL = "mysql+pymysql://root@localhost:3306/mysql"

TEST_MYSQL_ENABLED = os.getenv(
    "TEST_MYSQL_ENABLED",
    "1"
).lower() in TRUTH_VALUES


def mysql_create_db(engine, db_name):
    with engine.connect() as conn:
        conn.execute("CREATE DATABASE {};".format(db_name))


def mysql_drop_db(engine, db_name):
    terminate_connections_sql = (
        f"SELECT "
        f"CONCAT('KILL ', id, ';') "
        f"FROM INFORMATION_SCHEMA.PROCESSLIST "
        f"WHERE `db` = '{db_name}';"
    )

    with engine.connect() as conn:
        conn.execute(terminate_connections_sql)
        conn.execute(f"DROP DATABASE {db_name};")


class ExternalMySql(ExternalDB):
    def __init__(self,
                 url=DEFAULT_URL,
                 db_name=None):
        super().__init__(url,
                         mysql_create_db,
                         mysql_drop_db,
                         db_name=db_name)
