# Copyright 2021-present, Nike, Inc.
# All rights reserved.
#
# This source code is licensed under the Apache-2.0 license found in
# the LICENSE file in the root directory of this source tree.


from knockoff.sdk.table import KnockoffTable
from tests.knockoff.data_model import SOMETABLE


def sometable_blueprint_plan(knockoff_db):
    table = KnockoffTable(
        SOMETABLE,
        autoload=True,
        size=10,
        # we drop this because it's an autoincrement table
        # so we will offload populating this to the
        # database sequencer
        drop=["id"]
    )
    knockoff_db.add(table)
    return knockoff_db
