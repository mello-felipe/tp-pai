import type { Edge } from "@xyflow/react";
import { describe, expect, it } from "vitest";

import { createsCycle } from "./graph";

const edge = (source: string, target: string): Edge => ({ id: `${source}-${target}`, source, target });
const conn = (source: string, target: string) => ({ source, target });

describe("createsCycle", () => {
  const edges = [edge("a", "b"), edge("b", "c")];

  it("detecta ciclo e auto-ligação", () => {
    expect(createsCycle(edges, conn("c", "a"))).toBe(true);
    expect(createsCycle(edges, conn("a", "a"))).toBe(true);
  });

  it("aceita ligações sem ciclo", () => {
    expect(createsCycle(edges, conn("a", "c"))).toBe(false);
    expect(createsCycle(edges, conn("d", "a"))).toBe(false);
  });
});
