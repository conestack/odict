Changes
=======

1.6.2
-----

- Use class name instead of 'odict()' in ``__repr__``.
  [rnix]


1.6.1
-----

- pypi masness.
  [rnix]


1.6.0
-----

- Compatible with Python 3 and pypy.
  [rnix]


1.5.2
-----

- Fix permission problem in 1.5.1 release, some files were only rw by user.
  [jensens, 2016-11-25]


1.5.1
-----

- Implement ``__copy__`` and ``__deepcopy__`` in order to work with Python 2.7.
  [rnix, 2012-10-15]

- Use ``try/except`` instead of ``in`` in ``__contains__``.
  [rnix, 2012-10-15]


1.5.0
-----

- Implement ``alter_key``.
  [rnix, 2012-05-18]


1.4.4
-----

- Remove unused error variable.
  [rnix, 2011-11-28]

- Add note on why to check with ``==`` and ``!=`` against ``_nil``.
  [rnix, 2011-11-28]


1.4.3
-----

- Get rid of annoying warning about "global" usage in ``bench.py``.
  [jensens, 2011-09-20]


1.4.2
-----

- More ``copy`` testing.
  [rnix, 2010-12-18]

- Add ``has_key`` to odict.
  [rnix, 2010-12-18]


1.4.1
-----

- Fix release, README.rst was missing, added MANIFEST.in file to include it.
  [jensens, 2010-11-29]


1.4.0
-----

- Full test coverage.
  [chaoflow, rnix, 2010-08-17]

- Code cleanup and optimizing.
  [chaoflow, rnix, 2010-08-17]


1.3.2
-----

- Access ``dict`` API providing class via function ``_dict_impl()`` and
  provide odict logic as abstract base class ``_odict``.
  [rnix, 2010-07-08]


1.3.1
-----

- Add test for bool evaluation.
  [rnix, 2010-04-21]


1.3.0
-----

- Fix access to ``odict.lt`` and ``odict.lh`` properties. Now it's possible
  to overwrite ``__setattr__`` and ``__getattr__`` on ``odict`` subclass
  without hassle.
  [rnix, 2010-04-06]

- Add ``sort`` function to odict.
  [rnix, 2010-03-03]


1.2.6
-----

- Make ``odict`` serialize and deserialize properly.
  [gogo, 2010-01-12]


1.2.5
-----

- Add ``as_dict`` function. Supports type conto ordinary ``dict``.
  [rnix, 2009-12-19]

- Add benchmark script.
  [rnix, 2009-12-19]


1.2.4
-----

- Do not check for ``key in self`` on ``__delitem__``, ``KeyError`` is raised
  properly anyway. Huge Speedup!
  [rnix, jensens, 2009-12-18]


1.2.3
-----

- Move tests to seperate file and make egg testable with
  ``python setup.py test``.
  [rnix, 2009-12-07]

- improve ``lt`` and ``lh`` properties to make ``odict`` work with
  ``copy.deepcopy``.
  [rnix, 2009-12-07]


1.2.2
-----

- Use try/except instead of ``__iter__`` in ``__setitem__`` to determine if
  value was already set.
  [rnix, 2009-07-17]


1.2.1
-----

- Add missing ``__len__`` and ``__contains__`` functions.
  [rnix, 2009-03-17]


1.2.0
-----

- Eggified
  [rnix, 2009-03-17]


< 1.2
-----

- http://code.activestate.com/recipes/498195/
  [bearophile, 2006-10-12]

  
