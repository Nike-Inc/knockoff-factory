Knockoff Factory
---
[![codecov](https://codecov.io/gh/Nike-Inc/knockoff-factory/branch/master/graph/badge.svg?token=93wOmtZxIk)](https://codecov.io/gh/Nike-Inc/knockoff-factory)
[![Test](https://github.com/Nike-Inc/knockoff-factory/actions/workflows/python-test.yaml/badge.svg)](https://github.com/Nike-Inc/knockoff-factory/actions/workflows/python-test.yaml) 
[![PyPi Release](https://github.com/Nike-Inc/knockoff-factory/actions/workflows/python-build.yaml/badge.svg)](https://github.com/Nike-Inc/knockoff-factory/actions/workflows/python-build.yaml) 
[![Docker Build](https://github.com/Nike-Inc/knockoff-factory/actions/workflows/docker-build.yaml/badge.svg)](https://github.com/Nike-Inc/knockoff-factory/actions/workflows/docker-build.yaml)
![License](https://img.shields.io/pypi/l/knockoff)
![Python Versions](https://img.shields.io/pypi/pyversions/knockoff)
![Docker Image Size](https://img.shields.io/docker/image-size/nikelab222/knockoff-factory/latest)
![Python Wheel](https://img.shields.io/pypi/wheel/knockoff)

A library for generating mock data and creating database fixtures that can be used for unit testing.

Table of content
* [Installation](#installation)
* [Changelog](#changelog)
* [Documentation](#documentation)
* [Unit Tests](#unit-tests)
* [Future Work](#Future-work)
* [Legacy YAML Based CLI](legacy.md)

# <a name="installation"></a> Installation
From PyPi:
```shell script
pip install knockoff

# to install with PyMySQL 
pip install knockoff[mysql]
# Note: Other MySql DBAPI's can be used if installed and dialect provided in connection url
```

From GitHub:
```shell script
pip install git+https://github.com/Nike-Inc/knockoff-factory#egg=knockoff

# to install with PyMySQL 
pip install git+https://github.com/Nike-Inc/knockoff-factory#egg=knockoff[mysql]
# Note: Other MySql DBAPI's can be used if installed and dialect provided in connection url
```


# <a name="changelog"></a> Changelog

See the [changelog](CHANGELOG.md) for a history of notable changes to knockoff.

# <a name="documentation"></a> Documentation

We are working on adding more documentation and examples!  

* Knockoff SDK
    * [KnockoffTable](notebook/KnockoffTable.ipynb)
    * [KnockoffDB](notebook/KnockoffDB.ipynb)
* [TempDatabaseService](notebook/TempDatabaseService.ipynb)
* [Knockoff CLI](notebook/KnockoffCLI.ipynb)
* Unit Testing Example: Sample App


# <a name="unit-tests"></a> Unit Tests

### Prerequisites
* docker
* poetry (`curl -sSL https://raw.githubusercontent.com/python-poetry/poetry/master/get-poetry.py | python`) 

Some of the unit tests depend on a database instance. Knockoff will create ephemeral databases within that instance and clean
them up when tests have completed. By default it will attempt to connect to an existing
instance at `postgresql://postgres@localhost:5432/postgres` and will
create and destroy databases per test. This postgres location can
be overridden with the `KNOCKOFF_TEST_DB_URI` environment variable.

If no external postgres instance is available for testing, but postgresql is
installed, the `TEST_USE_EXTERNAL_DB` environment variable can be set to `0`.
The fixtures will then rely on the `testing.postgresql` library to create
ephemeral postgres instances per fixture.

If postgres is not available, dependent tests can be disabled with the
following: `export TEST_POSTGRES_ENABLED=0`.

Some tests also depend on a MySql database instance. These tests can be 
disabled with the following: `export TEST_MYSQL_ENABLED=0`.

Create the database instance using docker:
```bash
# Run postgres instance 
docker run --rm  --name pg-docker -e POSTGRES_HOST_AUTH_METHOD=trust -d -p 5432:5432  postgres:11.9

# Run mysql instance
docker run --name mysql-docker -e MYSQL_ALLOW_EMPTY_PASSWORD=yes -p 3306:3306 -d mysql:8.0.26
```

Install poetry:
```bash
# the -E flag is so we can run the mysql unit tests with the PyMySql DBAPI
poetry install -E mysql
```

Run unit test:
```bash
poetry run pytest
```

# <a name="future-work"></a> Future work
* Further documentation and examples for SDK
* Add yaml based configuration for SDK
* Make extensible generic output for KnockffDB.insert (csv, parquet, etc)
* Enable append option for KnockoffDB.insert
* Autodiscover and populate all tables by using reflection and building dependency graph with foreign key relationships
* Parallelize execution of dag. (e.g. https://ipython.org/ipython-doc/stable/parallel/dag_dependencies.html)
