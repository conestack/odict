# Python Software Foundation License
"""Pure Python ordered dictionary implementation.

This module provides a pure Python implementation of ordered dictionaries
using the common base class from odict.base.
"""
from odict.base import _BaseOrderedDict, _nil


class _odict(_BaseOrderedDict):
    """Ordered dict data structure, with O(1) complexity for dict operations
    that modify one element.

    Overwriting values doesn't change their original sequential order.
    """

    def _list_factory(self):
        # XXX: rename to _list_cls
        return list


class odict(_odict, dict):
    def _dict_impl(self):
        return dict
