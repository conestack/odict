# Python Software Foundation License
"""Tests for serialization (copy, pickle) of ordered dicts."""

import copy
import pickle
import pytest


# Copy tests

def test_copy_method(sample_od):
    """copy() creates a new independent instance."""
    o_copy = sample_od.copy()
    assert o_copy is not sample_od
    assert o_copy.items() == [('a', 1), ('b', 2), ('c', 3), ('d', 4)]


def test_shallow_copy_with_copy_module(ODict):
    """copy.copy() creates shallow copy."""
    obj = object()
    o = ODict([('1', 1), ('2', 2), ('3', obj)])
    o_copy = copy.copy(o)
    assert o_copy is not o
    assert o_copy['3'] is o['3']  # Same object reference


def test_deep_copy_with_copy_module(ODict):
    """copy.deepcopy() creates deep copy."""
    obj = object()
    o = ODict([('1', 1), ('2', 2), ('3', obj)])
    o_copy = copy.deepcopy(o)
    assert o_copy is not o
    assert o_copy['3'] is not o['3']  # Different object reference


# Pickle tests

def test_pickle_in_list(ODict):
    """Pickle and unpickle ordered dict inside a list."""
    original = [ODict([(1, 2)])]
    pickled = pickle.dumps(original)
    unpickled = pickle.loads(pickled)
    assert unpickled == original


def test_pickle_roundtrip(ODict):
    """Pickle and unpickle preserves data and order."""
    o = ODict([('a', 1), ('b', 2), ('c', 3)])
    pickled = pickle.dumps(o)
    unpickled = pickle.loads(pickled)
    assert unpickled.items() == [('a', 1), ('b', 2), ('c', 3)]
    assert unpickled.keys() == ['a', 'b', 'c']
    assert unpickled.values() == [1, 2, 3]


def test_pickle_all_protocols(ODict):
    """Pickle works with all protocol versions."""
    o = ODict([('a', 1), ('b', 2), ('c', 3)])
    # Start from protocol 2 to avoid issues with older protocols
    for protocol in range(2, pickle.HIGHEST_PROTOCOL + 1):
        pickled = pickle.dumps(o, protocol=protocol)
        unpickled = pickle.loads(pickled)
        assert unpickled.items() == [('a', 1), ('b', 2), ('c', 3)]


def test_pickle_empty_dict(ODict):
    """Pickle empty ordered dict."""
    o = ODict()
    pickled = pickle.dumps(o)
    unpickled = pickle.loads(pickled)
    assert len(unpickled) == 0
    assert unpickled.items() == []


def test_pickle_complex_values(ODict):
    """Pickle ordered dict with complex values."""
    o = ODict([
        ('list', [1, 2, 3]),
        ('dict', {'nested': 'value'}),
        ('tuple', (4, 5, 6)),
        ('string', 'hello world'),
        ('number', 42),
    ])
    pickled = pickle.dumps(o)
    unpickled = pickle.loads(pickled)
    assert unpickled['list'] == [1, 2, 3]
    assert unpickled['dict'] == {'nested': 'value'}
    assert unpickled['tuple'] == (4, 5, 6)
    assert unpickled['string'] == 'hello world'
    assert unpickled['number'] == 42
    assert unpickled.keys() == ['list', 'dict', 'tuple', 'string', 'number']


def test_pickle_large_dict(ODict):
    """Pickle large ordered dict."""
    o = ODict([(str(i), i * 2) for i in range(1000)])
    pickled = pickle.dumps(o)
    unpickled = pickle.loads(pickled)
    assert len(unpickled) == 1000
    assert unpickled['0'] == 0
    assert unpickled['500'] == 1000
    assert unpickled['999'] == 1998
    # Verify order is preserved
    assert unpickled.keys()[:5] == ['0', '1', '2', '3', '4']
    assert unpickled.keys()[-5:] == ['995', '996', '997', '998', '999']


def test_pickle_in_containers(ODict):
    """Pickle ordered dicts inside list/dict containers."""
    od1 = ODict([('a', 1), ('b', 2)])
    od2 = ODict([('x', 10), ('y', 20)])

    # In list
    container_list = [od1, od2, 'other']
    pickled = pickle.dumps(container_list)
    unpickled = pickle.loads(pickled)
    assert unpickled[0].items() == [('a', 1), ('b', 2)]
    assert unpickled[1].items() == [('x', 10), ('y', 20)]
    assert unpickled[2] == 'other'

    # In dict
    container_dict = {'first': od1, 'second': od2}
    pickled = pickle.dumps(container_dict)
    unpickled = pickle.loads(pickled)
    assert unpickled['first'].items() == [('a', 1), ('b', 2)]
    assert unpickled['second'].items() == [('x', 10), ('y', 20)]


def test_pickle_operations_on_unpickled(ODict):
    """Unpickled ordered dict supports all operations."""
    o = ODict([('a', 1), ('b', 2), ('c', 3)])
    unpickled = pickle.loads(pickle.dumps(o))

    # Test various operations
    unpickled['d'] = 4
    assert unpickled.keys() == ['a', 'b', 'c', 'd']

    del unpickled['b']
    assert unpickled.keys() == ['a', 'c', 'd']

    unpickled.insertbefore('c', 'new', 99)
    assert unpickled.keys() == ['a', 'new', 'c', 'd']

    unpickled.movefirst('d')
    assert unpickled.keys() == ['d', 'a', 'new', 'c']

    # Reverse iteration
    assert unpickled.rkeys() == ['c', 'new', 'a', 'd']


# Entry pickle test (codict-specific, but safe for both)

def test_entry_pickle(impl):
    """Test that Entry objects (codict) pickle correctly."""
    _, _, _nil = impl

    # Skip for odict since it doesn't have Entry
    if impl[0].__name__ == 'odict':
        pytest.skip('Entry is codict-specific')

    from odict.codict import Entry
    entry = Entry('prev', 'value', 'next')
    pickled = pickle.dumps(entry)
    unpickled = pickle.loads(pickled)
    assert unpickled.prev_key == 'prev'
    assert unpickled.value == 'value'
    assert unpickled.next_key == 'next'
