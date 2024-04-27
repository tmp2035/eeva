import matplotlib.pyplot as plt
import numpy as np
import seaborn as sns
import pandas as pd
##################################################################################
# set there style and etc parameters of firuges
##################################################################################
LINESTYLES = [
    ("d", "dashdot"),
    ("d", "dotted"),
    ("d", "solid"),
    ("d", "dashed"),
    ("long dash with offset", (1, (1, 0))),
    ("densely dashdotdotted", (0, (3, 1, 1, 1, 1, 1))),
    ("densely dashed", (0, (5, 1))),
    ("densely dashed", (0, (2, 2))),

    ("loosely dashdotdotted", (0, (3, 10, 1, 10, 1, 10))),
    ("densely dashdotted", (0, (3, 1, 1, 1))),
    ("dashdotdotted", (0, (3, 5, 1, 5, 1, 5))),
    ("dashdotted", (0, (3, 5, 1, 5))),
    ("densely dotted", (0, (1, 1))),
    ("long dash with offset", (5, (10, 3))),
    ("loosely dashdotted", (0, (3, 10, 1, 10))),
    ("densely dashdotdotted", (0, (3, 1, 1, 1, 1, 1))),
    ("loosely dashed", (0, (5, 10))),
    ("dashed", (0, (5, 5))),
    ("dashdotdotted", (0, (3, 5, 1, 5, 1, 5))),
    ("loosely dashdotdotted", (0, (3, 10, 1, 10, 1, 10))),
]


COLORMAP_NAME = "tab20"
DPI = 400
FIGSIZE = (17, 8)
FONTSIZE = 20


def get_fig_set_style(lines_count, shape = (1,1), figsize = None):
    colors_list = ["blue", "m", "red", "#0b5509", "y", "black", "m", "black", "y", "c", "g"]
    params = {'legend.fontsize': 40,
            'lines.markersize': 10,
            'axes.labelsize': 40,
            'axes.titlesize':40,
            'xtick.labelsize':30,
            'ytick.labelsize':30,
            "font.size":35,
        #  "text.usetex": True
         }
    sns.set_context("paper", rc=params)
    # sns.set_context("paper", font_scale=2.5, rc={"lines.linewidth": 2.5})
    if figsize is None:
        fig, ax = plt.subplots(*shape, dpi=DPI)
    else:
        fig, ax = plt.subplots(*shape, dpi=DPI, figsize = figsize)
    # plt.rcParams['text.usetex'] = True
    # plt.rcParams['text.latex.unicode'] = True
    plt.grid(which="both")
    return fig, ax, colors_list


##################################################################################

from matplotlib.ticker import FormatStrFormatter    
def plot_dencity(exp):

    c_scan, c_get = exp.config.cost_params.c_scan, exp.config.cost_params.c_get
    scan_probs, get_probs, _ = exp.generator.get_statistics()
    rez = dict()

    fig, ax, colors_list = get_fig_set_style(1)
    # ax.yaxis.set_major_formatter(FormatStrFormatter('%.2e'))
    ax.ticklabel_format(axis='y', scilimits=[-5, -5])
    ax.ticklabel_format(axis='x', scilimits=[-5, -5])
    # fig.suptitle("Density")
    ax.set_xlabel("page index")
    ax.set_ylabel("Prob density")
    ax.plot(scan_probs + get_probs, color = colors_list[0], linewidth = 2)
    fig.tight_layout()
    rez["density"] = fig

    fig, ax, colors_list = get_fig_set_style(1,)
    # ax.yaxis.set_major_formatter(FormatStrFormatter('%.2e'))
    ax.ticklabel_format(axis='y', scilimits=[-4, -4])
    ax.ticklabel_format(axis='x', scilimits=[-3, 4])
    # fig.suptitle("Cost density")
    ax.set_ylabel(r"$\mathbb{E} w_i\; /\;  N$")
    ax.set_xlabel(r"Page index, $i$")
    ax.plot(scan_probs * c_scan + get_probs * (c_get), color = colors_list[0], linewidth = 2)
    fig.tight_layout()
    rez["cost_density"] = fig

    fig, ax, colors_list = get_fig_set_style(1, figsize = (8,8))
    # ax.yaxis.set_major_formatter(FormatStrFormatter('%.2e'))
    ax.ticklabel_format(axis='y', scilimits=[-3, 3])
    ax.ticklabel_format(axis='x', scilimits=[-3, 3])
    # fig.suptitle("Mean cost")
    ax.set_xlabel("page index")
    ax.plot((scan_probs * c_scan + get_probs * (c_get  ))/ (scan_probs + get_probs), color = colors_list[0], linewidth = 2)
    fig.tight_layout()
    rez["mean_cost"] = fig

    return rez

