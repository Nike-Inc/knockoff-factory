# Changelog

All notable changes to this project will be documented in this file.
`knockoff-factory` adheres to [Semantic Versioning](http://semver.org/).

#### 4.x Releases
- `4.1.x` Releases - [4.1.0](#410)
- `4.0.x` Releases - [4.0.0](#400)

#### 3.x Releases
- `3.1.x` Releases - [3.1.1](#311) | [3.1.0](#310)
- `3.0.x` Releases - [3.0.0](#300)

#### 2.x Releases
- `2.1.x` Releases - [2.1.0](#210)
- `2.0.x` Releases - [2.0.0](#2.0.0)

#### 1.x Releases
- `1.9.x` Releases - [1.9.0](#190)
- `1.8.x` Releases - [1.8.1](#181) | [1.8.0](#180)
- `1.7.x` Releases - [1.7.0](#170)
- `1.6.x` Releases - [1.6.0](#160)
- `1.5.x` Releases - [1.5.1](#151) | [1.5.0](#150)
- `1.4.x` Releases - [1.4.0](#140)
- `1.3.x` Releases - [1.3.0](#130)
- `1.2.x` Releases - [1.2.0](#120)
- `1.1.x` Releases - [1.1.0](#110)

---
## Unreleased

#### Added

#### Updated

#### Deprecated

#### Removed

#### Fixed
---

## 4.1.0

#### Added
- CollectionsFactory for providing factory functions that return multiple columns 
    - Added by [Gregory Yu](https://github.com/gregyu) in Pull Request [#2](https://github.com/Nike-Inc/knockoff-factory/pull/2)
- Documentation and jupyter notebook for KnockoffTable
    - Added by [Gregory Yu](https://github.com/gregyu) in Pull Request [#2](https://github.com/Nike-Inc/knockoff-factory/pull/2)

#### Updated
    
#### Fixed

---

## 4.0.0

#### Added
- ColumnFactory for providing factory functions instead of requiring as a tuple (column, factory) 
    - Added by [Gregory Yu](https://github.com/gregyu) in Pull Request [#1](https://github.com/Nike-Inc/knockoff-factory/pull/1)
- `build` method for KnockoffDB to enable building dataframes without inserting into DB
    - Added by [Gregory Yu](https://github.com/gregyu) in Pull Request [#1](https://github.com/Nike-Inc/knockoff-factory/pull/1)
- Unit tests for column and collection factories
    - Added by [Gregory Yu](https://github.com/gregyu) in Pull Request [#1](https://github.com/Nike-Inc/knockoff-factory/pull/1)
- `run` CLI command for loading data into database from sdk configuration 
    - Added by [Gregory Yu](https://github.com/gregyu) in Pull Request [#1](https://github.com/Nike-Inc/knockoff-factory/pull/1)
- Add Blueprint class to sdk for more composable configuration 
    - Added by [Gregory Yu](https://github.com/gregyu) in Pull Request [#1](https://github.com/Nike-Inc/knockoff-factory/pull/1)    
- Added unit tests for knockoff.utilities.mixin
    - Added by [Gregory Yu](https://github.com/gregyu) in Pull Request [#1](https://github.com/Nike-Inc/knockoff-factory/pull/1)
- Added tempdb module and TempDatabaseService class
    - Added by [Gregory Yu](https://github.com/gregyu) in Pull Request [#1](https://github.com/Nike-Inc/knockoff-factory/pull/1)


#### Updated
- Made CLI extensible with injectable subcommands 
    - Updated by [Gregory Yu](https://github.com/gregyu) in Pull Request [#1](https://github.com/Nike-Inc/knockoff-factory/pull/1)
- Moved previous CLI to `legacy` subcommand for loading data into database using yaml configuration
    - Updated by [Gregory Yu](https://github.com/gregyu) in Pull Request [#1](https://github.com/Nike-Inc/knockoff-factory/pull/1)
- Renamed knockoff.utilities.mixin:FactoryMixin to knockoff.utilities.mixin:ResourceLocatorMixin
    - Updated by [Gregory Yu](https://github.com/gregyu) in Pull Request [#1](https://github.com/Nike-Inc/knockoff-factory/pull/1)
- Remove dependency on python-interface, use abc instead
    - Updated by [Gregory Yu](https://github.com/gregyu) in Pull Request [#1](https://github.com/Nike-Inc/knockoff-factory/pull/1)
- Updated internal knockoff fixtures to use TempDatabaseService
    - Updated by [Gregory Yu](https://github.com/gregyu) in Pull Request [#1](https://github.com/Nike-Inc/knockoff-factory/pull/1)

    
#### Fixed
- Fixed legacy CLI command by resolving breaking changes in sqlalchemy engine interface
    - Fixed by [Gregory Yu](https://github.com/gregyu) in Pull Request [#1](https://github.com/Nike-Inc/knockoff-factory/pull/1)
    
---

## 3.1.1

#### Updated
- Update version of package to release to public pypi
    - Updated by [Mohamed Abdul Huq Ismail](https://github.com/abdulhuq811)

---

## 3.1.0

#### Added
- Utilities for date intervals, sql engine builder and regex
    - Added by [Mohamed Abdul Huq Ismail](https://github.com/aisma7_nike)

---

## 3.0.0

#### Deprecated
- Python2 Support
    - Deprecated by [Mohamed Abdul Huq Ismail](https://github.com/aisma7_nike)

#### Fixed
- Test failures due to faker v8.1
    - Fixed by [Mohamed Abdul Huq Ismail](https://github.com/aisma7_nike)
    
---

## 2.1.0

#### Added
- dag_service and dependency handling for KnockoffDB
    - Added by [Gregory Yu](https://github.com/gyu7_nike)
    
---

## 2.0.0

#### Updated
- SDK interface to simplify configuration
    - Updated by [Gregory Yu](https://github.com/gyu7_nike)
    
---

## 1.9.0

#### Added
- Python sdk for simple table configuration and pytest fixture setup
    - Added by [Gregory Yu](https://github.com/gyu7_nike)
- knockoff.testing_postgresql for unit testing postgres
    - Added by [Gregory Yu](https://github.com/gyu7_nike)
    
#### Fixed
- Default engine builder setting host instead of uri
    - Fixed by [Gregory Yu](https://github.com/gyu7_nike)
    
---

## 1.8.1

#### Added
- `--version` flag to cli
    - Added by [Gregory Yu](https://github.com/gyu7_nike)

#### Fixed
- Python3 compatibility
    - Fixed by [Gregory Yu](https://github.com/gyu7_nike)
    
---

## 1.8.0

#### Added
- Prototype io to read sql query that returns query result as pandas dataframe
    - Added by [Gregory Yu](https://github.com/gyu7_nike)
    
---

## 1.7.0

#### Added
- Functionality to generate periods part using Intervals
    - Added by [Gregory Yu](https://github.com/gyu7_nike)
    
---

## 1.6.0

#### Added
- Utilities to clear default knockoff environment variables
    - Added by [Gregory Yu](https://github.com/gyu7_nike)
- Allow registering databases configured by engine builders in the yaml
    - Added by [Gregory Yu](https://github.com/gyu7_nike)

---    

## 1.5.1

#### Fixed
- Adding unique constraint on prototypes
    - Fixed by [Gregory Yu](https://github.com/gyu7_nike)
    
---

## 1.5.0

#### Added
- Knockoff class for interface with library instead of cli
    - Added by [Gregory Yu](https://github.com/gyu7_nike)
    
---

## 1.4.0

#### Added
- Enabled loading prototypes using io strategy
    - Added by [Gregory Yu](https://github.com/gyu7_nike)
    
#### Fixed
- Only attempt to create databases and users if provided in config
    - Fixed by [Gregory Yu](https://github.com/gyu7_nike)
    
---

## 1.3.0

#### Added
- Parallelize writes for sql sink
    - Added by [Gregory Yu](https://github.com/gyu7_nike)
- read_multi_parquet to read multiple parquet files
    - Added by [Gregory Yu](https://github.com/gyu7_nike)
    
---

## 1.2.0

#### Updated
- Use psycopg2 instead of psycopg2-binary
    - Updated by [Gregory Yu](https://github.com/gyu7_nike)
    
---

## 1.1.0

#### Added
- Added injectable dump strategy for tables. 
  - Currently supporting
    - sql: pandas dataframe to_sql
    - parquet: pandas dataframe to_parquet
  - Added by [Gregory Yu](https://github.com/gyu7_nike)
    
---
