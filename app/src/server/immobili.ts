// Le rotte degli immobili: dal database alla risposta, e ritorno.
//
// Il file si occupa di una cosa sola, cioe' di leggere e scrivere righe dentro il perimetro
// dell'organizzazione gia' risolta dal contesto. La forma di cio' che arriva dal browser non
// si decide qui: sta in src/condiviso/immobile.ts, che il Worker e l'interfaccia importano
// entrambi, perche' una regola di validazione scritta due volte e' una regola che al primo
// aggiornamento esiste in due versioni e fa accettare al modulo cio' che il server rifiuta.
//
// Quel che resta qui, e che non puo' stare altrove, e' la clausola sull'organizzazione:
// compare in ogni interrogazione di questo file, comprese quelle che seguono una lettura
// gia' filtrata, ed e' la ragione per cui l'indice del database e' costruito su quella
// colonna per prima.

import type { Immobile, Ipotesi } from "../condiviso/immobile";
import { validaImmobile } from "../condiviso/immobile";

import type { Contesto } from "./autorizzazione";

export type { ImmobileInviato } from "../condiviso/immobile";
export { validaImmobile } from "../condiviso/immobile";

interface RigaImmobile {
  id: string;
  organizzazione_id: string;
  titolo: string;
  comune: string;
  indirizzo: string;
  prezzo: number;
  superficie_mq: number;
  categoria: string;
  rendita_catastale: number;
  stato: string;
  ipotesi: string;
  creato_il: string;
  aggiornato_il: string;
}

/** Dalla riga del database alla forma che il browser conosce, che e' quella condivisa. */
function versoFuori(riga: RigaImmobile): Immobile {
  const { ipotesi, organizzazione_id, ...resto } = riga;
  return { ...resto, organizzazione: organizzazione_id, ipotesi: JSON.parse(ipotesi) as Ipotesi };
}

export async function elencaImmobili(ctx: Contesto): Promise<Response> {
  const esito = await ctx.db
    .prepare(
      "SELECT * FROM immobili WHERE organizzazione_id = ? ORDER BY aggiornato_il DESC, id ASC",
    )
    .bind(ctx.organizzazione)
    .all<RigaImmobile>();
  return Response.json({ immobili: (esito.results ?? []).map(versoFuori) });
}

export async function leggiImmobile(ctx: Contesto, id: string): Promise<Response> {
  const riga = await ctx.db
    .prepare("SELECT * FROM immobili WHERE id = ? AND organizzazione_id = ?")
    .bind(id, ctx.organizzazione)
    .first<RigaImmobile>();
  if (!riga) return Response.json({ errore: "immobile non trovato" }, { status: 404 });
  return Response.json(versoFuori(riga));
}

export async function creaImmobile(ctx: Contesto, corpo: unknown, id: string, adesso: string): Promise<Response> {
  const { errori, valore } = validaImmobile(corpo);
  if (!valore) return Response.json({ errori }, { status: 422 });

  await ctx.db
    .prepare(
      `INSERT INTO immobili
         (id, organizzazione_id, titolo, comune, indirizzo, prezzo, superficie_mq,
          categoria, rendita_catastale, stato, ipotesi, creato_il, aggiornato_il)
       VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)`,
    )
    .bind(
      id,
      ctx.organizzazione,
      valore.titolo,
      valore.comune,
      valore.indirizzo,
      valore.prezzo,
      valore.superficie_mq,
      valore.categoria,
      valore.rendita_catastale,
      valore.stato,
      JSON.stringify(valore.ipotesi),
      adesso,
      adesso,
    )
    .run();
  return leggiImmobile(ctx, id);
}

export async function aggiornaImmobile(ctx: Contesto, id: string, corpo: unknown, adesso: string): Promise<Response> {
  const { errori, valore } = validaImmobile(corpo);
  if (!valore) return Response.json({ errori }, { status: 422 });

  // La clausola sull'organizzazione sta anche qui, e non solo nella lettura che la precede:
  // un aggiornamento che si fidasse di un controllo fatto prima sarebbe corretto oggi e
  // scoperto domani, il giorno in cui qualcuno riordina le righe.
  const esito = await ctx.db
    .prepare(
      `UPDATE immobili
          SET titolo = ?, comune = ?, indirizzo = ?, prezzo = ?, superficie_mq = ?,
              categoria = ?, rendita_catastale = ?, stato = ?, ipotesi = ?, aggiornato_il = ?
        WHERE id = ? AND organizzazione_id = ?`,
    )
    .bind(
      valore.titolo,
      valore.comune,
      valore.indirizzo,
      valore.prezzo,
      valore.superficie_mq,
      valore.categoria,
      valore.rendita_catastale,
      valore.stato,
      JSON.stringify(valore.ipotesi),
      adesso,
      id,
      ctx.organizzazione,
    )
    .run();

  if (!esito.meta.changes) return Response.json({ errore: "immobile non trovato" }, { status: 404 });
  return leggiImmobile(ctx, id);
}

export async function rimuoviImmobile(ctx: Contesto, id: string): Promise<Response> {
  const esito = await ctx.db
    .prepare("DELETE FROM immobili WHERE id = ? AND organizzazione_id = ?")
    .bind(id, ctx.organizzazione)
    .run();
  if (!esito.meta.changes) return Response.json({ errore: "immobile non trovato" }, { status: 404 });
  return new Response(null, { status: 204 });
}
