import random
from dataclasses import dataclass

import numpy as np
import pandas as pd


def zipf_probs(n, q):
    """
    every element i have probabilty ~ (1/n)^1
    """
    probs = np.arange(1, n + 1) ** (-q)
    probs = probs / probs.sum()
    return probs


class Table:
    def __init__(self, num_pages, q=0.7) -> None:
        assert 0 < num_pages
        self.num_pages = num_pages
        self.distr = zipf_probs(num_pages, q)


class Database:
    def __init__(self, tables_list: list[Table], max_pages) -> None:
        assert all(t.num_pages < max_pages for t in tables_list)
        self.tables: Table = tables_list
        self.max_pages = max_pages

    def table_size(self, t_num):
        return self.tables[t_num].num_pages

    def add_table(self, t):
        assert t.num_pages <= self.max_pages, f"{t.num_pages=} greater than {self.max_pages=}"
        self.tables.append(t)

    def page2ind(self, t_num, p_num):
        return t_num * self.max_pages + p_num

    def ind2page(self, ind):
        return ind // self.max_pages, ind % self.max_pages

    def get(self, t_num, p_num):
        assert t_num < len(self.tables) and 0 <= p_num < self.tables[t_num].num_pages
        return (self.page2ind(t_num, p_num), ("get", t_num, p_num, self.tables[t_num].num_pages, 1))

    # def scan_list(self, t_num, p_nums):
    #     assert t_num < len(self.tables) and all(x < self.tables[t_num].num_pages for x in p_nums)
    #     return [(self.page2ind(t_num, x), 'scan_list') for x in p_nums]

    def scan_all(self, t_nums, gamma):
        assert all(0 <= x < len(self.tables) for x in t_nums)
        return [
            (
                self.page2ind(t_n, p_n),
                ("scan_all", t_n, p_n, self.tables[t_n].num_pages, 0 if np.random.rand() < gamma else 1),
            )
            for t_n in t_nums
            for p_n in range(self.tables[t_n].num_pages)
        ]


