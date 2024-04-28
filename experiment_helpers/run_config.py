from pathlib import Path

import fire
from hydra import compose, initialize
from tqdm import tqdm

from eeva import Experiment


def runner(cfg, conf_name):
    exp = Experiment.from_config(cfg)
    exp.generate_trace()
    exp.run()
    exp.save(conf_name, rewrite=True)


def main(config_path=".", config_names=None):

    p = Path(config_path)
    if config_names is None:
        config_names = [
            str(child).split("/")[-1].split(".")[0] for child in p.iterdir() if str(child).endswith(".yaml")
        ]
    else:
        config_names = config_names.split(",")
    print(config_names)
    print(config_path)
    configs = []
    for name in config_names:
        with initialize(version_base="1.3", config_path=config_path):
            cfg = compose(config_name=name, overrides=[])
        configs.append(cfg)

    for cfg, conf_name in tqdm(zip(configs, config_names)):
        runner(cfg, conf_name)


if __name__ == "__main__":
    fire.Fire(main)
