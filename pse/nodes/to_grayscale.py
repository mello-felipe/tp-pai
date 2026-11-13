"""Escala de Cinza: converte uma imagem RGB para tons de cinza."""
from __future__ import annotations

import numpy as np

from pse.core import NodeSpec, require_image

# =============================================================================
# DEFINIÇÃO
# =============================================================================
NODE = NodeSpec(
    title="Escala de Cinza",
    category="Interface",
    description="Converte a imagem para tons de cinza pela luminância "
                "(Y = 0.299 R + 0.587 G + 0.114 B). Imagem já em cinza passa direto.",
    inputs=("imagem",),
    outputs=("cinza",),
)


# =============================================================================
# EXECUÇÃO
# =============================================================================
def execute(inputs: dict, params: dict) -> dict:
    img = require_image(inputs, "imagem")
    if img.ndim == 2:
        return {"cinza": img}

    rgb = img.astype(np.float64)
    # luminância ITU-R BT.601
    gray = 0.299 * rgb[..., 0] + 0.587 * rgb[..., 1] + 0.114 * rgb[..., 2]

    return {"cinza": np.clip(np.rint(gray), 0, 255).astype(np.uint8)}
