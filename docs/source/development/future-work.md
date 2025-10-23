# Future Enhancement Opportunities

## Performance Optimizations (Without Breaking API)

### 1. Reduce Type Conversion Overhead

**Problem**: Deletion operations 7% slower due to C↔Python type conversions

**Potential solutions**:
- Minimize Python object wrapping/unwrapping
- Implement C-level cleanup routines
- Cache converted objects

**Estimated impact**: 5-10% deletion speedup

### 2. Implement C-Level Fast Paths

**Approach**: Add C-only functions for hot paths within current constraints

**Examples**:
```cython
# Fast path for iteration
cdef inline object _fast_next(self, key):
    cdef Node node = <Node>dict.__getitem__(self, key)
    return node.next_key
```

**Estimated impact**: 10-20% iteration speedup

### 3. Add Specialized Bulk Operations

**New methods**:
- `bulk_insert(items)` - Insert multiple items efficiently
- `bulk_delete(keys)` - Delete multiple keys in one pass
- `bulk_move(keys, position)` - Move multiple keys at once

**Benefits**:
- Amortize overhead across operations
- Reduce list traversals
- Better cache utilization

**Estimated impact**: 30-50% speedup for bulk operations

### 4. Memory Pooling for Node Allocation

**Approach**: Pre-allocate Node objects in pools

**Implementation**:
```cython
cdef class NodePool:
    cdef list free_nodes
    cdef int pool_size

    cdef Node allocate(self):
        if self.free_nodes:
            return self.free_nodes.pop()
        return Node(None, None, None)

    cdef void deallocate(self, Node node):
        self.free_nodes.append(node)
```

**Benefits**:
- Faster allocation/deallocation
- Reduced heap fragmentation
- Better memory locality

**Estimated impact**: 10-15% speedup for create/delete operations

### 5. Lazy Evaluation for Expensive Operations

**Approach**: Defer computation until actually needed

**Examples**:
- `keys()` returns lazy view instead of list
- Cache results until dict modified
- Implement view objects (like dict.keys() in Python 3)

**Benefits**:
- Reduced memory allocation
- Faster for partial iteration
- More Pythonic API

**Estimated impact**: Variable (big for partial iteration)

### 6. Hot Path Micro-Optimizations

**Techniques**:
- Inline critical operations in `__getitem__`/`__setitem__`
- Use Cython type hints and `@cython.locals()`
- Profile-guided optimization
- Cache frequently accessed attributes

**Example**:
```cython
@cython.locals(node=Node)
def __getitem__(self, key):
    node = <Node>dict.__getitem__(self, key)
    return node.value
```

**Estimated impact**: 5-10% speedup for access operations

## Feature Additions

### 1. Thread-Safe Variant

**Implementation**:
```python
from threading import RLock

class ThreadSafeCodict(codict):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self._lock = RLock()

    def __setitem__(self, key, value):
        with self._lock:
            super().__setitem__(key, value)

    # ... wrap all modification methods
```

**Use cases**:
- Multi-threaded applications
- Shared caches
- Concurrent data structures

### 2. Immutable Variant

**Implementation**:
```python
class FrozenCodict(codict):
    def __setitem__(self, key, value):
        raise TypeError("FrozenCodict is immutable")

    def __delitem__(self, key):
        raise TypeError("FrozenCodict is immutable")

    # ... raise on all modification methods

    def __hash__(self):
        return hash(tuple(self.items()))
```

**Benefits**:
- Hashable (can be dict key)
- Safe sharing between threads
- Guaranteed immutability

### 3. View Objects

**Implementation**: Like `dict.keys()` in Python 3

```python
class KeysView:
    def __init__(self, codict_obj):
        self._codict = codict_obj

    def __iter__(self):
        return self._codict.iterkeys()

    def __len__(self):
        return len(self._codict)

    def __contains__(self, key):
        return key in self._codict
```

**Benefits**:
- Lazy evaluation
- Memory efficient
- Standard Python 3 API

### 4. Comparison Operators

**Add**: `<`, `>`, `<=`, `>=` based on order

```python
def __lt__(self, other):
    """Compare by lexicographic order of items."""
    return list(self.items()) < list(other.items())
```

**Use cases**:
- Sorting collections of codicts
- Order-based comparisons

### 5. Slicing Support

**Implementation**:
```python
def __getitem__(self, key):
    if isinstance(key, slice):
        # Return new codict with sliced items
        items = list(self.items())[key]
        return codict(items)
    else:
        # Regular key access
        return super().__getitem__(key)
```

**Example**:
```python
cd = codict([('a', 1), ('b', 2), ('c', 3), ('d', 4)])
cd[1:3]  # codict([('b', 2), ('c', 3)])
```

## Tooling Improvements

### 1. Profiling Tools

**Tool**: codict-specific profiler

