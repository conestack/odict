
odict
=====

Dictionary in which the *insertion* order of items is preserved (using an
internal double linked list). In this implementation replacing an existing 
item keeps it at its original position.

Internal representation: values of the dict:
::

  (pred_key, val, succ_key)

The sequence of elements uses as a double linked list. The ``links`` are dict
keys. ``self.lh`` and ``self.lt`` are the keys of first and last element 
inseted in the odict. In a C reimplementation of this data structure, things 
can be simplified (and speed up) a lot if given a value you can at the same 
time find its key. With that, you can use normal C pointers.

Memory used (Python 2.5):

  -set(int): 28.2 bytes/element
  
  -dict(int:None): 36.2 bytes/element
  
  -odict(int:None): 102 bytes/element

Speed:

  -This odict is about 20-25 times slower than a dict, for insert and del
   operations.
    
  -del too is O(1).

Usage
=====

  >>> from odict import odict
  >>> od = odict()

Requires
======== 

  -Python 2.4+

Changes
=======

Version 1.2.3
-------------

  -Move tests to seperate file and make egg testable with 
   ``python setup.py test``.
   rnix, 2009-12-07

  -improve ``lt`` and ``lh`` properties to make ``odict`` work with 
   ``copy.deepcopy``.
   rnix, 2009-12-07

Version 1.2.2
-------------

  -Use try/except instead of ``__iter__`` in ``__setitem__`` to determine if
   value was already set.
   rnix, 2009-07-17

Version 1.2.1
-------------

  -Add missing ``__len__`` and ``__contains__`` functions.
   rnix, 2009-03-17
   
Version 1.2.0
-------------

  -eggified
   rnix, 2009-03-17

Version < 1.2
-------------

  -http://code.activestate.com/recipes/498195/
   bearophile, 2006-10-12
 
Credits
=======
  
  -bearophile
  
  -Robert Niederreiter <rnix@squarewave.at>
