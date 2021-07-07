# Copyright 2021-present, Nike, Inc.
# All rights reserved.
#
# This source code is licensed under the Apache-2.0 license found in
# the LICENSE file in the root directory of this source tree.

import itertools


def sample_df(df, **kwargs):
    return df.sample(**kwargs).to_dict('records')[0]


def cycle_df_factory(df):
    # TODO: add parameter for number of cycles defaulting to None (inifinity)
    generator = itertools.cycle(df.iterrows())

    def _call(*args, **kwargs):
        _, row = next(generator)
        return row.to_dict()

    return _call
