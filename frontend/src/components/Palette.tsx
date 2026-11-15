import { useReactFlow } from "@xyflow/react";
import type { DragEvent } from "react";

import { DND_MIME } from "../lib/dnd";
import { groupByCategory } from "../lib/nodeTypes";
import { useWorkflow } from "../store/workflow";

/** Lista de blocos por categoria. Arraste para o canvas ou clique para adicionar no centro. */
export function Palette() {
  const types = useWorkflow((s) => s.types);
  const addNode = useWorkflow((s) => s.addNode);
  const { screenToFlowPosition } = useReactFlow();

  const onDragStart = (event: DragEvent, key: string) => {
    event.dataTransfer.setData(DND_MIME, key);
    event.dataTransfer.effectAllowed = "move";
  };

  const addAtCenter = (key: string) => {
    const canvas = document.querySelector(".canvas")?.getBoundingClientRect();
    const x = canvas ? canvas.left + canvas.width / 2 : window.innerWidth / 2;
    const y = canvas ? canvas.top + canvas.height / 2 : window.innerHeight / 2;
    addNode(key, screenToFlowPosition({ x, y }));
  };

  return (
    <aside className="palette">
      <h2>Blocos</h2>
      {groupByCategory(Object.values(types)).map(([category, specs]) => (
        <section key={category}>
          <h3>{category}</h3>
          {specs.map((spec) => (
            <button
              key={spec.key}
              type="button"
              className="palette-item"
              title={spec.description}
              draggable
              onDragStart={(e) => onDragStart(e, spec.key)}
              onClick={() => addAtCenter(spec.key)}
            >
              {spec.title}
            </button>
          ))}
        </section>
      ))}
    </aside>
  );
}
