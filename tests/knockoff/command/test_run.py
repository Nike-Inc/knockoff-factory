# Copyright 2021-present, Nike, Inc.
# All rights reserved.
#
# This source code is licensed under the Apache-2.0 license found in
# the LICENSE file in the root directory of this source tree.

import pytest
import os
import pandas as pd

from sqlalchemy import create_engine
from unittest.mock import patch

from knockoff.command import run
from knockoff.sdk.blueprint import noplan
from knockoff.utilities.testing.mysql import TEST_MYSQL_ENABLED
from knockoff.utilities.testing.postgresql import TEST_POSTGRES_ENABLED

from tests.knockoff.data_model import SOMETABLE


HERE = os.path.dirname(__file__)

CONFIG_PATH = os.path.join(HERE, "knockoff.yaml")
CONFIG_PATH2 = os.path.join(HERE, "knockoff2.yaml")
MYSQL_CONFIG_PATH = os.path.join(HERE, "mysql-knockoff.yaml")

TESTABLE_INPUT_PATH = "knockoff.command.run.testable_input"

# this should only be used by test_run_command_ephemeral
_mock_testable_input_call_count = 0

SEED = 123


def mock_testable_input(
        prompt,
        test_temp_url=None,
        test_temp_db=None,
        test_blueprint=None,
        test_knockoff_db=None):

    global _mock_testable_input_call_count
    _mock_testable_input_call_count +=1

    # we are testing that everything configured in CONFIG_PATH
    # has been injected

    assert test_temp_db.url == "postgresql://postgres@localhost:5432/postgres"
    assert test_blueprint.plan == noplan

    engine = create_engine(test_temp_url)
    assert engine.url == test_knockoff_db.database_service.engine.url
    engine.dispose()
    # test that the database service has the table initialized by
    # the TempDBService with the --ephemeral flag
    assert test_knockoff_db.database_service.has_table(SOMETABLE)


def mock_seed(i):
    assert i == SEED


@pytest.mark.skipif(
    not TEST_POSTGRES_ENABLED,
    reason="postgres not available"
)
class TestRun:

    def test_run_command_ephemeral(self):
        global _mock_testable_input_call_count
        with patch(TESTABLE_INPUT_PATH, mock_testable_input):
            run.main(argv=[
                "--ephemeral",
                "--yaml-config",
                CONFIG_PATH,
                "--seed", f"{SEED}"
            ])
            assert _mock_testable_input_call_count == 1

    def test_run_command_seed(self):
        """
        this test expects to connect to postgresql://postgres@localhost:5432/postgres
        to exist, but doesn't actually do anything to the db
        """
        with patch("knockoff.command.run.seed", mock_seed):
            run.main(argv=[
                "--yaml-config",
                CONFIG_PATH,
                "--seed", f"{SEED}"
            ])

    def test_run_sample_blueprint_plan(self):
        run.clear_run_env_vars()

        # we are also testing the env variable override here
        os.environ[run.KNOCKOFF_RUN_BLUEPRINT_PLAN_ENV] = (
            "tests.knockoff.blueprint:sometable_blueprint_plan"
        )

        def mock_testable_input2(prompt, test_temp_url, **kwargs):
            engine = create_engine(test_temp_url)
            with engine.connect() as conn:
                df = pd.read_sql_table(SOMETABLE, conn)
            assert df.shape == (10, 7)

        with patch(TESTABLE_INPUT_PATH, mock_testable_input2):
            run.main(argv=[
                "--ephemeral",
                "--yaml-config",
                CONFIG_PATH2
            ])

        run.clear_run_env_vars()

    @pytest.mark.skipif(
        not TEST_MYSQL_ENABLED,
        reason="mysql not available"
    )
    def test_run_mysql(self):
        run.clear_run_env_vars()

        def _mock_testable_input(prompt, test_temp_url, **kwargs):
            engine = create_engine(test_temp_url)
            with engine.connect() as conn:
                df = pd.read_sql_table(SOMETABLE, conn)
            assert df.shape == (10, 7)

        with patch(TESTABLE_INPUT_PATH, _mock_testable_input):
            run.main(argv=[
                "--ephemeral",
                "--yaml-config",
                MYSQL_CONFIG_PATH
            ])

        run.clear_run_env_vars()
