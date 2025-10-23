# Python Software Foundation License
from collections import OrderedDict
from .pyodict import odict
try:
    from .codict import codict
    HAS_CODICT = True
except ImportError:
    HAS_CODICT = False
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
    start = time.perf_counter()
    create(factory, _range)
    mid = time.perf_counter()
    delete(_range)
    end = time.perf_counter()
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

    if HAS_CODICT:
        head('adding and deleting ``codict`` Cython-optimized objects')
        print(CREATE_DELETE_ROW)
        codict_results = {
            1000: result(codict, 1000),
            10000: result(codict, 10000),
            100000: result(codict, 100000),
            1000000: result(codict, 1000000),
        }

        head('relation ``odict : codict``')
        print(RELATION_ROW)
        for key, value in odict_results.items():
            ostart, omid, oend = value
            cstart, cmid, cend = codict_results[key]
            relation_create = (cmid - cstart) / (omid - ostart)
            relation_delete = (cend - cmid) / (oend - omid)
            relation_row('creating', key, relation_create)
            relation_row('deleting', key, relation_delete)

        head('relation ``dict : codict``')
        print(RELATION_ROW)
        for key, value in dict_results.items():
            dstart, dmid, dend = value
            cstart, cmid, cend = codict_results[key]
            relation_create = (cmid - cstart) / (dmid - dstart)
            relation_delete = (cend - cmid) / (dend - dmid)
            relation_row('creating', key, relation_create)
            relation_row('deleting', key, relation_delete)

        head('relation ``OrderedDict : codict``')
        print(RELATION_ROW)
        for key, value in ordereddict_results.items():
            odstart, odmid, odend = value
            cstart, cmid, cend = codict_results[key]
            relation_create = (cmid - cstart) / (odmid - odstart)
            relation_delete = (cend - cmid) / (odend - odmid)
            relation_row('creating', key, relation_create)
            relation_row('deleting', key, relation_delete)
    else:
        print('')
        print('Cython codict not available (not compiled)')
        print('')


if __name__ == '__main__':
    run()
