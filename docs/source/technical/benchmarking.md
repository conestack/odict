# Benchmarking Guide

## Overview

The `bench.py` module provides comprehensive performance and memory benchmarking for **all 50+ public API methods** across four implementations:
- `dict` (Python built-in)
- `OrderedDict` (collections.OrderedDict)
- `odict` (Pure Python implementation)
- `odict` (implementation)

The benchmarking suite supports **configurable baseline comparison** and is fully parameterizable via command-line arguments.

## Quick Start

### Run Full Benchmark Suite

```bash
# Run comprehensive benchmarks with default settings
python -m odict.bench

# Or from within the virtual environment
venv/bin/python -m odict.bench
```

**Note**: Full benchmark takes ~10-30 minutes depending on your system, as it tests 50+ methods across multiple sizes and 4 implementations.

### Run Micro-Benchmarks Only

```bash
# Run only micro-benchmarks (single operation timing)
python -m odict.bench --mode micro
```

### Custom Configuration

```bash
# Custom sizes
python -m odict.bench --sizes "100,1000,10000"

# Custom iteration counts
python -m odict.bench --micro-iterations 50000 --macro-iterations 5000

# Different baseline for comparison
python -m odict.bench --baseline dict

# Combine options
python -m odict.bench --mode comprehensive --sizes "1000,10000" --baseline fastest
```

## Command-Line Arguments

### --mode

**Choices**: `comprehensive` (default), `micro`

- **comprehensive**: Run all benchmark categories (basic ops, iteration, ordered dict methods)
- **micro**: Run micro-benchmarks only (fine-grained single-operation timing)

```bash
python -m odict.bench --mode micro
```

### --sizes

**Format**: Comma-separated list of integers
**Default**: `1000,10000,100000,1000000`

Specify which dict sizes to benchmark. Smaller sizes run faster but may not reveal scalability issues.

```bash
# Quick test with small sizes
python -m odict.bench --sizes "100,1000"

# Test large dictionaries
python -m odict.bench --sizes "10000,100000,1000000"
```

### --micro-iterations

**Type**: Integer
**Default**: `10000`

Number of iterations for micro-benchmarks (single operation timing). Higher values give more accurate results but take longer.

```bash
python -m odict.bench --micro-iterations 50000
```

### --macro-iterations

**Type**: Integer
**Default**: `1000`

Number of iterations for macro-benchmarks (bulk operations). Typically lower than micro-iterations since bulk ops are slower.

```bash
python -m odict.bench --macro-iterations 5000
```

### --baseline

**Choices**: `fastest` (default), `dict`, `OrderedDict`, `odict`, `odict`, `none`

Select which implementation to use as the baseline for percentage comparisons.

```bash
# Compare all implementations to fastest
python -m odict.bench --baseline fastest

# Compare all to standard dict
python -m odict.bench --baseline dict

# Compare all to odict
python -m odict.bench --baseline odict

# No baseline comparison (absolute times only)
python -m odict.bench --baseline none
```

**Baseline selection behavior**:
- `fastest`: Automatically selects the fastest implementation for each operation/size
- Specific implementation: Always compares to that implementation
- `none`: Shows absolute times with no percentage comparisons

## Output Format

### Comprehensive Mode

Each method gets its own table showing performance across all sizes and implementations:

```
==============================================================================================================
Method: __getitem__
Description: Access item by key: d['key']
==============================================================================================================

--- Size: 1,000 objects ---
Implementation  | Time (ms)    | vs fastest   | Memory (KB)  | vs fastest
--------------------------------------------------------------------------------------------------------------
dict ★          |     22.126ms | -            |      0.156KB | -
OrderedDict     |     22.834ms |    +3.2%     |      0.133KB |   -14.7%
odict           |     85.835ms |  +287.8%     |      0.133KB |   -14.7%
codict          |     82.426ms |  +272.5%     |      0.133KB |   -14.7%
```

**Table Legend**:
- **★**: Marks the baseline implementation for this operation/size
- **Time (ms)**: Total time in milliseconds for all iterations
- **vs baseline**: Percentage difference compared to baseline
  - Negative % = faster/less memory (better)
  - Positive % = slower/more memory (worse)
- **Memory (KB)**: Memory delta in kilobytes
- **N/A**: Method not available on that implementation

### Summary Output

After all benchmarks complete, a summary shows overall performance:

```
==============================================================================================================
BENCHMARK SUMMARY
==============================================================================================================

Overall Performance Summary:
Implementation  | Wins     | Win Rate   | Avg Time
------------------------------------------------------------
dict            | 48       |    88.9% |     82.648ms
OrderedDict     | 6        |    11.1% |    166.618ms
odict           | 55       |    38.2% |   1394.861ms
codict          | 35       |    24.3% |   2851.733ms
```

**Summary Metrics**:
- **Wins**: Number of operations where this implementation was fastest
- **Win Rate**: Percentage of all benchmarks won
- **Avg Time**: Average time across all benchmarks

## Benchmark Categories

### Category 1: Basic Dictionary Operations

**17 methods**: Core dict operations that all implementations support

- `__getitem__`, `__setitem__`, `__delitem__`, `__contains__`, `__len__`
- `get()`, `keys()`, `values()`, `items()`
- `clear()`, `copy()`, `update()`, `setdefault()`
- `pop()`, `popitem()`, `fromkeys()`
- `has_key()` (odict/codict only)

