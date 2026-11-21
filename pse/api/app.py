"""Aplicação FastAPI.

Roda só em 127.0.0.1. Em desenvolvimento, o Vite repassa /api para cá
(mesma origem), então não há CORS. O TrustedHostMiddleware recusa outros
Hosts (proteção contra DNS rebinding).
"""
from __future__ import annotations

import shutil
import tempfile
from contextlib import asynccontextmanager
from typing import Annotated

from fastapi import APIRouter, FastAPI, HTTPException, Path, Response, UploadFile
from fastapi.middleware.trustedhost import TrustedHostMiddleware
from fastapi.staticfiles import StaticFiles

from ..core import NodeType
from ..nodes import discover
from .images import encode_png
from .schemas import ID_PATTERN, WorkflowIn, node_type_json
from .uploads import MAX_UPLOAD, UploadError, store_png
from .values import WorkflowError
from .workspace import OUT, PREVIEW, Workspace

ALLOWED_HOSTS = ["127.0.0.1", "localhost"]
NodeIdPath = Annotated[str, Path(pattern=ID_PATTERN)]


def create_app(types: dict[str, NodeType] | None = None, max_upload: int = MAX_UPLOAD,
               static_dir: str | None = None) -> FastAPI:
    types = discover() if types is None else types
    workspace = Workspace(types)
    upload_dir = tempfile.mkdtemp(prefix="pse-image-")

    @asynccontextmanager
    async def lifespan(_app: FastAPI):
        yield
        shutil.rmtree(upload_dir, ignore_errors=True)  # uploads só valem enquanto o app roda

    app = FastAPI(title="PSE-Image", lifespan=lifespan)
    app.add_middleware(TrustedHostMiddleware, allowed_hosts=ALLOWED_HOSTS)
    app.state.workspace = workspace
    app.state.upload_dir = upload_dir

    api = APIRouter(prefix="/api")

    @api.get("/health")
    def health() -> dict:
        return {"ok": True}

    @api.get("/node-types")
    def node_types() -> list[dict]:
        return [node_type_json(t) for t in sorted(types.values(), key=lambda t: t.key)]

    @api.post("/images", status_code=201)
    def post_image(file: UploadFile) -> dict:
        try:
            return store_png(file.file, file.filename, upload_dir, max_upload)
        except UploadError as e:
            raise HTTPException(e.status, str(e)) from e

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
    if static_dir is not None:
        app.mount("/", StaticFiles(directory=static_dir, html=True), name="frontend")  # depois do /api
    return app


def _png(workspace: Workspace, nid: str, slot: str) -> Response:
    try:
        img = workspace.image(nid, slot)
    except KeyError as e:
        raise HTTPException(404, "imagem inexistente") from e
    return Response(encode_png(img), media_type="image/png", headers={"Cache-Control": "no-cache"})
