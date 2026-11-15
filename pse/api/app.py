"""Aplicação FastAPI.

Roda só em 127.0.0.1. Em desenvolvimento, o Vite repassa /api para cá
(mesma origem), então não há CORS. O TrustedHostMiddleware recusa outros
Hosts (proteção contra DNS rebinding).
"""
from __future__ import annotations

from fastapi import APIRouter, FastAPI
from fastapi.middleware.trustedhost import TrustedHostMiddleware

from ..core import NodeType
from ..nodes import discover
from .schemas import node_type_json

ALLOWED_HOSTS = ["127.0.0.1", "localhost"]


def create_app(types: dict[str, NodeType] | None = None) -> FastAPI:
    types = discover() if types is None else types
    app = FastAPI(title="PSE-Image")
    app.add_middleware(TrustedHostMiddleware, allowed_hosts=ALLOWED_HOSTS)

    api = APIRouter(prefix="/api")

    @api.get("/health")
    def health() -> dict:
        return {"ok": True}

    @api.get("/node-types")
    def node_types() -> list[dict]:
        return [node_type_json(t) for t in sorted(types.values(), key=lambda t: t.key)]

    app.include_router(api)
    return app
