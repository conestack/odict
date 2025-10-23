# Try to import Cython-optimized version first
try:
    from .codict import codict as odict  # noqa
except ImportError:  # pragma: no cover
    # Fall back to pure Python implementation
    from .odict import odict  # noqa
