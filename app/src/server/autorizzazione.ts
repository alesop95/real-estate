// L'autorizzazione, in un posto solo, e in una forma che non si puo' dimenticare.
//
// Questa e' la parte che ADR-024 obbliga a scrivere con cura, e la ragione va ripetuta qui
// perche' e' il genere di cosa che si dimentica dopo tre mesi. Con un database che applica
// regole dichiarative, come Firestore, una regola dimenticata nega l'accesso: si sbaglia
// rumorosamente, l'applicazione smette di funzionare e qualcuno se ne accorge subito. Con
// un'interfaccia di programmazione, come qui, una rotta che dimentica il controllo concede
// l'accesso: si sbaglia in silenzio, tutto funziona, e il dato di un cliente e' visibile a un
// altro finche' non lo scopre lui.
//
// La contromisura non e' raccomandare la forma giusta, e' rendere impossibile quella
// sbagliata. Una rotta non si registra chiamando il router: si registra passando da
// `rotta`, che pretende il ruolo minimo come argomento obbligatorio e consegna al gestore un
// contesto gia' autorizzato. Il gestore non riceve la richiesta grezza e non ha modo di
// vedere l'organizzazione chiesta prima che l'appartenenza sia stata verificata, quindi
// scrivere una rotta senza controllo richiederebbe di aggirare deliberatamente il registro,
// che e' un gesto visibile in revisione, non una dimenticanza.

import type { Context, Hono } from "hono";

import { ruoloSufficiente, type Ruolo } from "../condiviso/ruoli";

import { identita, type Ambiente, type FonteChiavi, type Identita } from "./identita";

// I ruoli e la loro gerarchia stanno in src/condiviso/ruoli.ts, perche' dal 14 settembre
// 2026 la stessa domanda se la fa anche l'interfaccia, per non mostrare un pulsante che
// produrrebbe soltanto un rifiuto. Qui si riesportano perche' questo resta il modulo che
// le rotte importano: la difesa e' quella che si applica di seguito, non quella del browser.
export { ruoloSufficiente, type Ruolo } from "../condiviso/ruoli";

/** Che cosa un gestore riceve: tutto gia' risolto, niente da verificare. */
export interface Contesto {
  identita: Identita;
  organizzazione: string;
  ruolo: Ruolo;
  db: D1Database;
}

export interface Registrazione {
  metodo: "get" | "post" | "put" | "delete";
  percorso: string;
  ruoloMinimo: Ruolo;
}

/** Il registro delle rotte, tenuto per potervi scrivere sopra dei test. */
export const registro: Registrazione[] = [];

export type Gestore = (contesto: Contesto, c: Context) => Promise<Response> | Response;

/**
 * Appartenenza di una persona a un'organizzazione, oppure null.
 *
 * E' l'unica interrogazione di questo modulo, e sta qui e non nei gestori perche' il ruolo
 * non e' un dato applicativo: e' il fondamento su cui ogni gestore poggia.
 */
export async function appartenenza(db: D1Database, organizzazione: string, email: string): Promise<Ruolo | null> {
  const riga = await db
    .prepare("SELECT ruolo FROM membri WHERE organizzazione_id = ? AND email = ?")
    .bind(organizzazione, email)
    .first<{ ruolo: Ruolo }>();
  return riga ? riga.ruolo : null;
}

/**
 * Registra una rotta sotto un'organizzazione, con il ruolo minimo richiesto.
 *
 * Sui codici di rifiuto c'e' una scelta che vale spiegare. A chi non e' membro si risponde
 * quattrocentoquattro e non quattrocentotre, cioe' "non esiste" e non "non ti e' permesso":
 * un divieto esplicito confermerebbe che quell'organizzazione esiste, e su un prodotto
 * multiproprieta' l'esistenza di un cliente e' gia' un'informazione. Il divieto esplicito
 * resta invece per chi e' membro ma con un ruolo insufficiente, dove la conferma non aggiunge
 * nulla che il chiamante non sappia gia'.
 */
export function rotta(
  app: Hono<{ Bindings: Ambiente }>,
  metodo: Registrazione["metodo"],
  percorso: string,
  ruoloMinimo: Ruolo,
  gestore: Gestore,
  fonteChiavi?: FonteChiavi,
): void {
  registro.push({ metodo, percorso, ruoloMinimo });
  app[metodo](percorso, async (c) => {
    const chi = await identita(c.req.raw, c.env, fonteChiavi);
    if (!chi) return c.json({ errore: "non autenticato" }, 401);

    const organizzazione = c.req.param("org");
    if (!organizzazione) return c.json({ errore: "organizzazione non indicata" }, 400);

    const ruolo = await appartenenza(c.env.DB, organizzazione, chi.email);
    if (!ruolo) return c.json({ errore: "organizzazione non trovata" }, 404);
    if (!ruoloSufficiente(ruolo, ruoloMinimo)) {
      return c.json({ errore: `serve il ruolo ${ruoloMinimo}, hai ${ruolo}` }, 403);
    }

    return gestore({ identita: chi, organizzazione, ruolo, db: c.env.DB }, c);
  });
}
