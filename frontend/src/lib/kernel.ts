import type { Kernel } from "../types";

export const KERNEL_SIZES = [3, 5, 7, 9] as const;

const fill = (n: number, value: number): Kernel =>
  Array.from({ length: n }, () => Array.from({ length: n }, () => value));

function pascalRow(n: number): number[] {
  return Array.from({ length: n - 1 }).reduce<number[]>(
    (row) => [...row, 0].map((v, i) => v + (i > 0 ? row[i - 1] : 0)),
    [1],
  );
}

// Pesos inteiros: o bloco Convolução divide pela soma dos pesos.
export const KERNEL_PRESETS: Record<string, (n: number) => Kernel> = {
  Identidade: (n) => resizeKernel([[1]], n),
  Média: (n) => fill(n, 1),
  Gaussiana: (n) => {
    const b = pascalRow(n);
    return b.map((x) => b.map((y) => x * y));
  },
  "Laplaciano (4 vizinhos)": (n) =>
    resizeKernel(
      [
        [0, 1, 0],
        [1, -4, 1],
        [0, 1, 0],
      ],
      n,
    ),
  "Laplaciano (8 vizinhos)": (n) =>
    fill(n, 1).map((row, r) => row.map((v, c) => (r === (n - 1) / 2 && c === (n - 1) / 2 ? 1 - n * n : v))),
  "Sobel X": (n) =>
    resizeKernel(
      [
        [-1, 0, 1],
        [-2, 0, 2],
        [-1, 0, 1],
      ],
      n,
    ),
  "Sobel Y": (n) =>
    resizeKernel(
      [
        [-1, -2, -1],
        [0, 0, 0],
        [1, 2, 1],
      ],
      n,
    ),
  Nitidez: (n) =>
    resizeKernel(
      [
        [0, -1, 0],
        [-1, 5, -1],
        [0, -1, 0],
      ],
      n,
    ),
};

export function resizeKernel(kernel: Kernel, n: number): Kernel {
  const offset = (n - kernel.length) / 2;
  return Array.from({ length: n }, (_, r) =>
    Array.from({ length: n }, (_, c) => kernel[r - offset]?.[c - offset] ?? 0),
  );
}

export function setWeight(kernel: Kernel, row: number, col: number, value: number): Kernel {
  return kernel.map((line, r) => (r === row ? line.map((v, c) => (c === col ? value : v)) : line));
}

export function kernelSum(kernel: Kernel): number {
  return kernel.flat().reduce((a, b) => a + b, 0);
}

export function isKernel(value: unknown): value is Kernel {
  return (
    Array.isArray(value) &&
    value.length % 2 === 1 &&
    value.every(
      (row) =>
        Array.isArray(row) &&
        row.length === value.length &&
        row.every((v) => typeof v === "number" && Number.isFinite(v)),
    )
  );
}
