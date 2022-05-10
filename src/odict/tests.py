# Python Software Foundation License
from odict import odict
from odict.pyodict import _nil
from odict.pyodict import _odict
import copy
import pickle
import sys
import unittest


class TestOdict(unittest.TestCase):

    def assertRaisesWithMessage(self, msg, func, exc, *args, **kwargs):
        try:
            func(*args, **kwargs)
        except exc as inst:
            self.assertEqual(str(inst), msg)

    def test_abstract_superclass(self):
        # Abstract superclass provides no concrete _dict_impl class.
        msg = 'No dict implementation class provided.'
        self.assertRaisesWithMessage(msg, _odict, TypeError)
        o = odict()
        self.assertEqual(o._dict_impl(), dict)
        del o

    def test_init_with_kw(self):
        # Initialization with keyword arguments fails.
        msg = (
            '__init__() of ordered dict takes no keyword arguments to avoid '
            'an ordering trap.'
        )
        self.assertRaisesWithMessage(msg, odict, TypeError, a=1)

    def test_init_with_dict(self):
        # When initialized with a dict instance, the order of elements is
        # undefined.
        o = odict({'b': 2, 'a': 1, 'd': 4, 'c': 3})
        self.assertEqual(sorted(o.keys()), ['a', 'b', 'c', 'd'])
        self.assertEqual(o['a'], 1)
        self.assertEqual(o['b'], 2)
        self.assertEqual(o['c'], 3)
        self.assertEqual(o['d'], 4)

    def test_init_with_items(self):
        # When initialized with a list instance, the order of elements is
        # preserved.
        o = odict([('a', 1), ('b', 2), ('c', 3), ('d', 4)])
        self.assertEqual(o.items(), [('a', 1), ('b', 2), ('c', 3), ('d', 4)])

    def test_containment(self):
        # Test key containment with __iter__() and has_key().
        o = odict([('a', 1)])
        self.assertTrue('a' in o)
        self.assertFalse('foo' in o)
        self.assertTrue(o.has_key('a'))

    def test_get(self):
        # Test fetching values with get()
        o = odict([('a', 1)])
        self.assertEqual(o.get('a'), 1)
        self.assertEqual(o.get('foo', ''), '')

    def test_values(self):
        # Test fetching values with values()
        o = odict([('a', 1), ('b', 2), ('c', 3), ('d', 4)])
        self.assertEqual(o.values(), [1, 2, 3, 4])

    def test_update_with_kw(self):
        # update() with keyword arguments fails.
        o = odict()
        msg = (
            'update() of ordered dict takes no keyword arguments to avoid '
            'an ordering trap.'
        )
        self.assertRaisesWithMessage(msg, o.update, TypeError, foo=1)

    def test_update(self):
        # Test update().
        o2 = odict()
        o2.update(data=((1, 1), (2, 2)))
        self.assertEqual(o2.items(), [(1, 1), (2, 2)])
        o2.update(data={3: 3})
        self.assertEqual(o2.items(), [(1, 1), (2, 2), (3, 3)])

    def test_first_and_last_key(self):
        # Test first and last key.
        o = odict([('a', 1), ('b', 2), ('c', 3), ('d', 4)])
        self.assertEqual(o.firstkey(), 'a')
        self.assertEqual(o.first_key, 'a')
        self.assertEqual(o.lastkey(), 'd')
        self.assertEqual(o.last_key, 'd')
        o = odict()
        msg = "'Ordered dictionary is empty'"
        self.assertRaisesWithMessage(msg, o.firstkey, KeyError)
        self.assertRaisesWithMessage(msg, lambda: o.first_key, KeyError)
        msg = "'Ordered dictionary is empty'"
        self.assertRaisesWithMessage(msg, o.lastkey, KeyError)
        self.assertRaisesWithMessage(msg, lambda: o.last_key, KeyError)

    def test_reverse_iteration(self):
        # Reverse iteration
        o = odict([('a', 1), ('b', 2), ('c', 3), ('d', 4)])
        self.assertEqual([x for x in o.riterkeys()], ['d', 'c', 'b', 'a'])
        self.assertEqual(o.rkeys(), ['d', 'c', 'b', 'a'])
        self.assertEqual([x for x in o.ritervalues()], [4, 3, 2, 1])
        self.assertEqual(o.rvalues(), [4, 3, 2, 1])
        self.assertEqual(
            [x for x in o.riteritems()],
            [('d', 4), ('c', 3), ('b', 2), ('a', 1)]
        )
        self.assertEqual(
            o.ritems(),
            [('d', 4), ('c', 3), ('b', 2), ('a', 1)]
        )

    def test_fromkeys(self):
        # From keys initialization::
        o = odict.fromkeys((1, 2, 3), 'x')
        self.assertEqual(o.items(), [(1, 'x'), (2, 'x'), (3, 'x')])

    def test_setdefault(self):
        # Test ``setdefault``.
        o = odict([(1, 'x')])
        self.assertEqual(o.setdefault(1, 9999), 'x')
        self.assertEqual(o.setdefault(4, 9999), 9999)

    def test_pop(self):
        # Test pop and popitem
        o = odict([(1, 'a'), (2, 'b')])
        self.assertRaisesWithMessage('3', o.pop, KeyError, 3)
        self.assertEqual(o.pop(3, 'foo'), 'foo')
        self.assertEqual(o.pop(2), 'b')
        self.assertEqual(o.popitem(), (1, 'a'))
        msg = "\"'popitem(): ordered dictionary is empty'\""
        self.assertRaisesWithMessage(msg, o.popitem, KeyError)

    def test_delete(self):
        # Removal from empty odict
        o = odict()

        def delete():
            del o['1']
        self.assertRaisesWithMessage("'1'", delete, KeyError)
        # Removal from odict with one element
        o['1'] = 1
        del o['1']
        self.assertEqual([o.lh, o.lt, o], [_nil, _nil, odict()])
        self.assertEqual(
            o._repr(),
            'odict low level repr lh,lt,data: nil, nil, {}'
        )
        # Remove first element of the odict sequence
        o = odict([('1', 1), ('2', 2), ('3', 3)])
        del o['1']
        self.assertEqual(
            [o.lh, o.lt, o],
            ['2', '3', odict([('2', 2), ('3', 3)])]
        )
        # Remove element in the middle of the odict sequence
        o = odict([('1', 1), ('2', 2), ('3', 3)])
        del o['2']
        self.assertEqual(
            [o.lh, o.lt, o],
            ['1', '3', odict([('1', 1), ('3', 3)])]
        )
        # Remove element at the end of the odict sequence
        o = odict([('1', 1), ('2', 2), ('3', 3)])
        del o['3']
        self.assertEqual(
            [o.lh, o.lt, o],
            ['1', '2', odict([('1', 1), ('2', 2)])],
        )

    def test_copy(self):
        # test copy function on odict
        o = odict([('a', 1), ('b', 2), ('c', 3), ('d', 4)])
        o_copy = o.copy()
        self.assertTrue(o_copy is not o)
        self.assertEqual(
            o_copy.items(),
            [('a', 1), ('b', 2), ('c', 3), ('d', 4)]
        )
        # test with copy module
        o = odict([('1', 1), ('2', 2), ('3', object())])
        # shallow copy
        o_copy = copy.copy(o)
        self.assertFalse(o_copy is o)
        self.assertTrue(o_copy['3'] is o['3'])
        # deep copy
        o_copy = copy.deepcopy(o)
        self.assertFalse(o_copy is o)
        self.assertFalse(o_copy['3'] is o['3'])

    def test_casting(self):
        # in python < 3.7 casting to dict will fail
        # Reason -> http://bugs.python.org/issue1615701
        # The __init__ function of dict checks wether arg is subclass of dict,
        # and ignores overwritten __getitem__ & co if so.
        # This was fixed and later reverted due to behavioural problems with
        # pickle.
        if sys.version_info < (3, 7):  # pragma: no cover
            self.assertEqual(dict(odict([(1, 1)])), {1: [_nil, 1, _nil]})
        else:  # pragma: no cover
            self.assertEqual(dict(odict([(1, 1)])), {1: 1})
        # The following ways for type conversion work
        self.assertEqual(dict(odict([(1, 1)]).items()), {1: 1})
        self.assertEqual(odict([(1, 1)]).as_dict(), {1: 1})

    def test_pickle(self):
        # dump and load odict pickle
        self.assertEqual(
            pickle.loads(pickle.dumps([odict([(1, 2)])])),
            [odict([(1, 2)])]
        )

    def test_sort(self):
        # basic sorting
        o = odict([('a', 1), ('c', 3), ('b', 2)])
        o.sort()
        self.assertEqual(o.items(), [('a', 1), ('b', 2), ('c', 3)])
        # A custom cmp function. Note that you get (key, value) tuples to
        # compare. Test with cmp function which sorting by key in reversed
        # order

        def mycmp(x, y):
            if x[0] > y[0]:
                return -1
            if x[0] < y[0]:
                return 1
        o = odict([('a', 1), ('c', 3), ('b', 2)])
        o.sort(cmp=mycmp)
        self.assertEqual(o.items(), [('c', 3), ('b', 2), ('a', 1)])
        # Test key and reverse kwargs
        o = odict([('a', 1), ('c', 3), ('b', 2)])
        o.sort(key=lambda x: x[0])
        self.assertEqual(o.items(), [('a', 1), ('b', 2), ('c', 3)])
        o.sort(key=lambda x: x[0], reverse=True)
        self.assertEqual(o.items(), [('c', 3), ('b', 2), ('a', 1)])

    def test_getattr_setattr_subclass(self):
        class Sub(odict):
            def __getattr__(self, name):
                try:
                    return self[name]
                except KeyError:
                    raise AttributeError(name)

            def __setattr__(self, name, value):
                self[name] = value

        sub = Sub()
        sub.title = 'foo'
        self.assertEqual(sub.keys(), ['title'])
        self.assertEqual(sub.title, 'foo')

    def test_bool_expessions(self):
        # Check boolean expressions.
        self.assertFalse(odict() and True or False)
        self.assertTrue(odict([('a', 1)]) and True or False)
        self.assertTrue(bool(odict([('a', 1)])))

    def test_alter_key(self):
        # Test alter_key function.
        o = odict((('1', 'a'), ('2', 'b'), ('3', 'c')))
        self.assertEqual(o.keys(), ['1', '2', '3'])
        o.alter_key('1', 'foo')
        self.assertEqual(o.keys(), ['foo', '2', '3'])
        self.assertEqual(o.rkeys(), ['3', '2', 'foo'])
        self.assertTrue(o._dict_impl() is dict)
        dict_values = o._dict_impl().values(o)
        self.assertEqual(len(dict_values), 3)
        self.assertTrue(['foo', 'b', '3'] in dict_values)
        self.assertTrue(['2', 'c', _nil] in dict_values)
        self.assertTrue([_nil, 'a', '2'] in dict_values)
        self.assertEqual(o.values(), ['a', 'b', 'c'])
        self.assertEqual(o['foo'], 'a')
        self.assertEqual(o.lh, 'foo')
        o.alter_key('2', 'bar')
        self.assertEqual(o.keys(), ['foo', 'bar', '3'])
        self.assertEqual(o.rkeys(), ['3', 'bar', 'foo'])
        dict_values = o._dict_impl().values(o)
        self.assertEqual(len(dict_values), 3)
        self.assertTrue(['bar', 'c', _nil] in dict_values)
        self.assertTrue(['foo', 'b', '3'] in dict_values)
        self.assertTrue([_nil, 'a', 'bar'] in dict_values)
        self.assertEqual(o.values(), ['a', 'b', 'c'])
        self.assertEqual(o['bar'], 'b')
        o.alter_key('3', 'baz')
        self.assertEqual(o.keys(), ['foo', 'bar', 'baz'])
        self.assertEqual(o.rkeys(), ['baz', 'bar', 'foo'])
        dict_values = o._dict_impl().values(o)
        self.assertEqual(len(dict_values), 3)
        self.assertTrue(['foo', 'b', 'baz'] in dict_values)
        self.assertTrue([_nil, 'a', 'bar'] in dict_values)
        self.assertTrue(['bar', 'c', _nil] in dict_values)
        self.assertEqual(o.values(), ['a', 'b', 'c'])
        self.assertEqual(o['baz'], 'c')
        self.assertEqual(o.lt, 'baz')

    def test_str(self):
        # Check __str__ function
        o = odict([('foo', 'a'), ('bar', 'b'), ('baz', 'c')])
        self.assertEqual(str(o), "{'foo': 'a', 'bar': 'b', 'baz': 'c'}")

    def test_repr(self):
        self.assertEqual(repr(odict()), 'odict()')
        self.assertEqual(repr(odict([('foo', 'a')])), "odict([('foo', 'a')])")

    def test_swap(self):
        # Test ``swap``
        o = odict([('0', 'a'), ('1', 'b'), ('2', 'c'), ('3', 'd'), ('4', 'e')])
        # Cannot swap same key
        with self.assertRaises(ValueError):
            o.swap('0', '0')
        self.assertEqual(o.keys(), ['0', '1', '2', '3', '4'])
        self.assertEqual(o.rkeys(), ['4', '3', '2', '1', '0'])
        self.assertEqual(o.values(), ['a', 'b', 'c', 'd', 'e'])
        self.assertEqual((o.lh, o.lt), ('0', '4'))
        # Case first 2, a < b
        o.swap('0', '1')
        self.assertEqual(o.keys(), ['1', '0', '2', '3', '4'])
        self.assertEqual(o.rkeys(), ['4', '3', '2', '0', '1'])
        self.assertEqual(o.values(), ['b', 'a', 'c', 'd', 'e'])
        self.assertEqual((o.lh, o.lt), ('1', '4'))
        # Case first 2, a > b
        o.swap('0', '1')
        self.assertEqual(o.keys(), ['0', '1', '2', '3', '4'])
        self.assertEqual(o.rkeys(), ['4', '3', '2', '1', '0'])
        self.assertEqual(o.values(), ['a', 'b', 'c', 'd', 'e'])
        self.assertEqual((o.lh, o.lt), ('0', '4'))
        # Case last 2, a < b
        o.swap('3', '4')
        self.assertEqual(o.keys(), ['0', '1', '2', '4', '3'])
        self.assertEqual(o.rkeys(), ['3', '4', '2', '1', '0'])
        self.assertEqual(o.values(), ['a', 'b', 'c', 'e', 'd'])
        self.assertEqual((o.lh, o.lt), ('0', '3'))
        # Case last 2, a > b
        o.swap('3', '4')
        self.assertEqual(o.keys(), ['0', '1', '2', '3', '4'])
        self.assertEqual(o.rkeys(), ['4', '3', '2', '1', '0'])
        self.assertEqual(o.values(), ['a', 'b', 'c', 'd', 'e'])
        self.assertEqual((o.lh, o.lt), ('0', '4'))
        # Case neighbors, a < b
        o.swap('1', '2')
        self.assertEqual(o.keys(), ['0', '2', '1', '3', '4'])
        self.assertEqual(o.rkeys(), ['4', '3', '1', '2', '0'])
        self.assertEqual(o.values(), ['a', 'c', 'b', 'd', 'e'])
        self.assertEqual((o.lh, o.lt), ('0', '4'))
        # Case neighbors, a > b
        o.swap('1', '2')
        self.assertEqual(o.keys(), ['0', '1', '2', '3', '4'])
        self.assertEqual(o.rkeys(), ['4', '3', '2', '1', '0'])
        self.assertEqual(o.values(), ['a', 'b', 'c', 'd', 'e'])
        self.assertEqual((o.lh, o.lt), ('0', '4'))
        # Case non neighbors, one key first, a < b
        o.swap('0', '2')
        self.assertEqual(o.keys(), ['2', '1', '0', '3', '4'])
        self.assertEqual(o.rkeys(), ['4', '3', '0', '1', '2'])
        self.assertEqual(o.values(), ['c', 'b', 'a', 'd', 'e'])
        self.assertEqual((o.lh, o.lt), ('2', '4'))
        # Case non neighbors, one key first, a > b
        o.swap('0', '2')
        self.assertEqual(o.keys(), ['0', '1', '2', '3', '4'])
        self.assertEqual(o.rkeys(), ['4', '3', '2', '1', '0'])
        self.assertEqual(o.values(), ['a', 'b', 'c', 'd', 'e'])
        self.assertEqual((o.lh, o.lt), ('0', '4'))
        # Case non neighbors, one key last, a < b
        o.swap('2', '4')
        self.assertEqual(o.keys(), ['0', '1', '4', '3', '2'])
        self.assertEqual(o.rkeys(), ['2', '3', '4', '1', '0'])
        self.assertEqual(o.values(), ['a', 'b', 'e', 'd', 'c'])
        self.assertEqual((o.lh, o.lt), ('0', '2'))
        # Case non neighbors, one key last, a > b
        o.swap('2', '4')
        self.assertEqual(o.keys(), ['0', '1', '2', '3', '4'])
        self.assertEqual(o.rkeys(), ['4', '3', '2', '1', '0'])
        self.assertEqual(o.values(), ['a', 'b', 'c', 'd', 'e'])
        self.assertEqual((o.lh, o.lt), ('0', '4'))
        # Case non neighbors, a < b
        o.swap('1', '3')
        self.assertEqual(o.keys(), ['0', '3', '2', '1', '4'])
        self.assertEqual(o.rkeys(), ['4', '1', '2', '3', '0'])
        self.assertEqual(o.values(), ['a', 'd', 'c', 'b', 'e'])
        self.assertEqual((o.lh, o.lt), ('0', '4'))
        # Case non neighbors, a > b
        o.swap('1', '3')
        self.assertEqual(o.keys(), ['0', '1', '2', '3', '4'])
        self.assertEqual(o.rkeys(), ['4', '3', '2', '1', '0'])
        self.assertEqual(o.values(), ['a', 'b', 'c', 'd', 'e'])
        self.assertEqual((o.lh, o.lt), ('0', '4'))

    def test_insertbefore(self):
        o = odict([('0', 'a')])
        with self.assertRaises(ValueError):
            o.insertbefore('0', '0', 'a')
        with self.assertRaises(KeyError):
            o.insertbefore('x', '1', 'b')
        o.insertbefore('0', '1', 'b')
        self.assertEqual(o.keys(), ['1', '0'])
        self.assertEqual(o.rkeys(), ['0', '1'])
        self.assertEqual(o.values(), ['b', 'a'])
        self.assertEqual((o.lh, o.lt), ('1', '0'))
        o.insertbefore('0', '2', 'c')
        self.assertEqual(o.keys(), ['1', '2', '0'])
        self.assertEqual(o.rkeys(), ['0', '2', '1'])
        self.assertEqual(o.values(), ['b', 'c', 'a'])
        self.assertEqual((o.lh, o.lt), ('1', '0'))

    def test_insertafter(self):
        o = odict([('0', 'a')])
        with self.assertRaises(ValueError):
            o.insertafter('0', '0', 'a')
        with self.assertRaises(KeyError):
            o.insertafter('x', '1', 'b')
        o.insertafter('0', '1', 'b')
        self.assertEqual(o.keys(), ['0', '1'])
        self.assertEqual(o.rkeys(), ['1', '0'])
        self.assertEqual(o.values(), ['a', 'b'])
        self.assertEqual((o.lh, o.lt), ('0', '1'))
        o.insertafter('0', '2', 'c')
        self.assertEqual(o.keys(), ['0', '2', '1'])
        self.assertEqual(o.rkeys(), ['1', '2', '0'])
        self.assertEqual(o.values(), ['a', 'c', 'b'])
        self.assertEqual((o.lh, o.lt), ('0', '1'))

    def test_insertfirst(self):
        o = odict()
        o.insertfirst('0', 'a')
        self.assertEqual(o.keys(), ['0'])
        self.assertEqual(o.rkeys(), ['0'])
        self.assertEqual(o.values(), ['a'])
        o.insertfirst('1', 'b')
        self.assertEqual(o.keys(), ['1', '0'])
        self.assertEqual(o.rkeys(), ['0', '1'])
        self.assertEqual(o.values(), ['b', 'a'])

    def test_insertlast(self):
        o = odict()
        o.insertlast('0', 'a')
        self.assertEqual(o.keys(), ['0'])
        self.assertEqual(o.rkeys(), ['0'])
        self.assertEqual(o.values(), ['a'])
        o.insertlast('1', 'b')
        self.assertEqual(o.keys(), ['0', '1'])
        self.assertEqual(o.rkeys(), ['1', '0'])
        self.assertEqual(o.values(), ['a', 'b'])

    def test_movebefore(self):
        o = odict([('0', 'a'), ('1', 'b'), ('2', 'c'), ('3', 'd'), ('4', 'e')])
        with self.assertRaises(ValueError):
            o.movebefore('0', '0')
        # case no neighbors ref < key
        o.movebefore('1', '3')
        self.assertEqual(o.keys(), ['0', '3', '1', '2', '4'])
        self.assertEqual(o.rkeys(), ['4', '2', '1', '3', '0'])
        self.assertEqual(o.values(), ['a', 'd', 'b', 'c', 'e'])
        self.assertEqual((o.lh, o.lt), ('0', '4'))
        # case no neighbors ref > key
        o.movebefore('2', '3')
        self.assertEqual(o.keys(), ['0', '1', '3', '2', '4'])
        self.assertEqual(o.rkeys(), ['4', '2', '3', '1', '0'])
        self.assertEqual(o.values(), ['a', 'b', 'd', 'c', 'e'])
        self.assertEqual((o.lh, o.lt), ('0', '4'))
        # case neighbors ref < key
        o.movebefore('3', '2')
        self.assertEqual(o.keys(), ['0', '1', '2', '3', '4'])
        self.assertEqual(o.rkeys(), ['4', '3', '2', '1', '0'])
        self.assertEqual(o.values(), ['a', 'b', 'c', 'd', 'e'])
        self.assertEqual((o.lh, o.lt), ('0', '4'))
        # case neighbors ref > key
        o.movebefore('3', '2')
        self.assertEqual(o.keys(), ['0', '1', '2', '3', '4'])
        self.assertEqual(o.rkeys(), ['4', '3', '2', '1', '0'])
        self.assertEqual(o.values(), ['a', 'b', 'c', 'd', 'e'])
        self.assertEqual((o.lh, o.lt), ('0', '4'))
        # case move first, no neighbors
        o.movebefore('0', '2')
        self.assertEqual(o.keys(), ['2', '0', '1', '3', '4'])
        self.assertEqual(o.rkeys(), ['4', '3', '1', '0', '2'])
        self.assertEqual(o.values(), ['c', 'a', 'b', 'd', 'e'])
        self.assertEqual((o.lh, o.lt), ('2', '4'))
        # case move first, neighbors
        o.movebefore('2', '0')
        self.assertEqual(o.keys(), ['0', '2', '1', '3', '4'])
        self.assertEqual(o.rkeys(), ['4', '3', '1', '2', '0'])
        self.assertEqual(o.values(), ['a', 'c', 'b', 'd', 'e'])
        self.assertEqual((o.lh, o.lt), ('0', '4'))
        # case ref last, no neighbors
        o.movebefore('4', '1')
        self.assertEqual(o.keys(), ['0', '2', '3', '1', '4'])
        self.assertEqual(o.rkeys(), ['4', '1', '3', '2', '0'])
        self.assertEqual(o.values(), ['a', 'c', 'd', 'b', 'e'])
        self.assertEqual((o.lh, o.lt), ('0', '4'))
        # case ref last, neighbors
        o.movebefore('4', '1')
        self.assertEqual(o.keys(), ['0', '2', '3', '1', '4'])
        self.assertEqual(o.rkeys(), ['4', '1', '3', '2', '0'])
        self.assertEqual(o.values(), ['a', 'c', 'd', 'b', 'e'])
        self.assertEqual((o.lh, o.lt), ('0', '4'))
        # case key first, no neighbors
        o.movebefore('3', '0')
        self.assertEqual(o.keys(), ['2', '0', '3', '1', '4'])
        self.assertEqual(o.rkeys(), ['4', '1', '3', '0', '2'])
        self.assertEqual(o.values(), ['c', 'a', 'd', 'b', 'e'])
        self.assertEqual((o.lh, o.lt), ('2', '4'))
        # case key first, neighbors
        o.movebefore('0', '2')
        self.assertEqual(o.keys(), ['2', '0', '3', '1', '4'])
        self.assertEqual(o.rkeys(), ['4', '1', '3', '0', '2'])
        self.assertEqual(o.values(), ['c', 'a', 'd', 'b', 'e'])
        self.assertEqual((o.lh, o.lt), ('2', '4'))
        # case key last, no neighbors
        o.movebefore('3', '4')
        self.assertEqual(o.keys(), ['2', '0', '4', '3', '1'])
        self.assertEqual(o.rkeys(), ['1', '3', '4', '0', '2'])
        self.assertEqual(o.values(), ['c', 'a', 'e', 'd', 'b'])
        self.assertEqual((o.lh, o.lt), ('2', '1'))
        # case key last, neighbors
        o.movebefore('3', '1')
        self.assertEqual(o.keys(), ['2', '0', '4', '1', '3'])
        self.assertEqual(o.rkeys(), ['3', '1', '4', '0', '2'])
        self.assertEqual(o.values(), ['c', 'a', 'e', 'b', 'd'])
        self.assertEqual((o.lh, o.lt), ('2', '3'))

    def test_moveafter(self):
        o = odict([('0', 'a'), ('1', 'b'), ('2', 'c'), ('3', 'd'), ('4', 'e')])
        with self.assertRaises(ValueError):
            o.moveafter('0', '0')
        # case no neighbors ref < key
        o.moveafter('1', '3')
        self.assertEqual(o.keys(), ['0', '1', '3', '2', '4'])
        self.assertEqual(o.rkeys(), ['4', '2', '3', '1', '0'])
        self.assertEqual(o.values(), ['a', 'b', 'd', 'c', 'e'])
        self.assertEqual((o.lh, o.lt), ('0', '4'))
        # case no neighbors ref > key
        o.moveafter('2', '1')
        self.assertEqual(o.keys(), ['0', '3', '2', '1', '4'])
        self.assertEqual(o.rkeys(), ['4', '1', '2', '3', '0'])
        self.assertEqual(o.values(), ['a', 'd', 'c', 'b', 'e'])
        self.assertEqual((o.lh, o.lt), ('0', '4'))
        # case neighbors ref < key
        o.moveafter('3', '2')
        self.assertEqual(o.keys(), ['0', '3', '2', '1', '4'])
        self.assertEqual(o.rkeys(), ['4', '1', '2', '3', '0'])
        self.assertEqual(o.values(), ['a', 'd', 'c', 'b', 'e'])
        self.assertEqual((o.lh, o.lt), ('0', '4'))
        # case neighbors ref > key
        o.moveafter('2', '3')
        self.assertEqual(o.keys(), ['0', '2', '3', '1', '4'])
        self.assertEqual(o.rkeys(), ['4', '1', '3', '2', '0'])
        self.assertEqual(o.values(), ['a', 'c', 'd', 'b', 'e'])
        self.assertEqual((o.lh, o.lt), ('0', '4'))
        # case move last, no neighbors
        o.moveafter('4', '3')
        self.assertEqual(o.keys(), ['0', '2', '1', '4', '3'])
        self.assertEqual(o.rkeys(), ['3', '4', '1', '2', '0'])
        self.assertEqual(o.values(), ['a', 'c', 'b', 'e', 'd'])
        self.assertEqual((o.lh, o.lt), ('0', '3'))
        # case move last, neighbors
        o.moveafter('3', '4')
        self.assertEqual(o.keys(), ['0', '2', '1', '3', '4'])
        self.assertEqual(o.rkeys(), ['4', '3', '1', '2', '0'])
        self.assertEqual(o.values(), ['a', 'c', 'b', 'd', 'e'])
        self.assertEqual((o.lh, o.lt), ('0', '4'))
        # case ref first, no neighbors
        o.moveafter('0', '3')
        self.assertEqual(o.keys(), ['0', '3', '2', '1', '4'])
        self.assertEqual(o.rkeys(), ['4', '1', '2', '3', '0'])
        self.assertEqual(o.values(), ['a', 'd', 'c', 'b', 'e'])
        self.assertEqual((o.lh, o.lt), ('0', '4'))
        # case ref first, neighbors
        o.moveafter('0', '3')
        self.assertEqual(o.keys(), ['0', '3', '2', '1', '4'])
        self.assertEqual(o.rkeys(), ['4', '1', '2', '3', '0'])
        self.assertEqual(o.values(), ['a', 'd', 'c', 'b', 'e'])
        self.assertEqual((o.lh, o.lt), ('0', '4'))
        # case key first, no neighbors
        o.moveafter('2', '0')
        self.assertEqual(o.keys(), ['3', '2', '0', '1', '4'])
        self.assertEqual(o.rkeys(), ['4', '1', '0', '2', '3'])
        self.assertEqual(o.values(), ['d', 'c', 'a', 'b', 'e'])
        self.assertEqual((o.lh, o.lt), ('3', '4'))
        # case key first, neighbors
        o.moveafter('2', '3')
        self.assertEqual(o.keys(), ['2', '3', '0', '1', '4'])
        self.assertEqual(o.rkeys(), ['4', '1', '0', '3', '2'])
        self.assertEqual(o.values(), ['c', 'd', 'a', 'b', 'e'])
        self.assertEqual((o.lh, o.lt), ('2', '4'))
        # case key last, no neighbors
        o.moveafter('0', '4')
        self.assertEqual(o.keys(), ['2', '3', '0', '4', '1'])
        self.assertEqual(o.rkeys(), ['1', '4', '0', '3', '2'])
        self.assertEqual(o.values(), ['c', 'd', 'a', 'e', 'b'])
        self.assertEqual((o.lh, o.lt), ('2', '1'))
        # case key last, neighbors
        o.moveafter('4', '1')
        self.assertEqual(o.keys(), ['2', '3', '0', '4', '1'])
        self.assertEqual(o.rkeys(), ['1', '4', '0', '3', '2'])
        self.assertEqual(o.values(), ['c', 'd', 'a', 'e', 'b'])
        self.assertEqual((o.lh, o.lt), ('2', '1'))

    def test_movefirst(self):
        o = odict([('0', 'a'), ('1', 'b'), ('2', 'c')])
        o.movefirst('2')
        self.assertEqual(o.keys(), ['2', '0', '1'])
        self.assertEqual(o.rkeys(), ['1', '0', '2'])
        self.assertEqual(o.values(), ['c', 'a', 'b'])
        self.assertEqual((o.lh, o.lt), ('2', '1'))

    def test_movelast(self):
        o = odict([('0', 'a'), ('1', 'b'), ('2', 'c')])
        o.movelast('0')
        self.assertEqual(o.keys(), ['1', '2', '0'])
        self.assertEqual(o.rkeys(), ['0', '2', '1'])
        self.assertEqual(o.values(), ['b', 'c', 'a'])
        self.assertEqual((o.lh, o.lt), ('1', '0'))

    def test_next_key(self):
        o = odict()
        with self.assertRaises(KeyError):
            o.next_key('x')
        o['x'] = 'x'
        with self.assertRaises(KeyError):
            o.next_key('x')
        o['y'] = 'y'
        self.assertEqual(o.next_key('x'), 'y')

    def test_prev_key(self):
        o = odict()
        with self.assertRaises(KeyError):
            o.prev_key('x')
        o['x'] = 'x'
        with self.assertRaises(KeyError):
            o.prev_key('x')
        o['y'] = 'y'
        self.assertEqual(o.prev_key('y'), 'x')


if __name__ == '__main__':
    from odict import tests

    suite = unittest.TestSuite()
    suite.addTest(unittest.findTestCases(tests))
    runner = unittest.TextTestRunner(failfast=True)
    result = runner.run(suite)
    sys.exit(not result.wasSuccessful())
