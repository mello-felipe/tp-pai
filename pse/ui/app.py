"""Interface gráfica (Dear PyGui): paleta de blocos + canvas de nós.

A UI só espelha o `Graph` do core: toda mudança (nó, ligação, parâmetro)
altera o grafo e chama `run()`, que reexecuta o fluxo e atualiza os nós.
"""
from __future__ import annotations

import os
import sys

import dearpygui.dearpygui as dpg
import numpy as np

from ..core import Graph, Link, NodeType, Param
from ..nodes import by_category, discover

THUMB_SIDE = 220  # tamanho máximo da miniatura dentro do nó
NODE_WIDGET_W = 150
ERROR_COLOR = (255, 110, 110)
OK_COLOR = (130, 220, 130)


def resource_path(rel: str) -> str:
    """Caminho de um recurso, funcionando também no executável do PyInstaller."""
    base = getattr(sys, "_MEIPASS", os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))
    return os.path.join(base, rel)


def thumbnail(img: np.ndarray, max_side: int) -> np.ndarray:
    """Reduz por vizinho mais próximo (só para exibição). Aceita cinza ou RGB."""
    h, w = img.shape[:2]
    scale = max(h, w) / max_side
    if scale <= 1:
        return img
    nh, nw = max(1, int(h / scale)), max(1, int(w / scale))
    rows = (np.arange(nh) * h / nh).astype(int)
    cols = (np.arange(nw) * w / nw).astype(int)
    return img[rows[:, None], cols]


def to_rgba(img: np.ndarray) -> np.ndarray:
    """Cinza (h, w) ou RGB (h, w, 3) uint8 -> buffer RGBA float32 achatado (textura do DPG)."""
    rgb = img if img.ndim == 3 else img[..., None]  # cinza: repete o canal em R, G e B
    rgba = np.empty((*img.shape[:2], 4), dtype=np.float32)
    rgba[..., :3] = rgb.astype(np.float32) / 255.0
    rgba[..., 3] = 1.0
    return rgba.ravel()


