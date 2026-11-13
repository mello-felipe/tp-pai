"""Modelo de nó do PSE-Image.

Todo arquivo em `pse/nodes/` segue o mesmo esqueleto:

    NODE = NodeSpec(...)                 # definição: título, entradas, saídas, parâmetros
    def execute(inputs, params) -> dict  # algoritmo (equivalente ao execute.ts do n8n)

`NodeType` junta as duas partes; `Node` é uma instância desse tipo no canvas
(guarda os valores dos parâmetros e o último resultado).
"""
from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any, Callable

import numpy as np

Image = np.ndarray  # uint8: (altura, largura) em cinza ou (altura, largura, 3) em RGB


@dataclass(frozen=True)
class Param:
    """Parâmetro configurável, exibido como widget dentro do nó.

    kind:
      "int" | "float"        slider (exige min e max)
      "choice"               combo (exige choices)
      "bool"                 checkbox
      "text"                 campo de texto
      "dir"                  campo de texto + botão para escolher pasta
      "file_open" | "file_save"  botão que abre o seletor de arquivo
      "action"               botão: ao clicar, execute() roda uma vez com
                             params[name] = True (nas execuções normais é False)
    """
    name: str
    label: str
    kind: str
    default: Any = None
    min: float | None = None
    max: float | None = None
    choices: tuple[str, ...] = ()
    hint: str = ""  # texto de exemplo exibido em campos vazios ("text" / "dir")

    def __post_init__(self) -> None:
        if self.kind == "action":
            object.__setattr__(self, "default", False)


@dataclass(frozen=True)
class NodeSpec:
    """Definição de um nó (equivalente à `description` de um nó do n8n)."""
    title: str
    category: str
    description: str = ""
    inputs: tuple[str, ...] = ()               # nomes das portas de entrada
    outputs: tuple[str, ...] = ()              # nomes das portas de saída
    params: tuple[Param, ...] = ()
    preview: str | None = None                 # porta de entrada exibida como imagem no nó


ExecuteFn = Callable[[dict[str, Any], dict[str, Any]], dict[str, Any]]

STATUS_KEY = "_status"  # execute() pode devolver {"_status": "msg"}: aparece em verde no nó


class NodeError(Exception):
    """Erro "esperado" (ex.: entrada faltando). A mensagem aparece no próprio nó."""


def require_image(inputs: dict[str, Any], port: str) -> Image:
    """Devolve a imagem da porta (cinza ou RGB) ou lança NodeError se desconectada."""
    img = inputs[port]
    if img is None:
        raise NodeError(f"entrada '{port}' sem imagem")
    return img


def require_gray(inputs: dict[str, Any], port: str) -> Image:
    """Como require_image, mas exige imagem em tons de cinza (2D)."""
    img = require_image(inputs, port)
    if img.ndim != 2:
        raise NodeError(f"entrada '{port}' é colorida: converta para escala de cinza antes")
    return img


@dataclass(frozen=True)
class NodeType:
    key: str            # nome do arquivo (ex.: "read_png")
    spec: NodeSpec
    execute: ExecuteFn = field(compare=False)

    def create(self) -> "Node":
        return Node(self)


class Node:
    """Instância de um NodeType no workflow."""

    def __init__(self, type_: NodeType) -> None:
        self.type = type_
        self.values: dict[str, Any] = {p.name: p.default for p in type_.spec.params}
        self.error: str | None = None
        self.last_inputs: dict[str, Image | None] = {}
        self.last_outputs: dict[str, Any] = {}
        self._memo: tuple[dict, dict] | None = None

    @property
    def spec(self) -> NodeSpec:
        return self.type.spec

    def run(self, inputs: dict[str, Any]) -> None:
        """Chama execute(). Se as entradas (mesmos objetos) e os parâmetros não
        mudaram desde a última execução, reaproveita o resultado anterior."""
        if self._memo is not None:
            prev_inputs, prev_values = self._memo
            if prev_values == self.values and all(inputs[p] is prev_inputs[p] for p in inputs):
                return
        self.last_inputs = inputs
        self._memo = None
        outputs = self._call(inputs, dict(self.values))
        self.last_outputs = outputs if outputs is not None else {}
        if outputs is not None:
            self._memo = (inputs, dict(self.values))

    def trigger(self, action: str) -> None:
        """Executa uma vez com o parâmetro "action" ligado (ex.: botão Salvar),
        usando as últimas entradas. Em caso de erro, mantém as saídas atuais."""
        inputs = {p: self.last_inputs.get(p) for p in self.spec.inputs}
        outputs = self._call(inputs, {**self.values, action: True})
        if outputs is not None:
            self.last_outputs = outputs

    @property
    def status(self) -> str:
        return self.last_outputs.get(STATUS_KEY, "")

    def _call(self, inputs: dict[str, Any], values: dict[str, Any]) -> dict[str, Any] | None:
        """Chama execute(); em erro, guarda a mensagem em self.error e devolve None."""
        self.error = None
        try:
            return self.type.execute(inputs, values) or {}
        except NodeError as e:
            self.error = str(e)
        except Exception as e:  # bug num nó não derruba o app
            self.error = f"{type(e).__name__}: {e}"
        return None
