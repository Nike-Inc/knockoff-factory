# Copyright 2021-present, Nike, Inc.
# All rights reserved.
#
# This source code is licensed under the Apache-2.0 license found in
# the LICENSE file in the root directory of this source tree.


from knockoff.utilities.testing.postgresql import get_postgresql
from knockoff.utilities.testing.mysql import ExternalMySql


def postgres_setup_teardown(url):
    # setup
    postgresql = get_postgresql(url=url) # create the database
    temp_url = postgresql.url()  # get temp url

    # return the temp url
    yield temp_url

    # teardown
    postgresql.stop()


def mysql_setup_teardown(url):
    # setup
    mysql = ExternalMySql(url=url) # create the database
    temp_url = mysql.url()  # get temp url

    # return the temp url
    yield temp_url

    # teardown
    mysql.stop()
