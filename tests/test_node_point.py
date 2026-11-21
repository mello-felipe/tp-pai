import numpy as np
import pytest

from pse.core import NodeError

from .helpers import gray, run

IMG = gray([[0, 64, 128], [192, 250, 255]])


def point(**params):
    return run("brightness_contrast", {"imagem": IMG}, **params)["imagem"]


def test_defaults_keep_image():
    assert (point() == IMG).all()


def test_brightness_adds_and_saturates():
    assert point(brilho=10).tolist() == [[10, 74, 138], [202, 255, 255]]
    assert point(brilho=-70).tolist() == [[0, 0, 58], [122, 180, 185]]


def test_contrast_scales_around_middle_gray():
    # g = 2 * (f - 128) + 128
    assert point(contraste=2.0).tolist() == [[0, 0, 128], [255, 255, 255]]
    # g = 0.5 * (f - 128) + 128, arredondado
    assert point(contraste=0.5).tolist() == [[64, 96, 128], [160, 189, 192]]


def test_contrast_zero_gives_flat_gray_plus_brightness():
    assert (point(contraste=0.0, brilho=-28) == 100).all()


def test_output_is_uint8_and_input_untouched():
    before = IMG.copy()
    out = point(brilho=50, contraste=1.5)
    assert out.dtype == np.uint8 and out.shape == IMG.shape
    assert (IMG == before).all()


def test_requires_gray():
    with pytest.raises(NodeError):
        run("brightness_contrast", {"imagem": np.zeros((2, 2, 3), np.uint8)})
