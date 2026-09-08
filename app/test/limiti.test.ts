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

  it("l'identificativo del database non e' rimasto un segnaposto in una distribuzione", () => {
    // Finche' si lavora in locale il segnaposto va benissimo, ed e' anzi la prova che
    // nessun account e' stato ancora aperto. Il test non lo vieta: dichiara la condizione,
    // cosi' che il giorno della prima distribuzione il messaggio dica che cosa manca.
    const segnaposto = configurazione.includes('database_id = "da-compilare-alla-creazione"');
    const inLocale = process.env.CI !== "true";
    expect(
      !segnaposto || inLocale,
      "prima di distribuire va scritto l'identificativo vero del database D1",
    ).toBe(true);
  });
});
