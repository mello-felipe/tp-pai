import pytest
from fastapi.testclient import TestClient

from pse.api import create_app


@pytest.fixture
def client():
    return TestClient(create_app(), base_url="http://127.0.0.1")


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
    client = TestClient(create_app(), base_url="http://evil.example")
    assert client.get("/api/health").status_code == 400
