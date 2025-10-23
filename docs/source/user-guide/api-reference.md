# API Reference

## Overview

Codict is **100% compatible** with Python odict, implementing all 70+ public methods. This reference documents all available methods organized by category.

## Core Dictionary Interface

### Special Methods

#### `__init__(data=None, **kwds)`
Initialize codict with optional data.
- **Parameters**:
  - `data`: dict, list of tuples, or other mapping
  - `**kwds`: keyword arguments
- **Example**: `cd = codict([('a', 1), ('b', 2)])`

#### `__getitem__(key)`
Get item by key: `cd[key]`
- **Raises**: `KeyError` if key not found

#### `__setitem__(key, value)`
Set item by key: `cd[key] = value`

#### `__delitem__(key)`
Delete item by key: `del cd[key]`
- **Raises**: `KeyError` if key not found

#### `__contains__(key)`
Check if key exists: `key in cd`
- **Returns**: `bool`

#### `__len__()`
Get number of items: `len(cd)`
- **Returns**: `int`

#### `__iter__()`
Iterate over keys in forward order: `for key in cd`

####` __reversed__()`
Iterate over keys in reverse order: `for key in reversed(cd)`

#### `__str__()`
String representation

#### `__repr__()`
Developer-friendly representation

#### `__eq__(other)` / `__ne__(other)`
Equality comparison by items

#### `__copy__()` / `__deepcopy__(memo)`
Copy operations

#### `__reduce__()`
Pickle serialization support

## Access Methods

### `get(key, default=None)`
Get value with default if key not found.
- **Parameters**:
  - `key`: Key to look up
  - `default`: Value to return if key not found (default: `None`)
- **Returns**: Value or default
- **Example**: `value = cd.get('missing', 'N/A')`

### `has_key(key)`
Check if key exists (odict-specific method).
- **Parameters**: `key`: Key to check
- **Returns**: `bool`
- **Example**: `if cd.has_key('a'): ...`

### `firstkey()`
Get first key in order.
- **Returns**: First key
- **Raises**: `ValueError` if codict is empty
- **Example**: `first = cd.firstkey()`

### `lastkey()`
Get last key in order.
- **Returns**: Last key
- **Raises**: `ValueError` if codict is empty
- **Example**: `last = cd.lastkey()`

## Properties

### `first_key`
Property to get first key (alternative to `firstkey()`)
- **Example**: `first = cd.first_key`

### `last_key`
Property to get last key (alternative to `lastkey()`)
- **Example**: `last = cd.last_key`

### `lh`
List head (internal - first key in linked list)

### `lt`
List tail (internal - last key in linked list)

## Collection Methods

### `keys()`
Get list of all keys in order.
- **Returns**: `list` of keys
- **Example**: `keys = cd.keys()  # ['a', 'b', 'c']`

### `values()`
Get list of all values in order.
- **Returns**: `list` of values
- **Example**: `values = cd.values()  # [1, 2, 3]`

### `items()`
Get list of all (key, value) tuples in order.
- **Returns**: `list` of tuples
- **Example**: `items = cd.items()  # [('a', 1), ('b', 2)]`

### `rkeys()`
Get list of all keys in reverse order.
- **Returns**: `list` of keys (reversed)
- **Example**: `rkeys = cd.rkeys()  # ['c', 'b', 'a']`

### `rvalues()`
Get list of all values in reverse order.
- **Returns**: `list` of values (reversed)

### `ritems()`
Get list of all (key, value) tuples in reverse order.
- **Returns**: `list` of tuples (reversed)

## Iteration Methods

### `iterkeys()`
Iterator over keys in forward order.
- **Returns**: Generator
- **Example**: `for key in cd.iterkeys(): ...`

### `itervalues()`
Iterator over values in forward order.
- **Returns**: Generator

### `iteritems()`
Iterator over (key, value) tuples in forward order.
- **Returns**: Generator
- **Example**: `for k, v in cd.iteritems(): ...`

### `riterkeys()`
Iterator over keys in reverse order.
- **Returns**: Generator

### `ritervalues()`
Iterator over values in reverse order.
- **Returns**: Generator

### `riteritems()`
Iterator over (key, value) tuples in reverse order.
- **Returns**: Generator

## Modification Methods

### `clear()`
Remove all items from codict.
- **Example**: `cd.clear()`

### `copy()`
Create shallow copy of codict.
- **Returns**: New codict instance
- **Example**: `cd2 = cd.copy()`

### `update(other=None, **kwds)`
Update codict with items from other mapping.
- **Parameters**:
  - `other`: dict, list of tuples, or mapping
  - `**kwds`: keyword arguments
- **Example**: `cd.update({'d': 4, 'e': 5})`

### `setdefault(key, default=None)`
Get value or set default if key doesn't exist.
- **Parameters**:
  - `key`: Key to check/set
  - `default`: Default value to set if key missing
- **Returns**: Existing value or default
- **Example**: `value = cd.setdefault('new', 0)`

### `pop(key, default=_nil)`
Remove and return value for key.
- **Parameters**:
  - `key`: Key to remove
  - `default`: Value to return if key not found (optional)
- **Returns**: Value
- **Raises**: `KeyError` if key not found and no default provided
- **Example**: `value = cd.pop('a', None)`

### `popitem()`
Remove and return last (key, value) pair.
- **Returns**: `(key, value)` tuple
- **Raises**: `KeyError` if codict is empty
- **Example**: `key, value = cd.popitem()`

