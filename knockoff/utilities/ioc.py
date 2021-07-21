# Copyright 2021-present, Nike, Inc.
# All rights reserved.
#
# This source code is licensed under the Apache-2.0 license found in
# the LICENSE file in the root directory of this source tree.


import inspect
import sys

from dependency_injector import containers
from knockoff.utilities.importlib_utils import resolve_package_name


def get_container(package_name,
                  config_path=None,
                  default_dict=None,
                  override_dict=None):
    """parses declarative container, loads optional config, wires and returns"""
    Container = resolve_package_name(package_name)
    _validate_container_class(Container, package_name)
    container = Container()
    container.init_resources()
    if default_dict:
        container.config.from_dict(default_dict)
    if config_path:
        container.config.from_yaml(config_path)
    if override_dict:
        container.config.from_dict(override_dict)
    container.wire(modules=[sys.modules[__name__]])
    return container


def _validate_container_class(cls, package_name):
    if not inspect.isclass(cls) or not issubclass(cls, containers.DeclarativeContainer):
        raise TypeError(f"{package_name} resolves to "
                         f"{cls} instead of "
                         f"a subclass of dependency_injector"
                         f".containers.DeclarativeContainer")
