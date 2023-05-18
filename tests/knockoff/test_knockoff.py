# Copyright 2021-present, Nike, Inc.
# All rights reserved.
#
# This source code is licensed under the Apache-2.0 license found in
# the LICENSE file in the root directory of this source tree.


import os
import unittest
import logging

from knockoff.knockoff import Knockoff


class TestKnockoff(unittest.TestCase):

    def setUp(self):
        here = os.path.realpath(__file__)
        self.config_path = os.path.join(os.path.dirname(here),
                                        'factory',
                                        'test_assembly.yaml')

    def test_knockoff(self):
        ko = Knockoff(self.config_path, seed=123)

        df_product = ko.prototypes["product"]
        df_transactions = ko.prototypes["transactions"]
        df_location = ko.prototypes["location"]

        self.assertEqual(df_product.shape, (25,6))
        self.assertEqual(df_transactions.shape, (100, 6))
        self.assertEqual(df_location.shape, (6, 3))

        self.assertEqual(df_transactions.quantity.sum(), 49)

        missing_skus = (set(df_transactions.sku.unique())
                        - set(df_product.sku.unique()))
        missing_locations = (set(df_transactions.location_id.unique())
                             - set(df_location.location_id.unique()))

        self.assertEqual(len(missing_skus), 0)
        self.assertEqual(len(missing_locations), 0)

        # tests autoincrement component
        self.assertSetEqual(set(df_location.location_id.values), set(range(6)))


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    unittest.main()
