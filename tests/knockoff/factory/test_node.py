# Copyright 2021-present, Nike, Inc.
# All rights reserved.
#
# This source code is licensed under the Apache-2.0 license found in
# the LICENSE file in the root directory of this source tree.


import unittest
import mock
import logging

from knockoff.factory.node import Table, FactoryPart


class TestNode(unittest.TestCase):

    def test_tablenode_visit(self):
        mock_assembler = mock.Mock()
        mock_source = mock.Mock()
        mock_sink = mock.Mock()
        node = Table('name', 'ix', mock_source, mock_sink)
        node.visit(mock_assembler)

        mock_assembler.assemble_table.assert_called_once_with(node)
        self.assertFalse(mock_assembler.assemble_part.called)

    def test_factorypartnode_visit(self):
        mock_assembler = mock.Mock()
        mock_source = mock.Mock()
        node = FactoryPart('name', 'ix', mock_source)
        node.visit(mock_assembler)

        mock_assembler.assemble_part.assert_called_once_with(node)
        self.assertFalse(mock_assembler.assemble_table.called)


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    unittest.main()
