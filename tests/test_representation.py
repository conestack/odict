# Python Software Foundation License
"""Tests for string representation of ordered dicts."""

import pytest


def test_str_with_items(ODict):
    """__str__() returns dict-like string representation."""
    o = ODict([('foo', 'a'), ('bar', 'b'), ('baz', 'c')])
    assert str(o) == "{'foo': 'a', 'bar': 'b', 'baz': 'c'}"


def test_repr_empty(ODict):
    """__repr__() of empty ordered dict."""
    o = ODict()
    assert repr(o) == 'odict()'


def test_repr_with_single_item(ODict):
    """__repr__() with single item."""
    o = ODict([('foo', 'a')])
    assert repr(o) == "odict([('foo', 'a')])"


@pytest.mark.parametrize('items,expected_repr', [
    ([], 'odict()'),
    ([('a', 1)], "odict([('a', 1)])"),
    ([('x', 'y'), ('z', 'w')], "odict([('x', 'y'), ('z', 'w')])"),
])
def test_repr_parametrized(ODict, items, expected_repr):
    """__repr__() with various contents."""
    o = ODict(items)
    assert repr(o) == expected_repr
