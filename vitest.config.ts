import { defineConfig } from "vitest/config";
import react from "@vitejs/plugin-react";
import path from "path";

export default defineConfig({
  plugins: [react()],
  resolve: {
    alias: {
      "@worker": path.resolve(__dirname, "./worker"),
    },
  },
  test: {
    globals: true,
    environment: "jsdom",
  },
});
