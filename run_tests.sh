#!/bin/sh
if [ -x "$(which python)" ]; then
    ./py2/bin/python -m unittest odict.tests
fi
if [ -x "$(which python3)" ]; then
    ./py3/bin/python -m unittest odict.tests
fi
if [ -x "$(which python3)" ]; then
    ./pypy/bin/python -m unittest odict.tests
fi
