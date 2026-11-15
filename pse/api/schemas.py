"""Formato JSON trocado com o frontend."""
from __future__ import annotations

from dataclasses import asdict
from typing import Annotated, Any

from pydantic import BaseModel, Field

from ..core import NodeType

ID_PATTERN = r"^[A-Za-z0-9_-]{1,64}$"  # ids gerados pelo frontend (React Flow)
NodeIdStr = Annotated[str, Field(pattern=ID_PATTERN)]
PortName = Annotated[str, Field(min_length=1, max_length=64)]


def node_type_json(t: NodeType) -> dict[str, Any]:
    """NodeSpec -> JSON. O frontend monta a paleta e os widgets a partir daqui."""
    spec = asdict(t.spec)
    return {"key": t.key, **spec}


class NodeIn(BaseModel):
    id: NodeIdStr
    type: Annotated[str, Field(max_length=64)]
    values: dict[str, Any] = Field(default_factory=dict)


class LinkIn(BaseModel):
    src: NodeIdStr
    src_port: PortName
    dst: NodeIdStr
    dst_port: PortName


class WorkflowIn(BaseModel):
    """Estado completo do fluxo no frontend. O backend se ajusta a ele."""
    nodes: list[NodeIn] = Field(default_factory=list, max_length=500)
    links: list[LinkIn] = Field(default_factory=list, max_length=2000)
