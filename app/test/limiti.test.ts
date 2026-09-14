// Il presidio della gratuita': un test che fallisce se la configurazione esce dal piano libero.
//
// Lo studio dell'architettura lo prevede fra le cose da costruire insieme allo scheletro, e
// la ragione e' scritta la': il vincolo non si viola con una decisione, si viola con una
// comodita'. Nessuno deciderebbe mai di "passare al piano a pagamento"; qualcuno aggiungera'
// una coda per spedire una notifica, o un bucket per tenere una planimetria, e la fattura
// arrivera' come conseguenza di un gesto che sembrava piccolo.
//
// Il test legge la configurazione del Worker e verifica tre cose: che non compaiano servizi
// fuori dal piano gratuito, che le attivazioni pianificate non superino le cinque concesse
// per account, e che nessuna dipendenza tiri dentro un prodotto a pagamento. Non e' una
// difesa contro un malintenzionato: e' una sveglia per chi lavora, e come tutte le sveglie
// vale solo se suona prima e non dopo.
//
// Sta fra le prove che girano in Node e non fra quelle dentro il runtime di Cloudflare,
// perche' legge file da disco e in un Worker il filesystem non esiste: e' la stessa ragione
// per cui in esercizio la configurazione non si puo' ispezionare da dentro l'applicazione.

import { readFileSync } from "node:fs";
import { describe, expect, it } from "vitest";

const configurazione = readFileSync(new URL("../wrangler.toml", import.meta.url), "utf8");
const manifesto = JSON.parse(readFileSync(new URL("../package.json", import.meta.url), "utf8")) as {
  dependencies?: Record<string, string>;
  devDependencies?: Record<string, string>;
};

/**
 * Il segnaposto dell'identificativo del database, scritto una volta sola.
 *
 * Lo stesso letterale compare in app/wrangler.toml e nel passo che distribuisce: tenerlo qui e
 * confrontarlo evita che i tre si allontanino, cioe' che il flusso cerchi una stringa che nel
 * file non c'e' piu' e lasci passare una distribuzione verso un database inesistente.
 */
const SEGNAPOSTO_DATABASE = "da-compilare-alla-creazione";

/** Sezioni della configurazione che implicano un prodotto fuori dal piano gratuito. */
const FUORI_DAL_GRATUITO = [
  { chiave: "[[queues.producers]]", prodotto: "Queues" },
  { chiave: "[[queues.consumers]]", prodotto: "Queues" },
  { chiave: "[[durable_objects", prodotto: "Durable Objects con SQLite" },
  { chiave: "[[hyperdrive]]", prodotto: "Hyperdrive" },
  { chiave: "[[vectorize]]", prodotto: "Vectorize" },
  { chiave: "[[mtls_certificates]]", prodotto: "certificati mTLS" },
  { chiave: "[[analytics_engine_datasets]]", prodotto: "Analytics Engine" },
  { chiave: "logpush", prodotto: "Logpush" },
];

describe("il piano gratuito, presidiato", () => {
  it("la configurazione non dichiara servizi a pagamento", () => {
    for (const { chiave, prodotto } of FUORI_DAL_GRATUITO) {
      expect(configurazione.includes(chiave), `configurazione: compare ${prodotto} (${chiave})`).toBe(false);
    }
  });

  it("le attivazioni pianificate stanno entro le cinque per account", () => {
    // Il piano gratuito ne concede cinque. Superarle non produce un addebito, produce un
    // rifiuto alla distribuzione, ed e' meglio saperlo qui che davanti al terminale.
    const espressioni = configurazione.match(/crons\s*=\s*\[([^\]]*)\]/);
    const quante = espressioni ? espressioni[1].split(",").filter((v) => v.trim().length > 2).length : 0;
    expect(quante).toBeLessThanOrEqual(5);
  });

  it("nessuna dipendenza tira dentro un prodotto a pagamento", () => {
    const tutte = { ...(manifesto.dependencies ?? {}), ...(manifesto.devDependencies ?? {}) };
    const sospette = Object.keys(tutte).filter((nome) =>
      ["@cloudflare/ai", "@cloudflare/puppeteer", "@cloudflare/workers-ai"].includes(nome),
    );
    expect(sospette, `dipendenze fuori dal piano gratuito: ${sospette.join(", ")}`).toEqual([]);
  });

  it("il database e' dichiarato, con l'identificativo vero o con il segnaposto esatto", () => {
    // Questo test e' stato riscritto il 14 settembre 2026, e la ragione merita di restare
    // perche' riguarda il mestiere di un presidio piu' che questo progetto.
    //
    // La prima versione pretendeva che, quando la variabile CI valeva "true", l'identificativo
    // non fosse piu' il segnaposto. L'intenzione era giusta, l'attuazione no: su CI ci si arriva
    // a ogni spinta, comprese quelle su un branch da cui non si distribuisce niente, quindi il
    // flusso risultava rosso dal 9 settembre a ogni singola corsa, mentre il lavoro di
    // distribuzione veniva correttamente saltato. Il commento sopra diceva "il test non lo
    // vieta: dichiara la condizione", e il codice invece lo vietava: si contraddiceva da solo.
    //
    // Il difetto non e' l'asserzione sbagliata, e' il posto sbagliato. Una prova risponde alla
    // domanda "il codice e' coerente?", che non dipende da dove gira; "siamo pronti a
    // distribuire?" e' una domanda diversa, e la risposta la deve dare il passo che distribuisce,
    // dove un rifiuto blocca cio' che va bloccato invece di colorare di rosso una corsa che non
    // distribuiva nulla. Quel controllo vive ora in .github/workflows/distribuzione.yml, dentro
    // il lavoro di distribuzione. Qui resta cio' che e' davvero una proprieta' della
    // configurazione: che un database sia dichiarato, e che se e' ancora il segnaposto sia quello
    // scritto esattamente cosi', perche' un segnaposto storpiato sfuggirebbe al controllo del
    // flusso e arriverebbe in esercizio.
    //
    // La regola generale, che vale oltre questo file: un presidio che suona a ogni corsa non e'
    // un presidio severo, e' un presidio che si impara a ignorare, e quando suonera' per il
    // motivo vero nessuno lo guardera'.
    const dichiarazione = configurazione.match(/database_id\s*=\s*"([^"]*)"/);
    expect(dichiarazione, "wrangler.toml non dichiara alcun database D1").not.toBeNull();
    const valore = dichiarazione?.[1] ?? "";
    expect(valore.length, "l'identificativo del database e' vuoto").toBeGreaterThan(0);
    if (valore.startsWith("da-compilare")) {
      expect(
        valore,
        "il segnaposto deve restare la stringa esatta che il flusso di distribuzione cerca",
      ).toBe(SEGNAPOSTO_DATABASE);
    }
  });
});
