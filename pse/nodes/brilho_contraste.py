"""Brilho e Contraste: processamento pontual g = c·(f − 128) + 128 + b."""
from __future__ import annotations

import numpy as np

from pse.core import NodeSpec, Param, require_gray

# =============================================================================
# DEFINIÇÃO
# =============================================================================
NODE = NodeSpec(
    title="Brilho e Contraste",
    category="Processamento pontual",
    description="g = c·(f − 128) + 128 + b. O contraste c estica (c > 1) ou "
                "comprime (c < 1) os tons em volta do cinza médio 128; o brilho b "
                "soma o mesmo valor a todos os pixels. O resultado fica entre 0 e 255.",
    inputs=("imagem",),
    outputs=("imagem",),
    params=(
        Param("brilho", "Brilho", "int", 0, -255, 255),
        Param("contraste", "Contraste", "float", 1.0, 0.0, 3.0),
    ),
)


# =============================================================================
# EXECUÇÃO
# =============================================================================
def execute(inputs: dict, params: dict) -> dict:
    imagem = require_gray(inputs, "imagem")
    brilho = params["brilho"]
    contraste = params["contraste"]

    # Matriz da imagem como lista de listas de int: pixels[y][x] = tom do pixel
    pixels = imagem.tolist()
    altura = len(pixels)
    largura = len(pixels[0])
    saida = [[0] * largura for _ in range(altura)]

    # Processamento pontual: o novo tom de cada pixel depende só do tom
    # antigo daquele mesmo pixel.
    for y in range(altura):
        for x in range(largura):
            f = pixels[y][x]

            # 1. Aplica a fórmula
            g = contraste * (f - 128) + 128 + brilho

            # 2. Satura: o que passou da faixa 0–255 fica no limite
            if g < 0:
                g = 0
            if g > 255:
                g = 255

            # 3. Arredonda para o inteiro mais próximo (c pode gerar fração)
            saida[y][x] = int(g + 0.5)

    # Volta para o formato de imagem usado pelos outros blocos
    return {"imagem": np.array(saida, dtype=np.uint8)}
