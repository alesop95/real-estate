// Le prove del documento delle ipotesi, cioe' della struttura che tutte e sei le aree scrivono.
//
// Sono la controparte di una scelta di forma: la conservazione di cio' che un'area non conosce
// non e' affidata alla disciplina di chi scrive un'area nuova, e' l'unico comportamento possibile
// di `conSezione`. Queste prove verificano che lo sia davvero, ai due livelli in cui una perdita
// e' possibile, cioe' fra le sezioni e dentro una sezione.
//
// Il difetto che coprono non fallisce: un'area che salvando cancellasse il lavoro di un'altra non
// produrrebbe nessun errore, soltanto numeri tornati ai predefiniti la volta dopo. E' lo stesso
// carattere del riferimento per coordinata di cella che ADR-013 ha isolato nel workbook.

import { describe, expect, it } from "vitest";

import {
  COSTI_PREDEFINITI,
  conSezione,
  conSezioni,
  leggiCosti,
  leggiFinanziamento,
  leggiGestione,
  leggiRegime,
  leggiVerifiche,
  REGIME_PREDEFINITO,
  SEZIONE,
} from "../src/condiviso/ipotesi";
import {
  ACQUIRENTE_PREDEFINITO,
  FINANZIAMENTO_PREDEFINITO,
  GESTIONE_PREDEFINITA,
} from "../src/condiviso/predefiniti.generate";
import { costoOperazione } from "../src/motore/motore";
import type { Acquirente, Immobile } from "../src/motore/tipi";

const IMMOBILE: Immobile = {
  prezzo: 180_000,
  rendita_catastale: 620,
  categoria: "A/2",
  superficie_mq: 85,
  comune: "Civitanova Marche",
  nuova_costruzione: false,
  venditore_impresa: false,
};

describe("la scrittura di una sezione conserva tutto il resto", () => {
  it("non tocca le sezioni delle altre aree", () => {
    const prima = {
      [SEZIONE.finanziamento]: { importo: 120_000 },
      [SEZIONE.gestione]: { canone_mensile: 650 },
    };
    const dopo = conSezione(prima, SEZIONE.regime, { prima_casa: false });
    expect(dopo[SEZIONE.finanziamento]).toEqual({ importo: 120_000 });
    expect(dopo[SEZIONE.gestione]).toEqual({ canone_mensile: 650 });
  });

  it("non tocca le chiavi di primo livello che nessuna sezione dichiara", () => {
    const dopo = conSezione({ scritto_da_una_versione_futura: 7 }, SEZIONE.costo, { altri_costi: 900 });
    expect(dopo.scritto_da_una_versione_futura).toBe(7);
  });

  it("conserva anche i campi sconosciuti dentro la sezione che tocca", () => {
    // E' il secondo livello, ed e' quello che si dimentica: un'area che riscrivesse la propria
    // sezione per intero cancellerebbe un campo aggiunto da una versione piu' recente
    // dell'applicazione, che e' esattamente il caso di due persone su due schede diverse.
    const prima = { [SEZIONE.costo]: { altri_costi: 900, campo_futuro: "da tenere" } };
    const dopo = conSezione(prima, SEZIONE.costo, { altri_costi: 1_100 });
    expect(dopo[SEZIONE.costo]).toEqual({ altri_costi: 1_100, campo_futuro: "da tenere" });
  });

  it("scrive piu' sezioni in un colpo solo senza perdere niente", () => {
    const dopo = conSezioni({ altro: 1 }, {
      [SEZIONE.regime]: { prima_casa: false },
      [SEZIONE.costo]: { altri_costi: 500 },
    });
    expect(Object.keys(dopo).sort()).toEqual([SEZIONE.costo, SEZIONE.regime, "altro"].sort());
  });

  it("un giro completo di lettura e scrittura non perde e non inventa nulla", () => {
    const originali = {
      [SEZIONE.regime]: { prima_casa: false, prezzo_valore: false, venditore_impresa: true, nuova_costruzione: true },
      [SEZIONE.costo]: { provvigione_aliquota: 0.02, notaio_compravendita: 2_200, altri_costi: 300 },
      [SEZIONE.finanziamento]: { ...FINANZIAMENTO_PREDEFINITO, importo: 120_000 },
      terze_parti: { chiunque: "non si tocca" },
    };
    const primo = conSezioni(originali, {
      [SEZIONE.regime]: leggiRegime(originali),
      [SEZIONE.costo]: leggiCosti(originali),
      [SEZIONE.finanziamento]: leggiFinanziamento(originali),
    });
    const secondo = conSezioni(primo, {
      [SEZIONE.regime]: leggiRegime(primo),
      [SEZIONE.costo]: leggiCosti(primo),
      [SEZIONE.finanziamento]: leggiFinanziamento(primo),
    });
    expect(secondo).toEqual(primo);
    expect(primo.terze_parti).toEqual(originali.terze_parti);
  });
});

