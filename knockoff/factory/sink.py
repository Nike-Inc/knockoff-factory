# Copyright 2021-present, Nike, Inc.
# All rights reserved.
#
# This source code is licensed under the Apache-2.0 license found in
# the LICENSE file in the root directory of this source tree.

from knockoff.utilities.mixin import ResourceLocatorMixin


class SinkDumpStrategyFactory(ResourceLocatorMixin, object):
    entry_point_group = "knockoff.factory.sink.dump_strategy"


class KnockoffSink:
    def __init__(self, config):
        self.config = config
        self.dump_strategy = (SinkDumpStrategyFactory()
                              .get_resource(config.get('strategy', 'noop')))

    def dump(self, table, df):
        return self.dump_strategy(self, table, df)
