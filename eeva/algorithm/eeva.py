from .proposed import PROPOSED


def EEvA(cache_size, alpha, beta, **kwargs):
    return PROPOSED(cache_size, alpha, beta, with_min=False, **kwargs)


def EEvAGreedy(cache_size, alpha, beta, **kwargs):
    return PROPOSED(cache_size, alpha, beta, with_min=True, **kwargs)
