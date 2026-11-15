"""Formato JSON trocado com o frontend."""
from __future__ import annotations

from dataclasses import asdict
from typing import Any

from ..core import NodeType


def node_type_json(t: NodeType) -> dict[str, Any]:
    """NodeSpec -> JSON. O frontend monta a paleta e os widgets a partir daqui."""
    spec = asdict(t.spec)
    return {"key": t.key, **spec}
