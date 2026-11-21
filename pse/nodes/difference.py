from __future__ import annotations

import math

import numpy as np

from pse.core import STATUS_KEY, NodeError, NodeSpec, Param, require_gray

MODES = ("Absoluta", "Com sinal")

# =============================================================================
# DEFINIÇÃO
# =============================================================================
NODE = NodeSpec(
    title="Diferença",
    category="Entre imagens",
    description="Absoluta: |A - B|. Com sinal: (A - B)/2 + 128 (cinza = iguais, claro = A "
                "maior, escuro = B maior). Mostra MSE e PSNR entre A e B.",
    inputs=("A", "B"),
    outputs=("imagem",),
    params=(Param("modo", "Modo", "choice", MODES[0], choices=MODES),),
)


# =============================================================================
# EXECUÇÃO
# =============================================================================
def quality(diff: np.ndarray) -> str:
    mse = float(np.mean(diff * diff))
    if mse == 0:
        return "imagens idênticas (MSE 0)"
    psnr = 10 * math.log10(255**2 / mse)
    return f"MSE {mse:.2f} · PSNR {psnr:.2f} dB"


def execute(inputs: dict, params: dict) -> dict:
    a, b = require_gray(inputs, "A"), require_gray(inputs, "B")
    if a.shape != b.shape:
        raise NodeError(f"tamanhos diferentes: A {a.shape[1]}×{a.shape[0]}, B {b.shape[1]}×{b.shape[0]}")

    diff = a.astype(np.float64) - b.astype(np.float64)
    out = np.abs(diff) if params["modo"] == "Absoluta" else diff / 2 + 128
    img = np.clip(np.floor(out + 0.5), 0, 255).astype(np.uint8)
    return {"imagem": img, STATUS_KEY: quality(diff)}
