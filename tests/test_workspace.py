import numpy as np
import pytest

from pse.api.schemas import WorkflowIn
from pse.api.values import WorkflowError
from pse.api.workspace import OUT, PREVIEW, Workspace
from pse.core import NodeSpec, NodeType, Param

SOURCE = NodeType("source", NodeSpec(
    title="Fonte", category="t", outputs=("img",),
    params=(Param("v", "V", "int", 10, 0, 255), Param("mode", "M", "choice", "a", choices=("a", "b")),
            Param("go", "Ir", "action"))),
    lambda i, p: {"img": np.full((2, 3), p["v"], np.uint8), "_status": "ok" if p["go"] else ""})
INVERT = NodeType("invert", NodeSpec(title="Inv", category="t", inputs=("img",), outputs=("img",), preview="img"),
                  lambda i, p: {"img": 255 - i["img"]})
TYPES = {t.key: t for t in (SOURCE, INVERT)}


def wf(nodes, links=()):
    return WorkflowIn.model_validate({
        "nodes": [{"id": i, "type": t, "values": v} for i, t, v in nodes],
        "links": [dict(zip(("src", "src_port", "dst", "dst_port"), l)) for l in links]})


CHAIN = [("s", "source", {}), ("i", "invert", {})]
LINK = ("s", "img", "i", "img")


@pytest.fixture
def ws():
    return Workspace(TYPES)


def test_sync_runs_flow_and_reports_images(ws):
    out = ws.sync(wf(CHAIN, [LINK]))
    assert out["rejected_links"] == []
    meta = out["nodes"]["i"]["outputs"]["img"]
    assert meta | {"version": 0} == {"version": 0, "width": 3, "height": 2, "channels": 1}
    assert (ws.image("i", OUT + "img") == 245).all()
    assert (ws.image("i", PREVIEW) == 10).all()
    assert out["nodes"]["s"]["preview"] is None


def test_version_changes_only_when_image_changes(ws):
    v1 = ws.sync(wf(CHAIN, [LINK]))["nodes"]["i"]["outputs"]["img"]["version"]
    v2 = ws.sync(wf(CHAIN, [LINK]))["nodes"]["i"]["outputs"]["img"]["version"]
    v3 = ws.sync(wf([("s", "source", {"v": 20}), CHAIN[1]], [LINK]))["nodes"]["i"]["outputs"]["img"]["version"]
    assert v1 == v2 != v3


def test_missing_input_reports_error_and_no_image(ws):
    node = ws.sync(wf(CHAIN))["nodes"]["i"]
    assert node["error"] and node["outputs"]["img"] is None
    with pytest.raises(KeyError):
        ws.image("i", OUT + "img")


def test_removed_node_and_its_images_are_dropped(ws):
    ws.sync(wf(CHAIN, [LINK]))
    out = ws.sync(wf(CHAIN[:1]))
    assert out["nodes"].keys() == {"s"} and not ws.graph.links
    with pytest.raises(KeyError):
        ws.image("i", OUT + "img")


def test_type_change_recreates_node(ws):
    ws.sync(wf([("x", "source", {})]))
    first = ws.graph.nodes["x"]
    ws.sync(wf([("x", "invert", {})]))
    assert ws.graph.nodes["x"] is not first and ws.graph.nodes["x"].type is INVERT


def test_values_are_validated(ws):
    ws.sync(wf([("s", "source", {"v": 999, "unknown": 1, "go": True})]))
    assert ws.graph.nodes["s"].values == {"v": 255, "mode": "a", "go": False}


@pytest.mark.parametrize("values", [{"v": "abc"}, {"v": True}, {"mode": "z"}])
def test_invalid_values_raise(ws, values):
    with pytest.raises(WorkflowError):
        ws.sync(wf([("s", "source", values)]))


@pytest.mark.parametrize("nodes", [[("s", "nope", {})], [("s", "source", {}), ("s", "source", {})]])
def test_invalid_nodes_raise(ws, nodes):
    with pytest.raises(WorkflowError):
        ws.sync(wf(nodes))


def test_bad_links_are_rejected(ws):
    nodes = [*CHAIN, ("j", "invert", {}), ("s2", "source", {})]
    out = ws.sync(wf(nodes, [LINK, ("s2", "img", "i", "img"), ("i", "img", "j", "img"),
                             ("j", "img", "i", "img"), ("ghost", "img", "i", "img")]))
    errors = [r["error"] for r in out["rejected_links"]]
    assert errors == ["entrada já ligada", "entrada já ligada", "nó inexistente"]
    assert len(ws.graph.links) == 2


def test_cycle_is_rejected(ws):
    nodes = [("a", "invert", {}), ("b", "invert", {})]
    out = ws.sync(wf(nodes, [("a", "img", "b", "img"), ("b", "img", "a", "img")]))
    assert [r["error"] for r in out["rejected_links"]] == ["ligação criaria um ciclo"]


def test_trigger_action(ws):
    ws.sync(wf(CHAIN[:1]))
    assert ws.trigger("s", "go")["status"] == "ok"
    with pytest.raises(WorkflowError):
        ws.trigger("s", "v")
    with pytest.raises(KeyError):
        ws.trigger("ghost", "go")
