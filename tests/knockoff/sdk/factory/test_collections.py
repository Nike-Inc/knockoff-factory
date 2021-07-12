# Copyright 2021-present, Nike, Inc.
# All rights reserved.
#
# This source code is licensed under the Apache-2.0 license found in
# the LICENSE file in the root directory of this source tree.


import pandas as pd

from knockoff.sdk.factory.collections import KnockoffDataFrameFactory
from knockoff.sdk.factory.next_strategy.df import cycle_df_factory

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
