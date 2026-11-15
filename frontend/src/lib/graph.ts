import type { Edge } from "@xyflow/react";

/** A ligação source -> target fecharia um ciclo? (existe caminho target -> ... -> source) */
export function createsCycle(edges: Edge[], conn: { source: string; target: string }): boolean {
  if (conn.source === conn.target) return true;
  const next = new Map<string, string[]>();
  for (const e of edges) next.set(e.source, [...(next.get(e.source) ?? []), e.target]);
  const stack = [conn.target];
  const seen = new Set<string>();
  while (stack.length > 0) {
    const id = stack.pop()!;
    if (id === conn.source) return true;
    if (seen.has(id)) continue;
    seen.add(id);
    stack.push(...(next.get(id) ?? []));
  }
  return false;
}
