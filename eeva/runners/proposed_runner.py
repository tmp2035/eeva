from collections import defaultdict
from itertools import product

import fire
from joblib import Parallel, delayed

from eeva import algorithm

from ..algorithm.requestItem import Req
from ..utils.time_checker import timer


def trace_reader(trace_file):
    with open(trace_file, "r") as f:
        _ = f.readline()  # линия с названиями столбцов
        while (s := f.readline()) != "":
            yield s


@timer
def simulate(algorithm, trace_file):
    reader = trace_reader(trace_file)
    hits = []
    miss_count = 0
    all_reqs = 0
    for elem in reader:
        all_reqs += 1
        item_id, info = elem.split(";")
        req = Req(item_id=int(item_id), info=info)
        ok = algorithm.access(req)
        if ok:
            hits.append(1)
        else:
            miss_count += 1
            hits.append(0)
    return algorithm.name, algorithm.cache_size, miss_count / all_reqs, hits


def run(
    tracepath: str,
    cache_sizes: str,
    algorithms: str,
    alpha: float,
    beta: float,
    move_cost: float,
    return_trace_hit: bool = False,
    n_jobs=12,
):
    assert tracepath is not None
    sizes = list(map(int, cache_sizes.split(",")))
    algos = list(map(str, algorithms.split(",")))

    lst = []
    for (alg_name), size in product(algos, sizes, repeat=1):
        alg = algorithm.alg_dict[alg_name](cache_size=size, alpha=alpha, beta=beta, move_cost=move_cost)
        alg.name = algorithm.alg_names[alg_name]
        lst.append(alg)

    # n_jobs = 1
    if n_jobs > 1:
        del_sim = delayed(simulate)
        comp_rez = Parallel(n_jobs=n_jobs, return_as="generator")(del_sim(elem, tracepath) for elem in lst)
    else:
        comp_rez = [simulate(elem, tracepath) for elem in lst]

    dct = defaultdict(list)
    time_dct = defaultdict(list)
    for rez in comp_rez:
        dct[rez[0]].append(rez[1:-1])
        time_dct[rez[0]].append([rez[1], rez[-1]])

    return dct, time_dct


if __name__ == "__main__":
    fire.Fire(run)

    # CACHE_NAME_TO_CLASS_DICT
