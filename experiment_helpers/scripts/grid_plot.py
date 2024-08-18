import itertools

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import seaborn as sns

from collections import defaultdict

from eeva.utils import drawer

def prepare_cscan(config, dcts):
    """
    this function is preparing dataframe 
    to plot ablation study of c_scan
    
    dcts: list of dictionaries with different runs of experiment
    """
    c_get = 1.
    
    # we variate c_scan. it is smth as exmeriment_name
    c_scans = dcts[0].keys()
    
    # data: experiment_name: alg_name: runs
    data = defaultdict(lambda: defaultdict(list))
    for elem in dcts:
        for exp_name, exp_rez in elem.items():
            # exp_rez is a dictionary alg:rez
            c_scan = float(exp_name)
            for alg_name, alg_rez in exp_rez.items():
                x = np.array(alg_rez)

                x = np.stack([x[:, 1], x[:, 2] * c_scan + x[:, 3] * c_get, x[:, 2], x[:, 3]], axis=1)
                data[alg_name][exp_name].append(x)
    return data            
    
def prepare_pscan(config, dcts):
    """
    this function is preparing dataframe 
    to plot ablation study of c_scan
    
    dcts: list of dictionaries with different runs of experiment
    """
    c_scan, c_get = config.cost_params.c_scan, config.cost_params.c_get
    
    # we variate c_scan. it is smth as exmeriment_name
    
    # data: experiment_name: alg_name: runs
    data = defaultdict(lambda: defaultdict(list))
    for elem in dcts:
        for exp_name, exp_rez in elem.items():
            # exp_rez is a dictionary alg:rez
            # c_scan = float(exp_name)
            for alg_name, alg_rez in exp_rez.items():
                x = np.array(alg_rez)
                
                x = np.stack([x[:, 1], x[:, 2] * c_scan + x[:, 3] * c_get, x[:, 2], x[:, 3]], axis=1)
                data[alg_name][exp_name].append(x)
    return data   
   
   
def plot_ddict(data, xlabel, relative_name = None):
    # data: alg_name: exp_type: data_arr
    # data_arr: ( "Miss rate", "Averaged time cost", "Scan misses", "Get misses")
    # alg_name is a numerical parameter, that will be plotted as x axis
    
    fig, ax, colors = drawer.get_fig_set_style(len(data), (1, 2), figsize=(19, 9))
    linestyles = ["dotted", "dashed", "solid"]
    for i in range(2):
        for k, (alg_name, alg_rez) in enumerate(data.items()):
            x = []
            y = []
            std = []
            for key, val in alg_rez.items():
                x.append(float(key))
                val = np.array(val, dtype = float).squeeze()
                tmp_y = val[:, i]
                if relative_name is not None:
                    rel_y = data[relative_name][key]
                    rel_y = np.array(rel_y, dtype = float).squeeze()
                    print()
                    rel_y = np.mean(rel_y[:, i])
                    tmp_y = (tmp_y - rel_y)/ rel_y * 100
                
                try:
                    y.append(np.nanmean(tmp_y))
                    std.append(np.nanstd(tmp_y))
                except Exception:
                    print(tmp_y, type(tmp_y))
                    raise ValueError
            x,y,std = np.array(x),np.array(y),np.array(std)
            ls = "solid"
            if alg_name.lower().startswith("eeva"):
                ls = linestyles[k%3]
            ax[i].plot(x, y, label = alg_name, color = colors[k], linestyle = ls, linewidth = 3)
            ax[i].fill_between(
                x,
                y - std,
                y + std,
                color=colors[k],
                alpha=0.15,
                interpolate=True,
            )
        
    for i in range(2):
        ax[i].ticklabel_format(axis="x", scilimits=[-3, 3])
        ax[i].set_xlabel(xlabel)
        ax[i].grid(True)
    if relative_name is None:
        ax[1].set_ylabel(r"Averaged time cost, $C$")
        ax[0].set_ylabel("Miss Rate")
    else:
        ax[1].set_ylabel(r"Relative time cost, $\%$")
        ax[0].set_ylabel(r"Relative Miss Rate, $\%$")
        
    h, legend_ = ax[0].get_legend_handles_labels()

    legend = fig.legend(
        h[:],
        legend_[:],
        ncol=4,
        bbox_to_anchor=(0.0, -0.1, 1, 0.10),
        loc="outside upper left",
        mode="expand",
        borderaxespad=0.0,
    )
    for line in legend.get_lines():
        line.set_linewidth(4)
    plt.tight_layout()
    return fig
            
        
