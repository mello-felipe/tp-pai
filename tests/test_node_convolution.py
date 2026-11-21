import numpy as np
import pytest

from pse.core import NodeError

from .helpers import gray, run

IDENTITY = [[0, 0, 0], [0, 1, 0], [0, 0, 0]]
MEAN = [[1, 1, 1], [1, 1, 1], [1, 1, 1]]


def conv(img, **params):
    return run("convolution", {"imagem": np.asarray(img, np.uint8)}, **params)["imagem"]


def test_identity_keeps_image():
    img = np.arange(25, dtype=np.uint8).reshape(5, 5)
    assert (conv(img, mascara=IDENTITY) == img).all()


def test_mean_with_zero_border():
    img = gray([[0, 0, 0], [0, 90, 0], [0, 0, 0]])
    # toda janela 3x3 contém o pixel central: 90 / 9 = 10
    assert (conv(img, mascara=MEAN, borda="Zero") == 10).all()


def test_replicate_border_keeps_constant_image():
    assert (conv(np.full((4, 4), 77, np.uint8), mascara=MEAN, borda="Replicar") == 77).all()


def test_convolution_flips_the_mask():
    # peso à esquerda do centro: na convolução lê o vizinho da direita
    k = [[0, 0, 0], [1, 0, 0], [0, 0, 0]]
    out = conv(gray([[10, 20, 30]]), mascara=k, normalizar=False, borda="Zero")
    assert out.tolist() == [[20, 30, 0]]


def test_zero_sum_mask_is_not_normalized():
    lap = [[0, 1, 0], [1, -4, 1], [0, 1, 0]]
    img = gray([[0, 0, 0], [0, 50, 0], [0, 0, 0]])
    out = conv(img, mascara=lap, saida="Valor absoluto", borda="Zero")
    assert out.tolist() == [[0, 50, 0], [50, 200, 50], [0, 50, 0]]
    assert conv(img, mascara=lap, saida="Limitar 0–255", borda="Zero")[1, 1] == 0  # -200 satura


def test_minmax_output_spans_full_range():
    img = gray([[0, 0, 0], [0, 50, 0], [0, 0, 0]])
    lap = [[0, 1, 0], [1, -4, 1], [0, 1, 0]]
    out = conv(img, mascara=lap, saida="Normalizar mín–máx", borda="Zero")
    assert out.min() == 0 and out.max() == 255 and out[1, 1] == 0


def test_median_removes_salt_noise():
    img = np.full((3, 3), 10, np.uint8)
    img[1, 1] = 255
    assert (conv(img, operacao="Mediana", mascara=MEAN) == 10).all()


def test_median_5x5_hand_computed():
    img = np.arange(25, dtype=np.uint8).reshape(5, 5)
    k5 = [[0] * 5 for _ in range(5)]
    assert conv(img, operacao="Mediana", mascara=k5)[2, 2] == 12


def test_requires_gray():
    with pytest.raises(NodeError):
        conv(np.zeros((2, 2, 3)))
