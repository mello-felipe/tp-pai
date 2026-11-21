"""Uso: python build.py [--skip-frontend]   (sem Node: reaproveita frontend/dist)"""
import os
import shutil
import subprocess
import sys

import PyInstaller.__main__

ROOT = os.path.dirname(os.path.abspath(__file__))
NODES_DIR = os.path.join(ROOT, "pse", "nodes")
FRONTEND = os.path.join(ROOT, "frontend")
FRONTEND_DIST = os.path.join(FRONTEND, "dist")


def build_frontend(skip: bool) -> None:
    if not skip:
        npm = shutil.which("npm")
        if npm is None:
            sys.exit("npm não encontrado: instale o Node.js 20+ ou use --skip-frontend com frontend/dist pronto")
        subprocess.run([npm, "ci"], cwd=FRONTEND, check=True)
        subprocess.run([npm, "run", "build"], cwd=FRONTEND, check=True)
    if not os.path.isfile(os.path.join(FRONTEND_DIST, "index.html")):
        sys.exit("frontend/dist/index.html não existe: rode sem --skip-frontend")


def node_imports() -> list[str]:
    """Os nós são descobertos em tempo de execução (pkgutil), então o PyInstaller
    não os enxerga sozinho: cada arquivo de pse/nodes/ vira um --hidden-import."""
    hidden = []
    for f in sorted(os.listdir(NODES_DIR)):
        if f.endswith(".py") and not f.startswith("_"):
            hidden += ["--hidden-import", f"pse.nodes.{f[:-3]}"]
    return hidden


def main() -> None:
    build_frontend(skip="--skip-frontend" in sys.argv)
    PyInstaller.__main__.run([
        os.path.join(ROOT, "main.py"),
        "--noconfirm", "--onefile",
        "--name", "PSE-Image",
        *node_imports(),
        "--collect-submodules", "uvicorn",  # uvicorn carrega loops/protocolos por nome
        "--add-data", f"{FRONTEND_DIST}{os.pathsep}frontend",
        "--distpath", os.path.join(ROOT, "dist"),
        "--workpath", os.path.join(ROOT, "build"),
        "--specpath", os.path.join(ROOT, "build"),
    ])


if __name__ == "__main__":
    main()
