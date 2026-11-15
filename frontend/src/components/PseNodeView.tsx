import { Handle, Position, type NodeProps } from "@xyflow/react";

import { useWorkflow, type PseNode } from "../store/workflow";

/** Bloco no canvas: título, uma alça por porta de entrada (esquerda) e de saída (direita). */
export function PseNodeView({ data, selected }: NodeProps<PseNode>) {
  const spec = useWorkflow((s) => s.types[data.typeKey]);
  if (!spec) return <div className="pse-node error">tipo desconhecido: {data.typeKey}</div>;

  const rows = Math.max(spec.inputs.length, spec.outputs.length);
  return (
    <div className={`pse-node${selected ? " selected" : ""}`}>
      <header>{spec.title}</header>
      <div className="ports">
        {Array.from({ length: rows }, (_, i) => (
          <div className="port-row" key={i}>
            <span className="port in">
              {spec.inputs[i] && (
                <>
                  <Handle type="target" position={Position.Left} id={spec.inputs[i]} />
                  {spec.inputs[i]}
                </>
              )}
            </span>
            <span className="port out">
              {spec.outputs[i] && (
                <>
                  {spec.outputs[i]}
                  <Handle type="source" position={Position.Right} id={spec.outputs[i]} />
                </>
              )}
            </span>
          </div>
        ))}
      </div>
    </div>
  );
}
