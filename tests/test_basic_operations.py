# Python Software Foundation License
"""Tests for basic ordered dict operations."""

import pytest


def test_containment_with_in_operator(ODict):
    """Test key containment with 'in' operator."""
    o = ODict([('a', 1)])
    assert 'a' in o
    assert 'foo' not in o


def test_has_key_method(ODict):
    """Test has_key() method."""
    o = ODict([('a', 1)])
    assert o.has_key('a')
    assert not o.has_key('foo')


def test_get_existing_key(ODict):
    """Test get() with existing key."""
    o = ODict([('a', 1)])
    assert o.get('a') == 1


def test_get_missing_key_with_default(ODict):
    """Test get() with missing key returns default."""
    o = ODict([('a', 1)])
    assert o.get('foo', '') == ''
    assert o.get('bar', None) is None
    assert o.get('baz', 42) == 42


def test_values_method(sample_od):
    """Test values() returns list of values in order."""
    assert sample_od.values() == [1, 2, 3, 4]


def test_setdefault_existing_key(ODict):
    """setdefault() on existing key returns existing value."""
    o = ODict([(1, 'x')])
    assert o.setdefault(1, 9999) == 'x'
    assert o[1] == 'x'  # Value unchanged


def test_setdefault_new_key(ODict):
    """setdefault() on new key sets and returns default value."""
    o = ODict([(1, 'x')])
    assert o.setdefault(4, 9999) == 9999
    assert o[4] == 9999
    assert o.items() == [(1, 'x'), (4, 9999)]


@pytest.mark.parametrize('key,default,expected_value,expected_items', [
    (1, 'default', 'x', [(1, 'x')]),  # existing key
    (2, 'new', 'new', [(1, 'x'), (2, 'new')]),  # new key
    (3, None, None, [(1, 'x'), (3, None)]),  # None default
])
def test_setdefault_parametrized(ODict, key, default, expected_value, expected_items):
    """setdefault() with various keys and defaults."""
    o = ODict([(1, 'x')])
    result = o.setdefault(key, default)
    assert result == expected_value
    assert o.items() == expected_items


def test_first_key_method(sample_od):
    """firstkey() returns first key."""
    assert sample_od.firstkey() == 'a'


def test_first_key_property(sample_od):
    """first_key property returns first key."""
    assert sample_od.first_key == 'a'


def test_last_key_method(sample_od):
    """lastkey() returns last key."""
    assert sample_od.lastkey() == 'd'


def test_last_key_property(sample_od):
    """last_key property returns last key."""
    assert sample_od.last_key == 'd'


def test_first_key_on_empty_dict_raises(empty_od):
    """firstkey() on empty dict raises KeyError."""
    with pytest.raises(KeyError, match='Ordered dictionary is empty'):
        empty_od.firstkey()


def test_first_key_property_on_empty_dict_raises(empty_od):
    """first_key property on empty dict raises KeyError."""
    with pytest.raises(KeyError, match='Ordered dictionary is empty'):
        _ = empty_od.first_key


def test_last_key_on_empty_dict_raises(empty_od):
    """lastkey() on empty dict raises KeyError."""
    with pytest.raises(KeyError, match='Ordered dictionary is empty'):
        empty_od.lastkey()


def test_last_key_property_on_empty_dict_raises(empty_od):
    """last_key property on empty dict raises KeyError."""
    with pytest.raises(KeyError, match='Ordered dictionary is empty'):
        _ = empty_od.last_key


def test_next_key_on_empty_dict_raises(empty_od):
    """next_key() on empty dict raises KeyError."""
    with pytest.raises(KeyError):
        empty_od.next_key('x')


def test_next_key_on_single_item_raises(ODict):
    """next_key() on last item raises KeyError."""
    o = ODict([('x', 1)])
    with pytest.raises(KeyError):
        o.next_key('x')


def test_next_key_returns_next(ODict):
    """next_key() returns the next key in order."""
    o = ODict([('x', 1), ('y', 2)])
    assert o.next_key('x') == 'y'


def test_prev_key_on_empty_dict_raises(empty_od):
    """prev_key() on empty dict raises KeyError."""
    with pytest.raises(KeyError):
        empty_od.prev_key('x')


def test_prev_key_on_single_item_raises(ODict):
    """prev_key() on first item raises KeyError."""
    o = ODict([('x', 1)])
    with pytest.raises(KeyError):
        o.prev_key('x')


def test_prev_key_returns_prev(ODict):
    """prev_key() returns the previous key in order."""
    o = ODict([('x', 1), ('y', 2)])
    assert o.prev_key('y') == 'x'
