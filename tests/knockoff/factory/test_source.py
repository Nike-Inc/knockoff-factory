# Copyright 2021-present, Nike, Inc.
# All rights reserved.
#
# This source code is licensed under the Apache-2.0 license found in
# the LICENSE file in the root directory of this source tree.


import os
import sys
import unittest
import logging
import pandas as pd
import random

from datetime import date, datetime
from faker import Faker
from unittest import mock

from knockoff.factory.source import KnockoffSource
from knockoff.factory.part import read_part_inline, generate_part_periods
from knockoff.factory.counterfeit import load_faker, KNOCKOFF_ATTEMPT_LIMIT_ENV
from knockoff.factory.counterfeit import load_faker_component_generator
from knockoff.io import load_strategy_io


class TestSource(unittest.TestCase):

    def setUp(self):
        Faker.seed(123)
        random.seed(123)
        os.environ['KNOCKOFF_TEST_MODE'] = '1'

    def tearDown(self):
        for env in [KNOCKOFF_ATTEMPT_LIMIT_ENV, 'KNOCKOFF_TEST_MODE']:
            try:
                del os.environ[env]
            except KeyError:
                pass

    def test_part_inline_load(self):
        config = {
            "strategy": "inline",
            "data": ["shoes", "apparel"]
        }
        source = KnockoffSource("part", config)
        self.assertEqual(source.load_strategy, read_part_inline)

        data = source.load(mock.Mock(), "node_name")
        self.assertSequenceEqual(data.to_dict('list')[0], config["data"])

    @mock.patch("knockoff.utilities.date.interval.now",
                mock.MagicMock(return_value=datetime(2020, 5, 4,
                                                     14, 57, 16)))
    def test_part_generate_periods(self):
        config = {
            "strategy": "period",
            "bop_interval": "[today -SU, +5w) | w",
            "eop_interval": "[today +SA, +5w) | w",
        }

        expected = pd.DataFrame(
            data=list(zip([
                (date(2020, 5, 3), date(2020, 5, 9)),
                (date(2020, 5, 10), date(2020, 5, 16)),
                (date(2020, 5, 17), date(2020, 5, 23)),
                (date(2020, 5, 24), date(2020, 5, 30)),
                (date(2020, 5, 31), date(2020, 6, 6))
            ])),
            columns=[0]
        )

        source = KnockoffSource("part", config)
        self.assertEqual(source.load_strategy, generate_part_periods)

        data = source.load(mock.Mock(), "node_name")
        self.assertTrue(data.equals(expected))

    @mock.patch("knockoff.utilities.date.interval.now",
                mock.MagicMock(return_value=datetime(2020, 5, 4,
                                                     14, 57, 16)))
    def test_part_generate_periods_with_string_format(self):
        config = {
            "strategy": "period",
            "bop_interval": "[today -SU, +5w) | w",
            "eop_interval": "[today +SA, +5w) | w",
            "string_format": "%Y%m%d"
        }

        expected = pd.DataFrame(
            data=list(zip([
                ('20200503', '20200509'), ('20200510', '20200516'),
                ('20200517', '20200523'), ('20200524', '20200530'),
                ('20200531', '20200606')
            ])),
            columns=[0]
        )

        source = KnockoffSource("part", config)
        self.assertEqual(source.load_strategy, generate_part_periods)

        data = source.load(mock.Mock(), "node_name")
        self.assertTrue(data.equals(expected))

    @mock.patch("knockoff.io.pd.read_sql_query")
    @mock.patch("knockoff.io.get_connection")
    def test_io_read_sql(self, mock_conn, mock_query):
        config = {
            "strategy": "io",
            "reader": "sql",
            "args": {
                "sql": "select GTINS from mock_table",
                "database": "default"
            }
        }
        expected = pd.DataFrame(data=['00091201623839', '00091201623853',
                                      '00091206420280', '00091206425155',
                                      '00091206457293', '00091206457309',
                                      '00091206457903', '00091206461191',
                                      '00091207547856', '00091207563245'])
        mock_query.return_value = expected
        mo = mock.Mock()
        mo.__enter__ = mock.Mock(return_value=(mock.Mock(), None))
        mo.__exit__ = mock.Mock(return_value=None)
        mock_conn.return_value = mo

        source = KnockoffSource("part", config)

        self.assertEqual(source.load_strategy, load_strategy_io)
        data = source.load(mock.Mock(), "node_name")
        mock_query.assert_called_once()
        self.assertTrue(data.equals(expected))

    def test_part_faker_load(self):
        config = {
            "strategy": "faker",
            "method": "color_name",
            "number": 10
        }
        source = KnockoffSource("part", config)
        self.assertEqual(source.load_strategy, load_faker)
        data = source.load(mock.Mock(), "node_name")
        expected = ['Blue', 'CadetBlue', 'DarkCyan', 'DarkMagenta', 'LightGreen',
                    'MediumSeaGreen', 'MediumSpringGreen', 'Olive', 'PaleTurquoise',
                    'WhiteSmoke']
        self.assertSequenceEqual(list(map(str, data.to_dict('list')[0])),
                                 expected)

    def test_part_faker_load_limit_reached(self):
        os.environ[KNOCKOFF_ATTEMPT_LIMIT_ENV] = '5'
        config = {
            "strategy": "faker",
            "method": "words",
            "args": [1, ["one", "two", "three"], True],
            "number": 10
        }
        source = KnockoffSource("part", config)
        self.assertEqual(source.load_strategy, load_faker)

        with self.assertRaises(Exception):
            source.load(mock.Mock())

    def test_component_faker_load(self):
        config = {
            "strategy": "faker",
            "method": "numerify",
            "args": ['%#########'],
            "unique": True,
        }
        source = KnockoffSource("component", config)
        self.assertEqual(source.load_strategy, load_faker_component_generator)
        generator = source.load(mock.Mock(), "node_name")
        actual = [next(generator) for _ in range(5)]

        if sys.version_info[0] < 3:
            # backwards compatibility with seed used in python 2
            expected = ['2004190538', '5332040503', '7901709528', '5382658337', '2666846307']
        else:
            expected = ['9041641068', '3550225853', '2061961057', '5012204697', '6704587398']
        self.assertSequenceEqual(actual, expected)


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    unittest.main()
