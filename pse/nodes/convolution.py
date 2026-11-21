from __future__ import annotations

import numpy as np

from pse.core import NodeSpec, Param, require_gray
from pse.core.window import pad, shifted

OPERATIONS = ("Convolução", "Mediana")
BORDERS = ("Replicar", "Zero")
OUTPUTS = ("Limitar 0–255", "Valor absoluto", "Normalizar mín–máx")
MEAN_3X3 = ((1, 1, 1), (1, 1, 1), (1, 1, 1))

# =============================================================================
# DEFINIÇÃO
# =============================================================================
NODE = NodeSpec(
    title="Convolução",
    category="Filtros",
    description="Convolução com a máscara (tamanho e pesos editáveis; use \"Preencher com\" "
                "para Média, Gaussiana, Laplaciano, Sobel...). Mediana usa só o tamanho da "
                "máscara: cada pixel vira a mediana da vizinhança (remove ruído sal e pimenta).",
    inputs=("imagem",),
    outputs=("imagem",),
    params=(
        Param("operacao", "Operação", "choice", OPERATIONS[0], choices=OPERATIONS),
        Param("mascara", "Máscara", "kernel", MEAN_3X3, -100, 100),
        Param("normalizar", "Dividir pela soma dos pesos", "bool", True),
        Param("borda", "Borda", "choice", BORDERS[0], choices=BORDERS),
        Param("saida", "Saída", "choice", OUTPUTS[0], choices=OUTPUTS),
    ),
)


# =============================================================================
# EXECUÇÃO
# =============================================================================
def convolve(img: np.ndarray, kernel: np.ndarray, replicate: bool) -> np.ndarray:
    # g(y, x) = soma de w(i, j)·f(y - i, x - j): máscara espelhada (convolução, não correlação)
    r = kernel.shape[0] // 2
    padded = pad(img.astype(np.float64), r, replicate=replicate)
    acc = np.zeros(img.shape, dtype=np.float64)
    for a in range(kernel.shape[0]):
        for b in range(kernel.shape[1]):
            if kernel[a, b] != 0:
                acc += kernel[a, b] * shifted(padded, r, r - a, r - b)
    return acc


def median(img: np.ndarray, n: int, replicate: bool) -> np.ndarray:
    r = n // 2
    padded = pad(img, r, replicate=replicate)
    stack = np.stack([shifted(padded, r, dy, dx) for dy in range(-r, r + 1) for dx in range(-r, r + 1)])
    return np.sort(stack, axis=0)[n * n // 2]


def to_uint8(values: np.ndarray, mode: str) -> np.ndarray:
    if mode == "Valor absoluto":
        values = np.abs(values)
    elif mode == "Normalizar mín–máx":
        lo, hi = values.min(), values.max()
        values = (values - lo) * (255 / (hi - lo)) if hi > lo else np.zeros_like(values)
    return np.clip(np.floor(values + 0.5), 0, 255).astype(np.uint8)


def execute(inputs: dict, params: dict) -> dict:
    img = require_gray(inputs, "imagem")
    kernel = np.asarray(params["mascara"], dtype=np.float64)
    replicate = params["borda"] == "Replicar"

    if params["operacao"] == "Mediana":
        return {"imagem": median(img, kernel.shape[0], replicate)}

    total = kernel.sum()
    if params["normalizar"] and total != 0:
        kernel = kernel / total
    return {"imagem": to_uint8(convolve(img, kernel, replicate), params["saida"])}
