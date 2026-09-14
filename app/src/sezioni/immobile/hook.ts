// L'hook che tiene l'elenco degli immobili di un'organizzazione.
//
// Due cose meritano di essere dette, perche' sono le due che in un hook di questo genere si
// sbagliano quasi sempre.
//
// La prima e' la corsa fra due caricamenti. Se si cambia organizzazione mentre la prima
// risposta e' ancora in volo, le due risposte arrivano in un ordine che non e' garantito, e
// quella vecchia puo' arrivare per ultima: il risultato e' l'elenco di un'organizzazione
// mostrato sotto il nome di un'altra. Su un prodotto multiproprieta' non e' un difetto
// estetico, e' la cosa esatta che l'intero impianto di autorizzazione esiste per impedire, che
// rientra dalla finestra dopo essere stata cacciata dalla porta. La difesa e' un contrassegno
// per ogni caricamento: quando la risposta torna, se il contrassegno non e' piu' quello
// corrente, la si butta.
//
// La seconda e' che dopo una scrittura l'elenco non si ricarica dal server: si aggiorna con la
// riga che il server ha appena restituito. Il server risponde sempre con l'immobile come e'
// rimasto, quindi la riga e' quella vera e non una ricostruzione ottimistica; ricaricare
// tutto sarebbe una richiesta in piu' per sapere una cosa che si sa gia'.

import { useCallback, useEffect, useRef, useState } from "react";

import type { Immobile, ImmobileInviato } from "../../condiviso/immobile";
import type { Cliente } from "../../interfaccia/cliente";

export interface StatoImmobili {
  immobili: Immobile[];
  caricamento: boolean;
  errore: string | null;
  ricarica: () => void;
  crea: (corpo: ImmobileInviato) => Promise<Immobile>;
  aggiorna: (id: string, corpo: ImmobileInviato) => Promise<Immobile>;
  rimuovi: (id: string) => Promise<void>;
}

/** L'ordine dell'elenco: ultima modifica per prima, come fa la rotta. */
function ordina(immobili: Immobile[]): Immobile[] {
  return [...immobili].sort((a, b) =>
    a.aggiornato_il === b.aggiornato_il
      ? a.id.localeCompare(b.id)
      : b.aggiornato_il.localeCompare(a.aggiornato_il),
  );
}

export function useImmobili(cliente: Cliente, organizzazione: string | null): StatoImmobili {
  const [immobili, setImmobili] = useState<Immobile[]>([]);
  const [caricamento, setCaricamento] = useState(false);
  const [errore, setErrore] = useState<string | null>(null);
  const corsa = useRef(0);

  const ricarica = useCallback(() => {
    if (!organizzazione) {
      corsa.current += 1;
      setImmobili([]);
      setCaricamento(false);
      setErrore(null);
      return;
    }
    const mia = (corsa.current += 1);
    setCaricamento(true);
    setErrore(null);
    cliente
      .elencaImmobili(organizzazione)
      .then((elenco) => {
        if (corsa.current !== mia) return;
        setImmobili(ordina(elenco));
        setCaricamento(false);
      })
      .catch((e: unknown) => {
        if (corsa.current !== mia) return;
        setErrore(e instanceof Error ? e.message : "errore imprevisto");
        setCaricamento(false);
      });
  }, [cliente, organizzazione]);

  useEffect(ricarica, [ricarica]);

  const inserisci = useCallback((salvato: Immobile) => {
    setImmobili((attuali) => ordina([salvato, ...attuali.filter((i) => i.id !== salvato.id)]));
  }, []);

  const crea = useCallback(
    async (corpo: ImmobileInviato) => {
      if (!organizzazione) throw new Error("nessuna organizzazione selezionata");
      const salvato = await cliente.creaImmobile(organizzazione, corpo);
      inserisci(salvato);
      return salvato;
    },
    [cliente, organizzazione, inserisci],
  );

  const aggiorna = useCallback(
    async (id: string, corpo: ImmobileInviato) => {
      if (!organizzazione) throw new Error("nessuna organizzazione selezionata");
      const salvato = await cliente.aggiornaImmobile(organizzazione, id, corpo);
      inserisci(salvato);
      return salvato;
    },
    [cliente, organizzazione, inserisci],
  );

  const rimuovi = useCallback(
    async (id: string) => {
      if (!organizzazione) throw new Error("nessuna organizzazione selezionata");
      await cliente.rimuoviImmobile(organizzazione, id);
      setImmobili((attuali) => attuali.filter((i) => i.id !== id));
    },
    [cliente, organizzazione],
  );

  return { immobili, caricamento, errore, ricarica, crea, aggiorna, rimuovi };
}
