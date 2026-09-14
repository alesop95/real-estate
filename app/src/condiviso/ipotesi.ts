// La forma del documento delle ipotesi, dichiarata una volta per tutte le aree.
//
// Lo schema tiene in colonne i campi su cui si filtra e si ordina, e in un documento JSON tutto
// il resto delle assunzioni di valutazione. E' la forma giusta, perche' evita di migrare una
// tabella ogni volta che il modello cresce, e introduce l'unico problema che con le colonne non
// esisterebbe: quel documento lo scrivono sei aree, e ciascuna ne conosce solo una parte.
//
// L'area immobile, il 14 settembre, aveva risolto il problema da sola, leggendo e riscrivendo le
// proprie due chiavi e conservando le altre. Finche' l'area era una, quella soluzione era la
// soluzione; con la seconda diventa un pattern da ricopiare, e un pattern da ricopiare e' un
// pattern che la quarta area dimentichera'. Qui la conservazione non si ricorda: e' l'unico modo
// di scrivere, perche' `conSezione` e' la sola funzione che produce un documento nuovo e spande
// sempre sia il documento sia la sezione che tocca.
//
// La seconda ragione di questo modulo e' che due sezioni non appartengono a un'area sola. Il
// finanziamento lo legge e lo scrive sia l'area del costo dell'operazione, perche' l'esborso
// iniziale e' il costo totale meno il mutuo, sia l'area del finanziamento, perche' e' la sua
// materia. Una sezione con due autori non e' un difetto se la sua forma e' dichiarata in un posto
// solo: lo diventa se ciascuno dei due la descrive a modo proprio, perche' allora il primo che
// salva cancella i campi che l'altro conosceva e lui no.
//
// I valori predefiniti non si scrivono qui. Vengono da predefiniti.generate.ts, che li emette
// dalle dataclass di calcoli.py, perche' un predefinito ricopiato a mano e' esattamente la specie
// di divergenza silenziosa che questo progetto ha gia' pagato altrove.

import { costi } from "../motore/parametri.generati";
import type { Finanziamento, Gestione } from "../motore/tipi";

import type { Ipotesi } from "./immobile";
import {
  ACQUIRENTE_PREDEFINITO,
  FINANZIAMENTO_PREDEFINITO,
  GESTIONE_PREDEFINITA,
} from "./predefiniti.generate";
import { STATI_VERIFICA, VERIFICHE, type StatoVerifica } from "./verifiche.generate";

/** Le chiavi di primo livello del documento, una per materia e non una per schermata. */
export const SEZIONE = {
  regime: "regime_acquisto",
  verifiche: "verifiche",
  costo: "costo_operazione",
  finanziamento: "finanziamento",
  gestione: "gestione",
} as const;

export type ChiaveSezione = (typeof SEZIONE)[keyof typeof SEZIONE];

/**
 * Il regime di acquisto, dichiarato per singolo immobile.
 *
 * Nel workbook questi quattro valori vivono in celle del foglio Immobile, quindi valgono per uno
 * alla volta, e il foglio Confronto immobili li eredita globali: e' uno dei cinque limiti
 * dichiarati del modello. Qui il limite non si aggira, sparisce.
 */
export interface RegimeAcquisto {
  venditore_impresa: boolean;
  nuova_costruzione: boolean;
  prima_casa: boolean;
  prezzo_valore: boolean;
}

/** Le tre voci di costo che non discendono da una norma ma da una trattativa. */
export interface CostiOperazione {
  /** Quota del prezzo che spetta alla mediazione, al netto dell'IVA che il motore aggiunge. */
  provvigione_aliquota: number;
  notaio_compravendita: number;
  /** Tutto cio' che l'operazione richiede e che nessuna delle altre voci copre. */
  altri_costi: number;
}

/** Lo stato di una verifica su questo immobile, piu' le note di chi l'ha seguita. */
export interface EsitoVerifica {
  stato: StatoVerifica;
  note: string;
}

