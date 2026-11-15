"""Aplicação FastAPI.

Roda só em 127.0.0.1. Em desenvolvimento, o Vite repassa /api para cá
(mesma origem), então não há CORS. O TrustedHostMiddleware recusa outros
Hosts (proteção contra DNS rebinding).
"""
from __future__ import annotations

from typing import Annotated

from fastapi import APIRouter, FastAPI, HTTPException, Path, Response
from fastapi.middleware.trustedhost import TrustedHostMiddleware

from ..core import NodeType
from ..nodes import discover
from .images import encode_png
from .schemas import ID_PATTERN, WorkflowIn, node_type_json
from .values import WorkflowError
from .workspace import OUT, PREVIEW, Workspace

ALLOWED_HOSTS = ["127.0.0.1", "localhost"]
NodeIdPath = Annotated[str, Path(pattern=ID_PATTERN)]


def create_app(types: dict[str, NodeType] | None = None) -> FastAPI:
    types = discover() if types is None else types
    workspace = Workspace(types)
    app = FastAPI(title="PSE-Image")
    app.add_middleware(TrustedHostMiddleware, allowed_hosts=ALLOWED_HOSTS)
    app.state.workspace = workspace

    api = APIRouter(prefix="/api")

    @api.get("/health")
    def health() -> dict:
        return {"ok": True}

    @api.get("/node-types")
    def node_types() -> list[dict]:
        return [node_type_json(t) for t in sorted(types.values(), key=lambda t: t.key)]

    @api.put("/workflow")
    def put_workflow(wf: WorkflowIn) -> dict:
        try:
            return workspace.sync(wf)
        except WorkflowError as e:
            raise HTTPException(422, str(e)) from e

    @api.post("/nodes/{nid}/actions/{action}")
    def post_action(nid: NodeIdPath, action: str) -> dict:
        try:
            return workspace.trigger(nid, action)
        except KeyError as e:
            raise HTTPException(404, "nó inexistente") from e
        except WorkflowError as e:
            raise HTTPException(422, str(e)) from e

    @api.get("/nodes/{nid}/preview.png")
    def get_preview(nid: NodeIdPath) -> Response:
        return _png(workspace, nid, PREVIEW)

    @api.get("/nodes/{nid}/outputs/{port}.png")
    def get_output(nid: NodeIdPath, port: str) -> Response:
        return _png(workspace, nid, OUT + port)

    app.include_router(api)
    return app


def _png(workspace: Workspace, nid: str, slot: str) -> Response:
    try:
        img = workspace.image(nid, slot)
    except KeyError as e:
        raise HTTPException(404, "imagem inexistente") from e
    return Response(encode_png(img), media_type="image/png", headers={"Cache-Control": "no-cache"})
