from dataclasses import dataclass


@dataclass
class GenerationParams:
    num_requests: int
    num_tables: int
    max_pages: int
    q: float
    p_scan: float
    gamma: float


@dataclass
class Paths:
    lib_cache_sim: str  # path to libCacheSim binaries
    datapath: str
    save_path: str


@dataclass
class CostParams:
    c_get: float
    c_scan: float


@dataclass
class SharedParameters:
    cache_sizes: str


@dataclass
class LibCacheParams:
    algos: str
    trace_format: str
    trace_format_params: str


@dataclass
class ProposedParams:
    algos: str
    alpha: float
    beta: float
    move_cost: float
    return_trace_hit: bool


@dataclass
class Config:
    paths: Paths
    generation_params: GenerationParams
    cost_params: CostParams
    shared_parameters: SharedParameters
    libCache_params: LibCacheParams
    proposed_params: ProposedParams
