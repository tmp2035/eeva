from pathlib import Path
import os
import fire
from hydra import compose, initialize
from tqdm import tqdm
import os


from eeva import Experiment


def runner(cfg, conf_name, dynamic, repetitions):
    exp = Experiment.from_config(cfg, dynamic_generator=dynamic)
    if repetitions == 1:
        exp.generate_trace()
        exp.run()
        exp.save(conf_name, rewrite=True)
    else:
        """
        in the repetition experiment, we are only interested 
        in logs that are accumulated in the res of the 
        algorithm and stored in `runs_history.pickle'.
          Therefore, saving occurs only once
        """
        for i in range(repetitions):
            exp.generate_trace()
            exp.run()
        exp.save(f"{conf_name}/{repetitions-1}", rewrite=True)
        
    
def dummy_runner(cfg, conf_name):
    """
    the same, but after generating the trace we change 
    all 'scan' queries to 'get' queries. 
    """
    exp = Experiment.from_config(cfg, dynamic_generator=False)
    req = exp.generator.generate_requests()
    for i, elem in enumerate(req):
        req[i] = (elem[0], ("get", *elem[1][1:]))
    tracepath = exp.datapath / (exp.generator.name() + ".csv")
    exp.generator.save_requests(req, tracepath)
    exp.tracepath = tracepath
    exp.cache_sizes = exp.get_sizes()
    
    
    exp.run()
    exp.save(conf_name, rewrite=True)



def main(config_path: str =".", config_names: str|None =None,  dynamic:bool = False, dummy: bool = False, repetitions = 1):
    assert repetitions >= 1 and isinstance(repetitions, int), "repetitions should be integer"
    p = Path(os.path.dirname(os.path.realpath(__file__)), os.path.dirname(os.path.realpath(__file__)), config_path)
    if config_names is None:
        if not p.exists():
            raise ValueError(f"{p} is not exist. CWD: {os.path.dirname(os.path.realpath(__file__))}")
        config_names = [
            str(child).split("/")[-1].split(".")[0] for child in p.iterdir() if str(child).endswith(".yaml")
        ]
    else:
        if isinstance(config_names, str):
            config_names = [config_names]
        # print(config_names)
        # config_names = config_names.split(",")
    print(config_names)
    print(config_path)
    configs = []
    for name in config_names:
        with initialize(version_base="1.3", config_path=config_path):
            cfg = compose(config_name=name, overrides=[])
            
        configs.append(cfg)

    for cfg, conf_name in tqdm(zip(configs, config_names)):
        if dummy:
            dummy_runner(cfg, conf_name)
        else:
            runner(cfg, conf_name, dynamic, repetitions)

if __name__ == "__main__":
    fire.Fire(main)
