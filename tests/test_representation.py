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
    # Should be 'odict()' or 'codict()'
    assert repr(o) in ('odict()', 'codict()')


def test_repr_with_single_item(ODict):
    """__repr__() with single item."""
    o = ODict([('foo', 'a')])
    # Should be "odict([('foo', 'a')])" or "codict([('foo', 'a')])"
    assert repr(o) in ("odict([('foo', 'a')])", "codict([('foo', 'a')])")


@pytest.mark.parametrize('items,expected_reprs', [
    ([], ['odict()', 'codict()']),
    ([('a', 1)], ["odict([('a', 1)])", "codict([('a', 1)])"]),
    ([('x', 'y'), ('z', 'w')], [
        "odict([('x', 'y'), ('z', 'w')])",
        "codict([('x', 'y'), ('z', 'w')])"
    ]),
])
def test_repr_parametrized(ODict, items, expected_reprs):
    """__repr__() with various contents."""
    o = ODict(items)
    assert repr(o) in expected_reprs
