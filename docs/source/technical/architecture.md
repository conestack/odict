# Codict Architecture

## Overview

Codict is a Cython-optimized implementation of ordered dictionaries that uses C extension types for improved performance and memory efficiency.

## Core Components

### Cython Node Class

The fundamental building block is a C extension type that replaces Python lists:

```cython
cdef class Node:
    cdef public object prev_key
    cdef public object value
    cdef public object next_key
```

**Benefits over Python lists `[prev_key, value, next_key]`**:
- **C-level attribute access**: Faster than Python list indexing
- **Lower memory overhead**: ~36% less memory per node
- **Type-safe operations**: Cython type checking at compile time
- **Full pickle compatibility**: Custom `__reduce__` support

**Memory Comparison**:
- Python list node: ~88 bytes (list object + 3 references + overhead)
- Cython Node: ~56 bytes (extension object + 3 references)
- **Savings: 32 bytes per node (36%)**

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

2. **`codict` inherits from both `_codict` and `dict`**
   - Provides dict interface (`isinstance(cd, dict)` → `True`)
   - Maintains ordered dict behavior from `_codict`

3. **`_dict_impl()` method**:
   ```python
   def _dict_impl(self):
       return dict  # Returns the dict class for dict operations
   ```

### Internal Structure

**Double-linked list with sentinel**:
```
_nil (sentinel node)
  ↓
[Node: prev='_nil', key='a', value=1, next='b']
  ↓
[Node: prev='a', key='b', value=2, next='c']
  ↓
[Node: prev='b', key='c', value=3, next='_nil']
  ↓
_nil (circular back to sentinel)
```

**Internal dictionary for O(1) lookups**:
```python
{
    'a': Node(prev='_nil', value=1, next='b'),
    'b': Node(prev='a', value=2, next='c'),
    'c': Node(prev='b', value=3, next='_nil')
}
```

## Implementation Details

### Node Allocation

Nodes are created using Cython's object creation:
```cython
# C-optimized allocation
cdef Node node = Node(prev_key, value, next_key)
```

This is faster than Python list allocation because:
- Single allocation (vs. list + 3 elements)
- Direct C struct access
- No list resize overhead

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
        node = dict.__getitem__(self, key)
        node.value = value
    else:
        # Insert at end
        node = Node(self.lt, value, None)
        dict.__setitem__(self, key, node)
        # Update linked list
```

**Deletion (`__delitem__`)**: O(1)
```python
def __delitem__(self, key):
    node = dict.__getitem__(self, key)
    # Unlink from list
    prev_node = dict.__getitem__(self, node.prev_key)
    next_node = dict.__getitem__(self, node.next_key)
    prev_node.next_key = node.next_key
    next_node.prev_key = node.prev_key
    # Remove from dict
    dict.__delitem__(self, key)
```

**Iteration (`__iter__`)**: O(n)
```python
def __iter__(self):
    key = self.lh  # Start at list head
    while key is not None:
        yield key
        node = dict.__getitem__(self, key)
        key = node.next_key
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
- All Node connections are rebuilt correctly
- Works with all pickle protocols (0-5)

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

- **Per-node overhead**: 56 bytes (Cython Node)
- **Dictionary overhead**: ~8 bytes per key (dict hash table)
- **Total per item**: ~64 bytes (vs. ~96 bytes for Python odict)
- **Reduction**: **~33% less memory**

### Trade-offs

**Advantages**:
- Fast C-level attribute access
- Lower memory footprint
- Compiled code (no interpretation overhead)

**Disadvantages**:
- Type conversion overhead (C ↔ Python)
- Cannot use `cpdef` optimization (architectural constraint)
- Requires compilation (not pure Python)

## Design Rationale

### Why Not Use cpdef?

See [Optimizations Analysis](../development/optimizations.md) for detailed explanation.

**Summary**: `cpdef` would provide 20-40% additional speedup, but requires `cdef class`, which cannot do multiple inheritance with `dict`. This would break API compatibility.

### Why Multiple Inheritance?

Having `codict` inherit from `dict` provides:
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

**Cython codict**:
- Cython/C implementation
- Uses C extension type for nodes
- Compiled (requires C compiler)
- Lower memory usage (36% less)
- Faster (15-38% creation speedup)
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
