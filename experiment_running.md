Before running experiments you have to follow the installation guidline in README.md file. 

Please note that you must create a directory to save the results of the experiments.

Next are the instructions for starting and drawing each experiment. All launches have the form

```bash
python3 experiment_helpers/[experiment_runner_name].py path_to_configs_folder [config_name]
```

If there is no config name, then the experiment will start for all configs in this directory.

To see how the algorithms work with other parameters, just change the parameters in the specified config.

For most experiments, a drawing script has been made and is presented in ![experiment_helpers/script_user.ipynb], look there to get graphs 


## different dencity experiments
These are guidlines for running experiments with various p_scan scenarios. This experiments have config files with names `zero_scan, scan_lower_get,scan_eq_get,scan_greater_get`which corresponds to a scenario without scans, with Low $p_{scan}$, medium $p_{scan}$ and high $p_{scan}$, respectively

configuration files are located at ![./experiments_configs/different_dencity] with the appropriate filenames.

to start experiment run:

```
cd /eeva
python3 experiment_helpers/run_config.py ../experiment_configs/different_dencity --dynamic=False
```

this will run experiment for all configuration files in this folder.

The graphs presented in the article can be found in the experiment folder under the names 'cost_dencity_image' and 'pair_image'. The rest of the images may not be displayed well due to font sizes being adjusted only for these two images.

## Worst case scenario

An experiment with repeated reading of table. Such a statement is often cited as a setup that breaks LRU-type algorithms.

```
cd /eeva
python3 experiment_helpers/run_config.py ../experiment_configs/dummy_conf --dynamic=False --dummy=True
```


## ablation study

There three experiments with ablation study: variation of the $c_{scan}$ parameter, variation of $p_{scan}$ and variation of the proportion of predominantly scanned tables. Each has its own script to run:

$p_{scan}$:

```
python3 experiment_helpers/run_grid_pscan.py ../experiment_configs/exp_conf_grid grid_bigg
```

$c_{scan}$:

```
python3 experiment_helpers/run_grid_cscan.py ../experiment_configs/exp_conf_grid grid_bigg_cscan
```

varying the proportion of scanned tables:

```
python3 experiment_helpers/run_grid_scan_tables.py ../experiment_configs/exp_conf_grid grid_bigg_tables
```


then draw them within ![experiment_helpers/script_user.ipynb] section  "plot ablation study"


## experiment 'Dynamics of miss rate for regular scenarios'

in this experiment we consider we look at cumulative miss rate of algorithms on different scenarios

```
python3 experiment_helpers/run_config.py ../experiment_configs/running --repetitions=5
```

There `repetitions` parameter set specifies the number of times experiments will be run to take the average of their results. For a given scenario, the database is generated once, after which traces are generated from this database.

To draw experiment run cells from section `Dynamics of miss rate for regular scenarios` in ![experiment_helpers/script_user.ipynb]

## experiment 'Changing data access pattern'

In this experiment, we looked at what would happen to hit rates if the distribution of query densities across tables suddenly changed.

```
python3 experiment_helpers/run_config.py ../experiment_configs/dynamic running_hit --dynamic=True
```

To draw experiment run cells from section `Changing data access pattern` in ![experiment_helpers/script_user.ipynb]