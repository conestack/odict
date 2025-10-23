# Cython-based odict Implementation Plan

## Overview

This plan describes the implementation of a Cython-optimized version of `odict` using C structs with native C pointers instead of Python lists for the double-linked list structure. The implementation will maintain 100% API compatibility with the Python `odict` while providing significant performance improvements.

## Goals

1. Create a Cython-based ordered dictionary (`codict`) that matches all functionality of `pyodict`
2. Use C structs with native pointers for the internal double-linked list
3. Support pickle serialization/deserialization
4. Maintain identical API and behavior for drop-in compatibility
5. Provide comprehensive test coverage mirroring the Python implementation
6. Include benchmarks comparing performance against Python odict, dict, and OrderedDict

## Architecture

### C Struct Design

```cython
cdef struct Node:
    PyObject* prev_key  # Pointer to previous key (or NULL for _nil)
    PyObject* value     # Pointer to the stored value
    PyObject* next_key  # Pointer to next key (or NULL for _nil)
```

### Key Design Decisions

- **C Pointers vs Python Lists**: Replace `[prev_key, val, next_key]` lists with C structs
- **Memory Management**: Use `Py_INCREF`/`Py_DECREF` for proper reference counting
- **Nil Sentinel**: Reuse `_Nil` class from pyodict or create C-optimized version
- **Inheritance**: Mirror the `_odict` (abstract) and `odict` (concrete) pattern with `_codict` and `codict`
- **Import Path**: `from odict.codict import codict` (separate submodule)

## File Structure

### New Files

1. **src/odict/codict.pyx** (~600 lines)
   - Cython implementation file
   - C struct definitions
   - _codict abstract base class
   - codict concrete class

2. **tests/test_codict.py** (~650 lines)
   - Complete mirror of test_odict.py
   - Test class: `TestCodict(unittest.TestCase)`
   - Additional C struct pickle roundtrip tests

### Modified Files

3. **src/odict/bench.py**
   - Import codict
   - Add codict benchmark results
   - Add `odict : codict` performance comparison
   - Add `dict : codict` performance comparison

4. **pyproject.toml**
   - Add Cython to build dependencies
   - Configure Cython extension compilation

5. **Makefile**
   - Add Cython build targets
   - Add codict build to install process
   - Update clean targets for `.c`, `.so`, `build/` artifacts

## Implementation Details

### Methods to Implement (70+ total)

All methods from `_odict` class must be implemented in `_codict`:

**Core Dictionary Operations:**
- `__init__(data=(), **kwds)`
- `__getitem__(key)`
- `__setitem__(key, val)`
- `__delitem__(key)`
- `__contains__(key)`
- `__len__()`
- `__str__()`
- `__repr__()`
- `__iter__()`
- `__reversed__()`

**Property Accessors:**
- `lh` (property) - first key
- `lt` (property) - last key
- `first_key` (property)
- `last_key` (property)
- `firstkey()` - method version
- `lastkey()` - method version

**Iteration Methods:**
- `iterkeys()` / `__iter__()`
- `itervalues()`
- `iteritems()`
- `keys()`
- `values()`
- `items()`
- `riterkeys()` / `__reversed__()`
- `ritervalues()`
- `riteritems()`
- `rkeys()`
- `rvalues()`
- `ritems()`

**Manipulation Methods:**
- `get(k, x=None)`
- `has_key(key)`
- `clear()`
- `copy()`
- `update(data=(), **kwds)`
- `setdefault(key, default=None)`
- `pop(key, default=_nil)`
- `popitem()`
- `sort(cmp=None, key=None, reverse=False)`

**Key Modification:**
- `alter_key(old_key, new_key)`

**Positional Operations:**
- `insertbefore(ref, key, value)`
- `insertafter(ref, key, value)`
- `insertfirst(key, value)`
- `insertlast(key, value)`
- `movebefore(ref, key)`
- `moveafter(ref, key)`
- `movefirst(key)`
- `movelast(key)`
- `swap(a, b)`

**Navigation:**
- `next_key(key)`
- `prev_key(key)`

**Conversion:**
- `as_dict()`

**Copy Operations:**
- `__copy__()`
- `__deepcopy__(memo)`

**Internal/Debug:**
- `_repr()`
- `_dict_impl()` - returns dict class
- `_list_factory()` - not needed for C implementation but kept for compatibility

### Pickle Support

**Strategy:**
```python
def __reduce__(self):
    # Return constructor and items list
    return (self.__class__, (list(self.items()),))

def __setstate__(self, state):
    # Reconstruct from items
    pass
```

The C structs are transparent to pickle - we serialize the logical state (key-value pairs) and reconstruct the C structures upon deserialization.

### Memory Management

**Critical Points:**
- **Allocation**: When creating a new Node struct, use `Py_INCREF` on all PyObject* references
- **Modification**: When changing a reference, `Py_DECREF` the old value and `Py_INCREF` the new value
- **Deletion**: When removing a node, `Py_DECREF` all three PyObject* references
- **Cleanup**: Implement `__dealloc__` to properly clean up all C-allocated memory

