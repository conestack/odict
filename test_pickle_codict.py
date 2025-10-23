#!/usr/bin/env python
# Test pickle serialization/deserialization for codict
import pickle
from odict.codict import codict, Node

def test_node_pickle():
    """Test that Node objects pickle correctly."""
    print("Testing Node pickle...")
    node = Node('prev', 'value', 'next')
    pickled = pickle.dumps(node)
    unpickled = pickle.loads(pickled)

    assert unpickled.prev_key == 'prev'
    assert unpickled.value == 'value'
    assert unpickled.next_key == 'next'
    print("✓ Node pickle works")

def test_simple_codict_pickle():
    """Test simple codict pickle."""
    print("\nTesting simple codict pickle...")
    cd = codict([('a', 1), ('b', 2), ('c', 3)])

    # Pickle and unpickle
    pickled = pickle.dumps(cd)
    unpickled = pickle.loads(pickled)

    # Verify data integrity
    assert unpickled.items() == [('a', 1), ('b', 2), ('c', 3)]
    assert unpickled.keys() == ['a', 'b', 'c']
    assert unpickled.values() == [1, 2, 3]
    assert unpickled['a'] == 1
    assert unpickled['b'] == 2
    assert unpickled['c'] == 3
    print("✓ Simple codict pickle works")

def test_complex_codict_pickle():
    """Test codict with complex values."""
    print("\nTesting complex codict pickle...")
    cd = codict([
        ('list', [1, 2, 3]),
        ('dict', {'nested': 'value'}),
        ('tuple', (4, 5, 6)),
        ('string', 'hello world'),
        ('number', 42),
    ])

    pickled = pickle.dumps(cd)
    unpickled = pickle.loads(pickled)

    assert unpickled['list'] == [1, 2, 3]
    assert unpickled['dict'] == {'nested': 'value'}
    assert unpickled['tuple'] == (4, 5, 6)
    assert unpickled['string'] == 'hello world'
    assert unpickled['number'] == 42
    assert unpickled.keys() == ['list', 'dict', 'tuple', 'string', 'number']
    print("✓ Complex codict pickle works")

def test_empty_codict_pickle():
    """Test empty codict pickle."""
    print("\nTesting empty codict pickle...")
    cd = codict()
    pickled = pickle.dumps(cd)
    unpickled = pickle.loads(pickled)

    assert len(unpickled) == 0
    assert unpickled.items() == []
    print("✓ Empty codict pickle works")

def test_large_codict_pickle():
    """Test large codict pickle."""
    print("\nTesting large codict pickle...")
    cd = codict([(str(i), i * 2) for i in range(1000)])

    pickled = pickle.dumps(cd)
    unpickled = pickle.loads(pickled)

    assert len(unpickled) == 1000
    assert unpickled['0'] == 0
    assert unpickled['500'] == 1000
    assert unpickled['999'] == 1998
    # Verify order is preserved
    assert unpickled.keys()[:5] == ['0', '1', '2', '3', '4']
    assert unpickled.keys()[-5:] == ['995', '996', '997', '998', '999']
    print("✓ Large codict pickle works")

def test_codict_in_container():
    """Test codict inside list/dict containers."""
    print("\nTesting codict in containers...")
    cd1 = codict([('a', 1), ('b', 2)])
    cd2 = codict([('x', 10), ('y', 20)])

    # In list
    container_list = [cd1, cd2, 'other']
    pickled = pickle.dumps(container_list)
    unpickled = pickle.loads(pickled)

    assert unpickled[0].items() == [('a', 1), ('b', 2)]
    assert unpickled[1].items() == [('x', 10), ('y', 20)]
    assert unpickled[2] == 'other'

    # In dict
    container_dict = {'first': cd1, 'second': cd2}
    pickled = pickle.dumps(container_dict)
    unpickled = pickle.loads(pickled)

    assert unpickled['first'].items() == [('a', 1), ('b', 2)]
    assert unpickled['second'].items() == [('x', 10), ('y', 20)]
    print("✓ Codict in containers pickle works")

def test_pickle_protocol_versions():
    """Test different pickle protocols."""
    print("\nTesting different pickle protocols...")
    cd = codict([('a', 1), ('b', 2), ('c', 3)])

    for protocol in range(pickle.HIGHEST_PROTOCOL + 1):
        pickled = pickle.dumps(cd, protocol=protocol)
        unpickled = pickle.loads(pickled)
        assert unpickled.items() == [('a', 1), ('b', 2), ('c', 3)]
        print(f"  ✓ Protocol {protocol} works")

def test_roundtrip_operations():
    """Test that unpickled codict supports all operations."""
    print("\nTesting operations on unpickled codict...")
    cd = codict([('a', 1), ('b', 2), ('c', 3)])

    # Pickle and unpickle
    unpickled = pickle.loads(pickle.dumps(cd))

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

    print("✓ All operations work on unpickled codict")

if __name__ == '__main__':
    print("=" * 60)
    print("Codict Pickle Serialization Tests")
    print("=" * 60)

    test_node_pickle()
    test_simple_codict_pickle()
    test_complex_codict_pickle()
    test_empty_codict_pickle()
    test_large_codict_pickle()
    test_codict_in_container()
    test_pickle_protocol_versions()
    test_roundtrip_operations()

    print("\n" + "=" * 60)
    print("✓ All pickle tests passed!")
    print("=" * 60)
