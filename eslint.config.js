import js from "@eslint/js";
import globals from "globals";
import tseslint from "typescript-eslint";
import eslintReact from "@eslint-react/eslint-plugin";
import reactRefresh from "eslint-plugin-react-refresh";
import { fixupPluginRules } from "@eslint/compat";

export default tseslint.config(
  { ignores: ["dist"] },
  js.configs.recommended,
  ...tseslint.configs.recommended,

  // 1. Let the plugin provide its recommended preset directly
  // This automatically sets up the @eslint-react/dom, /hooks, and /rsc plugins.
  eslintReact.configs.recommended,

  {
    files: ["**/*.{ts,tsx}"],
    ignores: ["tests/**/*.{ts,tsx}", "vitest.config.ts"],
    languageOptions: {
      ecmaVersion: 2020,
      globals: globals.browser,
      parserOptions: {
        // v8+ projectService is significantly faster in ESLint 10
        projectService: true,
        tsconfigRootDir: import.meta.dirname,
      },
    },
    plugins: {
      // 2. We only need to manually add the build-specific plugins here
      "react-refresh": fixupPluginRules(reactRefresh),
    },
    rules: {
      // 3. Keep your custom refresh rules
      "react-refresh/only-export-components": [
        "warn",
        { allowConstantExport: true },
      ],
    },
  },

  {
    // Test files live outside the app/worker tsconfig projects (they're not
    // part of the production build), so they get their own tsconfig here
    // rather than being pulled into `tsc -b`.
    files: ["tests/**/*.{ts,tsx}", "vitest.config.ts"],
    languageOptions: {
      ecmaVersion: 2020,
      globals: { ...globals.browser, ...globals.node },
      parserOptions: {
        project: ["./tsconfig.test.json"],
        tsconfigRootDir: import.meta.dirname,
      },
    },
  },
);
