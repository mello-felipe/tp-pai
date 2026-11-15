import type { ParamSpec, ParamValue } from "../../types";

interface Props {
  param: ParamSpec;
  value: ParamValue | undefined;
  onChange: (value: ParamValue) => void;
}

/** Widget de um parâmetro, escolhido pelo `kind` do NodeSpec.
 *  "nodrag" impede que mexer no widget arraste o bloco. */
export function ParamField({ param, value, onChange }: Props) {
  const id = `param-${param.name}`;
  switch (param.kind) {
    case "int":
    case "float": {
      const num = Number(value ?? param.default ?? 0);
      return (
        <label className="param" htmlFor={id}>
          <span>
            {param.label}: <b>{param.kind === "float" ? num.toFixed(2) : num}</b>
          </span>
          <input
            id={id}
            className="nodrag"
            type="range"
            min={param.min ?? 0}
            max={param.max ?? 100}
            step={param.kind === "int" ? 1 : ((param.max ?? 1) - (param.min ?? 0)) / 100}
            value={num}
            onChange={(e) => onChange(Number(e.target.value))}
          />
        </label>
      );
    }
    case "choice":
      return (
        <label className="param" htmlFor={id}>
          <span>{param.label}</span>
          <select
            id={id}
            className="nodrag"
            value={String(value ?? param.default)}
            onChange={(e) => onChange(e.target.value)}
          >
            {param.choices.map((c) => (
              <option key={c} value={c}>
                {c}
              </option>
            ))}
          </select>
        </label>
      );
    case "bool":
      return (
        <label className="param inline" htmlFor={id}>
          <input
            id={id}
            className="nodrag"
            type="checkbox"
            checked={Boolean(value ?? param.default)}
            onChange={(e) => onChange(e.target.checked)}
          />
          <span>{param.label}</span>
        </label>
      );
    case "text":
    case "dir":
    case "file_save":
      return (
        <label className="param" htmlFor={id}>
          <span>{param.label}</span>
          <input
            id={id}
            className="nodrag"
            type="text"
            placeholder={param.hint}
            value={String(value ?? "")}
            onChange={(e) => onChange(e.target.value)}
          />
        </label>
      );
    default:
      return null; // "file_open" e "action" dependem da API (upload e ações)
  }
}