**Example Pattern:**
```cython
cdef Node* node = <Node*>malloc(sizeof(Node))
Py_INCREF(<object>prev_key)
Py_INCREF(<object>value)
Py_INCREF(<object>next_key)
node.prev_key = <PyObject*>prev_key
node.value = <PyObject*>value
node.next_key = <PyObject*>next_key
```

### Method Visibility

- `cdef` - C-only methods (internal helpers)
- `cpdef` - Callable from both Python and C (performance-critical public methods)
- `def` - Python methods (standard public API)

## Test Strategy

### test_codict.py Structure

Mirror every test from test_odict.py:

```python
from odict.codict import codict, _codict
import unittest

class TestCodict(unittest.TestCase):
    def test_abstract_superclass(self): ...
    def test_init_with_kw(self): ...
    def test_init_with_dict(self): ...
    # ... all 40+ test methods from test_odict.py
```

**Additional Tests:**
- `test_c_struct_pickle_roundtrip()` - Verify C structs survive pickle
- `test_memory_cleanup()` - Verify no memory leaks (if possible)

### Test Execution

```bash
# Run just codict tests
venv/bin/pytest tests/test_codict.py

# Run all tests
make test

# Verify coverage includes compiled extension
make coverage
```

## Benchmark Extensions

### bench.py Additions

```python
from odict.codict import codict

# Add codict benchmarking
head('adding and deleting ``codict`` objects')
print(CREATE_DELETE_ROW)
codict_results = {
    1000: result(codict, 1000),
    10000: result(codict, 10000),
    100000: result(codict, 100000),
    1000000: result(codict, 1000000),
}

# Comparison: odict vs codict
head('relation ``odict : codict``')
print(RELATION_ROW)
for key, value in odict_results.items():
    ostart, omid, oend = value
    cstart, cmid, cend = codict_results[key]
    relation_create = (omid - ostart) / (cmid - cstart)
    relation_delete = (oend - omid) / (cend - cmid)
    relation_row('creating', key, relation_create)
    relation_row('deleting', key, relation_delete)

# Comparison: dict vs codict
head('relation ``dict : codict``')
# Similar to above
```

## Build Configuration

### pyproject.toml Changes

```toml
[build-system]
requires = ["hatchling", "cython"]
build-backend = "hatchling.build"

[tool.hatch.build.targets.wheel]
packages = ["src/odict"]

# Cython compilation configuration
[tool.cython]
language_level = 3
```

### Makefile Changes

Add new targets:

```makefile
# Cython build target
CODICT_TARGET:=$(SENTINEL_FOLDER)/codict.sentinel
$(CODICT_TARGET): $(PACKAGES_TARGET)
	@echo "Building Cython extension"
	@$(MXENV_PYTHON) setup.py build_ext --inplace
	@touch $(CODICT_TARGET)

.PHONY: codict
codict: $(CODICT_TARGET)

.PHONY: codict-clean
codict-clean:
	@rm -f src/odict/*.c
	@rm -f src/odict/*.so
	@rm -rf build/
	@rm -f $(CODICT_TARGET)

# Add to install targets
INSTALL_TARGETS+=$(CODICT_TARGET)

# Add to clean targets
CLEAN_TARGETS+=codict-clean
```

## Performance Expectations

Based on using C structs with native pointers instead of Python lists:

- **Creation**: 2-5x faster (reduced Python object overhead)
- **Deletion**: 2-5x faster (direct pointer manipulation)
- **Iteration**: 1.5-3x faster (C-level pointer traversal)
- **Memory**: ~30% less memory (C struct vs Python list)

## Implementation Risks & Mitigation

### Risks

1. **Memory Leaks**: Improper reference counting
   - Mitigation: Careful use of Py_INCREF/Py_DECREF, valgrind testing

2. **Pickle Compatibility**: C structs don't pickle directly
   - Mitigation: Custom __reduce__/__setstate__ methods

3. **Build Complexity**: Cython adds build dependencies
   - Mitigation: Clear build documentation, fallback to pyodict if build fails

4. **Platform Compatibility**: C extensions may have platform-specific issues
   - Mitigation: Test on Linux/macOS/Windows in CI

## Success Criteria

- [ ] All 40+ test methods pass for codict
- [ ] Pickle/unpickle works correctly
- [ ] Performance improvements demonstrated in benchmarks
- [ ] No memory leaks detected
- [ ] Builds successfully on CI (Linux/macOS/Windows)
- [ ] 100% API compatibility with pyodict
- [ ] Documentation updated

## Migration Path

Users can opt-in to the Cython version:

```python
# Use Python version (always works)
from odict import odict

# Use Cython version (faster, requires compilation)
from odict.codict import codict

# Try Cython, fallback to Python
try:
    from odict.codict import codict as odict
except ImportError:
    from odict import odict
```

## Future Enhancements

1. **Hybrid Approach**: Automatic fallback from codict to odict if Cython unavailable
2. **Additional Optimizations**: Use C arrays for small odicts
3. **Type Specializations**: Specialized versions for common key/value types
4. **Parallel Operations**: Thread-safe variants for concurrent access

## References

- Cython Documentation: https://cython.readthedocs.io/
- Python C API Reference Counting: https://docs.python.org/3/c-api/refcounting.html
- PyObject* Management: https://docs.python.org/3/c-api/structures.html
