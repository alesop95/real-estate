// Le prove che girano in Node: aritmetica, moduli puri e interfaccia.
//
// L'elenco dei file e' esplicito e non un ricorsivo su tutta la cartella, e la ragione e' che
// le prove delle rotte non devono finire qui: hanno bisogno del runtime di Cloudflare e di un
// D1 vero, e le raccoglie vitest.workers.config.ts. Un ricorsivo le prenderebbe entrambe, e
// fallirebbero per il motivo sbagliato.
//
// L'ambiente resta Node anche per le prove dell'interfaccia: quelle che hanno bisogno di un
// documento lo dichiarano da se' con la riga "@vitest-environment jsdom" in testa al file.
// Dichiararlo per tutti farebbe girare dentro un finto browser anche il motore di calcolo, che
// non ne ha bisogno e che in esercizio gira dove il browser non c'e'.

import { defineConfig } from "vitest/config";

export default defineConfig({
  test: {
    include: ["test/*.test.ts", "test/interfaccia/*.test.ts", "test/interfaccia/*.test.tsx"],
    reporters: "default",
  },
  esbuild: {
    // I componenti si scrivono in JSX e nessun file importa React per nome: e' la
    // trasformazione moderna, la stessa che usa la costruzione di Vite.
    jsx: "automatic",
  },
});
