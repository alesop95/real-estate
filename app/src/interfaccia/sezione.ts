// Il contratto di un'area, cioe' che cosa il guscio consegna a ciascuna delle sei.
//
// Vale la pena che sia un tipo dichiarato e non una convenzione, perche' fissa una divisione di
// responsabilita' che altrimenti si sposterebbe di area in area. Il guscio possiede tre cose: chi
// sei, quale immobile e' aperto, e come si salva. Un'area non carica l'elenco, non sceglie
// l'immobile e non parla con il server: riceve l'immobile e una funzione che salva, e se avesse
// il cliente potrebbe fare per conto proprio tutto il resto, che e' esattamente cio' che
// produrrebbe sei elenchi caricati sei volte e sei selezioni che si perdono passando da un'area
// all'altra.

import type { Immobile, ImmobileInviato } from "../condiviso/immobile";
import type { Ruolo } from "../condiviso/ruoli";

export interface ProprietaSezione {
  /** L'immobile aperto, oppure null quando si sta creando il primo o uno nuovo. */
  immobile: Immobile | null;
  /** Il ruolo di chi guarda dentro l'organizzazione scelta. */
  ruolo: Ruolo;
  /** Crea o aggiorna, secondo che un immobile sia aperto o no, e restituisce cio' che il server ha. */
  salva: (corpo: ImmobileInviato) => Promise<Immobile>;
  /**
   * Rimuove l'immobile aperto, o null quando non ce n'e' uno.
   *
   * Sta nel contratto e non nell'area perche' e' un'azione sul record e non sulla materia di
   * una schermata, come il salvataggio. Che sia null quando non c'e' nulla di aperto e' cio'
   * che rende impossibile offrire il gesto nel momento in cui non ha bersaglio: l'alternativa,
   * cioe' una funzione che non fa niente, lascerebbe all'area il compito di ricordarsene.
   */
  rimuovi: (() => Promise<void>) | null;
}
