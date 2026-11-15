import type { NodeTypeSpec } from "../types";

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
