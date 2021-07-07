# Copyright 2021-present, Nike, Inc.
# All rights reserved.
#
# This source code is licensed under the Apache-2.0 license found in
# the LICENSE file in the root directory of this source tree.

import os
from pprint import pformat
import logging

from faker import Faker
import pandas as pd

from knockoff.utilities.functools import call_with_args_kwargs

logger = logging.getLogger(__name__)

KNOCKOFF_ATTEMPT_LIMIT_ENV = "KNOCKOFF_ATTEMPT_LIMIT"


def load_faker_component_generator(source, assembler, name):
    fake = Faker()

    def generator():
        while True:
            yield call_with_args_kwargs(getattr(fake,
                                        source.config['method']),
                                        source.config.get('args'),
                                        source.config.get('kwargs'))
    return generator()


def load_faker(source, assembler, name):
    fake = Faker()
    data = set()
    i = 0
    limit = int(os.environ.get(KNOCKOFF_ATTEMPT_LIMIT_ENV, 1000000))
    while len(data) < source.config['number'] and i < limit:
        item = call_with_args_kwargs(getattr(fake, source.config['method']),
                                     source.config.get('args'),
                                     source.config.get('kwargs'))
        if isinstance(item, (list, tuple)):
            tuple(item)
        if item not in data:
            data.add(item)
        i += 1
    if i >= limit:
        logger.error(pformat(source.config))
        raise Exception("Attempts to create unique set reached: {}"
                        .format(limit))

    # TODO: move to property / function that lazily checks env var that be
    #       used globally for package
    KNOCKOFF_TEST_MODE = (os.environ
                          .get("KNOCKOFF_TEST_MODE", '0')
                          .lower()) in {'1', 'true', 'y', 'yes'}
    return pd.DataFrame(sorted(data)) if KNOCKOFF_TEST_MODE else pd.DataFrame(data)
