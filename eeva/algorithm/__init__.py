from .eeva import EEvA, EEvAGreedy, EEvA_UCB
from .eeva_seq import EEvASeq
from .eeva_t import EEvAT
from .proposed import PROPOSED
from .requestItem import Req

_ = Req
alg_dict = {"PROPOSED": PROPOSED, "EEvASeq": EEvASeq, 
            "EEvAT": EEvAT, "EEvA": EEvA, "EEvAGreedy": EEvAGreedy,
            "EEvAUCB": EEvA_UCB
            }
alg_names = {
    "PROPOSED": "PROPOSED",
    "EEvASeq": "EEvA-Seq",
    "EEvAT": "EEvA-T",
    "EEvA": "EEvA",
    "EEvAGreedy": "EEvA-Greedy",
    "EEvAUCB": "EEvA-UCB"
}
__all__ = ["Req", "alg_names", "alg_dict"] + list(alg_dict.keys())
