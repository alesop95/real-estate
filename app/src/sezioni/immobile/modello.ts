// Il ponte fra la forma che viaggia e la forma con cui si lavora, e i numeri che ne discendono.
//
// Tutto cio' che in questa area decide qualcosa sta qui, e la sezione che segue si limita a
// mostrare. Non e' una convenzione estetica: una funzione pura si prova con un'asserzione,
// mentre la stessa regola scritta dentro un componente si prova solo simulando un clic, il
// che costa dieci volte tanto e verifica meno. La regola pratica che ne discende e' che in
// sezione.tsx non deve comparire un solo `if` che riguardi il dominio.
//
// Il calcolo non vive nemmeno qui: vive nel motore, che e' l'implementazione verificata contro
// i duecentoundici vettori generati dal motore Python. Questo modulo prepara gli ingressi e
// legge gli esiti, e non ricalcola niente per conto proprio, nemmeno quando sarebbe una riga.

import type { Immobile, ImmobileInviato, Ipotesi } from "../../condiviso/immobile";
import { immobileNuovo } from "../../condiviso/immobile";
import { STATI_VERIFICA, VERIFICHE, type StatoVerifica } from "../../condiviso/verifiche.generate";
import { agevolazioneApplicabile, imposteAcquisto, valoreCatastale } from "../../motore/motore";
import type { Acquirente, Immobile as ImmobileDiCalcolo } from "../../motore/tipi";

import type { Anteprima, EsitoVerifica, RegimeAcquisto, Scheda, VerificaInScheda } from "./tipi";

/** La chiave sotto cui questa area scrive dentro il documento delle ipotesi. */
const CHIAVE_REGIME = "regime_acquisto";
const CHIAVE_VERIFICHE = "verifiche";

const REGIME_PREDEFINITO: RegimeAcquisto = {
  venditore_impresa: false,
  nuova_costruzione: false,
  prima_casa: true,
  prezzo_valore: true,
};

function booleano(fonte: Record<string, unknown>, campo: string, predefinito: boolean): boolean {
  const v = fonte[campo];
  return typeof v === "boolean" ? v : predefinito;
}

function testo(fonte: Record<string, unknown>, campo: string): string {
  const v = fonte[campo];
  return typeof v === "string" ? v : "";
}

function statoValido(v: unknown): v is StatoVerifica {
  return typeof v === "string" && (STATI_VERIFICA as readonly string[]).includes(v);
}

/**
 * Legge il regime dal documento delle ipotesi, tollerando l'assenza e il rumore.
 *
 * Tollerare non e' lassismo: il documento e' scritto da versioni diverse dell'applicazione
 * nel tempo, e una lettura che pretendesse la forma perfetta renderebbe illeggibile un
 * immobile salvato il mese prima. Cio' che non si riconosce si sostituisce con il
 * predefinito, e cio' che non si conosce affatto non si tocca: lo conserva `versoInvio`.
 */
export function regimeDa(ipotesi: Ipotesi): RegimeAcquisto {
  const grezzo = ipotesi[CHIAVE_REGIME];
  if (grezzo === null || typeof grezzo !== "object" || Array.isArray(grezzo)) {
    return { ...REGIME_PREDEFINITO };
  }
  const d = grezzo as Record<string, unknown>;
  return {
    venditore_impresa: booleano(d, "venditore_impresa", REGIME_PREDEFINITO.venditore_impresa),
    nuova_costruzione: booleano(d, "nuova_costruzione", REGIME_PREDEFINITO.nuova_costruzione),
    prima_casa: booleano(d, "prima_casa", REGIME_PREDEFINITO.prima_casa),
    prezzo_valore: booleano(d, "prezzo_valore", REGIME_PREDEFINITO.prezzo_valore),
  };
}

/** Legge gli esiti delle verifiche, scartando le chiavi che il catalogo non conosce piu'. */
export function verificheDa(ipotesi: Ipotesi): Record<string, EsitoVerifica> {
  const grezzo = ipotesi[CHIAVE_VERIFICHE];
  if (grezzo === null || typeof grezzo !== "object" || Array.isArray(grezzo)) return {};
  const conosciute = new Set(VERIFICHE.map((v) => v.id));
  const esito: Record<string, EsitoVerifica> = {};
  for (const [id, valore] of Object.entries(grezzo as Record<string, unknown>)) {
    if (!conosciute.has(id)) continue;
    if (valore === null || typeof valore !== "object" || Array.isArray(valore)) continue;
    const d = valore as Record<string, unknown>;
    if (!statoValido(d.stato)) continue;
    esito[id] = { stato: d.stato, note: testo(d, "note") };
  }
  return esito;
}

/** Da un immobile come torna dal server alla scheda su cui si lavora. */
export function schedaDa(immobile: Immobile | ImmobileInviato): Scheda {
  return {
    titolo: immobile.titolo,
    comune: immobile.comune,
    indirizzo: immobile.indirizzo,
    prezzo: immobile.prezzo,
    superficie_mq: immobile.superficie_mq,
    categoria: immobile.categoria,
    rendita_catastale: immobile.rendita_catastale,
    stato: immobile.stato,
    regime: regimeDa(immobile.ipotesi),
    verifiche: verificheDa(immobile.ipotesi),
  };
}

/** Una scheda vuota, con gli stessi predefiniti che il server assegnerebbe. */
export function schedaNuova(): Scheda {
  return schedaDa(immobileNuovo());
}

