import numpy as np
import pytest

from pse.core.window import pad, shifted

IMG = np.array([[1, 2], [3, 4]], np.uint8)


def test_pad_constant():
    assert pad(IMG, 1, value=9).tolist() == [[9, 9, 9, 9], [9, 1, 2, 9], [9, 3, 4, 9], [9, 9, 9, 9]]


def test_pad_replicate_edges():
    assert pad(IMG, 1, replicate=True).tolist() == [[1, 1, 2, 2], [1, 1, 2, 2], [3, 3, 4, 4], [3, 3, 4, 4]]


def test_pad_zero_radius_is_copy():
    out = pad(IMG, 0)
    assert (out == IMG).all() and out is not IMG


def test_shifted_reads_neighbor():
    p = pad(IMG, 1, value=0)
    assert shifted(p, 1, 0, 0).tolist() == IMG.tolist()
    assert shifted(p, 1, 0, 1).tolist() == [[2, 0], [4, 0]]    # vizinho da direita
    assert shifted(p, 1, -1, 0).tolist() == [[0, 0], [1, 2]]   # vizinho de cima


def test_pad_rejects_negative_radius():
    with pytest.raises(ValueError):
        pad(IMG, -1)
