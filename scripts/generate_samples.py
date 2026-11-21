"""Uso: python scripts/generate_samples.py"""
from __future__ import annotations

import os

import numpy as np
from PIL import Image

SIZE = 256
OUT = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "samples")
RNG = np.random.default_rng(42)

yy, xx = np.mgrid[0:SIZE, 0:SIZE]


def disk(cy: int, cx: int, r: int) -> np.ndarray:
    return (yy - cy) ** 2 + (xx - cx) ** 2 <= r * r


def rect(y0: int, x0: int, y1: int, x1: int) -> np.ndarray:
    return (yy >= y0) & (yy < y1) & (xx >= x0) & (xx < x1)


def scene() -> np.ndarray:
    img = np.full((SIZE, SIZE), 40.0)
    img[disk(80, 80, 45)] = 200
    img[rect(140, 30, 220, 120)] = 140
    img[disk(170, 180, 50)] = 240
    return img


def save(name: str, img: np.ndarray) -> None:
    Image.fromarray(np.clip(np.rint(img), 0, 255).astype(np.uint8)).save(os.path.join(OUT, name))


def main() -> None:
    os.makedirs(OUT, exist_ok=True)
    base = scene()

    save("gradiente.png", np.tile(np.arange(SIZE), (SIZE, 1)))
    save("baixo_contraste.png", 100 + (base - 40) * 50 / 200)  # tons entre 100 e 150
    save("ruido_gaussiano.png", base + RNG.normal(0, 25, base.shape))

    salt_pepper = base.copy()
    noise = RNG.random(base.shape)
    salt_pepper[noise < 0.05] = 0
    salt_pepper[noise > 0.95] = 255
    save("ruido_sal_pimenta.png", salt_pepper)

    checker = ((yy // 32 + xx // 32) % 2) * 255
    save("xadrez.png", checker)

    shapes = np.zeros((SIZE, SIZE))
    shapes[disk(70, 70, 40) | rect(140, 40, 210, 110) | disk(170, 180, 45)] = 255
    shapes[disk(70, 70, 8) | rect(165, 65, 185, 85)] = 0        # buracos (fechamento)
    specks = RNG.random(shapes.shape) < 0.01
    shapes[specks] = 255 - shapes[specks]                        # pontos soltos (abertura)
    save("formas_binarias.png", shapes)

    save("cena_a.png", base)
    moved = base.copy()
    moved[disk(80, 80, 45)] = 40
    moved[disk(80, 150, 45)] = 200                               # círculo deslocado
    moved[rect(30, 200, 60, 240)] = 255                          # objeto novo
    save("cena_b.png", moved)

    rgb = np.zeros((SIZE, SIZE, 3))
    rgb[..., 2] = 60
    rgb[disk(80, 80, 45)] = (220, 40, 40)
    rgb[rect(140, 30, 220, 120)] = (40, 200, 60)
    rgb[disk(170, 180, 50)] = (250, 220, 40)
    save("colorida.png", rgb)


if __name__ == "__main__":
    main()
