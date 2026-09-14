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
import type {
  AppartenenzaInviata,
  Membro,
  OrganizzazioneConMembri,
  OrganizzazioneInviata,
} from "../condiviso/organizzazione";
import type { LivelloPiattaforma, Ruolo } from "../condiviso/ruoli";

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
  /**
   * Il livello sulla piattaforma, o null per la stragrande maggioranza di chi entra.
   *
   * Arriva insieme alle appartenenze e non da una rotta propria, perche' l'interfaccia deve
   * sapere se mostrare il pannello di amministrazione prima di poterlo chiedere: una rotta che
   * rispondesse "non ti e' permesso" costringerebbe a interrogarla sempre e a trattare il
   * rifiuto come un esito ordinario, che e' il modo in cui un rifiuto smette di essere notato.
   */
  livello: LivelloPiattaforma | null;
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

const ORGANIZZAZIONI = "/api/piattaforma/organizzazioni";

export function creaCliente(recupera: Recupero = RECUPERO_PREDEFINITO) {
  const json = (metodo: string, corpo: unknown): RequestInit => ({
    method: metodo,
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify(corpo),
  });

  const sotto = (org: string) => `/api/organizzazioni/${encodeURIComponent(org)}`;
  const immobiliDi = (org: string) => `${sotto(org)}/immobili`;
  const membriDi = (org: string) => `${sotto(org)}/membri`;

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

    // --- chi fa parte di un'organizzazione ---

    async elencaMembri(org: string): Promise<Membro[]> {
      const esito = await esigi<{ membri: Membro[] }>(await recupera(membriDi(org)));
      return esito.membri;
    },

    /**
     * Aggiunge un membro o ne cambia il ruolo, e restituisce l'elenco come e' rimasto.
     *
     * Una sola chiamata per le due cose, perche' dal punto di vista di chi amministra lo sono: si
     * dichiara quale ruolo una persona deve avere, e che ci fosse gia' o no e' un dettaglio. Il
     * server risponde con l'elenco completo invece che con la riga toccata, cosi' l'interfaccia
     * non ricostruisce uno stato che il server conosce meglio di lei.
     */
    async scriviMembro(org: string, appartenenza: AppartenenzaInviata): Promise<Membro[]> {
      const esito = await esigi<{ membri: Membro[] }>(
        await recupera(membriDi(org), json("PUT", appartenenza)),
      );
      return esito.membri;
    },

    async rimuoviMembro(org: string, email: string): Promise<Membro[]> {
      const esito = await esigi<{ membri: Membro[] }>(
        await recupera(`${membriDi(org)}/${encodeURIComponent(email)}`, { method: "DELETE" }),
      );
      return esito.membri;
    },

    // --- l'amministrazione del prodotto ---

    async elencaOrganizzazioni(): Promise<OrganizzazioneConMembri[]> {
      const esito = await esigi<{ organizzazioni: OrganizzazioneConMembri[] }>(
        await recupera(ORGANIZZAZIONI),
      );
      return esito.organizzazioni;
    },

    async creaOrganizzazione(nuova: OrganizzazioneInviata): Promise<OrganizzazioneConMembri[]> {
      const esito = await esigi<{ organizzazioni: OrganizzazioneConMembri[] }>(
        await recupera(ORGANIZZAZIONI, json("POST", nuova)),
      );
      return esito.organizzazioni;
    },

    async rimuoviOrganizzazione(id: string): Promise<OrganizzazioneConMembri[]> {
      const esito = await esigi<{ organizzazioni: OrganizzazioneConMembri[] }>(
        await recupera(`${ORGANIZZAZIONI}/${encodeURIComponent(id)}`, { method: "DELETE" }),
      );
      return esito.organizzazioni;
    },
  };
}

export type Cliente = ReturnType<typeof creaCliente>;
