from __future__ import annotations

import numpy as np

from pse.core import NodeSpec, Param, require_gray

# Elementos estruturantes: 1 = pixel que precisa estar dentro do objeto.
ELEMENTS = {
    "Cruz": [[0, 1, 0],
              [1, 1, 1],
              [0, 1, 0]],
    "Quadrado 15x15": [[1] * 15 for _ in range(15)],
}

# =============================================================================
# DEFINIÇÃO
# =============================================================================
NODE = NodeSpec(
    title="Erosão",
    category="Morfologia",
    description="Mantém só os pontos em que o elemento estruturante cabe inteiro no objeto. "
                "Encolhe objetos e remove componentes pequenos.",
    inputs=("imagem",),
    outputs=("imagem",),
    params=(
        Param("element", "Elemento estruturante", "choice", "Cruz", choices=tuple(ELEMENTS)),
    ),
)


# =============================================================================
# EXECUÇÃO
# =============================================================================
def execute(inputs: dict, params: dict) -> dict:
    element = ELEMENTS[params["element"]]
    img = require_gray(inputs, "imagem")
    out = np.zeros_like(img)

    img_height, img_width = img.shape
    element_height, element_width = len(element), len(element[0])
    padding_height, padding_width = element_height // 2, element_width // 2

    for img_row in range(padding_height, img_height - padding_height):
        for img_col in range(padding_width, img_width - padding_width):
            element_fits = True
            for element_row in range(element_height):
                for element_col in range(element_width):
                    if element[element_row][element_col] == 1:
                        matching_row = img_row + element_row - padding_height
                        matching_col = img_col + element_col - padding_width
                        if img[matching_row, matching_col] == 0:
                            element_fits = False

            if element_fits:
                out[img_row, img_col] = 255

    return {"imagem": out}
