import numpy as np
import pytest

from pse.core import NodeError
from tests.test_nodes import run

TONS = np.array([[0, 64, 128, 192, 255]], np.uint8)


def test_valores_padrao_nao_mudam_a_imagem():
    out = run("brilho_contraste", {"imagem": TONS})["imagem"]
    assert out.dtype == np.uint8
    assert out.tolist() == TONS.tolist()


def test_brilho_soma_e_satura_em_255():
    out = run("brilho_contraste", {"imagem": TONS}, brilho=100)["imagem"]
    assert out.tolist() == [[100, 164, 228, 255, 255]]


def test_brilho_negativo_satura_em_0():
    out = run("brilho_contraste", {"imagem": TONS}, brilho=-100)["imagem"]
    assert out.tolist() == [[0, 0, 28, 92, 155]]


def test_contraste_estica_os_tons_em_volta_de_128():
    # g = 2·(f − 128) + 128: 64 vira 0, 192 vira 256 (satura em 255), 128 fica igual
    out = run("brilho_contraste", {"imagem": TONS}, contraste=2.0)["imagem"]
    assert out.tolist() == [[0, 0, 128, 255, 255]]


def test_contraste_menor_que_1_comprime_e_arredonda():
    # g = 0,5·(f − 128) + 128: 255 vira 191,5, arredondado para 192
    out = run("brilho_contraste", {"imagem": TONS}, contraste=0.5)["imagem"]
    assert out.tolist() == [[64, 96, 128, 160, 192]]


def test_contraste_zero_deixa_tudo_cinza_medio():
    out = run("brilho_contraste", {"imagem": TONS}, contraste=0.0)["imagem"]
    assert out.tolist() == [[128, 128, 128, 128, 128]]


def test_brilho_contraste_sem_imagem():
    with pytest.raises(NodeError):
        run("brilho_contraste", {"imagem": None})
