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
with other base classes. This may result in instance lay-out conflicts or other
errors. So ``odict`` is written in a way that let you alter the dictionary
base implementation easily.


Performance (Python 3.4)
------------------------

When running the benchmark script, you get results similar to the one below on
recent common hardware.

Adding and deleting builtin ``dict`` objects

+----------------+-------------+
| Add       1000 | 0.63800ms   |
+----------------+-------------+
| Delete    1000 | 0.36900ms   |
+----------------+-------------+
| Add      10000 | 5.74600ms   |
+----------------+-------------+
| Delete   10000 | 3.97000ms   |
+----------------+-------------+
| Add     100000 | 69.40600ms  |
+----------------+-------------+
| Delete  100000 | 47.30000ms  |
+----------------+-------------+
| Add    1000000 | 807.09100ms |
+----------------+-------------+
| Delete 1000000 | 495.33400ms |
+----------------+-------------+

Adding and deleting ``collection.OrderedDict`` objects

+----------------+---------------+
| Add       1000 | 8.15200ms     |
+----------------+---------------+
| Delete    1000 | 0.50800ms     |
+----------------+---------------+
| Add      10000 | 91.45800ms    |
+----------------+---------------+
| Delete   10000 | 7.10200ms     |
+----------------+---------------+
| Add     100000 | 982.35500ms   |
+----------------+---------------+
| Delete  100000 | 71.02300ms    |
+----------------+---------------+
| Add    1000000 | 10222.78300ms |
+----------------+---------------+
| Delete 1000000 | 715.35100ms   |
+----------------+---------------+

Adding and deleting ``odict`` objects provided by this package

+----------------+--------------+
| Add       1000 | 46.75600ms   |
+----------------+--------------+
| Delete    1000 | 0.35700ms    |
+----------------+--------------+
| Add      10000 | 23.97900ms   |
+----------------+--------------+
| Delete   10000 | 4.79100ms    |
+----------------+--------------+
| Add     100000 | 276.15900ms  |
+----------------+--------------+
| Delete  100000 | 49.02700ms   |
+----------------+--------------+
| Add    1000000 | 3244.68600ms |
+----------------+--------------+
| Delete 1000000 | 539.16500ms  |
+----------------+--------------+

Relation ``dict : odict``

+---------------------------+----------+
| creating     1000 objects | 1:73.285 |
+---------------------------+----------+
| deleting     1000 objects | 1: 0.967 |
+---------------------------+----------+
| creating    10000 objects | 1: 4.173 |
+---------------------------+----------+
| deleting    10000 objects | 1: 1.207 |
+---------------------------+----------+
| creating   100000 objects | 1: 3.979 |
+---------------------------+----------+
| deleting   100000 objects | 1: 1.037 |
+---------------------------+----------+
| creating  1000000 objects | 1: 4.020 |
+---------------------------+----------+
| deleting  1000000 objects | 1: 1.088 |
+---------------------------+----------+

Relation ``OrderedDict : odict``

+---------------------------+----------+
| creating     1000 objects | 1: 5.736 |
+---------------------------+----------+
| deleting     1000 objects | 1: 0.703 |
+---------------------------+----------+
| creating    10000 objects | 1: 0.262 |
+---------------------------+----------+
| deleting    10000 objects | 1: 0.675 |
+---------------------------+----------+
| creating   100000 objects | 1: 0.281 |
+---------------------------+----------+
| deleting   100000 objects | 1: 0.690 |
+---------------------------+----------+
| creating  1000000 objects | 1: 0.317 |
+---------------------------+----------+
| deleting  1000000 objects | 1: 0.754 |
+---------------------------+----------+


Usage
-----

Import and create ordered dictionary.

.. code-block:: python

    from odict import odict
    od = odict()

type conversion to ordinary ``dict``. This will fail.

.. code-block:: pycon

    >>> dict(odict([(1, 1)]))
    {1: [nil, 1, nil]}

The reason for this is here -> http://bugs.python.org/issue1615701

The ``__init__`` function of ``dict`` checks wether arg is subclass of dict,
and ignores overwritten ``__getitem__`` & co if so.

This was fixed and later reverted due to behavioural problems with ``pickle``.

Use one of the following ways for type conversion.

.. code-block:: pycon

    >>> dict(odict([(1, 1)]).items())
    {1: 1}

    >>> odict([(1, 1)]).as_dict()
    {1: 1}

It is possible to use abstract mixin class ``_odict`` to hook another dict base
implementation. This is useful i.e. when persisting to ZODB. Inheriting from
``dict`` and ``Persistent`` at the same time fails.

.. code-block:: python

    from persistent.dict import PersistentDict
    class podict(_odict, PersistentDict):

        def _dict_impl(self):
            return PersistentDict


Misc
----

In a C reimplementation of this data structure, things could be simplified
(and speed up) a lot if given a value you can at the same time find its key.
With that, you can use normal C pointers.


TestCoverage
------------

.. image:: https://travis-ci.org/bluedynamics/odict.svg?branch=master
    :target: https://travis-ci.org/bluedynamics/odict

Summary of the test coverage report::

    Name                    Stmts   Miss  Cover
    -------------------------------------------
    src/odict/__init__.py       1      0   100%
    src/odict/pyodict.py      237      0   100%
    src/odict/tests.py        198      0   100%
    -------------------------------------------
    TOTAL                     436      0   100%


Python Versions
---------------

- Python 2.6+, 3.2+, pypy

- May work with other versions (untested)


Contributors
============

- bearophile (Original Author)

- Robert Niederreiter (Author)

- Georg Bernhard

- Florian Friesdorf

- Jens Klein

under the `Python Software Foundation License <http://www.opensource.org/licenses/PythonSoftFoundation.php>`_.
