import sys

# Backwards compatibility: alias legacy pyodict module to new odict.odict module
# Import the odict submodule (not the odict variable defined above)
from . import odict

sys.modules['odict.pyodict'] = odict

# Use pure Python implementation
odict = odict.odict  # noqa
