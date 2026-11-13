import numpy as np
import pytest

from pse.core import Graph, Link, NodeError, NodeSpec, NodeType, Param


def make(key, inputs, outputs, execute):
    return NodeType(key, NodeSpec(title=key, category="t", inputs=inputs, outputs=outputs), execute)


def _sub(i, p):
    if i["x"] is None or i["y"] is None:
        raise NodeError("faltando entrada")
    return {"out": i["x"] - i["y"]}


SOURCE = make("source", (), ("a", "b"),  # nó com duas saídas
              lambda i, p: {"a": np.full((2, 2), 10, np.uint8), "b": np.full((2, 2), 3, np.uint8)})
SUB = make("sub", ("x", "y"), ("out",), _sub)
PASS = make("pass", ("in",), ("out",), lambda i, p: {"out": i["in"]})


def test_multi_output_and_two_inputs():
    g = Graph()
    s, d = g.add_node(SOURCE.create()), g.add_node(SUB.create())
    g.connect(Link(s, "a", d, "x"))
    g.connect(Link(s, "b", d, "y"))
    g.evaluate()
    assert (g.nodes[d].last_outputs["out"] == 7).all()


def test_missing_input_sets_error_and_propagates_none():
    g = Graph()
    d, p = g.add_node(SUB.create()), g.add_node(PASS.create())
    g.connect(Link(d, "out", p, "in"))
    g.evaluate()
    assert g.nodes[d].error == "faltando entrada"
    assert g.nodes[p].last_outputs["out"] is None


def test_unexpected_exception_is_shown_in_node():
    g = Graph()
    n = g.add_node(make("boom", (), ("o",), lambda i, p: 1 / 0).create())
    g.evaluate()
    assert g.nodes[n].error.startswith("ZeroDivisionError")


def test_input_accepts_single_link_replaces_old():
    g = Graph()
    s1, s2, p = g.add_node(SOURCE.create()), g.add_node(SOURCE.create()), g.add_node(PASS.create())
    first = Link(s1, "a", p, "in")
    g.connect(first)
    assert g.connect(Link(s2, "b", p, "in")) == first
    assert len(g.links) == 1


def test_output_can_feed_many_inputs():
    g = Graph()
    s, p1, p2 = g.add_node(SOURCE.create()), g.add_node(PASS.create()), g.add_node(PASS.create())
    g.connect(Link(s, "a", p1, "in"))
    g.connect(Link(s, "a", p2, "in"))
    g.evaluate()
    assert g.nodes[p2].last_outputs["out"] is g.nodes[p1].last_outputs["out"]


def test_cycle_rejected():
    g = Graph()
    a, b = g.add_node(PASS.create()), g.add_node(PASS.create())
    g.connect(Link(a, "out", b, "in"))
    with pytest.raises(ValueError):
        g.connect(Link(b, "out", a, "in"))


def test_remove_node_drops_links():
    g = Graph()
    s, p = g.add_node(SOURCE.create()), g.add_node(PASS.create())
    link = Link(s, "a", p, "in")
    g.connect(link)
    assert g.remove_node(s) == [link]
    assert not g.links


def test_unchanged_node_is_not_reexecuted():
    calls = []

    def counted(i, p):
        calls.append(p["k"])
        return {"out": i["in"]}

    t = NodeType("c", NodeSpec(title="c", category="t", inputs=("in",), outputs=("out",)), counted)
    g = Graph()
    s, c = g.add_node(SOURCE.create()), g.add_node(t.create())
    g.nodes[c].values["k"] = 1
    g.connect(Link(s, "a", c, "in"))
    g.evaluate()
    g.evaluate()                      # nada mudou: não executa de novo
    g.nodes[c].values["k"] = 2
    g.evaluate()                      # parâmetro mudou: executa
    assert calls == [1, 2]


def test_action_runs_once_with_flag_and_keeps_outputs_on_error():
    calls = []

    def ex(i, p):
        calls.append(p["go"])
        if p["go"] and p["fail"]:
            raise NodeError("falhou")
        return {"out": i["in"], "_status": "feito" if p["go"] else ""}

    spec = NodeSpec(title="a", category="t", inputs=("in",), outputs=("out",),
                    params=(Param("go", "Ir", "action"), Param("fail", "F", "bool", False)))
    g = Graph()
    s, a = g.add_node(SOURCE.create()), g.add_node(NodeType("a", spec, ex).create())
    g.connect(Link(s, "a", a, "in"))
    g.evaluate()
    node = g.nodes[a]
    node.trigger("go")
    assert node.status == "feito" and node.values["go"] is False
    g.evaluate()                         # nada mudou: status continua
    assert node.status == "feito" and calls == [False, True]
    node.values["fail"] = True
    g.evaluate()
    out = node.last_outputs["out"]
    node.trigger("go")
    assert node.error == "falhou" and node.last_outputs["out"] is out
