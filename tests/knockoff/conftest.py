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

from knockoff.orm import get_engine, clear_default_env_vars, KNOCKOFF_DB_URI
from knockoff.tempdb.db import TempDatabaseService

from .data_model import Base


MockDB = namedtuple('MockDB', ["engine", "url"])

KNOCKOFF_TEST_DB_URI = "KNOCKOFF_TEST_DB_URI"


@pytest.fixture(scope="function")
def empty_db_with_sometable(empty_db):
    Base.metadata.create_all(empty_db.engine)
    yield empty_db


@pytest.fixture(scope="function")
def empty_db():
    """
    Creates an empty database with tables from sample.data_model initialized
    """

    # setup
    clear_default_env_vars()
    url = os.getenv(KNOCKOFF_TEST_DB_URI, "postgresql://postgres@localhost:5432/postgres")

    temp_db_service = TempDatabaseService(url)
    # setup the database and initialize the tables
    temp_url = temp_db_service.start()

    os.environ[KNOCKOFF_DB_URI] = temp_url
    engine = get_engine()
    mock_db = MockDB(engine, temp_url)

    yield mock_db

    # tear down
    temp_db_service.stop()
    clear_default_env_vars()


@pytest.fixture(scope="function")
def seed():
    Faker.seed(123)
    random.seed(123)