describe("la lettura tollera un documento scritto da un'altra versione", () => {
  it("un documento assente da' i predefiniti", () => {
    expect(leggiRegime({})).toEqual(REGIME_PREDEFINITO);
    expect(leggiCosti({})).toEqual(COSTI_PREDEFINITI);
    expect(leggiFinanziamento({})).toEqual(FINANZIAMENTO_PREDEFINITO);
    expect(leggiGestione({})).toEqual(GESTIONE_PREDEFINITA);
  });

  it("una sezione scritta male non rompe la scheda", () => {
    expect(leggiRegime({ [SEZIONE.regime]: "si" }).prima_casa).toBe(REGIME_PREDEFINITO.prima_casa);
    expect(leggiRegime({ [SEZIONE.regime]: ["no"] }).prima_casa).toBe(REGIME_PREDEFINITO.prima_casa);
    expect(leggiRegime({ [SEZIONE.regime]: { prima_casa: "forse" } }).prima_casa).toBe(
      REGIME_PREDEFINITO.prima_casa,
    );
  });

  it("un numero che non e' un numero finito non entra nel calcolo", () => {
    // Un valore infinito o non numerico attraverserebbe l'aritmetica senza fallire e
    // comparirebbe come un trattino in fondo a una colonna, dopo aver contaminato ogni somma.
    expect(leggiFinanziamento({ [SEZIONE.finanziamento]: { importo: "centomila" } }).importo).toBe(0);
    expect(leggiCosti({ [SEZIONE.costo]: { altri_costi: Number.POSITIVE_INFINITY } }).altri_costi).toBe(0);
  });

  it("scarta gli esiti di verifiche che il catalogo non conosce piu'", () => {
    const letti = leggiVerifiche({
      [SEZIONE.verifiche]: {
        v01: { stato: "fatto", note: "ok" },
        verifica_sparita: { stato: "fatto", note: "resto di una versione vecchia" },
      },
    });
    expect(Object.keys(letti)).toEqual(["v01"]);
  });

  it("scarta uno stato che non esiste invece di mostrarlo", () => {
    expect(leggiVerifiche({ [SEZIONE.verifiche]: { v01: { stato: "quasi" } } })).toEqual({});
  });
});

describe("i predefiniti non sono una seconda verita'", () => {
  it("il regime predefinito segue l'acquirente predefinito del motore", () => {
    expect(REGIME_PREDEFINITO.prima_casa).toBe(ACQUIRENTE_PREDEFINITO.prima_casa);
    expect(REGIME_PREDEFINITO.prezzo_valore).toBe(ACQUIRENTE_PREDEFINITO.prezzo_valore);
  });

  it("i costi predefiniti coincidono con quelli che il motore usa quando non glieli si passa", () => {
    // E' la prova che tiene insieme COSTI_PREDEFINITI e i valori predefiniti degli argomenti di
    // `costoOperazione`, che il generatore non puo' emettere perche' non sono campi di una
    // dataclass. Senza di essa la coincidenza resterebbe affidata all'occhio, e il giorno in cui
    // uno dei due cambiasse l'interfaccia mostrerebbe un costo diverso da quello del motore.
    const acquirente: Acquirente = { ...ACQUIRENTE_PREDEFINITO };
    const senza = costoOperazione(IMMOBILE, acquirente, FINANZIAMENTO_PREDEFINITO);
    const con = costoOperazione(
      IMMOBILE,
      acquirente,
      FINANZIAMENTO_PREDEFINITO,
      COSTI_PREDEFINITI.provvigione_aliquota,
      COSTI_PREDEFINITI.notaio_compravendita,
      COSTI_PREDEFINITI.altri_costi,
    );
    expect(con).toEqual(senza);
  });
});
