# Copyright 2021-present, Nike, Inc.
# All rights reserved.
#
# This source code is licensed under the Apache-2.0 license found in
# the LICENSE file in the root directory of this source tree.


import pandas as pd
from .next_strategy.df import sample_df
from .next_strategy.table import sample_table


class CollectionsFactory(object):
    """
    CollectionsFactory is a callable that
    wraps another callable function. Similar
    to the ColumnFactory, this uses the depends_on
    parameter to take advantage of previously generated
    key-values from other factories that be passed as
    kwargs to the wrapped function during the KnockoffTable
    build routine.
    """
    def __init__(self,
                 callable_,
                 columns=None,
                 rename=None,
                 drop=None,
                 depends_on=None):
        """

        :param callable_: function
            This function should return a dict of
            column names as keys with values
            for a row.
        :param columns: list[str], default None
            Only these columns will be considered in the
            dict returned from a call to this instance.
        :param rename: dict[str,str], default None
            This is a dict from the current key name to the
            desired key name in the return dict.
        :param drop: list[str], default None
            This is a list of keys to drop in the return dict.
        :param depends_on:
            If this is not None, the strings provided here will
            be used by the KnockoffTable as keys in the kwargs
            when making a call to this instance. The values provided
            for those kwargs are looked up from a dict populated with
            previously returned key-values from calls to preceding factories.
        """
        self.callable = callable_
        self.depends_on = depends_on
        self.columns = columns
        self.rename = rename or {}
        self.drop = set(drop or [])

    def __call__(self, *args, **kwargs):
        record = self.callable(*args, **kwargs)
        return resolve_columns(record,
                               columns=self.columns,
                               rename=self.rename,
                               drop=self.drop)


def resolve_columns(record,
                    columns=None,
                    rename=None,
                    drop=None):
    rename = rename or {}
    drop = set(drop or [])
    out = {}
    columns = columns or record.keys()
    for col in columns:
        if col in drop:
            continue
        out[rename.get(col, col)] = record[col]
    return out


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
                 next_strategy_callable=None,
                 next_strategy_factory=None):
        if (next_strategy_factory is None) and (next_strategy_callable is None):
            next_strategy_callable = sample_table
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
