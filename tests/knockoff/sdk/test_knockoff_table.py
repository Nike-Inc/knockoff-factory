# Copyright 2021-present, Nike, Inc.
# All rights reserved.
#
# This source code is licensed under the Apache-2.0 license found in
# the LICENSE file in the root directory of this source tree.


import pytest
import pandas as pd
import numpy as np

from operator import itemgetter
from unittest import TestCase
from sqlalchemy import create_engine

from knockoff.sdk.table import KnockoffTable
from knockoff.sdk.constraints import KnockoffUniqueConstraint
from knockoff.sdk.db import KnockoffDB, DefaultDatabaseService
from knockoff.sdk.factory.column import ChoiceFactory, FakerFactory, ColumnFactory
from knockoff.sdk.factory.collections import KnockoffTableFactory, KnockoffDataFrameFactory
from knockoff.sdk.factory.next_strategy.df import cycle_df_factory
from knockoff.exceptions import AttemptLimitReached
from knockoff.testing_postgresql import TEST_POSTGRES_ENABLED

from tests.knockoff.data_model import Base, SOMETABLE, SomeTable


@pytest.fixture(scope="function")
def empty_db_with_tbl(empty_db):
    with create_engine(empty_db.url).connect() as conn:
        Base.metadata.create_all(conn)
    yield empty_db


@pytest.fixture(scope="function")
def knockoff_db(empty_db):
    database_service = DefaultDatabaseService(engine=empty_db.engine)
    knockoff_db = KnockoffDB(database_service=database_service)
    yield knockoff_db


