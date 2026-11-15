"""Validação dos valores de parâmetros vindos do frontend."""
from __future__ import annotations

from typing import Any

from ..core import NodeSpec, Param

MAX_TEXT = 1024
TEXT_KINDS = {"text", "dir", "file_open", "file_save"}


class WorkflowError(ValueError):
    """Fluxo inválido enviado pelo frontend (vira HTTP 422)."""


def merge_values(spec: NodeSpec, values: dict[str, Any]) -> dict[str, Any]:
    """Valores completos do nó: padrão de cada parâmetro + o que veio do frontend,
    convertido e validado. Nomes desconhecidos são ignorados. Parâmetros "action"
    ficam sempre False: só disparam pela rota de ações."""
    return {p.name: _coerce(p, values[p.name]) if p.name in values and p.kind != "action"
            else p.default for p in spec.params}


def _coerce(p: Param, value: Any) -> Any:
    try:
        if p.kind in ("int", "float"):
            if isinstance(value, bool):
                raise TypeError
            num = int(value) if p.kind == "int" else float(value)
            return min(max(num, p.min), p.max)
        if p.kind == "bool":
            if not isinstance(value, bool):
                raise TypeError
            return value
        if p.kind == "choice":
            if value not in p.choices:
                raise ValueError
            return value
        if p.kind in TEXT_KINDS:
            if not isinstance(value, str) or len(value) > MAX_TEXT:
                raise ValueError
            return value
    except (TypeError, ValueError) as e:
        raise WorkflowError(f"valor inválido para o parâmetro '{p.name}': {value!r}") from e
    raise WorkflowError(f"tipo de parâmetro não suportado: {p.kind}")
