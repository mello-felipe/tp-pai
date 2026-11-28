import numpy as np
import pytest

from pse.core import NodeError
from tests.test_nodes import run


def test_diferenca_absoluta_pixel_a_pixel():
    a = np.array([[10, 200, 50]], np.uint8)
    b = np.array([[30, 100, 50]], np.uint8)
    out = run("diferenca", {"A": a, "B": b})
    assert out["imagem"].dtype == np.uint8
    assert out["imagem"].tolist() == [[20, 100, 0]]  # 10 − 30 = −20 vira 20 (sem "dar a volta")
    assert out["_status"] == "diferença média: 40.00"


def test_diferenca_nao_depende_da_ordem():
    a = np.array([[10, 200]], np.uint8)
    b = np.array([[30, 100]], np.uint8)
    ab = run("diferenca", {"A": a, "B": b})["imagem"]
    ba = run("diferenca", {"A": b, "B": a})["imagem"]
    assert (ab == ba).all()


def test_imagens_iguais_dao_imagem_preta():
    img = np.arange(256, dtype=np.uint8).reshape(16, 16)
    out = run("diferenca", {"A": img, "B": img})
    assert (out["imagem"] == 0).all()
    assert out["_status"] == "diferença média: 0.00"


def test_diferenca_exige_mesmo_tamanho():
    a = np.zeros((2, 3), np.uint8)
    b = np.zeros((3, 2), np.uint8)
    with pytest.raises(NodeError, match="tamanhos diferentes"):
        run("diferenca", {"A": a, "B": b})


def test_diferenca_sem_uma_das_imagens():
    with pytest.raises(NodeError):
        run("diferenca", {"A": np.zeros((2, 2), np.uint8), "B": None})
