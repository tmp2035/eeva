import fire
from hydra import compose,  initialize
from hydra.core.config_store import ConfigStore

from cache import Experiment, Config

def main(path):
    exp = Experiment.from_save(path)
    exp.draw()

if __name__ == "__main__":
    fire.Fire(main)