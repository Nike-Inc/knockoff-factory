# Copyright 2021-present, Nike, Inc.
# All rights reserved.
#
# This source code is licensed under the Apache-2.0 license found in
# the LICENSE file in the root directory of this source tree.


import pkg_resources


class FactoryMixin:
    _resources = None
    entry_point_group = None

    def _register_resources(self):
        self._resources = {}
        for entry_point in (pkg_resources
                            .iter_entry_points(self
                                               .entry_point_group)):
            self._resources[entry_point.name] = entry_point.load()

    def get_resource(self, name):
        if self._resources is None:
            self._register_resources()
        return self._resources[name]


def noop(*args, **kwargs):
    pass
