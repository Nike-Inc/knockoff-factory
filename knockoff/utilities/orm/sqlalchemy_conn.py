# Copyright 2021-present, Nike, Inc.
# All rights reserved.
#
# This source code is licensed under the Apache-2.0 license found in
# the LICENSE file in the root directory of this source tree.


from sqlalchemy.orm import sessionmaker


class SqlAlchemyConn(object):
    def __init__(self, engine):
        self.engine = engine
        Session = sessionmaker(bind=self.engine)
        self.session = Session()


    def __enter__(self):
        return self

    def __exit__(self, exception_type, exception_value, traceback):
        if exception_type:
            self.session.rollback()
        else:
            self.session.commit()
        self.session.close()
