// L'unico punto dell'interfaccia che parla con il server.
//
// Nessuna sezione chiama fetch per conto proprio, e la ragione non e' l'ordine: e' che un
// giorno andranno aggiunte cose che riguardano ogni chiamata, per esempio il rinnovo di una
// sessione scaduta di Access o un messaggio uniforme quando la rete non c'e', e quel giorno
// la differenza fra un posto e quindici e' la differenza fra farlo e non farlo.
//
// La funzione di recupero e' un parametro con un valore predefinito, per la stessa ragione
// per cui nel Worker lo e' la fonte delle chiavi di Access: cosi' le prove esercitano il
// cliente vero contro un server finto, invece di esercitare un cliente finto.

import type { Immobile, ImmobileInviato } from "../condiviso/immobile";
import type { Ruolo } from "../condiviso/ruoli";

/** Un'appartenenza, cioe' un'organizzazione piu' il ruolo che vi si ha dentro. */
export interface Appartenenza {
  id: string;
  nome: string;
  ruolo: Ruolo;
}

/** Chi sono io: la risposta di /api/io. */
export interface Io {
  email: string;
  organizzazioni: Appartenenza[];
}

/**
 * Un rifiuto del server, con lo stato e, quando ci sono, gli errori di forma.
 *
 * Gli errori di forma restano un elenco e non diventano una frase: la sezione li mostra uno
 * per campo, e concatenarli qui vorrebbe dire disfarli dopo.
 */
export class ErroreApi extends Error {
  constructor(
    readonly stato: number,
    readonly errori: readonly string[],
    messaggio: string,
  ) {
    super(messaggio);
    this.name = "ErroreApi";
  }
}

export type Recupero = (richiesta: string, opzioni?: RequestInit) => Promise<Response>;

const RECUPERO_PREDEFINITO: Recupero = (richiesta, opzioni) => fetch(richiesta, opzioni);

async function esigi<T>(risposta: Response): Promise<T> {
  if (risposta.ok) {
    if (risposta.status === 204) return undefined as T;
    return (await risposta.json()) as T;
  }
  // Un rifiuto puo' non essere JSON: Access, quando la sessione scade, risponde con una
  // pagina. Leggerlo come JSON senza rete di sicurezza trasformerebbe "devi rientrare" in
  // un errore di sintassi, che e' il messaggio piu' inutile possibile.
  const corpo = (await risposta.json().catch(() => null)) as
    | { errore?: string; errori?: string[] }
    | null;
  const errori = corpo?.errori ?? [];
  const messaggio =
    corpo?.errore ??
    (errori.length ? errori.join("; ") : `il server ha risposto ${risposta.status}`);
  throw new ErroreApi(risposta.status, errori, messaggio);
}

export function creaCliente(recupera: Recupero = RECUPERO_PREDEFINITO) {
  const json = (metodo: string, corpo: unknown): RequestInit => ({
    method: metodo,
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify(corpo),
  });

  const immobiliDi = (org: string) => `/api/organizzazioni/${encodeURIComponent(org)}/immobili`;

  return {
    async io(): Promise<Io> {
      return esigi<Io>(await recupera("/api/io"));
    },

    async elencaImmobili(org: string): Promise<Immobile[]> {
      const esito = await esigi<{ immobili: Immobile[] }>(await recupera(immobiliDi(org)));
      return esito.immobili;
    },

    async leggiImmobile(org: string, id: string): Promise<Immobile> {
      return esigi<Immobile>(await recupera(`${immobiliDi(org)}/${encodeURIComponent(id)}`));
    },

    async creaImmobile(org: string, corpo: ImmobileInviato): Promise<Immobile> {
      return esigi<Immobile>(await recupera(immobiliDi(org), json("POST", corpo)));
    },

    async aggiornaImmobile(org: string, id: string, corpo: ImmobileInviato): Promise<Immobile> {
      return esigi<Immobile>(
        await recupera(`${immobiliDi(org)}/${encodeURIComponent(id)}`, json("PUT", corpo)),
      );
    },

    async rimuoviImmobile(org: string, id: string): Promise<void> {
      await esigi<void>(
        await recupera(`${immobiliDi(org)}/${encodeURIComponent(id)}`, { method: "DELETE" }),
      );
    },
  };
}

export type Cliente = ReturnType<typeof creaCliente>;
