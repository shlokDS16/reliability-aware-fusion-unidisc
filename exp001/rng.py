"""Counter-based generator keyed by (pool, seed index, stream) (card 4.5, 9 item 5).

Uses numpy Philox with key = (pool_code << 64) | i and the stream placed in the high words of the 256-bit counter, so
streams never overlap for any realistic draw count and a resumed seed is bitwise identical to an uninterrupted one.
"""
from __future__ import annotations

import numpy as np

from .config import POOL_CODE, STREAM_SAMPLER, STREAM_PRAND, STREAM_PROBE


def generator(pool: str, i: int, stream: int) -> np.random.Generator:
    key = (POOL_CODE[pool] << 64) | int(i)
    counter = int(stream) << 192
    return np.random.Generator(np.random.Philox(key=key, counter=counter))


def sampler_uniforms(pool: str, i: int, n: int) -> np.ndarray:
    """u_j for every generated position j, float64, drawn once (CRN across arms)."""
    return generator(pool, i, STREAM_SAMPLER).random(n, dtype=np.float64)


def position_priorities(pool: str, i: int, n: int) -> np.ndarray:
    """Fixed random priority per generated position for P_rand (uniformly random positions, shared across arms)."""
    return generator(pool, i, STREAM_PRAND).random(n, dtype=np.float64)


def probe_generator(pool: str, i: int, pass_index: int, direction: int = 0) -> np.random.Generator:
    """Probe stream, one sub-stream per (pass, direction), disjoint from the sampler stream."""
    key = (POOL_CODE[pool] << 64) | int(i)
    counter = (int(STREAM_PROBE) << 192) | (((int(pass_index) << 8) | int(direction)) << 128)
    return np.random.Generator(np.random.Philox(key=key, counter=counter))
