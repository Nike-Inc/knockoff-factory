# Copyright 2021-present, Nike, Inc.
# All rights reserved.
#
# This source code is licensed under the Apache-2.0 license found in
# the LICENSE file in the root directory of this source tree.

import logging
import re
import networkx as nx
from networkx.algorithms import topological_sort
from networkx.algorithms import is_directed_acyclic_graph


from knockoff.factory.sink import KnockoffSink
from knockoff.factory.source import KnockoffSource
from knockoff.factory.node import Table, FactoryPart, FactoryComponent, FactoryPrototype
from knockoff.exceptions import DependencyNotFoundError

logger = logging.getLogger(__name__)

DEPENDENCY_REGEX = (r'^(part|component|prototype)\:'
                    '([A-Za-z0-9-_]+)[.]?([A-Za-z0-9-_]*)$')

DEPENDENCY_PATTERN = re.compile(DEPENDENCY_REGEX)


class BlueprintBuilder:
    def __init__(self):
        self.dag = nx.DiGraph()
        self.nodes = []
        self.index = {}
        self.dependency_queue = []

    def _add_node_to_index(self, node_type, name):
        i = len(self.index)
        if (node_type, name) in self.index:
            raise Exception("Node of type={} with name={} already exists."
                            .format(node_type, name))
        self.index[(node_type, name)] = i
        return i

    def add_part(self, node):
        node_type = node['type']
        name = node['name']
        source = KnockoffSource(node_type, node['source'])

        i = self._add_node_to_index(node_type, name)

        node = FactoryPart(name, i, source)

        self.nodes.append(node)
        self.dag.add_node(i)

        dependencies = source.config.get('dependencies') or []
        for dep in dependencies:
            other_node_type, other_name, _ = Assembler.parse_dependency(dep)
            self._add_dependency(i, other_node_type, other_name)

    def _add_dependency(self, i, other_type, other_name, queue_on_error=True):
        try:
            other_i = self.index[other_type, other_name]
            self.dag.add_edge(other_i, i)
        except KeyError:
            if queue_on_error:
                self.dependency_queue.append((i, (other_type, other_name)))
            else:
                raise DependencyNotFoundError("Dependency not found: "
                                              "node={}, name={}"
                                              .format(other_type,
                                                      other_name))

    def add_table(self, node):
        node_type = node['type']
        name = node['name']
        source = KnockoffSource(node_type, node['source'])
        sink = KnockoffSink(node.get('sink', {'strategy': 'noop'}))

        i = self._add_node_to_index(node_type, name)

        node = Table(name, i, source, sink, table=node.get('table'))

        self.nodes.append(node)
        self.dag.add_node(i)

        if source.config['strategy'] == "knockoff":
            other_name = source.config.get('kwargs', {}).get('prototype')
            self._add_dependency(i, 'prototype', other_name)

    def add_prototype(self, node):
        node_type = node['type']
        name = node['name']

        i = self._add_node_to_index(node_type, name)
        source = KnockoffSource(node_type, node['source'])
        prototype = FactoryPrototype(name, i, source, unique=node.get('unique'))
        self.nodes.append(prototype)
        self.dag.add_node(i)

        if source.config['strategy'] == 'components':
            components = []
            for component in source.config['components']:
                component_index_name = "{}.{}".format(name,
                                                      component['name'])
                other_i = self._add_node_to_index('component',
                                                  component_index_name)
                component_source = KnockoffSource("component",
                                                  component['source'])
                component = FactoryComponent(component['name'],
                                             other_i,
                                             component_source)
                components.append(component)
                self.nodes.append(component)
                self._add_dependency(i, 'component',
                                     component_index_name)
                for dep in component.source.config.get('dependencies', []):
                    comp_dep_type, comp_dep_name, _ = Assembler.parse_dependency(dep)
                    self._add_dependency(other_i, comp_dep_type, comp_dep_name)

            prototype.source.components = components
        elif source.config['strategy'] == 'concat':
            for dep in source.config['dependencies']:
                other_type, other_name, _ = Assembler.parse_dependency(dep)
                self._add_dependency(i, other_type, other_name)
        elif source.config['strategy'] == 'io':
            # TODO: anything to do?
            pass
        else:
            raise ValueError("Unrecognized strategy: {} for prototype".format(source.config['strategy']))

    def build(self):
        assert len(self.index) == len(self.nodes), 'Mismatch in index and nodes'
        assert len(self.dag.nodes) == len(self.nodes), 'Mismatch in dag and nodes'
        for i, (node_type, name) in self.dependency_queue:
            self._add_dependency(i, node_type, name, queue_on_error=False)
        assert is_directed_acyclic_graph(self.dag)
        return Blueprint(self.dag, self.nodes, self.index)


class Blueprint:
    def __init__(self, dag, nodes, index):
        self.dag = dag
        self.nodes = nodes
        self.index = index

    def get_node(self, node_type, name):
        return self.nodes[self.index[node_type, name]]

    def iter_topologically(self):
        return topological_sort(self.dag)

    @staticmethod
    def from_config(config):
        # TODO: add validation for config

        builder = BlueprintBuilder()

        for node in config['dag']:

            if node['type'] == FactoryPart.node_type:
                builder.add_part(node)
            elif node['type'] == Table.node_type:
                builder.add_table(node)
            elif node['type'] == FactoryPrototype.node_type:
                builder.add_prototype(node)
            elif node['type'] == FactoryComponent.node_type:
                # TODO: can we get here? should components be restricted to prototypes
                raise Exception('component must be part of prototype')
            else:
                raise Exception('node type not recognized: {}'
                                .format(node['type']))
        blueprint = builder.build()

        return blueprint


class Assembler:
    def __init__(self, blueprint):
        self.blueprint = blueprint

    def accept(self, visitor):
        visitor.visit(self)

    def start(self):
        # TODO: we can parallelize the execution of the dag
        for i in self.blueprint.iter_topologically():
            node = self.blueprint.nodes[i]
            logger.debug(("Assembler accepting visit from node:"
                          " name={}, type={}, ix={}")
                         .format(node.name,
                                 # TODO: replace with enum / classmap?
                                 node.source.node_type,
                                 node.ix))
            self.accept(node)

    def assemble_table(self, node):
        node.load(self)
        node.sink.dump(node.table, node.data)

    def assemble_part(self, node):
        node.load(self)

    def prepare_component(self, node):
        node.prepare(self)

    def assemble_prototype(self, node):
        node.load(self)

    @staticmethod
    def parse_dependency(string, pattern=DEPENDENCY_PATTERN):
        match = pattern.match(string)
        if match:
            return match.groups()
        raise Exception("Dependency pattern not recognized: {}"
                        .format(string))



