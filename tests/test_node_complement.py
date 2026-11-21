import numpy as np
import pytest

from pse.core import NodeError

from .helpers import gray, run


def test_complement_inverts_gray_levels():
    out = run("complement", {"imagem": gray([[0, 1, 128], [200, 254, 255]])})["imagem"]
    assert out.dtype == np.uint8
    assert out.tolist() == [[255, 254, 127], [55, 1, 0]]


def test_complement_twice_is_identity():
    img = np.arange(256, dtype=np.uint8).reshape(16, 16)
    once = run("complement", {"imagem": img})["imagem"]
    assert (run("complement", {"imagem": once})["imagem"] == img).all()


@pytest.mark.parametrize("img", [None, np.zeros((2, 2, 3), np.uint8)])
def test_complement_requires_gray_image(img):
    with pytest.raises(NodeError):
        run("complement", {"imagem": img})
