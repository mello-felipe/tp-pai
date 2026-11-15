import type { Edge } from "@xyflow/react";
import { describe, expect, it } from "vitest";

import { connectEdge, withFile, withValue, type PseNode } from "./workflow";

const conn = (source: string, target: string, port = "imagem") => ({
  source,
  sourceHandle: "out",
  target,
  targetHandle: port,
});

describe("connectEdge", () => {
  it("substitui a ligação antiga da mesma entrada", () => {
    let edges: Edge[] = connectEdge([], conn("a", "c"));
    edges = connectEdge(edges, conn("b", "c"));
    expect(edges.map((e) => e.source)).toEqual(["b"]);
  });

  it("mantém ligações em entradas diferentes e saídas compartilhadas", () => {
    let edges: Edge[] = connectEdge([], conn("a", "c", "x"));
    edges = connectEdge(edges, conn("a", "c", "y"));
    edges = connectEdge(edges, conn("a", "d"));
    expect(edges).toHaveLength(3);
  });
});

describe("withValue", () => {
  it("troca o valor sem mutar o nó original", () => {
    const node: PseNode = { id: "n", type: "pse", position: { x: 0, y: 0 }, data: { typeKey: "t", values: { a: 1 } } };
    const next = withValue(node, "b", "x");
    expect(next.data.values).toEqual({ a: 1, b: "x" });
    expect(node.data.values).toEqual({ a: 1 });
  });
});

describe("withFile", () => {
  it("guarda o caminho no valor e o nome original à parte", () => {
    const node: PseNode = { id: "n", position: { x: 0, y: 0 }, data: { typeKey: "read_png", values: {} } };
    const next = withFile(node, "path", "/tmp/x/abc.png", "foto.png");
    expect(next.data.values).toEqual({ path: "/tmp/x/abc.png" });
    expect(next.data.fileNames).toEqual({ path: "foto.png" });
    expect(node.data.fileNames).toBeUndefined();
  });
});
