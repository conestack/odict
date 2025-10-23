# Python Software Foundation License
# cython: language_level=3
import copy
import functools
import sys


class _Nil(object):
    # Q: it feels like using the class with "is" and "is not" instead of "=="
    #    and "!=" should be faster.
    # A: This would break implementations which use pickle for persisting.

    def __repr__(self):
        return 'nil'

    def __eq__(self, other):
        if isinstance(other, _Nil):
            return True
        else:
            return NotImplemented

    def __ne__(self, other):
        if isinstance(other, _Nil):
            return False
        else:
            return NotImplemented

    def __hash__(self):
        return sys.maxsize


_nil = _Nil()


# Lightweight node class for storing linked list data
# Uses __slots__ for memory efficiency and faster attribute access
cdef class Node:
    """C-optimized node for double-linked list.

    Stores prev_key, value, and next_key with faster access than Python lists.
    """
    cdef public object prev_key
    cdef public object value
    cdef public object next_key

    def __init__(self, prev_key, value, next_key):
        self.prev_key = prev_key
        self.value = value
        self.next_key = next_key

    def __reduce__(self):
        # Support for pickle
        return (Node, (self.prev_key, self.value, self.next_key))

    def __repr__(self):
        return f'Node({self.prev_key!r}, {self.value!r}, {self.next_key!r})'


