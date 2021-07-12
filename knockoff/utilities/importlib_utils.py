# Copyright 2021-present, Nike, Inc.
# All rights reserved.
#
# This source code is licensed under the Apache-2.0 license found in
# the LICENSE file in the root directory of this source tree.


from importlib import import_module


def resolve_package_name(package_name):
    """
    Parameters
    ----------

    package_name: str
        The expected format of package_name is 'package:name'
        where 'package' should be an importable module name and
        'name' should be the name of an object accessible within
        that module
    """
    package, name = package_name.split(':')
    module = import_module(package)
    return getattr(module, name)
