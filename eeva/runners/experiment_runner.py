import json
import os
import pickle
import shutil
import warnings
from pathlib import Path
from typing import Dict
from copy import deepcopy

from eeva import Config

from ..utils import drawer as drawer
from ..utils.costs_calc import count_miss_types
from ..utils.req_generator import Generator, DynamicGenerator
from .libCache_runner import run_cachesim_size
from .proposed_runner import run


class Experiment:

    @staticmethod
    def clear(directory):
        directory = Path(directory)
        pass

    @staticmethod
    def from_save(directory):
        directory = Path(directory)
        with open(directory / "cfg.pickle", "rb") as f:
            config = pickle.load(f)
        with open(directory / "database.pickle", "rb") as f:
            generator = pickle.load(f)

        config.paths.datapath = directory
        config.paths.save_path = directory.parents[0]

        exp = Experiment.from_config(config, generator)
        exp.directory = directory
        exp.tracepath = directory / "data.csv"
        if (directory / "rez.json").exists():
            with open(directory / "rez.json", "r") as f:
                rez = json.load(f)
            exp.rez = rez
        if (directory / "times.json").exists():
            with open(directory / "times.json", "r") as f:
                times = json.load(f)
            exp.times = times
        exp.cache_sizes = exp.get_sizes()
        return exp

    @staticmethod
    def from_config(params: Config, generator: Generator = None, dynamic_generator = False):
        gen_params = params.generation_params
        if generator is None:
            if dynamic_generator is False:
                generator = Generator(
                    num_requests=gen_params.num_requests,
                    num_tables=gen_params.num_tables,
                    max_pages=gen_params.max_pages,
                    q=gen_params.q,
                    _p_scan=gen_params.p_scan,
                    gamma=gen_params.gamma,
                )
            else:
                generator = DynamicGenerator(
                    num_requests=gen_params.num_requests,
                    num_tables=gen_params.num_tables,
                    max_pages=gen_params.max_pages,
                    q=gen_params.q,
                    _p_scan=gen_params.p_scan,
                    gamma=gen_params.gamma,
                )


        libCache_params = {
            "CACHESIM_PATH": params.paths.lib_cache_sim,
            "tracepath": None,  # should be specified while running
            "algos": params.libCache_params.algos,
            "cache_sizes": None,  # should be specified while running
            "trace_format": params.libCache_params.trace_format,
            "trace_format_params": params.libCache_params.trace_format_params,
        }

        algos = "EEvAGreedy,EEvASeq,EEvAT"
        if hasattr(params.proposed_params, "algos"):
            algos = params.proposed_params.algos
        proposed_params = {
            "tracepath": None,  # should be specified while running
            "cache_sizes": None,
            "algorithms": algos,
            "alpha": params.proposed_params.alpha,
            "beta": params.proposed_params.beta,
            "move_cost": params.proposed_params.move_cost,
            "return_trace_hit": params.proposed_params.return_trace_hit,
        }

        rez = Experiment(generator, libCache_params, proposed_params, params)
        return rez

    def __init__(self, generator: Generator, libCache_params: Dict, proposed_params: Dict, params: Config):
        """
        params is a structure generateb by config
        """
        self.config = params
        self.generator = generator
        self.libCache_params = libCache_params
        self.proposed_params = proposed_params
        self.datapath = Path(params.paths.datapath)
        self.runs_history = []
        assert self.datapath.exists(), f"folder for data is not exists: {self.datapath}"

        self.savepath = Path(params.paths.save_path)
        assert self.savepath.exists(), f"folder for results saving is not exists: {self.savepath}"

    def get_sizes(self):
        percents = self.config.shared_parameters.cache_sizes
        full_pages = self.generator.num_pages
        sizes = []
        for p in map(float, percents.split(",")):
            val = int(full_pages * p / 100)
            if val > 0:
                sizes.append(str(val))
        return ",".join(sizes)

    def generate_trace(self):
        req = self.generator.generate_requests()
        tracepath = self.datapath / (self.generator.name() + ".csv")
        self.generator.save_requests(req, tracepath)
        self.tracepath = tracepath
        self.cache_sizes = self.get_sizes()

    def postprocess(self, dct):
        self.runs_history.append(deepcopy(dct))
        for key, val in dct.items():
            for i in range(len(val)):
                tmp = count_miss_types(self.tracepath, val[i][-1])
                dct[key][i] = list(dct[key][i][:2]) + list(tmp)

    def run_libCache(self):
        if not Path(self.config.paths.lib_cache_sim).exists():
            warnings.warn("Libcachesim is not installed. Experiments will run without some algorithms.")
            return
        assert hasattr(
            self, "tracepath"
        ), "tracepath is not specified. Previously generate trace or specify by existing data"
        if not hasattr(self, "cache_sizes") or self.cache_sizes is None:
            self.cache_sizes = self.get_sizes()
        self.libCache_params["tracepath"] = str(self.tracepath)
        self.libCache_params["cache_sizes"] = self.cache_sizes
        rez_lib = run_cachesim_size(**self.libCache_params)
        self.postprocess(rez_lib)
        if hasattr(self, "rez"):
            self.rez.update(rez_lib)
        else:
            self.rez = rez_lib

    def run_proposed(self, alpha=None, beta=None, move_cost=None):
        assert hasattr(
            self, "tracepath"
        ), "tracepath is not specified. Previously generate trace or specify by existing data"
        if not hasattr(self, "cache_sizes") or self.cache_sizes is None:
            self.cache_sizes = self.get_sizes()
        self.proposed_params["tracepath"] = str(self.tracepath)
        self.proposed_params["cache_sizes"] = self.cache_sizes

        if alpha is not None:
            self.proposed_params["alpha"] = alpha
        if beta is not None:
            self.proposed_params["beta"] = beta
        if move_cost is not None:
            self.proposed_params["move_cost"] = move_cost
        proposed_dct, time_dct = run(**self.proposed_params)
        self.times = time_dct
        self.postprocess(proposed_dct)
        if hasattr(self, "rez"):
            self.rez.update(proposed_dct)
        else:
            self.rez = proposed_dct

    def run(self):
        assert hasattr(
            self, "tracepath"
        ), "tracepath is not specified. Previously generate trace or specify by existing data"
        if not hasattr(self, "cache_sizes") or self.cache_sizes is None:
            self.cache_sizes = self.get_sizes()
        self.run_libCache()
        self.run_proposed()
        return self.rez

    def draw(self):

        dct_bar = drawer.plot_bar(self)
        drawer.save_figures(dct_bar, self.directory)

        dct_dencity = drawer.plot_dencity(self)
        drawer.save_figures(dct_dencity, self.directory)

        dct_rez = drawer.plot_dict(self)
        drawer.save_figures(dct_rez, self.directory)

        dct_rez = drawer.plot_dict_pair(self)
        drawer.save_figures(dct_rez, self.directory)

        times = drawer.plot_time(self)
        drawer.save_figures(times, self.directory)

    def save(self, name: str = "", description: str = "", rewrite=False):
        assert hasattr(
            self, "tracepath"
        ), "tracepath is not specified. Previously generate trace or specify by existing data"
        assert hasattr(self, "rez"), "rezults is not computed, nothing to save"

        if name == "":
            name = self.generator.name()
        print(name)
        directory = self.savepath / name
        self.directory = directory

        if directory.exists() and not rewrite:
            raise Exception(f"path {directory} already exists. Try another name or delete this")
        elif not directory.exists():
            os.mkdir(directory)

        with open(directory / "cfg.pickle", "wb") as f:
            pickle.dump(self.config, f)
        with open(directory / "database.pickle", "wb") as f:
            pickle.dump(self.generator, f)
        with open(directory/"runs_history.pickle","wb") as f:
            pickle.dump(self.runs_history, f)
        with open(directory / "rez.json", "w") as f:
            json.dump(self.rez, f)
        with open(directory / "times.json", "w") as f:
            json.dump(self.times, f)
        if not (directory / "data.csv").exists():
            shutil.copyfile(self.tracepath, directory / "data.csv")

        self.draw()
