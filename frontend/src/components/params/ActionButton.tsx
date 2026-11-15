import { useState } from "react";

import { triggerAction } from "../../api/client";
import type { NodeResult, ParamSpec } from "../../types";

interface Props {
  nodeId: string;
  param: ParamSpec;
  onResult: (result: NodeResult) => void;
}

/** "action": botão que roda o nó uma vez com o parâmetro ligado (ex.: Salvar). */
export function ActionButton({ nodeId, param, onResult }: Props) {
  const [busy, setBusy] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const onClick = async () => {
    setBusy(true);
    setError(null);
    try {
      onResult(await triggerAction(nodeId, param.name));
    } catch (e) {
      setError(e instanceof Error ? e.message : "falha na ação");
    } finally {
      setBusy(false);
    }
  };

  return (
    <>
      <button type="button" className="action nodrag" disabled={busy} onClick={onClick}>
        {param.label}
      </button>
      {error && <span className="node-error">{error}</span>}
    </>
  );
}
