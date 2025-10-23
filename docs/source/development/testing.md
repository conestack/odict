# Testing Documentation

## Test Suite Overview

**Total Tests**: 71 tests passing
- **codict tests**: 36 tests
- **odict tests**: 35 tests (compatibility verification)

**Test Framework**: pytest

**Test Files**:
- `tests/test_codict.py` - Codict-specific tests
- `tests/test_odict.py` - Original odict tests
- `test_pickle_codict.py` - Pickle serialization tests

## Running Tests

### Run All Tests

```bash
# Using make
make test

# Using pytest directly
pytest tests/ -v

# Run specific test file
pytest tests/test_codict.py -v
```

### Expected Output

```
tests/test_codict.py ....................................  [36/36] ✓
tests/test_odict.py ...................................   [35/35] ✓

============================== 71 passed in 0.04s ==============================
```

## Test Coverage

### Category 1: Basic Operations
- `test_init_with_dict` - Initialize from dict
- `test_init_with_items` - Initialize from list of tuples
- `test_init_with_kw` - Initialize with keyword arguments
- `test_getattr_setattr_subclass` - Attribute access on subclasses
- `test_get` - `get()` method with defaults
- `test_containment` - `in` operator
- `test_delete` - Item deletion
- `test_len` - Length operation
- `test_bool_expessions` - Boolean evaluation

### Category 2: Iteration Operations
- `test_reverse_iteration` - Reverse iteration
- `test_values` - Values access and iteration

### Category 3: Ordered Dict Specific
- `test_first_and_last_key` - First/last key access
- `test_next_key` - Navigate to next key
- `test_prev_key` - Navigate to previous key
- `test_firstkey` / `test_lastkey` - Method access
- `test_insertbefore` - Insert before reference key
- `test_insertafter` - Insert after reference key
- `test_insertfirst` - Insert at beginning
- `test_insertlast` - Insert at end
- `test_movebefore` - Move before reference
- `test_moveafter` - Move after reference
- `test_movefirst` - Move to beginning
- `test_movelast` - Move to end
- `test_swap` - Swap two keys
- `test_alter_key` - Rename key
- `test_sort` - Sort by keys

### Category 4: Modification Operations
- `test_clear` - Clear all items
- `test_copy` - Shallow copy
- `test_update` - Update from dict
- `test_update_with_kw` - Update with kwargs
- `test_setdefault` - Set default value
- `test_pop` - Pop with default
- `test_popitem` - Pop last item

### Category 5: Type Operations
- `test_casting` - Cast to list/dict
- `test_fromkeys` - Create from keys

### Category 6: Serialization
- `test_pickle` - Basic pickle
- `test_pickle_roundtrip` - Pickle/unpickle/use cycle

### Category 7: Other
- `test_repr` - Representation
- `test_str` - String conversion
- `test_abstract_superclass` - Inheritance behavior

## Pickle Tests

**File**: `test_pickle_codict.py`  
**Tests**: 8 comprehensive tests

### Test Functions

1. **test_node_pickle()** - Node objects pickle correctly
2. **test_simple_codict_pickle()** - Simple codict roundtrip
3. **test_complex_codict_pickle()** - Complex values (lists, dicts, tuples)
4. **test_empty_codict_pickle()** - Empty codict
5. **test_large_codict_pickle()** - 1,000 items
6. **test_codict_in_container()** - Codict inside list/dict
7. **test_pickle_protocol_versions()** - All protocols 0-5
8. **test_roundtrip_operations()** - Operations on unpickled codict

### Running Pickle Tests

```bash
python test_pickle_codict.py
```

### Expected Pickle Output

```
============================================================
Codict Pickle Serialization Tests
============================================================

Testing Node pickle...
✓ Node pickle works

Testing simple codict pickle...
✓ Simple codict pickle works

Testing complex codict pickle...
✓ Complex codict pickle works

Testing empty codict pickle...
✓ Empty codict pickle works

Testing large codict pickle...
✓ Large codict (1000 items) pickle works

Testing codict in containers...
✓ Codict in containers pickle works

Testing different pickle protocols...
  ✓ Protocol 0 works
  ✓ Protocol 1 works
  ✓ Protocol 2 works
  ✓ Protocol 3 works
  ✓ Protocol 4 works
  ✓ Protocol 5 works

Testing operations on unpickled codict...
✓ All operations work on unpickled codict

============================================================
✓ All pickle tests passed!
============================================================
```

## Test Structure

### Example Test

```python
def test_insertbefore(self):
    """Test insertbefore method."""
    cd = codict([('a', 1), ('b', 2), ('c', 3)])
    cd.insertbefore('b', 'new', 99)
    
    # Verify order
    self.assertEqual(cd.keys(), ['a', 'new', 'b', 'c'])
    
    # Verify value
    self.assertEqual(cd['new'], 99)
    
    # Verify other values unchanged
    self.assertEqual(cd['a'], 1)
    self.assertEqual(cd['b'], 2)
```

## Edge Cases Tested

### Empty Codict
- Operations on empty codict
- firstkey()/lastkey() raise ValueError
- Iteration over empty codict

### Single Element
- Single-element operations
- Move operations on single element
- Insert before/after single element

### Duplicate Keys
- Update existing key maintains position
- alter_key to existing key raises ValueError

### Boundary Conditions
- Insert at beginning/end
- Move first to first (no-op)
- Previous of first key
- Next of last key

## Continuous Integration

### GitHub Actions (if configured)

```yaml
name: Tests
on: [push, pull_request]
jobs:
  test:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v2
      - name: Set up Python
        uses: actions/setup-python@v2
        with:
          python-version: '3.12'
      - name: Install dependencies
        run: |
          pip install cython pytest
          python setup.py build_ext --inplace
      - name: Run tests
        run: pytest tests/ -v
```

## Test Maintenance

### Adding New Tests

1. Add test method to `test_codict.py`
2. Follow naming convention: `test_<feature>`
3. Include docstring
4. Test both success and failure cases
5. Verify with `pytest tests/test_codict.py -v`

### Test Best Practices

1. **Isolation**: Each test is independent
2. **Descriptive names**: Clearly indicate what's tested
3. **Assertions**: Multiple assertions to verify state
4. **Edge cases**: Test boundaries and errors
5. **Documentation**: Docstring explains purpose

## Troubleshooting Test Failures

### ImportError: cannot import codict

**Cause**: Extension not built

**Solution**:
```bash
make codict
pytest tests/test_codict.py -v
```

### Tests Pass Individually but Fail Together

**Cause**: Shared state between tests

**Solution**: Ensure each test creates its own codict instance

### Pickle Tests Fail

**Cause**: `__reduce__` implementation issue

**Solution**: Check that all state is preserved in pickle

## Test Metrics

- **Pass Rate**: 100% (71/71)
- **Execution Time**: ~0.04 seconds
- **Coverage**: All public methods tested
- **Pickle Protocols**: All 5 protocols verified

## Related Documentation

- [Development Notes](development.md) - Development methodology
- [Building](building.md) - Build before testing
- [API Reference](../user-guide/api-reference.md) - Methods tested
EOF
echo "Created testing.md"
