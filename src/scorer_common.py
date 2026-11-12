"""Backend-independent pieces of the scorer."""
from __future__ import annotations

from dataclasses import dataclass

import numpy as np


@dataclass
class Scored:
    logp: np.ndarray  # (T,) nats, log P(target token t | prefix, target < t)
    offsets: np.ndarray  # (T, 2) char span of each target token inside `target`
    n_prefix: int
    seconds: float
    rank1: np.ndarray | None = None  # (T,) bool, True if token was the argmax
    extra: dict | None = None  # name -> (T,) log-prob mass on a vocabulary subset at each position



def line_scores(target: str, sc: Scored) -> list[list[int]]:
    """Token indices belonging to each line (0-based line index) of `target`.

    A token is assigned to the line containing its first non-newline character; a pure
    newline token is assigned to the line it terminates.
    """
    # line start offsets
    starts = [0]
    for i, ch in enumerate(target):
        if ch == "\n":
            starts.append(i + 1)
    starts_arr = np.array(starts)
    buckets: list[list[int]] = [[] for _ in starts]
    for ti, (a, b) in enumerate(sc.offsets):
        seg = target[a:b]
        k = 0
        while k < len(seg) and seg[k] == "\n":
            k += 1
        anchor = a + k if k < len(seg) else a
        li = int(np.searchsorted(starts_arr, anchor, side="right") - 1)
        buckets[li].append(ti)
    return buckets
