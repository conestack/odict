# Codict Architecture

## Overview

Codict is a implementation of ordered dictionaries that uses C extension types for improved performance and memory efficiency.

## Core Components

### Entry Class

The fundamental building block is a C extension type that replaces Python lists:

```cython
cdef class Entry:
    cdef public object prev_key
    cdef public object value
    cdef public object next_key
```

**Benefits over Python lists `[prev_key, value, next_key]`**:
- **C-level attribute access**: Faster than Python list indexing
- **Lower memory overhead**: Reduced memory per entry
- **Type-safe operations**: type checking at compile time
- **Full pickle compatibility**: Custom `__reduce__` support

**Note**: While Entry provides C-level attribute access, actual performance varies by operation. See [Performance Analysis](performance.md) for detailed benchmarks.

### Class Hierarchy

Codict mirrors the Python odict structure for 100% API compatibility:

```
_codict (abstract base class)
    ↓
codict (_codict + dict)  [multiple inheritance]
```

**Key design decisions**:

1. **`_codict` is a regular Python class** (not `cdef class`)
   - Reason: Enables multiple inheritance with built-in `dict`
   - Trade-off: Cannot use `cpdef` methods (see [Optimizations](../development/optimizations.md))

2. **`odict` inherits from both `_codict` and `dict`**
   - Provides dict interface (`isinstance(cd, dict)` → `True`)
   - Maintains ordered dict behavior from `_codict`

3. **`_dict_cls()` method**:
   ```python
   def _dict_cls(self):
       return dict  # Returns the dict class for dict operations
   ```

4. **`_entry_cls()` method**:
   ```python
   def _entry_cls(self):
       return Entry  # Returns the Entry cdef class for nodes
   ```

### Internal Structure

**Double-linked list with sentinel**:
```
_nil (sentinel entry)
  ↓
[Entry: prev='_nil', key='a', value=1, next='b']
  ↓
[Entry: prev='a', key='b', value=2, next='c']
  ↓
[Entry: prev='b', key='c', value=3, next='_nil']
  ↓
_nil (circular back to sentinel)
```

**Internal dictionary for O(1) lookups**:
```python
{
    'a': Entry(prev='_nil', value=1, next='b'),
    'b': Entry(prev='a', value=2, next='c'),
    'c': Entry(prev='b', value=3, next='_nil')
}
```

## Implementation Details

### Entry Allocation

Entries are created using Cython's object creation:
```cython
# C-optimized allocation
cdef Entry entry = Entry(prev_key, value, next_key)
```

This provides C-level access benefits:
- Single allocation (vs. list + 3 elements)
- Direct C struct access
- No list resize overhead

However, benchmarks show that type conversion overhead can impact bulk operations (e.g., `values()`, `items()`).

### Key Operations

**Lookup (`__getitem__`)**: O(1)
```python
def __getitem__(self, key):
    node = dict.__getitem__(self, key)  # O(1) dict lookup
    return node.value
```

**Insertion (`__setitem__`)**: O(1)
```python
def __setitem__(self, key, value):
    if key in self:
        # Update existing
        entry = dict.__getitem__(self, key)
        entry.value = value
    else:
        # Insert at end
        entry = Entry(self.lt, value, None)
        dict.__setitem__(self, key, entry)
        # Update linked list
```

**Deletion (`__delitem__`)**: O(1)
```python
def __delitem__(self, key):
    entry = dict.__getitem__(self, key)
    # Unlink from list
    prev_entry = dict.__getitem__(self, entry.prev_key)
    next_entry = dict.__getitem__(self, entry.next_key)
    prev_entry.next_key = entry.next_key
    next_entry.prev_key = entry.prev_key
    # Remove from dict
    dict.__delitem__(self, key)
```

**Iteration (`__iter__`)**: O(n)
```python
def __iter__(self):
    key = self.lh  # Start at list head
    while key is not None:
        yield key
        entry = dict.__getitem__(self, key)
        key = entry.next_key
        if key == None:  # Reached sentinel
            break
```

### Pickle Support

Codict implements custom pickle serialization:

```python
def __reduce__(self):
    # Return: (callable, args, state)
    return (
        self.__class__,
        (list(self.items()),),
        None
    )
```

