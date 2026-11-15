"""Workspace: um Graph persistente que se ajusta ao fluxo enviado pelo frontend.

Os objetos Node são mantidos entre requisições (pelo id do React Flow), então
o cache de Node.run continua valendo: só reexecuta o que mudou. Cada imagem
exposta ganha uma "versão", usada pelo frontend na URL para recarregar só as
miniaturas que mudaram.
"""
from __future__ import annotations

import itertools
import threading
from typing import Any

import numpy as np

from ..core import Graph, Link, NodeType
from .images import image_meta
from .schemas import LinkIn, NodeIn, WorkflowIn
from .values import WorkflowError, merge_values

PREVIEW = "preview"   # slot da imagem exibida no nó (entrada NodeSpec.preview)
OUT = "out:"          # prefixo dos slots das portas de saída


class Workspace:
    def __init__(self, types: dict[str, NodeType]) -> None:
        self.types = types
        self.graph = Graph()
        self._lock = threading.Lock()
        self._versions = itertools.count(1)
        self._images: dict[tuple[str, str], tuple[np.ndarray, int]] = {}

    # ------------------------------------------------------------- operações
    def sync(self, wf: WorkflowIn) -> dict[str, Any]:
        """Ajusta o grafo ao fluxo recebido, executa e devolve o estado dos nós."""
        with self._lock:
            self._sync_nodes(wf.nodes)
            rejected = self._sync_links(wf.links)
            self.graph.evaluate()
            return {"nodes": {nid: self._state(nid) for nid in self.graph.nodes},
                    "rejected_links": rejected}

    def trigger(self, nid: str, action: str) -> dict[str, Any]:
        """Dispara um parâmetro "action" (ex.: Salvar) e devolve o estado do nó."""
        with self._lock:
            node = self.graph.nodes[nid]  # KeyError: nó inexistente
            if not any(p.name == action and p.kind == "action" for p in node.spec.params):
                raise WorkflowError(f"ação desconhecida: {action}")
            node.trigger(action)
            return self._state(nid)

    def image(self, nid: str, slot: str) -> np.ndarray:
        """Última imagem exposta no slot. KeyError se não houver."""
        with self._lock:
            return self._images[(nid, slot)][0]

    # ----------------------------------------------------------- sincronização
    def _sync_nodes(self, nodes: list[NodeIn]) -> None:
        wanted = {n.id: n for n in nodes}
        if len(wanted) != len(nodes):
            raise WorkflowError("ids de nó repetidos")
        unknown = sorted({n.type for n in nodes} - self.types.keys())
        if unknown:
            raise WorkflowError(f"tipo de nó desconhecido: {', '.join(unknown)}")
        merged = {n.id: merge_values(self.types[n.type].spec, n.values) for n in nodes}

        stale = [nid for nid, node in self.graph.nodes.items()
                 if nid not in wanted or node.type.key != wanted[nid].type]
        for nid in stale:
            self.graph.remove_node(nid)
            self._images = {k: v for k, v in self._images.items() if k[0] != nid}
        for n in nodes:
            if n.id not in self.graph.nodes:
                self.graph.add_node(self.types[n.type].create(), n.id)
            self.graph.nodes[n.id].values = merged[n.id]

    def _sync_links(self, links: list[LinkIn]) -> list[dict[str, Any]]:
        wanted = [Link(l.src, l.src_port, l.dst, l.dst_port) for l in links]
        for old in self.graph.links - set(wanted):
            self.graph.disconnect(old)
        rejected, taken = [], set()
        for link in wanted:
            error = self._link_error(link, taken)
            if error is None:
                try:
                    self.graph.connect(link)
                except ValueError as e:
                    error = str(e)
            if error is None:
                taken.add((link.dst, link.dst_port))
            else:
                rejected.append({**link._asdict(), "error": error})
        return rejected

    def _link_error(self, link: Link, taken: set) -> str | None:
        if link.src not in self.graph.nodes or link.dst not in self.graph.nodes:
            return "nó inexistente"
        if (link.dst, link.dst_port) in taken:
            return "entrada já ligada"
        return None

    # ------------------------------------------------------------------ estado
    def _state(self, nid: str) -> dict[str, Any]:
        node = self.graph.nodes[nid]
        spec = node.spec
        outputs = {p: self._expose(nid, OUT + p, node.last_outputs.get(p)) for p in spec.outputs}
        preview = self._expose(nid, PREVIEW, node.last_inputs.get(spec.preview)) if spec.preview else None
        return {"error": node.error, "status": node.status, "outputs": outputs, "preview": preview}

    def _expose(self, nid: str, slot: str, img: Any) -> dict[str, Any] | None:
        """Registra a imagem do slot; a versão só muda se o objeto mudou."""
        key = (nid, slot)
        if not isinstance(img, np.ndarray):
            self._images.pop(key, None)
            return None
        current = self._images.get(key)
        version = current[1] if current is not None and current[0] is img else next(self._versions)
        self._images[key] = (img, version)
        return image_meta(img, version)
