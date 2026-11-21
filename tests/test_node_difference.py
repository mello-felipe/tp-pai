import math

import numpy as np
import pytest

from pse.core import NodeError

from .helpers import gray, run

A = gray([[10, 200], [50, 255]])
B = gray([[30, 100], [50, 0]])


def diff(a=A, b=B, **params):
    return run("difference", {"A": a, "B": b}, **params)


def test_absolute_difference():
    assert diff()["imagem"].tolist() == [[20, 100], [0, 255]]


def test_signed_difference_maps_zero_to_128():
    # (A - B) / 2 + 128, arredondado
    assert diff(modo="Com sinal")["imagem"].tolist() == [[118, 178], [128, 255]]  # 255,5 satura em 255


def test_status_reports_mse_and_psnr():
    mse = (20**2 + 100**2 + 0 + 255**2) / 4
    psnr = 10 * math.log10(255**2 / mse)
    assert diff()["_status"] == f"MSE {mse:.2f} · PSNR {psnr:.2f} dB"


def test_identical_images():
    out = diff(b=A)
    assert (out["imagem"] == 0).all()
    assert out["_status"] == "imagens idênticas (MSE 0)"


def test_different_sizes_raise():
    with pytest.raises(NodeError, match="tamanho"):
        diff(b=np.zeros((3, 3), np.uint8))


@pytest.mark.parametrize("port", ["A", "B"])
def test_both_inputs_required(port):
    inputs = {"A": A, "B": B} | {port: None}
    with pytest.raises(NodeError):
        run("difference", inputs)
