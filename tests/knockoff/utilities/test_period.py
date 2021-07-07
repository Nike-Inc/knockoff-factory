# Copyright 2021-present, Nike, Inc.
# All rights reserved.
#
# This source code is licensed under the Apache-2.0 license found in
# the LICENSE file in the root directory of this source tree.


import mock
import unittest

from knockoff.utilities.period import generate_periods_from_intervals
from datetime import datetime


class TestPeriod(unittest.TestCase):

    @mock.patch("knockoff.utilities.date.interval.now",
                mock.MagicMock(return_value=datetime(2020, 5, 4,
                                                     14, 57, 16)))
    def test_generate_periods(self):
        actual_periods = generate_periods_from_intervals(
            bop_interval='[today -SU, +5w) | w',
            eop_interval='[today +SA, +5w) | w',
        )

        expected_periods = [
            (datetime(2020, 5, 3).date(), datetime(2020, 5, 9).date()),
            (datetime(2020, 5, 10).date(), datetime(2020, 5, 16).date()),
            (datetime(2020, 5, 17).date(), datetime(2020, 5, 23).date()),
            (datetime(2020, 5, 24).date(), datetime(2020, 5, 30).date()),
            (datetime(2020, 5, 31).date(), datetime(2020, 6, 6).date())
        ]

        self.assertListEqual(actual_periods, expected_periods)

        with self.assertRaises(AssertionError):
            _ = generate_periods_from_intervals(
                bop_interval='[today -SU, +2w) | w',
                eop_interval='[today +SA, +5w) | w',
            )
