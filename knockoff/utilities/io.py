import logging

from sqlalchemy import create_engine
from sqlalchemy.pool import NullPool
from joblib import Parallel, delayed

logger = logging.getLogger(__name__)


def _to_sql(df, table, url, **kwargs):
    to_sql_kwargs = {
        'index': False,
        'method': 'multi',
        'if_exists': 'append'
    }
    to_sql_kwargs.update(kwargs)
    # TODO: test performance without Nullpool?
    engine = create_engine(url, poolclass=NullPool)
    with engine.connect() as conn:
        df.to_sql(table, conn, **to_sql_kwargs)


def to_sql(df,
           table,
           url,
           parallelize=True,
           chunksize=1000,
           n_jobs=-1,
           **kwargs):
    logger.info("Populating table: {}".format(table))
    if parallelize:
        Parallel(n_jobs=n_jobs)(
            delayed(_to_sql)(
                df[i:i+chunksize],
                table,
                url,
                **kwargs
            ) for i in range(0, len(df), chunksize))
    else:
        _to_sql(df, table, url, **kwargs)
    logger.info("Populated table: {}".format(table))
