import type { Edge } from "@xyflow/react";
import { describe, expect, it } from "vitest";

import { connectEdge } from "./workflow";

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
