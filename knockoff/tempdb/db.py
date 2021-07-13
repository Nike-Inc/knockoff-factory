# Copyright 2021-present, Nike, Inc.
# All rights reserved.
#
# This source code is licensed under the Apache-2.0 license found in
# the LICENSE file in the root directory of this source tree.

from .setup_teardown import postgres_setup_teardown


class TempDatabaseService(object):
    def __init__(self,
                 url,
                 setup_teardown=postgres_setup_teardown,
                 initialize_tables=None):
        self.url = url
        self.setup_teardown = setup_teardown
        self.initialize_tables = initialize_tables
        self.temp_url = None
        self._setup_teardown_generator = None

    def start(self):
        if self._setup_teardown_generator is not None:
            raise ValueError(f"Invalid state reached on start()."
                             f"Possible causes: \n1) start() has "
                             f"already been called. \n2) Bad "
                             f"generator function returned by"
                             f" {self.setup_teardown}")
        self._setup_teardown_generator = self.setup_teardown(self.url)
        try:
            self.temp_url = next(self._setup_teardown_generator)
        except StopIteration:
            raise ValueError(f"Invalid state reached on start()."
                             f"Possible causes: \n1) Bad "
                             f"generator function returned by"
                             f" {self.setup_teardown}")
        except TypeError:
            raise ValueError(f"{self.setup_teardown} did not return a generator")

        if self.initialize_tables:
            self.initialize_tables(self.temp_url)
        return self.temp_url

    def stop(self):
        if self._setup_teardown_generator is None:
            raise ValueError(f"Invalid state reached on stop()."
                             f"Possible causes: \n1) start() was not called."
                             f"\n2) stop() was already called.")
        try:
            next(self._setup_teardown_generator)
        except StopIteration:
            return
        raise ValueError(f"Invalid state reached on stop()."
                         f"Possible causes: \n1) Bad "
                         f"generator function returned by"
                         f" {self.setup_teardown}")

    def reset(self):
        self.temp_url = None
        self._setup_teardown_generator = None