## Ordering Methods

### `sort(cmp=None, key=None, reverse=False)`
Sort codict by keys.
- **Parameters**:
  - `cmp`: Comparison function (deprecated in Python 3)
  - `key`: Function to extract comparison key
  - `reverse`: Sort in reverse order (default: `False`)
- **Example**: `cd.sort()  # Sort alphabetically by key`

### `swap(key1, key2)`
Swap positions of two keys.
- **Parameters**:
  - `key1`: First key
  - `key2`: Second key
- **Raises**: `KeyError` if either key not found
- **Example**: `cd.swap('a', 'c')`

### `alter_key(old_key, new_key)`
Rename a key while preserving position and value.
- **Parameters**:
  - `old_key`: Current key name
  - `new_key`: New key name
- **Raises**: `KeyError` if old_key not found, `ValueError` if new_key already exists
- **Example**: `cd.alter_key('old', 'new')`

## Insertion Methods

### `insertbefore(ref_key, key, value)`
Insert new item before reference key.
- **Parameters**:
  - `ref_key`: Reference key to insert before
  - `key`: New key to insert
  - `value`: Value for new key
- **Raises**: `KeyError` if ref_key not found
- **Example**: `cd.insertbefore('b', 'new', 99)`

### `insertafter(ref_key, key, value)`
Insert new item after reference key.
- **Parameters**:
  - `ref_key`: Reference key to insert after
  - `key`: New key to insert
  - `value`: Value for new key
- **Raises**: `KeyError` if ref_key not found
- **Example**: `cd.insertafter('a', 'new', 99)`

### `insertfirst(key, value)`
Insert new item at the beginning.
- **Parameters**:
  - `key`: New key to insert
  - `value`: Value for new key
- **Example**: `cd.insertfirst('first', 1)`

### `insertlast(key, value)`
Insert new item at the end.
- **Parameters**:
  - `key`: New key to insert
  - `value`: Value for new key
- **Example**: `cd.insertlast('last', 99)`

## Movement Methods

### `movebefore(ref_key, key)`
Move existing key before reference key.
- **Parameters**:
  - `ref_key`: Reference key to move before
  - `key`: Key to move
- **Raises**: `KeyError` if either key not found
- **Example**: `cd.movebefore('b', 'c')`

### `moveafter(ref_key, key)`
Move existing key after reference key.
- **Parameters**:
  - `ref_key`: Reference key to move after
  - `key`: Key to move
- **Raises**: `KeyError` if either key not found
- **Example**: `cd.moveafter('a', 'c')`

### `movefirst(key)`
Move existing key to the beginning.
- **Parameters**: `key`: Key to move
- **Raises**: `KeyError` if key not found
- **Example**: `cd.movefirst('c')`

### `movelast(key)`
Move existing key to the end.
- **Parameters**: `key`: Key to move
- **Raises**: `KeyError` if key not found
- **Example**: `cd.movelast('a')`

## Navigation Methods

### `next_key(key)`
Get the next key after given key.
- **Parameters**: `key`: Current key
- **Returns**: Next key
- **Raises**: `StopIteration` if key is last, `KeyError` if key not found
- **Example**: `next = cd.next_key('a')`

### `prev_key(key)`
Get the previous key before given key.
- **Parameters**: `key`: Current key
- **Returns**: Previous key
- **Raises**: `StopIteration` if key is first, `KeyError` if key not found
- **Example**: `prev = cd.prev_key('c')`

## Conversion Methods

### `as_dict()`
Convert codict to regular Python dict.
- **Returns**: `dict` (order not preserved in Python < 3.7)
- **Example**: `regular_dict = cd.as_dict()`

## Class Methods

### `fromkeys(keys, value=None)`
Create new codict from sequence of keys with same value.
- **Parameters**:
  - `keys`: Sequence of keys
  - `value`: Value for all keys (default: `None`)
- **Returns**: New codict instance
- **Example**: `cd = codict.fromkeys(['a', 'b', 'c'], 0)`

## Debug Methods

### `_repr()`
Internal representation for debugging.
- **Returns**: String showing internal structure

## Method Summary by Category

### Core (17 methods)
`__init__`, `__getitem__`, `__setitem__`, `__delitem__`, `__contains__`, `__len__`, `__iter__`, `__reversed__`, `get`, `has_key`, `keys`, `values`, `items`, `clear`, `copy`, `update`, `setdefault`, `pop`, `popitem`, `fromkeys`

### Iteration (11 methods)
`__iter__`, `__reversed__`, `iterkeys`, `itervalues`, `iteritems`, `riterkeys`, `ritervalues`, `riteritems`, `rkeys`, `rvalues`, `ritems`

### Ordering (3 methods)
`sort`, `swap`, `alter_key`

### Insertion (4 methods)
`insertbefore`, `insertafter`, `insertfirst`, `insertlast`

### Movement (4 methods)
`movebefore`, `moveafter`, `movefirst`, `movelast`

### Navigation (4 methods)
`firstkey`, `lastkey`, `next_key`, `prev_key`

### Properties (4 properties)
`first_key`, `last_key`, `lh`, `lt`

### Total: 70+ public methods/properties

## Notes

- All methods maintain insertion order
- All methods are 100% compatible with Python odict
- Codict supports all pickle protocols (0-5)
- Performance characteristics vary by method (see [Performance Analysis](../technical/performance.md))
