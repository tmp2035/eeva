# Cache

This repository contains the code for the paper "EEvA: Fast expert-based page eviction algorithm for database buffer management".

![Demo](./assets/compare_image.png)

## Installation Guideline

There are two installation options:

### Full Installation

To build and install the package with full functionality, follow these steps:

1. Copy the `Dockerfile` from our repository.
2. Build the Docker image using the following command:
   ```shell
   docker build -t 1a1a11a/libcachesim -f dockerfile .
   ```
3. Run the Docker container:
   ```shell
   docker run -it --name=libcache 1a1a11a/libcachesim:latest bash
   ```

   Note: We have made modifications to `libCacheSim/bin/cachesim/sim.c`. For installation, we copy it from our repository and follow the installation guidelines from the original authors.

### Partial Installation

If you prefer not to use Docker or only need the Python functionality, follow these steps:

1. Ensure you have Python 3.11 installed.
2. Setup the project using Poetry:
   ```shell
   poetry build
   ```
   or using setup.py:
   ```shell
   pip install -e . --force-reinstall
   ```

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

## Data Generation Procedure:

To generate requests we do the following:

1. We generate a set of tables $\mathcal{T}$ such that every table contains $P_i$ pages, where $i=1,\ldots,|\mathcal{T}|$. In the experiments, we use $|\mathcal{T}| = 50$ and $P_i \sim \mathcal{U}([P_{\max} / 2, P_{\max}])$, where $P_{\max}$ is the maximum number of pages per table, and we consider a setup where $P_{\max} = 1000$.

Since we test both \texttt{get}-type and \texttt{scan}-type queries, we introduce the probability of the \texttt{scan}-type query $p_{scan} = 0.002$, i.e., a \texttt{scan}-type query is quite a rare event.

We consider a trace of queries $Q = \{ q_1, \ldots, q_N\}$, where every query $q_i$ is a set of the queried pages by scan or get operation. Denote by $SQ_i$ and $GQ_i$ the sets of pages from query $q_i$ processed by scan and get operations, respectively, i.e. $q_i = SQ_i \sqcup GQ_i$.
```

This subsection provides a description of how data is generated for the experiments, using the parameters specified in the configuration file.

## Usage Guideline

To run experiments select the

1. ...
2. ...

## Code Structure

The project is structured as follows:

```
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

./experiment_helpers/
├── fig_image.pdf
├── run_config.py
├── run_grid_experiment.py
├── script_user.ipynb
└── scripts/
```

- `./cache/`: Contains the main project code.
- `./experiment_helpers/`: Contains scripts and utilities for running experiments.

## Project Overview

This project implements caching algorithms described in the paper. It provides implementations of various cache eviction strategies and utilities for running experiments to compare their performance.