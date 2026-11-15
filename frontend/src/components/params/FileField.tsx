import { useState, type ChangeEvent } from "react";

import { uploadImage } from "../../api/client";
import type { ParamSpec } from "../../types";

interface Props {
  param: ParamSpec;
  fileName: string | undefined;
  onUploaded: (path: string, fileName: string) => void;
}

/** "file_open": escolhe um PNG no navegador e envia ao backend (POST /api/images). */
export function FileField({ param, fileName, onUploaded }: Props) {
  const [busy, setBusy] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const onChange = async (event: ChangeEvent<HTMLInputElement>) => {
    const file = event.target.files?.[0];
    event.target.value = ""; // permite escolher o mesmo arquivo de novo
    if (!file) return;
    setBusy(true);
    setError(null);
    try {
      const result = await uploadImage(file);
      onUploaded(result.path, result.name);
    } catch (e) {
      setError(e instanceof Error ? e.message : "falha no envio");
    } finally {
      setBusy(false);
    }
  };

  return (
    <label className="param">
      <span>{param.label}</span>
      <span className="file nodrag">
        <input type="file" accept="image/png,.png" disabled={busy} onChange={onChange} />
        <span className="file-name">{busy ? "enviando…" : (fileName ?? "nenhum arquivo")}</span>
      </span>
      {error && <span className="node-error">{error}</span>}
    </label>
  );
}
