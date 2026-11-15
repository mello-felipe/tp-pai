// Formato JSON do backend (pse/api/schemas.py).

export type ParamKind =
  | "int"
  | "float"
  | "choice"
  | "bool"
  | "text"
  | "dir"
  | "file_open"
  | "file_save"
  | "action";

export type ParamValue = number | string | boolean;

export interface ParamSpec {
  name: string;
  label: string;
  kind: ParamKind;
  default: ParamValue | null;
  min: number | null;
  max: number | null;
  choices: string[];
  hint: string;
}

export interface NodeTypeSpec {
  key: string;
  title: string;
  category: string;
  description: string;
  inputs: string[];
  outputs: string[];
  params: ParamSpec[];
  preview: string | null;
}
