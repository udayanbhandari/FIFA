/// <reference types="vitest" />
import react from "@vitejs/plugin-react";
import { defineConfig } from "vite";

// https://vitejs.dev/config/
export default defineConfig({
  plugins: [react()],
  build: {
    sourcemap: false, // Security: disable source maps to avoid leaking code structure
  },
  test: {
    globals: true,
    environment: "jsdom",
    setupFiles: "./src/test/setup.ts",
    css: false, // Optimization: disable CSS processing in tests to speed up execution
    coverage: {
      provider: "v8",
      reporter: ["text", "json", "html"],
      thresholds: {
        statements: 90,
        branches: 85,
        functions: 90,
        lines: 90,
      },
      exclude: [
        "src/main.tsx",
        "src/test/**",
        "src/vite-env.d.ts",
        "**/*.d.ts",
        "**/*.test.{ts,tsx}",
        "vite.config.ts",
      ],
    },
  },
});
