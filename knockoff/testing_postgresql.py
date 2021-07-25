# Copyright 2021-present, Nike, Inc.
# All rights reserved.
#
# This source code is licensed under the Apache-2.0 license found in
# the LICENSE file in the root directory of this source tree.


import logging

logger = logging.getLogger(__name__)

logger.warning("knockoff.testing_postgresql will be deprecated "
               "in future releases of knockoff. Use imports from "
               "knockoff.utilities.testing.postgresql instead")
# Imports for backwards compatibility
from .utilities.testing.base import TRUTH_VALUES, TEST_USE_EXTERNAL_DB
from .utilities.testing.postgresql import TEST_POSTGRES_ENABLED
from .utilities.testing.postgresql import get_postgresql