export const REGIME_PREDEFINITO: RegimeAcquisto = {
  venditore_impresa: false,
  nuova_costruzione: false,
  prima_casa: ACQUIRENTE_PREDEFINITO.prima_casa,
  prezzo_valore: ACQUIRENTE_PREDEFINITO.prezzo_valore,
};

/**
 * I predefiniti delle tre voci di trattativa.
 *
 * Non sono scritti a mano e non sono generati, e la ragione sta nel fatto che nel motore quei
 * tre valori sono predefiniti di funzione e non campi di una dataclass, quindi il generatore per
 * introspezione non li vede. Si ricavano allora da dove il progetto li dichiara comunque: la
 * provvigione tipica e' un parametro, e l'onorario del notaio e' il punto medio dell'intervallo
 * registrato in `parametri.py`, che e' precisamente il numero che il motore usa come predefinito.
 * La coincidenza non e' lasciata all'occhio: una prova chiama il motore con questi valori e senza,
 * e pretende lo stesso esito.
 */
export const COSTI_PREDEFINITI: CostiOperazione = {
  provvigione_aliquota: costi.provvigioneAgenziaTipica,
  notaio_compravendita: (costi.notaioCompravenditaMin + costi.notaioCompravenditaMax) / 2,
  altri_costi: 0,
};

// ---------------------------------------------------------------------------
// Lettura: tollerante, perche' il documento e' scritto da versioni diverse nel tempo
// ---------------------------------------------------------------------------

function grezza(ipotesi: Ipotesi, chiave: string): Record<string, unknown> {
  const v = ipotesi[chiave];
  if (v === null || typeof v !== "object" || Array.isArray(v)) return {};
  return v as Record<string, unknown>;
}

function booleano(d: Record<string, unknown>, campo: string, predefinito: boolean): boolean {
  const v = d[campo];
  return typeof v === "boolean" ? v : predefinito;
}

function numero(d: Record<string, unknown>, campo: string, predefinito: number): number {
  const v = d[campo];
  return typeof v === "number" && Number.isFinite(v) ? v : predefinito;
}

function testo(d: Record<string, unknown>, campo: string, predefinito: string): string {
  const v = d[campo];
  return typeof v === "string" ? v : predefinito;
}

export function leggiRegime(ipotesi: Ipotesi): RegimeAcquisto {
  const d = grezza(ipotesi, SEZIONE.regime);
  return {
    venditore_impresa: booleano(d, "venditore_impresa", REGIME_PREDEFINITO.venditore_impresa),
    nuova_costruzione: booleano(d, "nuova_costruzione", REGIME_PREDEFINITO.nuova_costruzione),
    prima_casa: booleano(d, "prima_casa", REGIME_PREDEFINITO.prima_casa),
    prezzo_valore: booleano(d, "prezzo_valore", REGIME_PREDEFINITO.prezzo_valore),
  };
}

export function leggiCosti(ipotesi: Ipotesi): CostiOperazione {
  const d = grezza(ipotesi, SEZIONE.costo);
  return {
    provvigione_aliquota: numero(d, "provvigione_aliquota", COSTI_PREDEFINITI.provvigione_aliquota),
    notaio_compravendita: numero(d, "notaio_compravendita", COSTI_PREDEFINITI.notaio_compravendita),
    altri_costi: numero(d, "altri_costi", COSTI_PREDEFINITI.altri_costi),
  };
}

export function leggiFinanziamento(ipotesi: Ipotesi): Finanziamento {
  const d = grezza(ipotesi, SEZIONE.finanziamento);
  const p = FINANZIAMENTO_PREDEFINITO;
  return {
    importo: numero(d, "importo", p.importo),
    tasso_annuo: numero(d, "tasso_annuo", p.tasso_annuo),
    durata_anni: numero(d, "durata_anni", p.durata_anni),
    tipo: testo(d, "tipo", p.tipo),
    spread: numero(d, "spread", p.spread),
    istruttoria: numero(d, "istruttoria", p.istruttoria),
    perizia: numero(d, "perizia", p.perizia),
    polizza_annua: numero(d, "polizza_annua", p.polizza_annua),
    notaio_atto_mutuo: numero(d, "notaio_atto_mutuo", p.notaio_atto_mutuo),
  };
}

