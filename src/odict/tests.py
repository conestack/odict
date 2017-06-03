# Python Software Foundation License
from odict import odict
from odict.pyodict import _nil
from odict.pyodict import _odict
import copy
import pickle


try:
    import unittest2 as unittest
except ImportError:
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
        self.assertEqual(o.lastkey(), 'd')
        o = odict()
        msg = "\"'firstkey(): ordered dictionary is empty'\""
        self.assertRaisesWithMessage(msg, o.firstkey, KeyError)
        msg = "\"'lastkey(): ordered dictionary is empty'\""
        self.assertRaisesWithMessage(msg, o.lastkey, KeyError)

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
        # casting to dict will fail
        # Reason -> http://bugs.python.org/issue1615701
        # The __init__ function of dict checks wether arg is subclass of dict,
        # and ignores overwritten __getitem__ & co if so.
        # This was fixed and later reverted due to behavioural problems with
        # pickle.
        self.assertEqual(dict(odict([(1, 1)])), {1: [_nil, 1, _nil]})
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
        dict_values = o._dict_impl().values(o)
        self.assertEqual(len(dict_values), 3)
        self.assertTrue(['bar', 'c', _nil] in dict_values)
        self.assertTrue(['foo', 'b', '3'] in dict_values)
        self.assertTrue([_nil, 'a', 'bar'] in dict_values)
        self.assertEqual(o.values(), ['a', 'b', 'c'])
        self.assertEqual(o['bar'], 'b')
        o.alter_key('3', 'baz')
        self.assertEqual(o.keys(), ['foo', 'bar', 'baz'])
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


if __name__ == '__main__':
    unittest.main()                                          # pragma: no cover
