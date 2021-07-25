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

from .factory.column import ColumnFactory
from .factory.collections import CollectionsFactory

logger = logging.getLogger(__name__)

KNOCKOFF_ATTEMPT_LIMIT_ENV = "KNOCKOFF_ATTEMPT_LIMIT"


class KnockoffTable(object):
    """
    KnockoffTable declares how knockoff should populate a table.
    """
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
                 drop=None,
                 rename=None,
                 ):
        """
        :param name_or_table: str or sqlalchemy.Table
            This provides the name of the table. If a sqlalchemy.Table class is
            provided, it will be used to derive the columns and dtype of the
            table unless those are directly provided as __init__ parameters.

        :param factories: list, default None
            This is a list of factories. Factories are expected to be callables
            that return a dict of columns as keys and values for a single row or
            record.

            knockoff.factory.column.ColumnFactory and
            knockoff.factory.collections.CollectionsFactory both have a depends_on
            parameter which takes a list of keys that will be provided to the factory
            with kwargs where the key-values are looked up from a dict
            populated with previously returned key-values.

            Factories will be called in the order provided and subsequently
            generated keys' value will take precedence over previously generated ones.

            If no factories are provided, a default factory will be used based on
            the configured self.default_type_factory property.

        :param columns: list, default None
            This is a list of column names for the table. The order of precedence in
            which the columns are set is as follows:

            1) Provided by columns directly from __init__
            2) Provided by columns derived from table from name_or_table (if type==sqlalchemy.Table)
            3) Provided by columns from table via autoloaded table by name (requires
               database service on __init__ or via self.build(..) call. The KnockoffDB will
               provide a database service to the KnockoffTable if one is provided.

            If no columns are provided a ValueError is raised.

        :param autoload: boolean, default False
            If autoload is True, knockoff will attempt to automatically reflect the table columns, dtypes and
            constraints (primary key and unique) from the corresponding database table (by name)
            assuming a database service is provided at __init__ or
            during self.build(..) which is the case if provided to a KnockoffDB

        :param ignore_constraints_on_autoload: boolean, default False
            If True, knockoff will ignore any constraints (primary key and unique) when reflecting the
            table columns and dtypes from the database table

        :param dtype: dict, default None
            dict of column to type which determines the factory to use for each type
            if no factory is specified for a column. dtypes follow the same precedence as columns with
            a default value of str given to any column that doesn't have a dtype defined.

        :param constraints: list[KnockoffConstraint], default None
            This is a list of KnockoffConstraint's (e.g. KnockoffUniqueConstraint)

        :param default_type_factory: dict, default None
            dict of type to factory to use by default if no factory is provided for a column

        :param faker: Faker instance, default None
            Faker instance used to create default_type_factory if None is provided

        :param attempt_limit: int, default 1000000
            This is the maximum number attempts knockoff will take to generate a single
            row that satisfies all constraints until a knockoff.exceptions.AttemptLimitReached
            error is raised. attempt_limits provided as a parameter take precedence, but it
            can also be set with the KNOCKOFF_ATTEMPT_LIMIT environment variable.

        :param size: int, default None
            This is the number of rows to generate for the table. This is expected to be
            provided as a parameter in the __init__ or during the build. The knockoffDB will
            not provide a size to the table.

        :param database_service: KnockoffDatabaseService instance, default None
            The database service is only required if autoload==True. The database service
            will be provided to the KnockoffTable in the self.build(..) call when used with
            a KnockoffDB instance.

        :param table: sqlalchemy.Table, default None
            If provided this will be used to derive the columns and dtype for the table. This
            parameter is provided separately from name_or_table so the table columns and
            dtype definition can be decoupled from the name.

        :param drop: list[str], default None
            list of columns to drop from the generated DataFrame. Those columns will not be
            inserted into the database or output by the KnockoffDB

        :param rename: dict[str, str], default None
            A mapping of current name to desired name to apply to the generated DataFrame.
        """
        if isinstance(name_or_table, Table):
            self.name = name_or_table.name
            # used to set columns and dtype
            self._table = name_or_table
        elif isinstance(name_or_table, str):
            self.name = name_or_table
            self._table = None
        else:
            raise ValueError(
                f"name_or_table must be a str or sqlalchemy.Table."
                f"Received: {name_or_table} ({type(name_or_table)})."
            )

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
        self.rename = rename or {}
        self.drop = drop or []

    def prepare(self,
                lazy=True,
                database_service=None,
                autoload=None):
        """
        1) Provided by columns directly from __init__
        2) Provided by columns derived from table from name_or_table (if type==sqlalchemy.Table)
        3) Provided by columns from table via autoloaded table by name (requires
           database service on __init__ or via self.build(..) call. The KnockoffDB will
           provide a database service to the KnockoffTable if one is provided.

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
            return  # if we're lazy and columns are initialized, do nothing

        dtype = {}
        columns = None

        if autoload or self.autoload:
            database_service = database_service or self.database_service
            if database_service is None:
                raise ValueError("DatabaseService required for autoload. Must be "
                                 "provided at __init__ or self.prepare(..)")

            schema = database_service.reflect_schema(self.name)
            columns = schema.columns
            dtype.update(schema.dtype)

            if not self.ignore_constraints_on_autoload:
                constraints = database_service.reflect_unique_constraints(self.name)
                self.constraints.extend(constraints)

        if self._table is not None:
            columns, types = zip(*[(c.name, c.type.python_type) for c in self._table.c])
            dtype.update(dict(zip(columns, types)))

        self._columns = self._columns or columns
        if self._columns is None:
            raise ValueError("No columns provided, derived or autoloaded.")

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
            self.build()  # TODO: do we want to do this?
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
            record = self._build_record()
            out = []
            for col in columns:
                out[rename.get(col, col)] = record[col]
            return out

        return factory

    def _build_record(self):
        data = {}
        for factory in self.factories:
            if isinstance(factory, (tuple, list)):
                col, factory = factory
                key_values = {col: factory()}
            elif (isinstance(factory, (ColumnFactory, CollectionsFactory)) and
                  factory.depends_on):
                kwargs = {key: data[key] for key in factory.depends_on}
                key_values = factory(**kwargs)
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

            record = self._build_record()

            if self._check_constraints(record):
                self._add_record(record)
                return record

        if attempt >= self.attempt_limit:
            raise AttemptLimitReached("Attempts to create df with unique "
                                      "constraint reached limit={} for table={}"
                                      .format(self.attempt_limit, self.name))

    def build(self, size=None):
        size = size or self.size
        if size is None:
            raise ValueError("size must be provided on __init__"
                             " or during self.build(..)")
        # TODO: do this more memory efficiently?
        self._df = pd.DataFrame([self._next() for _ in range(size)])

        if self.drop:
            self._df = self._df.drop(columns=self.drop)

        if self.rename:
            self._df = self._df.rename(columns=self.rename)

        return self.df

    def reset(self):
        self._df = None
        for constraint in self.constraints:
            constraint.reset()
