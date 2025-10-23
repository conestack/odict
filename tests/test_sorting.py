# Python Software Foundation License
"""Tests for sorting ordered dicts."""

import pytest


def test_sort_basic(ODict):
    """Basic sorting by key."""
    o = ODict([('a', 1), ('c', 3), ('b', 2)])
    o.sort()
    assert o.items() == [('a', 1), ('b', 2), ('c', 3)]


def test_sort_with_cmp_function(ODict):
    """Sort with custom comparison function (reversed by key)."""
    def mycmp(x, y):
        if x[0] > y[0]:
            return -1
        if x[0] < y[0]:
            return 1
        return 0

    o = ODict([('a', 1), ('c', 3), ('b', 2)])
    o.sort(cmp=mycmp)
    assert o.items() == [('c', 3), ('b', 2), ('a', 1)]


def test_sort_with_key_function(ODict):
    """Sort with key function."""
    o = ODict([('a', 1), ('c', 3), ('b', 2)])
    o.sort(key=lambda x: x[0])
    assert o.items() == [('a', 1), ('b', 2), ('c', 3)]


def test_sort_with_key_and_reverse(ODict):
    """Sort with key function and reverse=True."""
    o = ODict([('a', 1), ('c', 3), ('b', 2)])
    o.sort(key=lambda x: x[0], reverse=True)
    assert o.items() == [('c', 3), ('b', 2), ('a', 1)]


def test_sort_numeric_string_keys(ODict):
    """Sort with numeric string keys."""
    o = ODict([('3', 'c'), ('1', 'a'), ('2', 'b')])
    o.sort()
    assert o.items() == [('1', 'a'), ('2', 'b'), ('3', 'c')]
