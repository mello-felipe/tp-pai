from __future__ import annotations

import numpy as np

from pse.core import STATUS_KEY, NodeSpec, Param, require_gray

METHODS = ("Otsu", "Manual")

# =============================================================================
# DEFINIÇÃO
# =============================================================================
NODE = NodeSpec(
    title="Limiarização",
    category="Segmentação",
    description="Pixels com tom maior que o limiar viram 255 (objeto), os demais 0 (fundo). "
                "Otsu escolhe o limiar que maximiza a variância entre as duas classes.",
    inputs=("imagem",),
    outputs=("imagem",),
    params=(
        Param("metodo", "Método", "choice", METHODS[0], choices=METHODS),
        Param("limiar", "Limiar (manual)", "int", 128, 0, 255),
        Param("inverter", "Inverter (objeto escuro)", "bool", False),
    ),
)


# =============================================================================
# EXECUÇÃO
# =============================================================================
def otsu_threshold(img: np.ndarray) -> int:
    # Classe 0 = tons <= t. Variância entre classes: (muT·w0 - mu)² / (w0·(1 - w0)).
    hist = np.bincount(img.ravel(), minlength=256).astype(np.float64)
    p = hist / hist.sum()
    levels = np.arange(256)
    w0 = np.cumsum(p)
    mu = np.cumsum(levels * p)
    mu_total = mu[-1]
    valid = (w0 > 0) & (w0 < 1)
    if not valid.any():  # imagem com um único tom
        return int(img.flat[0])
    between = np.zeros(256)
    between[valid] = (mu_total * w0[valid] - mu[valid]) ** 2 / (w0[valid] * (1 - w0[valid]))
    return int(np.argmax(between))


def execute(inputs: dict, params: dict) -> dict:
    img = require_gray(inputs, "imagem")
    otsu = params["metodo"] == "Otsu"
    t = otsu_threshold(img) if otsu else int(params["limiar"])

    foreground = img > t
    if params["inverter"]:
        foreground = ~foreground
    binary = np.where(foreground, 255, 0).astype(np.uint8)
    return {"imagem": binary, STATUS_KEY: f"limiar = {t}" + (" (Otsu)" if otsu else "")}
