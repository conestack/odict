# Python Software Foundation License
"""Tests for edge cases and special behaviors."""

import sys
import pytest


# Nil repr test

def test_nil_repr(nil):
    """_nil singleton has repr of 'nil'."""
    assert repr(nil) == 'nil'


# Low level repr test

def test_repr_method(ODict, nil):
    """_repr() returns low level representation."""
    o = ODict([('1', 1), ('2', 2), ('3', 3)])
    repr_str = o._repr()
    assert 'low level repr' in repr_str
    assert "'1'" in repr_str
    assert "'3'" in repr_str


def test_repr_method_empty(ODict, nil):
    """_repr() on empty dict."""
    o = ODict()
    repr_str = o._repr()
    assert 'low level repr' in repr_str
    assert str(nil) in repr_str


# Boolean expression tests

def test_empty_dict_is_falsy(empty_od):
    """Empty ordered dict evaluates to False in boolean context."""
    assert not (empty_od and True)
    assert not bool(empty_od)


def test_nonempty_dict_is_truthy(sample_od):
    """Non-empty ordered dict evaluates to True in boolean context."""
    assert sample_od and True
    assert bool(sample_od)


# Subclassing tests

def test_subclass_with_getattr_setattr(ODict):
    """Ordered dict can be subclassed with custom __getattr__ and __setattr__."""
    class Sub(ODict):
        def __getattr__(self, name):
            try:
                return self[name]
            except KeyError:
                raise AttributeError(name)

        def __setattr__(self, name, value):
            self[name] = value

    sub = Sub()
    sub.title = 'foo'
    assert sub.keys() == ['title']
    assert sub.title == 'foo'


# Casting tests

def test_casting_to_dict_via_items(ODict):
    """Casting via items() always works."""
    o = ODict([(1, 1)])
    assert dict(o.items()) == {1: 1}


def test_as_dict_method(ODict):
    """as_dict() method returns regular dict."""
    o = ODict([(1, 1)])
    assert o.as_dict() == {1: 1}


def test_casting_to_dict_python_version_dependent(ODict, nil):
    """Direct dict() cast behavior depends on Python version."""
    o = ODict([(1, 1)])
    if sys.version_info < (3, 7):  # pragma: no cover
        # In Python < 3.7, dict() cast exposes internal structure
        # (this was a known limitation)
        result = dict(o)
        # odict uses [prev, val, next] structure
        assert isinstance(result, dict)
    else:  # pragma: no cover
        # In Python >= 3.7, dict() cast works correctly
        assert dict(o) == {1: 1}
