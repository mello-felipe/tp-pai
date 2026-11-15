import { Background, Controls, MiniMap, ReactFlow, useReactFlow, type NodeTypes } from "@xyflow/react";
import type { DragEvent } from "react";

import { DND_MIME } from "../lib/dnd";
import { useWorkflow } from "../store/workflow";
import { PseNodeView } from "./PseNodeView";

const NODE_TYPES: NodeTypes = { default: PseNodeView };

export function Canvas() {
  const { nodes, edges, onNodesChange, onEdgesChange, onConnect, addNode } = useWorkflow();
  const { screenToFlowPosition } = useReactFlow();

  const onDragOver = (event: DragEvent) => {
    event.preventDefault();
    event.dataTransfer.dropEffect = "move";
  };

  const onDrop = (event: DragEvent) => {
    event.preventDefault();
    const key = event.dataTransfer.getData(DND_MIME);
    if (key) addNode(key, screenToFlowPosition({ x: event.clientX, y: event.clientY }));
  };

  return (
    <div className="canvas" onDragOver={onDragOver} onDrop={onDrop}>
      <ReactFlow
        nodes={nodes}
        edges={edges}
        nodeTypes={NODE_TYPES}
        onNodesChange={onNodesChange}
        onEdgesChange={onEdgesChange}
        onConnect={onConnect}
        deleteKeyCode={["Delete", "Backspace"]}
        fitView
      >
        <Background />
        <Controls />
        <MiniMap pannable zoomable />
      </ReactFlow>
    </div>
  );
}
