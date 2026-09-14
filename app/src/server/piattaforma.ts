// Il registro delle organizzazioni, cioe' l'amministrazione del prodotto.
//
// Queste rotte sono l'unico posto in cui nasce un'organizzazione, e con essa un cliente. Per
// ADR-029 chi le usa non guadagna alcun accesso ai dati che vivono dentro le organizzazioni che
// crea: vede quante sono, come si chiamano, quanti membri hanno e chi sono, e nient'altro. Gli
// immobili di un cliente restano dietro la stessa porta di prima, cioe' l'appartenenza, e per
// attraversarla anche un superamministratore deve aggiungersi ai membri, lasciando una riga.
//
// Vale enunciare il limite di questa difesa senza addolcirlo: un superamministratore puo'
// aggiungersi da solo, quindi la protezione non e' impossibilita' ma tracciabilita'. La forma
// tecnica che renderebbe impossibile la lettura, cioe' cifrare i dati con una chiave che il
// fornitore non possiede, e' una scelta diversa e piu' costosa, che questo progetto non ha preso.
// Dichiararlo qui serve a che nessuno, fra sei mesi, prometta a un cliente la cosa sbagliata.

import {
  validaOrganizzazione,
  type OrganizzazioneConMembri,
} from "../condiviso/organizzazione";

import type { ContestoPiattaforma } from "./autorizzazione";

/** Tutte le organizzazioni, con quanti membri e quanti amministratori hanno. */
export async function elencaOrganizzazioni(ctx: ContestoPiattaforma): Promise<Response> {
  const esito = await ctx.db
    .prepare(
      `SELECT o.id, o.nome, o.creata_il,
              COUNT(m.email) AS membri,
              SUM(CASE WHEN m.ruolo = 'amministratore' THEN 1 ELSE 0 END) AS amministratori
         FROM organizzazioni o LEFT JOIN membri m ON m.organizzazione_id = o.id
        GROUP BY o.id, o.nome, o.creata_il
        ORDER BY o.nome`,
    )
    .all<OrganizzazioneConMembri>();
  return Response.json({ organizzazioni: esito.results ?? [] });
}

/**
 * Crea un'organizzazione e la sua prima appartenenza, insieme.
 *
 * Le due scritture stanno in un lotto e non in sequenza, e non e' un'ottimizzazione: se la
 * seconda fallisse dopo la prima resterebbe un'organizzazione che nessuno puo' amministrare, e
 * ripararla richiederebbe di nuovo una scrittura a mano nel database, cioe' esattamente cio' che
 * queste rotte esistono per togliere di mezzo. Nascere gia' amministrata e' una proprieta' della
 * creazione, non un secondo passo che qualcuno potrebbe non fare.
 */
export async function creaOrganizzazione(
  ctx: ContestoPiattaforma,
  corpo: unknown,
  adesso: string,
): Promise<Response> {
  const { errori, valore } = validaOrganizzazione(corpo);
  if (!valore) return Response.json({ errori }, { status: 422 });

  const esistente = await ctx.db
    .prepare("SELECT id FROM organizzazioni WHERE id = ?")
    .bind(valore.id)
    .first<{ id: string }>();
  if (esistente) {
    return Response.json({ errore: `esiste gia' un'organizzazione con identificativo ${valore.id}` }, { status: 409 });
  }

  await ctx.db.batch([
    ctx.db
      .prepare("INSERT INTO organizzazioni (id, nome, creata_il) VALUES (?, ?, ?)")
      .bind(valore.id, valore.nome, adesso),
    ctx.db
      .prepare(
        "INSERT INTO membri (organizzazione_id, email, ruolo, aggiunto_il) VALUES (?, ?, 'amministratore', ?)",
      )
      .bind(valore.id, valore.amministratore, adesso),
  ]);

  return elencaOrganizzazioni(ctx);
}

/**
 * Rimuove un'organizzazione, con tutto cio' che contiene.
 *
 * La cancellazione a cascata la applica lo schema, dichiarata sulle chiavi esterne di `membri` e
 * `immobili`: sta li' e non qui perche' una cancellazione parziale, cioe' un'organizzazione tolta
 * che lascia dietro le sue righe, produrrebbe dati senza proprietario che nessun filtro puo'
 * recuperare. E' l'operazione piu' distruttiva dell'applicazione, e per questo chiede il livello
 * piu' alto e non si puo' fare da nessun'altra parte.
 */
export async function rimuoviOrganizzazione(
  ctx: ContestoPiattaforma,
  id: string,
): Promise<Response> {
  const esito = await ctx.db.prepare("DELETE FROM organizzazioni WHERE id = ?").bind(id).run();
  if (!esito.meta.changes) {
    return Response.json({ errore: "organizzazione non trovata" }, { status: 404 });
  }
  return elencaOrganizzazioni(ctx);
}
