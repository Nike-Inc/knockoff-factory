# Copyright 2021-present, Nike, Inc.
# All rights reserved.
#
# This source code is licensed under the Apache-2.0 license found in
# the LICENSE file in the root directory of this source tree.

from dependency_injector import containers, providers
from sqlalchemy import create_engine
from sqlalchemy.pool import NullPool

from knockoff.sdk.db import KnockoffDB, DefaultDatabaseService
from knockoff.sdk.blueprint import Blueprint


class KnockoffContainer(containers.DeclarativeContainer):
    config = providers.Configuration()

    engine = providers.Factory(
        create_engine,
        config.database_service.url,
        poolclass=NullPool
    )

    database_service = providers.Singleton(
        DefaultDatabaseService,
        engine=engine
    )

    knockoff_db = providers.Singleton(
        KnockoffDB,
        database_service=database_service
    )

    blueprint = providers.Factory(
        Blueprint.from_plan_package_name,
        config.blueprint.plan.package)
