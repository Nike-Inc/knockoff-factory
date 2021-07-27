# Copyright 2021-present, Nike, Inc.
# All rights reserved.
#
# This source code is licensed under the Apache-2.0 license found in
# the LICENSE file in the root directory of this source tree.


class DependencyNotFoundError(Exception):
    def __init__(self, msg=None, status_code=None):
        message = "{} {}".format(msg or "",
                                 status_code or "")
        super(DependencyNotFoundError, self).__init__(message)


class FactoryNotFound(Exception):
    """Exception when factory function is not found for column"""
    def __init__(self, msg):
        self.msg = msg

    def __str__(self):
        return repr(self.msg)


class AttemptLimitReached(Exception):
    def __init__(self, msg):
        self.msg = msg

    def __str__(self):
        return repr(self.msg)


class NoEntryPointGroupError(Exception):
    """Exception when no entry_point_group has been set"""
    def __init__(self, msg):
        self.msg = msg

    def __str__(self):
        return repr(self.msg)


class ResourceNotFoundError(Exception):
    """Exception when no entry_point_group has been set"""
    def __init__(self, msg):
        self.msg = msg

    def __str__(self):
        return repr(self.msg)
