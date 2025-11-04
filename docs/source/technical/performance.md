# Performance Analysis

## Test Environment

- **Python Version**: 3.12
- **Platform**: Linux x86_64
- **Version**: 3.x
- **Benchmark Date**: 2025
- **Benchmark Tool**: `python -m odict.bench --mode comprehensive --sizes "100,1000,10000"`

## Executive Summary

Performance characteristics of `odict` (Cython-optimized) vs `odict` (pure Python) are **highly operation-dependent**:

✅ **codict wins**: Basic operations (get/set), move operations
⚠️ **codict loses significantly**: Bulk operations (values/items/copy), reverse iteration

**Overall**: `odict` wins 55 benchmarks (38.2%) vs `odict` 35 benchmarks (24.3%)

## Benchmark Summary

From comprehensive benchmarks across 100, 1,000, and 10,000 element dictionaries:

| Implementation | Wins | Win Rate | Average Time | Notes |
|---------------|------|----------|--------------|-------|
| dict | 48 | 88.9% | 82.6ms | Expected (unordered) |
| OrderedDict | 6 | 11.1% | 166.6ms | Standard library |
| **odict** | **55** | **38.2%** | **1394.9ms** | **Pure Python** |
| **codict** | **35** | **24.3%** | **2851.7ms** | **Cython** |

**Key Finding**: Despite C-level optimizations, `odict` is NOT universally faster than `odict`.

## Detailed Performance by Operation Category

### Category 1: Basic Operations - Mixed Results

**codict Strengths**:
- `__setitem__`: Competitive (~13% slower than dict, similar to odict)
- `__getitem__`: Competitive with odict (~4x slower than dict)
- `__contains__`: Similar to odict

**codict Weaknesses**:
- `__len__`: Very slow (both odict ~10,000x slower than dict due to iteration)
- `__delitem__`: Slower than odict by ~10%

**Example - __setitem__ (10,000 objects)**:
```
dict:        11.8ms  (baseline)
OrderedDict: 11.8ms  (+0.3%)
codict:      13.1ms  (+11.3%)
odict:       13.4ms  (+13.7%)
```

**Example - __getitem__ (10,000 objects)**:
```
dict:        20.6ms  (baseline)
OrderedDict: 22.3ms  (+8.6%)
codict:      80.2ms  (+289.9%)
odict:       87.8ms  (+326.6%)
```

### Category 2: Bulk Operations - codict Much Slower

**Critical Performance Issue**: Type conversion overhead makes codict **dramatically slower** for operations that create Python objects in bulk.

**values() - 10,000 objects**:
```
dict:        35.8ms   (baseline)
OrderedDict: 247.3ms  (+590.9%)
odict:       1330.8ms (+3617.7%)
codict:      20506.0ms (+57185.8%)  ⚠️ 15x slower than odict!
```

**items() - 10,000 objects**:
```
dict:        2588.2ms  (baseline)
OrderedDict: 2941.9ms  (+13.7%)
odict:       5590.6ms  (+116.0%)
codict:      24458.8ms (+845.0%)  ⚠️ 4.4x slower than odict!
```

**copy() - 10,000 objects**:
```
dict:        26.0ms    (baseline)
OrderedDict: 2494.3ms  (+9510.4%)
odict:       54481.9ms (+209812.6%)
codict:      71267.1ms (+274484.2%)  ⚠️ 31% slower than odict!
```

### Category 3: Move Operations - codict Slightly Faster

`odict` shows small advantages in order manipulation:

**movefirst (10,000 objects)**:
```
odict:   598.5ms
codict:  596.9ms  (0.3% faster)
```

**movelast (10,000 objects)**:
```
odict:   575.5ms
codict:   560.3ms  (2.7% faster)
```

**moveafter (10,000 objects)**:
```
odict:   558.0ms
codict:  550.4ms  (1.4% faster)
```

### Category 4: Reverse Iteration - codict Much Slower

Similar to bulk operations, reverse iteration suffers from type conversion overhead:

**ritervalues() - 10,000 objects**:
```
odict:   1231.6ms
codict:  19962.9ms  ⚠️ 15.2x slower!
```

**riteritems() - 10,000 objects**:
```
odict:   3087.9ms
codict:  22066.2ms  ⚠️ 7.1x slower!
```

## Performance Characteristics

### codict Strengths

1. **✅ Basic get/set operations**: Competitive with odict
2. **✅ Move operations**: 1-3% faster than odict
3. **✅ Memory competitive**: Similar memory usage to odict
4. **✅ C-level attribute access**: Entry cdef class provides direct field access

### codict Weaknesses

1. **❌ Bulk operations**: 4-15x slower (values, items, copy)
2. **❌ Reverse iteration**: 7-15x slower
3. **❌ Type conversion overhead**: C↔Python conversion dominates for object-creating operations
4. **❌ Overall win rate**: Only 24.3% vs odict's 38.2%

## Root Cause Analysis

