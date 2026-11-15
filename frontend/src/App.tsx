import { ReactFlowProvider } from "@xyflow/react";
import { useEffect, useState } from "react";

import { fetchNodeTypes } from "./api/client";
import { Canvas } from "./components/Canvas";
import { Palette } from "./components/Palette";
import { useWorkflowSync } from "./hooks/useWorkflowSync";
import { useWorkflow } from "./store/workflow";

export function App() {
  const setTypes = useWorkflow((s) => s.setTypes);
  const [error, setError] = useState<string | null>(null);
  useWorkflowSync(setError);

  useEffect(() => {
    fetchNodeTypes()
      .then(setTypes)
      .catch((e: Error) => setError(`Backend indisponível: ${e.message}`));
  }, [setTypes]);

  return (
    <ReactFlowProvider>
      <div className="app">
        <Palette />
        <Canvas />
      </div>
      {error && <div className="banner error">{error}</div>}
    </ReactFlowProvider>
  );
}
