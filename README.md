# Cache

This repository contains the code for the paper "EEvA: Fast expert-based page eviction algorithm for database buffer management".

![Demo](./assets/compare_image.png)

## Table of Contents
1. [Installation Guideline](#installation-guideline)
   - [Full Installation](#full-installation)
   - [Partial Installation](#partial-installation)
2. [Usage Guideline](#usage-guideline)
   - [With Docker](#with-docker)
   - [Without Docker](#without-docker)
3. [Configuration File](#configuration-file)
   - [Description of Parameters](#description-of-parameters)
4. [Data Generation Procedure and Trace Structure](#data-generation-procedure-and-trace-structure)
   - [Generation](#generation)
   - [Trace Structure](#trace-structure)
5. [Code Structure](#code-structure)

## Installation Guideline

There are two installation options:

### Full Installation

To build and install the package with full functionality, follow these steps:

1. Copy the `Dockerfile` from our repository.
2. Build the Docker image using the following command:
   ```bash
   docker build -t cache_server -f Dockerfile .
   ```
3. Run the Docker container:
   ```bash
   docker run -it --name=libcache 1a1a11a/libcachesim:latest bash
   ```

   Note: We have made modifications to `libCacheSim/bin/cachesim/sim.c`. For installation, we copy it from our repository and follow the installation guidelines from the original authors.

### Partial Installation

If you prefer not to use Docker or only need the Python functionality, follow these steps:

1. Ensure you have Python 3.11 installed.
2. Setup the project using Poetry:

   ```bash
   poetry build
   ```

   or using setup.py:

   ```bash
   pip install -e . --force-reinstall
   ```

## Usage Guideline

since there are two abilities to install there are two guidlines how compute experiment:

### With docker

There we make directory `runs` to save results outside docker. Connect to the docker via concole:

```bash
mkdir runs runs/data runs/run_results && \
      docker run -v ./runs:/runs -it --name=cache_sim cache_server:latest bash
```

And inside it choose and run experiment for some configs:

```bash
cd cache
python3 experiment_helpers/run_config.py path_to_configs_folder [config_name]
```

For example:

```bash
cd cache
python3 experiment_helpers/run_config.py ../experiment_configs/exp_configs scan_eq_get
```

if second argument is not provided programm will run for all `yaml` files in provided directory.

### Without docker

Make folders to save experiments and run experiment:

```bash
mkdir runs runs/data runs/run_results
python3 experiment_helpers/run_config.py path_to_configs_folder [config_name]
```

More things that you can run in `/experiment_helpers/script_user.ipynb`

## Configuration File

The project uses a configuration file in YAML format to specify experiment parameters. Here is an example of the configuration file:

```yaml
paths:
  lib_cache_sim: /path/to/libCacheSim/_build/bin/cachesim
  datapath: ./data/
  save_path: ./run_results/
generation_params:
  num_requests: 1_000_000
  num_tables: 50
  max_pages: 1000
  q: 0.1
  p_scan: 0.0015
  gamma: 0.0
cost_params:
  c_scan: 0.8
  c_get: 1.0
shared_parameters:
  cache_sizes: 1,5,10,20,50
libCache_params:
  algos: lru,cacheus,belady,qdlp,tinylfu
  trace_format: csv
  trace_format_params: obj-id-col=1, delimiter=;, has-header=true
proposed_params:
  algos: EEvAGreedy,EEvAT,EEvASeq
  beta: 0.8
  alpha: 1.0
  move_cost: 0.0
  return_trace_hit: true
```

This configuration file allows customization of various parameters such as cache sizes, algorithm choices, and experiment settings.

Here's a description of each parameter in the configuration file:

1. **paths**:
   - `lib_cache_sim`: Path to the libCacheSim executable.
   - `datapath`: Path to the directory containing data.
   - `save_path`: Path to save the results of the experiment.

2. **generation_params**:
   - `num_requests`: Total number of requests to generate.
   - `num_tables`: Number of tables.
   - `max_pages`: Maximum number of pages per one table.
   - `q`: Parameter q for Zipf distribution for query generation.
   - `p_scan`: Probability of selection scan type query.
   - `gamma`: Partition of dirty pages in scanned table.

3. **cost_params**:
   - `c_scan`: Cost of scan type quert.
   - `c_get`: Cost of get type quert.

4. **shared_parameters**:
   - `cache_sizes`: List of cache sizes to test.It is a percent of database size.

5. **libCache_params**:
   - `algos`: List of caching algorithms to use from libCache.
   - `trace_format`: Format of the trace.
   - `trace_format_params`: Additional parameters for the trace format.

6. **proposed_params**:
   - `algos`: List of caching algorithms to use with the proposed implementation of EEvA algorithms.
   - `beta`: Beta parameter of algorithm.
   - `alpha`: Alpha parameter of algorithm.
   - `move_cost`: Cost of moving.
   - `return_trace_hit`: Whether to return trace hits.

## Data Generation Procedure and trace structure

### Generation

Generation occures in `cache/utils/req_generator.py`

To generate requests we do the following:

   1. Database generation. We generate a set of tables $\mathcal{T}$ such that every table contains $P_i$ pages, where $i=1,\ldots,$`num_tables`. For every table we generate number of pages $P_i\sim \mathcal{U}([P_{\max} / 2, P_{\max}])$, where $P_{\max}$=`max_pages`. Every table provided with probability to be scanned and probability to be getted.
   2. To generate queries we iteratively for `num_requests` do the following:
      - choose query type. P[scan] = `p_scan`, P[get] = 1 - `p_scan`
      - choose table with its probability to be selected with this type of query
      - if *scan* we scan all pages, if *get* we choose page according to Zipf distribution with parameter `q` on pages of this table.

### Trace structure

Generated trace is a sequence of entries:

```csv
   pg_id;req_info
   3349;('get', 33, 49, 72, 1)
   4584;('get', 45, 84, 93, 1)
   3473;('get', 34, 73, 82, 1)
   100;('scan_all', 1, 0, 58, 1)
   101;('scan_all', 1, 1, 58, 1)
   102;('scan_all', 1, 2, 58, 1)
   103;('scan_all', 1, 3, 58, 1)
```

where `req_info = (query type, table number, page index, table size, is_durty bit)` tuple.

Last entry is for future work. For current realization it is important, that scan occures sequentally.

## Code Structure

The project is structured as follows:

    ./cache/
    ├── __init__.py
    ├── algorithm
    │   ├── __init__.py
    │   ├── abstractCache.py
    │   ├── eeva.py
    │   ├── eeva_seq.py
    │   ├── eeva_t.py
    │   ├── proposed.py
    │   └── requestItem.py
    ├── config
    │   ├── __init__.py
    │   └── config.py
    ├── runners
    │   ├── __init__.py
    │   ├── experiment_runner.py
    │   ├── libCache_runner.py
    │   └── proposed_runner.py
    └── utils
        ├── __init__.py
        ├── costs_calc.py
        ├── drawer.py
        ├── req_generator.py
        ├── time_checker.py
        └── trace_utils.py

And there are functions to run experiments:

    ./experiment_helpers/
    ├── fig_image.pdf
    ├── run_config.py
    ├── run_grid_experiment.py
    ├── script_user.ipynb
    └── scripts/

- `./cache/`: Contains the main project code.
- `./experiment_helpers/`: Contains scripts and utilities for running experiments.