/**
 * Dalla scheda alla forma che si invia, conservando cio' che questa area non conosce.
 *
 * La riga che conta e' la copia delle ipotesi originali prima di sovrascrivere le due chiavi
 * di competenza. Senza di essa l'area immobile, salvando, cancellerebbe le ipotesi scritte
 * dall'area del finanziamento o da quella della messa a reddito, e lo farebbe in silenzio:
 * nessun errore, nessun rifiuto, soltanto numeri tornati ai valori predefiniti la prossima
 * volta che qualcuno apre l'altra area. E' lo stesso genere di difetto del riferimento per
 * coordinata di cella nel workbook, cioe' un guasto che non fallisce.
 */
export function versoInvio(scheda: Scheda, ipotesiOriginali: Ipotesi = {}): ImmobileInviato {
  return {
    titolo: scheda.titolo.trim(),
    comune: scheda.comune.trim(),
    indirizzo: scheda.indirizzo.trim(),
    prezzo: scheda.prezzo,
    superficie_mq: scheda.superficie_mq,
    categoria: scheda.categoria.trim(),
    rendita_catastale: scheda.rendita_catastale,
    stato: scheda.stato,
    ipotesi: {
      ...ipotesiOriginali,
      [CHIAVE_REGIME]: { ...scheda.regime },
      [CHIAVE_VERIFICHE]: { ...scheda.verifiche },
    },
  };
}

/** Gli ingressi del motore che questa area determina per intero. */
export function versoMotore(scheda: Scheda): { immobile: ImmobileDiCalcolo; acquirente: Acquirente } {
  return {
    immobile: {
      prezzo: scheda.prezzo,
      rendita_catastale: scheda.rendita_catastale,
      categoria: scheda.categoria,
      superficie_mq: scheda.superficie_mq,
      comune: scheda.comune,
      nuova_costruzione: scheda.regime.nuova_costruzione,
      venditore_impresa: scheda.regime.venditore_impresa,
    },
    // I campi che seguono appartengono ad altre aree e non entrano in nessuno dei numeri che
    // questa mostra: `imposteAcquisto` legge soltanto `prima_casa` e `prezzo_valore`, piu' la
    // categoria e il regime del venditore. Stanno qui perche' il tipo li pretende, e sono i
    // valori neutri, non stime: l'anteprima di questa area e' esatta, non indicativa.
    acquirente: {
      prima_casa: scheda.regime.prima_casa,
      prezzo_valore: scheda.regime.prezzo_valore,
      quota: 1,
      residenza_gia_nel_comune: false,
      eta: 0,
      isee: 0,
      reddito_imponibile_irpef: 0,
      possiede_altra_prima_casa: false,
    },
  };
}

/** I numeri che questa area calcola, tutti dal motore e nessuno riscritto qui. */
export function anteprima(scheda: Scheda): Anteprima {
  const { immobile, acquirente } = versoMotore(scheda);
  const imposte = imposteAcquisto(immobile, acquirente);
  const agevolata = agevolazioneApplicabile(immobile, acquirente);
  return {
    // La base si prende da `imposte` e non da `baseImponibileRegistro`, e la differenza non e'
    // di stile. Il prezzo-valore e' una regola dell'imposta di registro: quando il venditore e'
    // un'impresa la vendita e' soggetta a IVA, e la base torna a essere il prezzo pattuito.
    // `baseImponibileRegistro` risponde alla domanda del registro e non sa dell'IVA, quindi
    // chiamarla qui mostrava il valore catastale accanto a un'IVA calcolata sul prezzo: due
    // numeri entrambi giusti nel proprio contesto e incoerenti fra loro. E' la ragione per cui
    // in questo progetto non si ricalcola mai cio' che il motore ha gia' deciso.
    imponibile: imposte.imponibile,
    iva: imposte.iva,
    registro: imposte.registro,
    ipotecaria: imposte.ipotecaria,
    catastale: imposte.catastale,
    imposteTotali: imposte.totale,
    regime: imposte.regime,
    valoreCatastale: valoreCatastale(scheda.rendita_catastale, agevolata),
    agevolazioneApplicabile: agevolata,
    prezzoAlMq: scheda.superficie_mq > 0 ? scheda.prezzo / scheda.superficie_mq : null,
    incidenzaImposte: scheda.prezzo > 0 ? imposte.totale / scheda.prezzo : 0,
  };
}

/** Il catalogo unito agli esiti di questo immobile, nell'ordine del catalogo. */
export function verificheInScheda(scheda: Scheda): VerificaInScheda[] {
  return VERIFICHE.map((v) => {
    const esito = scheda.verifiche[v.id];
    return {
      id: v.id,
      fase: v.fase,
      verifica: v.verifica,
      percheConta: v.percheConta,
      fonte: v.fonte,
      chi: v.chi,
      stato: esito ? esito.stato : v.statoIniziale,
      note: esito ? esito.note : "",
      intatta: esito === undefined,
    };
  });
}

/**
 * Quante verifiche restano aperte, cioe' da fare o in corso.
 *
 * E' lo stesso conteggio della cella `verifiche_aperte` del workbook, e vale la pena che lo
 * sia: chi usa entrambi gli strumenti sullo stesso immobile deve leggere lo stesso numero,
 * altrimenti uno dei due sta mentendo e non si sa quale.
 */
export function verificheAperte(scheda: Scheda): number {
  return verificheInScheda(scheda).filter((v) => v.stato === "da fare" || v.stato === "in corso")
    .length;
}

/** Scrive lo stato di una verifica, lasciando immutata la scheda ricevuta. */
export function conVerifica(
  scheda: Scheda,
  id: string,
  cambio: Partial<EsitoVerifica>,
): Scheda {
  const catalogo = VERIFICHE.find((v) => v.id === id);
  if (!catalogo) return scheda;
  const corrente = scheda.verifiche[id] ?? { stato: catalogo.statoIniziale, note: "" };
  return {
    ...scheda,
    verifiche: { ...scheda.verifiche, [id]: { ...corrente, ...cambio } },
  };
}
