"""
this experiment runs algoriths several times on a greed of p_scam parameter
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

    probs = [x * 0.00018 for x in range(3)]

    path = Path(cfg.paths.save_path) / conf_name
    if not path.exists():
        os.mkdir(path)

    exp = Experiment.from_config(cfg)

    def f(p_scan):
        exp.generator.p_scan = p_scan
        exp.generate_trace()
        exp.run()
        return p_scan, exp.rez

    parr = Parallel(n_jobs=6, return_as="generator")
    del_f = delayed(f)
    for i in tqdm(range(5), leave=False):
        rez = {}
        runn = parr(del_f(p_scan) for p_scan in probs)
        for p_scan, r in tqdm(runn, leave=False):
            rez[p_scan] = deepcopy(r)

        if not (path / f"{i}").exists():
            os.mkdir(path / f"{i}")
        with open(path / f"{i}/rez.pickle", "w") as f:
            json.dump(rez, f)


if __name__ == "__main__":
    fire.Fire(main)
