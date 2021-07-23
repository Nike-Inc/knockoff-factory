# Copyright 2021-present, Nike, Inc.
# All rights reserved.
#
# This source code is licensed under the Apache-2.0 license found in
# the LICENSE file in the root directory of this source tree.

import pytest
from unittest import TestCase

import pandas as pd

from knockoff.sdk.factory.collections import KnockoffDataFrameFactory, CollectionsFactory
from knockoff.sdk.factory.next_strategy.df import cycle_df_factory


def some_func():
    return {
        'a': 1,
        'b': 2,
        'c': 3
    }


class TestCollections(object):

    def test_knockoff_dataframe_factory_cycle(self):

        df_expected = pd.DataFrame({'a': ['a1', 'a2', 'a3'],
                                    'b': ['b1', 'b2', 'b3'],
                                    'c': ['c1', 'c2', 'c3'],})

        factory = KnockoffDataFrameFactory(df_expected,
                                           next_strategy_factory=cycle_df_factory)

        df_actual1 = pd.DataFrame([factory() for _ in range(3)])
        df_actual2 = pd.DataFrame([factory() for _ in range(3)])

        assert df_expected.equals(df_actual1)
        assert df_expected.equals(df_actual2)

    @pytest.mark.parametrize("kwargs,expected",
                             [({}, {'a':1, 'b': 2, 'c':3}),
                              ({'columns': ['a','c']}, {'a':1, 'c':3}),
                              ({'rename': {'a':'a1'}}, {'a1':1, 'b': 2, 'c':3}),
                              ({'drop': ['a','c']}, {'b': 2})]
                             )
    def test_collections_factory(self, kwargs, expected):
        factory = CollectionsFactory(some_func, **kwargs)
        actual = factory()
        TestCase().assertDictEqual(actual, expected)

    def test_collections_factory_depends_on(self):
        def another_func(x,y):
            return {
                'x': x,
                'y': y,
                'z': x+y
            }
        factory = CollectionsFactory(another_func, depends_on=['x','y'])
        actual = factory(x=1,y=2)
        TestCase().assertDictEqual(actual, {'x':1,'y':2,'z':3})

        with pytest.raises(TypeError):
            factory()