export function leggiGestione(ipotesi: Ipotesi): Gestione {
  const d = grezza(ipotesi, SEZIONE.gestione);
  const p = GESTIONE_PREDEFINITA;
  return {
    canone_mensile: numero(d, "canone_mensile", p.canone_mensile),
    regime: (testo(d, "regime", p.regime) as Gestione["regime"]) ?? p.regime,
    mesi_sfitto_annui: numero(d, "mesi_sfitto_annui", p.mesi_sfitto_annui),
    morosita: numero(d, "morosita", p.morosita),
    condominio_annuo: numero(d, "condominio_annuo", p.condominio_annuo),
    quota_condominio_a_carico_proprietario: numero(
      d,
      "quota_condominio_a_carico_proprietario",
      p.quota_condominio_a_carico_proprietario,
    ),
    manutenzione_su_valore: numero(d, "manutenzione_su_valore", p.manutenzione_su_valore),
    assicurazione_annua: numero(d, "assicurazione_annua", p.assicurazione_annua),
    aliquota_imu: numero(d, "aliquota_imu", p.aliquota_imu),
    gestione_su_canone: numero(d, "gestione_su_canone", p.gestione_su_canone),
    ricavi_lordi_brevi_annui: numero(d, "ricavi_lordi_brevi_annui", p.ricavi_lordi_brevi_annui),
    costi_variabili_brevi: numero(d, "costi_variabili_brevi", p.costi_variabili_brevi),
  };
}

/** Gli esiti delle verifiche, scartando le chiavi che il catalogo non conosce piu'. */
export function leggiVerifiche(ipotesi: Ipotesi): Record<string, EsitoVerifica> {
  const d = grezza(ipotesi, SEZIONE.verifiche);
  const conosciute = new Set(VERIFICHE.map((v) => v.id));
  const esito: Record<string, EsitoVerifica> = {};
  for (const [id, valore] of Object.entries(d)) {
    if (!conosciute.has(id)) continue;
    if (valore === null || typeof valore !== "object" || Array.isArray(valore)) continue;
    const riga = valore as Record<string, unknown>;
    const stato = riga.stato;
    if (typeof stato !== "string" || !(STATI_VERIFICA as readonly string[]).includes(stato)) continue;
    esito[id] = { stato: stato as StatoVerifica, note: testo(riga, "note", "") };
  }
  return esito;
}

// ---------------------------------------------------------------------------
// Scrittura: conservativa, e lo e' per costruzione
// ---------------------------------------------------------------------------

/**
 * Scrive una sezione conservando tutto il resto, al primo e al secondo livello.
 *
 * E' la sola funzione con cui si produce un documento nuovo, ed e' scritta in modo che
 * dimenticare la conservazione non sia possibile invece che sconsigliato. Il primo spargimento
 * tiene le sezioni delle altre aree, il secondo tiene i campi che un'altra versione
 * dell'applicazione aveva scritto dentro questa sezione e che oggi nessuno legge: cancellarli
 * sarebbe la stessa perdita silenziosa, un piano piu' in basso.
 */
export function conSezione(ipotesi: Ipotesi, chiave: ChiaveSezione, valore: object): Ipotesi {
  return { ...ipotesi, [chiave]: { ...grezza(ipotesi, chiave), ...valore } };
}

/** Scrive piu' sezioni in un colpo solo, con la stessa conservazione. */
export function conSezioni(
  ipotesi: Ipotesi,
  cambi: Partial<Record<ChiaveSezione, object>>,
): Ipotesi {
  let esito = ipotesi;
  for (const [chiave, valore] of Object.entries(cambi)) {
    if (valore) esito = conSezione(esito, chiave as ChiaveSezione, valore);
  }
  return esito;
}
