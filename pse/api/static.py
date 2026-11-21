from __future__ import annotations

import os
import sys

from ..core import project_root


def frontend_dist() -> str | None:
    # No executável, o PyInstaller extrai o build em <_MEIPASS>/frontend.
    bundle = getattr(sys, "_MEIPASS", None)
    path = os.path.join(bundle, "frontend") if bundle else os.path.join(project_root(), "frontend", "dist")
    return path if os.path.isfile(os.path.join(path, "index.html")) else None
