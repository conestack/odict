# Python Software Foundation License
from __future__ import print_function
from collections import OrderedDict
from pyodict import odict
import time


CREATE_DELETE_ROW = '+----------------+---------------+'
RELATION_ROW = '+---------------------------+-----------+'

root = {}


def create(factory, _range):
    for i in range(_range):
        root[str(i)] = factory()


def delete(_range):
    for i in range(_range):
        del root[str(i)]


def result(factory, _range):
    start = time.clock()
    create(factory, _range)
    mid = time.clock()
    delete(_range)
    end = time.clock()
    print(
        '| Add    {0:7d} | {1:11.5f}ms |'.format(
            _range,
            (mid - start) * 1000,
        )
    )
    print(CREATE_DELETE_ROW)
    print(
        '| Delete {0:7d} | {1:11.5f}ms |'.format(
            _range,
            (end - mid) * 1000.0,
        )
    )
    print(CREATE_DELETE_ROW)
    return start, mid, end


def relation_row(action, _range, relation):
    print(
        '| {0:6s} {1:8d} objects |  1:{2:6.3f} |'.format(
            action,
            _range,
            relation,
        )
    )
    print(RELATION_ROW)


def head(value):
    print('')
    print(value)
    print('')


def run():
    head('adding and deleting builtin ``dict`` objects')
    print(CREATE_DELETE_ROW)
    dict_results = {
        1000: result(dict, 1000),
        10000: result(dict, 10000),
        100000: result(dict, 100000),
        1000000: result(dict, 1000000),
    }

    head('adding and deleting ``collection.OrderedDict`` objects')
    print(CREATE_DELETE_ROW)
    ordereddict_results = {
        1000: result(OrderedDict, 1000),
        10000: result(OrderedDict, 10000),
        100000: result(OrderedDict, 100000),
        1000000: result(OrderedDict, 1000000),
    }

    head('adding and deleting ``odict`` objects provided by this package')
    print(CREATE_DELETE_ROW)
    odict_results = {
        1000: result(odict, 1000),
        10000: result(odict, 10000),
        100000: result(odict, 100000),
        1000000: result(odict, 1000000),
    }

    head('relation ``dict : odict``')
    print(RELATION_ROW)
    for key, value in dict_results.items():
        dstart, dmid, dend = value
        ostart, omid, oend = odict_results[key]
        relation_create = (omid - ostart) / (dmid - dstart)
        relation_delete = (oend - omid) / (dend - dmid)
        relation_row('creating', key, relation_create)
        relation_row('deleting', key, relation_delete)

    head('relation ``OrderedDict : odict``')
    print(RELATION_ROW)
    for key, value in ordereddict_results.items():
        dstart, dmid, dend = value
        ostart, omid, oend = odict_results[key]
        relation_create = (omid - ostart) / (dmid - dstart)
        relation_delete = (oend - omid) / (dend - dmid)
        relation_row('creating', key, relation_create)
        relation_row('deleting', key, relation_delete)

if __name__ == '__main__':
    run()
