
Yet another odict implementation.

  >>> from odict import odict
  >>> od = odict()
 
Changes
-------

  -A use try/except instead of __iter__ in __setitem__ to determine if value
   was already set.

  -Add missing ``__len__`` and ``__contains__`` functions.
   rnix, 2009-03-17
 
Credits
-------

  -Written by ``bearophile`` (Oct 12 2006)
   http://code.activestate.com/recipes/498195/

  -Eggified by Robert Niederreiter <rnix@squarewave.at> (Mar 17 2009)