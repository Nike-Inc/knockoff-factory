# Copyright 2021-present, Nike, Inc.
# All rights reserved.
#
# This source code is licensed under the Apache-2.0 license found in
# the LICENSE file in the root directory of this source tree.


import unittest
import mock

from datetime import datetime, date
from dateutil.relativedelta import SU, MO, TU, WE, TH, FR, SA
from dateutil.relativedelta import relativedelta

from knockoff.utilities.date import interval
from knockoff.utilities.regex import InvalidStringError


class TestInterval(unittest.TestCase):

    def setUp(self):
        pass

    def tearDown(self):
        pass

    @mock.patch("knockoff.utilities.date.interval.now",
                mock.MagicMock(return_value=datetime(2020, 4, 17,
                                                     12, 30, 10)))
    def test_endpoint(self):
        today = date(2020, 4, 17)
        now = datetime(2020, 4, 17, 12, 30, 10)
        test_cases = {
            "today": today,
            'utctoday': today,
            'utcnow': now,
            "today -y": today + relativedelta(years=-1),
            "today +y": today + relativedelta(years=1),
            "today -2y": today + relativedelta(years=-2),
            "now -2y": now + relativedelta(years=-2),
            "today +y": today + relativedelta(years=+1),
            "today -52w": today + relativedelta(weeks=-52),
            "-2y -SU": relativedelta(years=-2, weekday=SU(-1)),
            "-2y +SU": relativedelta(years=-2, weekday=SU(1)),
            "+y +2SU": relativedelta(years=1, weekday=SU(2)),
            "-SU": relativedelta(weekday=SU(-1)),
            "+2SU": relativedelta(weekday=SU(2)),
            "today +2w +FR": today + relativedelta(weeks=2, weekday=FR(1)),
            "today +2w -TH": today + relativedelta(weeks=2, weekday=TH(-1)),
            "today +2WE": today + relativedelta(weekday=WE(2)),
            "today -1WE": today + relativedelta(weekday=WE(-1)),
            "+SU": relativedelta(weekday=SU(1)),
            "2020-01-01 -2y": datetime(2020, 1, 1) + relativedelta(years=-2),

        }

        for case, expected in test_cases.items():
            self.assertEqual(expected, interval.Endpoint.parse(case))

    def test_endpoint_exceptions(self):
        bad_cases = [
            "today today",
            "2+",
        ]

        for case in bad_cases:
            with self.assertRaises(InvalidStringError):
                interval.Endpoint.parse(case)

    def test_interval_frequency(self):
        test_cases = {
            "d": relativedelta(days=1),
            "1d": relativedelta(days=1),
            "10d": relativedelta(days=10),
            "w": relativedelta(weeks=1),
        }
        for case, expected in test_cases.items():
            self.assertEqual(expected,
                             interval.IntervalFrequency.parse(case))

    @mock.patch("knockoff.utilities.date.interval.now",
                mock.MagicMock(return_value=datetime(2020, 4, 17,
                                                     12, 30, 10)))
    def test_interval(self):
        today = date(2020, 4, 17)
        test_cases = {
            "[today -SU, +w)": {
                "len": 7,
                "first": today + relativedelta(weekday=SU(-1)),
                "last": today
                + relativedelta(weeks=1,weekday=SU(-1))
                + relativedelta(days=-1)
            },
            "[today -SU, +w]": {
                "len": 8,
                "first": today + relativedelta(weekday=SU(-1)),
                "last": today + relativedelta(weeks=1, weekday=SU(-1))
            },
            "(today -SU, +w]": {
                "len": 7,
                "first": today + relativedelta(weekday=SU(-1))
                + relativedelta(days=1),
                "last": today + relativedelta(weeks=1, weekday=SU(-1))
            },
            "(-104w, 2019-01-01 -SU] | w": {
                "len": 104,
                "first": date(2019, 1, 1)
                + relativedelta(weekday=SU(-1))
                + relativedelta(weeks=-104)
                + relativedelta(weeks=1),
                "last": date(2019, 1, 1)
                + relativedelta(weekday=SU(-1))
            },
            "[today +SA, -w)": {
                "len": 7,
                "first": today + relativedelta(weekday=SA(1)),
                "last": today
                + relativedelta(weekday=SA(1))
                + relativedelta(weeks=-1)
                + relativedelta(days=1)
            },
            "[today, +d) | H": {
                "len": 24,
                "first": datetime(2020, 4, 17),
                "last": datetime(2020, 4, 17)
                + relativedelta(days=1)
                + relativedelta(hours=-1)
            },
            "[today, +5H) | 15M": {
                "len": 20,
                "first": datetime(2020, 4, 17),
                "last": datetime(2020, 4, 17)
                + relativedelta(hours=5)
                + relativedelta(minutes=-15)
            },
            "[2020-04-15T01:35:15, +45s) | 5s": {
                "len": 9,
                "first": datetime(2020, 4, 15, 1, 35, 15),
                "last": datetime(2020, 4, 15, 1, 35, 15)
                        + relativedelta(seconds=45)
                        + relativedelta(seconds=-5)
            },
        }

        for case, expected in test_cases.items():
            dates = interval.Interval.parse(case)
            self.assertEqual(expected["len"], len(dates))
            self.assertEqual(expected["first"], dates[0])
            self.assertEqual(expected["last"], dates[-1])

    def test_interval_reverse(self):
        dates1 = interval.Interval.parse("[today -SU, +2w)")
        dates2 = interval.Interval.parse("(+2w, today -SU]")[::-1]
        dates3 = interval.Interval.parse("[-2w, today +2w -SU)")
        dates4 = interval.Interval.parse("(today +2w -SU, -2w]")[::-1]

        self.assertSequenceEqual(dates1, dates2)
        self.assertSequenceEqual(dates2, dates3)
        self.assertSequenceEqual(dates3, dates4)

    def test_unit_splitter(self):
        test_cases = {
            '-2y': (-2, 'y'),
            '+2y': (2, 'y'),
            'y': (1, 'y'),
            '+y': (1, 'y'),
            '-w': (-1, 'w'),
            'w': (1, 'w'),
            'd': (1, 'd'),
            '-104w': (-104, 'w'),
            '+90d': (90, 'd'),
        }
        for case, expected in test_cases.items():
            multiple, unit = interval.UnitSplitter.parse(case)
            self.assertEqual(expected[0], multiple)
            self.assertEqual(expected[1], unit)


if __name__ == "__main__":
    unittest.main()
