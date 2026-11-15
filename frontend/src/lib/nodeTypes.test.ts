import { describe, expect, it } from "vitest";

import type { NodeTypeSpec, ParamSpec } from "../types";
import { defaultValues, groupByCategory } from "./nodeTypes";

const param = (p: Partial<ParamSpec>): ParamSpec => ({
  name: "p",
  label: "P",
  kind: "int",
  default: 0,
  min: 0,
  max: 1,
  choices: [],
  hint: "",
  ...p,
});

const spec = (p: Partial<NodeTypeSpec>): NodeTypeSpec => ({
  key: "k",
  title: "T",
  category: "C",
  description: "",
  inputs: [],
  outputs: [],
  params: [],
  preview: null,
  ...p,
});

describe("groupByCategory", () => {
  it("agrupa por categoria e ordena pelo título", () => {
    const groups = groupByCategory([
      spec({ key: "b", title: "Salvar", category: "Interface" }),
      spec({ key: "c", title: "Média", category: "Filtros" }),
      spec({ key: "a", title: "Exibir", category: "Interface" }),
    ]);
    expect(groups.map(([cat, ts]) => [cat, ts.map((t) => t.key)])).toEqual([
      ["Interface", ["a", "b"]],
      ["Filtros", ["c"]],
    ]);
  });
});

describe("defaultValues", () => {
  it("usa o padrão de cada parâmetro e ignora ações", () => {
    const values = defaultValues(
      spec({
        params: [
          param({ name: "t", default: 128 }),
          param({ name: "nome", kind: "text", default: "x" }),
          param({ name: "salvar", kind: "action", default: false }),
          param({ name: "arquivo", kind: "file_open", default: null }),
        ],
      }),
    );
    expect(values).toEqual({ t: 128, nome: "x" });
  });
});
