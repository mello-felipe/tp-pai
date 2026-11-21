from __future__ import annotations

import numpy as np


def pad(img: np.ndarray, r: int, value: float = 0, replicate: bool = False) -> np.ndarray:
    if r < 0:
        raise ValueError("raio negativo")
    h, w = img.shape
    if replicate:
        rows = np.clip(np.arange(-r, h + r), 0, h - 1)
        cols = np.clip(np.arange(-r, w + r), 0, w - 1)
        return img[rows[:, None], cols[None, :]]
    out = np.full((h + 2 * r, w + 2 * r), value, dtype=img.dtype)
    out[r:r + h, r:r + w] = img
    return out


def shifted(padded: np.ndarray, r: int, dy: int, dx: int) -> np.ndarray:
    """Vizinho (y+dy, x+dx) de cada pixel da imagem original."""
    h, w = padded.shape[0] - 2 * r, padded.shape[1] - 2 * r
    return padded[r + dy:r + dy + h, r + dx:r + dx + w]
