# Copyright 2021-present, Nike, Inc.
# All rights reserved.
#
# This source code is licensed under the Apache-2.0 license found in
# the LICENSE file in the root directory of this source tree.


import pandas as pd
from knockoff.sdk.table import KnockoffTable
from .next_strategy.df import sample_df
from .next_strategy.table import sample_table


class KnockoffFactory(object):
    def __init__(self, obj, columns=None, rename=None, drop=None,
                 next_strategy_callable=None,
                 next_strategy_factory=None,
                 lazy_init=True):

        self.obj = obj
        self.columns = columns
        self.rename = rename or {}
        self.drop = set(drop or [])
        self.lazy_init = lazy_init
        self.next = None
        self.initialized = False
        assert (next_strategy_callable is None) ^ (next_strategy_factory is None)
        self.next_strategy_callable = next_strategy_callable
        self.next_strategy_factory = next_strategy_factory
        if not self.lazy_init:
            self.initialize()

    def initialize(self):
        if self.next_strategy_factory:
            self.next = self.next_strategy_factory(self.obj)
        else:
            self.next = self.next_strategy_callable
        self.initialized = True

    def __call__(self):
        if not self.initialized:
            self.initialize()
        record = self.next(self.obj)
        out = {}
        for col in self.columns:
            if col in self.drop:
                continue
            out[self.rename.get(col, col)] = record[col]
        return out


class KnockoffTableFactory(KnockoffFactory):

    def __init__(self, table, columns=None, rename=None, drop=None,
                 next_strategy_callable=sample_table,
                 next_strategy_factory=None):
        if (next_strategy_factory is None) and (next_strategy_callable is None):
            next_strategy_callable = sample_table
        assert isinstance(table, KnockoffTable) # TODO : do we actually need this assert?
        super(KnockoffTableFactory, self).__init__(table,
                                                   columns=columns,
                                                   rename=rename,
                                                   drop=drop,
                                                   next_strategy_callable=next_strategy_callable,
                                                   next_strategy_factory=next_strategy_factory)

    def initialize(self):
        super(KnockoffTableFactory, self).initialize()
        if self.columns is None:
            self.columns = self.columns or self.obj.columns


class KnockoffDataFrameFactory(KnockoffFactory):

    def __init__(self, df, columns=None, rename=None, drop=None,
                 next_strategy_callable=None,
                 next_strategy_factory=None):
        if (next_strategy_factory is None) and (next_strategy_callable is None):
            next_strategy_callable = sample_df
        assert isinstance(df, pd.DataFrame)
        super(KnockoffDataFrameFactory, self).__init__(df,
                                                       columns=columns,
                                                       rename=rename,
                                                       drop=drop,
                                                       next_strategy_callable=next_strategy_callable,
                                                       next_strategy_factory=next_strategy_factory)

    def initialize(self):
        super(KnockoffDataFrameFactory, self).initialize()
        if self.columns is None:
            self.columns = self.columns or self.obj.columns


class KnockoffTransform(object):
    def __init__(self, factory, transform):
        self.factory = factory
        self.transform = transform

    def __call__(self):
        return self.transform(self.factory())

