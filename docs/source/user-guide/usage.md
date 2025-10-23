# Usage Guide

## Basic Usage

### Creating a Codict

```python
from odict.codict import codict

# Create from list of tuples
cd = codict([('a', 1), ('b', 2), ('c', 3)])

# Create from keyword arguments
cd = codict(a=1, b=2, c=3)

# Create from dict
cd = codict({'a': 1, 'b': 2, 'c': 3})

# Create empty and populate
cd = codict()
cd['a'] = 1
cd['b'] = 2
cd['c'] = 3
```

### Accessing Items

```python
cd = codict([('a', 1), ('b', 2), ('c', 3)])

# Get item by key
value = cd['a']  # 1

# Get with default
value = cd.get('d', 'default')  # 'default'

# Check if key exists
if 'a' in cd:
    print("Key exists")

# Alternative check (odict-specific)
if cd.has_key('a'):
    print("Key exists")
```

### Accessing in Order

```python
cd = codict([('a', 1), ('b', 2), ('c', 3)])

# Get all keys in order
keys = cd.keys()  # ['a', 'b', 'c']

# Get all values in order
values = cd.values()  # [1, 2, 3]

# Get all items in order
items = cd.items()  # [('a', 1), ('b', 2), ('c', 3)]
```

### Iteration

```python
cd = codict([('a', 1), ('b', 2), ('c', 3)])

# Forward iteration
for key in cd:
    print(f"{key}: {cd[key]}")

# Iterate over items
for key, value in cd.items():
    print(f"{key}: {value}")

# Reverse iteration
for key in reversed(cd):
    print(f"{key}: {cd[key]}")

# Or use odict-specific reverse methods
for key in cd.riterkeys():
    print(key)

# Reverse items
for key, value in cd.riteritems():
    print(f"{key}: {value}")
```

### First and Last Access

```python
cd = codict([('a', 1), ('b', 2), ('c', 3)])

# Get first key
first = cd.firstkey()  # 'a'
# Or use property
first = cd.first_key   # 'a'

# Get last key
last = cd.lastkey()    # 'c'
# Or use property
last = cd.last_key     # 'c'
```

## Advanced Operations

### Inserting at Specific Positions

```python
cd = codict([('a', 1), ('b', 2), ('c', 3)])

# Insert before a specific key
cd.insertbefore('b', 'new', 99)
print(cd.keys())  # ['a', 'new', 'b', 'c']

# Insert after a specific key
cd.insertafter('a', 'another', 88)
print(cd.keys())  # ['a', 'another', 'new', 'b', 'c']

# Insert at beginning
cd.insertfirst('first', 11)
print(cd.keys())  # ['first', 'a', 'another', 'new', 'b', 'c']

# Insert at end
cd.insertlast('last', 99)
print(cd.keys())  # ['first', 'a', 'another', 'new', 'b', 'c', 'last']
```

### Moving Elements

```python
cd = codict([('a', 1), ('b', 2), ('c', 3), ('d', 4)])

# Move element to first position
cd.movefirst('c')
print(cd.keys())  # ['c', 'a', 'b', 'd']

# Move element to last position
cd.movelast('a')
print(cd.keys())  # ['c', 'b', 'd', 'a']

# Move element before another
cd.movebefore('b', 'a')
print(cd.keys())  # ['c', 'a', 'b', 'd']

# Move element after another
cd.moveafter('d', 'a')
print(cd.keys())  # ['c', 'b', 'd', 'a']
```

### Swapping Elements

```python
cd = codict([('a', 1), ('b', 2), ('c', 3)])

# Swap two elements
cd.swap('a', 'c')
print(cd.keys())  # ['c', 'b', 'a']
```

### Renaming Keys

```python
cd = codict([('a', 1), ('b', 2), ('c', 3)])

# Rename a key (keeps position and value)
cd.alter_key('b', 'beta')
print(cd.keys())  # ['a', 'beta', 'c']
print(cd['beta']) # 2
```

### Sorting

```python
cd = codict([('c', 3), ('a', 1), ('b', 2)])

# Sort by keys
cd.sort()
print(cd.keys())  # ['a', 'b', 'c']

# Sort with custom key function
cd.sort(key=lambda x: -cd[x])  # Sort by value descending
print(cd.keys())  # ['c', 'b', 'a']
```

### Navigation

