import {
  Background,
  Controls,
  MiniMap,
  ReactFlow,
  useReactFlow,
  type Connection,
  type Edge,
  type NodeTypes,
} from "@xyflow/react";
import type { DragEvent } from "react";

import { DND_MIME } from "../lib/dnd";
import { createsCycle } from "../lib/graph";
import { useWorkflow } from "../store/workflow";
import { PseNodeView } from "./PseNodeView";

// Tipo próprio: o tipo "default" do React Flow aplica borda, largura e padding no invólucro.
const NODE_TYPES: NodeTypes = { pse: PseNodeView }; // ver PseNode em store/workflow.ts

export function Canvas() {
  const { nodes, edges, onNodesChange, onEdgesChange, onConnect, addNode } = useWorkflow();
  const { screenToFlowPosition } = useReactFlow();

  // Recusa ligações que formariam ciclo (o backend também recusa).
  const isValidConnection = (conn: Connection | Edge) => !createsCycle(edges, conn);

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
        isValidConnection={isValidConnection}
        deleteKeyCode={["Delete", "Backspace"]}
        defaultViewport={{ x: 0, y: 0, zoom: 1 }} // sem fitView: o 1º bloco não dá zoom de 2x
      >
        <Background />
        <Controls />
        <MiniMap pannable zoomable />
      </ReactFlow>
    </div>
  );
}
