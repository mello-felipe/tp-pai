import pathlib

import numpy as np
import pytest
from PIL import Image as PILImage

from pse.core import NodeError, require_gray
from pse.api.values import merge_values
from pse.nodes import discover

TYPES = discover()
KINDS = {"int", "float", "choice", "bool", "text", "dir", "file_open", "file_save", "kernel", "action"}


def run(key, inputs=None, **params):
    t = TYPES[key]
    values = {p.name: p.default for p in t.spec.params} | params
    return t.execute(inputs or {}, values)


@pytest.mark.parametrize("key", sorted(TYPES))
def test_node_skeleton_is_valid(key):
    """Todo arquivo em pse/nodes/ precisa seguir o esqueleto padrão."""
    spec = TYPES[key].spec
    assert spec.title and spec.category
    assert isinstance(spec.inputs, tuple) and isinstance(spec.outputs, tuple)
    assert len(set(spec.inputs)) == len(spec.inputs)
    assert len(set(spec.outputs)) == len(spec.outputs)
    assert not any(o.startswith("_") for o in spec.outputs), "portas com '_' são reservadas"
    for p in spec.params:
        assert p.kind in KINDS, f"{key}: tipo de parâmetro desconhecido {p.kind}"
        if p.kind in ("int", "float"):
            assert p.min is not None and p.max is not None
        if p.kind == "choice":
            assert p.default in p.choices
        if p.kind == "kernel":
            merge_values(spec, {p.name: p.default})  # padrão precisa ser uma matriz válida


def test_expected_nodes_exist():
    assert {"read_png", "to_grayscale", "display", "save_png"} <= TYPES.keys()
    assert "_template" not in TYPES


RGB = np.array([[[255, 0, 0], [0, 255, 0], [0, 0, 255], [255, 255, 255]]], np.uint8)


def test_read_png_keeps_colors(tmp_path):
    path = tmp_path / "c.png"
    PILImage.fromarray(RGB).save(path)
    out = run("read_png", path=str(path))["imagem"]
    assert out.dtype == np.uint8 and out.shape == (1, 4, 3)
    assert (out == RGB).all()


def test_read_png_without_file():
    with pytest.raises(NodeError):
        run("read_png")


def test_to_grayscale_luminance():
    out = run("to_grayscale", {"imagem": RGB})["cinza"]
    assert out.dtype == np.uint8 and out.tolist() == [[76, 150, 29, 255]]


def test_to_grayscale_passes_gray_through():
    gray = np.zeros((2, 2), np.uint8)
    assert run("to_grayscale", {"imagem": gray})["cinza"] is gray


def test_require_gray_rejects_color():
    assert require_gray({"i": np.zeros((2, 2), np.uint8)}, "i").shape == (2, 2)
    with pytest.raises(NodeError, match="colorida"):
        require_gray({"i": RGB}, "i")
    with pytest.raises(NodeError):
        require_gray({"i": None}, "i")


@pytest.fixture
def root(tmp_path, monkeypatch):
    """Raiz do projeto falsa, para não gravar no repositório."""
    import pse.nodes.save_png as save_png
    monkeypatch.setattr(save_png, "project_root", lambda: str(tmp_path))
    return tmp_path


GRAY = np.arange(256, dtype=np.uint8).reshape(16, 16)


def test_save_png_only_saves_when_triggered(root):
    out = run("save_png", {"imagem": GRAY})
    assert out == {"imagem": GRAY} and not (root / "img").exists()


def test_save_png_default_dir_is_img_in_project_root(root):
    out = run("save_png", {"imagem": GRAY}, name="teste", save=True)
    assert (root / "img" / "teste.png").exists()
    assert out["_status"] == f"salvo em {pathlib.Path('img', 'teste.png')}"


@pytest.mark.parametrize("img", [GRAY, RGB])
def test_save_png_roundtrip_gray_and_color(root, img):
    run("save_png", {"imagem": img}, name="x.png", save=True)
    back = run("read_png", path=str(root / "img" / "x.png"))["imagem"]
    if img.ndim == 2:
        back = run("to_grayscale", {"imagem": back})["cinza"]
    assert (back == img).all()


def test_save_png_custom_absolute_and_relative_path(root, tmp_path_factory):
    other = tmp_path_factory.mktemp("outra")
    run("save_png", {"imagem": GRAY}, name="a", path=str(other), save=True)
    assert (other / "a.png").exists()
    (root / "saidas").mkdir()
    run("save_png", {"imagem": GRAY}, name="b", path="saidas", save=True)
    assert (root / "saidas" / "b.png").exists()


@pytest.mark.parametrize("params, msg", [
    ({"name": "  "}, "nome"),
    ({"name": "a/b"}, "barras"),
    ({"name": "a", "path": "/nao/existe/mesmo"}, "não existe"),
])
def test_save_png_errors(root, params, msg):
    with pytest.raises(NodeError, match=msg):
        run("save_png", {"imagem": GRAY}, save=True, **params)


@pytest.mark.parametrize("img", [np.zeros((3, 3), np.uint8), RGB])
def test_display_passes_image_through(img):
    assert run("display", {"imagem": img})["imagem"] is img


def test_display_without_image():
    with pytest.raises(NodeError):
        run("display", {"imagem": None})
