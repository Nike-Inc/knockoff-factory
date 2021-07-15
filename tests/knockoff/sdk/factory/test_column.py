# Copyright 2021-present, Nike, Inc.
# All rights reserved.
#
# This source code is licensed under the Apache-2.0 license found in
# the LICENSE file in the root directory of this source tree.


import pytest
from unittest import TestCase
from mock import MagicMock, patch

from knockoff.sdk.factory.column import ColumnFactory, ChoiceFactory, FakerFactory
from knockoff.sdk.table import KnockoffTable


class TestColumn(object):
    @pytest.mark.parametrize("input,expected",
        [(lambda: 1, {'col': 1}),
         (lambda: 2, {'col': 2}),
         (lambda: 3, {'col': 3})]
    )
    def test_column_factory(self, input, expected):
        factory = ColumnFactory('col', input)
        actual = factory()
        TestCase().assertDictEqual(actual, expected)

    def test_faker_factory(self):
        mock_faker = MagicMock()
        expected = 123
        mock_faker.some_method.return_value = expected
        factory = FakerFactory('some_method',
                               faker=mock_faker,
                               some_kwarg='some_value')
        actual = factory()
        assert actual == expected
        mock_faker.some_method.assert_called_once_with(some_kwarg='some_value')


    def test_choice_factory(self):
        mock_choice = MagicMock()
        choices = [1,2,3]
        p = [.2, .3, .5]
        replace = None
        factory = ChoiceFactory([1,2,3], p=p, replace=replace)
        with patch('knockoff.sdk.factory.column.np.random.choice',
                   mock_choice):
            factory()
            mock_choice.assert_called_once_with(choices,
                                                p=p,
                                                replace=replace,
                                                size=None)
            p2 = [.3, .3, .4]
            factory(size=2, p=p2, replace=True)
            mock_choice.assert_called_with(choices, p=p2,
                                           replace=True, size=2)

    def test_depends_on(self):
        add_one_to_col_factory = ColumnFactory(
            "col+1",
            lambda col: col+1,
            depends_on="col"
        )
        assert add_one_to_col_factory(col=2)["col+1"] == 3

    def test_depends_on_missing_arg(self):
        add_one_to_col_factory = ColumnFactory(
            "col+1",
            lambda col: col+1,
            depends_on="col"
        )
        with pytest.raises(TypeError):
            add_one_to_col_factory()
