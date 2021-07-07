# Copyright 2021-present, Nike, Inc.
# All rights reserved.
#
# This source code is licensed under the Apache-2.0 license found in
# the LICENSE file in the root directory of this source tree.


import os
import pytest
from collections import namedtuple

from faker import Faker
from numpy import random

from knockoff.testing_postgresql import get_postgresql
from knockoff.orm import get_engine, clear_default_env_vars, KNOCKOFF_DB_URI


MockDB = namedtuple('MockDB', ["engine", "url"])


KNOCKOFF_TEST_DB_URI = "KNOCKOFF_TEST_DB_URI"


@pytest.fixture(scope="function")
def empty_db():
    clear_default_env_vars()

    url = os.getenv(KNOCKOFF_TEST_DB_URI, "postgresql://postgres@localhost:5432/postgres")
    postgresql = get_postgresql(url=url)

    os.environ[KNOCKOFF_DB_URI] = postgresql.url()

    engine = get_engine()

    mock_db = MockDB(engine, postgresql.url())

    yield mock_db

    # tear down
    clear_default_env_vars()
    engine.dispose()
    postgresql.stop()


@pytest.fixture(scope="function")
def seed():
    Faker.seed(123)
    random.seed(123)
