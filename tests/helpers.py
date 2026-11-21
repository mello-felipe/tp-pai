from __future__ import annotations

import numpy as np

from pse.nodes import discover

TYPES = discover()


def run(key: str, inputs: dict | None = None, **params) -> dict:
    t = TYPES[key]
    values = {p.name: p.default for p in t.spec.params} | params
    return t.execute(inputs or {}, values)


def gray(rows: list[list[int]]) -> np.ndarray:
    return np.array(rows, dtype=np.uint8)
