# Copyright 2021-present, Nike, Inc.
# All rights reserved.
#
# This source code is licensed under the Apache-2.0 license found in
# the LICENSE file in the root directory of this source tree.

from knockoff.utilities.mixin import ResourceLocatorMixin


class ComponentFunctionFactory(ResourceLocatorMixin, object):
    entry_point_group = "knockoff.factory.component.function"


class ComponentMixin:
    source = None
    generator = None
    name = None

    def prepare(self, assembler):
        if self.name is None:
            raise Exception("Missing name")
        if self.source is None:
            raise Exception('Missing source')
        if self.generator is None:
            self.generator = self.source.load(assembler, self.name)


def load_autoincrement(source, assembler, name):

    def autoincrement_generator():
        i = source.config.get('start_value', 0)
        while True:
            yield i
            i += 1

    return autoincrement_generator()
