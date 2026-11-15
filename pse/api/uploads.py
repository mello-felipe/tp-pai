"""Upload de PNG pelo navegador.

O navegador não informa o caminho do arquivo escolhido, então o frontend envia
o arquivo e o backend o grava numa pasta temporária. O caminho devolvido vai no
parâmetro `path` do nó Ler PNG, que continua igual.
"""
from __future__ import annotations

import os
import uuid
from typing import BinaryIO

from PIL import Image as PILImage

PNG_SIGNATURE = b"\x89PNG\r\n\x1a\n"
MAX_UPLOAD = 20 * 1024 * 1024  # bytes


class UploadError(ValueError):
    def __init__(self, message: str, status: int = 422) -> None:
        super().__init__(message)
        self.status = status


def store_png(src: BinaryIO, filename: str | None, folder: str, max_bytes: int = MAX_UPLOAD) -> dict:
    """Valida o PNG e grava em `folder` com nome aleatório. Devolve caminho e metadados."""
    data = src.read(max_bytes + 1)
    if len(data) > max_bytes:
        raise UploadError(f"arquivo maior que {max_bytes // (1024 * 1024)} MB", 413)
    if not data.startswith(PNG_SIGNATURE):
        raise UploadError("o arquivo não é um PNG")

    dest = os.path.join(folder, f"{uuid.uuid4().hex}.png")
    with open(dest, "wb") as f:
        f.write(data)
    try:
        with PILImage.open(dest) as im:
            im.verify()  # só confere a integridade; a leitura de verdade é do nó Ler PNG
            width, height = im.size
    except Exception as e:
        os.remove(dest)
        raise UploadError("PNG inválido ou corrompido") from e
    return {"path": dest, "name": os.path.basename(filename or "imagem.png")[:255],
            "width": width, "height": height}