### Why codict is Slower for Bulk Operations

**Python List (odict)**:
```python
# Direct Python list creation
[prev_key, value, next_key]  # Native Python objects
```

**Entry (codict)**:
```cython
cdef class Entry:
    cdef public object prev_key
    cdef public object value
    cdef public object next_key
```

While Entry provides C-level attribute access within code, **every operation that returns Entry values to Python code incurs conversion overhead**:

1. `values()` must extract `entry.value` for each entry → C↔Python conversion
2. `items()` must create `(key, entry.value)` tuples → multiple conversions
3. `copy()` must create new Entry objects → allocation + initialization overhead

### Why odict is Faster for Bulk Operations

Pure Python implementation benefits from:
- Native Python object handling
- No conversion overhead
- Optimized Python list operations
- Better integration with Python memory management

## Scale Analysis

Performance characteristics are relatively consistent across scales:

### Small (100 objects)

- codict competitive for basic ops
- Bulk operation overhead already visible

### Medium (1,000 objects)

- codict maintains competitiveness for basic ops
- Bulk operation gap widens (10-20x slower)

### Large (10,000 objects)

- Basic operations still competitive
- Bulk operations 15-50x slower

**Conclusion**: Scale doesn't significantly change relative performance - codict's weaknesses are fundamental, not scale-dependent.

## Memory Usage

Based on benchmarks, memory usage is generally competitive between odict for most operations, with some variation:

- Basic operations: Similar memory footprint
- Bulk operations: codict may use slightly less memory (despite being slower)
- Overall: Not a significant differentiator

## When to Use Each Implementation

### Use dict When:
- ✅ Maximum performance required
- ✅ Order maintenance not needed (Python 3.7+ maintains insertion order)
- ✅ No need for order manipulation methods

### Use OrderedDict When:
- ✅ Need standard library solution
- ✅ Basic ordered dict functionality sufficient
- ✅ Good balance of performance and features

### Use odict (Pure Python) When:
- ✅ Need extended API (move, swap, insertbefore, etc.)
- ✅ Frequent bulk operations (`values()`, `items()`, `copy()`)
- ✅ Frequent reverse iteration
- ✅ Pure Python portability required
- ✅ **Generally the better choice for most use cases**

### Use codict (Cython) When:
- ✅ Need extended API
- ✅ Workload dominated by basic get/set/delete operations
- ✅ Frequent move operations (movefirst, movelast, etc.)
- ❌ **Avoid if**: Heavy use of bulk operations or reverse iteration

## Recommendations

### Performance Best Practices

1. **Profile your actual workload** before choosing implementation:
   ```bash
   python -m odict.bench --sizes "1000,10000" --baseline odict
   ```

2. **Prefer odict over codict** unless you've confirmed codict is faster for your specific use case

3. **Avoid bulk operations in loops**:
   ```python
   # Slow with codict
   for i in range(1000):
       values = cd.values()  # Recreates list each time

   # Better
   values = cd.values()  # Cache once
   for i in range(1000):
       process(values)
   ```

4. **Use iteration methods for large datasets**:
   ```python
   # More efficient (avoids list creation)
   for key in cd:  # or cd.iterkeys()
       process(cd[key])

   # Less efficient
   for key in cd.keys():  # Creates intermediate list
       process(cd[key])
   ```

5. **Consider OrderedDict** as a middle ground:
   - Standard library (no dependencies)
   - Better performance than both odict for many operations
   - Lacks extended API but may not be needed

### Automatic Fallback Behavior

The package automatically imports `odict` if available, otherwise falls back to `odict`:

```python
# In __init__.py
try:
    from .codict import codict as odict
except ImportError:
    odict = odict.odict
```

**Recommendation**: Consider explicitly using `odict.odict` to get predictable performance characteristics:

```python
from odict.odict import odict  # Explicitly use pure Python version
```

## Future Optimization Opportunities

Potential improvements f:

1. **Optimize bulk operations**: Implement C-level fast paths for `values()`, `items()`
2. **Reduce conversion overhead**: Batch conversions, lazy evaluation
3. **Implement cpdef for Entry methods**: Requires architectural changes (see [Optimizations](../development/optimizations.md))
4. **Profile-guided optimization**: Focus on operations that actually benefit from Cython

However, fundamental trade-off remains: C↔Python conversion overhead may always limit codict's effectiveness for Python-object-heavy operations.

## Conclusion

`odict` demonstrates that **optimization doesn't automatically improve all operations**. The type conversion overhead between C and Python can dominate performance for operations that create or manipulate Python objects in bulk.

**Key Takeaway**: `odict` (pure Python) is generally the better default choice, with `odict` appropriate only for specific workloads dominated by basic operations and move operations.

Always benchmark your actual use case before assuming = faster.

## Related Documentation

- [Benchmarking Guide](benchmarking.md) - Run your own benchmarks
- [Architecture](architecture.md) - Implementation details
- [Memory Analysis](memory.md) - Memory characteristics
