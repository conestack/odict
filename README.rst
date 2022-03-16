.. image:: https://img.shields.io/pypi/v/odict.svg
    :target: https://pypi.python.org/pypi/odict
    :alt: Latest PyPI version

.. image:: https://img.shields.io/pypi/dm/odict.svg
    :target: https://pypi.python.org/pypi/odict
    :alt: Number of PyPI downloads

.. image:: https://github.com/conestack/odict/actions/workflows/test.yaml/badge.svg
    :target: https://github.com/conestack/odict/actions/workflows/test.yaml
    :alt: Test odict


odict
=====

Dictionary in which the *insertion* order of items is preserved (using an
internal double linked list). In this implementation replacing an existing
item keeps it at its original position.

Internal representation: values of the dict.

.. code-block:: python

    [pred_key, val, succ_key]

The sequence of elements uses as a double linked list. The ``links`` are dict
keys. ``self.lh`` and ``self.lt`` are the keys of first and last element
inserted in the odict.


Motivation
----------

When this package was created, ``collections.OrderedDict`` not existed yet.

Another problem is that ``dict`` cannot always be inherited from in conjunction
with other base classes. This may result in instance layout conflicts or other
errors. So ``odict`` is written in a way that let you alter the dictionary
base implementation.


Usage
-----

Import and create ordered dictionary.

.. code-block:: python

    from odict import odict
    od = odict()


Custom odict
------------

It is possible to use ``_odict`` base class to implement an ordered dict not
inheriting from ``dict`` type. This is useful i.e. when persisting to ZODB.

Inheriting from ``dict`` and ``Persistent`` at the same time fails. Also,
using a regular ``list`` for the internal double linked list representation
causes problems, so we define a custom class for it as well.

.. code-block:: python

    from persistent.dict import PersistentDict
    from persistent.list import PersistentList

    class podict(_odict, PersistentDict):

        def _dict_impl(self):
            return PersistentDict

        def _list_factory(self):
            return PersistentList


Python < 3.7
------------

In Python < 3.7 casting to dict will fail. The reason for this can be found
`here <http://bugs.python.org/issue1615701>`_. The ``__init__`` function of
dict checks whether arg is subclass of ``dict``, and ignores overwritten
``__getitem__`` & co if so. This was fixed and later reverted due to
behavioural problems with pickle:

.. code-block:: pycon

    >>> dict(odict([(1, 1)]))
    {1: [nil, 1, nil]}

Use one of the following ways for type conversion.

.. code-block:: pycon

    >>> dict(odict([(1, 1)]).items())
    {1: 1}

    >>> odict([(1, 1)]).as_dict()
    {1: 1}


Misc
----

In a C reimplementation of this data structure, things could be simplified
(and speed up) a lot if given a value you can at the same time find its key.
With that, you can use normal C pointers.


Python Versions
---------------

- Python 2.7, 3.7+

- Probably works with other/older versions


Contributors
============

- bearophile (Original Author)

- Robert Niederreiter (Author)

- Georg Bernhard

- Florian Friesdorf

- Jens Klein

under the `Python Software Foundation License <http://www.opensource.org/licenses/PythonSoftFoundation.php>`_.
