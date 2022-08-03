# Copyright 2021-present, Nike, Inc.
# All rights reserved.
#
# This source code is licensed under the Apache-2.0 license found in
# the LICENSE file in the root directory of this source tree.


import logging
from abc import ABCMeta, abstractmethod
from collections import namedtuple

from sqlalchemy import MetaData, Table, inspect
from sqlalchemy.dialects import postgresql, mysql
from sqlalchemy.types import JSON
from sqlalchemy.exc import NoSuchTableError
from sqlalchemy.dialects.mysql import TINYINT
from sqlalchemy import create_engine

from faker import Faker
from numpy import random

from knockoff.utilities.io import to_sql
from knockoff.orm import get_engine, get_child_tables
from .constraints import KnockoffUniqueConstraint
from .dag import DagService, Node

logger = logging.getLogger(__name__)


class KnockoffDatabaseService(metaclass=ABCMeta):

    Schema = namedtuple("Schema", ["columns", "dtype"])

    @abstractmethod
    def reflect_table(self, name):
        return  # pragma: no cover

    @abstractmethod
    def insert(self, name, df, dtype=None):
        return  # pragma: no cover

    @abstractmethod
    def reflect_unique_constraints(self, name):
        return  # pragma: no cover

    @abstractmethod
    def has_table(self, name):
        return  # pragma: no cover

    @abstractmethod
    def reflect_schema(self, name) -> Schema:
        return  # pragma: no cover


class DefaultDatabaseService(KnockoffDatabaseService):
    def __init__(self, engine=None, **kwargs):
        self.engine = engine or get_engine()
        # No longer using the engine directly. Recreating with url instead
        # since we were getting "TypeError: argument 2 must be a connection,
        # cursor or None" when testing with mysql
        self.url = str(self.engine.url)
        self.kwargs = {
            'if_exists': 'append',
            'index': False,
            'method': 'multi'
        }
        self.kwargs.update(kwargs)

    def has_table(self, name):
        engine = create_engine(self.url)
        with engine.connect() as conn:
            return conn.dialect.has_table(conn, name)

    def _resolve_table_name_postgresql(self, name, conn):
        inspector = inspect(conn)
        try:
            inspector.get_table_oid(name)
            return name
        except NoSuchTableError:
            # if this is a postgres partitioned table, we'll try to load
            # with a child table
            logger.warning("Got NoSuchTableError for {}. "
                           "Will attempt to get child partitions "
                           "in case this is a postgres partitioned "
                           "table.".format(name))
            names = get_child_tables(name, engine=self.engine)
            if names:
                return names[0]
            raise

    def _resolve_table_name(self, name):
        engine = create_engine(self.url)
        with engine.connect() as conn:
            dialect = conn.dialect.name
            if dialect == postgresql.dialect.name:
                return self._resolve_table_name_postgresql(name, conn)
            # so far there are no special cases we've had to deal with
            # for other dialects like postgresql partitioned tables
            return name

    def reflect_table(self, name):
        if not self.has_table(name):
            raise NoSuchTableError(name)
        meta = MetaData()
        engine = create_engine(self.url)
        with engine.connect() as conn:
            table = Table(self._resolve_table_name(name), meta, autoload=True, autoload_with=conn)
            table.name = name  # we do this in case we needed to use the resolved child table of a partition
            return table

    def reflect_schema(self, name):
        table = self.reflect_table(name)
        dialect = self.engine.dialect.name
        dtype = {}
        columns = []
        for col in table.c:
            columns.append(col.name)
            if (dialect == mysql.dialect.name and
                    isinstance(col.type, TINYINT) and
                    (col.type.display_width == 1)):
                # special mysql case for booleans
                dtype[col.name] = bool
            else:
                dtype[col.name] = col.type.python_type
        return self.Schema(columns=columns, dtype=dtype)

    def reflect_unique_constraints(self, name):
        if not self.has_table(name):
            raise NoSuchTableError(name)
        name = self._resolve_table_name(name)
        engine = create_engine(self.url)
        with engine.connect() as conn:
            insp = inspect(conn)
            response = insp.get_pk_constraint(name)
            constraints = [KnockoffUniqueConstraint(response['constrained_columns'],
                                                    name=response['name'])]

            unique_constraints = insp.get_unique_constraints(name)

            for constraint in unique_constraints:
                constraints.append(KnockoffUniqueConstraint(constraint['column_names'],
                                                            name=constraint['name']))
            return constraints

    def insert(self, name, df, dtype=None, parallelize=True):
        kwargs = self.kwargs.copy()
        # TODO: handle dtype[col] = JSON different?
        if dtype:
            kwargs['dtype'] = dtype

        to_sql(
            df,
            name,
            self.url,
            parallelize=parallelize,
            **kwargs
        )


class KnockoffDB(object):
    """
    This class is responsible for orchestrating the
    generation of knockoff data based on the knockoff
    table definitions and dependencies provided. It
    can also insert the data into their corresponding
    database tables.
    """
    def __init__(self, database_service,
                 dag_service=None,
                 seed=None):
        self.database_service = database_service
        self.dag_service = dag_service or DagService()
        self.seed = seed
        self._tables = {}

    @property
    def tables(self):
        return self._tables

    def add(self, table, insert=True, depends_on=None):
        """
        :param table: KnockoffTable
        :param insert: boolean, default True
            If True, will attempt to insert the knockoff data into the
            corresponding database table
        :param depends_on: list[str], default None
            List of table names that are the table being added has a
            dependency on.
        :return:
        """
        # TODO: should we automatically check for KnockoffTableFactory
        #       to add thoes as dependencies?
        node = Node(table.name, table=table, insert=insert)
        self.tables[table.name] = table
        self.dag_service.add_node(node, depends_on=depends_on)

    def prepare(self):
        for node in self.dag_service.iter_topologically():
            node.table.prepare(database_service=self.database_service)

    def build(self):
        dfs = {}
        # TODO: parallelize?
        for node in self.dag_service.iter_topologically():
            table = node.table
            table.prepare(database_service=self.database_service)
            dfs[table.name] = table.df
        return dfs

    def insert(self):
        # TODO: Should we use the dfs from self.build()?
        # TODO: parallelize?
        for node in self.dag_service.iter_topologically():
            table = node.table
            table.prepare(database_service=self.database_service)
            if not node.insert:
                _ = node.table.build() # create table needed downstream
                continue
            dtype = {}
            for c, t in table.dtype.items():
                if t == dict:
                    dtype[c] = JSON
            self.database_service.insert(table.name, table.df, dtype=dtype)

    @property
    def seed(self):
        return self._seed

    @seed.setter
    def seed(self, seed):
        if seed:
            Faker.seed(seed)
            random.seed(seed)
        self._seed = seed
