Knockoff Factory
---
[![codecov](https://codecov.io/gh/Nike-Inc/knockoff-factory/branch/master/graph/badge.svg?token=93wOmtZxIk)](https://codecov.io/gh/Nike-Inc/knockoff-factory)
[![Test](https://github.com/Nike-Inc/knockoff-factory/actions/workflows/python-test.yaml/badge.svg)](https://github.com/Nike-Inc/knockoff-factory/actions/workflows/python-test.yaml) 
[![PyPi Release](https://github.com/Nike-Inc/knockoff-factory/actions/workflows/python-build.yaml/badge.svg)](https://github.com/Nike-Inc/knockoff-factory/actions/workflows/python-build.yaml) 
[![Docker Build](https://github.com/Nike-Inc/knockoff-factory/actions/workflows/docker-build.yaml/badge.svg)](https://github.com/Nike-Inc/knockoff-factory/actions/workflows/docker-build.yaml)

A library for generating fake data and populating database tables.

# Run poetry install/update with psycopg2

Requirements:
* postgresql (`brew install postrgresql`)

Run the following command:
```shell script
pg_config | grep "LDFLAGS ="
```
Output:
> LDFLAGS = -L/usr/local/opt/openssl@1.1/lib -L/usr/local/opt/readline/lib -Wl,-dead_strip_dylibs

Take the value of `LDFLAGS` and set that environment variable. E.g.:
```shell script
export LDFLAGS="-L/usr/local/opt/openssl@1.1/lib -L/usr/local/opt/readline/lib -Wl,-dead_strip_dylibs"
``` 
You should now be able to run poetry install and/or update commands without failing on psycopg2.


### Local Postgres Setup
The following steps can be used to setup a local postgres instance for testing.

#### Requirements
* docker
* poetry (`curl -sSL https://raw.githubusercontent.com/python-poetry/poetry/master/get-poetry.py | python`)
* postgresql (`brew install postgresql`) or pgcli (`brew install pgcli`) 
  
#### Run Postgres
1. Pull docker image `docker pull postgres:11.7`
2. Run docker container: `docker run --rm  --name pg-docker -e POSTGRES_PASSWORD=docker -d -p 5432:5432  postgres:11.7` 
    * Note: you can see the running container with `docker ps` and can terminate it with `docker kill pg-docker`

You can now access the shell with `PGPASSWORD=docker pgcli -h localhost -U postgres` or
`PGPASSWORD=docker psql -h localhost -U postgres`.
    

## Tests
Run unit tests
```bash
poetry run pytest
```

The unit tests depend on fixtures using ephemeral postgres databases
and/or instances. By default it will attempt to connect to an existing
instance at `postgresql://postgres@localhost:5432/postgres` and will
create and destroy databases per fixture. This postgres location can
be overridden with the `KNOCKOFF_TEST_DB_URI` environment variable.

If no external postgres instance is available for testing, but postgresql is
installed, the `TEST_USE_EXTERNAL_DB` environment variable can be set to `0`.
The fixtures will then rely on the `testing.postgresql` library to create
ephemeral postgres instances per fixture.

If postgres is not available, dependent tests can be disabled with the
following environment variable
```bash
export TEST_POSTGRES_ENABLED=0
```


### Knockoff Configuration


#### Creating Databases
Knockoff will start by creating any specified databases. This section
is optional if you do not need a database created. You can also configure
an engine builder to use by providing the `config` parameter for each
configured database (factory function used is knockoff.utilities.orm.sql.EngineBuilder.from_config)
otherwise the default engine based on knockoff environment variables will be used.
The following yaml will result in the following sql queries:
* `create database mydb;`
* `create user myuser with encrypted password 'MYUSER_PASSWORD';`
    * `MYUSER_PASSWORD` is replaced with the value of the corresponding environment variable
* `grant all privileges on database mydb to myuser;`
```yaml
create-databases:
  - name: mydb
    type: postgres
    users:
      - user: myuser
        password_env: MYUSER_PASSWORD
```

#### Load existing table definitions
Knockoff uses [Pyrseas](https://github.com/perseas/Pyrseas)'s yamltodb tool to load existing table
definitions into a database.

##### Example:
In this example there is a table `films` with the following definition:
```commandline
+----------+-------------------+-------------+
| Column   | Type              | Modifiers   |
|----------+-------------------+-------------|
| title    | character varying |  not null   |
| director | character varying |             |
| year     | character varying |             |
+----------+-------------------+-------------+
Indexes:
    "films_pkey" PRIMARY KEY, btree (title)
```
Executing `dbtoyaml mydb` results in the following yaml that knockoff
can be configured to use to load with `yamltodb`. 
```yaml
schema public:
  description: standard public schema
  owner: postgres
  privileges:
  - PUBLIC:
    - all
  - postgres:
    - all
  table films:
    columns:
    - title:
        not_null: true
        type: character varying
    - director:
        type: character varying
    - year:
        type: character varying
    owner: myuser
    primary_key:
      films_pkey:
        columns:
        - title
```
Note: If you are running the local postgres setup described above and running from within a docker container on your mac, you can use the following: `PGPASSWORD=docker dbtoyaml -H docker.for.mac.host.internal -U postgres mydb`

#### Loading data into tables
Data can be loaded into new or existing tables.

##### Examples
The following example loads data into an existing table from a provided csv.
```yaml
knockoff:
  dag:
    - name: films # arbitrary name of node in dag
      type: table # table | prototype | component | part
      table: films # defaults to the name of the node if not provided 
      source:
        strategy: io
        reader: pandas.read_csv
        kwargs:
          filepath_or_buffer: example/films.csv # local or s3:// path
          sep: "|"
      sink:
        database: mydb
        kwargs:
          if_exists: append # defaults to fail
          index: false # Data is loaded into a pandas DataFrame this option ignores the index
```

The following example loads data into a new table from data defined in the yaml.
```yaml
knockoff:
  dag:
    - name: films2 # Note: "table" key not specified, so defaults to "film2"
      type: table
      source:
        strategy: io
        reader: inline
        kwargs:
          sep: ","
          data: |
            title,director,year
            t5,d1,2020
            t6,d2,2020
            t7,d1,2020
      sink:
        database: mydb
        user: myuser
        password_env: MYUSER_PASSWORD
        kwargs:
          index: false
```

#### Generating fake retail data
Knockoff uses [faker](https://github.com/joke2k/faker) to help generate fake retail data that can be used for testing.
Hierarchical relationships with various dependencies can be also be modelled with knockoff. This [example](examples/knockoff.yaml)
generates the following tables (in addition to the above examples).
```shell script
postgres@localhost:mydb> select * from location;
+-------------------------------+---------------+-----------+
| address                       | location_id   | channel   |
|-------------------------------+---------------+-----------|
| 07528 Fischer Track Suite 779 | 1             | nfs       |
| Melissaview, MD 90363         |               |           |
| 1535 Kelly Canyon             | 2             | nso       |
| Rhodesborough, CA 43893       |               |           |
| 216 Kayla Lake Apt. 126       | 3             | nso       |
| South Matthewmouth, OH 36332  |               |           |
| 561 Jones Burg Suite 382      | 4             | nso       |
| Hugheschester, DE 21908       |               |           |
| 042 Robinson Fort Suite 945   | 5             | nfs       |
| Pattersonshire, NC 96317      |               |           |
| 2332 Watkins Road             | 0             | digital   |
| Davidfort, MS 71411           |               |           |
+-------------------------------+---------------+-----------+

postgres@localhost:mydb> select * from product;
+------------+----------+-----------------------+---------------+------------+
| division   | gender   | category              | color         | sku        |
|------------+----------+-----------------------+---------------+------------|
| apparel    | men      | shorts                | PaleGoldenRod | 6357812379 |
| apparel    | women    | pants & tights        | NavajoWhite   | 8332320303 |
| apparel    | men      | tops & t-shirts       | Lavender      | 9243289077 |
| shoes      | men      | lifestyle             | PaleGoldenRod | 7270972977 |
| apparel    | women    | pants & tights        | PaleGoldenRod | 4443641793 |
| apparel    | women    | hoodies & sweatshirts | NavajoWhite   | 6130018459 |
| shoes      | women    | jordan                | Lavender      | 3791231041 |
| apparel    | men      | pants & tights        | PaleGoldenRod | 3899370297 |
| apparel    | men      | shorts                | Lavender      | 7557742055 |
| apparel    | men      | pants & tights        | SkyBlue       | 9785957221 |
| apparel    | women    | shorts                | SkyBlue       | 9979359561 |
| apparel    | women    | tops & t-shirts       | Lavender      | 7006056836 |
| shoes      | women    | jordan                | Lavender      | 4853474331 |
| shoes      | women    | jordan                | NavajoWhite   | 6589395336 |
| apparel    | men      | pants & tights        | Beige         | 7168664719 |
| apparel    | men      | hoodies & sweatshirts | Beige         | 7525844204 |
| apparel    | men      | shorts                | SkyBlue       | 9735336861 |
| shoes      | men      | skateboarding         | SkyBlue       | 6385212885 |
| apparel    | men      | tops & t-shirts       | Beige         | 9735107927 |
| apparel    | women    | pants & tights        | SkyBlue       | 2633853831 |
| apparel    | women    | jackets & vests       | NavajoWhite   | 2758275877 |
| apparel    | men      | shorts                | Lavender      | 1330756304 |
| apparel    | women    | tops & t-shirts       | NavajoWhite   | 9334676293 |
| shoes      | men      | skateboarding         | Lavender      | 6735393792 |
| apparel    | men      | jackets & vests       | Lavender      | 2907811814 |
+------------+----------+-----------------------+---------------+------------+

postgres@localhost:mydb> select * from transactions limit 10;
+---------------+------------+-----------+------------+------------+------------+
| location_id   | sku        | line_id   | order_id   | quantity   | date       |
|---------------+------------+-----------+------------+------------+------------|
| 5             | 7557742055 | 2         | 2957859949 | 0          | 2018-05-06 |
| 1             | 1330756304 | 1         | 3920316859 | 0          | 2018-07-19 |
| 4             | 9243289077 | 3         | 1875617688 | 0          | 2019-10-14 |
| 3             | 9334676293 | 2         | 7317451987 | 0          | 2018-06-09 |
| 0             | 9979359561 | 3         | 1236640244 | 2          | 2019-07-17 |
| 0             | 9735107927 | 1         | 9030486883 | 3          | 2018-04-27 |
| 1             | 9735336861 | 2         | 6196902209 | 2          | 2020-01-21 |
| 3             | 7006056836 | 4         | 1432537227 | 0          | 2019-04-22 |
| 2             | 2907811814 | 1         | 4039132536 | 0          | 2019-09-23 |
| 0             | 4443641793 | 5         | 8648324533 | 2          | 2018-09-06 |
+---------------+------------+-----------+------------+------------+------------+
```

#### Run the example:

1. Run postgres: `docker run --rm  --name pg-docker -e POSTGRES_PASSWORD=docker -d -p 5432:5432  postgres:11.4`
    * Terminate existing container with `docker kill pg-docker`
    * Note: The example assumes you're running with *POSTGRES_PASSWORD=docker* and on port *5432*
2. Checkout the repo or download the examples folder
3. Pull knockoff docker image: `docker pull knockoff-factory`
```commandline
docker run --rm -v $PWD/examples:/examples \
-e KNOCKOFF_DB_HOST='docker.for.mac.host.internal' \
-e KNOCKOFF_DB_USER='postgres' \
-e KNOCKOFF_DB_PASSWORD='docker' \
-e KNOCKOFF_DB_NAME='knockoff' \
-e KNOCKOFF_CONFIG=/examples/knockoff.yaml nikelab222/knockoff-factory:latest knockoff
```
Note: if you are loading data from an s3 bucket you have access to, you can enable your docker
container access to those credentials by adding `-v ~/.aws:/root/.aws` to the `docker run` command.


### Future work
* Add documentation for SDK
* Autodiscover and populate all tables by using reflection and building dependency graph with foreign key relationships
* Update CLI and yaml configuration to use SDK
* Documentation / use-cases
* Parallelize execution of dag. (e.g. https://ipython.org/ipython-doc/stable/parallel/dag_dependencies.html)
