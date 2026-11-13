"""Ler PNG: abre um arquivo PNG e entrega a imagem colorida (RGB)."""
from __future__ import annotations

import numpy as np
from PIL import Image as PILImage

from pse.core import NodeError, NodeSpec, Param

# =============================================================================
# DEFINIÇÃO
# =============================================================================
NODE = NodeSpec(
    title="Ler PNG",
    category="Interface",
    description="Abre um arquivo PNG e entrega a imagem colorida (RGB). "
                "Use o nó Escala de Cinza para converter.",
    inputs=(),
    outputs=("imagem",),
    params=(
        Param("path", "Arquivo", "file_open"),
    ),
)


# =============================================================================
# EXECUÇÃO
# =============================================================================
def execute(inputs: dict, params: dict) -> dict:
    path = params["path"]
    if not path:
        raise NodeError("escolha um arquivo")

    # Pillow só decodifica o PNG; qualquer modo (paleta, cinza, RGBA) vira RGB
    with PILImage.open(path) as im:
        rgb = np.array(im.convert("RGB"), dtype=np.uint8)

    return {"imagem": rgb}
