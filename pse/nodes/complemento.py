"""Complemento: negativo da imagem (preto vira branco e branco vira preto)."""
from __future__ import annotations

import numpy as np

from pse.core import NodeSpec, require_gray

# =============================================================================
# DEFINIÇÃO
# =============================================================================
NODE = NodeSpec(
    title="Complemento",
    category="Processamento pontual",
    description="Negativo da imagem: cada tom f vira 255 − f. "
                "Preto (0) vira branco (255) e vice-versa.",
    inputs=("imagem",),
    outputs=("imagem",),
)


# =============================================================================
# EXECUÇÃO
# =============================================================================
def execute(inputs: dict, params: dict) -> dict:
    imagem = require_gray(inputs, "imagem")

    # Matriz da imagem como lista de listas de int: pixels[y][x] = tom do pixel
    pixels = imagem.tolist()
    altura = len(pixels)
    largura = len(pixels[0])
    saida = [[0] * largura for _ in range(altura)]

    # Percorre a imagem pixel a pixel aplicando g = 255 − f.
    # Como f vai de 0 a 255, 255 − f também fica entre 0 e 255.
    for y in range(altura):
        for x in range(largura):
            f = pixels[y][x]
            saida[y][x] = 255 - f

    # Volta para o formato de imagem usado pelos outros blocos
    return {"imagem": np.array(saida, dtype=np.uint8)}
