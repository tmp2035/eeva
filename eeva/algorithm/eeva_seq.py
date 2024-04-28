# coding=utf-8


from collections import defaultdict

import numpy as np

from .abstractCache import Cache
from .requestItem import Req, parse_info

REQ_ID = 0
WEIGHT = 1
AGE = 2


def dict_def_val():
    return 1.0


class EEvASeq(Cache):
    """
    PROPOSED algorithm for cache eviction

    weights update:

    w = w * beta            # on access
    w = w * (1 - gamma)     # on iteration

    self.cacheline_dict [item_id: item_pos]
    self.cacheline_deq [item_pos: (req_id, weight, last_call_step)]
    """

    def __init__(self, cache_size, alpha, beta, move_cost, verbose=False, **kwargs):
        self.scans = 0
        super(EEvASeq, self).__init__(cache_size, **kwargs)
        self.cacheline_list = -np.ones(shape=(cache_size, 3), dtype=float)
        self.table_weights = defaultdict(dict_def_val)
        self.cacheline_dict = dict()
        self.hand = 0

        self.alpha = alpha
        self.beta = beta
        self.move_cost = move_cost
        self.cache_sum = 0.0
        self.step = 0

        self.table_max = -1
        self.page_max = -1
        self.max_value = 1e3

        self._scan_proccessing = False
        self._scan_table = None

        self.verbose = verbose
        if verbose:
            # in this algo we verbise search steps of eviction algorithm
            self.history = []
        # assert "k" in kwargs.keys(), 'parameter k is not setted'

    def _normalize(self):
        mm = max(self.table_max, self.page_max)
        if mm > self.max_value:
            self.cacheline_list[:, WEIGHT] /= mm
            for key in self.table_weights.keys():
                self.table_weights[key] = self.table_weights[key] / mm
            self.table_max = self.table_max / mm
            self.page_max = self.page_max / mm

    def has(self, req_id, **kwargs):
        """
        check whether the given id in the cache or not

        :return: whether the given element is in the cache
        """
        if req_id in self.cacheline_dict:
            return True
        else:
            return False

    def _get_init_weight(self, req_item):
        req_type, table_num, _, _ = parse_info(req_item.info)
        return self.table_weights[table_num]

    def _update_init_weight(self, req_item):
        req_type, table_num, pg_ind, table_size = parse_info(req_item.info)
        if req_type == "scan_all":
            if self._scan_proccessing is False and pg_ind == 0:
                self._scan_proccessing = True
            if self._scan_proccessing is True and pg_ind == table_size - 1:
                self.table_weights[table_num] += self.beta
        else:
            self._scan_proccessing = False
            self.table_weights[table_num] += +1.0 / table_size * self.alpha
        self.table_max = max(self.table_max, self.table_weights[table_num])

    def _update(self, req_item, **kwargs):
        """the given element is in the cache,
        now update cache metadata and its content

        :param **kwargs:
        :param req_item:
        :return: None
        """

        req_id = req_item
        if isinstance(req_item, Req):
            req_id = req_item.item_id

        list_pos = self.cacheline_dict[req_id]

        req_type, table_num, _, table_size = parse_info(req_item.info)

        delta = self.beta * (req_type == "scan_all") + self.alpha * (req_type == "get")
        self.cache_sum += delta
        self.cacheline_list[list_pos][[WEIGHT, AGE]] = np.array([self.cacheline_list[list_pos][1] + delta, self.step])

    def _insert(self, req_item, w, **kwargs):
        """
        the given element is not in the cache, now insert it into cache
        :param **kwargs:
        :param req_item:
        :return: evicted element or None
        """

        req_id = req_item
        if isinstance(req_item, Req):
            req_id = req_item.item_id

        assert int(self.cacheline_list[self.hand][0]) == -1

        self.cacheline_dict[req_id] = self.hand

        self.cache_sum += w
        self.cacheline_list[self.hand] = np.array([req_id, w, self.step])
        self.hand = (self.hand + 1) % self.cache_size

    def evict(self, w, **kwargs):
        """
        evict one cacheline from the cache

        :param
        w: to be inserted element weight

           **kwargs:
        :return: id of evicted cacheline
        """

        threshold = (self.cache_sum / (self.step) + self.move_cost) / len(self.cacheline_dict)
        pos = self.hand
        victim = self.hand
        i = 0
        while self.cacheline_list[pos][WEIGHT] / self.step > threshold:
            pos = (pos + 1) % self.cache_size
            i += 1
        victim = pos
        if self.verbose:
            self.history.append((threshold, i))

        self.cache_sum -= self.cacheline_list[victim][WEIGHT]

        self.cacheline_dict.pop(int(self.cacheline_list[victim][REQ_ID]))

        self.hand = victim
        self.cacheline_list[victim][REQ_ID] = -1
        return

    def access(self, req_item, **kwargs):
        """
        request access cache, it updates cache metadata,
        it is the underlying method for both get and put

        :param **kwargs:
        :param req_item: the request from the trace, it can be in the cache, or not
        :return: None
        """
        # self._normalize()
        self.step += 1

        req_id = req_item
        if isinstance(req_item, Req):
            req_id = req_item.item_id

        if self.has(req_id):
            self._update(req_item)
            self._update_init_weight(req_item)
            return True
        else:
            w = self._get_init_weight(req_item)
            if len(self.cacheline_dict) >= self.cache_size:
                llen = len(self.cacheline_dict)
                _ = self.evict(w)
                assert llen > len(self.cacheline_dict), "item is not deleted"
            self._insert(req_item, w)

            self._update_init_weight(req_item)
            return False

    def __contains__(self, req_item):
        return req_item in self.cacheline_dict

    def __len__(self):
        return len(self.cacheline_dict)

    def get_verbose(self):
        if self.verbose:
            return self.history
        return []

    @property
    def name(self):
        if hasattr(self, "_name"):
            return self._name
        else:
            print("vtf man??")
            raise ValueError()

    @name.setter
    def name(self, n):
        self._name = n

    def __repr__(self):
        return f"PROPOSED:{self.alpha=}_{self.beta=}"

    def __str__(self):
        return "PROPOSED:alpha={}_beta={}".format(self.alpha, self.beta)
