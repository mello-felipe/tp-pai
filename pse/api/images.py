"""Codificação das imagens (ndarray uint8) em PNG para o navegador."""
from __future__ import annotations

import io

import numpy as np
from PIL import Image as PILImage


def encode_png(img: np.ndarray) -> bytes:
    """Pillow só grava o PNG (permitido pelo TP); nenhum processamento aqui."""
    buf = io.BytesIO()
    PILImage.fromarray(np.asarray(img, dtype=np.uint8)).save(buf, format="PNG")
    return buf.getvalue()


def image_meta(img: np.ndarray, version: int) -> dict:
    return {"version": version, "width": int(img.shape[1]), "height": int(img.shape[0]),
            "channels": 1 if img.ndim == 2 else int(img.shape[2])}
