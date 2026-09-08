// Configurazione delle prove che girano dentro il runtime di Cloudflare.
//
// Il motore di calcolo si prova in Node, perche' e' aritmetica e non ha bisogno di altro.
// Le rotte no: hanno bisogno di un D1 vero, di un oggetto Request vero e delle stesse
// interfacce che troveranno in esercizio. Provarle contro un finto database darebbe una
// suite verde che non dice niente sul comportamento reale, e in particolare non direbbe
// nulla sui vincoli di integrita', che sono meta' della difesa.
//
// Questa configurazione fa girare i test dentro workerd, cioe' il runtime che Cloudflare
// esegue davvero, con un D1 locale creato per l'occasione. Non serve alcun account e non
// esce niente in rete.

import { defineWorkersConfig, readD1Migrations } from "@cloudflare/vitest-pool-workers/config";

const migrazioni = await readD1Migrations("./migrazioni");

export default defineWorkersConfig({
  test: {
    include: ["test/server/**/*.test.ts"],
    setupFiles: ["./test/server/prepara.ts"],
    poolOptions: {
      workers: {
        singleWorker: true,
        wrangler: { configPath: "./wrangler.toml" },
        miniflare: {
          compatibilityDate: "2024-12-05",
          // Le migrazioni arrivano ai test come una variabile: le applica il file di
          // preparazione, prima di ogni prova, su un database pulito.
          bindings: { MIGRAZIONI: migrazioni },
        },
      },
    },
  },
});
