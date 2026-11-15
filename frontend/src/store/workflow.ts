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
export type PseNode = Node<PseNodeData>;

interface WorkflowState {
  types: Record<string, NodeTypeSpec>;
  nodes: PseNode[];
  edges: Edge[];
  setTypes: (types: NodeTypeSpec[]) => void;
  addNode: (typeKey: string, position: XYPosition) => void;
  onNodesChange: OnNodesChange<PseNode>;
  onEdgesChange: OnEdgesChange;
  onConnect: OnConnect;
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
      position,
      data: { typeKey, values: defaultValues(spec) },
    };
    set({ nodes: [...get().nodes, node] });
  },
  onNodesChange: (changes) => set({ nodes: applyNodeChanges(changes, get().nodes) }),
  onEdgesChange: (changes) => set({ edges: applyEdgeChanges(changes, get().edges) }),
  onConnect: (conn) => set({ edges: connectEdge(get().edges, conn) }),
}));
