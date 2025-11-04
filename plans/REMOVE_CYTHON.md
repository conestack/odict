# Plan: Remove Cython Implementation from odict (Version 2.0)

**Branch**: `2.0`
**Goal**: Remove all Cython/codict implementation and references, keeping only the pure Python odict implementation.

## Overview

After experimentation with Cythonizing parts of odict showed no performance benefit, and refactoring the pure Python implementation yielded improvements, we're removing the Cython implementation. This branch will serve as a reference for the experimental work while moving forward with the optimized pure Python implementation.

---

## Phase 1: Git Branch & Core Files

1. **Create new branch `2.0`** from current `codict` branch
2. **Delete** `src/odict/codict.pyx` (Cython source file - 114 lines)
3. **Delete** `include.mk` (codict build targets - 28 lines)
4. **Run** `make clean` to remove compiled artifacts and build files

---

## Phase 2: Build Configuration

5. **Update** `pyproject.toml`:
   - Remove `hatch-cython` from `build-requires`
   - Delete entire `[tool.hatch.build.targets.wheel.hooks.cython]` section

6. **Update** `src/odict/__init__.py`:
   - Simplify import to directly use pure Python odict
   - Remove try/except codict import logic
   - Change from:
     ```python
     try:
         from .codict import codict as odict  # noqa
     except ImportError:
         odict = odict.odict  # noqa
     ```
   - To:
     ```python
     odict = odict.odict
     ```

7. **Update** `src/odict/odict.py`:
   - Remove codict mention from module docstring (line 5)

---

## Phase 3: Tests

8. **Update** `tests/conftest.py`:
   - Remove `from odict.codict import codict, _codict, Entry` (line 6)
   - Remove codict from parametrization - keep only odict implementation
   - Update docstrings to remove codict mentions

9. **Update** `tests/test_representation.py`:
   - Remove `'codict()'` from expected repr values (lines 16-17, 23-24, 28-29, 31-32)

10. **Update** `tests/test_edge_cases.py`:
    - Remove codict-specific conditionals (lines 90, 94-96)

11. **Update** `tests/test_serialization.py`:
    - Delete `test_entry_pickle` function entirely (lines 151-164)

12. **Update** `tests/test_initialization.py`:
    - Update comments to remove `_codict` mentions (lines 10, 14)

13. **Run** `make test` to verify all tests pass

---

## Phase 4: Benchmarks

14. **Update** `src/odict/bench.py`:
    - Remove codict import and `HAS_CODICT` flag (lines 9, 22-26)
    - Remove codict from `implementations` dict (line 69)
    - Remove `'codict'` from implementation order (line 234)
    - Remove codict from implementation lists (lines 1153, 1191, 1354, 1395)
    - Update all comments mentioning "odict/codict only"
    - Update help text and argument choices to remove codict references

---

## Phase 5: Documentation Updates

### Core Documentation

15. **Update** `README.md`:
    - Remove "Cython-optimized version (codict)" from features (line 11)
    - Remove "codict is used transparently" (line 12)
    - Remove installation fallback mention (line 23)
    - Delete entire "Cython Optimization (codict)" section (lines 70-77)
    - Remove `odict.__module__` codict example (line 85)
    - Remove "Transparent optimization" from features (line 146)

16. **Update** `CLAUDE.md`:
    - Remove `codict.pyx` from directory structure (line 14)
    - Remove Entry class mention (line 88)
    - Remove codict implementation description (lines 94-96)
    - Update test parametrization note (line 117)

### User Guide Documentation

17. **Major revision** of `docs/source/user-guide/installation.md` (318 lines):
    - Remove C compiler and Cython prerequisites (lines 6-7)
    - Remove "Installation with Cython extension" section (lines 10, 24-48)
    - Remove build options for codict (lines 55-85)
    - Remove build system configuration (lines 87-133)
    - Remove codict verification instructions (lines 138-165)
    - Remove troubleshooting codict builds (lines 187-232)
    - Remove codict build artifacts section (lines 246-271)
    - Remove performance considerations for codict (lines 289-305)
    - Simplify to pure Python installation only

