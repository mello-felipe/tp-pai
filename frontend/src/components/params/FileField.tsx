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
    <div className="param">
      <span>{param.label}</span>
      {/* input nativo escondido: o rótulo vira o botão (texto em português, sem "No file chosen") */}
      <label className={`file-button nodrag${busy ? " busy" : ""}`}>
        <input type="file" accept="image/png,.png" disabled={busy} onChange={onChange} />
        {busy ? "Enviando…" : fileName ? "Trocar PNG…" : "Escolher PNG…"}
      </label>
      {fileName && !busy && (
        <span className="file-name" title={fileName}>
          {fileName}
        </span>
      )}
      {error && <span className="node-error">{error}</span>}
    </div>
  );
}
