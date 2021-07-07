# Copyright 2021-present, Nike, Inc.
# All rights reserved.
#
# This source code is licensed under the Apache-2.0 license found in
# the LICENSE file in the root directory of this source tree.


import numpy as np
from faker import Faker


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
