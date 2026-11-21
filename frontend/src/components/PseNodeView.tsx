import { Handle, Position, type NodeProps } from "@xyflow/react";

import { previewUrl } from "../api/client";
import { useWorkflow, type PseNode } from "../store/workflow";
import type { ParamSpec } from "../types";
import { ActionButton } from "./params/ActionButton";
import { FileField } from "./params/FileField";
import { KernelEditor } from "./params/KernelEditor";
import { ParamField } from "./params/ParamField";

/** Bloco no canvas: título, portas, parâmetros, miniatura e mensagens do backend. */
export function PseNodeView({ id, data, selected }: NodeProps<PseNode>) {
  const spec = useWorkflow((s) => s.types[data.typeKey]);
  const result = useWorkflow((s) => s.results[id]);
  const { setValue, setFile, setNodeResult } = useWorkflow.getState();
  if (!spec) return <div className="pse-node error">tipo desconhecido: {data.typeKey}</div>;

  const renderParam = (p: ParamSpec) => {
    if (p.kind === "file_open")
      return (
        <FileField
          key={p.name}
          param={p}
          fileName={data.fileNames?.[p.name]}
          onUploaded={(path, name) => setFile(id, p.name, path, name)}
        />
      );
    if (p.kind === "kernel")
      return (
        <KernelEditor key={p.name} param={p} value={data.values[p.name]} onChange={(k) => setValue(id, p.name, k)} />
      );
    if (p.kind === "action")
      return <ActionButton key={p.name} nodeId={id} param={p} onResult={(r) => setNodeResult(id, r)} />;
    return (
      <ParamField key={p.name} param={p} value={data.values[p.name]} onChange={(v) => setValue(id, p.name, v)} />
    );
  };

  const rows = Math.max(spec.inputs.length, spec.outputs.length);
  return (
    <div className={`pse-node${selected ? " selected" : ""}${result?.error ? " failed" : ""}`}>
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
      {spec.params.length > 0 && <div className="params">{spec.params.map(renderParam)}</div>}
      {result?.preview && (
        <a className="preview nodrag" href={previewUrl(id, result.preview.version)} target="_blank" rel="noreferrer">
          <img src={previewUrl(id, result.preview.version)} alt={`Imagem de ${spec.title}`} />
          <span>
            {result.preview.width}×{result.preview.height}
          </span>
        </a>
      )}
      {result?.error && <div className="node-error">{result.error}</div>}
      {!result?.error && result?.status && <div className="node-status">{result.status}</div>}
    </div>
  );
}
