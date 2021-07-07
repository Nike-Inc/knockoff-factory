# Copyright 2021-present, Nike, Inc.
# All rights reserved.
#
# This source code is licensed under the Apache-2.0 license found in
# the LICENSE file in the root directory of this source tree.

import pandas as pd

from ..utilities.period import generate_periods_from_intervals
from datetime import datetime


def concat_strategy(source, assembler, node_name):
    dfs = []
    for dependency in source.config['dependencies']:
        node_type, name, sub_name = assembler.parse_dependency(dependency)
        node = assembler.blueprint.get_node(node_type, name)
        if sub_name:
            dfs.append(node.data[[sub_name]])
        else:
            dfs.append(node.data)
    return pd.concat(dfs, axis=0)


def cartesian_product_strategy(source, assembler, node_name):
    values = []
    assert (len(source.config['dependencies'])
            == len(source.config['index'])), ('Number of elements in '
                                              'dependencies and index '
                                              'must be equal.')
    for dependency in source.config['dependencies']:
        node_type, name, sub_name = assembler.parse_dependency(dependency)
        node = assembler.blueprint.get_node(node_type, name)
        if sub_name:
            values.append(node.data[[sub_name]].values)
        else:
            values.append(node.data[0].values)
    index = pd.MultiIndex.from_product(values, names=source.config['index'])
    return pd.DataFrame(index=index).reset_index()


def read_part_inline(source, assembler, node_name):
    return pd.DataFrame(source.config['data'])


def generate_part_periods(source, assembler, node_name):

    periods = generate_periods_from_intervals(
        bop_interval=source.config['bop_interval'],
        eop_interval=source.config['eop_interval'],
    )

    string_format = source.config.get("string_format")

    if string_format:
        def to_string(x):
            return (
                datetime.strftime(x[0], string_format),
                datetime.strftime(x[1], string_format)
            )

        periods = [to_string(x) for x in periods]

    return pd.DataFrame(list(zip(periods)))