@pytest.mark.usefixtures("seed")
class TestKnockoffTable(object):

    @pytest.mark.skipif(not TEST_POSTGRES_ENABLED,
                        reason="postgres not available")
    def test_default_from_table_object(self, empty_db_with_tbl, knockoff_db):

        table = KnockoffTable(SomeTable.__table__,
                              size=3)

        knockoff_db.add(table)
        knockoff_db.insert()

        with create_engine(empty_db_with_tbl.url).connect() as conn:
            df = pd.read_sql_table(SOMETABLE, conn)

        assert df.shape == (3, 7)

    def test_df_default_from_table_object(self):
        table = KnockoffTable(SomeTable.__table__, size=3)
        df = table.build()
        assert df.shape == (3, 7)

    @pytest.mark.skipif(not TEST_POSTGRES_ENABLED,
                    reason="postgres not available")
    def test_default_from_db_reflect(self, empty_db_with_tbl, knockoff_db):
        table = KnockoffTable(SOMETABLE,
                              size=3,
                              autoload=True)

        knockoff_db.add(table)
        knockoff_db.insert()

        with create_engine(empty_db_with_tbl.url).connect() as conn:
            df = pd.read_sql_table(SOMETABLE, conn)

        assert df.shape == (3, 7)

    def test_unique_constraint(self):
        table = KnockoffTable(SOMETABLE, size=15,
                              columns=["col1", "col2", "col3"],
                              constraints=[
                                  KnockoffUniqueConstraint(['col1', 'col2']),
                                  KnockoffUniqueConstraint(['col3']),
                              ],
                              factories=[
                                  ("col1", FakerFactory("pyint",
                                                        min_value=0,
                                                        max_value=10)),
                                  ("col2", FakerFactory("pyint",
                                                        min_value=0,
                                                        max_value=10)),
                                  ("col3", FakerFactory("pyint",
                                                        min_value=0,
                                                        max_value=50))
                              ])
        df = table.build()
        assert df.shape == (15, 3)
        assert len(set(zip(df.col1, df.col2))) == 15
        assert len(set(df.col3)) == 15

    @pytest.mark.skipif(not TEST_POSTGRES_ENABLED,
                    reason="postgres not available")
    def test_unique_constraint_reflection(self, empty_db_with_tbl, knockoff_db):
        table = KnockoffTable(SOMETABLE, size=15,
                              autoload=True,
                              factories=[
                                  ("id", FakerFactory("pyint",
                                                      min_value=0,
                                                      max_value=50)),
                                  ("str_col", ChoiceFactory(["a", "b", "c"])),
                                  ("int_col", FakerFactory("pyint",
                                                           min_value=0,
                                                           max_value=10))
                              ])
        table.prepare(database_service=knockoff_db.database_service)
        df = table.build()

        assert len(table.constraints) == 2
        assert df.shape == (15, 7)
        assert len(set(zip(df.str_col, df.int_col))) == 15
        assert len(set(df["id"])) == 15

    def test_attempt_limit_reached(self):
        table = KnockoffTable(SOMETABLE, size=10,
                              columns=["col1"],
                              factories=[
                                  ("col1", ChoiceFactory(["onlyone"]))
                              ],
                              constraints=[KnockoffUniqueConstraint(["col1"])],
                              attempt_limit=20)
        with pytest.raises(AttemptLimitReached):
            table.build()

    @pytest.mark.skipif(not TEST_POSTGRES_ENABLED,
                    reason="postgres not available")
    def test_default(self, empty_db, knockoff_db):

        table = KnockoffTable(SOMETABLE, size=3,
                              columns=["col1", "col2"])

        knockoff_db.add(table)
        knockoff_db.insert()

        with create_engine(empty_db.url).connect() as conn:
            df = pd.read_sql_table(SOMETABLE, conn)

        # TODO: We were initially testing against expected
        #       values that came based on the seed set. However,
        #       we had an issue where the values in the CI were
        #       slightly different in the CI build than locally
        #       (even using the same docker image locally)
        #       The difference was the random str value that
        #       Faker was generating locally vs in the CI:
        #       e.g.: "r1-905871V" vs. "r1-905871v"

        assert df.shape == (3, 2)

        for record in df.to_dict('records'):
            assert (isinstance(record['col1'], str)
                    and isinstance(record['col2'], str))

    @pytest.mark.skipif(not TEST_POSTGRES_ENABLED,
                        reason="postgres not available")
    def test_dtype(self, empty_db, knockoff_db):

        table = KnockoffTable(SOMETABLE, size=3,
                              columns=["col1", "col2"],
                              dtype={"col1": int})

        knockoff_db.add(table)
        knockoff_db.insert()

        with create_engine(empty_db.url).connect() as conn:
            df = pd.read_sql_table(SOMETABLE, conn)

        assert df.shape == (3, 2)

        for record in df.to_dict('records'):
            assert isinstance(record['col1'],
                              int) and isinstance(record['col2'],
                                                  str)

    @pytest.mark.skipif(not TEST_POSTGRES_ENABLED,
                    reason="postgres not available")
    def test_autoload_and_dtype(self, empty_db_with_tbl, knockoff_db):

        table = KnockoffTable(SOMETABLE, size=3,
                              autoload=True,
                              dtype={"str_col": int})
        knockoff_db.add(table)
        knockoff_db.insert()

        for i in table.df["str_col"]:
            assert isinstance(i, int)

        with create_engine(empty_db_with_tbl.url).connect() as conn:
            df = pd.read_sql_table(SOMETABLE, conn)

        assert df.shape == (3, 7)
        assert set(table.df['str_col'].values) == {int(i) for i in df['str_col']}

    def test_with_column_factory(self):
        choices = ["red", "blue", "green"]
        color_factory = ChoiceFactory(choices)
        table = KnockoffTable(SOMETABLE, size=30, columns=["color"],
                              factories=[("color", color_factory)])
        df = table.build()
        assert df.shape == (30, 1)
        assert set(choices) == set(df.color.values)

    @pytest.mark.skipif(not TEST_POSTGRES_ENABLED,
                    reason="postgres not available")
    def test_with_table_factory(self, empty_db_with_tbl, knockoff_db):

        table = KnockoffTable(SOMETABLE,
                              autoload=True,
                              size=10)

        factory = KnockoffTableFactory(table, columns=["int_col", "bool_col"],
                                       rename={"int_col": "col1"})

        name = "someothertable"
        table2 = KnockoffTable(name, factories=[factory],
                               columns=["col1", "bool_col", "col2"],
                               size=4)

        knockoff_db.add(table)
        knockoff_db.add(table2, depends_on=[SOMETABLE])
        knockoff_db.insert()

        with create_engine(empty_db_with_tbl.url).connect() as conn:
            df1 = pd.read_sql_table(SOMETABLE, conn)
            df2 = pd.read_sql_table(name, conn)

        assert df1.shape == (10, 7)
        assert df2.shape == (4, 3)

        tbl1_set = set(zip(df1.int_col, df1.bool_col))

        for record in df2.to_dict('records'):
            assert itemgetter('col1', 'bool_col')(record) in tbl1_set
            assert (isinstance(record['col1'], int)
                    and isinstance(record['col2'], str)
                    and isinstance(record['bool_col'], bool))

    def test_with_dataframe_factory(self):
        df1 = pd.DataFrame({
            "col1": [1, 2, 3],
            "col2": [4, 5, 6]
        })
        factory = KnockoffDataFrameFactory(df1)

        table = KnockoffTable(SOMETABLE, size=30,
                              columns=["col1", "col2", "col3"],
                              factories=[factory])

        df2 = table.build()

        assert df2.shape == (30, 3)
        assert set(zip(df1.col1, df1.col2)) == set(zip(df2.col1, df2.col2))

    def test_with_dataframe_factory_cycle_generator(self):
        df1 = pd.DataFrame({
            "col1": [1, 2, 3],
            "col2": [4, 5, 6]
        })

        factory = KnockoffDataFrameFactory(df1,
                                           next_strategy_factory=cycle_df_factory)
        table = KnockoffTable(SOMETABLE, size=30,
                              columns=["col1", "col2", "col3"],
                              factories=[factory])
        df2 = table.build()
        assert df2.shape == (30, 3)
        assert (pd.concat([df1]*10).reset_index(drop=True)
                .equals(df2[['col1', 'col2']]))

    def test_table_using_column_factory(self):
        table = KnockoffTable(
            "sometable",
            columns=["a", "b", "c"],
            factories=[
                ColumnFactory("a", lambda: 1),
                ColumnFactory("b", lambda: 2),
                ColumnFactory("c", lambda a,b: a + b, depends_on=["a", "b"]),
            ],
            size=3
        )
        actual = table.build()
        expected = pd.DataFrame({"a": [1]*3,
                                 "b": [2]*3,
                                 "c": [3]*3})
        assert actual.equals(expected)

    def test_name_or_table_value_error(self):
        with pytest.raises(ValueError):
            # Need to pass SomeTable.__table__ to avoid error
            KnockoffTable(SomeTable, size=100)

    @pytest.mark.parametrize(
        "kwargs,expected",
        [({"drop": ["id", "json_col"], "rename": {"bool_col": "binary_col"}},
          {"str_col", "binary_col", "dt_col",
           "int_col", "float_col"}),
         ({"rename": {"int_col": "integer_col",
                      "str_col": "string_col"}},
          {"id", "string_col", "bool_col", "dt_col",
           "integer_col", "float_col", "json_col"}),
         ({"drop": ["id", "json_col"]},
          {"str_col", "bool_col", "dt_col",
           "int_col", "float_col"})])
    def test_table_using_drop_or_rename(self, kwargs, expected):
        df = KnockoffTable(
            SomeTable.__table__,
            size=100,
            constraints=[
                KnockoffUniqueConstraint(['id']),
                KnockoffUniqueConstraint(['str_col', 'int_col']),
            ],
            **kwargs
        ).build()
        actual = set(df.columns)
        TestCase().assertSetEqual(actual, expected)

    def test_no_size_provided(self):
        with pytest.raises(ValueError):
            KnockoffTable(SOMETABLE).build()

    def test_no_columns_provided(self):
        with pytest.raises(ValueError):
            KnockoffTable(SOMETABLE).build(size=10)
