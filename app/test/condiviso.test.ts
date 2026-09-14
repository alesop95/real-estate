// Le prove del modulo condiviso fra Worker e interfaccia.
//
// Il modulo esiste per una ragione sola, cioe' che la stessa regola valga dalle due parti, e
// queste prove verificano la regola in se'. Che il Worker la applichi davvero e' gia' provato
// altrove, dentro il runtime di Cloudflare, contro un D1 vero: la' si prova la conseguenza,
// qui la regola. Provarla due volte nello stesso modo non aggiungerebbe niente; provarla nei
// due modi diversi copre sia il contenuto sia il collegamento.

import { describe, expect, it } from "vitest";

import { immobileNuovo, STATI_IMMOBILE, validaImmobile } from "../src/condiviso/immobile";
import { NOME_RUOLO, ruoloSufficiente, type Ruolo } from "../src/condiviso/ruoli";
import { FASI_VERIFICA, STATI_VERIFICA, VERIFICHE } from "../src/condiviso/verifiche.generate";

const VALIDO = {
  titolo: "Trilocale via Roma",
  comune: "Civitanova Marche",
  indirizzo: "via Roma 1",
  prezzo: 180_000,
  superficie_mq: 85,
  categoria: "A/2",
  rendita_catastale: 620,
  stato: "da valutare",
  ipotesi: {},
};

describe("la forma di un immobile, condivisa", () => {
  it("accetta un immobile compilato bene", () => {
    const { errori, valore } = validaImmobile(VALIDO);
    expect(errori).toEqual([]);
    expect(valore?.prezzo).toBe(180_000);
  });

  it("un immobile appena cominciato e' gia' valido tranne il titolo", () => {
    // E' la proprieta' che tiene insieme il modulo nuovo e il server: i predefiniti sono gli
    // stessi, quindi una scheda vuota fallisce su cio' che manca davvero e non su cio' che
    // il browser ha dimenticato di mandare.
    const { errori } = validaImmobile({ ...immobileNuovo(), titolo: "x" });
    expect(errori).toEqual([]);
  });

  it("restituisce tutti gli errori insieme, non il primo", () => {
    const { errori, valore } = validaImmobile({
      titolo: "",
      prezzo: -1,
      categoria: "Z/9",
      stato: "inventato",
      ipotesi: [],
    });
    expect(valore).toBeUndefined();
    expect(errori.length).toBeGreaterThanOrEqual(5);
    expect(errori.some((e) => e.startsWith("titolo:"))).toBe(true);
    expect(errori.some((e) => e.startsWith("prezzo:"))).toBe(true);
    expect(errori.some((e) => e.startsWith("categoria:"))).toBe(true);
    expect(errori.some((e) => e.startsWith("stato:"))).toBe(true);
    expect(errori.some((e) => e.startsWith("ipotesi:"))).toBe(true);
  });

  it("rifiuta le categorie fuori dal residenziale e accetta le pertinenze", () => {
    expect(validaImmobile({ ...VALIDO, categoria: "C/6" }).errori).toEqual([]);
    expect(validaImmobile({ ...VALIDO, categoria: "D/1" }).errori).toContain(
      "categoria: forma attesa tipo A/2",
    );
  });

  it("rifiuta un numero non finito invece di scriverlo in tabella", () => {
    // NaN e infinito attraversano JSON come null, ma un chiamante che parli direttamente
    // all'interfaccia di programmazione puo' mandarli: il controllo e' sul tipo, non sul
    // formato di trasporto.
    expect(validaImmobile({ ...VALIDO, prezzo: Number.NaN }).errori).toContain(
      "prezzo: deve essere un numero finito",
    );
  });

  it("rifiuta un documento di ipotesi oltre il limite", () => {
    const enorme = { nota: "x".repeat(20_001) };
    expect(validaImmobile({ ...VALIDO, ipotesi: enorme }).errori.some((e) => e.startsWith("ipotesi:"))).toBe(
      true,
    );
  });

  it("accetta ogni stato dell'elenco, e nessun altro", () => {
    for (const stato of STATI_IMMOBILE) {
      expect(validaImmobile({ ...VALIDO, stato }).errori).toEqual([]);
    }
    expect(validaImmobile({ ...VALIDO, stato: "venduto" }).errori.length).toBe(1);
  });
});

describe("i ruoli, condivisi", () => {
  it("un ruolo superiore soddisfa la richiesta di uno inferiore", () => {
    expect(ruoloSufficiente("amministratore", "lettore")).toBe(true);
    expect(ruoloSufficiente("amministratore", "membro")).toBe(true);
    expect(ruoloSufficiente("membro", "membro")).toBe(true);
  });

  it("un ruolo inferiore non soddisfa la richiesta di uno superiore", () => {
    expect(ruoloSufficiente("lettore", "membro")).toBe(false);
    expect(ruoloSufficiente("membro", "amministratore")).toBe(false);
  });

  it("ogni ruolo ha un nome da mostrare", () => {
    const ruoli: Ruolo[] = ["amministratore", "membro", "lettore"];
    for (const r of ruoli) expect(NOME_RUOLO[r]).toBeTruthy();
  });
});

describe("il catalogo delle verifiche, generato dal motore Python", () => {
  it("porta trenta voci con identificativo distinto", () => {
    expect(VERIFICHE.length).toBe(30);
    expect(new Set(VERIFICHE.map((v) => v.id)).size).toBe(30);
  });

  it("ogni voce dichiara una fase dell'elenco e uno stato ammesso", () => {
    for (const v of VERIFICHE) {
      expect(FASI_VERIFICA).toContain(v.fase);
      expect(STATI_VERIFICA).toContain(v.statoIniziale);
    }
  });

  it("ogni fase dichiarata ha almeno una voce", () => {
    // Il contrario del controllo precedente. Da solo, il primo passerebbe anche con una fase
    // di troppo rimasta in elenco dopo aver tolto le sue voci, e l'interfaccia mostrerebbe un
    // titolo di sezione vuoto.
    for (const fase of FASI_VERIFICA) {
      expect(VERIFICHE.some((v) => v.fase === fase)).toBe(true);
    }
  });

  it("le voci sono raggruppate per fase e non sparse", () => {
    // L'interfaccia mostra le fasi nell'ordine dichiarato e le voci nell'ordine del catalogo:
    // se una voce di una fase comparisse dopo quelle della fase successiva, l'ordine mostrato
    // e quello del foglio Checklist smetterebbero di coincidere.
    const ordine = VERIFICHE.map((v) => FASI_VERIFICA.indexOf(v.fase));
    expect(ordine).toEqual([...ordine].sort((a, b) => a - b));
  });

  it("ogni voce dice perche' conta e su quale fonte si chiude", () => {
    for (const v of VERIFICHE) {
      expect(v.verifica.length).toBeGreaterThan(10);
      expect(v.percheConta.length).toBeGreaterThan(30);
      expect(v.fonte.length).toBeGreaterThan(3);
      expect(v.chi.length).toBeGreaterThan(3);
    }
  });
});
