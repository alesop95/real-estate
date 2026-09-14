// L'autorizzazione, in un posto solo, e in una forma che non si puo' dimenticare.
//
// Questa e' la parte che ADR-024 obbliga a scrivere con cura, e la ragione va ripetuta qui
// perche' e' il genere di cosa che si dimentica dopo tre mesi. Con un database che applica regole
// dichiarative, come Firestore, una regola dimenticata nega l'accesso: si sbaglia rumorosamente,
// l'applicazione smette di funzionare e qualcuno se ne accorge subito. Con un'interfaccia di
// programmazione, come qui, una rotta che dimentica il controllo concede l'accesso: si sbaglia in
// silenzio, tutto funziona, e il dato di un cliente e' visibile a un altro finche' non lo scopre
// lui.
//
// La contromisura non e' raccomandare la forma giusta, e' rendere impossibile quella sbagliata.
// Una rotta non si registra chiamando il router: si registra passando da `rotta` o da
// `rottaPiattaforma`, che pretendono il requisito come argomento obbligatorio e consegnano al
// gestore un contesto gia' autorizzato. Il gestore non riceve la richiesta grezza e non ha modo
// di vedere l'organizzazione chiesta prima che l'appartenenza sia stata verificata, quindi
// scrivere una rotta senza controllo richiederebbe di aggirare deliberatamente il registro, che
// e' un gesto visibile in revisione, non una dimenticanza.
//
// Dal 14 settembre 2026 le famiglie di rotte sono due, per ADR-029. Quelle sotto
// un'organizzazione toccano i dati e chiedono un ruolo; quelle di piattaforma toccano il registro
// delle organizzazioni e chiedono un livello. Le due non si sommano e non si implicano, ed e' la
// scelta di sostanza: un superamministratore puo' creare l'organizzazione di un cliente e
// nominarne l'amministratore, e non puo' leggerne gli immobili. Se vuole vederli deve aggiungersi
// fra i membri, e quell'aggiunta lascia una riga. Non e' impossibilita', e' tracciabilita': la
// differenza va detta, perche' chi compra il prodotto ha diritto di sapere quale delle due gli si
// sta promettendo.

import type { Context, Hono } from "hono";

import {
  livelloSufficiente,
  ruoloSufficiente,
  type LivelloPiattaforma,
  type Ruolo,
} from "../condiviso/ruoli";

import { identita, type Ambiente, type FonteChiavi, type Identita } from "./identita";

// I livelli e la loro gerarchia stanno in src/condiviso/ruoli.ts, perche' la stessa domanda se la
// fa anche l'interfaccia, per non mostrare un gesto che produrrebbe soltanto un rifiuto. Qui si
// riesportano perche' questo resta il modulo che le rotte importano: la difesa e' quella che si
// applica di seguito, non quella del browser.
export {
  livelloSufficiente,
  ruoloSufficiente,
  type LivelloPiattaforma,
  type Ruolo,
} from "../condiviso/ruoli";

/** Che cosa un gestore di rotta sotto organizzazione riceve: tutto gia' risolto. */
export interface Contesto {
  identita: Identita;
  organizzazione: string;
  ruolo: Ruolo;
  db: D1Database;
}

/** Che cosa un gestore di rotta di piattaforma riceve. Non c'e' organizzazione, ed e' il punto. */
export interface ContestoPiattaforma {
  identita: Identita;
  livello: LivelloPiattaforma;
  db: D1Database;
}

/**
 * Il requisito di una rotta, in forma discriminata e non come due campi facoltativi.
 *
 * La differenza non e' di gusto: con due campi entrambi opzionali esisterebbe la forma in cui
 * nessuno dei due e' valorizzato, cioe' una rotta registrata senza requisito, e il registro
 * smetterebbe di essere la prova che non ne esistono. Con l'unione quella forma non compila.
 */
export type Requisito =
  | { tipo: "organizzazione"; ruoloMinimo: Ruolo }
  | { tipo: "piattaforma"; livelloMinimo: LivelloPiattaforma };

export interface Registrazione {
  metodo: "get" | "post" | "put" | "delete";
  percorso: string;
  requisito: Requisito;
}

/** Il registro delle rotte, tenuto per potervi scrivere sopra dei test. */
export const registro: Registrazione[] = [];

export type Gestore = (contesto: Contesto, c: Context) => Promise<Response> | Response;

export type GestorePiattaforma = (
  contesto: ContestoPiattaforma,
  c: Context,
) => Promise<Response> | Response;

/**
 * Appartenenza di una persona a un'organizzazione, oppure null.
 *
 * Sta qui e non nei gestori perche' il ruolo non e' un dato applicativo: e' il fondamento su cui
 * ogni gestore poggia.
 */
