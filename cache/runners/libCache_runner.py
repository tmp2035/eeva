from joblib import delayed, Parallel
from typing import Dict, List, Tuple
from collections import defaultdict
import subprocess
import os
import tempfile
import logging
from itertools import product
import fire

logger = logging.getLogger("libCache_runner")
                
def run_cachesim_size(
    CACHESIM_PATH: str,
    tracepath: str,
    algos: str,
    cache_sizes: str,
    ignore_obj_size: bool = True,
    byte_miss_ratio: bool = False,  # not used
    trace_format: str = "oracleGeneral",
    trace_format_params: str = ""
) -> Dict[str, Tuple[int, float, List[int]]]:
    mrc_dict = defaultdict(list)
    processes = []
    for algo, size in product(algos.split(","), cache_sizes.split(","), repeat=1):
        run_args = [
            CACHESIM_PATH,
            tracepath,
            trace_format,
            algo,
            size,
            "--ignore-obj-size",
            "1"
            # "1" if ignore_obj_size else "0",
        ]
        if len(trace_format_params) > 0:
            run_args.append("--trace-type-params")
            run_args.append(trace_format_params)
        
        f = tempfile.TemporaryFile("w+")
        p = subprocess.Popen(run_args, stdout= f)

        logger.debug('running "{}"'.format(algo))
        processes.append((algo, size, p, f))

    for algo, size, p, f in processes:
        # print(type(p), type(f))
        p.wait()
        f.seek(0)        

        stdout_str = f.read() #p.stdout.decode("utf-8")
        f.close()
        logger.info('out :"{}"'.format(stdout_str))

        tmp_rez = [None, None]
        # hits_misses, cache_size, miss_ratio = 0,0,0
        for line in stdout_str.split("\n"):
            # print(line[:20], line.startswith("hits"), line.startswith("result"))
            logger.info("cachesim log: " + line)
            if "[INFO]" in line[:16]:
                continue
            if line.startswith("hits"):
                tmp_rez[1] = list(map(int, line.split()[1:]))            
            if line.startswith("result"):
                ls = line.split()
                tmp_rez[0] = float(ls[10].strip(","))
        mrc_dict[algo].append([int(size), *tmp_rez])
    return mrc_dict

if __name__ == '__main__':
    fire.Fire(run_cachesim_size)