18. **Delete or rewrite** `docs/source/user-guide/overview.md`:
    - Currently entirely about codict overview (100+ lines)
    - Either delete or rewrite for pure Python odict overview

### Technical Documentation

19. **Update** remaining documentation files:
    - `docs/source/user-guide/usage.md` - Remove codict usage examples
    - `docs/source/user-guide/api-reference.md` - Remove codict API references
    - `docs/source/technical/architecture.md` - Revise to document odict architecture only
    - `docs/source/technical/benchmarking.md` - Remove codict benchmarking
    - `docs/source/technical/memory.md` - Remove codict memory analysis
    - `docs/source/technical/performance.md` - Remove codict performance comparisons
    - `docs/source/development/building.md` - Remove Cython build instructions
    - `docs/source/development/development.md` - Remove codict development workflow
    - `docs/source/development/testing.md` - Remove codict test parametrization details
    - `docs/source/development/future-work.md` - Update future work section
    - `docs/source/development/optimizations.md` - Document pure Python optimizations

20. **Update** `plans/OPTIMIZATION_PLAN.md`:
    - Remove or update any codict-related optimization notes

---

## Phase 6: Verification & Testing

21. **Clean rebuild**: `make clean && make install`
    - Verify installation completes without Cython dependencies
    - Ensure no .c, .so, .pyd files are generated

22. **Run tests**: `make test`
    - Ensure 100% pass rate with only odict implementation

23. **Run coverage**: `make coverage`
    - Ensure 100% coverage maintained on `src/odict`

24. **Build documentation**: `cd docs && make html`
    - Verify no broken links or missing references
    - Check that all codict mentions are removed

25. **Test benchmarks**: `venv/bin/python -m odict.bench --mode comprehensive`
    - Verify benchmarks run with odict, OrderedDict, and dict only
    - Ensure no codict import errors

---

## Files Affected Summary

### Deleted Files (2)
- `src/odict/codict.pyx`
- `include.mk`

### Core Implementation (3)
- `src/odict/__init__.py`
- `src/odict/odict.py`
- `src/odict/bench.py`

### Build Configuration (1)
- `pyproject.toml`

### Tests (5)
- `tests/conftest.py`
- `tests/test_representation.py`
- `tests/test_edge_cases.py`
- `tests/test_serialization.py`
- `tests/test_initialization.py`

### Documentation (20+)
- `README.md`
- `CLAUDE.md`
- `docs/source/user-guide/installation.md`
- `docs/source/user-guide/overview.md`
- `docs/source/user-guide/usage.md`
- `docs/source/user-guide/api-reference.md`
- `docs/source/technical/architecture.md`
- `docs/source/technical/benchmarking.md`
- `docs/source/technical/memory.md`
- `docs/source/technical/performance.md`
- `docs/source/development/building.md`
- `docs/source/development/development.md`
- `docs/source/development/testing.md`
- `docs/source/development/future-work.md`
- `docs/source/development/optimizations.md`
- `plans/OPTIMIZATION_PLAN.md`

---

## Expected Outcome

**Version 2.0** will contain:
- Pure Python odict implementation only
- No Cython dependencies or build configuration
- Simplified installation (no C compiler required)
- Streamlined tests (single implementation)
- Updated documentation reflecting pure Python approach
- Benchmarks comparing odict vs stdlib (OrderedDict, dict)

**Benefits**:
- Simpler maintenance
- Easier installation for users
- No compiler dependency
- Clearer codebase
- Preserved reference to experimental Cython work in git history

---

## Checklist

- [ ] Phase 1: Git branch and core file deletion
- [ ] Phase 2: Build configuration updates
- [ ] Phase 3: Test updates and verification
- [ ] Phase 4: Benchmark updates
- [ ] Phase 5: Documentation updates (20+ files)
- [ ] Phase 6: Full verification suite
- [ ] Final review: No codict references remain
- [ ] Final review: All tests pass
- [ ] Final review: Documentation builds cleanly
- [ ] Final review: Benchmarks run successfully
