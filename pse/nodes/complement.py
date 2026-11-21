from __future__ import annotations

import numpy as np

from pse.core import NodeSpec, require_gray

# =============================================================================
# DEFINIÇÃO
# =============================================================================
NODE = NodeSpec(
    title="Complemento",
    category="Pontual",
    description="Negativo da imagem: cada pixel f vira 255 - f.",
    inputs=("imagem",),
    outputs=("imagem",),
)


# =============================================================================
# EXECUÇÃO
# =============================================================================
def execute(inputs: dict, params: dict) -> dict:
    img = require_gray(inputs, "imagem")
    return {"imagem": (np.uint8(255) - img).astype(np.uint8)}
