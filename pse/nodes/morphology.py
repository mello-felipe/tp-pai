from __future__ import annotations

import numpy as np

from pse.core import NodeSpec, Param, require_gray
from pse.core.window import pad, shifted

OPERATIONS = ("Erosão", "Dilatação", "Abertura", "Fechamento")
ELEMENTS = ("Quadrado", "Cruz", "Disco")
SIZES = ("3×3", "5×5", "7×7", "9×9")

# =============================================================================
# DEFINIÇÃO
# =============================================================================
NODE = NodeSpec(
    title="Morfologia",
    category="Morfologia",
    description="Erosão = mínimo na vizinhança do elemento; dilatação = máximo. Abertura "
                "(erosão e depois dilatação) remove pontos soltos; fechamento (dilatação e "
                "depois erosão) fecha buracos. Funciona em imagens binárias e em tons de cinza.",
    inputs=("imagem",),
    outputs=("imagem",),
    params=(
        Param("operacao", "Operação", "choice", OPERATIONS[2], choices=OPERATIONS),
        Param("elemento", "Elemento", "choice", ELEMENTS[0], choices=ELEMENTS),
        Param("tamanho", "Tamanho", "choice", SIZES[0], choices=SIZES),
    ),
)


# =============================================================================
# EXECUÇÃO
# =============================================================================
def element(shape: str, n: int) -> np.ndarray:
    r = n // 2
    dy, dx = np.mgrid[-r:r + 1, -r:r + 1]
    if shape == "Cruz":
        return (dy == 0) | (dx == 0)
    if shape == "Disco":
        return dy * dy + dx * dx <= r * r
    return np.ones((n, n), dtype=bool)


def _extreme(img: np.ndarray, se: np.ndarray, use_max: bool) -> np.ndarray:
    r = se.shape[0] // 2
    padded = pad(img, r, value=0 if use_max else 255)  # valor neutro: a borda não interfere
    combine = np.maximum if use_max else np.minimum
    result = None
    for dy, dx in zip(*np.nonzero(se)):
        view = shifted(padded, r, int(dy) - r, int(dx) - r)
        result = view.copy() if result is None else combine(result, view)
    return result


def erode(img: np.ndarray, se: np.ndarray) -> np.ndarray:
    return _extreme(img, se, use_max=False)


def dilate(img: np.ndarray, se: np.ndarray) -> np.ndarray:
    return _extreme(img, se, use_max=True)


def execute(inputs: dict, params: dict) -> dict:
    img = require_gray(inputs, "imagem")
    se = element(params["elemento"], int(params["tamanho"][0]))
    op = params["operacao"]
    if op == "Erosão":
        out = erode(img, se)
    elif op == "Dilatação":
        out = dilate(img, se)
    elif op == "Abertura":
        out = dilate(erode(img, se), se)
    else:
        out = erode(dilate(img, se), se)
    return {"imagem": out.astype(np.uint8)}
