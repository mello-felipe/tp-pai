import numpy as np
import pytest

from pse.core import NodeError
from tests.test_nodes import run


def test_complemento_inverte_os_tons():
    img = np.array([[0, 100, 255]], np.uint8)
    out = run("complemento", {"imagem": img})["imagem"]
    assert out.dtype == np.uint8
    assert out.tolist() == [[255, 155, 0]]


def test_complemento_duas_vezes_volta_a_original():
    img = np.arange(256, dtype=np.uint8).reshape(16, 16)
    uma_vez = run("complemento", {"imagem": img})["imagem"]
    duas_vezes = run("complemento", {"imagem": uma_vez})["imagem"]
    assert (duas_vezes == img).all()


def test_complemento_sem_imagem():
    with pytest.raises(NodeError):
        run("complemento", {"imagem": None})
