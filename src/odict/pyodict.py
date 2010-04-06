# Python Software Foundation License

class _Nil(object):
    
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
        
_nil = _Nil()

class odict(dict):
    """Ordered dict data structure, with O(1) complexity for dict operations
    that modify one element.
    
    Overwriting values doesn't change their original sequential order.
    """
    
    def __init__(self, data=(), **kwds):
        """This doesn't accept keyword initialization as normal dicts to avoid
        a trap - inside a function or method the keyword args are accessible
        only as a dict, without a defined order, so their original order is
        lost.
        """
        if kwds:
            raise TypeError("__init__() of ordered dict takes no keyword "
                            "arguments to avoid an ordering trap.")
        dict.__init__(self)
        # If you give a normal dict, then the order of elements is undefined
        if hasattr(data, "iteritems"):
            for key, val in data.iteritems():
                self[key] = val
        else:
            for key, val in data:
                self[key] = val
    
    # Double-linked list header
    def _get_lh(self):
        if not hasattr(self, '_lh'):
            object.__setattr__(self, '_lh', _nil)
        return object.__getattribute__(self, '_lh')
    
    def _set_lh(self, val):
        object.__setattr__(self, '_lh', val)
    
    lh = property(_get_lh, _set_lh)
    
    # Double-linked list tail
    def _get_lt(self):
        if not hasattr(self, '_lt'):
            object.__setattr__(self, '_lt', _nil)
        return object.__getattribute__(self, '_lt')
    
    def _set_lt(self, val):
        object.__setattr__(self, '_lt', val)
    
    lt = property(_get_lt, _set_lt)

    def __getitem__(self, key):
        return dict.__getitem__(self, key)[1]

    def __setitem__(self, key, val):
        try:
            dict.__getitem__(self, key)[1] = val
        except KeyError, e:
            new = [object.__getattribute__(self, 'lt'), val, _nil]
            dict.__setitem__(self, key, new)
            if object.__getattribute__(self, 'lt') == _nil:
                object.__setattr__(self, 'lh', key)
            else:
                dict.__getitem__(self,
                                 object.__getattribute__(self, 'lt'))[2] = key
            object.__setattr__(self, 'lt', key)

    def __delitem__(self, key):
        pred, _ ,succ= dict.__getitem__(self, key)
        if pred == _nil:
            object.__setattr__(self, 'lh', succ)
        else:
            dict.__getitem__(self, pred)[2] = succ
        if succ == _nil:
            object.__setattr__(self, 'lt', pred)
        else:
            dict.__getitem__(self, succ)[0] = pred
        dict.__delitem__(self, key)
    
    def __contains__(self, key):
        return key in self.keys()
    
    def __len__(self):
        return len(self.keys())

    def __str__(self):
        pairs = ("%r: %r" % (k, v) for k, v in self.iteritems())
        return "{%s}" % ", ".join(pairs)

    def __repr__(self):
        if self:
            pairs = ("(%r, %r)" % (k, v) for k, v in self.iteritems())
            return "odict([%s])" % ", ".join(pairs)
        else:
            return "odict()"
    
    def get(self, k, x=None):
        if k in self:
            return dict.__getitem__(self, k)[1]
        else:
            return x

    def __iter__(self):
        curr_key = object.__getattribute__(self, 'lh')
        while curr_key != _nil:
            yield curr_key
            curr_key = dict.__getitem__(self, curr_key)[2]

    iterkeys = __iter__

    def keys(self):
        return list(self.iterkeys())

    def itervalues(self):
        curr_key = object.__getattribute__(self, 'lh')
        while curr_key != _nil:
            _, val, curr_key = dict.__getitem__(self, curr_key)
            yield val

    def values(self):
        return list(self.itervalues())

    def iteritems(self):
        curr_key = object.__getattribute__(self, 'lh')
        while curr_key != _nil:
            _, val, next_key = dict.__getitem__(self, curr_key)
            yield curr_key, val
            curr_key = next_key

    def items(self):
        return list(self.iteritems())
    
    def sort(self, cmp=None, key=None, reverse=False):
        cmpkey = key
        items = [(key, value) for key, value in self.items()]
        if cmp is None and cmpkey is None:
            def cmp(x, y):
                if x[1] < y[1]: return -1
                if x[1] > y[1]: return 1
                return 0
        if cmp is not None:
            items = sorted(items, cmp=cmp)
        else:
            items = sorted(items, key=cmpkey)
        if reverse:
            items.reverse()
        self.clear()
        self.__init__(items)

    def clear(self):
        dict.clear(self)
        object.__setattr__(self, 'lh', _nil)
        object.__setattr__(self, 'lt', _nil)

    def copy(self):
        return self.__class__(self)

    def update(self, data=(), **kwds):
        if kwds:
            raise TypeError("update() of ordered dict takes no keyword "
                            "arguments to avoid an ordering trap.")
        if hasattr(data, "iteritems"):
            for key, val in data.iteritems():
                self[key] = val
        else:
            for key, val in data:
                self[key] = val

    @classmethod
    def fromkeys(cls, seq, value=None):
        new = cls()
        for key in seq:
            new[key] = value
        return new

    def setdefault(self, k, x=None):
        if k in self:
            return self[k]
        else:
            self[k] = x
            return x

    def pop(self, k, x=_nil):
        if k in self:
            val = self[k]
            del self[k]
            return val
        elif x == _nil:
            raise KeyError(k)
        else:
            return x

    def popitem(self):
        if self:
            key = object.__getattribute__(self, 'lt')
            val = dict.__getitem__(self, key)[1]
            self.__delitem__(key)
            return key, val
        else:
            raise KeyError("'popitem(): ordered dictionary is empty'")

    def riterkeys(self):
        """To iterate on keys in reversed order.
        """
        curr_key = object.__getattribute__(self, 'lt')
        while curr_key != _nil:
            yield curr_key
            curr_key = dict.__getitem__(self, curr_key)[0]

    __reversed__ = riterkeys

    def rkeys(self):
        """List of the keys in reversed order.
        """
        return list(self.riterkeys())

    def ritervalues(self):
        """To iterate on values in reversed order.
        """
        curr_key = object.__getattribute__(self, 'lt')
        while curr_key != _nil:
            curr_key, val, _ = dict.__getitem__(self, curr_key)
            yield val

    def rvalues(self):
        """List of the values in reversed order.
        """
        return list(self.ritervalues())

    def riteritems(self):
        """To iterate on (key, value) in reversed order.
        """
        curr_key = object.__getattribute__(self, 'lt')
        while curr_key != _nil:
            pred_key, val, _ = dict.__getitem__(self, curr_key)
            yield curr_key, val
            curr_key = pred_key

    def ritems(self):
        """List of the (key, value) in reversed order.
        """
        return list(self.riteritems())

    def firstkey(self):
        if self:
            return object.__getattribute__(self, 'lh')
        else:
            raise KeyError("'firstkey(): ordered dictionary is empty'")

    def lastkey(self):
        if self:
            return object.__getattribute__(self, 'lt')
        else:
            raise KeyError("'lastkey(): ordered dictionary is empty'")
    
    def as_dict(self):
        return dict(self.items())

    def _repr(self):
        """_repr(): low level repr of the whole data contained in the odict.
        Useful for debugging.
        """
        form = "odict low level repr lh,lt,data: %r, %r, %s"
        return form % (object.__getattribute__(self, 'lh'),
                       object.__getattribute__(self, 'lt'),
                       dict.__repr__(self))