# Copyright 2021-present, Nike, Inc.
# All rights reserved.
#
# This source code is licensed under the Apache-2.0 license found in
# the LICENSE file in the root directory of this source tree.


from dependency_injector import containers, providers

from knockoff.utilities.importlib_utils import resolve_package_name
from knockoff.tempdb.db import TempDatabaseService
from knockoff.tempdb.initialize_tables import SqlAlchemyInitTablesFunc


class TempDBContainer(containers.DeclarativeContainer):
    config = providers.Configuration()

    setup_teardown = providers.Factory(
        resolve_package_name,
        config.tempdb.setup_teardown.package
    )

    base = providers.Factory(
        resolve_package_name,
        config.tempdb.initialize_tables.base.package
    )

    initialize_tables = providers.Factory(
        SqlAlchemyInitTablesFunc,
        base
    )

    temp_db = providers.Factory(
        TempDatabaseService,
        url=config.tempdb.url,
        setup_teardown=setup_teardown,
        initialize_tables=initialize_tables,
    )
