# Memory Analysis

## Overview

Codict achieves **36% memory reduction** per node compared to Python odict through the use of C-optimized extension types.

## Node Memory Footprint

### Python odict Node

**Structure**:
```python
node = [prev_key, value, next_key]  # Python list object
```

**Memory breakdown**:
- List object header: ~56 bytes
- 3 object references: 3 × 8 bytes = 24 bytes
- List overhead (capacity, etc.): ~8 bytes
- **Total: ~88 bytes per node**

### codict Node

**Structure**:
```cython
cdef class Node:
    cdef public object prev_key
    cdef public object value
    cdef public object next_key
```

**Memory breakdown**:
- extension object header: ~40 bytes
- 3 object references: 3 × 8 bytes = 24 bytes
- **Total: ~56 bytes per node**

### Memory Savings

**Per node**: 88 - 56 = **32 bytes (36% reduction)**

## Scale Analysis

### Memory Savings by Scale

| Scale | Python odict | codict | Savings | Reduction |
|-------|--------------|---------------|---------|-----------|
| 1,000 | ~88 KB | ~56 KB | ~32 KB | 36% |
| 10,000 | ~880 KB | ~560 KB | ~320 KB | 36% |
| 100,000 | ~8.8 MB | ~5.6 MB | ~3.2 MB | 36% |
| 1,000,000 | ~88 MB | ~56 MB | ~32 MB | 36% |

**Consistent 36% reduction across all scales**

## Total Memory Usage

Memory usage includes:
1. Node storage (detailed above)
2. Dictionary hash table (~8 bytes per key)
3. Key/value objects (depends on types)

### Example: 1,000,000 String Keys

Assuming keys are short strings (~10 chars) and values are integers:

**Python odict**:
- Nodes: ~88 MB
- Dict table: ~8 MB
- Keys (strings): ~10 MB
- Values (ints): ~28 MB
- **Total: ~134 MB**

**codict**:
- Nodes: ~56 MB ✅ (32 MB less)
- Dict table: ~8 MB
- Keys (strings): ~10 MB
- Values (ints): ~28 MB
- **Total: ~102 MB**

**Savings: ~32 MB (24% of total)**

## Memory Efficiency Benefits

### 1. Reduced Cache Pressure

Smaller node size means:
- More nodes fit in CPU cache
- Fewer cache misses
- Better performance for large datasets

### 2. Better Memory Locality

Nodes are:
- Allocated as single objects
- More compact in memory
- Better spatial locality

### 3. Reduced Allocation Overhead

- Single allocation per node (vs. list + elements)
- Less heap fragmentation
- Faster allocation/deallocation

## Memory Measurement Methodology

Memory measurements use Python's `tracemalloc` module:

```python
import tracemalloc
import gc

# Force garbage collection
gc.collect()

# Start tracking
tracemalloc.start()
mem_before = tracemalloc.get_traced_memory()[0]

# Create structure
cd = codict([(str(i), i) for i in range(1000000)])

# Measure after
mem_after = tracemalloc.get_traced_memory()[0]
tracemalloc.stop()

# Calculate delta
memory_used = (mem_after - mem_before) / (1024 * 1024)  # MB
```

## Memory vs. Performance Trade-off

### Codict Benefits

- **Lower memory**: 36% per node
- **Faster creation**: 15-38% faster
- **Good cache behavior**: Smaller nodes = better cache utilization

### Considerations

- **Compilation required**: Binary size (~1.9 MB for .so file)
- **Type conversion**: Some overhead converting C ↔ Python

**Overall**: Memory reduction + performance gain with minimal trade-offs

## Comparison with Other Implementations

| Implementation | Bytes/Node | vs codict | Notes |
|---------------|------------|-----------|-------|
| **codict** | **56** | **Baseline** | C extension type |
| Python odict | 88 | +57% | Python list |
| OrderedDict | ~80 | +43% | C implementation |
| dict | 0* | N/A | No ordering overhead |

*dict has no per-node overhead for ordering (just hash table)

## Recommendations

### For Memory-Constrained Environments

Codict is ideal when:
- ✅ Working with large datasets (100K+ items)
- ✅ Memory is limited (embedded systems, containers)
- ✅ Multiple ordered dicts in memory
- ✅ Long-lived data structures

### Example Use Cases

1. **Large Configuration Files**:
   - 10,000 config entries
   - Savings: ~320 KB per config object
   - 10 configs = **3.2 MB saved**

2. **Data Processing Pipelines**:
   - 1M records in memory
   - Savings: 32 MB per dataset
   - Multiple datasets = **significant savings**

3. **Web Application Caches**:
   - 100K cached items
   - Savings: ~3.2 MB per cache
   - Multiple caches = **noticeable reduction**

## Future Memory Optimizations

See [Future Work](../development/future-work.md):

1. **Memory pooling**: Pre-allocate Node objects
2. **Lazy node allocation**: Delay creation until needed
3. **Compressed nodes**: Store small values inline
4. **Node reuse**: Recycle deleted nodes

## Related Documentation

- [Architecture](architecture.md) - Node structure details
- [Performance Analysis](performance.md) - Speed vs. memory trade-offs
- [Benchmarking](benchmarking.md) - Measure your own memory usage
