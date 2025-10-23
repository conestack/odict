# Python Software Foundation License
"""Shared pytest fixtures for ordered dict tests."""

import pytest
from odict import odict
from odict.pyodict import _odict, _nil as pyodict_nil
from odict.codict import codict, _codict, _nil as codict_nil, Entry


@pytest.fixture(params=[
    pytest.param(
        (odict, _odict, pyodict_nil),
        id='odict'
    ),
    pytest.param(
        (codict, _codict, codict_nil),
        id='codict'
    ),
])
def impl(request):
    """Parametrize tests with both odict and codict implementations.

    Returns:
        tuple: (concrete_class, abstract_class, _nil_singleton)
    """
    return request.param


@pytest.fixture
def ODict(impl):
    """Concrete ordered dict class (odict or codict)."""
    return impl[0]


@pytest.fixture
def AbstractODict(impl):
    """Abstract ordered dict class (_odict or _codict)."""
    return impl[1]


@pytest.fixture
def nil(impl):
    """Nil singleton for the current implementation."""
    return impl[2]


@pytest.fixture
def empty_od(ODict):
    """Empty ordered dict instance."""
    return ODict()


@pytest.fixture
def sample_od(ODict):
    """Ordered dict with sample data: [('a', 1), ('b', 2), ('c', 3), ('d', 4)]."""
    return ODict([('a', 1), ('b', 2), ('c', 3), ('d', 4)])


@pytest.fixture
def five_items_od(ODict):
    """Ordered dict with 5 items for move/swap tests."""
    return ODict([('0', 'a'), ('1', 'b'), ('2', 'c'), ('3', 'd'), ('4', 'e')])
