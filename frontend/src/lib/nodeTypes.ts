import type { NodeTypeSpec, ParamValue } from "../types";

/** Agrupa os tipos por categoria (seções da paleta), ordenados pelo título. */
export function groupByCategory(types: NodeTypeSpec[]): [string, NodeTypeSpec[]][] {
  const groups = new Map<string, NodeTypeSpec[]>();
  for (const t of [...types].sort((a, b) => a.title.localeCompare(b.title, "pt-BR"))) {
    groups.set(t.category, [...(groups.get(t.category) ?? []), t]);
  }
  return [...groups.entries()];
}

/** Valores iniciais dos parâmetros (os "action" não guardam valor). */
export function defaultValues(spec: NodeTypeSpec): Record<string, ParamValue> {
  return Object.fromEntries(
    spec.params
      .filter((p) => p.kind !== "action" && p.default !== null)
      .map((p) => [p.name, p.default as ParamValue]),
  );
}
