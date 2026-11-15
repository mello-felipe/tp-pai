import io
import pathlib

import numpy as np
import pytest
from fastapi.testclient import TestClient
from PIL import Image as PILImage

from pse.api import create_app


@pytest.fixture
def client():
    with TestClient(create_app(), base_url="http://127.0.0.1") as c:  # with: remove a pasta de uploads
        yield c


def test_health(client):
    assert client.get("/api/health").json() == {"ok": True}


def test_node_types_lists_every_node_with_spec(client):
    types = {t["key"]: t for t in client.get("/api/node-types").json()}
    assert {"read_png", "to_grayscale", "display", "save_png"} <= types.keys()
    save = types["save_png"]
    assert save["title"] == "Salvar PNG"
    assert save["inputs"] == ["imagem"] and save["outputs"] == ["imagem"]
    assert [p["name"] for p in save["params"]] == ["name", "path", "save"]
    assert save["params"][2]["kind"] == "action"
    assert types["display"]["preview"] == "imagem"


def test_rejects_unknown_host():
    with TestClient(create_app(), base_url="http://evil.example") as client:
        assert client.get("/api/health").status_code == 400


GRAY = np.arange(12, dtype=np.uint8).reshape(3, 4)


@pytest.fixture
def png(tmp_path):
    path = tmp_path / "in.png"
    PILImage.fromarray(GRAY).save(path)
    return str(path)


def flow(png, save_path=""):
    return {"nodes": [{"id": "r", "type": "read_png", "values": {"path": png}},
                      {"id": "g", "type": "to_grayscale"},
                      {"id": "d", "type": "display"},
                      {"id": "s", "type": "save_png", "values": {"name": "out", "path": save_path}}],
            "links": [{"src": "r", "src_port": "imagem", "dst": "g", "dst_port": "imagem"},
                      {"src": "g", "src_port": "cinza", "dst": "d", "dst_port": "imagem"},
                      {"src": "d", "src_port": "imagem", "dst": "s", "dst_port": "imagem"}]}


def decode(resp):
    assert resp.status_code == 200 and resp.headers["content-type"] == "image/png"
    return np.array(PILImage.open(io.BytesIO(resp.content)))


def test_workflow_runs_and_serves_pngs(client, png):
    body = client.put("/api/workflow", json=flow(png)).json()
    assert body["nodes"]["d"]["error"] is None
    assert body["nodes"]["d"]["preview"]["channels"] == 1
    assert (decode(client.get("/api/nodes/d/preview.png")) == GRAY).all()
    assert (decode(client.get("/api/nodes/r/outputs/imagem.png"))[..., 0] == GRAY).all()


def test_workflow_validation_errors(client):
    bad_type = {"nodes": [{"id": "x", "type": "nope"}]}
    assert client.put("/api/workflow", json=bad_type).status_code == 422
    bad_id = {"nodes": [{"id": "../x", "type": "display"}]}
    assert client.put("/api/workflow", json=bad_id).status_code == 422


def test_missing_images_are_404(client):
    assert client.get("/api/nodes/x/preview.png").status_code == 404
    client.put("/api/workflow", json={"nodes": [{"id": "d", "type": "display"}]})
    assert client.get("/api/nodes/d/outputs/imagem.png").status_code == 404


def test_action_saves_png(client, png, tmp_path):
    client.put("/api/workflow", json=flow(png, str(tmp_path)))
    state = client.post("/api/nodes/s/actions/save").json()
    assert state["error"] is None and state["status"].startswith("salvo em")
    assert (np.array(PILImage.open(tmp_path / "out.png")) == GRAY).all()
    assert client.post("/api/nodes/s/actions/name").status_code == 422
    assert client.post("/api/nodes/ghost/actions/save").status_code == 404


def upload(client, data, name="foto.png"):
    return client.post("/api/images", files={"file": (name, data, "image/png")})


def png_bytes(img=GRAY):
    buf = io.BytesIO()
    PILImage.fromarray(img).save(buf, format="PNG")
    return buf.getvalue()


def test_uploaded_png_feeds_read_png(client):
    resp = upload(client, png_bytes(), "../../segredo/foto.png")
    assert resp.status_code == 201
    body = resp.json()
    assert body["name"] == "foto.png" and (body["width"], body["height"]) == (4, 3)
    assert body["path"].startswith(client.app.state.upload_dir)
    nodes = [{"id": "r", "type": "read_png", "values": {"path": body["path"]}}]
    assert client.put("/api/workflow", json={"nodes": nodes}).json()["nodes"]["r"]["error"] is None


@pytest.mark.parametrize("data", [b"GIF89a....", b"\x89PNG\r\n\x1a\n" + b"lixo" * 10])
def test_upload_rejects_non_png(client, data):
    assert upload(client, data).status_code == 422
    assert not list(pathlib.Path(client.app.state.upload_dir).iterdir())


def test_upload_rejects_large_file():
    with TestClient(create_app(max_upload=100), base_url="http://127.0.0.1") as client:
        assert upload(client, png_bytes(np.zeros((64, 64), np.uint8)) + b"\0" * 200).status_code == 413


def test_upload_dir_removed_on_shutdown():
    with TestClient(create_app(), base_url="http://127.0.0.1") as client:
        folder = pathlib.Path(client.app.state.upload_dir)
        assert folder.is_dir()
    assert not folder.exists()
