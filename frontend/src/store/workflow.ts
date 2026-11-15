import {
  addEdge,
  applyEdgeChanges,
  applyNodeChanges,
  type Connection,
  type Edge,
  type Node,
  type OnConnect,
  type OnEdgesChange,
  type OnNodesChange,
  type XYPosition,
} from "@xyflow/react";
import { create } from "zustand";

import { defaultValues } from "../lib/nodeTypes";
import type { NodeTypeSpec, ParamValue } from "../types";

export type PseNodeData = {
  typeKey: string;
  values: Record<string, ParamValue>;
};
export type PseNode = Node<PseNodeData, "pse">;

interface WorkflowState {
  types: Record<string, NodeTypeSpec>;
  nodes: PseNode[];
  edges: Edge[];
  setTypes: (types: NodeTypeSpec[]) => void;
  addNode: (typeKey: string, position: XYPosition) => void;
  setValue: (nodeId: string, name: string, value: ParamValue) => void;
  onNodesChange: OnNodesChange<PseNode>;
  onEdgesChange: OnEdgesChange;
  onConnect: OnConnect;
}

/** Novo nó com o valor trocado (sem mutar o original). */
export function withValue(node: PseNode, name: string, value: ParamValue): PseNode {
  return { ...node, data: { ...node.data, values: { ...node.data.values, [name]: value } } };
}

/** Uma entrada aceita só uma ligação: a nova substitui a antiga. */
export function connectEdge(edges: Edge[], conn: Connection): Edge[] {
  const others = edges.filter(
    (e) => !(e.target === conn.target && e.targetHandle === conn.targetHandle),
  );
  return addEdge(conn, others);
}

export const useWorkflow = create<WorkflowState>((set, get) => ({
  types: {},
  nodes: [],
  edges: [],
  setTypes: (types) => set({ types: Object.fromEntries(types.map((t) => [t.key, t])) }),
  addNode: (typeKey, position) => {
    const spec = get().types[typeKey];
    if (!spec) return;
    const node: PseNode = {
      id: crypto.randomUUID(),
      type: "pse",
      position,
      data: { typeKey, values: defaultValues(spec) },
    };
    set({ nodes: [...get().nodes, node] });
  },
  setValue: (nodeId, name, value) =>
    set({ nodes: get().nodes.map((n) => (n.id === nodeId ? withValue(n, name, value) : n)) }),
  onNodesChange: (changes) => set({ nodes: applyNodeChanges(changes, get().nodes) }),
  onEdgesChange: (changes) => set({ edges: applyEdgeChanges(changes, get().edges) }),
  onConnect: (conn) => set({ edges: connectEdge(get().edges, conn) }),
}));
