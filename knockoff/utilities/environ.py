# Copyright 2021-present, Nike, Inc.
# All rights reserved.
#
# This source code is licensed under the Apache-2.0 license found in
# the LICENSE file in the root directory of this source tree.

import os


class EnvironmentVariable(object):
    def __init__(self, variable,
                 default_value=None,
                 allow_default_value=False):
        self.variable = variable
        self.default_value = default_value
        self.allow_default_value = allow_default_value

    def get(self):
        if self.allow_default_value:
            return os.getenv(self.variable, self.default_value)
        return os.environ[self.variable]

    def set(self, value):
        os.environ[self.variable] = value


def clear_env_vars(env_vars):
    for variable in env_vars:
        try:
            del os.environ[variable]
        except KeyError:
            pass
