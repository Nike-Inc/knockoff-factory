# Copyright 2021-present, Nike, Inc.
# All rights reserved.
#
# This source code is licensed under the Apache-2.0 license found in
# the LICENSE file in the root directory of this source tree.


import pytest

from knockoff.utilities.mixin import ResourceLocatorMixin
from knockoff.exceptions import ResourceNotFoundError
from knockoff.exceptions import NoEntryPointGroupError


class SomeResourceLocator(ResourceLocatorMixin):
    entry_point_group = "some_entry_point_group"


class SomeResource(object):
    pass


@pytest.fixture(scope="function")
def resource_locator():
    locator = SomeResourceLocator()
    locator.register_resources()
    # safer way to do this?
    locator._ResourceLocatorMixin__resources['dummy'] = SomeResource
    yield locator


class TestMixin(object):

    def test_get_resource(self, resource_locator):
        resource = resource_locator.get_resource('dummy')
        assert resource == SomeResource

    def test_get_resource_not_found(self, resource_locator):
        with pytest.raises(ResourceNotFoundError):
            resource_locator.get_resource('not_found')

    def test_get_resource_no_entry_point(self, resource_locator):
        with pytest.raises(NoEntryPointGroupError):
            ResourceLocatorMixin().register_resources()
