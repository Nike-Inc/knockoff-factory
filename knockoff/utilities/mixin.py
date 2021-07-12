# Copyright 2021-present, Nike, Inc.
# All rights reserved.
#
# This source code is licensed under the Apache-2.0 license found in
# the LICENSE file in the root directory of this source tree.


import pkg_resources
import logging

from knockoff.exceptions import ResourceNotFoundError
from knockoff.exceptions import NoEntryPointGroupError

logger = logging.getLogger(__name__)


# noinspection PyAttributeOutsideInit
class ResourceLocatorMixin(object):

    entry_point_group = None

    @property
    def registered_resources(self):
        try:
            return isinstance(self.__resources, dict)
        except AttributeError:
            return False

    def lazy_register_resources(self):
        if not self.registered_resources:
            self.register_resources()

    def register_resources(self):
        if self.entry_point_group is None:
            raise NoEntryPointGroupError(f"No entry_point declared for {self}")
        if self.registered_resources:
            logger.warning("Resources already registered. "
                           "Registering again will override "
                           "existing resources")
        self.__resources = {}
        for entry_point in (pkg_resources
                            .iter_entry_points(self
                                               .entry_point_group)):
            self.__resources[entry_point.name] = entry_point.load()

    def get_resource(self, name):
        self.lazy_register_resources()
        try:
            return self.__resources[name]
        except KeyError:
            raise ResourceNotFoundError(f"Resource not found: {name}"
                                        f" (entry_point_group="
                                        f"{self.entry_point_group})")

    def get_resource_names(self):
        self.lazy_register_resources()
        return self.__resources.keys()


def noop(*args, **kwargs):
    pass
