# Copyright 2021-present, Nike, Inc.
# All rights reserved.
#
# This source code is licensed under the Apache-2.0 license found in
# the LICENSE file in the root directory of this source tree.

import os
from mock import MagicMock, patch

from sqlalchemy import create_engine

from knockoff.command import run
from knockoff.sdk.blueprint import noplan
from tests.knockoff.data_model import SOMETABLE


HERE = os.path.dirname(__file__)

CONFIG_PATH = os.path.join(HERE, "knockoff.yaml")

_mock_testable_input_call_count = 0

SEED = 123

def mock_testable_input(
        prompt,
        test_temp_url=None,
        test_temp_db = None,
        test_blueprint = None,
        test_knockoff_db = None):

    global _mock_testable_input_call_count
    _mock_testable_input_call_count +=1

    # we are testing that everything configured in CONFIG_PATH
    # has been injected

    assert test_temp_db.url == "postgresql://postgres@localhost:5432/postgres"
    assert test_blueprint.plan == noplan
    engine = create_engine(test_temp_url)

    # test that the database at temp url has the configured table
    test_knockoff_db.database_service.engine = engine
    assert test_knockoff_db.database_service.has_table(SOMETABLE)


def mock_seed(i):
    assert i == SEED


class TestRun:

    def test_run_command_ephemeral(self):
        global _mock_testable_input_call_count
        with patch("knockoff.command.run.testable_input", mock_testable_input):
            run.main(argv=[
                "--ephemeral",
                "--yaml-config",
                CONFIG_PATH,
            ])
            assert _mock_testable_input_call_count == 1
            run.main(argv=[
                "--yaml-config",
                os.path.join(HERE, "knockoff.yaml"),
                # passing here since we're testing in test_run_command_seed
                # so it feels only fair to get the coverage :)
                "--seed", f"{SEED}"
            ])
            assert _mock_testable_input_call_count == 1

    def test_run_command_seed(self):
        with patch("knockoff.command.run.seed", mock_seed):
            run.main(argv=[
                "--yaml-config",
                os.path.join(HERE, "knockoff.yaml"),
                # passing here since we're testing in test_run_command_seed
                # so it feels only fair to get the coverage :)
                "--seed", f"{SEED}"
            ])