from .proposed import PROPOSED
from .proposed_UCB import PROPOSED_UCB

def EEvA(cache_size, alpha, beta, **kwargs):
    return PROPOSED(cache_size, alpha, beta, with_min=False, **kwargs)

def EEvA_UCB(cache_size, alpha, beta, **kwargs):
    return PROPOSED_UCB(cache_size, alpha, beta, with_min=True, **kwargs)


def EEvAGreedy(cache_size, alpha, beta, **kwargs):
    return PROPOSED(cache_size, alpha, beta, with_min=True, **kwargs)
