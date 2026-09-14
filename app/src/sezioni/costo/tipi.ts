// La forma con cui l'area del costo dell'operazione lavora.
//
// La scheda porta due sezioni intere del documento delle ipotesi e non i singoli campi che la
// schermata mostra, ed e' una scelta. Le sezioni sono dichiarate in src/condiviso/ipotesi.ts, le
// scrive anche l'area del finanziamento, e leggerle e riscriverle per intero e' il modo in cui un
// campo che quest'area non mostra, per esempio il tasso, sopravvive al salvataggio senza che
// quest'area debba saperne l'esistenza.

import type { CostiOperazione } from "../../condiviso/ipotesi";
import type { Finanziamento } from "../../motore/tipi";

export interface SchedaCosto {
  costi: CostiOperazione;
  finanziamento: Finanziamento;
}

/** Il costo dell'operazione voce per voce, come lo restituisce il motore, piu' il rapporto. */
export interface RiepilogoCosto {
  prezzo: number;
  imposteTotali: number;
  regimeImposte: string;
  provvigione: number;
  notaioCompravendita: number;
  notaioMutuo: number;
  sostitutivaMutuo: number;
  istruttoria: number;
  perizia: number;
  altriCosti: number;
  costiAccessori: number;
  /** Prezzo piu' tutti i costi: e' il denominatore corretto dei rendimenti, per ADR-002. */
  costoTotale: number;
  mutuo: number;
  /** La cassa che serve davvero, cioe' il costo totale al netto di cio' che presta la banca. */
  esborsoIniziale: number;
  incidenzaCosti: number;
  rapportoMutuoPrezzo: number;
  oltreRapportoOrdinario: boolean;
  rapportoOrdinarioMassimo: number;
}
