import numpy as np
import pytest

from pse.core import NodeError
from pse.nodes.morphology import element

from .helpers import run


def morph(img, **params):
    return run("morphology", {"imagem": np.asarray(img, np.uint8)}, **params)["imagem"]


def dot(n=5):
    img = np.zeros((n, n), np.uint8)
    img[n // 2, n // 2] = 255
    return img


def test_elements():
    assert element("Quadrado", 3).sum() == 9
    assert element("Cruz", 3).tolist() == [[0, 1, 0], [1, 1, 1], [0, 1, 0]]
    assert element("Cruz", 5).sum() == 9
    assert element("Disco", 5).tolist() == [
        [0, 0, 1, 0, 0],
        [0, 1, 1, 1, 0],
        [1, 1, 1, 1, 1],
        [0, 1, 1, 1, 0],
        [0, 0, 1, 0, 0],
    ]


def test_dilation_stamps_element_shape():
    out = morph(dot(), operacao="Dilatação", elemento="Cruz", tamanho="3×3")
    assert (out == 255).sum() == 5 and out[1, 2] == 255 and out[1, 1] == 0


def test_erosion_shrinks_square():
    img = np.zeros((5, 5), np.uint8)
    img[1:4, 1:4] = 255
    out = morph(img, operacao="Erosão", elemento="Quadrado", tamanho="3×3")
    assert (out == 255).sum() == 1 and out[2, 2] == 255


def test_border_does_not_erode_full_image():
    full = np.full((4, 4), 255, np.uint8)
    assert (morph(full, operacao="Erosão") == 255).all()


def test_opening_removes_isolated_pixel_and_keeps_block():
    img = np.zeros((9, 9), np.uint8)
    img[1:6, 1:6] = 255
    img[7, 7] = 255
    out = morph(img, operacao="Abertura", elemento="Quadrado", tamanho="3×3")
    assert out[7, 7] == 0 and (out[1:6, 1:6] == 255).all()


def test_closing_fills_small_hole():
    img = np.full((7, 7), 255, np.uint8)
    img[3, 3] = 0
    assert (morph(img, operacao="Fechamento", elemento="Quadrado", tamanho="3×3") == 255).all()


def test_gray_erosion_is_neighborhood_minimum():
    img = np.array([[9, 8, 7], [6, 5, 4], [3, 2, 1]], np.uint8)
    assert morph(img, operacao="Erosão", elemento="Quadrado", tamanho="3×3")[1, 1] == 1
    assert morph(img, operacao="Dilatação", elemento="Quadrado", tamanho="3×3")[1, 1] == 9


def test_requires_gray():
    with pytest.raises(NodeError):
        morph(np.zeros((2, 2, 3)))
