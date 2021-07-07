# Copyright 2021-present, Nike, Inc.
# All rights reserved.
#
# This source code is licensed under the Apache-2.0 license found in
# the LICENSE file in the root directory of this source tree.


import logging
from sqlalchemy import MetaData, Table, inspect
from sqlalchemy.types import JSON
from sqlalchemy.exc import NoSuchTableError
from interface import Interface, implements, default

from faker import Faker
from numpy import random

from knockoff.orm import get_engine, get_child_tables
from .constraints import KnockoffUniqueConstraint
from .dag import DagService, Node

logger = logging.getLogger(__name__)


class KnockoffDatabaseService(Interface):
    def reflect_table(self, name):
        return

    def insert(self, name, df, dtype=None):
        return

    def reflect_unique_constraints(self, name):
        return

    def has_table(self, name):
        return


class DefaultDatabaseService(implements(KnockoffDatabaseService)):
    def __init__(self, engine=None, **kwargs):
        self.engine = engine or get_engine()
        self.kwargs = {
            'if_exists': 'append',
            'index': False,
            'method': 'multi'
        }
        self.kwargs.update(kwargs)

    def has_table(self, name):
        with self.engine.connect() as conn:
            return conn.dialect.has_table(conn, name)

    def _resolve_table_name(self, name):
        with self.engine.connect() as conn:
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

    def reflect_table(self, name):
        if not self.has_table(name):
            raise NoSuchTableError(name)
        meta = MetaData()
        with self.engine.connect() as conn:
            table = Table(self._resolve_table_name(name), meta, autoload=True, autoload_with=conn)
            table.name = name # we do this in case we needed to use the resolved child table of a partition
            return table

    def reflect_unique_constraints(self, name):
        if not self.has_table(name):
            raise NoSuchTableError(name)
        name = self._resolve_table_name(name)
        with self.engine.connect() as conn:
            insp = inspect(conn)
            response = insp.get_pk_constraint(name)
            constraints = [KnockoffUniqueConstraint(response['constrained_columns'],
                                                    name=response['name'])]

            unique_constraints = insp.get_unique_constraints(name)

            for constraint in unique_constraints:
                constraints.append(KnockoffUniqueConstraint(constraint['column_names'],
                                                            name=constraint['name']))
            return constraints

    def insert(self, name, df, dtype=None):
        kwargs = self.kwargs.copy()
        # TODO: handle dtype[col] = JSON different?
        if dtype:
            kwargs['dtype'] = dtype
        # TODO: parallelize?
        with self.engine.connect() as conn:
            df.to_sql(name, conn,
                      **kwargs)


class KnockoffDB(object):

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
        identify table by name (for depends_on?)

        build graph base on depends on
        :param table:
        :param insert:
        :param depends_on:
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

    def insert(self):
        # TODO: parallelize?
        for node in self.dag_service.iter_topologically():
            table = node.table
            table.prepare(database_service=self.database_service)
            if not node.insert:
                _ = node.table.build() # create table needed downstream
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
