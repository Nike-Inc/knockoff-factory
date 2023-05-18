# Copyright 2021-present, Nike, Inc.
# All rights reserved.
#
# This source code is licensed under the Apache-2.0 license found in
# the LICENSE file in the root directory of this source tree.


from unittest.mock import MagicMock

from knockoff.sdk.blueprint import Blueprint, noplan


class TestBlueprint(object):

    def test_blueprint_from_plan_package_name(self):
        blueprint = Blueprint.from_plan_package_name("knockoff.sdk.blueprint:noplan")
        assert blueprint.plan == noplan

    def test_construct(self):
        knockoff_db = MagicMock()
        plan = MagicMock(side_effect=knockoff_db)

        blueprint = Blueprint(plan)
        response = blueprint.construct(knockoff_db)

        plan.assert_called_once_with(knockoff_db)
        response.knockoff_db.build.assert_called_once()
