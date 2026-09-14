// Chi fa parte di un'organizzazione, e chi puo' cambiarlo.
//
// Queste rotte esistono per togliere di mezzo l'ultima scrittura a mano nel database. Fino al 14
// settembre 2026 la prima appartenenza si creava con un comando SQL, e la procedura di messa in
// rete lo dichiarava come cosa provvisoria, in attesa di "un pannello di amministrazione con un
// ruolo che la protegge". Il ruolo c'e' sempre stato, cioe' `amministratore`; mancavano le rotte.
//
// L'invariante che questo file difende, e che nessun altro puo' difendere al posto suo, e' che
// un'organizzazione non resti senza amministratori. Lo schema non lo puo' esprimere, perche' e'
// una condizione su un insieme di righe e non su una riga; il browser non lo puo' garantire,
// perche' chiunque puo' parlare all'interfaccia di programmazione senza passarci. Resta qui, e
// resta scritto una volta sola in `restaSenzaAmministratori`, perche' le due operazioni che
// possono violarlo sono due, cioe' la revoca e la retrocessione, e scrivere due volte lo stesso
// controllo significa che una delle due versioni prima o poi cambiera' da sola.
//
// Il caso concreto da cui nasce non e' teorico: l'unico amministratore che si retrocede a membro
// per provare come si vede l'applicazione con meno permessi, e poi non puo' piu' rimettersi
// amministratore, perche' per farlo servirebbe il ruolo che si e' appena tolto.

import { normalizzaEmail, type Membro } from "../condiviso/organizzazione";
import { validaAppartenenza } from "../condiviso/organizzazione";

import type { Contesto } from "./autorizzazione";

/** I membri di un'organizzazione, gli amministratori per primi e poi in ordine di indirizzo. */
export async function elencaMembri(ctx: Contesto): Promise<Response> {
  const esito = await ctx.db
    .prepare(
      `SELECT email, ruolo, aggiunto_il
         FROM membri
        WHERE organizzazione_id = ?
        ORDER BY CASE ruolo WHEN 'amministratore' THEN 0 WHEN 'membro' THEN 1 ELSE 2 END, email`,
    )
    .bind(ctx.organizzazione)
    .all<Membro>();
  return Response.json({ membri: esito.results ?? [] });
}

/** Quanti amministratori ha l'organizzazione, escludendone eventualmente uno. */
async function amministratori(ctx: Contesto, escluso?: string): Promise<number> {
  const riga = await ctx.db
    .prepare(
      `SELECT COUNT(*) AS quanti
         FROM membri
        WHERE organizzazione_id = ? AND ruolo = 'amministratore' AND email <> ?`,
    )
    .bind(ctx.organizzazione, escluso ?? "")
    .first<{ quanti: number }>();
  return riga?.quanti ?? 0;
}

/**
 * Vero se togliere o retrocedere questa persona lascerebbe l'organizzazione senza amministratori.
 *
 * Scritta una volta e chiamata da entrambe le operazioni che possono violare l'invariante. La
 * domanda e' sempre la stessa, cioe' quanti amministratori restano se questo non lo e' piu'.
 */
async function restaSenzaAmministratori(ctx: Contesto, email: string): Promise<boolean> {
  const riga = await ctx.db
    .prepare("SELECT ruolo FROM membri WHERE organizzazione_id = ? AND email = ?")
    .bind(ctx.organizzazione, email)
    .first<{ ruolo: string }>();
  if (!riga || riga.ruolo !== "amministratore") return false;
  return (await amministratori(ctx, email)) === 0;
}

/**
 * Aggiunge un membro o ne cambia il ruolo.
 *
 * E' una sola operazione e non due, e la ragione e' che dal punto di vista di chi amministra lo
 * sono: si dichiara quale ruolo una persona deve avere in questa organizzazione, e che ci fosse
 * gia' o no e' un dettaglio. Due rotte distinte obbligherebbero l'interfaccia a sapere prima se
 * la riga esiste, cioe' a fare una lettura per scegliere quale scrittura fare, e fra la lettura e
 * la scrittura qualcun altro potrebbe averla creata.
 */
export async function scriviMembro(ctx: Contesto, corpo: unknown, adesso: string): Promise<Response> {
  const { errori, valore } = validaAppartenenza(corpo);
  if (!valore) return Response.json({ errori }, { status: 422 });

  if (valore.ruolo !== "amministratore" && (await restaSenzaAmministratori(ctx, valore.email))) {
    return Response.json(
      {
        errore:
          "e' l'ultimo amministratore dell'organizzazione: nominane un altro prima di retrocedere questo",
      },
      { status: 409 },
    );
  }

  await ctx.db
    .prepare(
      `INSERT INTO membri (organizzazione_id, email, ruolo, aggiunto_il)
       VALUES (?, ?, ?, ?)
       ON CONFLICT (organizzazione_id, email) DO UPDATE SET ruolo = excluded.ruolo`,
    )
    .bind(ctx.organizzazione, valore.email, valore.ruolo, adesso)
    .run();

  return elencaMembri(ctx);
}

/** Revoca un'appartenenza, se non e' l'ultima che tiene in piedi l'organizzazione. */
export async function rimuoviMembro(ctx: Contesto, emailGrezza: string): Promise<Response> {
  const email = normalizzaEmail(emailGrezza);

  if (await restaSenzaAmministratori(ctx, email)) {
    return Response.json(
      {
        errore:
          "e' l'ultimo amministratore dell'organizzazione: nominane un altro prima di revocare questo",
      },
      { status: 409 },
    );
  }

  const esito = await ctx.db
    .prepare("DELETE FROM membri WHERE organizzazione_id = ? AND email = ?")
    .bind(ctx.organizzazione, email)
    .run();
  if (!esito.meta.changes) return Response.json({ errore: "membro non trovato" }, { status: 404 });
  return elencaMembri(ctx);
}
