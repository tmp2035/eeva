# coding=utf-8

import numpy as np
from dataclasses import dataclass
import scipy

from collections import defaultdict
from .abstractCache import Cache
from .requestItem import Req


import numpy as np
from dataclasses import dataclass, field
import scipy

from collections import defaultdict
from .abstractCache import Cache
from .requestItem import Req, parse_info

@dataclass
class cache_item:
    req_id: int = -1
    weight: float = 1.0
    age: int = 0

REQ_ID = 0
WEIGHT = 1
AGE = 2

@dataclass
class table_item:
    weight: float = 1.
    pages: list[float] = field(default_factory=list)


class EEvAT(Cache):
    """
    PROPOSED algorithm for cache eviction

    weights update:

    w = w * beta            # on access
    w = w * (1 - gamma)     # on iteration

    self.cacheline_dict [item_id: item_pos]
    self.table_weights: [table_id: table_weight, list(loaded pages)]
    """

    def __init__(self, cache_size,alpha , beta , **kwargs):
        super(EEvAT,self).__init__(cache_size, **kwargs)
        self.table_weights = defaultdict(table_item)
        self.cacheline_dict = dict()

        self.alpha = alpha
        self.beta = beta
        self.step = 0

        self._scan_proccessing = False

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
        _, table_num, _, _ = parse_info(req_item.info)
        return self.table_weights[table_num].weight
    def _update_init_weight(self, req_item):
        req_type, table_num, pg_ind, table_size = parse_info(req_item.info)
        if req_type == "scan_all":
            if self._scan_proccessing == False and pg_ind == 0:
                self._scan_proccessing = True
            if self._scan_proccessing == True and pg_ind == table_size - 1:
                self.table_weights[table_num].weight += self.beta
        else:
            self._scan_proccessing = False
            self.table_weights[table_num].weight += 1./table_size * self.alpha
    
    def _update(self, req_item, **kwargs):
        """ the given element is in the cache,
        now update cache metadata and its content

        for EEvA-t this function do nothing because only table weights are used

        :param **kwargs:
        :param req_item:
        :return: None
        """
        return

    def _insert(self, req_item, w, **kwargs):
        """
        the given element is not in the cache, now insert it into cache
        :param **kwargs:
        :param req_item:
        :return: evicted element or None
        """

        assert len(self.cacheline_dict) < self.cache_size, "too many items in cache"

        req_type, table_num, pg_ind, table_size = parse_info(req_item.info)
        req_id = req_item
        if isinstance(req_item, Req):
            req_id = req_item.item_id


        self.cacheline_dict[req_id] = True
        self.table_weights[table_num].pages.append(req_id)

    def evict(self, w, **kwargs):
        """
        evict one cacheline from the cache

        :param
        w: to be inserted element weight

           **kwargs:
        :return: id of evicted cacheline
        """
        victim_table = min(self.table_weights.items(), \
                    key= lambda x: x[1].weight if len(x[1].pages) > 0 else float("inf"))[1]
        victim = victim_table.pages[0]
        del victim_table.pages[0]

        self.cacheline_dict.pop(victim)
        return

    def access(self, req_item, **kwargs):
        """
        request access cache, it updates cache metadata,
        it is the underlying method for both get and put

        :param **kwargs:
        :param req_item: the request from the trace, it can be in the cache, or not
        :return: None
        """
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
                evict_item = self.evict(w)
                assert llen > len(self.cacheline_dict), "item is not deleted"
            self._insert(req_item, w)
            
            self._update_init_weight(req_item)
            return False

    @property
    def name(self):
        if hasattr(self, "_name"):
            return self._name
        else:
            print('vtf man??')
            raise ValueError()

    @name.setter
    def name(self, n):
        self._name  = n

    def __contains__(self, req_item):
        return req_item in self.cacheline_dict

    def __len__(self):
        return len(self.cacheline_dict)

    def __repr__(self):
        return "LRU cache of size: {}, current size: {}".\
            format(self.cache_size, len(self.cacheline_dict))