class App:
    def __init__(self) -> None:
        self.graph = Graph()
        self.types = discover()
        self.node_items: dict[int, int] = {}                 # id no grafo -> item dpg
        self.attr_ports: dict[int, tuple[int, str, bool]] = {}  # atributo dpg -> (nó, porta, é_saída)
        self.port_attrs: dict[tuple[int, str, bool], int] = {}
        self.link_items: dict[Link, int] = {}                # ligação -> item dpg
        self.status: dict[int, int] = {}                     # nó -> texto de status
        self.previews: dict[int, dict] = {}                  # nó -> widgets de miniatura
        self.file_labels: dict[tuple[int, str], int] = {}
        self.last_dir = os.getcwd()
        self._spawn = 0
        self._trash: list[int] = []  # texturas a apagar com atraso (podem estar em uso no frame)

    # ================================================================ montagem
    def build(self) -> None:
        dpg.create_context()
        self._setup_font()
        self.textures = dpg.add_texture_registry()

        with dpg.window(tag="main"):
            with dpg.group(horizontal=True):
                with dpg.child_window(width=220):
                    dpg.add_text("Blocos")
                    dpg.add_separator()
                    for cat, types in by_category(self.types).items():
                        with dpg.collapsing_header(label=cat, default_open=True):
                            for t in types:
                                btn = dpg.add_button(label=t.spec.title, width=-1, user_data=t,
                                                     callback=lambda s, a, u: self.add_node(u))
                                if t.spec.description:
                                    with dpg.tooltip(btn):
                                        dpg.add_text(t.spec.description, wrap=300)
                    dpg.add_spacer(height=10)
                    dpg.add_separator()
                    dpg.add_text(
                        "• Clique num bloco para adicioná-lo\n"
                        "• Arraste de uma saída até uma entrada para ligar\n"
                        "• Selecione nós/ligações e aperte Delete para remover\n"
                        "• Ctrl+clique num slider para digitar o valor",
                        wrap=200, color=(170, 170, 170))
                with dpg.node_editor(tag="editor", callback=self.on_link, delink_callback=self.on_delink,
                                     minimap=True, minimap_location=dpg.mvNodeMiniMap_Location_BottomRight):
                    pass

        with dpg.handler_registry():
            dpg.add_key_press_handler(dpg.mvKey_Delete, callback=self.delete_selected)

        # fluxo inicial de exemplo
        src = self.add_node(self.types["read_png"], (40, 60), run=False)
        gray = self.add_node(self.types["to_grayscale"], (320, 60), run=False)
        dst = self.add_node(self.types["display"], (560, 60), run=False)
        self.connect(Link(src, "imagem", gray, "imagem"))
        self.connect(Link(gray, "cinza", dst, "imagem"))

        dpg.create_viewport(title="PSE-Image", width=1400, height=850)
        dpg.setup_dearpygui()
        dpg.show_viewport()
        dpg.set_primary_window("main", True)

    def _setup_font(self) -> None:
        # a fonte padrão do DPG não tem acentos (ç, ã, é...)
        path = resource_path(os.path.join("assets", "DejaVuSans.ttf"))
        if os.path.exists(path):
            with dpg.font_registry():
                dpg.bind_font(dpg.add_font(path, 16))

    # =================================================================== nós
    def add_node(self, ntype: NodeType, pos: tuple[int, int] | None = None, run: bool = True) -> int:
        nid = self.graph.add_node(ntype.create())
        spec = ntype.spec
        if pos is None:
            k = self._spawn % 8
            self._spawn += 1
            pos = (60 + 30 * k, 40 + 30 * k)

        with dpg.node(label=spec.title, parent="editor", pos=pos) as item:
            self.node_items[nid] = item
            for port in spec.inputs:
                with dpg.node_attribute(attribute_type=dpg.mvNode_Attr_Input) as attr:
                    dpg.add_text(port)
                self._map_attr(attr, nid, port, False)

            for p in spec.params:
                with dpg.node_attribute(attribute_type=dpg.mvNode_Attr_Static):
                    self._param_widget(nid, p)

            if spec.preview:
                with dpg.node_attribute(attribute_type=dpg.mvNode_Attr_Static):
                    tex = dpg.add_static_texture(1, 1, [0.0, 0.0, 0.0, 0.0], parent=self.textures)
                    self.previews[nid] = {
                        "texture": tex,
                        "src": None,
                        "image": dpg.add_image(tex, show=False),
                        "info": dpg.add_text("", color=(170, 170, 170)),
                        "zoom": dpg.add_button(label="Ampliar", show=False, user_data=nid,
                                               callback=lambda s, a, u: self.open_full(u)),
                    }

            with dpg.node_attribute(attribute_type=dpg.mvNode_Attr_Static):
                self.status[nid] = dpg.add_text("", color=ERROR_COLOR, wrap=THUMB_SIDE)

            for port in spec.outputs:
                with dpg.node_attribute(attribute_type=dpg.mvNode_Attr_Output) as attr:
                    dpg.add_text(port)
                self._map_attr(attr, nid, port, True)

        if run:
            self.run()
        return nid

    def _map_attr(self, attr: int, nid: int, port: str, is_out: bool) -> None:
        self.attr_ports[attr] = (nid, port, is_out)
        self.port_attrs[(nid, port, is_out)] = attr

    def _param_widget(self, nid: int, p: Param) -> None:
        def cb(sender, value, user_data=None):
            self.set_param(nid, p.name, value)

        common = dict(label=p.label, width=NODE_WIDGET_W, callback=cb)
        if p.kind == "int":
            dpg.add_slider_int(default_value=p.default, min_value=int(p.min), max_value=int(p.max), **common)
        elif p.kind == "float":
            dpg.add_slider_float(default_value=p.default, min_value=p.min, max_value=p.max, **common)
        elif p.kind == "choice":
            dpg.add_combo(items=p.choices, default_value=p.default, **common)
        elif p.kind == "bool":
            dpg.add_checkbox(label=p.label, default_value=p.default, callback=cb)
        elif p.kind in ("file_open", "file_save"):
            save = p.kind == "file_save"
            dpg.add_button(label=p.label + "...", width=NODE_WIDGET_W,
                           callback=lambda: self.ask_file(save, lambda path: self.set_param(nid, p.name, path)))
            self.file_labels[(nid, p.name)] = dpg.add_text("(nenhum)", wrap=THUMB_SIDE, color=(170, 170, 170))
        elif p.kind == "text":
            dpg.add_input_text(default_value=p.default or "", hint=p.hint, **common)
        elif p.kind == "dir":
            with dpg.group(horizontal=True):
                field = dpg.add_input_text(default_value=p.default or "", hint=p.hint,
                                           width=NODE_WIDGET_W - 34, callback=cb)
                dpg.add_button(label="...", width=26, callback=lambda: self.ask_dir(
                    lambda path: (dpg.set_value(field, path), self.set_param(nid, p.name, path))))
                dpg.add_text(p.label)
        elif p.kind == "action":
            dpg.add_button(label=p.label, width=NODE_WIDGET_W, callback=lambda: self.trigger(nid, p.name))
        else:
            raise ValueError(f"tipo de parâmetro desconhecido: {p.kind}")

    def set_param(self, nid: int, name: str, value) -> None:
        self.graph.nodes[nid].values[name] = value
        label = self.file_labels.get((nid, name))
        if label and isinstance(value, str):
            dpg.set_value(label, os.path.basename(value))
        self.run()

    def trigger(self, nid: int, action: str) -> None:
        """Botão de um parâmetro "action" (ex.: Salvar)."""
        self.run()  # garante entradas atualizadas
        self.graph.nodes[nid].trigger(action)
        self.run()

    # ============================================================== ligações
    def connect(self, link: Link) -> bool:
        try:
            replaced = self.graph.connect(link)
        except ValueError:
            return False  # ciclo / porta inválida: simplesmente não liga
        if replaced and replaced in self.link_items:
            dpg.delete_item(self.link_items.pop(replaced))
        self.link_items[link] = dpg.add_node_link(
            self.port_attrs[(link.src, link.src_port, True)],
            self.port_attrs[(link.dst, link.dst_port, False)],
            parent="editor")
        self.run()
        return True

    def on_link(self, sender, app_data) -> None:
        a, b = (self.attr_ports[x] for x in app_data)
        if a[2] == b[2]:
            return  # saída-saída ou entrada-entrada
        out, inp = (a, b) if a[2] else (b, a)
        self.connect(Link(out[0], out[1], inp[0], inp[1]))

    def on_delink(self, sender, link_item) -> None:
        self._remove_link_item(link_item)
        self.run()

    def _remove_link_item(self, link_item: int) -> None:
        link = next((l for l, it in self.link_items.items() if it == link_item), None)
        if link:
            self.graph.disconnect(link)
            del self.link_items[link]
        dpg.delete_item(link_item)

    def delete_selected(self) -> None:
        for link_item in dpg.get_selected_links("editor"):
            self._remove_link_item(link_item)
        item_to_nid = {it: nid for nid, it in self.node_items.items()}
        for node_item in dpg.get_selected_nodes("editor"):
            nid = item_to_nid.get(node_item)
            if nid is None:
                continue
            for link in self.graph.remove_node(nid):
                if link in self.link_items:
                    dpg.delete_item(self.link_items.pop(link))
            for attr in [a for a, (n, _, _) in self.attr_ports.items() if n == nid]:
                del self.port_attrs[self.attr_ports.pop(attr)]
            if nid in self.previews:
                self._trash.append(self.previews.pop(nid)["texture"])
            self.status.pop(nid, None)
            dpg.delete_item(self.node_items.pop(nid))
        self.run()

    # ============================================================== execução
    def run(self) -> None:
        for tex in self._trash:
            if dpg.does_item_exist(tex):
                dpg.delete_item(tex)
        self._trash.clear()

        self.graph.evaluate()
        for nid, node in self.graph.nodes.items():
            dpg.configure_item(self.status[nid], color=ERROR_COLOR if node.error else OK_COLOR)
            dpg.set_value(self.status[nid], node.error or node.status)
            if nid in self.previews:
                self._update_preview(nid, node.last_inputs.get(node.spec.preview))

    def _update_preview(self, nid: int, img: np.ndarray | None) -> None:
        pv = self.previews[nid]
        if img is pv["src"]:
            return  # mesma imagem: não reenvia a textura
        pv["src"] = img
        shown = img is not None
        for key in ("image", "zoom"):
            dpg.configure_item(pv[key], show=shown)
        if shown:
            kind = "RGB" if img.ndim == 3 else "cinza"
            dpg.set_value(pv["info"], f"{img.shape[1]} x {img.shape[0]} · {kind}")
        else:
            dpg.set_value(pv["info"], "")
        if not shown:
            return
        th = thumbnail(img, THUMB_SIDE)
        tex = dpg.add_static_texture(th.shape[1], th.shape[0], to_rgba(th), parent=self.textures)
        dpg.configure_item(pv["image"], texture_tag=tex, width=th.shape[1], height=th.shape[0])
        self._trash.append(pv["texture"])
        pv["texture"] = tex

    def open_full(self, nid: int) -> None:
        img = self.previews[nid]["src"]
        if img is None:
            return
        h, w = img.shape[:2]
        tex = dpg.add_static_texture(w, h, to_rgba(img), parent=self.textures)

        def close(sender):
            self._trash.append(tex)
            dpg.delete_item(sender)

        with dpg.window(label=f"{self.graph.nodes[nid].spec.title} ({w} x {h})", width=min(w + 30, 1000),
                        height=min(h + 50, 800), pos=(250, 40), horizontal_scrollbar=True, on_close=close):
            dpg.add_image(tex)

    # ============================================================ arquivos
    def ask_file(self, save: bool, on_ok) -> None:
        def done(sender, app_data):
            dpg.delete_item(sender)
            if save:
                path = app_data.get("file_path_name", "")
                if path.endswith(".*"):
                    path = path[:-2]
                if path and not path.lower().endswith(".png"):
                    path += ".png"
            else:
                sel = list(app_data.get("selections", {}).values())
                path = sel[0] if sel else app_data.get("file_path_name", "")
            if path:
                self.last_dir = os.path.dirname(path)
                on_ok(path)

        with dpg.file_dialog(label="Salvar PNG" if save else "Abrir PNG", modal=True,
                             width=760, height=460, default_path=self.last_dir,
                             callback=done, cancel_callback=lambda s, a: dpg.delete_item(s)):
            dpg.add_file_extension(".png", color=(120, 200, 255))
            if not save:
                dpg.add_file_extension(".*")

    def ask_dir(self, on_ok) -> None:
        def done(sender, app_data):
            dpg.delete_item(sender)
            path = app_data.get("file_path_name", "")
            if path:
                self.last_dir = path
                on_ok(path)

        dpg.add_file_dialog(label="Escolher pasta", directory_selector=True, modal=True,
                            width=760, height=460, default_path=self.last_dir,
                            callback=done, cancel_callback=lambda s, a: dpg.delete_item(s))


def main() -> None:
    app = App()
    app.build()
    dpg.start_dearpygui()
    dpg.destroy_context()
