# Copyright 2021-present, Nike, Inc.
# All rights reserved.
#
# This source code is licensed under the Apache-2.0 license found in
# the LICENSE file in the root directory of this source tree.

import logging
from abc import ABCMeta, abstractmethod

from knockoff.factory.source import SourceMixin
from knockoff.factory.component import ComponentMixin


logger = logging.getLogger(__name__)


class KnockoffNode(metaclass=ABCMeta):

    node_type = None

    def __init__(self, name, ix):
        self.name = name
        self.ix = ix

    @abstractmethod
    def visit(self):
        raise NotImplementedError


class Table(SourceMixin, KnockoffNode):

    node_type = "table"

    def __init__(self, name, ix, source, sink, table=None):
        super(Table, self).__init__(name, ix)
        self.table = table or name
        self.source = source
        self.sink = sink

    def visit(self, assembler):
        assembler.assemble_table(self)


class FactoryPart(SourceMixin, KnockoffNode):

    node_type = "part"

    def __init__(self, name, ix, source):
        super(FactoryPart, self).__init__(name, ix)
        self.source = source

    def visit(self, assembler):
        assembler.assemble_part(self)


class FactoryComponent(ComponentMixin, KnockoffNode):

    node_type = "component"

    def __init__(self, name, ix, source):
        super(FactoryComponent, self).__init__(name, ix)
        self.source = source

    def visit(self, assembler):
        assembler.prepare_component(self)


class FactoryPrototype(SourceMixin, KnockoffNode):

    node_type = "prototype"

    def __init__(self, name, ix, source, unique=None):
        super(FactoryPrototype, self).__init__(name, ix)
        self.source = source
        self.unique = unique or []
        self.data = None

    def visit(self, assembler):
        assembler.assemble_prototype(self)