### Category 2: Iteration Operations

**11 methods**: Iteration and reverse iteration

- `__iter__`, `__reversed__`
- `iterkeys()`, `itervalues()`, `iteritems()`
- `riterkeys()`, `ritervalues()`, `riteritems()` (odict/codict only)
- `rkeys()`, `rvalues()`, `ritems()` (odict/codict only)

### Category 3: Ordered Dict Specific Operations

**22 methods**: Extended API for order manipulation (odict/codict only)

- **Access**: `first_key`, `last_key`, `next_key()`, `prev_key()`
- **Modification**: `sort()`, `alter_key()`, `swap()`
- **Insertion**: `insertbefore()`, `insertafter()`, `insertfirst()`, `insertlast()`
- **Movement**: `movebefore()`, `moveafter()`, `movefirst()`, `movelast()`
- **Other**: `as_dict()`, `lh`, `lt`

## Programmatic Usage

### Custom Benchmark Script

```python
from odict.bench import BenchmarkRunner

# Create runner with custom config
config = {
    'sizes': [1000, 10000],
    'micro_iterations': 5000,
    'macro_iterations': 1000,
    'baseline': 'fastest'
}

runner = BenchmarkRunner(config=config)

# Run comprehensive benchmarks
runner.run_comprehensive()

# Or run micro-benchmarks only
runner.run_micro()

# Access results
for (impl, size), metrics in runner.results.items():
    print(f"{impl} at size {size}: {metrics['time_ms']}ms")
```

### Running Individual Benchmarks

```python
from odict.bench import BenchmarkRunner, setup_populated, test_getitem

runner = BenchmarkRunner()

# Run a single benchmark
runner.benchmark_and_print(
    method_name='__getitem__',
    setup_func=setup_populated,
    test_func=test_getitem,
    description="Access item by key: d['key']"
)
```

## Performance Analysis Tips

### Identifying Performance Characteristics

1. **Basic Operations (get/set/delete)**:
   - Compare `dict`, `OrderedDict`, `odict`, `odict` for `__getitem__`, `__setitem__`, `__delitem__`
   - Expected: `dict` fastest, ordered implementations 2-5x slower

2. **Bulk Operations (values/items/copy)**:
   - Check `values()`, `items()`, `copy()` benchmarks
   - Note: `odict` may be significantly slower due to C↔Python conversion overhead

3. **Order-Specific Operations**:
   - Compare `odict` vs `odict` for `movefirst()`, `movelast()`, `swap()`, etc.
   - Note: `odict` is typically competitive or slightly faster for these

4. **Memory Usage**:
   - Compare memory columns across implementations
   - `OrderedDict` and `odict` generally use less memory than `odict`

### Understanding Baseline Selection

**Use `--baseline fastest`** (default) when:
- Comparing all implementations objectively
- Identifying the best implementation for each operation
- Generating neutral performance reports

**Use `--baseline odict`** when:
- Evaluating `odict` optimization effectiveness
- Measuring improvement over pure Python implementation
- Documentation and release notes

**Use `--baseline dict`** when:
- Understanding ordering overhead
- Comparing to standard library baseline
- Evaluating if ordered dict is worth the performance cost

## Interpreting Results

### Codict Performance Characteristics

Based on benchmark data, `odict` exhibits:

**Strengths**:
- Competitive with `odict` for basic operations (`__getitem__`, `__setitem__`)
- Slightly faster for move operations (`movefirst`, `movelast`, `moveafter`)
- Similar memory usage to `odict`

**Weaknesses**:
- **Significantly slower** for bulk operations: `values()`, `items()`, `copy()`
- **10-50x slower** for reverse iteration methods
- Type conversion overhead impacts Python object creation

### When to Use Each Implementation

**Use `dict`** when:
- Maximum performance needed
- Order maintenance not required (or Python 3.7+ insertion order sufficient)
- No need for order manipulation methods

**Use `OrderedDict`** when:
- Need standard library solution
- Basic ordered dict functionality sufficient
- Good balance of performance and features

**Use `odict`** when:
- Need extended API (move, swap, insertbefore, etc.)
- Frequent bulk operations (`values()`, `items()`)
- Pure Python portability required

**Use `odict`** when:
- Need extended API
- Workload dominated by basic operations and move operations
- Few bulk operations or reverse iterations

## Benchmarking Best Practices

### Accurate Measurements

1. **Disable CPU frequency scaling**: Use `cpupower` or similar to set performance governor
2. **Close background applications**: Minimize system load during benchmarks
3. **Run multiple times**: Benchmark variance can be significant; average multiple runs
4. **Warm-up iterations**: First run may include compilation overhead

### Interpreting Variance

- **<5% difference**: Likely within measurement noise
- **5-20% difference**: Noticeable but may vary by workload
- **>20% difference**: Significant performance difference

### System Dependencies

Performance characteristics depend on:
- **CPU architecture**: x86_64 vs ARM
- **Python version**: CPython 3.10 vs 3.11 vs 3.14
- **Memory hierarchy**: Cache size, memory speed
- **Compilation**: GCC vs Clang vs MSVC

Always benchmark on your target deployment environment.

## Related Documentation

- [Performance Analysis](performance.md) - Detailed performance discussion
- [Architecture](architecture.md) - Implementation details
- [Memory Analysis](memory.md) - Memory usage breakdown
