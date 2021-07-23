# Copyright 2021-present, Nike, Inc.
# All rights reserved.
#
# This source code is licensed under the Apache-2.0 license found in
# the LICENSE file in the root directory of this source tree.


import numpy as np
from faker import Faker


class ColumnFactory(object):
    """
    ColumnFactory is a callable that wraps another callable
    so that it can return a dict with the column as the key
    for the value returned by the callable.
    """
    def __init__(self, column, callable_, depends_on=None):
        """
        :param column: str
            Column name that will be used as the
            key for the return
        :param callable_: function
        :param depends_on: list[str], default None
            If this is not None, the strings provided here will
            be used by the KnockoffTable as keys in the kwargs
            when making a call to this instance. The values provided
            for those kwargs are looked up from a dict populated with
            previously returned key-values from calls to preceding factories.
        """
        self.column = column
        self.callable = callable_
        self.depends_on = depends_on

    def __call__(self, *args, **kwargs):
        return {self.column: self.callable(*args,**kwargs)}


class ChoiceFactory(object):
    def __init__(self, choices, p=None, replace=True):
        self.choices = choices
        self.p = p
        self.replace = replace

    def __call__(self, size=None, p=None, replace=None):
        if replace is None:
            replace = self.replace
        return np.random.choice(self.choices,
                                size=size,
                                replace=replace,
                                p=p or self.p)


class FakerFactory(object):
    def __init__(self, method, faker=None, **kwargs):
        self.method = method
        self.faker = faker or Faker()
        self.kwargs = kwargs

    def __call__(self):
        return getattr(self.faker, self.method)(**self.kwargs)