@dataclass
class Generator:
    """
    Class for generation requests for one experiments
    Parameters:
        num_requests: int
            numver of times that get or scan will be selected
        num_tables: int
            number of tables that modeled database will contain
        max_pages: int
            maximum number of pages per table
        q: float = 1
            parameter of zipf distribution for dencity modelling in table
        p_scan: float
            probability to select scan instead of table
        gamma: float
            partition of dirty pages in scanned table
    """

    num_requests: int = 0
    num_tables: int = 0
    max_pages: int = 0
    q: float = 1
    _p_scan: float = 0.0
    gamma: float = 0.0

    def __post_init__(self) -> None:
        self.database = Database([], self.max_pages)

        self.num_pages = 0
        for _ in range(self.num_tables):
            size = random.randint(self.max_pages // 2, self.max_pages)
            self.num_pages += size
            self.database.add_table(Table(size, q=self.q))

        num_tables_to_scan = self.num_tables // 3
        self.num_tables_to_scan = num_tables_to_scan
        probs = np.ones((self.num_tables,))
        self.probs_scan = probs.copy()
        self.probs_get = probs.copy()
        self.probs_scan[:num_tables_to_scan] *= 10
        if self.p_scan != 0.0:
            self.probs_get[:num_tables_to_scan] /= 10

        self.probs_get /= np.sum(self.probs_get)
        self.probs_scan /= np.sum(self.probs_scan)

    @property
    def p_scan(self):
        return self._p_scan

    @p_scan.setter
    def p_scan(self, value):
        self._p_scan = value
        probs = np.ones((self.num_tables,))
        self.probs_scan = probs.copy()
        self.probs_get = probs.copy()
        self.probs_scan[: self.num_tables_to_scan] *= 10
        if self.p_scan != 0.0:
            self.probs_get[: self.num_tables_to_scan] /= 10

        self.probs_get /= np.sum(self.probs_get)
        self.probs_scan /= np.sum(self.probs_scan)

    def get_statistics(self) -> tuple[list[float], list[float]]:
        """
        computes values ~ to request page using proposed type of requests

        Return : scan_probs, get_probs

        So, expected pages in request with duration T:

        T * np.sum(scan_probs + get_probs)

        Expected pages to be scanned in request with duration T:
        T * np.sum(scan_probs)
        """
        scan_probs = []
        get_probs = []
        scan_pages = []
        for i, tab in enumerate(self.database.tables):
            fv = 1.0 if i < self.num_tables_to_scan else 0.0
            scan_pages.extend(np.full(shape=(tab.num_pages,), fill_value=fv))
            scan_probs.extend(self.probs_scan[i] * np.full(shape=(tab.num_pages,), fill_value=1.0))
            get_probs.extend(self.probs_get[i] * tab.distr)

        scan_probs = np.array(scan_probs) * self.p_scan
        get_probs = np.array(get_probs) * (1 - self.p_scan)

        return scan_probs, get_probs, scan_pages

    def name(self):
        return f"_{self.num_requests}_{self.num_tables}_{self.max_pages}_{self.q}_{self.p_scan}_{self.gamma}"

    def generate_requests(self, num_requests: int | None = None) -> list:
        """
        Generates a range of requests with related information.
        one element if request has the following structure:
        (page_id, (req_type, table_num, page_num, table_size, is_durty)

        req_type in ["get", "scan_all"]
        is_durty in {0, 1}, used to detect durty pages in scan.
            Used only for metrics computation afger algorithms work.
        """
        if num_requests is None:
            num_requests = self.num_requests
        requests = []
        for _ in range(num_requests):
            req = np.random.choice(["get", "scan_all"], p=[1.0 - self.p_scan, self.p_scan])
            if req == "get":
                t_num = np.random.choice(self.num_tables, p=self.probs_get)
                p_num = np.random.choice(self.database.table_size(t_num), p=self.database.tables[t_num].distr)
                requests.append(self.database.get(t_num, p_num))
            if req == "scan_all":
                t_nums = np.random.choice(self.num_tables, p=self.probs_scan, size=1, replace=False)
                requests.extend(self.database.scan_all(t_nums, gamma=self.gamma))
        return requests

    def save_requests(self, requests, name):
        pd.DataFrame(requests, columns=["pg_id", "req_info"]).to_csv(name, sep=";", index=False)


# ###### ####

@dataclass
class DynamicGenerator(Generator):
    """
    Class for trace generation with changing distribution over pages.
    In this case we use the same distribution at the start of disrtibution as in the Generator above
    and continuously change it over time to get another distribution.

    Parameters:
        num_requests: int
            numver of times that get or scan will be selected
        num_tables: int
            number of tables that modeled database will contain
        max_pages: int
            maximum number of pages per table
        q: float = 1
            parameter of zipf distribution for dencity modelling in table
        p_scan: float
            probability to select scan instead of table
        gamma: float
            partition of dirty pages in scanned table
    """

    def __post_init__(self) -> None:
        self.database = Database([], self.max_pages)

        self.num_pages = 0
        for _ in range(self.num_tables):
            size = random.randint(self.max_pages // 2, self.max_pages)
            self.num_pages += size
            self.database.add_table(Table(size, q=self.q))

        num_tables_to_scan = self.num_tables // 3
        self.num_tables_to_scan = num_tables_to_scan


        # there will be differences in 
        probs = np.ones((2, self.num_tables))
        self.probs_scan = probs.copy()
        self.probs_get = probs.copy()

        # сначала первая треть сканируется, потом вторая треть
        self.probs_scan[0, :num_tables_to_scan] *= 5
        self.probs_scan[1,num_tables_to_scan : 3*num_tables_to_scan] *= 5
        # для  get операций сначала на первой трети меньше операций get, потом распределение становится равномерным.
        if self.p_scan != 0.0:
            self.probs_get[1, : 2 * num_tables_to_scan] /=10

        self.probs_get /= np.sum(self.probs_get, axis = 1)[:, None]
        self.probs_scan /= np.sum(self.probs_scan, axis = 1)[:, None]

    @property
    def p_scan(self):
        return self._p_scan

    @p_scan.setter
    def p_scan(self, value):
        self._p_scan = value
        # raise NotImplemented("There is no p_scan setter for dynamic trace generator")

    def get_statistics(self) -> tuple[list[float], list[float]]:
        # this is dummy variables
        return np.array([1]), np.array([1]), np.array([1])

    def name(self):
        return f"_{self.num_requests}_{self.num_tables}_{self.max_pages}_{self.q}_{self.p_scan}_{self.gamma}"

    def generate_requests(self, num_requests: int | None = None) -> list:
        """
        Generates a range of requests with related information.
        one element if request has the following structure:
        (page_id, (req_type, table_num, page_num, table_size, is_durty)

        req_type in ["get", "scan_all"]
        is_durty in {0, 1}, used to detect durty pages in scan.
            Used only for metrics computation afger algorithms work.

        При генерации используется линейная комбинация тех плотностей распределений запросов по таблицам
        """
        if num_requests is None:
            num_requests = self.num_requests
        requests = []
        for iter in range(num_requests):
            req = np.random.choice(["get", "scan_all"], p=[1.0 - self.p_scan, self.p_scan])
            if req == "get":
                probs = self.probs_get[0] if iter < num_requests//4 else self.probs_get[1]
                # (np.array([num_requests - iter, iter], dtype=float)/num_requests)@ self.probs_get
                assert len(probs) == self.probs_get.shape[1]

                t_num = np.random.choice(self.num_tables, p=probs)
                p_num = np.random.choice(self.database.table_size(t_num), p=self.database.tables[t_num].distr)
                requests.append(self.database.get(t_num, p_num))
            if req == "scan_all":
                probs = self.probs_scan[0] if iter < num_requests//4 else self.probs_scan[1]
                #  (np.array([num_requests - iter, iter], dtype=float)/num_requests)@ self.probs_scan

                t_nums = np.random.choice(self.num_tables, p=probs, size=1, replace=False)
                requests.extend(self.database.scan_all(t_nums, gamma=self.gamma))
        return requests

    def save_requests(self, requests, name):
        pd.DataFrame(requests, columns=["pg_id", "req_info"]).to_csv(name, sep=";", index=False)
