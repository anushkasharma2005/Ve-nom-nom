// vite.config.js
import { defineConfig } from "vite";
import react from "@vitejs/plugin-react";

// https://vitejs.dev/config/
export default defineConfig({
  plugins: [react()],

  server: {
    port: 5173,
    proxy: {
      // In dev, proxy /health and /predict to FastAPI
      "/health":  "http://localhost:7860",
      "/predict": "http://localhost:7860",
    },
  },

  build: {
    // Output to backend/static so FastAPI can serve it as static files
    outDir: "../backend/static",
    emptyOutDir: true,
  },
});
