# Copyright 2021-present, Nike, Inc.
# All rights reserved.
#
# This source code is licensed under the Apache-2.0 license found in
# the LICENSE file in the root directory of this source tree.


import os
import logging
from datetime import datetime

from sqlalchemy import Table

import pandas as pd

from faker import Faker
from knockoff.exceptions import FactoryNotFound, AttemptLimitReached


logger = logging.getLogger(__name__)


KNOCKOFF_ATTEMPT_LIMIT_ENV = "KNOCKOFF_ATTEMPT_LIMIT"


class KnockoffTable(object):

    def __init__(self, name_or_table,
                 factories=None,
                 columns=None,
                 autoload=False,
                 ignore_constraints_on_autoload=False,
                 dtype=None,
                 constraints=None,
                 default_type_factory=None,
                 faker=None,
                 attempt_limit=None,
                 size=None,
                 database_service=None,
                 table=None,
                 ):

        if isinstance(name_or_table, Table):
            self.name = name_or_table.name
            # used to set columns and dtype
            self._table = name_or_table
        else:
            self.name = name_or_table
            self._table = None

        if table is not None:
            # overrides table from name_or_table
            # intended use-case is if you want
            # to upload based on an existing table
            # definition to a table of a different name
            self._table = table

        self.factories = factories or []
        self.columns = columns
        self._is_prepared = False
        # autoload: whether or not to reflect the schema
        self.autoload = autoload
        self.dtype = dtype or {}
        self.constraints = constraints or []
        self.faker = faker or Faker()
        self.attempt_limit = attempt_limit or int(os.getenv(KNOCKOFF_ATTEMPT_LIMIT_ENV, 1000000))
        self.default_type_factory = default_type_factory or {}
        self.size = size
        self._df = None
        self.database_service = database_service
        self.ignore_constraints_on_autoload = ignore_constraints_on_autoload

    def prepare(self, lazy=True,
                database_service=None,
                autoload=None):
        """
        Precedence of columns:
        1) Provided by columns directly from __init__
        2) Provided by columns from table from __init__
        3) Provided by columns from table from autloading table by name

        Precedence of dtype:
        1) Provided by dtype directly from __init__
        2) Provided by table from __init__
        3) Provided by table autoloaded by name
        4) Default to string for column

        TODO: should we save the original init params for reset?
              or do we only allow reset of constraints?

        :param lazy:
        :return:
        """
        if lazy and self._is_prepared:
            return # if we're lazy and columns are initialized, do nothing

        dtype = {}
        columns = None

        if autoload or self.autoload:
            database_service = database_service or self.database_service
            assert database_service is not None, "DatabaseService required for autoload"
            table = database_service.reflect_table(self.name)
            columns, types = zip(*[(c.name, c.type.python_type) for c in table.c])
            dtype.update(dict(zip(columns, types)))

            if not self.ignore_constraints_on_autoload:
                constraints = database_service.reflect_unique_constraints(self.name)
                self.constraints.extend(constraints)

        if self._table is not None:
            columns, types = zip(*[(c.name, c.type.python_type) for c in self._table.c])
            dtype.update(dict(zip(columns, types)))

        self._columns = self._columns or columns
        assert self._columns is not None

        # dtype provided by init take precedence
        dtype.update(self.dtype)
        self.dtype = dtype

        self._is_prepared = True

    @property
    def columns(self):
        # TODO should we instead assert that table has been prepared?
        self.prepare(lazy=True)
        return self._columns

    @columns.setter
    def columns(self, columns):
        self._columns = columns

    @property
    def df(self):
        if self._df is None:
            self.build() # TODO: do we want to do this?
        return self._df

    @property
    def default_type_factory(self):
        return self._default_type_factory

    @default_type_factory.setter
    def default_type_factory(self, default_type_factory):
        # defaults
        self._default_type_factory = {
            int: self.faker.pyint,
            float: self.faker.pyfloat,
            str: self.faker.pystr_format,
            bool: self.faker.pybool,
            datetime: self.faker.date_time,
            dict: lambda: {}
        }
        self._default_type_factory.update(default_type_factory)

    def copy_factory(self, columns=None, rename=None):
        columns = columns or self.columns
        rename = rename or {}

        def factory():
            record = self.build_record()
            out = []
            for col in columns:
                out[rename.get(col, col)] = record[col]
            return out
        return factory

    def build_record(self):
        """TODO: should this be public?"""
        data = {}
        for factory in self.factories:
            if isinstance(factory, (tuple, list)):
                col, factory = factory
                key_values = {col: factory()}
            else:
                key_values = factory()
            data.update(key_values)
        record = {}
        for col in self.columns:
            if col not in data:
                try:
                    type_ = self.dtype.get(col, str)
                    factory = self.default_type_factory[type_]
                    record[col] = factory()
                except KeyError:
                    raise FactoryNotFound("[table={}] No column factory provided"
                                          " for column={} or type={}"
                                          .format(self.name, col, type_))
            else:
                record[col] = data[col]
        return record

    def _check_constraints(self, record):
        constraints_satisfied = True
        for constraint in self.constraints:
            if not constraint.check(record):
                constraints_satisfied = False
                break
        return constraints_satisfied

    def _add_record(self, record):
        """add record to constraints if they need to track for future violations"""
        for constraint in self.constraints:
            constraint.add(record)

    def _next(self):
        attempt = 0
        while attempt < self.attempt_limit:
            attempt += 1

            record = self.build_record()

            if self._check_constraints(record):
                self._add_record(record)
                return record

        if attempt >= self.attempt_limit:
            raise AttemptLimitReached("Attempts to create df with unique "
                                      "constraint reached limit={} for table={}"
                                      .format(self.attempt_limit, self.name))

    def build(self, size=None):
        size = size or self.size
        assert size is not None
        # TODO: do this more memory efficiently?
        self._df = pd.DataFrame([self._next() for _ in range(size)])
        return self.df

    def reset(self):
        self._df = None
        for constraint in self.constraints:
            constraint.reset()
