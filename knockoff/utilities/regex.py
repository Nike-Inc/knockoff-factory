# Copyright 2021-present, Nike, Inc.
# All rights reserved.
#
# This source code is licensed under the Apache-2.0 license found in
# the LICENSE file in the root directory of this source tree.


from abc import ABCMeta, abstractmethod

from .functools import abstractproperty2to3


class InvalidStringError(ValueError):
    """ Raised when an invalid string is encountered """

    def __init__(self, string, regex):
        self.string = string
        self.regex = regex

    def __str__(self):
        return ('Invalid string: {}. Regex: {}'
                .format(repr(self.string),
                        repr(self.regex)))


class RegexParser(metaclass=ABCMeta):

    @abstractproperty2to3
    def compiled_regex(self):
        raise NotImplementedError  # pragma: no cover

    @classmethod
    @abstractmethod
    def make(cls, **kwargs):
        return  # pragma: no cover

    @classmethod
    def parse(cls, string):
        m = cls.compiled_regex.match(string)
        if not m:
            raise InvalidStringError(string,
                                     cls.compiled_regex.pattern)
        kwargs = m.groupdict()
        kwargs = {k: v for k, v in kwargs.items() if v is not None}
        return cls.make(**kwargs)
