# Copyright 2021-present, Nike, Inc.
# All rights reserved.
#
# This source code is licensed under the Apache-2.0 license found in
# the LICENSE file in the root directory of this source tree.


import logging

from knockoff.orm import get_engine
from joblib import Parallel, delayed

logger = logging.getLogger(__name__)


def _to_sql(df, engine_builder, table, **kwargs):
    engine = engine_builder.build()
    with engine.connect() as conn:
        df.to_sql(table, conn, method="multi", **kwargs)


def to_sql(sink, table, df):
    logger.info("Populating table: {}".format(table))

    chunksize = sink.config.get("chunksize", 10000)
    n_jobs = sink.config.get("n_jobs", -1)
    parallelize = sink.config.get("parallelize", True)
    database = sink.config.get('database')
    kwargs = sink.config.get('kwargs', {})
    engine_builder = get_engine(database, build='builder')
    if parallelize:
        Parallel(n_jobs=n_jobs)(delayed(_to_sql)(df[i:i+chunksize],
                                                 engine_builder,
                                                 table,
                                                 **kwargs)
                                for i in range(0, len(df),
                                               chunksize))
    else:
        _to_sql(df, engine_builder, table, **kwargs)

    logger.info("Populated table: {}".format(table))


def to_parquet(sink, table, df):
    logger.info("Writing table ({}) to parquet.".format(table))
    df.to_parquet(sink.config['fname'],
                  **sink.config.get('kwargs', {}))
    logger.info("Wrote table ({}) to parquet.".format(table))
