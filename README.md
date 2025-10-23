# odict

[![PyPI version](https://img.shields.io/pypi/v/odict.svg)](https://pypi.python.org/pypi/odict)
[![PyPI downloads](https://img.shields.io/pypi/dm/odict.svg)](https://pypi.python.org/pypi/odict)
[![Test odict](https://github.com/conestack/odict/actions/workflows/test.yaml/badge.svg)](https://github.com/conestack/odict/actions/workflows/test.yaml)

**Ordered dictionary implementation** that preserves **insertion order** using an internal double-linked list. Unlike `collections.OrderedDict`, replacing an existing item keeps it at its original position.

## Features

- **Pure Python implementation** (`odict`) with optional **Cython-optimized version** (`codict`)
- **Automatic drop-in replacement**: When Cython extension is compiled, `codict` is used transparently
- **Flexible base class**: Create custom ordered dicts for special use cases (e.g., ZODB persistence)
- **Extended API**: Additional methods for moving, swapping, and reordering items
- **100% test coverage**

## Installation

```bash
pip install odict
```

The package will automatically use the Cython-optimized `codict` implementation if the extension was compiled during installation. Otherwise, it gracefully falls back to the pure Python `odict` implementation.

## Quick Start

```python
from odict import odict

# Create ordered dictionary
od = odict()
od['a'] = 1
od['b'] = 2
od['c'] = 3

# Order is preserved
print(od.keys())  # ['a', 'b', 'c']

# Replace item - keeps original position
od['b'] = 200
print(od.keys())  # ['a', 'b', 'c']  (order unchanged!)

# Initialize from list to preserve order
od = odict([('a', 1), ('b', 2), ('c', 3)])
print(od.items())  # [('a', 1), ('b', 2), ('c', 3)]

# Extended operations
od.movefirst('c')  # Move 'c' to start
od.movelast('a')   # Move 'a' to end
od.swap('b', 'c')  # Swap positions
```

## Implementation Details

### Internal Representation

odict uses a **double-linked list** embedded within dictionary values:

```python
# Each dict value is a 3-element list:
[predecessor_key, actual_value, successor_key]
```

- `self.lh`: Key of the first element (list head)
- `self.lt`: Key of the last element (list tail)
- Links use a special `_nil` sentinel object (not `None`) to mark boundaries

This design allows O(1) ordering operations while maintaining dict-like O(1) lookups.

### Cython Optimization (codict)

When the Cython extension is available, `from odict import odict` automatically imports the optimized `codict` implementation. The fallback to pure Python `odict` is completely transparent.

**Performance characteristics:**
- `codict` is competitive with `odict` for basic operations (get/set/delete)
- `codict` is slightly faster for move operations (movefirst, movelast, etc.)
- `codict` may be slower for bulk operations (values(), items(), copy())

See the [benchmarking documentation](docs/source/technical/benchmarking.md) for detailed performance comparisons.

**To check which implementation is active:**

```python
from odict import odict
print(odict.__module__)  # 'odict.codict' or 'odict.odict'
```

## Custom Ordered Dictionary Implementations

The abstract `_odict` base class allows creating custom ordered dicts for special use cases:

```python
from odict.odict import _odict
from persistent.dict import PersistentDict
from persistent.list import PersistentList

class podict(_odict, PersistentDict):
    """ZODB-compatible ordered dictionary."""

    def _dict_cls(self):
        return PersistentDict

    def _entry_cls(self):
        return PersistentList
```

This pattern avoids instance layout conflicts when inheriting from both `dict` and other base classes like ZODB's `Persistent`.

## Extended API

Beyond standard dict operations, odict provides:

- **Reordering**: `movebefore()`, `moveafter()`, `movefirst()`, `movelast()`
- **Swapping**: `swap()`
- **Insertion**: `insertbefore()`, `insertafter()`, `insertfirst()`, `insertlast()`
- **Reverse iteration**: `rkeys()`, `rvalues()`, `ritems()`, `riterkeys()`, `ritervalues()`, `riteritems()`
- **Key navigation**: `first_key`, `last_key`, `next_key()`, `prev_key()`
- **Conversion**: `as_dict()`
- **Modification**: `alter_key()`, `sort()`

## Python Version Compatibility

- **Supported**: Python 3.10 - 3.14
- **Tested**: Python 3.10, 3.11, 3.12, 3.13, 3.14

### Python < 3.7 Notes

In Python < 3.7, casting to dict fails due to [this Python bug](http://bugs.python.org/issue1615701):

```python
# This fails in Python < 3.7
dict(odict([('a', 1)]))  # {1: [nil, 1, nil]}

# Use one of these instead:
dict(odict([('a', 1)]).items())  # {'a': 1}
odict([('a', 1)]).as_dict()      # {'a': 1}
```

## History and Motivation

When this package was created, `collections.OrderedDict` didn't exist yet. Even today, odict offers unique advantages:

1. **Replacing preserves position**: Unlike `OrderedDict`, updating an existing key doesn't move it
2. **Flexible base class**: Avoid instance layout conflicts by using `_odict` abstract base
3. **Extended API**: Move, swap, and reorder operations not available in `OrderedDict`
4. **Transparent optimization**: Automatic Cython acceleration without code changes

## Development

```bash
# Clone and install for development
git clone https://github.com/conestack/odict.git
cd odict
make install

# Run tests
make test

# Run with coverage (requires 100%)
make coverage

# Code formatting
make format

# Run benchmarks
venv/bin/python -m odict.bench --mode comprehensive
```

## Contributors

- bearophile (Original Author)
- Robert Niederreiter (Maintainer)
- Georg Bernhard
- Florian Friesdorf
- Jens Klein

## License

[Python Software Foundation License](http://www.opensource.org/licenses/PythonSoftFoundation.php)
