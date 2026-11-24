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
  | "kernel"
  | "action";

export type Kernel = number[][];

export type ParamValue = number | string | boolean | Kernel;

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

export interface ImageMeta {
  version: number;
  width: number;
  height: number;
  channels: number;
}

export interface NodeResult {
  error: string | null;
  status: string;
  outputs: Record<string, ImageMeta | null>;
  preview: ImageMeta | null;
}

export interface LinkPayload {
  src: string;
  src_port: string;
  dst: string;
  dst_port: string;
}

export interface RejectedLink extends LinkPayload {
  error: string;
}

export interface WorkflowPayload {
  nodes: { id: string; type: string; values: Record<string, ParamValue> }[];
  links: LinkPayload[];
}

export interface WorkflowResult {
  nodes: Record<string, NodeResult>;
  rejected_links: RejectedLink[];
}

export interface UploadResult {
  path: string;
  name: string;
  width: number;
  height: number;
}
