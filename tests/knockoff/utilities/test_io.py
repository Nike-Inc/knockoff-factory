import pytest
import pandas as pd
from sqlalchemy.types import JSON

from knockoff.sdk.table import KnockoffTable
from knockoff.sdk.constraints import KnockoffUniqueConstraint
from knockoff.testing_postgresql import TEST_POSTGRES_ENABLED
from knockoff.utilities.io import to_sql

from tests.knockoff.data_model import SomeTable, SOMETABLE


def get_sometable_df(size):
    return KnockoffTable(
        SomeTable.__table__,
        size=size,
        constraints=[
            KnockoffUniqueConstraint(['id']),
            KnockoffUniqueConstraint(['str_col', 'int_col']),
        ]
    ).build()


@pytest.mark.skipif(
    not TEST_POSTGRES_ENABLED,
    reason="postgres not available"
)
class TestIO:

    def test_to_sql(self, empty_db_with_sometable):
        df = get_sometable_df(1000)
        to_sql(
            df,
            SOMETABLE,
            str(empty_db_with_sometable.engine.url),
            chunksize=100,
            dtype={'json_col': JSON}
        )

        df_actual = pd.read_sql_table(
            SOMETABLE,
            empty_db_with_sometable.engine
        )

        df = df.sort_values(by='id').reset_index(drop=True)
        df_actual = df_actual.sort_values(by='id').reset_index(drop=True)
        assert df.equals(df_actual)

    def test_to_sql_single_process(self, empty_db_with_sometable):
        df = get_sometable_df(100)
        to_sql(
            df,
            SOMETABLE,
            str(empty_db_with_sometable.engine.url),
            parallelize=False,
            dtype={'json_col': JSON}
        )

        df_actual = pd.read_sql_table(
            SOMETABLE,
            empty_db_with_sometable.engine
        )

        df = df.sort_values(by='id').reset_index(drop=True)
        df_actual = df_actual.sort_values(by='id').reset_index(drop=True)
        assert df.equals(df_actual)
