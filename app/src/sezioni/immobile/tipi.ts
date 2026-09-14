// La forma con cui l'area immobile lavora, che non e' la forma con cui il dato viaggia.
//
// La distinzione va tenuta perche' si paga se si dimentica. Sul filo passa un `ImmobileInviato`,
// cioe' nove campi piatti di cui uno, `ipotesi`, e' un documento libero che il database non
// guarda: e' la forma giusta per un'interfaccia di programmazione che non vuole migrare una
// tabella ogni volta che il modello cresce. Dentro la sezione quella stessa informazione conviene
// invece che sia tipizzata, perche' qui si scrive codice che la legge campo per campo e un
// `Record<string, unknown>` toglie al compilatore ogni possibilita' di aiutare.
//
// Le due sezioni del documento che quest'area governa, cioe' il regime di acquisto e gli esiti
// delle verifiche, non sono dichiarate qui ma in src/condiviso/ipotesi.ts, insieme a quelle di
// tutte le altre aree. Qui restano i tipi che esistono soltanto dentro questa schermata: la
// scheda su cui si lavora, la riga di verifica come la si mostra, e i numeri che si leggono.

import type { EsitoVerifica, RegimeAcquisto } from "../../condiviso/ipotesi";
import type { StatoVerifica } from "../../condiviso/verifiche.generate";

export type { EsitoVerifica, RegimeAcquisto };

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
