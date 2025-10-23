# Installation Guide

## Prerequisites

- Python 3.7 or later
- C compiler (gcc, clang, or MSVC)
- Cython 3.0 or later
- make (for Makefile-based builds)

## Quick Start

### Full Installation

```bash
# Clone or navigate to odict directory
cd odict/

# Build and install everything (includes codict extension)
make install

# Verify installation
python3 -c "from odict.codict import codict; print('codict installed successfully')"
```

## Build Options

### Option 1: Using Makefile (Recommended)

```bash
# Build only the codict extension
make codict

# Clean build artifacts
make codict-clean

# Full install (creates venv, installs packages, builds codict)
make install

# Run tests
make test
```

### Option 2: Using setup.py Directly

```bash
# Build codict extension in-place
python setup.py build_ext --inplace

# This creates src/odict/codict.*.so file
```

### Option 3: Using pip (Development Install)

```bash
# Install in development mode with Cython dependency
pip install -e .

# Build the extension
python setup.py build_ext --inplace
```

## Build System Configuration

### pyproject.toml

The project uses `hatchling` as the build backend with Cython as a build dependency:

```toml
[build-system]
requires = ["hatchling", "cython>=3.0"]
build-backend = "hatchling.build"
```

### setup.py

Defines the Cython extension configuration:

```python
from setuptools import Extension
from Cython.Build import cythonize

extensions = [
    Extension(
        "odict.codict",
        ["src/odict/codict.pyx"],
        language_level=3,
    )
]

setup(
    ext_modules=cythonize(extensions, compiler_directives={'embedsignature': True})
)
```

### include.mk

Custom Makefile targets for codict build:

```makefile
CODICT_TARGET:=$(SENTINEL_FOLDER)/codict.sentinel

$(CODICT_TARGET): $(PACKAGES_TARGET)
ifeq ("$(BUILD_CODICT)", "true")
    @echo "Building Cython codict extension"
    @$(MXENV_PYTHON) setup.py build_ext --inplace
    @touch $(CODICT_TARGET)
endif
```

## Verifying Installation

### Check Extension is Loaded

```python
from odict.codict import codict
import sys

# Check if codict is the Cython version
print(f"codict module: {codict.__module__}")
print(f"codict file: {sys.modules['odict.codict'].__file__}")

# Should show .so or .pyd extension file
```

### Run Quick Test

```python
from odict.codict import codict

# Create a simple codict
cd = codict([('a', 1), ('b', 2), ('c', 3)])

# Test basic operations
assert cd.keys() == ['a', 'b', 'c']
assert cd['a'] == 1
assert cd.firstkey() == 'a'
assert cd.lastkey() == 'c'

print("✓ All quick tests passed!")
```

### Run Full Test Suite

```bash
# Run all tests (odict + codict)
make test

# Or use pytest directly
pytest tests/test_codict.py tests/test_odict.py -v
```

Expected output:
```
tests/test_codict.py ....................................  [36/36] ✓
tests/test_odict.py ...................................   [35/35] ✓

============================== 71 passed in 0.04s ==============================
```

## Troubleshooting

### Cython Not Found

```bash
# Install Cython
pip install "cython>=3.0"

# Then rebuild
make codict-clean
make codict
```

### Compiler Not Found

**Linux/Mac:**
```bash
# Ubuntu/Debian
sudo apt-get install build-essential

# macOS (install Xcode Command Line Tools)
xcode-select --install
```

**Windows:**
- Install Visual Studio Build Tools
- Or use MinGW-w64

### Build Fails with "language_level" Error

This indicates an older Cython version. Upgrade:
```bash
pip install --upgrade "cython>=3.0"
```

### ImportError: cannot import codict

Possible causes:
1. Extension not built: Run `make codict`
2. Extension built in wrong location: Check `src/odict/` for `*.so` or `*.pyd` file
3. Wrong Python environment: Ensure you're using the same Python that built the extension

```bash
# Rebuild and verify
make codict-clean
make codict
ls -la src/odict/codict*.so
```

### Tests Fail After Installation

```bash
# Clean and rebuild everything
make clean
make install

# Run tests again
make test
```

## Build Artifacts

After successful build, you should see:

```
src/odict/
├── codict.pyx              # Source Cython file
├── codict.c                # Generated C code (~1.4 MB)
└── codict.*.so             # Compiled extension (~1.9 MB)
    # Filename varies by platform:
    # - Linux: codict.cpython-312-x86_64-linux-gnu.so
    # - macOS: codict.cpython-312-darwin.so
    # - Windows: codict.cp312-win_amd64.pyd
```

## Cleaning Build Artifacts

```bash
# Clean codict build artifacts only
make codict-clean

# Clean all build artifacts
make clean

# Remove sources directory too
make purge
```

## Advanced Build Options

### Debug Build

```python
# Add debug symbols
CFLAGS="-g -O0" python setup.py build_ext --inplace
```

### Optimized Build

```python
# Maximum optimization
CFLAGS="-O3" python setup.py build_ext --inplace
```

### Disable codict Build

If you only want Python odict without the Cython extension:

```bash
# Set BUILD_CODICT to false in Makefile or environment
BUILD_CODICT=false make install
```

## Next Steps

- [Usage Guide](usage.md) - Learn how to use codict
- [API Reference](api-reference.md) - Complete method listing
- [Building Guide](../development/building.md) - Detailed build system information