# def plot_dict(config, rez):
#     c_scan, c_get = config.cost_params.c_scan, config.cost_params.c_get
#     dct = rez
    
#     values = []
#     disps = []
#     probs = list(dct.keys()) #[x * 0.00018 for x in range(18)]
#     for i, (p_scan, (p_scan, fixed_scan_rez)) in enumerate(zip(probs, dct.items())):
#         for key, x in fixed_scan_rez.items():
#             x = np.stack([x[:, 1], x[:, 2] * c_scan + x[:, 3] * c_get, x[:, 2], x[:, 3]], axis=1)


#             x_mean = np.nanmean(x,axis=0)
#             x_std = np.nanstd(x, axis=0)
#             val = np.array([[key, p_scan, *x_mean]])
#             values.append(val)
#             disp = np.array([[key, p_scan, *x_std]])
#             disps.append(disp)
#     v = np.concatenate(values, axis=0)
#     d = np.concatenate(disps, axis=0)
#     rez = pd.DataFrame(
#         v, columns=["Algorithm", "p_scan", "Miss rate", "Averaged time cost", "Scan misses", "Get misses"]
#     )
#     disp = pd.DataFrame(
#         d, columns=["Algorithm", "p_scan", "Miss rate", "Averaged time cost", "Scan misses", "Get misses"]
#     )
#     rez = rez.astype(
#         {
#             "Algorithm": str,
#             "p_scan": float,
#             "Miss rate": float,
#             "Averaged time cost": float,
#             "Scan misses": float,
#             "Get misses": float,
#         }
#     )
#     disp = disp.astype(
#         {
#             "Algorithm": str,
#             "p_scan": float,
#             "Miss rate": float,
#             "Averaged time cost": float,
#             "Scan misses": float,
#             "Get misses": float,
#         }
#     )

    
#     return rez, None

#     sns.set_context("paper", font_scale=1.5, rc={"lines.linewidth": 2.5, "axes.grid": True})
#     fig, ax, colors = get_fig_set_style(len(dct), (1, 2), figsize=(19, 9))

#     for i, alg_name in enumerate(rez["Algorithm"].unique()):
#         r_tmp = rez[rez["Algorithm"] == alg_name]
#         d_tmp = disp[disp["Algorithm"] == alg_name]
#         l_style = next(linestyles)
#         for k, col_n in enumerate(["Miss rate", "Averaged time cost"]):

#             m = r_tmp[col_n].values
            
#             d = d_tmp[col_n] * 0.5
#             ax[k].plot(r_tmp["p_scan"], m, label=alg_name, color=colors[i], linestyle=l_style, linewidth=2)
#             ax[k].fill_between(
#                 r_tmp["p_scan"],
#                 m - d,
#                 m + d,
#                 color=colors[i],
#                 alpha=0.15,
#                 interpolate=True,
#             )
#     for i in range(2):
#         ax[i].ticklabel_format(axis="x", scilimits=[-3, 3])
#         ax[i].set_xlabel(r"$p_{scan}$")
#         ax[i].grid(True)
#     ax[1].set_ylabel(r"Averaged time cost, $C$")
#     ax[0].set_ylabel("Miss rate")

#     h, legend_ = ax[0].get_legend_handles_labels()

#     fig.legend(
#         h[:],
#         legend_[:],
#         ncol=4,
#         bbox_to_anchor=(0.0, -0.05, 1, 0.10),
#         loc="outside upper left",
#         mode="expand",
#         borderaxespad=0.0,
#     )

#     fig.tight_layout()
#     return rez, fig
