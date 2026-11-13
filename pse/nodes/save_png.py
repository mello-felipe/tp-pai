"""Salvar PNG: grava a imagem de entrada (cinza ou colorida) num arquivo PNG."""
from __future__ import annotations

import os

import numpy as np
from PIL import Image as PILImage

from pse.core import STATUS_KEY, NodeError, NodeSpec, Param, project_root, require_image

DEFAULT_DIR = "img"  # pasta usada quando o caminho fica vazio (relativa à raiz do projeto)

# =============================================================================
# DEFINIÇÃO
# =============================================================================
NODE = NodeSpec(
    title="Salvar PNG",
    category="Interface",
    description="Grava a imagem num PNG ao clicar em Salvar. Sem caminho, salva "
                "em ./img na raiz do projeto.",
    inputs=("imagem",),
    outputs=("imagem",),
    params=(
        Param("name", "Nome", "text", "resultado", hint="ex.: resultado"),
        Param("path", "Caminho", "dir", "", hint="vazio = ./img"),
        Param("save", "Salvar", "action"),
    ),
)


# =============================================================================
# EXECUÇÃO
# =============================================================================
def execute(inputs: dict, params: dict) -> dict:
    img = require_image(inputs, "imagem")
    if not params["save"]:  # execução normal: só repassa a imagem
        return {"imagem": img}

    name = params["name"].strip()
    if not name:
        raise NodeError("informe o nome do arquivo")
    if "/" in name or "\\" in name:
        raise NodeError("o nome não pode conter barras: use o campo Caminho")
    if not name.lower().endswith(".png"):
        name += ".png"

    root = project_root()
    folder = os.path.expanduser(params["path"].strip())
    if not folder:
        folder = os.path.join(root, DEFAULT_DIR)
        os.makedirs(folder, exist_ok=True)
    elif not os.path.isabs(folder):
        folder = os.path.join(root, folder)  # caminho relativo: a partir da raiz do projeto
    if not os.path.isdir(folder):
        raise NodeError(f"pasta não existe: {folder}")

    dest = os.path.join(folder, name)
    PILImage.fromarray(np.asarray(img, dtype=np.uint8)).save(dest, format="PNG")

    try:  # mostra relativo à raiz quando possível (commonpath falha entre drives no Windows)
        shown = os.path.relpath(dest, root) if os.path.commonpath([dest, root]) == root else dest
    except ValueError:
        shown = dest
    return {"imagem": img, STATUS_KEY: f"salvo em {shown}"}
