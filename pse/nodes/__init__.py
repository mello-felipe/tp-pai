"""Catálogo de nós: cada arquivo .py desta pasta é um nó.

Basta criar o arquivo (copie `_template.py`) que ele aparece na paleta.
Arquivos que começam com "_" são ignorados.
"""
from __future__ import annotations

import importlib
import pkgutil

from pse.core import NodeSpec, NodeType


def discover() -> dict[str, NodeType]:
    """Importa todos os módulos de nó e valida o esqueleto de cada um."""
    types: dict[str, NodeType] = {}
    for info in sorted(pkgutil.iter_modules(__path__), key=lambda m: m.name):
        if info.name.startswith("_"):
            continue
        mod = importlib.import_module(f"{__name__}.{info.name}")
        spec, execute = getattr(mod, "NODE", None), getattr(mod, "execute", None)
        if not isinstance(spec, NodeSpec) or not callable(execute):
            raise TypeError(f"pse/nodes/{info.name}.py precisa definir NODE = NodeSpec(...) e def execute(inputs, params)")
        if spec.preview is not None and spec.preview not in spec.inputs:
            raise TypeError(f"pse/nodes/{info.name}.py: preview '{spec.preview}' não é uma entrada")
        types[info.name] = NodeType(info.name, spec, execute)
    return types


def by_category(types: dict[str, NodeType]) -> dict[str, list[NodeType]]:
    cats: dict[str, list[NodeType]] = {}
    for t in sorted(types.values(), key=lambda t: t.spec.title):
        cats.setdefault(t.spec.category, []).append(t)
    return cats
