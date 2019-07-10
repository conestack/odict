# Python Software Foundation License
import copy
import functools
import sys


ITER_FUNC = 'iteritems' if sys.version_info[0] < 3 else 'items'


class _Nil(object):
    """Q: it feels like using the class with "is" and "is not" instead of
    "==" and "!=" should be faster.

    A: This would break implementations which use pickle for persisting.
    """

    def __repr__(self):
        return "nil"

    def __eq__(self, other):
        if (isinstance(other, _Nil)):
            return True
        else:
            return NotImplemented

    def __ne__(self, other):
        if (isinstance(other, _Nil)):
            return False
        else:
            return NotImplemented

    def __hash__(self):
        return sys.maxsize


_nil = _Nil()


class _odict(object):
    """Ordered dict data structure, with O(1) complexity for dict operations
    that modify one element.

    Overwriting values doesn't change their original sequential order.
    """

    def _dict_impl(self):
        return None

    def __init__(self, data=(), **kwds):
        """This doesn't accept keyword initialization as normal dicts to avoid
        a trap - inside a function or method the keyword args are accessible
        only as a dict, without a defined order, so their original order is
        lost.
        """
        if kwds:
            raise TypeError("__init__() of ordered dict takes no keyword "
                            "arguments to avoid an ordering trap.")
        dict_impl = self._dict_impl()
        if dict_impl is None:
            raise TypeError("No dict implementation class provided.")
        dict_impl.__init__(self)
        # If you give a normal dict, then the order of elements is undefined
        if hasattr(data, ITER_FUNC):
            for key, val in getattr(data, ITER_FUNC)():
                self[key] = val
        else:
            for key, val in data:
                self[key] = val

    # Double-linked list header
    def _get_lh(self):
        dict_impl = self._dict_impl()
        if not hasattr(self, '_lh'):
            dict_impl.__setattr__(self, '_lh', _nil)
        return dict_impl.__getattribute__(self, '_lh')

    def _set_lh(self, val):
        self._dict_impl().__setattr__(self, '_lh', val)

    lh = property(_get_lh, _set_lh)

    # Double-linked list tail
    def _get_lt(self):
        dict_impl = self._dict_impl()
        if not hasattr(self, '_lt'):
            dict_impl.__setattr__(self, '_lt', _nil)
        return dict_impl.__getattribute__(self, '_lt')

    def _set_lt(self, val):
        self._dict_impl().__setattr__(self, '_lt', val)

    lt = property(_get_lt, _set_lt)

    def __getitem__(self, key):
        return self._dict_impl().__getitem__(self, key)[1]

    def __setitem__(self, key, val):
        dict_impl = self._dict_impl()
        try:
            dict_impl.__getitem__(self, key)[1] = val
        except KeyError:
            new = [dict_impl.__getattribute__(self, 'lt'), val, _nil]
            dict_impl.__setitem__(self, key, new)
            if dict_impl.__getattribute__(self, 'lt') == _nil:
                dict_impl.__setattr__(self, 'lh', key)
            else:
                dict_impl.__getitem__(
                    self, dict_impl.__getattribute__(self, 'lt'))[2] = key
            dict_impl.__setattr__(self, 'lt', key)

    def __delitem__(self, key):
        dict_impl = self._dict_impl()
        pred, _, succ = self._dict_impl().__getitem__(self, key)
        if pred == _nil:
            dict_impl.__setattr__(self, 'lh', succ)
        else:
            dict_impl.__getitem__(self, pred)[2] = succ
        if succ == _nil:
            dict_impl.__setattr__(self, 'lt', pred)
        else:
            dict_impl.__getitem__(self, succ)[0] = pred
        dict_impl.__delitem__(self, key)

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
        for k, v in getattr(self.__dict__, ITER_FUNC)():
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
        pairs = ("%r: %r" % (k, v) for k, v in getattr(self, ITER_FUNC)())
        return "{%s}" % ", ".join(pairs)

    def __repr__(self):
        if self:
            pairs = (
                "(%r, %r)" % (k, v) for k, v in getattr(self, ITER_FUNC)()
            )
            return "%s([%s])" % (self.__class__.__name__, ", ".join(pairs))
        else:
            return "%s()" % self.__class__.__name__

    def get(self, k, x=None):
        if k in self:
            return self._dict_impl().__getitem__(self, k)[1]
        else:
            return x

    def __iter__(self):
        dict_impl = self._dict_impl()
        curr_key = dict_impl.__getattribute__(self, 'lh')
        while curr_key != _nil:
            yield curr_key
            curr_key = dict_impl.__getitem__(self, curr_key)[2]

    iterkeys = __iter__

    def keys(self):
        return list(self.iterkeys())

    def alter_key(self, old_key, new_key):
        dict_impl = self._dict_impl()
        val = dict_impl.__getitem__(self, old_key)
        dict_impl.__delitem__(self, old_key)
        if val[0] != _nil:
            prev = dict_impl.__getitem__(self, val[0])
            dict_impl.__setitem__(self, val[0], [prev[0], prev[1], new_key])
        else:
            dict_impl.__setattr__(self, 'lh', new_key)
        if val[2] != _nil:
            next = dict_impl.__getitem__(self, val[2])
            dict_impl.__setitem__(self, val[2], [new_key, next[1], next[2]])
        else:
            dict_impl.__setattr__(self, 'lt', new_key)
        dict_impl.__setitem__(self, new_key, val)

    def itervalues(self):
        dict_impl = self._dict_impl()
        curr_key = dict_impl.__getattribute__(self, 'lh')
        while curr_key != _nil:
            _, val, curr_key = dict_impl.__getitem__(self, curr_key)
            yield val

    def values(self):
        return list(self.itervalues())

    def iteritems(self):
        dict_impl = self._dict_impl()
        curr_key = dict_impl.__getattribute__(self, 'lh')
        while curr_key != _nil:
            _, val, next_key = dict_impl.__getitem__(self, curr_key)
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
        dict_impl = self._dict_impl()
        dict_impl.clear(self)
        dict_impl.__setattr__(self, 'lh', _nil)
        dict_impl.__setattr__(self, 'lt', _nil)

    def copy(self):
        return self.__class__(self)

    def update(self, data=(), **kwds):
        if kwds:
            raise TypeError(
                "update() of ordered dict takes no keyword arguments to avoid "
                "an ordering trap."
            )
        if hasattr(data, ITER_FUNC):
            data = getattr(data, ITER_FUNC)()
        for key, val in data:
            self[key] = val

    def setdefault(self, k, x=None):
        try:
            return self[k]
        except KeyError:
            self[k] = x
            return x

    def pop(self, k, x=_nil):
        try:
            val = self[k]
            del self[k]
            return val
        except KeyError:
            if x == _nil:
                raise
            return x

    def popitem(self):
        try:
            dict_impl = self._dict_impl()
            key = dict_impl.__getattribute__(self, 'lt')
            return key, self.pop(key)
        except KeyError:
            raise KeyError("'popitem(): ordered dictionary is empty'")

    def riterkeys(self):
        """To iterate on keys in reversed order.
        """
        dict_impl = self._dict_impl()
        curr_key = dict_impl.__getattribute__(self, 'lt')
        while curr_key != _nil:
            yield curr_key
            curr_key = dict_impl.__getitem__(self, curr_key)[0]

    __reversed__ = riterkeys

    def rkeys(self):
        """List of the keys in reversed order.
        """
        return list(self.riterkeys())

    def ritervalues(self):
        """To iterate on values in reversed order.
        """
        dict_impl = self._dict_impl()
        curr_key = dict_impl.__getattribute__(self, 'lt')
        while curr_key != _nil:
            curr_key, val, _ = dict_impl.__getitem__(self, curr_key)
            yield val

    def rvalues(self):
        """List of the values in reversed order.
        """
        return list(self.ritervalues())

    def riteritems(self):
        """To iterate on (key, value) in reversed order.
        """
        dict_impl = self._dict_impl()
        curr_key = dict_impl.__getattribute__(self, 'lt')
        while curr_key != _nil:
            pred_key, val, _ = dict_impl.__getitem__(self, curr_key)
            yield curr_key, val
            curr_key = pred_key

    def ritems(self):
        """List of the (key, value) in reversed order.
        """
        return list(self.riteritems())

    def firstkey(self):
        if self:
            return self._dict_impl().__getattribute__(self, 'lh')
        else:
            raise KeyError("'firstkey(): ordered dictionary is empty'")

    def lastkey(self):
        if self:
            return self._dict_impl().__getattribute__(self, 'lt')
        else:
            raise KeyError("'lastkey(): ordered dictionary is empty'")

    def as_dict(self):
        return self._dict_impl()(self.iteritems())

    def _repr(self):
        """_repr(): low level repr of the whole data contained in the odict.
        Useful for debugging.
        """
        dict_impl = self._dict_impl()
        form = "odict low level repr lh,lt,data: %r, %r, %s"
        return form % (dict_impl.__getattribute__(self, 'lh'),
                       dict_impl.__getattribute__(self, 'lt'),
                       dict_impl.__repr__(self))

    def swap(self, a, b):
        if a == b:
            raise ValueError('Swap keys are equal')
        dict_impl = self._dict_impl()
        orgin_a = dict_impl.__getitem__(self, a)
        orgin_b = dict_impl.__getitem__(self, b)
        new_a = [orgin_b[0], orgin_a[1], orgin_b[2]]
        new_b = [orgin_a[0], orgin_b[1], orgin_a[2]]
        if new_a[0] == a:
            new_a[0] = b
            new_b[2] = a
        if new_b[0] == b:
            new_b[0] = a
            new_a[2] = b
        if new_a[0] != _nil:
            dict_impl.__getitem__(self, new_a[0])[2] = a
        if new_a[2] != _nil:
            dict_impl.__getitem__(self, new_a[2])[0] = a
        if new_b[0] != _nil:
            dict_impl.__getitem__(self, new_b[0])[2] = b
        if new_b[2] != _nil:
            dict_impl.__getitem__(self, new_b[2])[0] = b
        dict_impl.__setitem__(self, a, new_a)
        dict_impl.__setitem__(self, b, new_b)
        if new_a[0] == _nil:
            dict_impl.__setattr__(self, 'lh', a)
        if new_a[2] == _nil:
            dict_impl.__setattr__(self, 'lt', a)
        if new_b[0] == _nil:
            dict_impl.__setattr__(self, 'lh', b)
        if new_b[2] == _nil:
            dict_impl.__setattr__(self, 'lt', b)

    def insertbefore(self, ref, key, value):
        if ref == key:
            raise ValueError('Reference key and new key are equal')
        try:
            index = self.keys().index(ref)
        except ValueError:
            raise KeyError('Reference key \'{}\' not found'.format(ref))
        prevkey = prevval = None
        dict_impl = self._dict_impl()
        if index > 0:
            prevkey = self.keys()[index - 1]
            prevval = dict_impl.__getitem__(self, prevkey)
        if prevval is not None:
            dict_impl.__getitem__(self, prevkey)[2] = key
            newval = [prevkey, value, ref]
        else:
            dict_impl.__setattr__(self, 'lh', key)
            newval = [_nil, value, ref]
        dict_impl.__getitem__(self, ref)[0] = key
        dict_impl.__setitem__(self, key, newval)

    def insertafter(self, ref, key, value):
        if ref == key:
            raise ValueError('Reference key and new key are equal')
        try:
            index = self.keys().index(ref)
        except ValueError:
            raise KeyError('Reference key \'{}\' not found'.format(ref))
        nextkey = nextval = None
        keys = self.keys()
        dict_impl = self._dict_impl()
        if index < len(keys) - 1:
            nextkey = keys[index + 1]
            nextval = dict_impl.__getitem__(self, nextkey)
        if nextval is not None:
            dict_impl.__getitem__(self, nextkey)[0] = key
            newval = [ref, value, nextkey]
        else:
            dict_impl.__setattr__(self, 'lt', key)
            newval = [ref, value, _nil]
        dict_impl.__getitem__(self, ref)[2] = key
        dict_impl.__setitem__(self, key, newval)

    def insertfirst(self, key, value):
        keys = self.keys()
        if not keys:
            self[key] = value
            return
        self.insertbefore(keys[0], key, value)

    def insertlast(self, key, value):
        keys = self.keys()
        if not keys:
            self[key] = value
            return
        self.insertafter(keys[-1], key, value)


class odict(_odict, dict):

    def _dict_impl(self):
        return dict
