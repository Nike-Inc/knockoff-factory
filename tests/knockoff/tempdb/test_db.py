# Copyright 2021-present, Nike, Inc.
# All rights reserved.
#
# This source code is licensed under the Apache-2.0 license found in
# the LICENSE file in the root directory of this source tree.


import pytest

from collections import namedtuple
from mock import MagicMock, call

from knockoff.tempdb.db import TempDatabaseService


TEMP_URL = 'tempurl'
URL = 'url'

def make_setup_teardown(some_mock):
    def dummy_setup_teardown(url):
        # do some setup
        some_mock.check_setup_happened(url)
        yield TEMP_URL
        # do some teardown
        some_mock.check_teardown_happened()
    return dummy_setup_teardown


def bad_setup_teardown1(url):
    yield TEMP_URL
    yield TEMP_URL

def bad_setup_teardown2(url):
    return


TempDBFixture = namedtuple(
    'TempDBFixture',
    ['tracker_mock',
     'initialize_tables',
     'mock_setup_teardown',
     'temp_db_service']
)

@pytest.fixture(scope="function")
def temp_db_fixture():
    tracker_mock = MagicMock()
    initialize_tables = MagicMock()
    mock_setup_teardown = make_setup_teardown(tracker_mock)
    url = URL
    temp_db_service = TempDatabaseService(url,
                                          setup_teardown=mock_setup_teardown,
                                          initialize_tables=initialize_tables)
    yield TempDBFixture(tracker_mock=tracker_mock,
                        initialize_tables=initialize_tables,
                        mock_setup_teardown=mock_setup_teardown,
                        temp_db_service=temp_db_service)


class TestTempDatabaseService(object):

    def test_temp_database_service(self, temp_db_fixture):
        temp_db_fixture.temp_db_service.start()

        assert temp_db_fixture.temp_db_service.url == URL
        assert temp_db_fixture.temp_db_service.temp_url == TEMP_URL
        temp_db_fixture.tracker_mock.check_setup_happened.assert_called_once_with(URL)
        temp_db_fixture.tracker_mock.check_teardown_happened.assert_not_called()
        temp_db_fixture.initialize_tables.assert_called_once_with(TEMP_URL)

        temp_db_fixture.temp_db_service.stop()

        temp_db_fixture.tracker_mock.check_setup_happened.assert_called_once_with(URL)
        temp_db_fixture.tracker_mock.check_teardown_happened.assert_called_once()

        temp_db_fixture.temp_db_service.reset()
        temp_db_fixture.temp_db_service.start()
        temp_db_fixture.temp_db_service.stop()

        temp_db_fixture.tracker_mock.check_setup_happened.assert_has_calls(
            [call(URL), call(URL)], any_order=True
        )

        temp_db_fixture.tracker_mock.check_teardown_happened.assert_has_calls(
            [call(), call()], any_order=True
        )
        temp_db_fixture.initialize_tables.assert_has_calls(
            [call(TEMP_URL), call(TEMP_URL)], any_order=True
        )

    def test_stop_before_start(self, temp_db_fixture):
        with pytest.raises(ValueError):
            temp_db_fixture.temp_db_service.stop()

    def test_bad_setup1(self):
        temp_db_service = TempDatabaseService(URL,
                                              setup_teardown=bad_setup_teardown1,
                                              initialize_tables=MagicMock())
        with pytest.raises(ValueError):
            temp_db_service.start()
            temp_db_service.stop()

    def test_bad_setup2(self):
        temp_db_service = TempDatabaseService(URL,
                                              setup_teardown=bad_setup_teardown2,
                                              initialize_tables=MagicMock())
        with pytest.raises(ValueError):
            temp_db_service.start()
