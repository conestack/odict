# Python Software Foundation License
"""Tests for ordering operations (swap, insert, move) on ordered dicts."""

import pytest


# Swap tests

def test_swap_same_key_raises(five_items_od):
    """swap() with same key raises ValueError."""
    with pytest.raises(ValueError):
        five_items_od.swap('0', '0')


@pytest.mark.parametrize('key_a,key_b,expected_keys,expected_values', [
    # Case first 2, a < b
    ('0', '1', ['1', '0', '2', '3', '4'], ['b', 'a', 'c', 'd', 'e']),
    # Case last 2, a < b
    ('3', '4', ['0', '1', '2', '4', '3'], ['a', 'b', 'c', 'e', 'd']),
    # Case neighbors, a < b
    ('1', '2', ['0', '2', '1', '3', '4'], ['a', 'c', 'b', 'd', 'e']),
    # Case non neighbors, one key first, a < b
    ('0', '2', ['2', '1', '0', '3', '4'], ['c', 'b', 'a', 'd', 'e']),
    # Case non neighbors, one key last, a < b
    ('2', '4', ['0', '1', '4', '3', '2'], ['a', 'b', 'e', 'd', 'c']),
    # Case non neighbors, a < b
    ('1', '3', ['0', '3', '2', '1', '4'], ['a', 'd', 'c', 'b', 'e']),
])
def test_swap_scenarios(five_items_od, key_a, key_b, expected_keys, expected_values):
    """swap() with various position combinations."""
    five_items_od.swap(key_a, key_b)
    assert five_items_od.keys() == expected_keys
    assert five_items_od.values() == expected_values


def test_swap_first_with_last(ODict):
    """swap() first and last items (edge case for head/tail updates)."""
    o = ODict([('a', 1), ('b', 2), ('c', 3)])
    o.swap('a', 'c')
    assert o.keys() == ['c', 'b', 'a']
    assert o.values() == [3, 2, 1]
    assert o.lh == 'c'
    assert o.lt == 'a'


def test_swap_adjacent_at_end(ODict):
    """swap() last two items (edge case for tail update)."""
    o = ODict([('a', 1), ('b', 2), ('c', 3)])
    o.swap('b', 'c')
    assert o.keys() == ['a', 'c', 'b']
    assert o.values() == [1, 3, 2]
    assert o.lt == 'b'


# Insert tests

def test_insertbefore_same_key_raises(ODict):
    """insertbefore() with same key as reference raises ValueError."""
    o = ODict([('0', 'a')])
    with pytest.raises(ValueError):
        o.insertbefore('0', '0', 'a')


def test_insertbefore_missing_reference_raises(ODict):
    """insertbefore() with missing reference key raises KeyError."""
    o = ODict([('0', 'a')])
    with pytest.raises(KeyError):
        o.insertbefore('x', '1', 'b')


def test_insertbefore_basic(ODict):
    """insertbefore() inserts new item before reference."""
    o = ODict([('0', 'a')])
    o.insertbefore('0', '1', 'b')
    assert o.keys() == ['1', '0']
    assert o.rkeys() == ['0', '1']
    assert o.values() == ['b', 'a']
    assert (o.lh, o.lt) == ('1', '0')


def test_insertbefore_multiple(ODict):
    """insertbefore() can be called multiple times."""
    o = ODict([('0', 'a')])
    o.insertbefore('0', '1', 'b')
    o.insertbefore('0', '2', 'c')
    assert o.keys() == ['1', '2', '0']
    assert o.rkeys() == ['0', '2', '1']
    assert o.values() == ['b', 'c', 'a']
    assert (o.lh, o.lt) == ('1', '0')


def test_insertafter_same_key_raises(ODict):
    """insertafter() with same key as reference raises ValueError."""
    o = ODict([('0', 'a')])
    with pytest.raises(ValueError):
        o.insertafter('0', '0', 'a')


def test_insertafter_missing_reference_raises(ODict):
    """insertafter() with missing reference key raises KeyError."""
    o = ODict([('0', 'a')])
    with pytest.raises(KeyError):
        o.insertafter('x', '1', 'b')


def test_insertafter_basic(ODict):
    """insertafter() inserts new item after reference."""
    o = ODict([('0', 'a')])
    o.insertafter('0', '1', 'b')
    assert o.keys() == ['0', '1']
    assert o.rkeys() == ['1', '0']
    assert o.values() == ['a', 'b']
    assert (o.lh, o.lt) == ('0', '1')


