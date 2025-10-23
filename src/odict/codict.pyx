# Python Software Foundation License
# cython: language_level=3
import copy
import functools
import sys
from cpython.ref cimport Py_INCREF, Py_DECREF
from cpython.object cimport PyObject
from cpython.mem cimport PyMem_Malloc, PyMem_Free


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


# C struct for the linked list nodes
cdef struct Node:
    PyObject* prev_key
    PyObject* value
    PyObject* next_key


class _codict(object):
    """Cython-optimized ordered dict data structure using C structs.

    Uses C pointers instead of Python lists for O(1) dict operations.
    Maintains insertion order; overwriting values doesn't change order.
    """

    def _dict_impl(self):
        return None

    def _list_factory(self):
        # Not used in C implementation, kept for API compatibility
        return list

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

    cdef Node* _get_node(self, key):
        """Get the C struct node for a key."""
        cdef dict dict_impl = self._dict_impl()
        cdef object node_obj = dict_impl.__getitem__(self, key)
        return <Node*><size_t>node_obj

    cdef void _set_node(self, key, Node* node):
        """Store a C struct node for a key."""
        cdef dict dict_impl = self._dict_impl()
        # Store the pointer address as an int
        dict_impl.__setitem__(self, key, <size_t>node)

    cdef Node* _create_node(self, prev_key, value, next_key):
        """Create a new node with proper reference counting."""
        cdef Node* node = <Node*>PyMem_Malloc(sizeof(Node))
        if node == NULL:
            raise MemoryError()

        Py_INCREF(prev_key)
        Py_INCREF(value)
        Py_INCREF(next_key)

        node.prev_key = <PyObject*>prev_key
        node.value = <PyObject*>value
        node.next_key = <PyObject*>next_key

        return node

    cdef void _free_node(self, Node* node):
        """Free a node and decrement references."""
        if node == NULL:
            return

        Py_DECREF(<object>node.prev_key)
        Py_DECREF(<object>node.value)
        Py_DECREF(<object>node.next_key)

        PyMem_Free(node)

    def __getitem__(self, key):
        cdef Node* node = self._get_node(key)
        return <object>node.value

    def __setitem__(self, key, val):
        dict_ = self._dict_impl()
        try:
            # Key exists, update value
            node = self._get_node(key)
            old_val = <object>node.value
            Py_DECREF(old_val)
            Py_INCREF(val)
            node.value = <PyObject*>val
        except KeyError:
            # New key, create node and link it
            lt = dict_.__getattribute__(self, 'lt')
            new_node = self._create_node(lt, val, _nil)
            self._set_node(key, new_node)

            if lt == _nil:
                dict_.__setattr__(self, 'lh', key)
            else:
                lt_node = self._get_node(lt)
                Py_DECREF(<object>lt_node.next_key)
                Py_INCREF(key)
                lt_node.next_key = <PyObject*>key
            dict_.__setattr__(self, 'lt', key)

    def __delitem__(self, key):
        dict_ = self._dict_impl()
        cdef Node* node = self._get_node(key)

        pred = <object>node.prev_key
        succ = <object>node.next_key

        if pred == _nil:
            dict_.__setattr__(self, 'lh', succ)
        else:
            pred_node = self._get_node(pred)
            Py_DECREF(<object>pred_node.next_key)
            Py_INCREF(succ)
            pred_node.next_key = <PyObject*>succ

        if succ == _nil:
            dict_.__setattr__(self, 'lt', pred)
        else:
            succ_node = self._get_node(succ)
            Py_DECREF(<object>succ_node.prev_key)
            Py_INCREF(pred)
            succ_node.prev_key = <PyObject*>pred

        self._free_node(node)
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

    def get(self, k, x=None):
        if k in self:
            node = self._get_node(k)
            return <object>node.value
        else:
            return x

    def __iter__(self):
        dict_ = self._dict_impl()
        curr_key = dict_.__getattribute__(self, 'lh')
        while curr_key != _nil:
            yield curr_key
            node = self._get_node(curr_key)
            curr_key = <object>node.next_key

    iterkeys = __iter__

    def keys(self):
        return list(self.iterkeys())

    def alter_key(self, old_key, new_key):
        dict_ = self._dict_impl()
        cdef Node* node = self._get_node(old_key)

        prev_key = <object>node.prev_key
        next_key = <object>node.next_key

        dict_.__delitem__(self, old_key)

        if prev_key != _nil:
            prev_node = self._get_node(prev_key)
            Py_DECREF(<object>prev_node.next_key)
            Py_INCREF(new_key)
            prev_node.next_key = <PyObject*>new_key
        else:
            dict_.__setattr__(self, 'lh', new_key)

        if next_key != _nil:
            next_node = self._get_node(next_key)
            Py_DECREF(<object>next_node.prev_key)
            Py_INCREF(new_key)
            next_node.prev_key = <PyObject*>new_key
        else:
            dict_.__setattr__(self, 'lt', new_key)

        dict_.__setitem__(self, new_key, <size_t>node)

    def itervalues(self):
        dict_ = self._dict_impl()
        curr_key = dict_.__getattribute__(self, 'lh')
        while curr_key != _nil:
            node = self._get_node(curr_key)
            val = <object>node.value
            curr_key = <object>node.next_key
            yield val

    def values(self):
        return list(self.itervalues())

    def iteritems(self):
        dict_ = self._dict_impl()
        curr_key = dict_.__getattribute__(self, 'lh')
        while curr_key != _nil:
            node = self._get_node(curr_key)
            val = <object>node.value
            next_key = <object>node.next_key
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
        # Free all nodes before clearing
        for key in list(dict_.keys(self)):
            node = self._get_node(key)
            self._free_node(node)
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
            node = self._get_node(curr_key)
            curr_key = <object>node.prev_key

    __reversed__ = riterkeys

    def rkeys(self):
        """List of the keys in reversed order."""
        return list(self.riterkeys())

    def ritervalues(self):
        """To iterate on values in reversed order."""
        dict_ = self._dict_impl()
        curr_key = dict_.__getattribute__(self, 'lt')
        while curr_key != _nil:
            node = self._get_node(curr_key)
            prev_key = <object>node.prev_key
            val = <object>node.value
            curr_key = prev_key
            yield val

    def rvalues(self):
        """List of the values in reversed order."""
        return list(self.ritervalues())

    def riteritems(self):
        """To iterate on (key, value) in reversed order."""
        dict_ = self._dict_impl()
        curr_key = dict_.__getattribute__(self, 'lt')
        while curr_key != _nil:
            node = self._get_node(curr_key)
            pred_key = <object>node.prev_key
            val = <object>node.value
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

        cdef Node* node_a = self._get_node(a)
        cdef Node* node_b = self._get_node(b)

        origin_a_prev = <object>node_a.prev_key
        origin_a_next = <object>node_a.next_key
        origin_b_prev = <object>node_b.prev_key
        origin_b_next = <object>node_b.next_key

        # Swap node positions
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

        # Update prev nodes
        if new_a_prev != _nil:
            prev_node = self._get_node(new_a_prev)
            Py_DECREF(<object>prev_node.next_key)
            Py_INCREF(a)
            prev_node.next_key = <PyObject*>a
        if new_b_prev != _nil:
            prev_node = self._get_node(new_b_prev)
            Py_DECREF(<object>prev_node.next_key)
            Py_INCREF(b)
            prev_node.next_key = <PyObject*>b

        # Update next nodes
        if new_a_next != _nil:
            next_node = self._get_node(new_a_next)
            Py_DECREF(<object>next_node.prev_key)
            Py_INCREF(a)
            next_node.prev_key = <PyObject*>a
        if new_b_next != _nil:
            next_node = self._get_node(new_b_next)
            Py_DECREF(<object>next_node.prev_key)
            Py_INCREF(b)
            next_node.prev_key = <PyObject*>b

        # Update nodes a and b
        Py_DECREF(<object>node_a.prev_key)
        Py_DECREF(<object>node_a.next_key)
        Py_INCREF(new_a_prev)
        Py_INCREF(new_a_next)
        node_a.prev_key = <PyObject*>new_a_prev
        node_a.next_key = <PyObject*>new_a_next

        Py_DECREF(<object>node_b.prev_key)
        Py_DECREF(<object>node_b.next_key)
        Py_INCREF(new_b_prev)
        Py_INCREF(new_b_next)
        node_b.prev_key = <PyObject*>new_b_prev
        node_b.next_key = <PyObject*>new_b_next

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
        cdef Node* ref_node = self._get_node(ref)
        prev_key = <object>ref_node.prev_key

        # Create new node
        new_node = self._create_node(prev_key, value, ref)
        self._set_node(key, new_node)

        # Update reference node
        Py_DECREF(<object>ref_node.prev_key)
        Py_INCREF(key)
        ref_node.prev_key = <PyObject*>key

        # Update previous node or head
        if prev_key != _nil:
            prev_node = self._get_node(prev_key)
            Py_DECREF(<object>prev_node.next_key)
            Py_INCREF(key)
            prev_node.next_key = <PyObject*>key
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
        cdef Node* ref_node = self._get_node(ref)
        next_key = <object>ref_node.next_key

        # Create new node
        new_node = self._create_node(ref, value, next_key)
        self._set_node(key, new_node)

        # Update reference node
        Py_DECREF(<object>ref_node.next_key)
        Py_INCREF(key)
        ref_node.next_key = <PyObject*>key

        # Update next node or tail
        if next_key != _nil:
            next_node = self._get_node(next_key)
            Py_DECREF(<object>next_node.prev_key)
            Py_INCREF(key)
            next_node.prev_key = <PyObject*>key
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

        cdef Node* node = self._get_node(key)
        cdef Node* ref_node = self._get_node(ref)

        prev_key = <object>node.prev_key
        next_key = <object>node.next_key

        # Remove from current position
        if prev_key == _nil:
            dict_.__setattr__(self, 'lh', next_key)
        else:
            prev_node = self._get_node(prev_key)
            Py_DECREF(<object>prev_node.next_key)
            Py_INCREF(next_key)
            prev_node.next_key = <PyObject*>next_key

        if next_key == _nil:
            dict_.__setattr__(self, 'lt', prev_key)
        else:
            next_node = self._get_node(next_key)
            Py_DECREF(<object>next_node.prev_key)
            Py_INCREF(prev_key)
            next_node.prev_key = <PyObject*>prev_key

        # Insert before ref
        ref_prev = <object>ref_node.prev_key

        if ref_prev == _nil:
            Py_DECREF(<object>node.prev_key)
            Py_INCREF(_nil)
            node.prev_key = <PyObject*>_nil
            Py_DECREF(<object>node.next_key)
            Py_INCREF(ref)
            node.next_key = <PyObject*>ref
            Py_DECREF(<object>ref_node.prev_key)
            Py_INCREF(key)
            ref_node.prev_key = <PyObject*>key
            dict_.__setattr__(self, 'lh', key)
        else:
            ref_prev_node = self._get_node(ref_prev)
            Py_DECREF(<object>node.prev_key)
            Py_INCREF(ref_prev)
            node.prev_key = <PyObject*>ref_prev
            Py_DECREF(<object>node.next_key)
            Py_INCREF(ref)
            node.next_key = <PyObject*>ref
            Py_DECREF(<object>ref_node.prev_key)
            Py_INCREF(key)
            ref_node.prev_key = <PyObject*>key
            Py_DECREF(<object>ref_prev_node.next_key)
            Py_INCREF(key)
            ref_prev_node.next_key = <PyObject*>key

    def moveafter(self, ref, key):
        if ref == key:
            raise ValueError('Move keys are equal')
        dict_ = self._dict_impl()

        cdef Node* node = self._get_node(key)
        cdef Node* ref_node = self._get_node(ref)

        prev_key = <object>node.prev_key
        next_key = <object>node.next_key

        # Remove from current position
        if prev_key == _nil:
            dict_.__setattr__(self, 'lh', next_key)
        else:
            prev_node = self._get_node(prev_key)
            Py_DECREF(<object>prev_node.next_key)
            Py_INCREF(next_key)
            prev_node.next_key = <PyObject*>next_key

        if next_key == _nil:
            dict_.__setattr__(self, 'lt', prev_key)
        else:
            next_node = self._get_node(next_key)
            Py_DECREF(<object>next_node.prev_key)
            Py_INCREF(prev_key)
            next_node.prev_key = <PyObject*>prev_key

        # Insert after ref
        ref_next = <object>ref_node.next_key

        if ref_next == _nil:
            Py_DECREF(<object>node.prev_key)
            Py_INCREF(ref)
            node.prev_key = <PyObject*>ref
            Py_DECREF(<object>node.next_key)
            Py_INCREF(_nil)
            node.next_key = <PyObject*>_nil
            Py_DECREF(<object>ref_node.next_key)
            Py_INCREF(key)
            ref_node.next_key = <PyObject*>key
            dict_.__setattr__(self, 'lt', key)
        else:
            ref_next_node = self._get_node(ref_next)
            Py_DECREF(<object>node.prev_key)
            Py_INCREF(ref)
            node.prev_key = <PyObject*>ref
            Py_DECREF(<object>node.next_key)
            Py_INCREF(ref_next)
            node.next_key = <PyObject*>ref_next
            Py_DECREF(<object>ref_node.next_key)
            Py_INCREF(key)
            ref_node.next_key = <PyObject*>key
            Py_DECREF(<object>ref_next_node.prev_key)
            Py_INCREF(key)
            ref_next_node.prev_key = <PyObject*>key

    def movefirst(self, key):
        first_key = self.first_key
        if first_key != key:
            self.movebefore(first_key, key)

    def movelast(self, key):
        last_key = self.last_key
        if last_key != key:
            self.moveafter(last_key, key)

    def next_key(self, key):
        cdef Node* node = self._get_node(key)
        next_k = <object>node.next_key
        if next_k == _nil:
            raise KeyError('No next key')
        return next_k

    def prev_key(self, key):
        cdef Node* node = self._get_node(key)
        prev_k = <object>node.prev_key
        if prev_k == _nil:
            raise KeyError('No previous key')
        return prev_k

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

    def __dealloc__(self):
        """Cleanup when object is destroyed."""
        dict_ = self._dict_impl()
        if dict_ and hasattr(self, '__dict__'):
            for key in list(dict_.keys(self)):
                try:
                    node = self._get_node(key)
                    self._free_node(node)
                except:
                    pass


class codict(_codict, dict):
    def _dict_impl(self):
        return dict
