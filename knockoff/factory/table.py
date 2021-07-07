# Copyright 2021-present, Nike, Inc.
# All rights reserved.
#
# This source code is licensed under the Apache-2.0 license found in
# the LICENSE file in the root directory of this source tree.

def load_knockoff(source, assembler, node_name):
    kwargs = source.config["kwargs"]
    df = assembler.blueprint.get_node("prototype",
                                      kwargs["prototype"]).data
    columns = kwargs.get('columns')
    if columns:
        return df[columns]
    return df
