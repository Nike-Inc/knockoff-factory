# Copyright 2021-present, Nike, Inc.
# All rights reserved.
#
# This source code is licensed under the Apache-2.0 license found in
# the LICENSE file in the root directory of this source tree.


import os
import unittest
import logging
import yaml
from faker import Faker
from numpy import random

from knockoff.factory.assembly import Blueprint, Assembler


class TestAssembly(unittest.TestCase):

    def setUp(self):
        with open(os.path.join(os.
                               path.
                               dirname(os.
                                       path.
                                       realpath(__file__)),
                  'test_assembly.yaml'), 'rb') as f:
            self.assembly_config = yaml.safe_load(f)
        Faker.seed(123)
        random.seed(123)

    def test_blueprint_from_config(self):
        blueprint = Blueprint.from_config(self.
                                            assembly_config['knockoff'])
        self.assertEqual(len(blueprint.dag.nodes), len(blueprint.nodes))
        self.assertEqual(len(blueprint.dag.nodes), 34)

    def test_blueprint_from_config_cyclical_exception(self):
        with open(os.path.join(os.
                               path.
                               dirname(os.
                                       path.
                                       realpath(__file__)),
                  'test_cyclical_dag.yaml'), 'rb') as f:
            assembly_config = yaml.safe_load(f)
        with self.assertRaises(AssertionError):
            Blueprint.from_config(assembly_config['knockoff'])

    def test_assembler(self):
        blueprint = Blueprint.from_config(self.
                                          assembly_config['knockoff'])
        assembler = Assembler(blueprint)
        assembler.start()
        product = assembler.blueprint.get_node("prototype", "product")
        transactions = assembler.blueprint.get_node("prototype", "transactions")
        location = assembler.blueprint.get_node("prototype", "location")

        self.assertEqual(product.data.shape, (25,6))
        self.assertEqual(transactions.data.shape, (100, 6))
        self.assertEqual(location.data.shape, (6, 3))
        self.assertEqual(transactions.data.quantity.sum(), 40)

        missing_skus = (set(transactions.data.sku.unique())
                        - set(product.data.sku.unique()))
        missing_locations = (set(transactions.data.location_id.unique())
                             - set(location.data.location_id.unique()))

        self.assertEqual(len(missing_skus), 0)
        self.assertEqual(len(missing_locations), 0)

        # tests autoincrement component
        self.assertSetEqual(set(location.data.location_id.values), set(range(6)))


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    unittest.main()
