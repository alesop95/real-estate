// Il ciclo di modifica e salvataggio di una scheda, comune a tutte le aree.
//
// Ogni area lavora allo stesso modo: prende l'immobile scelto, ne ricava una bozza tipizzata, la
// si modifica, e a un certo punto la si salva. Attorno a questo ci sono cinque cose che non hanno
// niente a che vedere con la materia dell'area e che pure andrebbero riscritte in ciascuna:
// azzerare la bozza quando cambia l'immobile scelto, applicare la validazione condivisa prima di
// partire, tenere lo stato di attesa, portare fuori il rifiuto del server in una forma leggibile,
// e sapere se ci sono modifiche non salvate.
//
// Scritte sei volte diventerebbero sei varianti, e la variante che si perde per prima e' sempre
// la stessa: l'azzeramento quando cambia l'immobile. Un'area che se lo dimentica mostra i dati
// dell'immobile precedente sotto il nome del nuovo, e chi salva sovrascrive il secondo con il
// primo. Su un prodotto multiproprieta' e' il guasto peggiore di questa categoria, perche' non
// fallisce e non si vede finche' qualcuno non riapre la scheda.
//
// La validazione applicata qui e' quella di src/condiviso/immobile.ts, cioe' la stessa che il
// Worker riapplichera'. Non e' una difesa: e' l'anticipo di una risposta che si puo' dare senza un
// giro di rete, per ADR-027.

import { useCallback, useEffect, useRef, useState } from "react";

import type { Immobile, ImmobileInviato } from "../condiviso/immobile";
import { validaImmobile } from "../condiviso/immobile";

import { quando } from "./formato";

export interface Bozza<S> {
  bozza: S;
  /** Modifica la bozza, e azzera il messaggio di conferma perche' non e' piu' vero. */
  cambia: (aggiorna: (precedente: S) => S) => void;
  errori: readonly string[];
  messaggio: string | null;
  salvataggio: boolean;
  /** Vero se la bozza differisce da cio' che il server ha. */
  modificata: boolean;
  salva: () => Promise<void>;
}

/**
 * L'impronta di un immobile ai fini della bozza.
 *
 * Non e' l'oggetto e non e' il solo identificativo. L'oggetto cambia identita' a ogni ricarica
 * dell'elenco, e farlo osservare butterebbe via cio' che si sta scrivendo; il solo identificativo
 * non basta, perche' dopo un salvataggio l'immobile e' lo stesso ma il contenuto no, e la bozza
 * deve ripartire da cio' che il server ha davvero accettato.
 */
function impronta(immobile: Immobile | null): string {
  return immobile ? `${immobile.id}@${immobile.aggiornato_il}` : "nuovo";
}

export function useBozza<S>(
  immobile: Immobile | null,
  daImmobile: (immobile: Immobile | null) => S,
  versoInvio: (bozza: S, immobile: Immobile | null) => ImmobileInviato,
  salvaSulServer: (corpo: ImmobileInviato) => Promise<Immobile>,
): Bozza<S> {
  const [bozza, setBozza] = useState<S>(() => daImmobile(immobile));
  const [errori, setErrori] = useState<readonly string[]>([]);
  const [messaggio, setMessaggio] = useState<string | null>(null);
  const [salvataggio, setSalvataggio] = useState(false);

  // Le due funzioni arrivano ridefinite a ogni resa, perche' le aree le passano come letterali.
  // Tenerle in un riferimento le rende utilizzabili dentro l'effetto senza che l'effetto
  // riparta a ogni battitura, che e' precisamente cio' che cancellerebbe la bozza.
  const converti = useRef(daImmobile);
  converti.current = daImmobile;
  const invia = useRef(versoInvio);
  invia.current = versoInvio;
  const salvaOra = useRef(salvaSulServer);
  salvaOra.current = salvaSulServer;

  // L'impronta dell'ultimo salvataggio riuscito. Serve a non cancellare la conferma appena
  // mostrata: il salvataggio fa arrivare un immobile nuovo, l'impronta cambia, e senza questo
  // confronto l'effetto che riazzera la bozza spegnerebbe il messaggio che dice che e' andata.
  const appenaSalvato = useRef<string | null>(null);
  const attuale = impronta(immobile);

  useEffect(() => {
    setBozza(converti.current(immobile));
    setErrori([]);
    if (appenaSalvato.current !== attuale) setMessaggio(null);
    appenaSalvato.current = null;
    // Si osserva l'impronta e non l'immobile, per la ragione scritta sopra la funzione.
  }, [attuale]);

  const cambia = useCallback((aggiorna: (precedente: S) => S) => {
    setBozza(aggiorna);
    setMessaggio(null);
  }, []);

  const modificata =
    JSON.stringify(versoInvio(bozza, immobile)) !==
    JSON.stringify(versoInvio(daImmobile(immobile), immobile));

  const salva = useCallback(async () => {
    const corpo = invia.current(bozza, immobile);
    const { errori: problemi } = validaImmobile(corpo);
    if (problemi.length) {
      setErrori(problemi);
      return;
    }
    setErrori([]);
    setSalvataggio(true);
    try {
      const salvato = await salvaOra.current(corpo);
      appenaSalvato.current = impronta(salvato);
      setMessaggio(`Salvato alle ${quando(salvato.aggiornato_il)}.`);
    } catch (e: unknown) {
      setErrori([e instanceof Error ? e.message : "errore imprevisto nel salvataggio"]);
    } finally {
      setSalvataggio(false);
    }
  }, [bozza, immobile]);

  return { bozza, cambia, errori, messaggio, salvataggio, modificata, salva };
}
