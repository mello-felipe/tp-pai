import numpy as np
import pytest

from pse.core import NodeError
from pse.nodes.threshold import otsu_threshold

from .helpers import gray, run

IMG = gray([[10, 20, 30], [200, 210, 220]])


def seg(img=IMG, **params):
    return run("threshold", {"imagem": img}, **params)


def test_manual_threshold_is_strictly_greater():
    out = seg(metodo="Manual", limiar=20)
    assert out["imagem"].tolist() == [[0, 0, 255], [255, 255, 255]]
    assert out["_status"] == "limiar = 20"


def test_invert_swaps_foreground():
    out = seg(metodo="Manual", limiar=20, inverter=True)["imagem"]
    assert out.tolist() == [[255, 255, 0], [0, 0, 0]]


def test_otsu_splits_two_clusters():
    out = seg(metodo="Otsu")
    assert out["imagem"].tolist() == [[0, 0, 0], [255, 255, 255]]
    t = int(out["_status"].split("= ")[1].split()[0])
    assert 30 <= t < 200


def test_otsu_hand_computed():
    # metade dos pixels em 50 e metade em 150: qualquer t em [50, 150) separa;
    # a variância entre classes é máxima (e igual) nesse intervalo -> primeiro máximo
    img = gray([[50, 50, 150, 150]])
    assert otsu_threshold(img) == 50


def test_otsu_constant_image():
    assert otsu_threshold(np.full((3, 3), 77, np.uint8)) == 77
    assert (seg(np.full((3, 3), 77, np.uint8), metodo="Otsu")["imagem"] == 0).all()


def test_requires_gray():
    with pytest.raises(NodeError):
        seg(np.zeros((2, 2, 3), np.uint8))
