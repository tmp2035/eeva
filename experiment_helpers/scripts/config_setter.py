# there functions for interactive config setting defined

# imports

import pathlib
import matplotlib.pyplot as plt

from ipywidgets import interactive, widgets

from omegaconf import OmegaConf

from cache.utils.req_generator import Generator
import matplotlib.gridspec as gridspec
from IPython.display import display, clear_output


from hydra import compose,  initialize
from hydra.core.config_store import ConfigStore

from cache import Experiment, Config

from pathlib import Path
import seaborn as sns
from itertools import product
from collections import defaultdict


def plot_req(num_requests = 100, num_tables = 50, max_pages =  100, q = 0.5,p_scan = 0.0, gamma = 0, c_scan = 0.7, c_get = 1., name = ""):
    g = Generator(num_requests, num_tables, max_pages, q, p_scan, gamma)
    scan_probs, get_probs, _ = g.get_statistics()
    print(len(scan_probs))
    fig = plt.figure(tight_layout=True, figsize= (16, 4))
    gs = gridspec.GridSpec(1, 4)

    ax = fig.add_subplot(gs[0, 0])
    ax.plot(scan_probs + get_probs)
    ax.set_ylabel("request prob")
    ax.set_xlabel("page ID")

    ax = fig.add_subplot(gs[0, 1])
    ax.plot(scan_probs * c_scan + get_probs * (c_get  ))
    ax.set_ylabel(r"$E w_i/T$ ~ expected weight")
    ax.set_xlabel("page ID")

    # ax = fig.add_subplot(gs[0, 2])
    # ax.plot((scan_probs * c_scan + get_probs * (c_get  ))/ (scan_probs + get_probs))
    # ax.set_ylabel("Mean cost")
    # ax.set_xlabel("page ID")

    ax = fig.add_subplot(gs[0, 2])
    ax.hist(scan_probs + get_probs, bins = max_pages + 1, density=True)
    ax.set_ylabel("Prob hist")
    ax.set_xlabel("page ID")

    ax = fig.add_subplot(gs[0, 3])
    ax.hist(scan_probs * c_scan + get_probs * (c_get), bins = max_pages + 1, density=True)
    ax.set_ylabel("Prob hist")
    ax.set_xlabel("page ID")
    
    display(fig)
    plt.close(fig)
    # num_requests = 100, num_tables = 50, max_pages =  100, q = 0.5,p_scan = 0.0, gamma = 0, c_scan = 0.7, c_get = 1., name = ""):
    # clear_output(wait=True)
    return p_scan


class Board:
    def __init__(self, savepath, config_path= "./../conf/", config_name = "config"):
        self.savepath = Path(savepath)
        self.config_path = config_path
        self.config_name = config_name
        try:
            with initialize(version_base="1.3", config_path=self.config_path,):
                cfg = compose(config_name=self.config_name, overrides=[])
        except Exception as e:
            print("ERROR: ", e)
        self.cfg = cfg

    def save_config(self):
        assert hasattr(self, 'dct')
        print("try save")
        but = self.dct
        num_requests = but["num_requests"].value
        num_tables = but["num_tables"].value
        max_pages = but["max_pages"].value
        q = but["q"].value
        p_scan = but["p_scan"].value
        gamma = but["gamma"].value
        c_scan = but["c_scan"].value
        c_get = but["c_get"].value
        name = but["name"].value

        if name == "":
            name = f"_{num_requests}_{num_tables}_{max_pages}_{q}_{p_scan}_{gamma}"
        print(f"saving: {name},\n path: {self.config_path}")
        from os import walk

        f = []
        for (dirpath, dirnames, filenames) in walk("./../"):
            f.extend(filenames)
            f.extend(dirnames)
            break
        print(f)
        
        cfg = self.cfg
        cfg.generation_params.num_requests = num_requests
        cfg.generation_params.num_tables = num_tables
        cfg.generation_params.gamma = gamma
        cfg.generation_params.max_pages = max_pages
        cfg.generation_params.p_scan = p_scan
        cfg.generation_params.q = q

        cfg.cost_params.c_scan = c_scan
        cfg.cost_params.c_get = c_get
        cfg.proposed_params.beta = c_scan
        cfg.proposed_params.alpha = c_get

        OmegaConf.save(cfg, self.savepath/f"{name}.yaml")


    def get_plot(self):
        from ipywidgets import interactive, HBox, Layout,VBox

        num_requests = widgets.IntSlider(self.cfg.generation_params.num_requests, min= 0, max=200_000, step=1000)
        num_tables = widgets.IntSlider(self.cfg.generation_params.num_tables,  min= 0, max =100, step = 10)
        max_pages =  widgets.IntSlider(self.cfg.generation_params.max_pages, min=  0,  max= 1000,step= 10)
        q = widgets.FloatSlider(self.cfg.generation_params.q,  min= 0.0, max= 1.0, step=0.01,)

        my_values = [i / 10000 for i in range(10000)]  # [0.001, 0.002, ...] Or use numpy to list
        p_scan = widgets.SelectionSlider(options=[("%g"%i,i) for i in my_values])
        p_scan.value = self.cfg.generation_params.p_scan
        # p_scan = widgets.FloatSlider(0.0,  min= 0.0, max= 1.0, step=0.001,) 
        gamma = widgets.FloatSlider(0.,  min= 0.0, max= 1.0, step=0.01,)
        c_scan = widgets.FloatSlider(self.cfg.cost_params.c_scan,  min= 0.0, max= 1.0, step=0.01,)
        c_get = widgets.FloatSlider(self.cfg.cost_params.c_get,  min= 0.0, max= 1.0, step=0.01,)
        name = widgets.Text(value = self.config_name)

        dct = {"num_requests": num_requests, 
                "num_tables": num_tables, "max_pages": max_pages,
                "q": q, "p_scan": p_scan, "gamma": gamma, "c_scan": c_scan, "c_get": c_get, "name": name,}

        widget = interactive(plot_req, **dct)

        controls = HBox(widget.children[:-1], layout = Layout(flex_flow='row wrap'))
        output = widget.children[-1]
        display(VBox([controls, output]))

        self.dct = dct