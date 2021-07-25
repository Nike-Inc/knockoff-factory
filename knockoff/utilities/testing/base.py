# Copyright 2021-present, Nike, Inc.
# All rights reserved.
#
# This source code is licensed under the Apache-2.0 license found in
# the LICENSE file in the root directory of this source tree.


import os
import re
from uuid import uuid4
from sqlalchemy import create_engine
from sqlalchemy.pool import NullPool


TRUTH_VALUES = {'1', 't', 'true'}

TEST_USE_EXTERNAL_DB = os.getenv('TEST_USE_EXTERNAL_DB',
                                 '1').lower() in TRUTH_VALUES


class ExternalDB:
    def __init__(self,
                 url,
                 create_db,
                 drop_db,
                 db_name=None):
        self.db_name = db_name or 'test_' + str(uuid4()).replace('-', '')
        self.create_db = create_db
        self.drop_db = drop_db
        self.engine = create_engine(url)
        create_db(self.engine, self.db_name)

    def url(self):
        # Substitute db name in URI with generated db
        url = re.sub(
            "(?:/[A-Za-z0-9_]+)$", "/{}".format(self.db_name), str(self.engine.url)
        )
        engine = create_engine(url, pool=NullPool)
        url = str(engine.url)
        return url

    def __enter__(self):
        return self

    def __exit__(self, exception_type, exception_value, traceback):
        self.stop()

    def stop(self):
        self.drop_db(self.engine, self.db_name)
        self.engine.dispose()
