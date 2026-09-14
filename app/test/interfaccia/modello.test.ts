// Le prove del modello dell'area immobile, cioe' di tutto cio' che in quell'area decide.
//
// Sono prove di funzioni pure e non hanno bisogno di un documento: e' la conseguenza pratica
// della scelta di tenere fuori dal componente ogni regola di dominio. La prova che conta di
// piu' e' la prima, quella sulla conservazione delle ipotesi altrui, perche' copre un difetto
// che non fallisce: un'area che salvando cancellasse il lavoro delle altre non produrrebbe
// nessun errore, soltanto numeri tornati ai predefiniti la volta dopo.

import { describe, expect, it } from "vitest";

import type { Immobile } from "../../src/condiviso/immobile";
import { VERIFICHE } from "../../src/condiviso/verifiche.generate";
import { imposteAcquisto } from "../../src/motore/motore";
import {
  anteprima,
  conVerifica,
  regimeDa,
  schedaDa,
  schedaNuova,
  verificheAperte,
  verificheDa,
  verificheInScheda,
  versoInvio,
  versoMotore,
} from "../../src/sezioni/immobile/modello";

function immobileFinto(ipotesi: Record<string, unknown> = {}): Immobile {
  return {
    id: "i1",
    organizzazione: "o1",
    titolo: "Trilocale via Roma",
    comune: "Civitanova Marche",
    indirizzo: "via Roma 1",
    prezzo: 180_000,
    superficie_mq: 85,
    categoria: "A/2",
    rendita_catastale: 620,
    stato: "da valutare",
    ipotesi,
    creato_il: "2026-09-14T10:00:00.000Z",
    aggiornato_il: "2026-09-14T10:00:00.000Z",
  };
}

describe("il documento delle ipotesi, scritto da piu' aree", () => {
  it("conserva le chiavi che quest'area non conosce", () => {
    const altrui = {
      finanziamento: { importo: 120_000, tasso_annuo: 0.032 },
      gestione: { canone_mensile: 650 },
    };
    const scheda = schedaDa(immobileFinto(altrui));
    const inviato = versoInvio(scheda, altrui);
    expect(inviato.ipotesi.finanziamento).toEqual(altrui.finanziamento);
    expect(inviato.ipotesi.gestione).toEqual(altrui.gestione);
  });

  it("sovrascrive soltanto le due chiavi di competenza", () => {
    const originali = { regime_acquisto: { prima_casa: false }, verifiche: {}, altro: 1 };
    const scheda = schedaDa(immobileFinto(originali));
    const inviato = versoInvio(scheda, originali);
    expect(Object.keys(inviato.ipotesi).sort()).toEqual(["altro", "regime_acquisto", "verifiche"]);
    expect((inviato.ipotesi.regime_acquisto as Record<string, unknown>).prima_casa).toBe(false);
  });

  it("un giro completo non perde e non inventa nulla", () => {
    const originali = {
      regime_acquisto: {
        prima_casa: false,
        prezzo_valore: false,
        venditore_impresa: true,
        nuova_costruzione: true,
      },
      verifiche: { v01: { stato: "fatto", note: "visura del 2 settembre" } },
      terze_parti: { chiunque: "non si tocca" },
    };
    const primo = versoInvio(schedaDa(immobileFinto(originali)), originali);
    const secondo = versoInvio(schedaDa({ ...immobileFinto(primo.ipotesi) }), primo.ipotesi);
    expect(secondo.ipotesi).toEqual(primo.ipotesi);
  });
});

describe("la lettura tollerante di un documento scritto da un'altra versione", () => {
  it("un documento assente da' il regime predefinito", () => {
    expect(regimeDa({})).toEqual({
      venditore_impresa: false,
      nuova_costruzione: false,
      prima_casa: true,
      prezzo_valore: true,
    });
  });

  it("un regime scritto male non rompe la scheda", () => {
    expect(regimeDa({ regime_acquisto: "si" }).prima_casa).toBe(true);
    expect(regimeDa({ regime_acquisto: ["no"] }).prima_casa).toBe(true);
    expect(regimeDa({ regime_acquisto: { prima_casa: "forse" } }).prima_casa).toBe(true);
  });

  it("scarta gli esiti di verifiche che il catalogo non conosce piu'", () => {
    const letti = verificheDa({
      verifiche: {
        v01: { stato: "fatto", note: "ok" },
        verifica_sparita: { stato: "fatto", note: "resto di una versione vecchia" },
      },
    });
    expect(Object.keys(letti)).toEqual(["v01"]);
  });

  it("scarta uno stato che non esiste invece di mostrarlo", () => {
    expect(verificheDa({ verifiche: { v01: { stato: "quasi" } } })).toEqual({});
  });
});

