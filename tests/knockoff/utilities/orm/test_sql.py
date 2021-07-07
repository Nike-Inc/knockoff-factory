# Copyright 2021-present, Nike, Inc.
# All rights reserved.
#
# This source code is licensed under the Apache-2.0 license found in
# the LICENSE file in the root directory of this source tree.


import pytest
import mock
import os

from sqlalchemy.pool import NullPool

from knockoff.utilities.orm import sql as sql_utils


@pytest.fixture
def env():
    # setup
    obj = type('testclass', (object,), {
        'builder1': (
            sql_utils
            .EngineBuilder()
            .host("localhost")
            .port(5432)
            .user("someuser")
            .password("somepass")
            .database("somedb")
        ),
        'uri1': "postgresql://someuser:somepass@localhost:5432/somedb",
        'uri2': "postgresql://someuser2:somepass2@anotherhost:5433/somedb2",

        'host_var': "TEST_HOST",
        'user_var': "TEST_USER",
        'password_var': "TEST_PASSWORD",
        'db_var': "TEST_DATABASE",
        'uri_var': "TEST_URI",
    })

    yield obj

    # tear down
    for variable in [obj.host_var, obj.user_var,
                     obj.password_var, obj.db_var,
                     obj.uri_var]:
        try:
            del os.environ[variable]
        except KeyError:
            pass


@pytest.fixture
def mock_create_engine():
    with mock.patch("knockoff"
                    ".utilities.orm.sql"
                    ".create_engine") as mock_create_engine:
        yield mock_create_engine


class TestSql(object):

    def test_set_parameter_multi(self, env):
        builder = (env.builder1
                   .user("usr1")
                   .port(5433)
                   .host(env_var=env.host_var))
        os.environ[env.host_var] = "host1"
        assert "postgresql://usr1:somepass@host1:5433/somedb" == \
            builder.build(uri_only=True)
        builder = (builder
                   .user(env_var=env.user_var)
                   .host("host2"))
        os.environ[env.user_var] = "usr2"
        assert "postgresql://usr2:somepass@host2:5433/somedb" == \
            builder.build(uri_only=True)

    def test_build_uri_from_values(self, env):
        uri = env.builder1.build(uri_only=True)
        assert env.uri1 == uri

    def test_build_uri_from_env_vars(self, env):
        builder = (
            sql_utils
            .EngineBuilder()
            .host(env_var=env.host_var, default="defaulthost")
            .user(env_var=env.user_var, default="defaultuser")
            .password(env_var=env.password_var, default="defaultpass")
            .database(env_var=env.db_var, default="defaultdb")
        )
        assert ("postgresql://defaultuser:defaultpass"
                "@defaulthost:5432/defaultdb") == \
            builder.build(uri_only=True)
        os.environ[env.host_var] = "anotherhost"
        os.environ[env.user_var] = "anotheruser"
        os.environ[env.password_var] = "anotherpass"
        os.environ[env.db_var] = "anotherdb"
        assert ("postgresql://anotheruser:anotherpass"
                "@anotherhost:5432/anotherdb") == \
            builder.build(uri_only=True)

    def test_uri_override(self, env):
        builder = env.builder1.uri(env_var=env.uri_var, default=None)
        assert env.uri1 == builder.build(uri_only=True)
        os.environ[env.uri_var] = env.uri2
        assert env.uri2 == builder.build(uri_only=True)

    def test_build_from_config(self, env, mock_create_engine):
        config = [
            {"property": "host", "value": "somehost"},
            {"property": "user", "value": "auser"},
            {"property": "password", "env_var": env.password_var,
             "allow_default": False},
            {"property": "database", "value": "db"}
        ]

        builder = (sql_utils
                   .EngineBuilder.from_config(config, build="builder"))
        assert isinstance(builder, sql_utils.EngineBuilder)
        with pytest.raises(KeyError):
            builder.build()

        with pytest.raises(KeyError):
            sql_utils.EngineBuilder.from_config(config, build="uri")

        os.environ[env.password_var] = "helloworld"

        uri_expected = "postgresql://auser:helloworld@somehost:5432/db"
        assert uri_expected == (sql_utils
                                .EngineBuilder
                                .from_config(config, build="uri"))

        mock_engine = mock.Mock()
        mock_create_engine.return_value = mock_engine

        engine = sql_utils.EngineBuilder.from_config(config)
        mock_create_engine.assert_called_once_with(uri_expected)
        assert mock_engine == engine

    def test_builder_exception(self, env):
        # only allow value or env_var to be passed
        with pytest.raises(AssertionError):
            sql_utils.EngineBuilder().user(value="user",
                                           env_var=env.user_var)

    def test_build_engine(self, env, mock_create_engine):
        mock_engine = mock.Mock()
        mock_create_engine.return_value = mock_engine
        engine = env.builder1.build()
        mock_create_engine.assert_called_once_with(env.uri1)
        assert mock_engine == engine

    def test_build_engine_kwargs(self, env, mock_create_engine):
        mock_engine = mock.Mock()
        mock_create_engine.return_value = mock_engine
        engine = env.builder1.build(poolclass=NullPool)
        mock_create_engine.assert_called_once_with(env.uri1,
                                                   poolclass=NullPool)
        assert mock_engine == engine