```python
class CodictProfiler:
    def __init__(self, cd):
        self.cd = cd
        self.stats = defaultdict(int)

    def profile_method(self, method_name):
        original = getattr(self.cd, method_name)

        def wrapper(*args, **kwargs):
            start = time.perf_counter()
            result = original(*args, **kwargs)
            elapsed = time.perf_counter() - start
            self.stats[method_name] += elapsed
            return result

        setattr(self.cd, method_name, wrapper)
```

### 2. Memory Visualization Tools

**Tool**: Visualize codict memory layout

```python
def visualize_memory(cd):
    """Generate ASCII visualization of linked list."""
    print("HEAD")
    key = cd.firstkey()
    while key:
        node = cd._dict_impl().__getitem__(cd, key)
        print(f"  ↓")
        print(f"[{key}: {cd[key]}]")
        try:
            key = cd.next_key(key)
        except (StopIteration, KeyError):
            break
    print("  ↓")
    print("TAIL")
```

### 3. Benchmarking Suite for Regression Detection

**Tool**: Automated performance regression tests

```python
def benchmark_regression():
    """Compare performance against baseline."""
    baseline = load_baseline_results()
    current = run_benchmarks()

    for method in current:
        if current[method] > baseline[method] * 1.1:
            print(f"REGRESSION: {method} is 10% slower!")
```

### 4. Documentation Generation from Docstrings

**Tool**: Sphinx integration with Cython

```bash
# Generate API docs from docstrings
sphinx-apidoc -o docs/api src/odict/
sphinx-build docs docs/_build/html
```

## High-Performance Variant (Breaking Changes)

### Concept: `fastcodict`

A separate implementation using composition instead of inheritance, enabling cpdef optimizations.

**Architecture**:
```cython
cdef class FastCodict:
    cdef dict _storage
    cdef object _head
    cdef object _tail

    cpdef get(self, key, default=None):
        # 20-40% faster due to cpdef
        ...

    cpdef list keys(self):
        # 20-40% faster due to cpdef
        ...
```

**Trade-offs**:
- **+20-40% faster** (theoretical)
- **Not a dict subclass** (`isinstance(fc, dict)` → `False`)
- **Different API** (delegate pattern)
- **Incompatible with odict** (not drop-in replacement)

**Use case**: Maximum performance when API compatibility not required

## Memory Optimizations

### 1. Compressed Nodes for Small Values

**Idea**: Store small integers/bools inline

```cython
cdef class CompressedNode:
    cdef public object prev_key
    cdef public object next_key
    cdef int small_value_flag
    cdef long small_value  # For small ints
    cdef object large_value  # For objects
```

**Benefits**:
- No Python object for small values
- Less memory for common case (ints, bools)
- Fewer allocations

### 2. Node Reuse (Recycling)

**Approach**: Don't deallocate deleted nodes, reuse them

```cython
cdef class Codict:
    cdef list _free_nodes  # Pool of recycled nodes

    def __delitem__(self, key):
        node = dict.__getitem__(self, key)
        # Unlink but don't deallocate
        self._free_nodes.append(node)
        dict.__delitem__(self, key)

    def __setitem__(self, key, value):
        if self._free_nodes:
            node = self._free_nodes.pop()
            node.value = value
            # ... reuse node
```

**Benefits**:
- Faster allocation (no malloc)
- Reduced heap fragmentation

## API Extensions

### 1. Atomic Operations

```python
def atomic_move_and_insert(self, key_to_move, ref_key, new_key, new_value):
    """Move key and insert new key atomically."""
    with transaction(self):
        self.movebefore(ref_key, key_to_move)
        self.insertafter(key_to_move, new_key, new_value)
```

### 2. Batch Operations with Rollback

```python
with cd.batch() as batch:
    batch.insert('a', 1)
    batch.insert('b', 2)
    batch.move('a', 'first')
    # All or nothing
```

### 3. Change Tracking

```python
cd = TrackedCodict()
cd['a'] = 1
cd['b'] = 2
del cd['a']

print(cd.changes)
# [('insert', 'a', 1), ('insert', 'b', 2), ('delete', 'a')]
```

## Compatibility Enhancements

### 1. Python 2/3 Compatibility Layer

```python
if sys.version_info[0] < 3:
    # Python 2 compatibility
    def iteritems(self):
        return self.items()
```

### 2. Type Hints (PEP 484)

```python
from typing import Iterator, Tuple, TypeVar, Generic

K = TypeVar('K')
V = TypeVar('V')

class codict(Generic[K, V]):
    def __getitem__(self, key: K) -> V: ...
    def keys(self) -> list[K]: ...
    def items(self) -> list[Tuple[K, V]]: ...
```

## Related Documentation

- [Optimizations](optimizations.md) - What we've tried
- [Performance](../technical/performance.md) - Current performance
- [Architecture](../technical/architecture.md) - Current design
