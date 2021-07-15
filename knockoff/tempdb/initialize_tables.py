# Copyright 2021-present, Nike, Inc.
# All rights reserved.
#
# This source code is licensed under the Apache-2.0 license found in
# the LICENSE file in the root directory of this source tree.


from sqlalchemy import create_engine


class SqlAlchemyInitTablesFunc(object):
    def __init__(self, base):
        """
        Parameters
        ----------
        base: sqlachlemy.ext.declarative_base() class
        """
        self.base = base

    def __call__(self, url):
        engine = create_engine(url)
        self.base.metadata.create_all(engine)
