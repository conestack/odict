#!/bin/sh
./$1/bin/coverage run -m odict.tests
./$1/bin/coverage report
./$1/bin/coverage html
