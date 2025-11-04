# Development Notes

## What Worked Well

### 1. `cdef class` Approach

**Decision**: Use extension types for Node class

**Benefits**:
- Provides C-level performance
- Maintains Python object model
- Easy to integrate with Python code
- Full pickle compatibility

**Example**:
```cython
cdef class Node:
    cdef public object prev_key
    cdef public object value
    cdef public object next_key
```

### 2. Node-Based Design

**Decision**: Separate Node class from dict logic

**Benefits**:
- Clean separation of concerns
- Easy to optimize Node independently
- Testable components
- Clear architecture

### 3. Incremental Testing

**Approach**: Test each method as implemented

**Benefits**:
- Caught issues early
- Prevented compound bugs
- Fast iteration cycle
- High confidence in code

### 4. Comprehensive Test Mirroring

**Approach**: Mirror all odict tests f

**Benefits**:
- Ensured 100% API compatibility
- Found edge cases
- Documented expected behavior
- Regression protection

### 5. Build System Integration

**Approach**: Integrate with existing Makefile via `include.mk`

**Benefits**:
- Seamless compilation
- No disruption to existing workflow
- Optional build (can disable)
- Clean separation

## Challenges Overcome

### 1. Syntax Constraints

**Challenge**: Cannot use `cdef` in regular Python classes

**Initial attempt**:
```python
class _codict(object):
    cdef object some_field  # ❌ Syntax error!
```

**Solution**: Use `cdef class Node` for C optimization, keep `_codict` as regular Python class

**Learning**: Understand Cython's type system limitations

### 2. Object Equality

**Challenge**: Initial tests failed - two identical codicts compared as unequal

**Root cause**: Python's default equality uses object identity, not value comparison

**Solution**: Implement `__eq__` and `__ne__` methods:
```python
def __eq__(self, other):
    if not isinstance(other, (_codict, dict)):
        return NotImplemented
    if len(self) != len(other):
        return False
    return self.items() == list(other.items())
```

**Learning**: Always implement equality for container types

### 3. Python 3.12 Compatibility

**Challenge**: `time.clock()` removed in Python 3.12

**Error**:
```python
AttributeError: module 'time' has no attribute 'clock'
```

**Solution**: Update bench.py to use `time.perf_counter()`

**Learning**: Stay current with Python deprecations

### 4. Module Import

**Challenge**: `ModuleNotFoundError` for during build

**Root cause**: Build dependencies not installed in correct order

**Solution**: 
1. Add `cython>=3.0` to `pyproject.toml` build requirements
2. Manually install when needed: `pip install cython`

**Learning**: Build dependencies must be explicit

## Lessons Learned

### 1. Extension Types are Ideal for Data Structures

**Why**:
- Heavy attribute access patterns
- Benefit from C-level performance
- Memory layout control
- Type safety at compile time

**Best use cases**:
- Tree nodes
- Linked list nodes
- Graph vertices
- Any structure with fixed fields accessed frequently

### 2. Memory Layout Matters

**Discovery**: 36% memory reduction from using `cdef class` vs. Python lists

**Impact**:
- Better cache utilization
- Faster allocation
- Lower memory pressure
- Improved performance

**Takeaway**: Profile memory usage, not just speed

### 3. Type Conversions Have Overhead

**Observation**: Some operations slower due to C↔Python conversions

**Examples**:
- Deletion: 7% slower (type conversions in cleanup)
- Object wrapping/unwrapping costs

**Mitigation**:
- Minimize conversions in hot paths
- Batch operations when possible
- Consider pure C paths for critical operations

### 4. Comprehensive Testing is Crucial

**Stats**: 71 tests (36 codict + 35 odict) caught numerous edge cases

**Examples caught by tests**:
- Empty codict behavior
- Single-element operations
- Reverse iteration edge cases
- Pickle roundtrip correctness

**Best practice**: Mirror tests from reference implementation

### 5. Pickle Compatibility Requires Careful Design

**Key insight**: `__reduce__` must preserve all state

**Implementation**:
```python
def __reduce__(self):
    return (
        self.__class__,
        (list(self.items()),),  # Preserves order!
        None
    )
```

**Testing**: All pickle protocols (0-5) must work

**Verification**: Roundtrip tests (pickle → unpickle → use)

## Development Methodology

### Phase 1: Planning
1. Analyze odict implementation
2. Design C-optimized Node structure
3. Plan architecture (class hierarchy)
4. Document in `plans/codict-implementation.md`

### Phase 2: Implementation
1. Create `cdef class Node`
2. Implement `_codict` base class
3. Mirror odict methods one-by-one
4. Test each method immediately

### Phase 3: Testing
1. Create test_codict.py
2. Mirror all test_odict.py tests
3. Add pickle-specific tests
4. Verify 100% pass rate

### Phase 4: Optimization
1. Profile performance
2. Create benchmarks
3. Investigate cpdef (not feasible)
4. Document findings

### Phase 5: Documentation
1. Write usage examples
2. Document API
3. Analyze performance
4. Create guides

## Best Practices Discovered

### 1. Start with Working Python, Then Cythonize

Don't optimize prematurely. Get it working in Python first, then identify hot spots.

### 2. Use `cdef class` for Data Containers

When you have a structure with fixed fields accessed frequently, `cdef class` is ideal.

### 3. Maintain API Compatibility

100% compatibility enables drop-in replacement. Worth the constraints.

### 4. Test Pickle Thoroughly

Pickle is complex. Test all protocols, nested structures, and roundtrips.

### 5. Document Architectural Constraints

Explain why certain optimizations (like cpdef) aren't possible. Saves future confusion.

### 6. Benchmark Across Scales

Performance characteristics change with scale. Test 1K, 10K, 100K, 1M.

### 7. Use Existing Build Systems

Integrate with existing infrastructure (Makefile, mx.ini) rather than creating new tools.

## Tools and Techniques

### Development Tools
- 3.0+ (language_level=3)
- pytest for testing
- tracemalloc for memory profiling
- time.perf_counter() for timing
- git for version control

### Debugging Cython
```bash
# Generate annotated HTML to see Python/C boundaries
cython -a src/odict/codict.pyx
# Open codict.html in browser
```

### Profiling
```python
import cProfile
import pstats

cProfile.run('benchmark_code()', 'profile.stats')
stats = pstats.Stats('profile.stats')
stats.sort_stats('cumulative')
stats.print_stats(20)
```

## Related Documentation

- [Testing](testing.md) - Test suite details
- [Building](building.md) - Build system
- [Optimizations](optimizations.md) - What we tried
- [Future Work](future-work.md) - Next steps
