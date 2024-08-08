# coding=utf-8

"""
this module contains the Req class, which describes a request

"""

translation = {ord(symb): "" for symb in ")( '"}


def parse_info(s):
    assert(len(s) > 0)
    a, b, c, d, *_ = s.translate(translation).split(",")
    assert a in ["get", "scan_all"], f"getting type {a} is unknown"
    return a, int(b), int(c), int(d)


class Req:
    def __init__(self, item_id, size=1, op=None, cost=-1, info=None, **kwargs):
        self._item_id = item_id
        self._size = size
        self._op = op
        self._cost = cost
        self._info = info

    @property
    def info(self):
        return self._info

    @property
    def item_id(self):
        return self._item_id

    @property
    def size(self):
        return self._size

    @property
    def op(self):
        return self._op

    @property
    def cost(self):
        return self._cost
