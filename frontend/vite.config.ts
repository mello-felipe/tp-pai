import react from "@vitejs/plugin-react";
import { defineConfig } from "vite";

// Em desenvolvimento, /api vai para o backend (python -m pse.api): mesma origem, sem CORS.
const API_TARGET = "http://127.0.0.1:8000";

export default defineConfig({
  plugins: [react()],
  server: {
    proxy: { "/api": { target: API_TARGET, changeOrigin: true } },
  },
});
