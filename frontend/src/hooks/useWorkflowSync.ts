import { useEffect, useMemo } from "react";

import { putWorkflow } from "../api/client";
import { toPayload } from "../lib/payload";
import { useWorkflow } from "../store/workflow";

const DEBOUNCE_MS = 150;

/** Envia o fluxo ao backend quando nós, valores ou ligações mudam (não ao mover blocos).
 *  Requisições antigas são canceladas: só a resposta mais recente é aplicada. */
export function useWorkflowSync(onError: (message: string | null) => void): void {
  const nodes = useWorkflow((s) => s.nodes);
  const edges = useWorkflow((s) => s.edges);
  const ready = useWorkflow((s) => Object.keys(s.types).length > 0);
  const setResults = useWorkflow((s) => s.setResults);

  const body = useMemo(() => JSON.stringify(toPayload(nodes, edges)), [nodes, edges]);

  useEffect(() => {
    if (!ready) return;
    const controller = new AbortController();
    const timer = setTimeout(() => {
      putWorkflow(JSON.parse(body), controller.signal)
        .then((result) => {
          setResults(result);
          onError(null);
        })
        .catch((e: Error) => {
          if (e.name !== "AbortError") onError(`Erro ao executar o fluxo: ${e.message}`);
        });
    }, DEBOUNCE_MS);
    return () => {
      clearTimeout(timer);
      controller.abort();
    };
  }, [body, ready, setResults, onError]);
}
