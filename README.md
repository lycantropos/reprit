reprit
======

[![](https://travis-ci.org/lycantropos/reprit.svg?branch=master)](https://travis-ci.org/lycantropos/reprit "Travis CI")
[![](https://ci.appveyor.com/api/projects/status/github/lycantropos/reprit?branch=master&svg=true)](https://ci.appveyor.com/project/lycantropos/reprit "AppVeyor")
[![](https://codecov.io/gh/lycantropos/reprit/branch/master/graph/badge.svg)](https://codecov.io/gh/lycantropos/reprit "Codecov")
[![](https://img.shields.io/github/license/lycantropos/reprit.svg)](https://github.com/lycantropos/reprit/blob/master/LICENSE "License")
[![](https://badge.fury.io/py/reprit.svg)](https://badge.fury.io/py/reprit "PyPI")

In what follows
- `python` is an alias for `python3.5` or any later
version (`python3.6` and so on),
- `pypy` is an alias for `pypy3.5` or any later
version (`pypy3.6` and so on).

Installation
------------

Install the latest `pip` & `setuptools` packages versions:
- with `CPython`
  ```bash
  python -m pip install --upgrade pip setuptools
  ```
- with `PyPy`
  ```bash
  pypy -m pip install --upgrade pip setuptools
  ```

### User

Download and install the latest stable version from `PyPI` repository:
- with `CPython`
  ```bash
  python -m pip install --upgrade reprit
  ```
- with `PyPy`
  ```bash
  pypy -m pip install --upgrade reprit
  ```

### Developer

Download the latest version from `GitHub` repository
```bash
git clone https://github.com/lycantropos/reprit.git
cd reprit
```

Install:
- with `CPython`
  ```bash
  python setup.py install
  ```
- with `PyPy`
  ```bash
  pypy setup.py install
  ```

Usage
-----

Let's suppose we are defining a class and we want to have `__repr__`, that:

1. Includes parameters involved in instance creation. 
For simple cases it should be possible 
to copy string & paste in some place (e.g. REPL session) 
and have similar object definition with as less work as possible. 
This helps a lot during debugging sessions, logging, 
in failed test cases with randomly generated data, etc.
2. In case of signature change, 
method should handle this automatically for simple cases 
like renaming/removing/changing order of parameters.

This can be done like
```python
from reprit.base import generate_repr


class MyClass:
    def __init__(self, positional, *variadic_positional, keyword_only, **variadic_keyword):
        self.positional = positional
        self.variadic_positional = variadic_positional
        self.keyword_only = keyword_only
        self.variadic_keyword = variadic_keyword
    
    __repr__ = generate_repr(__init__)
```
after that
```python
>>> MyClass(range(10), 2, 3, keyword_only='some', a={'sample': 42}, b={1, 2})
MyClass(range(0, 10), 2, 3, keyword_only='some', a={'sample': 42}, b={1, 2})
```

*Note*: this method doesn't automatically handle changes during runtime 
(e.g. if someone deletes instance field 
or replaces `MyClass.__init__` method implementation), 
in this case user should update `__repr__` method as well.

Development
-----------

### Bumping version

#### Preparation

Install
[bump2version](https://github.com/c4urself/bump2version#installation).

#### Pre-release

Choose which version number category to bump following [semver
specification](http://semver.org/).

Test bumping version
```bash
bump2version --dry-run --verbose $CATEGORY
```

where `$CATEGORY` is the target version number category name, possible
values are `patch`/`minor`/`major`.

Bump version
```bash
bump2version --verbose $CATEGORY
```

This will set version to `major.minor.patch-alpha`. 

#### Release

Test bumping version
```bash
bump2version --dry-run --verbose --tag release
```

Bump version
```bash
bump2version --verbose --tag release
```

This will set version to `major.minor.patch` and add `Git` tag.

#### Notes

To avoid inconsistency between branches and pull requests,
bumping version should be merged into `master` branch as separate pull
request.

### Running tests

Plain:
- with `CPython`
  ```bash
  python setup.py test
  ```
- with `PyPy`
  ```bash
  pypy setup.py test
  ```

Inside `Docker` container:
- with `CPython`
  ```bash
  docker-compose --file docker-compose.cpython.yml up
  ```
- with `PyPy`
  ```bash
  docker-compose --file docker-compose.pypy.yml up
  ```

`Bash` script (e.g. can be used in `Git` hooks):
- with `CPython`
  ```bash
  ./run-tests.sh
  ```
  or
  ```bash
  ./run-tests.sh cpython
  ```

- with `PyPy`
  ```bash
  ./run-tests.sh pypy
  ```

`PowerShell` script (e.g. can be used in `Git` hooks):
- with `CPython`
  ```powershell
  .\run-tests.ps1
  ```
  or
  ```powershell
  .\run-tests.ps1 cpython
  ```
- with `PyPy`
  ```powershell
  .\run-tests.ps1 pypy
  ```
