# Copyright 2021-present, Nike, Inc.
# All rights reserved.
#
# This source code is licensed under the Apache-2.0 license found in
# the LICENSE file in the root directory of this source tree.


import sys
import logging
import glob

import pandas as pd
import s3fs
from pyarrow import parquet as pq

from .utilities.functools import call_with_args_kwargs
from .utilities.mixin import ResourceLocatorMixin
from .orm import get_connection

if sys.version_info[0] < 3:
    from StringIO import StringIO
else:
    from io import StringIO

logger = logging.getLogger(__name__)


class ReaderFactory(ResourceLocatorMixin, object):
    entry_point_group = "knockoff.io.readers"


class WriterFactory(ResourceLocatorMixin, object):
    entry_point_group = "knockoff.io.writers"


def load_strategy_io(source, assembler, name):
    reader = ReaderFactory().get_resource(source.config['reader'])
    args = source.config.get('args')
    kwargs = source.config.get('kwargs')

    return call_with_args_kwargs(reader, args, kwargs)


def read_inline(data, **kwargs):
    return pd.read_csv(StringIO(data), **kwargs)


def read_multi_parquet(path):
    if path.startswith("s3://"):
        s3 = s3fs.S3FileSystem()
        fs = s3fs.core.S3FileSystem()

        s3_path = path.replace("s3://", "", 1)
        s3_paths = fs.glob(path=s3_path)
        return pq.ParquetDataset(s3_paths, filesystem=s3).read_pandas().to_pandas()

    paths = glob.glob(path)
    return pq.ParquetDataset(paths).read_pandas().to_pandas()


def read_sql(sql, database, **kwargs):
    with get_connection(database) as conn:
        return pd.read_sql_query(sql, conn, **kwargs)
