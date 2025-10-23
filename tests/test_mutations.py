# Python Software Foundation License
"""Tests for mutation operations on ordered dicts."""

import pytest


def test_update_with_keyword_arguments_fails(empty_od):
    """update() with keyword arguments fails to avoid ordering trap."""
    with pytest.raises(
        TypeError,
        match='update\\(\\) of ordered dict takes no keyword arguments'
    ):
        empty_od.update(foo=1)


def test_update_with_tuples(ODict):
    """update() with tuple sequence adds items in order."""
    o = ODict()
    o.update(data=((1, 1), (2, 2)))
    assert o.items() == [(1, 1), (2, 2)]


def test_update_with_dict(ODict):
    """update() with dict adds items."""
    o = ODict()
    o.update(data=((1, 1), (2, 2)))
    o.update(data={3: 3})
    assert o.items() == [(1, 1), (2, 2), (3, 3)]


def test_pop_missing_key_raises(ODict):
    """pop() on missing key raises KeyError."""
    o = ODict([(1, 'a'), (2, 'b')])
    with pytest.raises(KeyError, match='3'):
        o.pop(3)


def test_pop_missing_key_with_default(ODict):
    """pop() on missing key with default returns default."""
    o = ODict([(1, 'a'), (2, 'b')])
    assert o.pop(3, 'foo') == 'foo'
    assert o.items() == [(1, 'a'), (2, 'b')]


def test_pop_existing_key(ODict):
    """pop() on existing key returns value and removes item."""
    o = ODict([(1, 'a'), (2, 'b')])
    assert o.pop(2) == 'b'
    assert o.items() == [(1, 'a')]


def test_popitem_returns_and_removes_last(ODict):
    """popitem() returns and removes last item."""
    o = ODict([(1, 'a'), (2, 'b')])
    assert o.popitem() == (2, 'b')
    assert o.items() == [(1, 'a')]


def test_popitem_on_empty_raises(empty_od):
    """popitem() on empty dict raises KeyError."""
    with pytest.raises(KeyError, match='popitem\\(\\): ordered dictionary is empty'):
        empty_od.popitem()


def test_delete_from_empty_raises(ODict, nil):
    """Deleting from empty dict raises KeyError."""
    o = ODict()
    with pytest.raises(KeyError, match='1'):
        del o['1']


def test_delete_single_item_makes_empty(ODict, nil):
    """Deleting the only item makes dict empty."""
    o = ODict([('1', 1)])
    del o['1']
    assert len(o) == 0
    assert o.lh == nil
    assert o.lt == nil


def test_delete_first_item(ODict):
    """Deleting first item updates head pointer."""
    o = ODict([('1', 1), ('2', 2), ('3', 3)])
    del o['1']
    assert o.lh == '2'
    assert o.lt == '3'
    assert o.items() == [('2', 2), ('3', 3)]


def test_delete_middle_item(ODict):
    """Deleting middle item maintains order."""
    o = ODict([('1', 1), ('2', 2), ('3', 3)])
    del o['2']
    assert o.lh == '1'
    assert o.lt == '3'
    assert o.items() == [('1', 1), ('3', 3)]


def test_delete_last_item(ODict):
    """Deleting last item updates tail pointer."""
    o = ODict([('1', 1), ('2', 2), ('3', 3)])
    del o['3']
    assert o.lh == '1'
    assert o.lt == '2'
    assert o.items() == [('1', 1), ('2', 2)]


def test_alter_key_first_position(ODict):
    """alter_key() on first key changes key but preserves position."""
    o = ODict((('1', 'a'), ('2', 'b'), ('3', 'c')))
    o.alter_key('1', 'foo')
    assert o.keys() == ['foo', '2', '3']
    assert o.rkeys() == ['3', '2', 'foo']
    assert o.values() == ['a', 'b', 'c']
    assert o['foo'] == 'a'
    assert o.lh == 'foo'


def test_alter_key_middle_position(ODict):
    """alter_key() on middle key changes key but preserves position."""
    o = ODict((('1', 'a'), ('2', 'b'), ('3', 'c')))
    o.alter_key('1', 'foo')
    o.alter_key('2', 'bar')
    assert o.keys() == ['foo', 'bar', '3']
    assert o.rkeys() == ['3', 'bar', 'foo']
    assert o.values() == ['a', 'b', 'c']
    assert o['bar'] == 'b'


def test_alter_key_last_position(ODict):
    """alter_key() on last key changes key but preserves position."""
    o = ODict((('1', 'a'), ('2', 'b'), ('3', 'c')))
    o.alter_key('1', 'foo')
    o.alter_key('2', 'bar')
    o.alter_key('3', 'baz')
    assert o.keys() == ['foo', 'bar', 'baz']
    assert o.rkeys() == ['baz', 'bar', 'foo']
    assert o.values() == ['a', 'b', 'c']
    assert o['baz'] == 'c'
    assert o.lt == 'baz'


def test_alter_key_preserves_dict_class(ODict):
    """alter_key() preserves internal dict class."""
    o = ODict((('1', 'a'), ('2', 'b'), ('3', 'c')))
    o.alter_key('1', 'foo')
    assert o._dict_cls() is dict
