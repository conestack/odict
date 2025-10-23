# Python Software Foundation License
# cython: language_level=3
"""Cython-optimized ordered dictionary implementation.

This module provides a high-performance implementation of ordered dictionaries
using Cython extension types for the node structure.
"""
from odict.base import _BaseOrderedDict, _nil


# Lightweight entry class for storing linked list data
# Uses __slots__ for memory efficiency and faster attribute access
cdef class Entry:
    """C-optimized entry for double-linked list.

    Stores prev_key, value, and next_key with faster access than Python lists.
    """
    cdef public object prev_key
    cdef public object value
    cdef public object next_key

    def __init__(self, *args):
        """Initialize Entry with either a list or 3 separate arguments.

        Supports both:
        - Entry([prev, val, next]) - for backwards compatibility
        - Entry(prev, val, next) - for pickle support
        """
        if len(args) == 1 and isinstance(args[0], (list, tuple)):
            # Called with list: Entry([prev, val, next])
            self.prev_key, self.value, self.next_key = args[0]
        elif len(args) == 3:
            # Called with 3 args: Entry(prev, val, next)
            self.prev_key, self.value, self.next_key = args
        else:
            raise TypeError(
                f"Entry() takes either 1 list/tuple argument or 3 separate arguments, "
                f"got {len(args)} argument(s)"
            )

    def __reduce__(self):
        # Support for pickle
        return (Entry, (self.prev_key, self.value, self.next_key))

    def __repr__(self):
        return f'Entry({self.prev_key!r}, {self.value!r}, {self.next_key!r})'

    def __getitem__(self, int index):
        """Support list-like item access: entry[0], entry[1], entry[2]."""
        if index == 0 or index == -3:
            return self.prev_key
        elif index == 1 or index == -2:
            return self.value
        elif index == 2 or index == -1:
            return self.next_key
        else:
            raise IndexError("Entry index out of range")

    def __setitem__(self, int index, object val):
        """Support list-like item assignment: entry[0] = x, entry[1] = y, entry[2] = z."""
        if index == 0 or index == -3:
            self.prev_key = val
        elif index == 1 or index == -2:
            self.value = val
        elif index == 2 or index == -1:
            self.next_key = val
        else:
            raise IndexError("Entry index out of range")


class _codict(_BaseOrderedDict):
    """Cython-optimized ordered dict data structure using Entry objects.

    Uses Cython-optimized Entry class instead of Python lists for better performance.
    Maintains insertion order; overwriting values doesn't change order.
    """

    def _entry_cls(self):
        # Returns Entry class instead of list for C-optimized storage
        return Entry

    def __eq__(self, other):
        """Compare two codicts for equality based on their items."""
        if not isinstance(other, (_codict, dict)):
            return NotImplemented
        if len(self) != len(other):
            return False
        # Compare items in order
        return self.items() == list(other.items()) if hasattr(other, 'items') else False

    def __ne__(self, other):
        """Compare two codicts for inequality."""
        result = self.__eq__(other)
        if result is NotImplemented:
            return result
        return not result

    @classmethod
    def fromkeys(cls, keys, value=None):
        """Create a new ordered dictionary with keys from keys and values set to value."""
        new = cls()
        for key in keys:
            new[key] = value
        return new

    def __reduce__(self):
        """Support for pickle serialization."""
        return (self.__class__, (list(self.items()),))


class codict(_codict, dict):
    def _dict_cls(self):
        return dict