export async function appartenenza(
  db: D1Database,
  organizzazione: string,
  email: string,
): Promise<Ruolo | null> {
  const riga = await db
    .prepare("SELECT ruolo FROM membri WHERE organizzazione_id = ? AND email = ?")
    .bind(organizzazione, email)
    .first<{ ruolo: Ruolo }>();
  return riga ? riga.ruolo : null;
}

/** Livello di piattaforma di una persona, oppure null, che e' il caso ordinario. */
export async function livelloDi(
  db: D1Database,
  email: string,
): Promise<LivelloPiattaforma | null> {
  const riga = await db
    .prepare("SELECT livello FROM gestori WHERE email = ?")
    .bind(email)
    .first<{ livello: LivelloPiattaforma }>();
  return riga ? riga.livello : null;
}

/**
 * Registra una rotta sotto un'organizzazione, con il ruolo minimo richiesto.
 *
 * Sui codici di rifiuto c'e' una scelta che vale spiegare. A chi non e' membro si risponde
 * quattrocentoquattro e non quattrocentotre, cioe' "non esiste" e non "non ti e' permesso": un
 * divieto esplicito confermerebbe che quell'organizzazione esiste, e su un prodotto
 * multiproprieta' l'esistenza di un cliente e' gia' un'informazione. Il divieto esplicito resta
 * invece per chi e' membro ma con un ruolo insufficiente, dove la conferma non aggiunge nulla che
 * il chiamante non sappia gia'.
 */
export function rotta(
  app: Hono<{ Bindings: Ambiente }>,
  metodo: Registrazione["metodo"],
  percorso: string,
  ruoloMinimo: Ruolo,
  gestore: Gestore,
  fonteChiavi?: FonteChiavi,
): void {
  registro.push({ metodo, percorso, requisito: { tipo: "organizzazione", ruoloMinimo } });
  app[metodo](percorso, async (c) => {
    const chi = await identita(c.req.raw, c.env, fonteChiavi);
    if (!chi) return c.json({ errore: "non autenticato" }, 401);

    const organizzazione = c.req.param("org");
    if (!organizzazione) return c.json({ errore: "organizzazione non indicata" }, 400);

    // Non c'e' scorciatoia per il livello di piattaforma, ed e' deliberato: per ADR-029 un
    // superamministratore non e' membro di niente finche' non lo diventa esplicitamente.
    const ruolo = await appartenenza(c.env.DB, organizzazione, chi.email);
    if (!ruolo) return c.json({ errore: "organizzazione non trovata" }, 404);
    if (!ruoloSufficiente(ruolo, ruoloMinimo)) {
      return c.json({ errore: `serve il ruolo ${ruoloMinimo}, hai ${ruolo}` }, 403);
    }

    return gestore({ identita: chi, organizzazione, ruolo, db: c.env.DB }, c);
  });
}

/**
 * Registra una rotta di piattaforma, con il livello minimo richiesto.
 *
 * Qui il rifiuto a chi non ha alcun livello e' quattrocentotre e non quattrocentoquattro, e la
 * differenza rispetto alle rotte sotto organizzazione e' voluta. La' nascondere l'esistenza
 * serve, perche' confermarla rivelerebbe l'esistenza di un cliente; qui non c'e' niente da
 * nascondere, perche' l'esistenza di un pannello di amministrazione della piattaforma non e'
 * un'informazione riservata, e rispondere "non esiste" a chi semplicemente non e' amministratore
 * lo manderebbe a cercare un difetto che non c'e'.
 */
export function rottaPiattaforma(
  app: Hono<{ Bindings: Ambiente }>,
  metodo: Registrazione["metodo"],
  percorso: string,
  livelloMinimo: LivelloPiattaforma,
  gestore: GestorePiattaforma,
  fonteChiavi?: FonteChiavi,
): void {
  registro.push({ metodo, percorso, requisito: { tipo: "piattaforma", livelloMinimo } });
  app[metodo](percorso, async (c) => {
    const chi = await identita(c.req.raw, c.env, fonteChiavi);
    if (!chi) return c.json({ errore: "non autenticato" }, 401);

    const livello = await livelloDi(c.env.DB, chi.email);
    if (!livelloSufficiente(livello, livelloMinimo)) {
      return c.json({ errore: `serve il livello ${livelloMinimo} sulla piattaforma` }, 403);
    }

    // Il livello non e' nullo: `livelloSufficiente` restituisce falso per il null, quindi qui
    // siamo oltre quel caso e l'asserzione e' sicura.
    return gestore({ identita: chi, livello: livello as LivelloPiattaforma, db: c.env.DB }, c);
  });
}
