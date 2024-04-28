import fire

from eeva import Experiment


def main(path):
    exp = Experiment.from_save(path)
    exp.draw()


if __name__ == "__main__":
    fire.Fire(main)
