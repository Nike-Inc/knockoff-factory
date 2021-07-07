# Copyright 2021-present, Nike, Inc.
# All rights reserved.
#
# This source code is licensed under the Apache-2.0 license found in
# the LICENSE file in the root directory of this source tree.


from .df import sample_df, cycle_df_factory


def sample_table(table, **kwargs):
    return sample_df(table.df, **kwargs)


def cycle_table_factory(table):
    return cycle_df_factory(table.df)
