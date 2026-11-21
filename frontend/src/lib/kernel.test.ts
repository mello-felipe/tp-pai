import { describe, expect, it } from "vitest";

import { isKernel, KERNEL_PRESETS, kernelSum, resizeKernel, setWeight } from "./kernel";

describe("KERNEL_PRESETS", () => {
  it("monta as máscaras 3x3 conhecidas", () => {
    expect(KERNEL_PRESETS["Média"](3)).toEqual([
      [1, 1, 1],
      [1, 1, 1],
      [1, 1, 1],
    ]);
    expect(KERNEL_PRESETS["Gaussiana"](3)).toEqual([
      [1, 2, 1],
      [2, 4, 2],
      [1, 2, 1],
    ]);
    expect(KERNEL_PRESETS["Laplaciano (8 vizinhos)"](3)).toEqual([
      [1, 1, 1],
      [1, -8, 1],
      [1, 1, 1],
    ]);
  });

  it("gera todas as máscaras no tamanho pedido", () => {
    for (const make of Object.values(KERNEL_PRESETS)) {
      for (const n of [3, 5, 7]) expect(isKernel(make(n)) && make(n).length === n).toBe(true);
    }
  });

  it("Gaussiana 5x5 usa a linha 1 4 6 4 1 e Laplaciano soma zero", () => {
    expect(KERNEL_PRESETS["Gaussiana"](5)[2]).toEqual([6, 24, 36, 24, 6]);
    expect(kernelSum(KERNEL_PRESETS["Laplaciano (8 vizinhos)"](5))).toBe(0);
    expect(kernelSum(KERNEL_PRESETS["Laplaciano (4 vizinhos)"](7))).toBe(0);
  });
});

describe("resizeKernel", () => {
  const k3 = [
    [1, 2, 3],
    [4, 5, 6],
    [7, 8, 9],
  ];

  it("aumenta completando com zeros e mantém o centro", () => {
    const k5 = resizeKernel(k3, 5);
    expect(k5[0]).toEqual([0, 0, 0, 0, 0]);
    expect(k5[2]).toEqual([0, 4, 5, 6, 0]);
  });

  it("diminui cortando as bordas", () => {
    expect(resizeKernel(resizeKernel(k3, 5), 3)).toEqual(k3);
    expect(resizeKernel(k3, 1)).toEqual([[5]]);
  });
});

describe("setWeight", () => {
  it("troca um peso sem mutar a máscara", () => {
    const k = [
      [0, 0],
      [0, 0],
    ];
    expect(setWeight(k, 1, 0, 7)).toEqual([
      [0, 0],
      [7, 0],
    ]);
    expect(k[1][0]).toBe(0);
  });
});

describe("isKernel", () => {
  it("aceita só matrizes quadradas, ímpares e numéricas", () => {
    expect(isKernel([[1]])).toBe(true);
    expect(isKernel([[1, 2], [3, 4]])).toBe(false);
    expect(isKernel([[1, 2, 3]])).toBe(false);
    expect(isKernel([[1, Number.NaN, 0], [0, 0, 0], [0, 0, 0]])).toBe(false);
    expect(isKernel("3x3")).toBe(false);
  });
});
