# Copyright 2021-present, Nike, Inc.
# All rights reserved.
#
# This source code is licensed under the Apache-2.0 license found in
# the LICENSE file in the root directory of this source tree.


from mock import MagicMock, patch

from knockoff.cli_v2 import main


class TestKnockoffCLI:

    def test_version(self):
        mock_version = MagicMock()
        with patch("knockoff.command.version.main", mock_version):
            some_other_commands = ['--flag', '--input', 'value']
            main(["knockoff", "version"]+some_other_commands)
            mock_version.assert_called_once_with(some_other_commands)