class _codict(object):
    """Cython-optimized ordered dict data structure using Node objects.

    Uses Cython-optimized Node class instead of Python lists for better performance.
    Maintains insertion order; overwriting values doesn't change order.
    """

    def _dict_impl(self):
        return None

    def _list_factory(self):
        # Returns Node class instead of list for C-optimized storage
        return Node

    def __init__(self, data=(), **kwds):
        """This doesn't accept keyword initialization as normal dicts to avoid
        a trap - inside a function or method the keyword args are accessible
        only as a dict, without a defined order, so their original order is
        lost.
        """
        if kwds:
            raise TypeError(
                '__init__() of ordered dict takes no keyword '
                'arguments to avoid an ordering trap.'
            )
        dict_ = self._dict_impl()
        if dict_ is None:
            raise TypeError('No dict implementation class provided.')
        dict_.__init__(self)
        # If you give a normal dict, then the order of elements is undefined
        if hasattr(data, 'items'):
            for key, val in data.items():
                self[key] = val
        else:
            for key, val in data:
                self[key] = val

    # Double-linked list header
    @property
    def lh(self):
        dict_ = self._dict_impl()
        if not hasattr(self, '_lh'):
            dict_.__setattr__(self, '_lh', _nil)
        return dict_.__getattribute__(self, '_lh')

    @lh.setter
    def lh(self, val):
        self._dict_impl().__setattr__(self, '_lh', val)

    # Double-linked list tail
    @property
    def lt(self):
        dict_ = self._dict_impl()
        if not hasattr(self, '_lt'):
            dict_.__setattr__(self, '_lt', _nil)
        return dict_.__getattribute__(self, '_lt')

    @lt.setter
    def lt(self, val):
        self._dict_impl().__setattr__(self, '_lt', val)

    def __getitem__(self, key):
        return self._dict_impl().__getitem__(self, key).value

    def __setitem__(self, key, val):
        dict_ = self._dict_impl()
        try:
            dict_.__getitem__(self, key).value = val
        except KeyError:
            lt = dict_.__getattribute__(self, 'lt')
            new = Node(lt, val, _nil)
            dict_.__setitem__(self, key, new)
            if lt == _nil:
                dict_.__setattr__(self, 'lh', key)
            else:
                dict_.__getitem__(self, lt).next_key = key
            dict_.__setattr__(self, 'lt', key)

    def __delitem__(self, key):
        dict_ = self._dict_impl()
        node = dict_.__getitem__(self, key)
        pred = node.prev_key
        succ = node.next_key

        if pred == _nil:
            dict_.__setattr__(self, 'lh', succ)
        else:
            dict_.__getitem__(self, pred).next_key = succ
        if succ == _nil:
            dict_.__setattr__(self, 'lt', pred)
        else:
            dict_.__getitem__(self, succ).prev_key = pred
        dict_.__delitem__(self, key)

    def __copy__(self):
        new = type(self)()
        for k, v in self.iteritems():
            new[k] = v
        new.__dict__.update(self.__dict__)
        return new

    def __deepcopy__(self, memo):
        new = type(self)()
        memo[id(self)] = new
        for k, v in self.iteritems():
            new[k] = copy.deepcopy(v, memo)
        for k, v in self.__dict__.items():
            setattr(new, k, copy.deepcopy(v, memo))
        return new

    def __contains__(self, key):
        try:
            self[key]
            return True
        except KeyError:
            return False

    def has_key(self, key):
        return key in self

    def __len__(self):
        return len(self.keys())

    def __str__(self):
        pairs = ('%r: %r' % (k, v) for k, v in self.items())
        return '{%s}' % ', '.join(pairs)

    def __repr__(self):
        if self:
            pairs = ('(%r, %r)' % (k, v) for k, v in self.items())
            return '%s([%s])' % (self.__class__.__name__, ', '.join(pairs))
        else:
            return '%s()' % self.__class__.__name__

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

    def get(self, k, x=None):
        if k in self:
            return self._dict_impl().__getitem__(self, k).value
        else:
            return x

    def __iter__(self):
        dict_ = self._dict_impl()
        curr_key = dict_.__getattribute__(self, 'lh')
        while curr_key != _nil:
            yield curr_key
            curr_key = dict_.__getitem__(self, curr_key).next_key

    iterkeys = __iter__

    def keys(self):
        return list(self.iterkeys())

    def alter_key(self, old_key, new_key):
        dict_ = self._dict_impl()
        node = dict_.__getitem__(self, old_key)
        dict_.__delitem__(self, old_key)

        if node.prev_key != _nil:
            dict_.__getitem__(self, node.prev_key).next_key = new_key
        else:
            dict_.__setattr__(self, 'lh', new_key)

        if node.next_key != _nil:
            dict_.__getitem__(self, node.next_key).prev_key = new_key
        else:
            dict_.__setattr__(self, 'lt', new_key)

        dict_.__setitem__(self, new_key, node)

    def itervalues(self):
        dict_ = self._dict_impl()
        curr_key = dict_.__getattribute__(self, 'lh')
        while curr_key != _nil:
            node = dict_.__getitem__(self, curr_key)
            val = node.value
            curr_key = node.next_key
            yield val

    def values(self):
        return list(self.itervalues())

    def iteritems(self):
        dict_ = self._dict_impl()
        curr_key = dict_.__getattribute__(self, 'lh')
        while curr_key != _nil:
            node = dict_.__getitem__(self, curr_key)
            val = node.value
            next_key = node.next_key
            yield curr_key, val
            curr_key = next_key

    def items(self):
        return list(self.iteritems())

    def sort(self, cmp=None, key=None, reverse=False):
        items = [(k, v) for k, v in self.iteritems()]
        if cmp is not None:
            key = functools.cmp_to_key(cmp)
        if key is not None:
            items = sorted(items, key=key)
        else:
            items = sorted(items, key=lambda x: x[1])
        if reverse:
            items.reverse()
        self.clear()
        self.__init__(items)

    def clear(self):
        dict_ = self._dict_impl()
        dict_.clear(self)
        dict_.__setattr__(self, 'lh', _nil)
        dict_.__setattr__(self, 'lt', _nil)

    def copy(self):
        return self.__class__(self)

    def update(self, data=(), **kwds):
        if kwds:
            raise TypeError(
                'update() of ordered dict takes no keyword arguments to avoid '
                'an ordering trap.'
            )
        if hasattr(data, 'items'):
            data = data.items()
        for key, val in data:
            self[key] = val

    def setdefault(self, key, default=None):
        try:
            return self[key]
        except KeyError:
            self[key] = default
            return default

    def pop(self, key, default=_nil):
        try:
            val = self[key]
            del self[key]
            return val
        except KeyError:
            if default == _nil:
                raise
            return default

    def popitem(self):
        try:
            dict_ = self._dict_impl()
            key = dict_.__getattribute__(self, 'lt')
            return key, self.pop(key)
        except KeyError:
            raise KeyError("'popitem(): ordered dictionary is empty'")

    def riterkeys(self):
        """To iterate on keys in reversed order."""
        dict_ = self._dict_impl()
        curr_key = dict_.__getattribute__(self, 'lt')
        while curr_key != _nil:
            yield curr_key
            curr_key = dict_.__getitem__(self, curr_key).prev_key

    __reversed__ = riterkeys

    def rkeys(self):
        """List of the keys in reversed order."""
        return list(self.riterkeys())

    def ritervalues(self):
        """To iterate on values in reversed order."""
        dict_ = self._dict_impl()
        curr_key = dict_.__getattribute__(self, 'lt')
        while curr_key != _nil:
            node = dict_.__getitem__(self, curr_key)
            curr_key = node.prev_key
            yield node.value

    def rvalues(self):
        """List of the values in reversed order."""
        return list(self.ritervalues())

    def riteritems(self):
        """To iterate on (key, value) in reversed order."""
        dict_ = self._dict_impl()
        curr_key = dict_.__getattribute__(self, 'lt')
        while curr_key != _nil:
            node = dict_.__getitem__(self, curr_key)
            pred_key = node.prev_key
            val = node.value
            yield curr_key, val
            curr_key = pred_key

    def ritems(self):
        """List of the (key, value) in reversed order."""
        return list(self.riteritems())

    def firstkey(self):
        if self:
            return self._dict_impl().__getattribute__(self, 'lh')
        else:
            raise KeyError('Ordered dictionary is empty')

    @property
    def first_key(self):
        return self.firstkey()

    def lastkey(self):
        if self:
            return self._dict_impl().__getattribute__(self, 'lt')
        else:
            raise KeyError('Ordered dictionary is empty')

    @property
    def last_key(self):
        return self.lastkey()

    def as_dict(self):
        return self._dict_impl()(self.iteritems())

    def _repr(self):
        """_repr(): low level repr of the whole data contained in the codict.
        Useful for debugging.
        """
        dict_ = self._dict_impl()
        form = 'codict low level repr lh,lt,data: %r, %r, %s'
        return form % (
            dict_.__getattribute__(self, 'lh'),
            dict_.__getattribute__(self, 'lt'),
            dict_.__repr__(self),
        )

    def swap(self, a, b):
        if a == b:
            raise ValueError('Swap keys are equal')
        dict_ = self._dict_impl()

        node_a = dict_.__getitem__(self, a)
        node_b = dict_.__getitem__(self, b)

        # Store original links
        origin_a_prev = node_a.prev_key
        origin_a_next = node_a.next_key
        origin_b_prev = node_b.prev_key
        origin_b_next = node_b.next_key

        # Calculate new links
        new_a_prev = origin_b_prev
        new_a_next = origin_b_next
        new_b_prev = origin_a_prev
        new_b_next = origin_a_next

        # Handle neighbor case
        if new_a_prev == a:
            new_a_prev = b
            new_b_next = a
        if new_b_prev == b:
            new_b_prev = a
            new_a_next = b

        # Update neighboring nodes
        if new_a_prev != _nil:
            dict_.__getitem__(self, new_a_prev).next_key = a
        if new_a_next != _nil:
            dict_.__getitem__(self, new_a_next).prev_key = a
        if new_b_prev != _nil:
            dict_.__getitem__(self, new_b_prev).next_key = b
        if new_b_next != _nil:
            dict_.__getitem__(self, new_b_next).prev_key = b

        # Update the nodes themselves
        node_a.prev_key = new_a_prev
        node_a.next_key = new_a_next
        node_b.prev_key = new_b_prev
        node_b.next_key = new_b_next

        # Update head/tail if necessary
        if new_a_prev == _nil:
            dict_.__setattr__(self, 'lh', a)
        if new_a_next == _nil:
            dict_.__setattr__(self, 'lt', a)
        if new_b_prev == _nil:
            dict_.__setattr__(self, 'lh', b)
        if new_b_next == _nil:
            dict_.__setattr__(self, 'lt', b)

    def insertbefore(self, ref, key, value):
        if ref == key:
            raise ValueError('Reference key and new key are equal')
        try:
            index = self.keys().index(ref)
        except ValueError:
            raise KeyError("Reference key '{}' not found".format(ref))

        dict_ = self._dict_impl()
        ref_node = dict_.__getitem__(self, ref)
        prev_key = ref_node.prev_key

        # Create new node
        new_node = Node(prev_key, value, ref)
        dict_.__setitem__(self, key, new_node)

        # Update reference node
        ref_node.prev_key = key

        # Update previous node or head
        if prev_key != _nil:
            dict_.__getitem__(self, prev_key).next_key = key
        else:
            dict_.__setattr__(self, 'lh', key)

    def insertafter(self, ref, key, value):
        if ref == key:
            raise ValueError('Reference key and new key are equal')
        try:
            index = self.keys().index(ref)
        except ValueError:
            raise KeyError("Reference key '{}' not found".format(ref))

        dict_ = self._dict_impl()
        ref_node = dict_.__getitem__(self, ref)
        next_key = ref_node.next_key

        # Create new node
        new_node = Node(ref, value, next_key)
        dict_.__setitem__(self, key, new_node)

        # Update reference node
        ref_node.next_key = key

        # Update next node or tail
        if next_key != _nil:
            dict_.__getitem__(self, next_key).prev_key = key
        else:
            dict_.__setattr__(self, 'lt', key)

    def insertfirst(self, key, value):
        try:
            self.insertbefore(self.first_key, key, value)
        except KeyError:
            self[key] = value

    def insertlast(self, key, value):
        try:
            self.insertafter(self.last_key, key, value)
        except KeyError:
            self[key] = value

    def movebefore(self, ref, key):
        if ref == key:
            raise ValueError('Move keys are equal')
        dict_ = self._dict_impl()

        node = dict_.__getitem__(self, key)
        ref_node = dict_.__getitem__(self, ref)

        prev_key = node.prev_key
        next_key = node.next_key

        # Remove from current position
        if prev_key == _nil:
            dict_.__setattr__(self, 'lh', next_key)
        else:
            dict_.__getitem__(self, prev_key).next_key = next_key

        if next_key == _nil:
            dict_.__setattr__(self, 'lt', prev_key)
        else:
            dict_.__getitem__(self, next_key).prev_key = prev_key

        # Insert before ref
        ref_prev = ref_node.prev_key

        if ref_prev == _nil:
            node.prev_key = _nil
            node.next_key = ref
            ref_node.prev_key = key
            dict_.__setattr__(self, 'lh', key)
        else:
            ref_prev_node = dict_.__getitem__(self, ref_prev)
            node.prev_key = ref_prev
            node.next_key = ref
            ref_node.prev_key = key
            ref_prev_node.next_key = key

    def moveafter(self, ref, key):
        if ref == key:
            raise ValueError('Move keys are equal')
        dict_ = self._dict_impl()

        node = dict_.__getitem__(self, key)
        ref_node = dict_.__getitem__(self, ref)

        prev_key = node.prev_key
        next_key = node.next_key

        # Remove from current position
        if prev_key == _nil:
            dict_.__setattr__(self, 'lh', next_key)
        else:
            dict_.__getitem__(self, prev_key).next_key = next_key

        if next_key == _nil:
            dict_.__setattr__(self, 'lt', prev_key)
        else:
            dict_.__getitem__(self, next_key).prev_key = prev_key

        # Insert after ref
        ref_next = ref_node.next_key

        if ref_next == _nil:
            node.prev_key = ref
            node.next_key = _nil
            ref_node.next_key = key
            dict_.__setattr__(self, 'lt', key)
        else:
            ref_next_node = dict_.__getitem__(self, ref_next)
            node.prev_key = ref
            node.next_key = ref_next
            ref_node.next_key = key
            ref_next_node.prev_key = key

    def movefirst(self, key):
        first_key = self.first_key
        if first_key != key:
            self.movebefore(first_key, key)

    def movelast(self, key):
        last_key = self.last_key
        if last_key != key:
            self.moveafter(last_key, key)

    def next_key(self, key):
        node = self._dict_impl().__getitem__(self, key)
        if node.next_key == _nil:
            raise KeyError('No next key')
        return node.next_key

    def prev_key(self, key):
        node = self._dict_impl().__getitem__(self, key)
        if node.prev_key == _nil:
            raise KeyError('No previous key')
        return node.prev_key

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
    def _dict_impl(self):
        return dict
