# Benchmarking Guide

## Overview

The refactored `bench.py` provides comprehensive performance and memory benchmarking for **all 50+ public API methods** across four implementations:
- `dict` (Python built-in)
- `OrderedDict` (collections.OrderedDict)
- `odict` (Python implementation)
- `codict` (Cython-optimized implementation)

## Quick Start

### Run Full Benchmark Suite

```bash
python3 -m odict.bench
```

**Note**: Full benchmark takes ~10-30 minutes depending on your system, as it tests 50+ methods across 4 sizes (1K, 10K, 100K, 1M objects) and 4 implementations.

### Run Specific Benchmarks

```python
from odict.bench import BenchmarkRunner, setup_populated, test_getitem
import odict.bench as bench

# Test with smaller sizes for faster results
bench.SIZES = [1000, 10000]

runner = BenchmarkRunner()
runner.benchmark_and_print('__getitem__', setup_populated, test_getitem,
                           description="Access item by key: d['key']")
```

## Output Format

Each method gets its own comprehensive table:

```
==============================================================================================================
Method: __getitem__
Description: Access item by key: d['key']
==============================================================================================================

--- Size: 1,000 objects ---
Implementation  | Time (ms)    | vs odict     | Memory (KB)  | vs odict
--------------------------------------------------------------------------------------------------------------
dict            |     22.126ms |   -74.2%     |      0.156KB |   +17.6%
OrderedDict     |     22.834ms |   -73.4%     |      0.133KB |    +0.0%
odict           |     85.835ms | -            |      0.133KB | -
codict          |     93.490ms |    +8.9%     |      0.133KB |    +0.0%

--- Size: 10,000 objects ---
[... similar table ...]
```

### Reading the Results

- **Time (ms)**: Total time in milliseconds for all iterations
- **vs odict**: Percentage difference compared to odict baseline
  - Negative % = **faster/less memory** than odict (good for codict!)
  - Positive % = slower/more memory than odict
- **Memory (KB)**: Memory delta in kilobytes
- **N/A**: Method not available on that implementation

## Benchmark Categories

### Category 1: Basic Dictionary Operations (17 methods)
- `__getitem__`, `__setitem__`, `__delitem__`, `__contains__`, `__len__`
- `get()`, `has_key()`, `keys()`, `values()`, `items()`
- `clear()`, `copy()`, `update()`, `setdefault()`
- `pop()`, `popitem()`, `fromkeys()`

### Category 2: Iteration Operations (11 methods)
- `__iter__`, `__reversed__`
- `iterkeys()`, `itervalues()`, `iteritems()`
- `riterkeys()`, `ritervalues()`, `riteritems()`
- `rkeys()`, `rvalues()`, `ritems()`

### Category 3: Ordered Dict Specific (22 methods)
- **Access**: `firstkey()`, `lastkey()`, `first_key`, `last_key`, `next_key()`, `prev_key()`
- **Modification**: `sort()`, `alter_key()`, `swap()`
- **Insertion**: `insertbefore()`, `insertafter()`, `insertfirst()`, `insertlast()`
- **Movement**: `movebefore()`, `moveafter()`, `movefirst()`, `movelast()`
- **Other**: `as_dict()`, `lh`, `lt`

## Configuration

Edit `bench.py` to customize:

```python
# Test sizes (default: [1000, 10000, 100000, 1000000])
SIZES = [1000, 10000, 100000, 1000000]

# Number of iterations for fast operations (default: 10000)
MICRO_ITERATIONS = 10000

# Number of iterations for slow operations (default: 1000)
MACRO_ITERATIONS = 1000
```

## Performance Tips

### For Faster Results

1. **Reduce sizes**: Use smaller SIZES list
   ```python
   bench.SIZES = [1000, 10000]  # Only test small sizes
   ```

2. **Reduce iterations**: Lower iteration counts
   ```python
   bench.MICRO_ITERATIONS = 1000
   bench.MACRO_ITERATIONS = 100
   ```

3. **Test specific methods**: Run individual benchmarks instead of full suite

### For More Accurate Results

1. **Increase iterations**: More iterations = more stable results
2. **Close other applications**: Reduce system noise
3. **Run multiple times**: Average results across multiple runs
4. **Use larger sizes**: Better representation of real-world usage

## Memory Measurement

Memory usage is measured using Python's `tracemalloc` module:
- Measures **memory delta** (change before/after operation)
- Garbage collection forced before each measurement
- Results show per-operation memory footprint
- Negative memory values possible (garbage collection during test)

## Summary Statistics

At the end of the full benchmark, you'll see:

```
==============================================================================================================
BENCHMARK SUMMARY
==============================================================================================================

Codict vs Odict Performance:
  Methods tested: 180
  Codict faster: 120 times
  Codict slower: 60 times
  Average speedup: +12.3%
  Best speedup: +93.9%
  Worst speedup: -15.2%
```

## Example: Benchmarking Custom Methods

```python
from odict.bench import BenchmarkRunner

def my_setup(impl_class, size):
    """Custom setup function"""
    return impl_class([(f"key_{i}", i) for i in range(size)])

def my_test(obj, size, iterations):
    """Custom test function"""
    for _ in range(iterations):
        # Your operation here
        for key in list(obj.keys())[:10]:
            _ = obj[key]

runner = BenchmarkRunner()
runner.benchmark_and_print('custom_operation', my_setup, my_test,
                           iterations=1000,
                           description="My custom benchmark")
```

## Interpreting Results

### What to Look For

1. **dict Performance**: Usually fastest for non-ordered operations (expected)
2. **codict vs odict**: Look for negative % in "vs odict" column
   - Negative = codict is faster/more memory efficient
   - Typical range: -20% to +10%
3. **OrderedDict Comparison**: codict should be competitive or faster
4. **Memory Usage**: codict typically uses less memory due to C-optimized Node class

### Known Performance Characteristics

**codict Strengths**:
- Creation operations (15-38% faster)
- Memory footprint (36% less per node)
- Read operations (competitive or faster)

**codict Weaknesses**:
- Some deletion operations (7% slower due to type conversion overhead)
- Very small dictionaries (<100 items) may not show benefits

## Troubleshooting

### Benchmark Takes Too Long

- Reduce SIZES: `bench.SIZES = [1000, 10000]`
- Reduce iterations
- Run specific methods instead of full suite

### Memory Errors with Large Sizes

- Use smaller SIZES
- Close other applications
- The 1M object tests require ~500MB RAM

### Inconsistent Results

- Run multiple times and average
- Ensure system is idle
- Increase iterations for more stable results

## Files

- `src/odict/bench.py` - Main benchmark suite (846 lines)
- `PERFORMANCE_ANALYSIS.md` - Detailed performance analysis
- `CPDEF_ANALYSIS.md` - cpdef optimization investigation
- `benchmark_cpdef.py` - Micro-benchmark tool

## See Also

- [Overview](../user-guide/overview.md) - Complete codict implementation summary
- [Performance Analysis](performance.md) - Detailed performance analysis
- [Optimizations](../development/optimizations.md) - cpdef optimization findings
