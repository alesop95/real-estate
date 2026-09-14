// Le prove del modello dell'area del costo dell'operazione.
//
// Due proprieta' valgono piu' delle altre e sono le prime due gruppi. La prima e' che quest'area
// non tocca cio' che non governa, ne' le colonne dell'immobile ne' le sezioni delle altre aree: e'
// la stessa regola di conservazione dell'area immobile, verificata dall'altro lato, perche' una
// regola che vale solo dove e' stata scritta non e' una regola. La seconda e' che i numeri
// mostrati sono quelli del motore e non una loro riscrittura, che e' il difetto trovato il 14
// settembre nell'anteprima delle imposte e che conviene non ripetere.

import { describe, expect, it } from "vitest";

import type { Immobile } from "../../src/condiviso/immobile";
import { COSTI_PREDEFINITI, SEZIONE } from "../../src/condiviso/ipotesi";
import { ACQUIRENTE_PREDEFINITO, FINANZIAMENTO_PREDEFINITO } from "../../src/condiviso/predefiniti.generate";
import { costoOperazione } from "../../src/motore/motore";
import { mutuo as parametriMutuo } from "../../src/motore/parametri.generati";
import {
  conCosto,
  conFinanziamento,
  riepilogo,
  schedaDa,
  versoInvio,
  versoMotore,
} from "../../src/sezioni/costo/modello";

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

describe("quest'area non tocca cio' che non governa", () => {
  it("ricopia le colonne dell'immobile senza cambiarle", () => {
    const immobile = immobileFinto();
    const inviato = versoInvio(schedaDa(immobile), immobile);
    expect(inviato.titolo).toBe(immobile.titolo);
    expect(inviato.prezzo).toBe(immobile.prezzo);
    expect(inviato.categoria).toBe(immobile.categoria);
    expect(inviato.rendita_catastale).toBe(immobile.rendita_catastale);
    expect(inviato.stato).toBe(immobile.stato);
  });

  it("conserva le sezioni delle altre aree", () => {
    const immobile = immobileFinto({
      [SEZIONE.regime]: { prima_casa: false, prezzo_valore: false },
      [SEZIONE.verifiche]: { v01: { stato: "fatto", note: "visura del 2 settembre" } },
      [SEZIONE.gestione]: { canone_mensile: 650 },
    });
    const inviato = versoInvio(schedaDa(immobile), immobile);
    expect(inviato.ipotesi[SEZIONE.verifiche]).toEqual(immobile.ipotesi[SEZIONE.verifiche]);
    expect(inviato.ipotesi[SEZIONE.gestione]).toEqual(immobile.ipotesi[SEZIONE.gestione]);
    expect(inviato.ipotesi[SEZIONE.regime]).toEqual(immobile.ipotesi[SEZIONE.regime]);
  });

  it("conserva i campi del finanziamento che non mostra", () => {
    // Tasso e durata appartengono all'area del finanziamento e vivono nella stessa sezione.
    // Quest'area li riscrive perche' riscrive la sezione intera, e deve riscriverli uguali.
    const immobile = immobileFinto({
      [SEZIONE.finanziamento]: { ...FINANZIAMENTO_PREDEFINITO, tasso_annuo: 0.041, durata_anni: 30 },
    });
    const scheda = conFinanziamento(schedaDa(immobile), "importo", 120_000);
    const sezione = versoInvio(scheda, immobile).ipotesi[SEZIONE.finanziamento] as Record<string, unknown>;
    expect(sezione.tasso_annuo).toBe(0.041);
    expect(sezione.durata_anni).toBe(30);
    expect(sezione.importo).toBe(120_000);
  });

  it("un giro completo non perde e non inventa nulla", () => {
    const immobile = immobileFinto({
      [SEZIONE.costo]: { provvigione_aliquota: 0.02, notaio_compravendita: 2_200, altri_costi: 300 },
      [SEZIONE.finanziamento]: { ...FINANZIAMENTO_PREDEFINITO, importo: 120_000 },
      terze_parti: { chiunque: "non si tocca" },
    });
    const primo = versoInvio(schedaDa(immobile), immobile);
    const secondo = versoInvio(schedaDa({ ...immobile, ipotesi: primo.ipotesi }), {
      ...immobile,
      ipotesi: primo.ipotesi,
    });
    expect(secondo.ipotesi).toEqual(primo.ipotesi);
    expect(primo.ipotesi.terze_parti).toEqual({ chiunque: "non si tocca" });
  });
});

