"""<Nome do nó>: <o que ele faz, em uma linha>.

COMO USAR ESTE TEMPLATE
  1. Copie para pse/nodes/<nome_do_no>.py (snake_case, sem "_" no início).
  2. Preencha NODE e execute(). Pronto: o nó aparece na paleta.
"""
from __future__ import annotations

import numpy as np

from pse.core import NodeError, NodeSpec, Param, require_gray

# =============================================================================
# DEFINIÇÃO — título, portas e parâmetros (a UI é gerada a partir daqui)
# =============================================================================
NODE = NodeSpec(
    title="Exemplo",
    category="Outros",                 # seção da paleta
    description="Descrição exibida ao passar o mouse na paleta.",
    inputs=("imagem",),                # portas de entrada (pode ser vazio ou várias)
    outputs=("imagem",),               # portas de saída (pode ser vazio ou várias)
    params=(
        # Param(nome, rótulo, tipo, padrão, mín, máx)
        # tipos: "int", "float", "choice" (use choices=(...)), "bool", "text", "dir",
        #        "file_open", "file_save", "action" (botão; ver pse/core/node.py)
        Param("valor", "Valor", "int", 0, -100, 100),
    ),
    preview=None,                      # nome de uma entrada para mostrar a imagem no nó
)


# =============================================================================
# EXECUÇÃO — o algoritmo (equivalente ao execute.ts do n8n)
#   inputs: {porta_entrada: imagem uint8 ou None se desconectada}
#           cinza = (altura, largura); colorida = (altura, largura, 3)
#   params: {nome_param: valor atual}
#   retorno: {porta_saida: imagem uint8}
#   require_gray(inputs, porta) devolve a imagem em cinza ou mostra erro no nó
#   (desconectada / colorida). Lance NodeError("mensagem") para outros erros.
#   Regra do TP: nada de métodos prontos (OpenCV, scipy.ndimage, PIL.ImageFilter...).
# =============================================================================
def execute(inputs: dict, params: dict) -> dict:
    img = require_gray(inputs, "imagem")

    out = np.clip(img.astype(np.int16) + params["valor"], 0, 255).astype(np.uint8)

    return {"imagem": out}
