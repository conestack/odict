import sys

# Backwards compatibility: alias legacy pyodict module to new odict.odict module
# Import the odict submodule (not the odict variable defined above)
from . import odict

sys.modules['odict.pyodict'] = odict

# Try to import Cython-optimized version first
try:
    from .codict import codict as odict  # noqa
except ImportError:  # pragma: no cover
    # Fall back to pure Python implementation
    odict = odict.odict  # noqa
