"""Caminhos do projeto."""
from __future__ import annotations

import os
import sys


def project_root() -> str:
    """Raiz do projeto. No executável (PyInstaller), a pasta onde está o executável."""
    if getattr(sys, "frozen", False):
        return os.path.dirname(os.path.abspath(sys.executable))
    return os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