import itertools

def plot_dict(exp,):
    percents = sorted(list(map(int, exp.config.shared_parameters.cache_sizes.split(","))))
    sizes = sorted([i[0] for i in next(iter(exp.rez.values()))])
    s2p = {s: p for s, p in zip(sizes, percents)}

    c_scan, c_get = exp.config.cost_params.c_scan, exp.config.cost_params.c_get
    dct = exp.rez
    figs = [get_fig_set_style(len(dct)) for i in range(4)]
    linestyles = itertools.cycle([e[1] for e in LINESTYLES])
    for i, (key, val) in enumerate(dct.items()):
        val = np.array([[s2p[x[0]], x[1], x[2]* c_scan + x[3]* c_get, x[2],x[3]]  for x in val])
        l_style = next(linestyles)
        for j in range(1, 5):
            figs[j-1][1].plot(val[:,0], val[:,j], label=key, color = figs[j-1][2][i], linestyle = l_style, linewidth = 2)        
    for i in range(4):
        figs[i][1].legend(loc="best")
        figs[i][1].set_xlabel("Buffer size")
    
    rez = dict()
    for i, name in enumerate(["Miss rate", r"Averaged time cost, $C$", "Scan misses", "Get misses"]):
        # figs[i][0].suptitle(name)
        figs[i][1].set_ylabel(name)
        figs[i][0].tight_layout()
        rez[name] = figs[i][0]
    return rez

from cache.utils.drawer import *

def plot_dict_pair(exp,):
    percents = sorted(list(map(int, exp.config.shared_parameters.cache_sizes.split(","))))
    sizes = sorted([i[0] for i in next(iter(exp.rez.values()))])
    s2p = {s: p for s, p in zip(sizes, percents)}

    c_scan, c_get = exp.config.cost_params.c_scan, exp.config.cost_params.c_get
    dct = exp.rez
    fig, ax, colors = get_fig_set_style(len(dct), (1, 2), figsize = (19, 9))
    linestyles = itertools.cycle([e[1] for e in LINESTYLES])
    for i, (key, val) in enumerate(dct.items()):
        val = np.array([[s2p[x[0]], x[1], x[2]* c_scan + x[3]* c_get]  for x in val])
        l_style = next(linestyles)
        for j in range(1, 3):
            ax[j-1].plot(val[:,0], val[:,j], label=key, color = colors[i], linestyle = l_style, linewidth = 2)        
            ax[j-1].plot(val[:,0], val[:,j],".", markersize = 20, color = colors[i],)        
    
    for i, name in enumerate(["Miss rate", r"Averaged time cost, $C$"]):
        # figs[i][0].suptitle(name)
        # ax[i].set_xscale('log')
        ax[i].set_ylabel(name)
        ax[i].set_xlabel(r"Buffer size, % database size")
        ax[i].grid(True)
        # ax[i].ticklabel_format(axis='x', scilimits=[-4, 4])

    h,l = ax[0].get_legend_handles_labels()

    fig.legend(h[:],l[:],ncol=4, bbox_to_anchor=(0., -.05, 1, 0.10),
                loc='outside upper left', 
                mode="expand", borderaxespad=0)

    fig.tight_layout()
    # 
    return {"pair": fig}

