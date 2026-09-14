// Il modello dell'area del costo dell'operazione: che cosa si scrive, e che cosa ne discende.
//
// L'area risponde a una domanda sola, che e' la piu' pratica di tutte: quanta cassa serve davvero
// per comprare. La risposta non e' il prezzo, e la distanza fra i due e' il motivo per cui questa
// area esiste: fra imposte, mediazione, notaio e oneri del mutuo, un'operazione da centottantamila
// euro ne chiede quasi duecento, e chi ha in tasca l'anticipo esatto scopre il divario in agenzia.
//
// Tre confini vanno tenuti presenti leggendo questo file.
//
// Il primo e' che quest'area non scrive nulla dell'immobile: prezzo, categoria, rendita e regime
// di acquisto appartengono all'area immobile e qui si leggono soltanto. Il regime, in particolare,
// cambia il numero piu' grande della tabella, perche' decide fra IVA e imposta di registro; si
// mostra quindi accanto al risultato, ma con la sua provenienza dichiarata, perche' un valore
// modificabile da due schermate e' un valore che nessuno sa piu' dove si cambia.
//
// Il secondo e' che gli oneri accessori del mutuo stanno qui e non nell'area del finanziamento,
// pur essendo campi della stessa sezione delle ipotesi. La ragione e' d'uso e non di struttura:
// istruttoria, perizia e notaio dell'atto di mutuo si pagano una volta all'inizio e appartengono
// alla domanda "quanto serve per comprare", mentre tasso e durata governano la rata, che e' una
// domanda diversa e di un'altra area. La sezione condivisa in src/condiviso/ipotesi.ts esiste
// precisamente perche' due aree possano scrivere nella stessa senza che l'una cancelli l'altra.
//
// Il terzo e' che nessun numero si ricalcola qui. `costoOperazione` del motore restituisce ogni
// voce, comprese quelle che dipendono dal regime, e questo modulo le rigira: il solo calcolo che
// aggiunge e' il rapporto fra mutuo e prezzo, che il motore non espone e che serve a dire se la
// richiesta alla banca sta dentro il rapporto ordinario.

import type { Immobile, ImmobileInviato } from "../../condiviso/immobile";
import {
  conSezioni,
  leggiCosti,
  leggiFinanziamento,
  leggiRegime,
  SEZIONE,
  type CostiOperazione,
} from "../../condiviso/ipotesi";
import { ACQUIRENTE_PREDEFINITO } from "../../condiviso/predefiniti.generate";
import { costoOperazione } from "../../motore/motore";
import { mutuo as parametriMutuo } from "../../motore/parametri.generati";
import type { Acquirente, Finanziamento, Immobile as ImmobileDiCalcolo } from "../../motore/tipi";

import type { RiepilogoCosto, SchedaCosto } from "./tipi";

/** Dalla riga dell'immobile alla scheda su cui si lavora in quest'area. */
export function schedaDa(immobile: Immobile): SchedaCosto {
  return {
    costi: leggiCosti(immobile.ipotesi),
    finanziamento: leggiFinanziamento(immobile.ipotesi),
  };
}

/**
 * Dalla scheda alla forma che si invia.
 *
 * Le colonne dell'immobile si ricopiano tali e quali, perche' quest'area non le governa: toccarle
 * qui, anche solo normalizzandole, significherebbe che salvare un costo cambia silenziosamente un
 * dato di un'altra schermata.
 */
export function versoInvio(scheda: SchedaCosto, immobile: Immobile): ImmobileInviato {
  return {
    titolo: immobile.titolo,
    comune: immobile.comune,
    indirizzo: immobile.indirizzo,
    prezzo: immobile.prezzo,
    superficie_mq: immobile.superficie_mq,
    categoria: immobile.categoria,
    rendita_catastale: immobile.rendita_catastale,
    stato: immobile.stato,
    ipotesi: conSezioni(immobile.ipotesi, {
      [SEZIONE.costo]: scheda.costi,
      [SEZIONE.finanziamento]: scheda.finanziamento,
    }),
  };
}

/** Gli ingressi del motore: l'immobile e il regime vengono dall'area immobile, il resto da qui. */
export function versoMotore(
  scheda: SchedaCosto,
  immobile: Immobile,
): { immobile: ImmobileDiCalcolo; acquirente: Acquirente; finanziamento: Finanziamento } {
  const regime = leggiRegime(immobile.ipotesi);
  return {
    immobile: {
      prezzo: immobile.prezzo,
      rendita_catastale: immobile.rendita_catastale,
      categoria: immobile.categoria,
      superficie_mq: immobile.superficie_mq,
      comune: immobile.comune,
      nuova_costruzione: regime.nuova_costruzione,
      venditore_impresa: regime.venditore_impresa,
    },
    acquirente: {
      ...ACQUIRENTE_PREDEFINITO,
      prima_casa: regime.prima_casa,
      prezzo_valore: regime.prezzo_valore,
    },
    finanziamento: scheda.finanziamento,
  };
}

/** Tutte le voci del costo, prese dal motore, piu' il rapporto fra mutuo e prezzo. */
export function riepilogo(scheda: SchedaCosto, immobile: Immobile): RiepilogoCosto {
  const ingressi = versoMotore(scheda, immobile);
  const c = costoOperazione(
    ingressi.immobile,
    ingressi.acquirente,
    ingressi.finanziamento,
    scheda.costi.provvigione_aliquota,
    scheda.costi.notaio_compravendita,
    scheda.costi.altri_costi,
  );
  const rapporto = immobile.prezzo > 0 ? c.mutuo / immobile.prezzo : 0;
  return {
    prezzo: c.prezzo,
    imposteTotali: c.imposte.totale,
    regimeImposte: c.imposte.regime,
    provvigione: c.provvigione,
    notaioCompravendita: c.notaioCompravendita,
    notaioMutuo: c.notaioMutuo,
    sostitutivaMutuo: c.sostitutivaMutuo,
    istruttoria: c.istruttoria,
    perizia: c.perizia,
    altriCosti: c.altriCosti,
    costiAccessori: c.costiAccessori,
    costoTotale: c.costoTotale,
    mutuo: c.mutuo,
    esborsoIniziale: c.esborsoIniziale,
    incidenzaCosti: c.incidenzaCosti,
    rapportoMutuoPrezzo: rapporto,
    // Il rapporto ordinario e' quello oltre il quale una banca di norma non va senza garanzia
    // pubblica. Superarlo non e' un errore del modello ed e' anzi possibile con il fondo di
    // garanzia, ma e' un'assunzione che va vista mentre la si fa e non scoperta in delibera.
    oltreRapportoOrdinario: rapporto > parametriMutuo.ltvOrdinarioMax,
    rapportoOrdinarioMassimo: parametriMutuo.ltvOrdinarioMax,
  };
}

/** Scrive una voce di costo, lasciando immutata la scheda ricevuta. */
export function conCosto(
  scheda: SchedaCosto,
  campo: keyof CostiOperazione,
  valore: number,
): SchedaCosto {
  return { ...scheda, costi: { ...scheda.costi, [campo]: valore } };
}

/** Scrive un campo del finanziamento, conservando tutti gli altri della stessa sezione. */
export function conFinanziamento(
  scheda: SchedaCosto,
  campo: keyof Finanziamento,
  valore: number,
): SchedaCosto {
  return { ...scheda, finanziamento: { ...scheda.finanziamento, [campo]: valore } };
}
