import type { NodeResult, NodeTypeSpec, UploadResult, WorkflowPayload, WorkflowResult } from "../types";

export class ApiError extends Error {
  constructor(
    message: string,
    readonly status: number,
  ) {
    super(message);
  }
}

async function request<T>(path: string, init?: RequestInit): Promise<T> {
  const resp = await fetch(`/api${path}`, init);
  if (!resp.ok) {
    const body = await resp.json().catch(() => null);
    const detail = typeof body?.detail === "string" ? body.detail : resp.statusText;
    throw new ApiError(detail, resp.status);
  }
  return (await resp.json()) as T;
}

export function fetchNodeTypes(): Promise<NodeTypeSpec[]> {
  return request<NodeTypeSpec[]>("/node-types");
}

export function putWorkflow(payload: WorkflowPayload, signal?: AbortSignal): Promise<WorkflowResult> {
  return request<WorkflowResult>("/workflow", {
    method: "PUT",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify(payload),
    signal,
  });
}

export function uploadImage(file: File): Promise<UploadResult> {
  const form = new FormData();
  form.append("file", file);
  return request<UploadResult>("/images", { method: "POST", body: form });
}

export function triggerAction(nodeId: string, action: string): Promise<NodeResult> {
  return request<NodeResult>(`/nodes/${encodeURIComponent(nodeId)}/actions/${encodeURIComponent(action)}`, {
    method: "POST",
  });
}

/** URL da imagem exibida no nó; `version` muda quando a imagem muda (recarrega só então). */
export function previewUrl(nodeId: string, version: number): string {
  return `/api/nodes/${encodeURIComponent(nodeId)}/preview.png?v=${version}`;
}
