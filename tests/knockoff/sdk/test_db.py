# Copyright 2021-present, Nike, Inc.
# All rights reserved.
#
# This source code is licensed under the Apache-2.0 license found in
# the LICENSE file in the root directory of this source tree.


import pandas as pd

from knockoff.sdk.db import KnockoffDB
from .knockoff_table import PRODUCT_TABLE_NAME, LOCATION_TABLE_NAME, TRANSACTION_TABLE_NAME
from .knockoff_table import PRODUCT_TABLE, LOCATION_TABLE, TRANSACTION_TABLE


class TestDB:

    def test_knockoff_db_build(self):

        # TODO: Should we make database_service optional?
        knockoff_db = KnockoffDB(database_service=None)
        knockoff_db.add(TRANSACTION_TABLE,
                        depends_on=[PRODUCT_TABLE_NAME, LOCATION_TABLE_NAME])
        knockoff_db.add(PRODUCT_TABLE)
        knockoff_db.add(LOCATION_TABLE)

        dfs = knockoff_db.build()

        df_p = dfs[PRODUCT_TABLE_NAME]
        df_l = dfs[LOCATION_TABLE_NAME]
        df_t = dfs[TRANSACTION_TABLE_NAME]

        assert df_p.shape == (20, 7)
        assert df_l.shape == (3, 2)
        assert df_t.shape == (50, 5)

        df_p = df_p.set_index("sku")
        df_t = df_t.set_index("sku")

        df = df_t.join(df_p)
        df = df.set_index("location_id").join(df_l.set_index("location_id"))

        assert pd.notnull(df["address"]).sum() == 50
        assert pd.notnull(df["gender"]).sum() == 50
        assert all(df["units"]*df["price"] == df["revenue"])