describe("l'anteprima delle imposte", () => {
  it("coincide con il motore, che e' l'unica implementazione verificata", () => {
    const scheda = schedaDa(immobileFinto());
    const { immobile, acquirente } = versoMotore(scheda);
    const dalMotore = imposteAcquisto(immobile, acquirente);
    const mostrata = anteprima(scheda);
    expect(mostrata.imposteTotali).toBe(dalMotore.totale);
    expect(mostrata.registro).toBe(dalMotore.registro);
    expect(mostrata.regime).toBe(dalMotore.regime);
  });

  it("l'agevolazione non spetta sulle categorie di lusso, anche se la si chiede", () => {
    const scheda = { ...schedaDa(immobileFinto()), categoria: "A/1" };
    expect(scheda.regime.prima_casa).toBe(true);
    expect(anteprima(scheda).agevolazioneApplicabile).toBe(false);
  });

  it("con venditore impresa compare l'IVA e il prezzo-valore non si applica", () => {
    const base = schedaDa(immobileFinto());
    const conImpresa = { ...base, regime: { ...base.regime, venditore_impresa: true } };
    const numeri = anteprima(conImpresa);
    expect(numeri.iva).toBeGreaterThan(0);
    expect(numeri.imponibile).toBe(conImpresa.prezzo);
  });

  it("senza rendita catastale il prezzo-valore non ha su cosa applicarsi", () => {
    const base = schedaDa(immobileFinto());
    const senzaRendita = { ...base, rendita_catastale: 0 };
    expect(anteprima(senzaRendita).imponibile).toBe(senzaRendita.prezzo);
  });

  it("senza superficie non inventa un prezzo al metro quadro", () => {
    const base = schedaDa(immobileFinto());
    expect(anteprima({ ...base, superficie_mq: 0 }).prezzoAlMq).toBeNull();
    expect(anteprima(base).prezzoAlMq).toBeCloseTo(180_000 / 85, 9);
  });

  it("su una scheda vuota non produce numeri assurdi", () => {
    const numeri = anteprima(schedaNuova());
    expect(Number.isFinite(numeri.imposteTotali)).toBe(true);
    expect(numeri.incidenzaImposte).toBe(0);
  });
});

describe("le verifiche di un immobile", () => {
  it("una scheda nuova parte dagli stati iniziali del catalogo", () => {
    const scheda = schedaNuova();
    const unite = verificheInScheda(scheda);
    expect(unite.length).toBe(VERIFICHE.length);
    expect(unite.every((v) => v.intatta)).toBe(true);
    expect(verificheAperte(scheda)).toBe(
      VERIFICHE.filter((v) => v.statoIniziale === "da fare" || v.statoIniziale === "in corso").length,
    );
  });

  it("chiudere una verifica abbassa il conteggio delle aperte", () => {
    const scheda = schedaNuova();
    const prima = verificheAperte(scheda);
    const dopo = conVerifica(scheda, "v01", { stato: "fatto" });
    expect(verificheAperte(dopo)).toBe(prima - 1);
  });

  it("non modifica la scheda ricevuta", () => {
    const scheda = schedaNuova();
    const dopo = conVerifica(scheda, "v01", { stato: "fatto", note: "chiusa" });
    expect(scheda.verifiche.v01).toBeUndefined();
    expect(dopo.verifiche.v01).toEqual({ stato: "fatto", note: "chiusa" });
  });

  it("ignora una chiave che il catalogo non conosce", () => {
    const scheda = schedaNuova();
    expect(conVerifica(scheda, "inesistente", { stato: "fatto" })).toBe(scheda);
  });

  it("scrivere solo le note non perde lo stato, e viceversa", () => {
    const conStato = conVerifica(schedaNuova(), "v01", { stato: "in corso" });
    const conNote = conVerifica(conStato, "v01", { note: "richiesta al notaio" });
    expect(conNote.verifiche.v01).toEqual({ stato: "in corso", note: "richiesta al notaio" });
  });
});
