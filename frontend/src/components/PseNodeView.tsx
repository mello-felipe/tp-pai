import { Handle, Position, type NodeProps } from "@xyflow/react";

import { useWorkflow, type PseNode } from "../store/workflow";
import { ParamField } from "./params/ParamField";

/** Bloco no canvas: título, uma alça por porta de entrada (esquerda) e de saída (direita). */
export function PseNodeView({ id, data, selected }: NodeProps<PseNode>) {
  const spec = useWorkflow((s) => s.types[data.typeKey]);
  const setValue = useWorkflow((s) => s.setValue);
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
      {spec.params.length > 0 && (
        <div className="params">
          {spec.params.map((p) => (
            <ParamField
              key={p.name}
              param={p}
              value={data.values[p.name]}
              onChange={(v) => setValue(id, p.name, v)}
            />
          ))}
        </div>
      )}
    </div>
  );
}
