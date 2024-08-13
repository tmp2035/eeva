import itertools

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import seaborn as sns

DPI = 200
LINESTYLES = [
    ("d", "dashdot"),
    ("d", "dotted"),
    ("d", "solid"),
    ("d", "dashed"),
    ("long dash with offset", (1, (1, 0))),
    ("densely dashdotdotted", (0, (3, 1, 1, 1, 1, 1))),
    ("densely dashed", (0, (5, 1))),
    ("densely dashed", (0, (1, 5))),
]


def get_fig_set_style(lines_count, shape=(1, 1), figsize=None):
    colors_list = ["blue", "m", "red", "#0b5509", "y", "black", "m", "black", "y", "c", "g"]
    params = {
        "legend.fontsize": 40,
        "lines.markersize": 10,
        "axes.labelsize": 40,
        "axes.titlesize": 40,
        "xtick.labelsize": 30,
        "ytick.labelsize": 30,
        "font.size": 35,
        #  "text.usetex": True
    }
    sns.set_context("paper", rc=params)
    # sns.set_context("paper", font_scale=2.5, rc={"lines.linewidth": 2.5})
    if figsize is None:
        fig, ax = plt.subplots(*shape, dpi=DPI)
    else:
        fig, ax = plt.subplots(*shape, dpi=DPI, figsize=figsize)
    plt.grid(which="both")
    return fig, ax, colors_list


linestyles = itertools.cycle([e[1] for e in LINESTYLES])


def plot_dict(config, rez):
    c_scan, c_get = config.cost_params.c_scan, config.cost_params.c_get
    dct = rez
    
    values = []
    disps = []
    c_scans = [(0.9 - 0.01)/9 * i + 0.01 for i in range(10)]
    for i, (c_scan, (p_scan, fixed_scan_rez)) in enumerate(zip(c_scans, dct.items())):
        for key, x in fixed_scan_rez.items():
            x = np.stack([x[:, 1], x[:, 2] * c_scan + x[:, 3] * c_get, x[:, 2], x[:, 3]], axis=1)
            x_mean = x.mean(axis=0)
            x_std = x.std(axis=0)
            val = np.array([[key, p_scan, *x_mean]])
            values.append(val)
            disp = np.array([[key, p_scan, *x_std]])
            disps.append(disp)
    v = np.concatenate(values, axis=0)
    d = np.concatenate(disps, axis=0)
    rez = pd.DataFrame(
        v, columns=["Algorithm", "p_scan", "Miss rate", "Averaged time cost", "Scan misses", "Get misses"]
    )
    disp = pd.DataFrame(
        d, columns=["Algorithm", "p_scan", "Miss rate", "Averaged time cost", "Scan misses", "Get misses"]
    )
    # rez.p_scan = [f"{float(x)}" for x in rez.p_scan]
    rez = rez.astype(
        {
            "Algorithm": str,
            "p_scan": float,
            "Miss rate": float,
            "Averaged time cost": float,
            "Scan misses": float,
            "Get misses": float,
        }
    )
    disp = disp.astype(
        {
            "Algorithm": str,
            "p_scan": float,
            "Miss rate": float,
            "Averaged time cost": float,
            "Scan misses": float,
            "Get misses": float,
        }
    )

    sns.set_context("paper", font_scale=1.5, rc={"lines.linewidth": 2.5, "axes.grid": True})
    fig, ax, colors = get_fig_set_style(len(dct), (1, 2), figsize=(19, 9))

    m_compare = rez[rez["Algorithm"] == "EEvA-Seq"]
    for i, alg_name in enumerate(rez["Algorithm"].unique()):
        r_tmp = rez[rez["Algorithm"] == alg_name]
        d_tmp = disp[disp["Algorithm"] == alg_name]
        l_style = next(linestyles)
        for k, col_n in enumerate(["Miss rate", "Averaged time cost"]):

            """
                from scipy.interpolate import spline

            # 300 represents number of points to make between T.min and T.max
            xnew = np.linspace(T.min(), T.max(), 300)

            power_smooth = spline(T, power, xnew)

            plt.plot(xnew,power_smooth)
            plt.show()

            """
            # print(r_tmp[col_n], m_compare[col_n],"\n", (r_tmp[col_n] - m_compare[col_n]))
            if col_n == "Miss rate":
                m = r_tmp[col_n].values
            else:
                m = (r_tmp[col_n].values - m_compare[col_n].values)/m_compare[col_n].values
            d = d_tmp[col_n] * 0.5
            ax[k].plot(r_tmp["p_scan"], m, label=alg_name, color=colors[i], linestyle=l_style, linewidth=2)
            ax[k].fill_between(
                r_tmp["p_scan"],
                m - d,
                m + d,
                color=colors[i],
                alpha=0.15,
                interpolate=True,
            )
    for i in range(2):
        ax[i].ticklabel_format(axis="x", scilimits=[-3, 3])
        ax[i].set_xlabel(r"$c_{scan}$")
        ax[i].grid(True)
    ax[1].set_ylabel(r"Relative time cost, $C$")
    ax[0].set_ylabel("Miss rate")

    h, legend_ = ax[0].get_legend_handles_labels()

    fig.legend(
        h[:],
        legend_[:],
        ncol=4,
        bbox_to_anchor=(0.0, -0.05, 1, 0.10),
        loc="outside upper left",
        mode="expand",
        borderaxespad=0.0,
    )

    fig.tight_layout()
    return rez, fig
