"""Exibir: mostra a imagem (cinza ou colorida) dentro do nó e a repassa adiante."""
from __future__ import annotations

from pse.core import NodeSpec, require_image

# =============================================================================
# DEFINIÇÃO
# =============================================================================
NODE = NodeSpec(
    title="Exibir",
    category="Interface",
    description="Mostra a imagem. Repassa a imagem, então pode ficar no meio do fluxo.",
    inputs=("imagem",),
    outputs=("imagem",),
    preview="imagem",  # a UI desenha esta entrada no nó
)


# =============================================================================
# EXECUÇÃO
# =============================================================================
def execute(inputs: dict, params: dict) -> dict:
    return {"imagem": require_image(inputs, "imagem")}
