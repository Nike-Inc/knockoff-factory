# Copyright 2021-present, Nike, Inc.
# All rights reserved.
#
# This source code is licensed under the Apache-2.0 license found in
# the LICENSE file in the root directory of this source tree.

from sqlalchemy import create_engine
from sqlalchemy import Table, MetaData

from ..environ import EnvironmentVariable


def get_table(name, engine=None, meta=None):
    engine = engine or get_engine()
    with engine.connect() as conn:
        meta = meta or MetaData()
        return Table(name, meta, autoload=True, autoload_with=conn)


def execute(sql, engine=None):
    engine = engine or get_engine()
    with engine.connect() as conn:
        conn.execute("commit")
        conn.execute(sql)


def get_engine(uri=None, **kwargs):
    uri = uri or get_uri()
    return create_engine(uri, **kwargs)


def get_uri(user="postgres",
            database="",
            password="password",
            host="localhost",
            port=5432,
            dialect="postgresql",
            driver=None):
    driver = '+{}'.format(driver) if driver else ''
    uri = ('{dialect}{driver}://{user}:'
           '{password}@{host}:{port}/{database}'
           ).format(dialect=dialect,
                    driver=driver,
                    user=user,
                    password=password,
                    host=host,
                    port=port,
                    database=database or '')
    return uri


class EngineBuilder(object):
    def __init__(self):
        """
        Builder for building sqlalchemy engine (or uri).

        Each component of the uri can be set with either a
        value or an environment variable. Environment variables
        will default to value passed in default parameter if
        allow_default is True. Otherwise, it will fail if
        with a KeyError if environment variable is not set.

        Components can be set multiple times, where each the
        previous set values are overridden.

        If a uri value is passed, all other components will be
        ignored. If uri environment variable is set with
        allow_default=True and default=None, uri will be used if the
        environment variable is set, otherwise it will fall back to
        the other components.

        """
        self.engine_kwargs = {}
        self.env_vars = {}

    @staticmethod
    def _assert_xor(name, value, env_var):
        assert (value is None) ^ (env_var is None), \
            ("{} must be set with either value or env (environment "
             "variable). default will be used if env_var is set "
             "and allow_default is True".format(name))

    def _remove_if_exists(self, name):
        try:
            del self.engine_kwargs[name]
        except KeyError:
            pass
        try:
            del self.env_vars[name]
        except KeyError:
            pass

    def _add_var(self, name, value, env_var,
                 default, allow_default):
        self._assert_xor(name, value, env_var)
        self._remove_if_exists(name)
        if value:
            self.engine_kwargs[name] = value
        else:
            self.env_vars[name] = \
                EnvironmentVariable(env_var,
                                    default_value=default,
                                    allow_default_value=allow_default)

    def user(self, value=None, env_var=None,
             default="postgres", allow_default=True):
        self._add_var("user", value, env_var, default, allow_default)
        return self

    def database(self, value=None, env_var=None,
                 default="", allow_default=True):
        self._add_var("database", value, env_var, default, allow_default)
        return self

    def password(self, value=None, env_var=None,
                 default="password", allow_default=True):
        self._add_var("password", value, env_var, default, allow_default)
        return self

    def host(self, value=None, env_var=None,
             default="localhost", allow_default=True):
        self._add_var("host", value, env_var, default, allow_default)
        return self

    def port(self, value=None, env_var=None,
             default=5432, allow_default=True):
        self._add_var("port", value, env_var, default, allow_default)
        return self

    def dialect(self, value=None, env_var=None,
                default="postgresql", allow_default=True):
        self._add_var("dialect", value, env_var, default, allow_default)
        return self

    def driver(self, value=None, env_var=None,
               default=None, allow_default=True):
        self._add_var("driver", value, env_var, default, allow_default)
        return self

    def uri(self, value=None, env_var=None,
            default=None, allow_default=True):
        self._add_var("uri", value, env_var, default, allow_default)
        return self

    def build(self, uri_only=False, **kwargs):
        engine_kwargs = self.engine_kwargs.copy()

        for name, variable in self.env_vars.items():
            engine_kwargs[name] = variable.get()

        try:
            uri = engine_kwargs.pop("uri")
        except KeyError:
            uri = None

        uri = uri or get_uri(**engine_kwargs)

        return uri if uri_only else get_engine(uri, **kwargs)

    @staticmethod
    def from_config(config, build='engine', **kwargs):
        """

        :param config: list
            list of dict

            e.g.

            config = [
                {
                    "property": host | port | database | user | password | dialect | driver | uri,
                    "value" : <value to set>,
                    "env_var": <environment variable to get value from>,
                    "default": <default value to use if env var isn't set>,
                    "allow_default": bool
                }
            ]

        :param build: str
            'engine', 'uri', 'builder'
        :return:
        """
        assert build in {'engine', 'uri', 'builder'}
        builder = EngineBuilder()
        for item in config:
            item = item.copy()
            name = item.pop("property")
            assert name in {"host", "port", "database",
                            "user", "password", "dialect",
                            "driver", "uri"}, \
                "property={} is not recognized".format(name)
            builder = getattr(builder, name)(**item)
        if build == "builder":
            return builder
        if build == "uri":
            return builder.build(uri_only=True)
        return builder.build(**kwargs)
