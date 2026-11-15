import type { Edge } from "@xyflow/react";

import type { PseNode } from "../store/workflow";
import type { LinkPayload, WorkflowPayload } from "../types";

/** Estado do canvas -> corpo do PUT /api/workflow (posições não importam ao backend). */
export function toPayload(nodes: PseNode[], edges: Edge[]): WorkflowPayload {
  return {
    nodes: nodes.map((n) => ({ id: n.id, type: n.data.typeKey, values: n.data.values })),
    links: edges.map(edgeToLink),
  };
}

export function edgeToLink(e: Edge): LinkPayload {
  return { src: e.source, src_port: e.sourceHandle ?? "", dst: e.target, dst_port: e.targetHandle ?? "" };
}

export function sameLink(a: LinkPayload, b: LinkPayload): boolean {
  return a.src === b.src && a.src_port === b.src_port && a.dst === b.dst && a.dst_port === b.dst_port;
}
