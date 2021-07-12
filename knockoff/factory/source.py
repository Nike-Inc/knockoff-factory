# Copyright 2021-present, Nike, Inc.
# All rights reserved.
#
# This source code is licensed under the Apache-2.0 license found in
# the LICENSE file in the root directory of this source tree.

import logging

from knockoff.utilities.mixin import ResourceLocatorMixin


logger = logging.getLogger(__name__)


class TableSourceFactory(ResourceLocatorMixin, object):
    entry_point_group = "knockoff.factory.source.table.load_strategy"


class PartSourceFactory(ResourceLocatorMixin, object):
    entry_point_group = "knockoff.factory.source.part.load_strategy"


class ComponentSourceFactory(ResourceLocatorMixin, object):
    entry_point_group = "knockoff.factory.source.component.load_strategy"


class PrototypeSourceFactory(ResourceLocatorMixin, object):
    entry_point_group = "knockoff.factory.source.prototype.load_strategy"


TYPE_TO_FACTORY = {
    "part": PartSourceFactory,
    "table": TableSourceFactory,
    "component": ComponentSourceFactory,
    "prototype": PrototypeSourceFactory,
}


class KnockoffSource:
    def __init__(self, node_type, config):
        self.node_type = node_type
        self.config = config
        self.load_strategy = (TYPE_TO_FACTORY[self.node_type]()
                              .get_resource(self.config['strategy']))

    def load(self, assembler, node_name):
        return self.load_strategy(self, assembler, node_name)


class SourceMixin:
    source = None
    data = None
    name = None

    def load(self, assembler):
        if self.name is None:
            raise Exception("Missing name")
        if self.source is None:
            raise Exception('Missing source')
        if self.data is None:
            self.data = self.source.load(assembler,
                                         self.name)
