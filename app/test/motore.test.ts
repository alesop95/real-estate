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
import { confronta } from "./confronto";
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
