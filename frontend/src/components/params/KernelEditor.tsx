import { useEffect, useState } from "react";

import { isKernel, KERNEL_PRESETS, KERNEL_SIZES, kernelSum, resizeKernel, setWeight } from "../../lib/kernel";
import type { Kernel, ParamSpec } from "../../types";

interface Props {
  param: ParamSpec;
  value: unknown;
  onChange: (kernel: Kernel) => void;
}

const IDENTITY: Kernel = KERNEL_PRESETS["Identidade"](3);

export function KernelEditor({ param, value, onChange }: Props) {
  const kernel = isKernel(value) ? value : isKernel(param.default) ? param.default : IDENTITY;
  const n = kernel.length;
  const clamp = (v: number) => Math.min(param.max ?? Infinity, Math.max(param.min ?? -Infinity, v));

  return (
    <div className="param kernel">
      <span>{param.label}</span>
      <div className="kernel-controls">
        <select
          className="nodrag"
          aria-label="Tamanho da máscara"
          value={n}
          onChange={(e) => onChange(resizeKernel(kernel, Number(e.target.value)))}
        >
          {KERNEL_SIZES.map((s) => (
            <option key={s} value={s}>
              {s}×{s}
            </option>
          ))}
        </select>
        <select
          className="nodrag"
          aria-label="Preencher com máscara conhecida"
          value=""
          onChange={(e) => e.target.value && onChange(KERNEL_PRESETS[e.target.value](n))}
        >
          <option value="">Preencher com…</option>
          {Object.keys(KERNEL_PRESETS).map((name) => (
            <option key={name} value={name}>
              {name}
            </option>
          ))}
        </select>
      </div>
      <div className="kernel-grid nodrag" style={{ gridTemplateColumns: `repeat(${n}, 1fr)` }}>
        {kernel.map((row, r) =>
          row.map((w, c) => (
            <KernelCell
              key={`${r}-${c}`}
              value={w}
              label={`Peso linha ${r + 1}, coluna ${c + 1}`}
              onCommit={(v) => onChange(setWeight(kernel, r, c, clamp(v)))}
            />
          )),
        )}
      </div>
      <span className="kernel-sum">soma dos pesos: {Number(kernelSum(kernel).toFixed(4))}</span>
    </div>
  );
}

interface CellProps {
  value: number;
  label: string;
  onCommit: (value: number) => void;
}

// Guarda o texto digitado para permitir estados intermediários como "-" e "0.".
function KernelCell({ value, label, onCommit }: CellProps) {
  const [draft, setDraft] = useState(String(value));
  useEffect(() => setDraft(String(value)), [value]);

  const commit = () => {
    const num = Number(draft.replace(",", "."));
    if (draft.trim() !== "" && Number.isFinite(num)) onCommit(num);
    else setDraft(String(value));
  };

  return (
    <input
      type="text"
      inputMode="decimal"
      aria-label={label}
      value={draft}
      onChange={(e) => setDraft(e.target.value)}
      onBlur={commit}
      onKeyDown={(e) => e.key === "Enter" && e.currentTarget.blur()}
    />
  );
}
