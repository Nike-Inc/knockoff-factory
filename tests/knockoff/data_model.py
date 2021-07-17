# Copyright 2021-present, Nike, Inc.
# All rights reserved.
#
# This source code is licensed under the Apache-2.0 license found in
# the LICENSE file in the root directory of this source tree.


from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy import JSON, Column, PrimaryKeyConstraint, UniqueConstraint
from sqlalchemy.types import Integer, String, Boolean, DateTime, BigInteger, Float

Base = declarative_base()

SOMETABLE = "sometable"


class SomeTable(Base):
    """A class that can be used for testing"""
    __tablename__ = SOMETABLE
    id = Column(BigInteger, autoincrement=True)
    str_col = Column(String)
    bool_col = Column(Boolean)
    dt_col = Column(DateTime)
    int_col = Column(Integer)
    float_col = Column(Float)
    json_col = Column(JSON)
    __table_args__ = (
        PrimaryKeyConstraint('id'),
        UniqueConstraint('str_col', 'int_col')
    )
