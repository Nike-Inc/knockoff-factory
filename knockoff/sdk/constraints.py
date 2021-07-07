# Copyright 2021-present, Nike, Inc.
# All rights reserved.
#
# This source code is licensed under the Apache-2.0 license found in
# the LICENSE file in the root directory of this source tree.


from operator import itemgetter

from interface import Interface, implements


class KnockoffConstraint(Interface):
    def reset(self):
        # TODO: reset to initial state
        return

    def check(self, record):
        # TODO if record would satisfy constraint return True
        return True

    def add(self, record):
        if not self.check(record):
            raise ValueError('Should raise a constraint error here')


class KnockoffUniqueConstraint(implements(KnockoffConstraint)):
    def __init__(self, keys, name=None):
        self.name = name # is this necessary?
        assert len(keys) > 0
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
