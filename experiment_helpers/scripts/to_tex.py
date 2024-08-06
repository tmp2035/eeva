import shutil
from pathlib import Path
from string import Template
import os
TEMPLATE = """
\begin{figure*}[!ht]
    \centering
    \begin{subfigure}{$w1\linewidth}
        \includegraphics[width=\textwidth]{figures/experiments/$p1}
    \end{subfigure}
    \begin{subfigure}{$w2\linewidth}
        \includegraphics[width=\textwidth]{figures/experiments/$p2}
    \end{subfigure}

    \caption{$caption}
    \label{fig::$label}
\end{figure*}
"""

def copy_reg_expression(experiment_paths, to_save_path, parts = list[str]):
    assert to_save_path.exists(), "Provided path to save is not exist"
    assert all(p.exists() for p in experiment_paths), "Provided experiment paths is is not exist"

    for part in parts:
        os.mkdir(to_save_path/part)
        filenames = []
        for pp in experiment_paths:
            for p in pp.rglob(f"*{part}*"):
                filenames.append(p)
        for n in filenames:
            name =   f"{n.parts[-2]}_{n.parts[-1]}"
            shutil.copyfile(n, to_save_path/part/name)

def prepare_for_tex(experiment_paths=None, to_save_path=Path("../run_plots/")):
    if experiment_paths is None:
        path = Path("../run_results")
        experiment_paths = [p for p in path.rglob("") if p.parts[-1].startswith("scan")]

    assert to_save_path.exists(), "Provided path to save is not exist"
    assert all(p.exists() for p in experiment_paths), "Provided experiment paths is is not exist"

    pair_paths = []
    cost_paths = []
    template_values = []
    for pp in experiment_paths:
        for p in pp.rglob("*pair*"):
            pair_paths.append(p)
        for p in pp.rglob("*cost_density*"):
            cost_paths.append(p)
    assert len(pair_paths) == len(cost_paths)
    for pair, cost in zip(pair_paths, cost_paths):
        assert pair.parts[-2] == cost.parts[-2], f"{pair.parts[-2]} != {cost.parts[-2]}"
        pair_name = f"{pair.parts[-2]}_{pair.parts[-1]}"
        cost_name = f"{cost.parts[-2]}_{cost.parts[-1]}"
        print(pair)
        shutil.copyfile(pair, to_save_path / pair_name)
        shutil.copyfile(cost, to_save_path / cost_name)

        caption = 'Figure for "{}"  generated data'.format(pair.parts[-2].translate({ord("_"): ord(" ")}))
        tv = {
            "p1": str(cost_name),
            "p2": str(pair_name),
            "w1": 0.3,
            "w2": 0.6,
            "caption": caption,
            "label": pair.parts[-2],
        }
        template_values.append(tv)

    txts = []

    src = Template(TEMPLATE)
    for elem in template_values:
        result = src.substitute(elem)
        txts.append(result)

    print("\n\n".join(txts))
