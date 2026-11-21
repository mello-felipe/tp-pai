"""Gera o executável em dist/ (Windows, Linux ou macOS):  python build.py"""
import os

import PyInstaller.__main__

ROOT = os.path.dirname(os.path.abspath(__file__))
NODES_DIR = os.path.join(ROOT, "pse", "nodes")

# Os nós são descobertos em tempo de execução (pkgutil), então o PyInstaller
# não os enxerga sozinho: cada arquivo de pse/nodes/ vira um --hidden-import.
hidden = []
for f in sorted(os.listdir(NODES_DIR)):
    if f.endswith(".py") and not f.startswith("_"):
        hidden += ["--hidden-import", f"pse.nodes.{f[:-3]}"]

PyInstaller.__main__.run([
    os.path.join(ROOT, "main.py"),
    "--noconfirm", "--onefile", "--windowed",
    "--name", "PSE-Image",
    *hidden,
    "--distpath", os.path.join(ROOT, "dist"),
    "--workpath", os.path.join(ROOT, "build"),
    "--specpath", os.path.join(ROOT, "build"),
])
