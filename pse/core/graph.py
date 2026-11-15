"""Grafo do workflow: guarda nós e ligações e executa em ordem topológica."""
from __future__ import annotations

from collections import deque
from typing import NamedTuple

from .node import Node


NodeId = int | str  # gerado pelo Graph (int) ou vindo de fora, ex.: id do React Flow (str)


class Link(NamedTuple):
    src: NodeId    # id do nó de origem
    src_port: str  # porta de saída
    dst: NodeId    # id do nó de destino
    dst_port: str  # porta de entrada


class Graph:
    def __init__(self) -> None:
        self.nodes: dict[NodeId, Node] = {}
        self.links: set[Link] = set()
        self._next_id = 1

    # ---------------------------------------------------------------- edição
    def add_node(self, node: Node, nid: NodeId | None = None) -> NodeId:
        """Adiciona o nó com o id dado (ou um id inteiro novo) e devolve o id."""
        if nid is None:
            while self._next_id in self.nodes:
                self._next_id += 1
            nid = self._next_id
            self._next_id += 1
        elif nid in self.nodes:
            raise ValueError(f"id de nó repetido: {nid!r}")
        self.nodes[nid] = node
        return nid

    def remove_node(self, nid: NodeId) -> list[Link]:
        """Remove o nó e devolve as ligações removidas junto com ele."""
        removed = [l for l in self.links if nid in (l.src, l.dst)]
        self.links.difference_update(removed)
        del self.nodes[nid]
        return removed

    def connect(self, link: Link) -> Link | None:
        """Cria a ligação. Uma entrada aceita só uma ligação: se já houver,
        a antiga é substituída e devolvida. Uma saída pode alimentar vários nós.
        Lança ValueError se a ligação criar um ciclo ou for inválida."""
        src, dst = self.nodes[link.src], self.nodes[link.dst]
        if link.src_port not in src.spec.outputs or link.dst_port not in dst.spec.inputs:
            raise ValueError("porta inválida")
        if link.src == link.dst or self._reaches(link.dst, link.src):
            raise ValueError("ligação criaria um ciclo")
        old = self.input_link(link.dst, link.dst_port)
        if old:
            self.links.discard(old)
        self.links.add(link)
        return old

    def disconnect(self, link: Link) -> None:
        self.links.discard(link)

    def input_link(self, nid: NodeId, port: str) -> Link | None:
        return next((l for l in self.links if l.dst == nid and l.dst_port == port), None)

    def _reaches(self, start: NodeId, target: NodeId) -> bool:
        """Existe caminho start -> ... -> target?"""
        stack, seen = [start], set()
        while stack:
            n = stack.pop()
            if n == target:
                return True
            if n in seen:
                continue
            seen.add(n)
            stack.extend(l.dst for l in self.links if l.src == n)
        return False

    # -------------------------------------------------------------- execução
    def topological_order(self) -> list[NodeId]:
        indeg = {nid: 0 for nid in self.nodes}
        for l in self.links:
            indeg[l.dst] += 1
        queue = deque(sorted((n for n, d in indeg.items() if d == 0), key=lambda n: (isinstance(n, str), n)))
        order = []
        while queue:
            n = queue.popleft()
            order.append(n)
            for l in self.links:
                if l.src == n:
                    indeg[l.dst] -= 1
                    if indeg[l.dst] == 0:
                        queue.append(l.dst)
        return order

    def evaluate(self) -> None:
        """Executa o fluxo inteiro, em ordem topológica. Resultados ficam em
        node.last_outputs; erros em node.error (e as saídas viram vazias)."""
        for nid in self.topological_order():
            node = self.nodes[nid]
            inputs = {}
            for port in node.spec.inputs:
                l = self.input_link(nid, port)
                inputs[port] = self.nodes[l.src].last_outputs.get(l.src_port) if l else None
            node.run(inputs)