def test_insertafter_multiple(ODict):
    """insertafter() can be called multiple times."""
    o = ODict([('0', 'a')])
    o.insertafter('0', '1', 'b')
    o.insertafter('0', '2', 'c')
    assert o.keys() == ['0', '2', '1']
    assert o.rkeys() == ['1', '2', '0']
    assert o.values() == ['a', 'c', 'b']
    assert (o.lh, o.lt) == ('0', '1')


def test_insertfirst_on_empty(ODict):
    """insertfirst() on empty dict."""
    o = ODict()
    o.insertfirst('0', 'a')
    assert o.keys() == ['0']
    assert o.rkeys() == ['0']
    assert o.values() == ['a']


def test_insertfirst_on_nonempty(ODict):
    """insertfirst() inserts at beginning."""
    o = ODict()
    o.insertfirst('0', 'a')
    o.insertfirst('1', 'b')
    assert o.keys() == ['1', '0']
    assert o.rkeys() == ['0', '1']
    assert o.values() == ['b', 'a']


def test_insertlast_on_empty(ODict):
    """insertlast() on empty dict."""
    o = ODict()
    o.insertlast('0', 'a')
    assert o.keys() == ['0']
    assert o.rkeys() == ['0']
    assert o.values() == ['a']


def test_insertlast_on_nonempty(ODict):
    """insertlast() inserts at end."""
    o = ODict()
    o.insertlast('0', 'a')
    o.insertlast('1', 'b')
    assert o.keys() == ['0', '1']
    assert o.rkeys() == ['1', '0']
    assert o.values() == ['a', 'b']


# Move tests

def test_movebefore_same_key_raises(five_items_od):
    """movebefore() with same key raises ValueError."""
    with pytest.raises(ValueError):
        five_items_od.movebefore('0', '0')


@pytest.mark.parametrize('ref,key,expected_keys,expected_values', [
    # Case no neighbors ref < key
    ('1', '3', ['0', '3', '1', '2', '4'], ['a', 'd', 'b', 'c', 'e']),
    # Case no neighbors ref > key
    ('2', '3', ['0', '1', '3', '2', '4'], ['a', 'b', 'd', 'c', 'e']),
    # Case neighbors ref < key
    ('3', '2', ['0', '1', '2', '3', '4'], ['a', 'b', 'c', 'd', 'e']),
    # Case move first, no neighbors
    ('0', '2', ['2', '0', '1', '3', '4'], ['c', 'a', 'b', 'd', 'e']),
])
def test_movebefore_scenarios(ODict, ref, key, expected_keys, expected_values):
    """movebefore() with various position combinations."""
    o = ODict([('0', 'a'), ('1', 'b'), ('2', 'c'), ('3', 'd'), ('4', 'e')])
    o.movebefore(ref, key)
    assert o.keys() == expected_keys
    assert o.values() == expected_values


def test_moveafter_same_key_raises(five_items_od):
    """moveafter() with same key raises ValueError."""
    with pytest.raises(ValueError):
        five_items_od.moveafter('0', '0')


@pytest.mark.parametrize('ref,key,expected_keys,expected_values', [
    # Case no neighbors ref < key
    ('1', '3', ['0', '1', '3', '2', '4'], ['a', 'b', 'd', 'c', 'e']),
    # Case neighbors
    ('3', '2', ['0', '1', '3', '2', '4'], ['a', 'b', 'd', 'c', 'e']),
])
def test_moveafter_scenarios(ODict, ref, key, expected_keys, expected_values):
    """moveafter() with various position combinations."""
    o = ODict([('0', 'a'), ('1', 'b'), ('2', 'c'), ('3', 'd'), ('4', 'e')])
    o.moveafter(ref, key)
    assert o.keys() == expected_keys
    assert o.values() == expected_values


def test_movefirst(ODict):
    """movefirst() moves item to beginning."""
    o = ODict([('0', 'a'), ('1', 'b'), ('2', 'c')])
    o.movefirst('2')
    assert o.keys() == ['2', '0', '1']
    assert o.rkeys() == ['1', '0', '2']
    assert o.values() == ['c', 'a', 'b']
    assert (o.lh, o.lt) == ('2', '1')


def test_movelast(ODict):
    """movelast() moves item to end."""
    o = ODict([('0', 'a'), ('1', 'b'), ('2', 'c')])
    o.movelast('0')
    assert o.keys() == ['1', '2', '0']
    assert o.rkeys() == ['0', '2', '1']
    assert o.values() == ['b', 'c', 'a']
    assert (o.lh, o.lt) == ('1', '0')
