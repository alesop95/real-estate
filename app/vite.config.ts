// La costruzione dell'interfaccia, e il modo in cui si lavora in locale.
//
// Due cose meritano una riga di spiegazione, perche' non sono le predefinite e la ragione si
// dimentica in fretta.
//
// La prima e' la cartella di uscita, che e' `statico/` e non `dist/`. Il nome dice che cosa
// contiene, cioe' i file che Cloudflare serve senza far girare il Worker, e tiene distinta
// questa uscita dalla compilazione del Worker, che non passa da qui: il Worker lo costruisce
// wrangler leggendo `main` in wrangler.toml. Sono due catene separate che finiscono nello
// stesso rilascio, ed e' bene che i loro artefatti non si confondano in una cartella sola.
//
// La seconda e' il rimando delle chiamate all'interfaccia di programmazione. In sviluppo
// girano due processi: Vite, che ricostruisce la pagina a ogni salvataggio, e wrangler, che
// esegue il Worker vero con il suo D1 locale. Il modulo chiama `/api/...` come fara' in
// esercizio, e qui quel prefisso viene inoltrato a wrangler: cosi' il codice dell'interfaccia
// non sa di essere in sviluppo e non porta con se' un ramo che in esercizio non serve.

import react from "@vitejs/plugin-react";
import { defineConfig } from "vite";

/** Dove risponde wrangler dev. Cambiarlo qui, non in venti punti del codice. */
const WORKER_LOCALE = "http://127.0.0.1:8787";

export default defineConfig({
  plugins: [react()],
  build: {
    outDir: "statico",
    emptyOutDir: true,
    // Le mappe dei sorgenti non entrano nel rilascio: pubblicherebbero il codice
    // dell'interfaccia in chiaro a chiunque apra gli strumenti del browser, che non e' un
    // danno di sicurezza ma non e' nemmeno qualcosa che si regala a un concorrente, visto
    // che questo strumento si vende.
    sourcemap: false,
  },
  server: {
    proxy: {
      "/api": {
        target: WORKER_LOCALE,
        changeOrigin: false,
      },
    },
  },
});
