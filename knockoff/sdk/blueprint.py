# Copyright 2021-present, Nike, Inc.
# All rights reserved.
#
# This source code is licensed under the Apache-2.0 license found in
# the LICENSE file in the root directory of this source tree.

from collections import namedtuple

from knockoff.utilities.importlib_utils import resolve_package_name

class Blueprint(object):

    ConstructionResult = namedtuple('ConstructionResult', [
        'dfs',
        'knockoff_db'
    ])

    def __init__(self, plan):
        """
        Parameters
        ----------
        plan: function
            plan(knockoff_db: KnockoffDB) -> KnockoffDB
        """

        self.plan = plan

    @classmethod
    def from_plan_package_name(cls, package_name):
        plan = resolve_package_name(package_name)
        return Blueprint(plan)

    def construct(self, knockoff_db):
        knockoff_db = self.plan(knockoff_db)
        dfs = knockoff_db.build()
        return Blueprint.ConstructionResult(dfs=dfs,
                                            knockoff_db=knockoff_db)


def noplan(knockoff_db):
    """no plan used for testing"""
    return knockoff_db
