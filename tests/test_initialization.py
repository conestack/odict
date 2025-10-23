# Python Software Foundation License
"""Tests for ordered dict initialization and factory methods."""

import pytest


def test_abstract_superclass_no_dict_impl(AbstractODict, ODict):
    """Abstract superclass provides no concrete _dict_cls class."""
    with pytest.raises(TypeError, match='No dict implementation class provided'):
        AbstractODict()

    o = ODict()
    assert o._dict_cls() == dict


def test_abstract_entry_cls_not_implemented():
    """Abstract _entry_cls() raises NotImplementedError if not overridden."""
    from odict.odict import _base_odict

    # Create a minimal subclass that only implements _dict_cls
    class PartialImpl(_base_odict, dict):
        def _dict_cls(self):
            return dict
        # Intentionally NOT implementing _entry_cls()

    obj = PartialImpl()
    with pytest.raises(NotImplementedError, match='Subclasses must implement _entry_cls'):
        obj._entry_cls()


def test_init_with_keyword_arguments_fails(ODict):
    """Initialization with keyword arguments fails to avoid ordering trap."""
    with pytest.raises(
        TypeError,
        match='__init__\\(\\) of ordered dict takes no keyword arguments'
    ):
        ODict(a=1)


def test_init_with_dict_order_undefined(ODict):
    """When initialized with a dict, element order is undefined."""
    o = ODict({'b': 2, 'a': 1, 'd': 4, 'c': 3})
    assert sorted(o.keys()) == ['a', 'b', 'c', 'd']
    assert o['a'] == 1
    assert o['b'] == 2
    assert o['c'] == 3
    assert o['d'] == 4


def test_init_with_items_preserves_order(ODict):
    """When initialized with a list, element order is preserved."""
    o = ODict([('a', 1), ('b', 2), ('c', 3), ('d', 4)])
    assert o.items() == [('a', 1), ('b', 2), ('c', 3), ('d', 4)]


def test_fromkeys_factory_method(ODict):
    """fromkeys() creates ordered dict with keys and default value."""
    o = ODict.fromkeys((1, 2, 3), 'x')
    assert o.items() == [(1, 'x'), (2, 'x'), (3, 'x')]


@pytest.mark.parametrize('keys,value,expected', [
    ([], None, []),
    ([1], 'x', [(1, 'x')]),
    ([1, 2, 3], None, [(1, None), (2, None), (3, None)]),
    (['a', 'b'], 42, [('a', 42), ('b', 42)]),
])
def test_fromkeys_parametrized(ODict, keys, value, expected):
    """fromkeys() with various inputs."""
    o = ODict.fromkeys(keys, value)
    assert o.items() == expected
