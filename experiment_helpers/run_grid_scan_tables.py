"""
this experiment runs algoriths several times, 
varying number of tables to be scanned

this is done by changing partition of para
"""

import json
import os
from copy import deepcopy
from pathlib import Path

import fire
from hydra import compose, initialize
from joblib import Parallel, delayed
from tqdm import tqdm

from eeva import Experiment

import numpy as np

def runner(cfg, conf_name):
    exp = Experiment.from_config(cfg)
    exp.generate_trace()
    exp.run()
    exp.save(conf_name, rewrite=True)


def main(config_path=".", conf_name=""):
    assert len(conf_name) > 0
    p = Path(os.path.dirname(os.path.realpath(__file__)), os.path.dirname(os.path.realpath(__file__)), config_path)
    if not p.exists():
        raise SystemExit(f"{p} is not exists")

    with initialize(version_base="1.3", config_path=config_path):
        cfg = compose(config_name=conf_name, overrides=[])

    # provide experiments for this partitions of scanned tables
    partitions = [x * 0.1 for x in range(1, 7)]

    path = Path(cfg.paths.save_path) / conf_name
    if not path.exists():
        os.mkdir(path)

    exp = Experiment.from_config(cfg)

    def f(exp, part):
        """v
        there part means part of tables to be scanned.
        To not generate all database again we change some parameters of generator 
        """
        
        # code from eeva.utils.req_generator: Generator: __post_init__
        gen = exp.generator
        
        # there we use partition
        num_tables_to_scan = int(gen.num_tables * part)
        
        gen.num_tables_to_scan = num_tables_to_scan
        probs = np.ones((gen.num_tables,))
        gen.probs_scan = probs.copy()
        gen.probs_get = probs.copy()
        gen.probs_scan[:num_tables_to_scan] *= 10
        gen.probs_get[:num_tables_to_scan] /= 10
        # gen.probs_get[num_tables_to_scan : min( 2 * num_tables_to_scan, gen.num_tables)] /= 10

        gen.probs_get /= np.sum(gen.probs_get)
        gen.probs_scan /= np.sum(gen.probs_scan)
        # end of changes
        # to distinguish trace from others
        gen._name = f"table_{part}"
        
        exp.generate_trace()
        exp.run()
        return part, exp.rez

    parr = Parallel(n_jobs=6, return_as="generator")
    del_f = delayed(f)
    for i in tqdm(range(5), leave=False):
        rez = {}
        runn = parr(del_f(exp, part) for part in partitions)
        for part, r in tqdm(runn, leave=False):
            rez[part] = deepcopy(r)

        if not (path / f"{i}").exists():
            os.mkdir(path / f"{i}")
        with open(path / f"{i}/rez.pickle", "w") as f:
            json.dump(rez, f)


if __name__ == "__main__":
    fire.Fire(main)
