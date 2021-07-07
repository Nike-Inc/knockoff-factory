# Copyright 2021-present, Nike, Inc.
# All rights reserved.
#
# This source code is licensed under the Apache-2.0 license found in
# the LICENSE file in the root directory of this source tree.


import networkx as nx
from networkx.algorithms import topological_sort
from networkx.algorithms import is_directed_acyclic_graph


class Node(object):
    def __init__(self, node_id, **kwargs):
        self._node_id = node_id
        for key, value in kwargs.items():
            assert key not in {'node_id', '_node_id'}
            setattr(self, key, value)

    @property
    def node_id(self):
        return self._node_id


class DagService(object):
    def __init__(self):
        self.dag = nx.DiGraph()
        self.nodes = []
        self.index = {}

    def get_node(self, node_id):
        return self.nodes[self.index[node_id]]

    def add_node(self, node, depends_on=None):
        node_id = node.node_id
        assert node_id not in self.index, 'Node already present'
        ix = len(self.nodes)
        self.nodes.append(node)
        self.index[node_id] = ix
        self.dag.add_node(node_id)
        if depends_on:
            self.dag.add_edges_from([(other_node_id, node_id) for other_node_id in depends_on])

    def iter_topologically(self):
        assert is_directed_acyclic_graph(self.dag)
        return (self.nodes[self.index[node_id]] for node_id in topological_sort(self.dag))
