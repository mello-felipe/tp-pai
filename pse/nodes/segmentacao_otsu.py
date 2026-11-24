"""Segmentação (Otsu): binariza a imagem em cinza pelo limiar ótimo automático."""
from __future__ import annotations

import numpy as np

from pse.core import STATUS_KEY, NodeError, NodeSpec, require_gray

# =============================================================================
# DEFINIÇÃO
# =============================================================================
NODE = NodeSpec(
    title="Segmentação (Otsu)",
    category="Segmentação",
    description="Binariza a imagem em tons de cinza escolhendo automaticamente "
                "o limiar que maximiza a variância entre as classes fundo/objeto "
                "(método de Otsu). Sem parâmetros: o limiar é calculado a partir "
                "do histograma da própria imagem.",
    inputs=("imagem",),
    outputs=("binária",),
)



def execute(inputs: dict, params: dict) -> dict:
    img = require_gray(inputs, "imagem")

    hist = np.bincount(img.ravel(), minlength=256).astype(np.float64)
    prob = hist / hist.sum()

    niveis = np.arange(256, dtype=np.float64)
    w0 = np.cumsum(prob)                      # peso acumulado da classe "fundo" até t
    soma0 = np.cumsum(prob * niveis)          # soma acumulada de nível*probabilidade até t
    media_global = soma0[-1]

    w1 = 1.0 - w0
    valido = (w0 > 0) & (w1 > 0)              # t só é candidato se as duas classes existem
    if not valido.any():
        raise NodeError("imagem com um único nível de cinza: não há limiar que separe classes")

    with np.errstate(divide="ignore", invalid="ignore"):
        mu0 = np.where(w0 > 0, soma0 / w0, 0.0)
        mu1 = np.where(w1 > 0, (media_global - soma0) / w1, 0.0)

    variancia_entre_classes = np.where(valido, w0 * w1 * (mu0 - mu1) ** 2, -1.0)
    t_otimo = int(np.argmax(variancia_entre_classes))

    out = np.where(img > t_otimo, 255, 0).astype(np.uint8)
    return {"binária": out, STATUS_KEY: f"limiar (Otsu) = {t_otimo}"}