This ensures:
- Order is preserved across pickle/unpickle
- All Entry connections are rebuilt correctly
- Works with all pickle protocols (2+)

## Performance Characteristics

### Time Complexity

| Operation | Complexity | Notes |
|-----------|------------|-------|
| `__getitem__` | O(1) | Dict lookup |
| `__setitem__` | O(1) | Dict insert + list link |
| `__delitem__` | O(1) | Dict delete + list unlink |
| `__contains__` | O(1) | Dict membership test |
| `__len__` | O(1) | Dict length |
| `keys()` | O(n) | Traverse linked list |
| `values()` | O(n) | Traverse linked list |
| `items()` | O(n) | Traverse linked list |
| `firstkey()` | O(1) | Access list head |
| `lastkey()` | O(1) | Access list tail |
| `next_key()` | O(1) | Follow next pointer |
| `prev_key()` | O(1) | Follow prev pointer |
| `sort()` | O(n log n) | Python sort |
| `insertbefore()` | O(1) | List manipulation |
| `movefirst()` | O(1) | List manipulation |

### Space Complexity

- **Per-entry overhead**: Entry cdef class
- **Dictionary overhead**: ~8 bytes per key (dict hash table)
- **Memory usage**: Competitive with Python odict for most operations

### Trade-offs

**Advantages**:
- C-level attribute access for Entry objects
- Compiled code for core operations
- Competitive performance for basic operations (get/set/delete)
- Slightly faster for move operations

**Disadvantages**:
- Type conversion overhead (C ↔ Python) affects bulk operations
- Cannot use `cpdef` optimization (architectural constraint)
- Requires compilation (not pure Python)
- Significantly slower for: `values()`, `items()`, `copy()`, reverse iteration

## Design Rationale

### Why Not Use cpdef?

See [Optimizations Analysis](../development/optimizations.md) for detailed explanation.

**Summary**: `cpdef` would provide 20-40% additional speedup, but requires `cdef class`, which cannot do multiple inheritance with `dict`. This would break API compatibility.

### Why Multiple Inheritance?

Having `odict` inherit from `dict` provides:
- `isinstance(cd, dict)` returns `True`
- Duck-typing compatibility with dict-expecting code
- Direct access to optimized dict C methods

Alternative (composition) would break compatibility:
```python
# Would NOT work with this code:
def process_dict(d):
    assert isinstance(d, dict)  # Would fail!
```

## Comparison with Other Implementations

### vs. Python odict (pyodict)

**Python odict**:
- Pure Python implementation
- Uses Python lists for nodes: `[prev, value, next]`
- Easy to debug (readable Python code)
- Portable (no compilation needed)
- Higher memory usage
- Slower due to interpretation overhead

**codict**:
- Cython/C implementation
- Uses C extension type for entries
- Compiled (requires C compiler)
- Competitive performance for basic operations
- Faster for move operations
- **Note**: Slower for bulk operations like `values()`, `items()`, `copy()`
- Platform-specific binary

### vs. collections.OrderedDict

**OrderedDict**:
- Standard library (always available)
- C implementation (in CPython)
- Different API (no `firstkey()`, `insertbefore()`, etc.)
- Good performance
- No odict compatibility

**Codict**:
- Requires installation/compilation
- 100% odict API compatible
- More methods (70+ vs. ~20 in OrderedDict)
- Similar or better performance
- Drop-in odict replacement

### vs. dict (Python 3.7+)

**dict**:
- Fastest (no ordering overhead after 3.7)
- Order is maintained but not guaranteed
- Minimal API

**Codict**:
- Explicit ordering guarantees
- Rich API for order manipulation
- Slightly slower (expected for ordering features)

## Future Architectural Considerations

See [Future Work](../development/future-work.md) for potential enhancements:
- Separate high-performance variant (`fastcodict`) using composition
- Memory pooling for Node allocation
- C-level bulk operations

## Related Documentation

- [Performance Analysis](performance.md) - Benchmark results
- [Memory Analysis](memory.md) - Detailed memory breakdown
- [Optimizations](../development/optimizations.md) - Why cpdef doesn't work
