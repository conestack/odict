# Python Software Foundation License
"""Tests for iteration over ordered dicts."""

import pytest


def test_riterkeys(sample_od):
    """riterkeys() iterates over keys in reverse order."""
    assert [x for x in sample_od.riterkeys()] == ['d', 'c', 'b', 'a']


def test_rkeys(sample_od):
    """rkeys() returns list of keys in reverse order."""
    assert sample_od.rkeys() == ['d', 'c', 'b', 'a']


def test_ritervalues(sample_od):
    """ritervalues() iterates over values in reverse order."""
    assert [x for x in sample_od.ritervalues()] == [4, 3, 2, 1]


def test_rvalues(sample_od):
    """rvalues() returns list of values in reverse order."""
    assert sample_od.rvalues() == [4, 3, 2, 1]


def test_riteritems(sample_od):
    """riteritems() iterates over (key, value) pairs in reverse order."""
    assert [x for x in sample_od.riteritems()] == [
        ('d', 4), ('c', 3), ('b', 2), ('a', 1)
    ]


def test_ritems(sample_od):
    """ritems() returns list of (key, value) pairs in reverse order."""
    assert sample_od.ritems() == [('d', 4), ('c', 3), ('b', 2), ('a', 1)]