```python
cd = codict([('a', 1), ('b', 2), ('c', 3), ('d', 4)])

# Get next key
next_key = cd.next_key('b')  # 'c'

# Get previous key
prev_key = cd.prev_key('c')  # 'b'

# Navigate through all keys
key = cd.firstkey()
while key:
    print(f"Key: {key}, Value: {cd[key]}")
    try:
        key = cd.next_key(key)
    except (KeyError, StopIteration):
        break
```

### Copying

```python
cd = codict([('a', 1), ('b', 2), ('c', 3)])

# Shallow copy
cd_copy = cd.copy()

# Deep copy
import copy
cd_deep = copy.deepcopy(cd)
```

### Conversion

```python
cd = codict([('a', 1), ('b', 2), ('c', 3)])

# Convert to regular dict
regular_dict = cd.as_dict()
print(type(regular_dict))  # <class 'dict'>

# Convert to list of tuples
tuples_list = list(cd.items())
```

## Drop-in Replacement for Odict

The most common use case is to use codict as a drop-in replacement for odict:

```python
# Option 1: Try codict, fallback to odict
try:
    from odict.codict import codict as odict
except ImportError:
    from odict import odict

# Use as normal
od = odict([('x', 10), ('y', 20)])
```

```python
# Option 2: Conditional import based on performance needs
import os

if os.environ.get('USE_CODICT', 'true').lower() == 'true':
    try:
        from odict.codict import codict as OrderedDict
    except ImportError:
        from collections import OrderedDict
else:
    from collections import OrderedDict

# Use consistently
data = OrderedDict([('a', 1), ('b', 2)])
```

```python
# Option 3: Direct replacement in existing code
# Change this:
from odict import odict

# To this:
from odict.codict import codict as odict

# All existing code continues to work
```

## Pickle Serialization

Codict fully supports pickle serialization with all protocols:

```python
import pickle
from odict.codict import codict

# Create codict
cd = codict([('a', 1), ('b', 2), ('c', 3)])

# Pickle (all protocols 0-5 supported)
pickled = pickle.dumps(cd)

# Unpickle
restored = pickle.loads(pickled)

# Verify
assert restored.keys() == cd.keys()
assert restored.values() == cd.values()

# All operations work on unpickled codict
restored['d'] = 4
restored.movefirst('d')
print(restored.keys())  # ['d', 'a', 'b', 'c']
```

## Common Patterns

### Building from Data

```python
# From database results
from odict.codict import codict

def query_to_codict(cursor):
    """Convert database results to ordered dict."""
    results = cursor.fetchall()
    return codict([(row['id'], row['data']) for row in results])
```

### Maintaining Insertion Order with Updates

```python
cd = codict()

# Add items - order is maintained
for key in ['c', 'a', 'b']:
    cd[key] = key.upper()

print(cd.keys())  # ['c', 'a', 'b'] - insertion order preserved

# Update existing key - order unchanged
cd['a'] = 'AAA'
print(cd.keys())  # ['c', 'a', 'b'] - still same order
```

### LRU Cache-like Behavior

```python
class LRUCodict(codict):
    """Simple LRU cache using codict."""

    def __init__(self, max_size=100):
        super().__init__()
        self.max_size = max_size

    def __setitem__(self, key, value):
        # If key exists, move to end (most recent)
        if key in self:
            del self[key]

        # Add new item at end
        super().__setitem__(key, value)

        # Remove oldest if over capacity
        if len(self) > self.max_size:
            oldest = self.firstkey()
            del self[oldest]
```

### Configuration Files with Order

```python
def load_config(filename):
    """Load config file maintaining order."""
    from odict.codict import codict
    import json

    with open(filename) as f:
        data = json.load(f, object_pairs_hook=codict)

    return data

# Config maintains order from file
config = load_config('config.json')
```

## Performance Tips

1. **Use appropriate size**: Codict excels with 10K+ items
2. **Prefer creation over insertion**: Batch creation is faster than individual inserts
3. **Cache results**: If calling `keys()` multiple times with no modifications, cache the result
4. **Use iteration methods**: `iteritems()` is more memory-efficient than `items()`

## Next Steps

- [API Reference](api-reference.md) - Complete method listing
- [Performance Analysis](../technical/performance.md) - Detailed benchmarks
- [Benchmarking Guide](../technical/benchmarking.md) - Run your own benchmarks
