// La forma con cui l'area immobile lavora, che non e' la forma con cui il dato viaggia.
//
// La distinzione va tenuta perche' si paga se si dimentica. Sul filo passa un `ImmobileInviato`,
// cioe' nove campi piatti di cui uno, `ipotesi`, e' un documento libero che il database non
// guarda: e' la forma giusta per un'interfaccia di programmazione che non vuole migrare una
// tabella ogni volta che il modello cresce. Dentro la sezione quella stessa informazione
// conviene invece che sia tipizzata, perche' qui si scrive codice che la legge campo per campo
// e un `Record<string, unknown>` toglie al compilatore ogni possibilita' di aiutare.
//
// Il ponte fra le due forme e' modello.ts, ed e' li' che sta la regola che conta: cio' che la
// sezione non conosce dentro `ipotesi` va conservato, non riscritto. Le altre cinque aree
// scriveranno nello stesso documento, e un'area che salvasse solo cio' che sa cancellerebbe
// il lavoro delle altre senza che nulla fallisca.

import type { StatoVerifica } from "../../condiviso/verifiche.generate";

/**
 * Il regime di acquisto, dichiarato per singolo immobile.
 *
 * Nel workbook questi quattro valori vivono in celle del foglio Immobile, quindi valgono per
 * uno alla volta, e il foglio Confronto immobili li eredita globali: e' uno dei cinque limiti
 * dichiarati del modello, perche' una lista in cui un immobile e' prima casa e un altro no
 * viene valutata come se lo fossero tutti. Qui il limite non si aggira, sparisce: sono
 * attributi dell'immobile, come `docs/architettura-web.md` prevedeva.
 */
export interface RegimeAcquisto {
  /** Vendita da impresa costruttrice soggetta a IVA invece che a imposta di registro. */
  venditore_impresa: boolean;
  /** Attiva le tutele del decreto legislativo 122/2005, cioe' fideiussione e polizza decennale. */
  nuova_costruzione: boolean;
  /** Si chiede l'agevolazione prima casa. Sulle categorie di lusso non spetta comunque. */
  prima_casa: boolean;
  /** Si chiede al notaio la tassazione sul valore catastale invece che sul prezzo. */
  prezzo_valore: boolean;
}

/** Lo stato di una verifica su questo immobile, piu' le note di chi l'ha seguita. */
export interface EsitoVerifica {
  stato: StatoVerifica;
  note: string;
}

/** Come l'area immobile vede un immobile mentre lo si compila. */
export interface Scheda {
  titolo: string;
  comune: string;
  indirizzo: string;
  prezzo: number;
  superficie_mq: number;
  categoria: string;
  rendita_catastale: number;
  stato: string;
  regime: RegimeAcquisto;
  /** Per chiave di verifica, e solo per quelle che qualcuno ha toccato. */
  verifiche: Record<string, EsitoVerifica>;
}

/** Una verifica del catalogo, unita allo stato che ha su questo immobile. */
export interface VerificaInScheda {
  id: string;
  fase: string;
  verifica: string;
  percheConta: string;
  fonte: string;
  chi: string;
  stato: StatoVerifica;
  note: string;
  /** Vero se lo stato e' quello iniziale del catalogo e nessuno l'ha ancora toccato. */
  intatta: boolean;
}

/** I numeri che l'area immobile puo' calcolare da sola, senza assumere nulla di altre aree. */
export interface Anteprima {
  imponibile: number;
  iva: number;
  registro: number;
  ipotecaria: number;
  catastale: number;
  imposteTotali: number;
  regime: string;
  valoreCatastale: number;
  agevolazioneApplicabile: boolean;
  /** Prezzo al metro quadro, o null se la superficie non e' stata inserita. */
  prezzoAlMq: number | null;
  /** Le imposte in rapporto al prezzo, che e' il modo in cui si confrontano due operazioni. */
  incidenzaImposte: number;
}