describe("il riepilogo viene dal motore, non da una riscrittura", () => {
  it("coincide voce per voce con costoOperazione", () => {
    const immobile = immobileFinto({
      [SEZIONE.finanziamento]: { ...FINANZIAMENTO_PREDEFINITO, importo: 120_000 },
    });
    const scheda = schedaDa(immobile);
    const ingressi = versoMotore(scheda, immobile);
    const dalMotore = costoOperazione(
      ingressi.immobile,
      ingressi.acquirente,
      ingressi.finanziamento,
      scheda.costi.provvigione_aliquota,
      scheda.costi.notaio_compravendita,
      scheda.costi.altri_costi,
    );
    const mostrato = riepilogo(scheda, immobile);
    expect(mostrato.costoTotale).toBe(dalMotore.costoTotale);
    expect(mostrato.costiAccessori).toBe(dalMotore.costiAccessori);
    expect(mostrato.esborsoIniziale).toBe(dalMotore.esborsoIniziale);
    expect(mostrato.provvigione).toBe(dalMotore.provvigione);
    expect(mostrato.sostitutivaMutuo).toBe(dalMotore.sostitutivaMutuo);
    expect(mostrato.imposteTotali).toBe(dalMotore.imposte.totale);
  });

  it("prende il regime dall'area immobile e non da predefiniti propri", () => {
    const conImpresa = immobileFinto({ [SEZIONE.regime]: { venditore_impresa: true } });
    const ingressi = versoMotore(schedaDa(conImpresa), conImpresa);
    expect(ingressi.immobile.venditore_impresa).toBe(true);
    expect(ingressi.acquirente.prima_casa).toBe(ACQUIRENTE_PREDEFINITO.prima_casa);
    expect(riepilogo(schedaDa(conImpresa), conImpresa).regimeImposte).toContain("IVA");
  });

  it("senza mutuo gli oneri del finanziamento non entrano nel totale", () => {
    // E' una regola del motore e non di quest'area, ma e' la piu' facile da rompere mostrando i
    // campi: chi li compila e poi porta l'importo a zero deve vedere il totale scendere.
    const immobile = immobileFinto({
      [SEZIONE.finanziamento]: { ...FINANZIAMENTO_PREDEFINITO, importo: 0 },
    });
    const numeri = riepilogo(schedaDa(immobile), immobile);
    expect(numeri.istruttoria).toBe(0);
    expect(numeri.perizia).toBe(0);
    expect(numeri.notaioMutuo).toBe(0);
    expect(numeri.sostitutivaMutuo).toBe(0);
    expect(numeri.esborsoIniziale).toBe(numeri.costoTotale);
  });

  it("l'esborso iniziale e' il costo totale meno il mutuo", () => {
    const immobile = immobileFinto({
      [SEZIONE.finanziamento]: { ...FINANZIAMENTO_PREDEFINITO, importo: 120_000 },
    });
    const numeri = riepilogo(schedaDa(immobile), immobile);
    expect(numeri.esborsoIniziale).toBeCloseTo(numeri.costoTotale - 120_000, 9);
  });

  it("segnala quando la richiesta supera il rapporto ordinario", () => {
    const immobile = immobileFinto();
    const sotto = conFinanziamento(schedaDa(immobile), "importo", 140_000);
    const sopra = conFinanziamento(schedaDa(immobile), "importo", 170_000);
    expect(riepilogo(sotto, immobile).oltreRapportoOrdinario).toBe(false);
    expect(riepilogo(sopra, immobile).oltreRapportoOrdinario).toBe(true);
    expect(riepilogo(sopra, immobile).rapportoOrdinarioMassimo).toBe(parametriMutuo.ltvOrdinarioMax);
  });

  it("su un immobile senza prezzo non produce un rapporto infinito", () => {
    const senzaPrezzo = { ...immobileFinto(), prezzo: 0 };
    const scheda = conFinanziamento(schedaDa(senzaPrezzo), "importo", 50_000);
    expect(riepilogo(scheda, senzaPrezzo).rapportoMutuoPrezzo).toBe(0);
    expect(Number.isFinite(riepilogo(scheda, senzaPrezzo).incidenzaCosti)).toBe(true);
  });
});

describe("le scritture della scheda lasciano immutato cio' che ricevono", () => {
  it("conCosto non modifica la scheda di partenza", () => {
    const scheda = schedaDa(immobileFinto());
    const dopo = conCosto(scheda, "altri_costi", 900);
    expect(scheda.costi.altri_costi).toBe(COSTI_PREDEFINITI.altri_costi);
    expect(dopo.costi.altri_costi).toBe(900);
    expect(dopo.costi.provvigione_aliquota).toBe(scheda.costi.provvigione_aliquota);
  });

  it("conFinanziamento non modifica la scheda di partenza", () => {
    const scheda = schedaDa(immobileFinto());
    const dopo = conFinanziamento(scheda, "importo", 100_000);
    expect(scheda.finanziamento.importo).toBe(FINANZIAMENTO_PREDEFINITO.importo);
    expect(dopo.finanziamento.importo).toBe(100_000);
    expect(dopo.finanziamento.tasso_annuo).toBe(scheda.finanziamento.tasso_annuo);
  });
});
