# Copyright 2021-present, Nike, Inc.
# All rights reserved.
#
# This source code is licensed under the Apache-2.0 license found in
# the LICENSE file in the root directory of this source tree.


import unittest
import os
from knockoff.utilities.environ import EnvironmentVariable


class TestEnviron(unittest.TestCase):

    def setUp(self):
        self.var1 = "TEST_VAR1"
        self.val1 = "var1"
        os.environ[self.var1] = self.val1

        self.var2 = "TEST_VAR2"
        self.var3 = "TEST_VAR3"

    def tearDown(self):
        for variable in [self.var1, self.var2]:
            try:
                del os.environ[variable]
            except KeyError:
                pass

    def test_environ_existing(self):
        env_var = EnvironmentVariable(self.var1)
        self.assertEqual(self.val1, env_var.get())

        env_var.set("new_val")
        self.assertEqual("new_val", env_var.get())

    def test_environ_new(self):
        env_var = EnvironmentVariable(self.var2,
                                      default_value="default2",
                                      allow_default_value=True)
        self.assertEqual("default2", env_var.get())

        env_var.set("new_val")
        self.assertEqual("new_val", env_var.get())

        env_var = EnvironmentVariable(self.var3,
                                      default_value=None,
                                      allow_default_value=True)
        self.assertEqual(None, env_var.get())

    def test_environ_exception(self):
        env_var = EnvironmentVariable(self.var2,
                                      allow_default_value=False)
        with self.assertRaises(KeyError):
            env_var.get()


if __name__ == "__main__":
    unittest.main()
