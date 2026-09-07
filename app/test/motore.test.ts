// Verifica del motore TypeScript contro i vettori generati dal motore Python.
//
// Questa suite e' il presidio che rende accettabile avere due implementazioni dello stesso
// modello. Non contiene numeri scritti a mano: prende i casi e gli esiti attesi da
// app/test/vettori.generati.json, che `python tools/genera-motore.py` produce eseguendo il
// motore Python, e confronta ogni singolo valore. Se un vettore fallisce, la risposta non e'
// allargare la tolleranza: e' capire quale delle due implementazioni fa una cosa diversa,
// sapendo che il riferimento e' Python fino a prova contraria.
//
// I vettori scadono. Dopo aver toccato parametri.py o calcoli.py vanno rigenerati, e
// `python tools/genera-motore.py --check` lo dice senza scrivere niente.

import { describe, expect, it } from "vitest";

import { esitoCompleto, type Ingresso } from "../src/motore/esito";
import { REVISIONE } from "../src/motore/parametri.generati";
import vettori from "./vettori.generati.json";

type Documento = {
  generatoDa: string;
  revisioneParametri: string;
  tolleranzaRelativa: number;
  tolleranzaAssoluta: number;
  casi: number;
  vettori: { n: number; ingresso: Ingresso; atteso: unknown }[];
};

const documento = vettori as unknown as Documento;

/** Gli infiniti non esistono in JSON: il generatore li scrive come stringhe. */
function normalizza(valore: unknown): unknown {
  if (valore === "Infinity") return Infinity;
  if (valore === "-Infinity") return -Infinity;
  return valore;
}

/**
 * Confronta due esiti scendendo in ogni ramo, e riporta il percorso del primo scarto.
 *
 * Il percorso conta piu' del valore: su duecentoundici casi e un centinaio di grandezze
 * ciascuno, un messaggio che dice soltanto "atteso 1234 trovato 1235" costringe a cercare a
 * mano quale voce sia. Riportare "conto.imposta" indica subito la funzione da guardare.
 */
function confronta(
  atteso: unknown,
  trovato: unknown,
  percorso: string,
  scarti: string[],
  tolleranzaRelativa: number,
  tolleranzaAssoluta: number,
): void {
  const a = normalizza(atteso);

  if (typeof a === "number" && typeof trovato === "number") {
    if (Number.isNaN(a) || Number.isNaN(trovato)) {
      if (!(Number.isNaN(a) && Number.isNaN(trovato))) {
        scarti.push(`${percorso}: atteso ${a}, trovato ${trovato}`);
      }
      return;
    }
    if (!Number.isFinite(a) || !Number.isFinite(trovato)) {
      if (a !== trovato) scarti.push(`${percorso}: atteso ${a}, trovato ${trovato}`);
      return;
    }
    const scarto = Math.abs(a - trovato);
    const ammesso = Math.abs(a) > 1 ? Math.abs(a) * tolleranzaRelativa : tolleranzaAssoluta;
    if (scarto > ammesso) {
      scarti.push(`${percorso}: atteso ${a}, trovato ${trovato}, scarto ${scarto.toExponential(3)}`);
    }
    return;
  }

  if (a !== null && typeof a === "object") {
    if (trovato === null || typeof trovato !== "object") {
      scarti.push(`${percorso}: atteso un oggetto, trovato ${String(trovato)}`);
      return;
    }
    const chiavi = Object.keys(a as Record<string, unknown>);
    for (const chiave of chiavi) {
      confronta(
        (a as Record<string, unknown>)[chiave],
        (trovato as Record<string, unknown>)[chiave],
        percorso ? `${percorso}.${chiave}` : chiave,
        scarti,
        tolleranzaRelativa,
        tolleranzaAssoluta,
      );
    }
    // Una chiave in piu' da questo lato non e' un errore di calcolo, ma e' un segnale che
    // le due implementazioni non descrivono piu' la stessa cosa, quindi va detto.
    for (const chiave of Object.keys(trovato as Record<string, unknown>)) {
      if (!chiavi.includes(chiave)) {
        scarti.push(`${percorso}.${chiave}: presente in TypeScript e assente nei vettori`);
      }
    }
    return;
  }

  if (a !== trovato) {
    scarti.push(`${percorso}: atteso ${JSON.stringify(a)}, trovato ${JSON.stringify(trovato)}`);
  }
}

describe("motore TypeScript contro i vettori del motore Python", () => {
  it("usa i parametri della stessa revisione con cui i vettori sono stati generati", () => {
    // Se questo test fallisce i vettori sono scaduti, e tutti gli altri direbbero cose
    // sbagliate su un modello vecchio: va rilanciato il generatore.
    expect(REVISIONE).toBe(documento.revisioneParametri);
  });

  it("ha un campione di casi non banale", () => {
    expect(documento.vettori.length).toBe(documento.casi);
    expect(documento.vettori.length).toBeGreaterThan(100);
  });

  it("il confronto sa fallire: un valore alterato viene visto", () => {
    // Controllo negativo, e non e' una formalita'. Una suite che confronta duecento casi e
    // li dichiara tutti uguali va sospettata prima di essere creduta: se il confronto
    // scendesse nel ramo sbagliato, o se i vettori arrivassero vuoti, il verde sarebbe
    // indistinguibile da quello vero. Qui si prende un vettore, si altera l'atteso di poco
    // piu' della tolleranza, e si pretende che lo scarto venga riportato col suo percorso.
    const vettore = documento.vettori[0];
    const trovato = esitoCompleto(vettore.ingresso);
    const attesoGuasto = JSON.parse(JSON.stringify(vettore.atteso)) as Record<string, any>;
    attesoGuasto.conto.imposta = attesoGuasto.conto.imposta + 0.001;
    attesoGuasto.imposte.regime = "un regime che non esiste";

    const scarti: string[] = [];
    confronta(attesoGuasto, trovato, "", scarti, documento.tolleranzaRelativa, documento.tolleranzaAssoluta);

    expect(scarti.length).toBe(2);
    expect(scarti.some((s) => s.startsWith("conto.imposta:"))).toBe(true);
    expect(scarti.some((s) => s.startsWith("imposte.regime:"))).toBe(true);

    // E sullo stesso vettore non alterato non deve trovare niente, altrimenti il test
    // precedente passerebbe per la ragione sbagliata.
    const nessuno: string[] = [];
    confronta(vettore.atteso, trovato, "", nessuno, documento.tolleranzaRelativa, documento.tolleranzaAssoluta);
    expect(nessuno).toEqual([]);
  });

  it("riproduce ogni vettore entro la tolleranza dichiarata", () => {
    const fallimenti: string[] = [];
    for (const vettore of documento.vettori) {
      const scarti: string[] = [];
      const trovato = esitoCompleto(vettore.ingresso);
      confronta(
        vettore.atteso,
        trovato,
        "",
        scarti,
        documento.tolleranzaRelativa,
        documento.tolleranzaAssoluta,
      );
      if (scarti.length) {
        const g = vettore.ingresso.gestione;
        const i = vettore.ingresso.immobile;
        const contesto = `caso ${vettore.n} [${i.venditore_impresa ? "impresa" : "privato"}, ${i.categoria}, ${g.regime}, mutuo ${vettore.ingresso.finanziamento.importo}]`;
        fallimenti.push(`${contesto}\n    ${scarti.join("\n    ")}`);
      }
    }
    expect(fallimenti.join("\n  "), `${fallimenti.length} casi su ${documento.vettori.length} divergono`).toBe("");
  });
});
