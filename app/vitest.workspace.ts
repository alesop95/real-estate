// Due gruppi di prove con due esigenze diverse: l'aritmetica in Node, le rotte in workerd.
import { defineWorkspace } from "vitest/config";

export default defineWorkspace(["./vitest.config.ts", "./vitest.workers.config.ts"]);
