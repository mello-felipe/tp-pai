"""Diferença: |A − B| pixel a pixel entre duas imagens do mesmo tamanho."""
from __future__ import annotations

import numpy as np

from pse.core import STATUS_KEY, NodeError, NodeSpec, require_gray

# =============================================================================
# DEFINIÇÃO
# =============================================================================
NODE = NodeSpec(
    title="Diferença",
    category="Comparação",
    description="Diferença absoluta |A − B| pixel a pixel. Preto = pixels iguais; "
                "quanto mais claro, mais diferentes. Mostra a diferença média.",
    inputs=("A", "B"),
    outputs=("imagem",),
)


# =============================================================================
# EXECUÇÃO
# =============================================================================
def execute(inputs: dict, params: dict) -> dict:
    # Matrizes das imagens como listas de listas de int: a[y][x] = tom do pixel
    a = require_gray(inputs, "A").tolist()
    b = require_gray(inputs, "B").tolist()

    altura, largura = len(a), len(a[0])
    altura_b, largura_b = len(b), len(b[0])
    if (altura, largura) != (altura_b, largura_b):
        raise NodeError(f"tamanhos diferentes: A é {largura}×{altura}, "
                        f"B é {largura_b}×{altura_b}")

    saida = [[0] * largura for _ in range(altura)]
    soma = 0

    # Percorre as duas imagens juntas, pixel a pixel
    for y in range(altura):
        for x in range(largura):
            # 1. Diferença entre os pixels na mesma posição (pode ser negativa)
            d = a[y][x] - b[y][x]

            # 2. Valor absoluto: |A − B| fica entre 0 e 255
            if d < 0:
                d = -d

            saida[y][x] = d
            soma += d

    # 3. Um número para comparar: a média das diferenças (0 = imagens iguais)
    media = soma / (altura * largura)

    # Volta para o formato de imagem usado pelos outros blocos
    return {"imagem": np.array(saida, dtype=np.uint8),
            STATUS_KEY: f"diferença média: {media:.2f}"}
