from __future__ import annotations

import numpy as np

from pse.core import NodeSpec, Param, require_gray

# =============================================================================
# DEFINIÇÃO
# =============================================================================
NODE = NodeSpec(
    title="Brilho e Contraste",
    category="Pontual",
    description="g = c·(f - 128) + 128 + b. Contraste c > 1 afasta os tons do cinza "
                "médio, c < 1 aproxima; brilho b soma a todos os pixels. Satura em 0 e 255.",
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
def lookup_table(contrast: float, brightness: int) -> np.ndarray:
    levels = np.arange(256, dtype=np.float64)
    out = contrast * (levels - 128) + 128 + brightness
    return np.clip(np.floor(out + 0.5), 0, 255).astype(np.uint8)  # np.rint arredondaria .5 para o par


def execute(inputs: dict, params: dict) -> dict:
    img = require_gray(inputs, "imagem")
    lut = lookup_table(params["contraste"], params["brilho"])
    return {"imagem": lut[img]}
