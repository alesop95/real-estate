// Il ponte fra la forma che viaggia e la forma con cui si lavora, e i numeri che ne discendono.
//
// Tutto cio' che in questa area decide qualcosa sta qui, e la sezione che segue si limita a
// mostrare. Non e' una convenzione estetica: una funzione pura si prova con un'asserzione,
// mentre la stessa regola scritta dentro un componente si prova solo simulando un clic, il che
// costa dieci volte tanto e verifica meno. La regola pratica che ne discende e' che in
// sezione.tsx non deve comparire un solo `if` che riguardi il dominio.
//
// Il calcolo non vive nemmeno qui: vive nel motore, che e' l'implementazione verificata contro i
// duecentoundici vettori generati dal motore Python. Questo modulo prepara gli ingressi e legge
// gli esiti, e non ricalcola niente per conto proprio, nemmeno quando sarebbe una riga.
//
// La lettura e la scrittura del documento delle ipotesi non stanno nemmeno qui: stanno in
// src/condiviso/ipotesi.ts, che le dichiara una volta per tutte le aree. Era codice di questo
// file fino al 14 settembre, quando l'area era una sola; con la seconda sarebbe diventato un
// pattern da ricopiare, e la conservazione di cio' che non si conosce non e' una cosa che
// convenga affidare alla memoria di chi scrivera' la quarta.

import type { Immobile, ImmobileInviato, Ipotesi } from "../../condiviso/immobile";
import { immobileNuovo } from "../../condiviso/immobile";
import { conSezioni, leggiRegime, leggiVerifiche, SEZIONE } from "../../condiviso/ipotesi";
import { ACQUIRENTE_PREDEFINITO } from "../../condiviso/predefiniti.generate";
import { VERIFICHE } from "../../condiviso/verifiche.generate";
import { agevolazioneApplicabile, imposteAcquisto, valoreCatastale } from "../../motore/motore";
import type { Acquirente, Immobile as ImmobileDiCalcolo } from "../../motore/tipi";

import type { Anteprima, EsitoVerifica, Scheda, VerificaInScheda } from "./tipi";

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
    regime: leggiRegime(immobile.ipotesi),
    verifiche: leggiVerifiche(immobile.ipotesi),
  };
}

/** Una scheda vuota, con gli stessi predefiniti che il server assegnerebbe. */
export function schedaNuova(): Scheda {
  return schedaDa(immobileNuovo());
}

/**
 * Dalla scheda alla forma che si invia.
 *
 * La conservazione di cio' che quest'area non conosce non si vede qui perche' non e' un gesto:
 * `conSezioni` e' l'unica funzione con cui si produce un documento nuovo, e sparge sempre sia il
 * documento sia la sezione che tocca. Scrivere un'area che cancella il lavoro delle altre
 * richiederebbe di costruire l'oggetto a mano, aggirandola.
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
    ipotesi: conSezioni(ipotesiOriginali, {
      [SEZIONE.regime]: scheda.regime,
      [SEZIONE.verifiche]: scheda.verifiche,
    }),
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
    // Dell'acquirente questa area conosce due campi, cioe' i due del regime; gli altri
    // appartengono ad altre aree e non entrano in nessuno dei numeri che questa mostra, perche'
    // `imposteAcquisto` legge soltanto quei due piu' la categoria e il regime del venditore.
    // Si prendono dai predefiniti generati dal motore Python invece di scriverne di propri: un
    // valore neutro inventato qui sarebbe la solita seconda verita', e il giorno in cui un
    // predefinito cambiasse in `calcoli.py` questa area resterebbe indietro senza fallire.
    acquirente: {
      ...ACQUIRENTE_PREDEFINITO,
      prima_casa: scheda.regime.prima_casa,
      prezzo_valore: scheda.regime.prezzo_valore,
    },
  };
}

/** I numeri che questa area calcola, tutti dal motore e nessuno riscritto qui. */
export function anteprima(scheda: Scheda): Anteprima {
  const { immobile, acquirente } = versoMotore(scheda);
  const imposte = imposteAcquisto(immobile, acquirente);
  const agevolata = agevolazioneApplicabile(immobile, acquirente);
  return {
    // La base si prende da `imposte` e non da `baseImponibileRegistro`, e la differenza non e' di
    // stile. Il prezzo-valore e' una regola dell'imposta di registro: quando il venditore e'
    // un'impresa la vendita e' soggetta a IVA, e la base torna a essere il prezzo pattuito.
    // `baseImponibileRegistro` risponde alla domanda del registro e non sa dell'IVA, quindi
    // chiamarla qui mostrava il valore catastale accanto a un'IVA calcolata sul prezzo: due
    // numeri entrambi giusti nel proprio contesto e incoerenti fra loro. E' la ragione per cui in
    // questo progetto non si ricalcola mai cio' che il motore ha gia' deciso.
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
 * E' lo stesso conteggio della cella `verifiche_aperte` del workbook, e vale la pena che lo sia:
 * chi usa entrambi gli strumenti sullo stesso immobile deve leggere lo stesso numero, altrimenti
 * uno dei due sta mentendo e non si sa quale.
 */
export function verificheAperte(scheda: Scheda): number {
  return verificheInScheda(scheda).filter((v) => v.stato === "da fare" || v.stato === "in corso")
    .length;
}

/** Scrive lo stato di una verifica, lasciando immutata la scheda ricevuta. */
export function conVerifica(scheda: Scheda, id: string, cambio: Partial<EsitoVerifica>): Scheda {
  const catalogo = VERIFICHE.find((v) => v.id === id);
  if (!catalogo) return scheda;
  const corrente = scheda.verifiche[id] ?? { stato: catalogo.statoIniziale, note: "" };
  return {
    ...scheda,
    verifiche: { ...scheda.verifiche, [id]: { ...corrente, ...cambio } },
  };
}
