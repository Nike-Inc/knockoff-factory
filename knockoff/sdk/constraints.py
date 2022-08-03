# Copyright 2021-present, Nike, Inc.
# All rights reserved.
#
# This source code is licensed under the Apache-2.0 license found in
# the LICENSE file in the root directory of this source tree.


from abc import ABCMeta, abstractmethod
from operator import itemgetter


class KnockoffConstraint(metaclass=ABCMeta):
    @abstractmethod
    def reset(self):
        """reset to initial state"""
        return  # pragma: no cover

    @abstractmethod
    def check(self, record):
        """if record would satisfy constraint return True"""
        return  # pragma: no cover

    def add(self, record):
        if not self.check(record):
            raise ValueError('Should raise a constraint error here')


class KnockoffUniqueConstraint(KnockoffConstraint):
    def __init__(self, keys, name=None):
        self.name = name # is this necessary?
        assert isinstance(keys, (list, tuple)) and len(keys) > 0
        self.keys = keys
        self.curr_set = set()
        self.parse = itemgetter(*self.keys)

    def check(self, record):
        return self.parse(record) not in self.curr_set

    def add(self, record):
        # TODO: do we care if it already exists?
        self.curr_set.add(self.parse(record))

    def reset(self):
        self.curr_set = set()