def plot_bar(exp):
    c_scan, c_get = exp.config.cost_params.c_scan, exp.config.cost_params.c_get
    percents = sorted(list(map(int, exp.config.shared_parameters.cache_sizes.split(","))))
    sizes = sorted([i[0] for i in next(iter(exp.rez.values()))])
    s2p = {s: p for s, p in zip(sizes, percents)}
    dct = exp.rez

    values = []
    for i, (key, val) in enumerate(dct.items()):
        val = np.array([[key, s2p[x[0]], x[1], x[2]* c_scan + x[3]* c_get, x[2],x[3]]  for x in val])
        values.append(val)
    v = np.concatenate(values, axis = 0)
    rez = pd.DataFrame(v, columns=["Algorithm","size", "Miss rate", r"Averaged time cost, $C$", "Scan misses","Get misses"])
    
    rez = rez.astype({"Algorithm": str,"size": int, "Miss rate": float, r"Averaged time cost, $C$":float, "Scan misses":float,"Get misses":float})
    # print('lol')
    # rez["Miss rate"] = 1. - rez["Miss rate"]
# get figure and plot    
    sns.set_context("paper", font_scale=1.5, rc={"lines.linewidth": 2.5, 'axes.grid' : True})
    # fig, ax = plt.subplots(1, 2, figsize = (17, 8), sharex=True)
    fig, ax, colors = get_fig_set_style(len(dct), (1, 2), figsize = (17, 8))
    sns.barplot(rez, x="size", y="Miss rate", hue="Algorithm", ax=ax[0], width= 0.6, dodge=True, gap=0.1)
    sns.barplot(rez, x="size", y=r"Averaged time cost, $C$", hue="Algorithm", ax=ax[1], width= 0.6, dodge=True, gap=0.1)

    ax[0].get_legend().remove()
    ax[1].get_legend().remove()
    for i in range(2):
        ax[i].set_xlabel("Buffer size, % database size")
        ax[i].set_ylim([0., 1.])
        ax[i].grid(True)
    ax[1].set_ylabel("Time cost")
    ax[0].set_ylabel("Miss rate")

    h,l = ax[0].get_legend_handles_labels()

    fig.legend(h[:],l[:],ncol=4, bbox_to_anchor=(0., -.05, 1, 0.10),
                loc='outside upper left', mode="expand", borderaxespad=0.)

    fig.tight_layout()

# plot one bar
    def plot_one_bar(y="Miss rate"):
        fig, ax, colors = get_fig_set_style(len(dct), (1, 1), figsize = (8, 8))
        ax = [ax]
        sns.barplot(rez, x="size", y=y, hue="Algorithm", ax=ax[0], width= 0.6, dodge=True, gap=0.1)

        ax[0].get_legend().remove()
        for i in range(1):
            ax[i].set_xlabel("Buffer size, % database size")
            ax[i].set_ylim([0., 1.])
            ax[i].grid(True)
        ax[0].set_ylabel(y)

        h,l = ax[0].get_legend_handles_labels()

        fig.legend(h[:],l[:],ncol=3, bbox_to_anchor=(0., -.05, 1, 0.10),
                    loc='outside upper left', mode="expand", borderaxespad=0.)
        fig.tight_layout()
        return fig
    
    rez = {"Barplot": fig, 
           "Barplot_mr": plot_one_bar("Miss rate"), 
           "Barplot_at": plot_one_bar(r"Averaged time cost, $C$")}


    return rez

def plot_time(exp):
    fig, ax = plt.subplots()
    colors = ['r', 'g', 'b', 'y']
    for i, (key, val) in enumerate(exp.times.items()):
        tp = np.array(val).T
        ax.plot(tp[0], tp[1], label = key, color = colors[i])
    plt.legend()
    return {"runtime": fig}
    
import os
def save_figures(dct: dict, path ):
    for name, fig in dct.items():
        # fig.savefig(str(path / f"{name}_image.png"))
        p = path / f"{name}_image.pdf"
        if p.exists():
            os.remove(p)
        fig.savefig(str(p),  bbox_inches='tight')

        # data = np.array(fig.canvas.buffer_rgba())
        # weights = [0.2989, 0.5870, 0.1140]
        # data = np.dot(data[..., :-1], weights)
        # plt.imsave(str(path / f"{name}_image_gray.png"), data, cmap="gray")
        # plt.imsave(str(path / f"{name}_image_gray.pdf"), data, cmap="gray")
        plt.close(fig)

