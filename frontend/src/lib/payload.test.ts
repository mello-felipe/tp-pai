import { describe, expect, it } from "vitest";

import type { PseNode } from "../store/workflow";
import { edgeToLink, sameLink, toPayload } from "./payload";

const node = (id: string, x: number): PseNode => ({
  id,
  position: { x, y: 0 },
  data: { typeKey: "display", values: { a: 1 } },
});
const edge = { id: "e", source: "a", sourceHandle: "imagem", target: "b", targetHandle: "imagem" };

describe("toPayload", () => {
  it("converte nós e ligações e ignora posições", () => {
    const payload = toPayload([node("a", 0)], [edge]);
    expect(payload).toEqual({
      nodes: [{ id: "a", type: "display", values: { a: 1 } }],
      links: [{ src: "a", src_port: "imagem", dst: "b", dst_port: "imagem" }],
    });
    expect(JSON.stringify(toPayload([node("a", 50)], [edge]))).toBe(JSON.stringify(payload));
  });
});

describe("sameLink", () => {
  it("compara as quatro partes da ligação", () => {
    const link = edgeToLink(edge);
    expect(sameLink(link, { ...link })).toBe(true);
    expect(sameLink(link, { ...link, dst_port: "x" })).toBe(false);
  });
});
