// Come si chiama l'applicazione dentro il runtime di Cloudflare, e con quali dati si parte.
//
// Sta in un file proprio dal 14 settembre 2026, quando le prove delle rotte sono diventate due
// file: uno sugli immobili e uno sugli accessi. Gli aiutanti erano dieci righe e la tentazione di
// ricopiarli era forte, ma due impalcature che credono di partire dagli stessi dati e non lo fanno
// sono il modo piu' sicuro di far passare entrambe le suite mentre una delle due non verifica
// quello che dice di verificare.
//
// La popolazione iniziale e' deliberatamente minima e deliberatamente doppia: due organizzazioni
// con persone diverse, perche' con una sola ogni prova di isolamento passerebbe anche su
// un'applicazione che non filtra niente.

import { env } from "cloudflare:test";

import applicazione from "../../src/server/indice";

export const AMBIENTE = { ...env, MODALITA: "sviluppo" };

/** Una richiesta come la manderebbe il browser, con l'identita' della modalita' sviluppo. */
export function richiesta(
  metodo: string,
  percorso: string,
  email: string | null,
  corpo?: unknown,
): Request {
  const intestazioni: Record<string, string> = { "Content-Type": "application/json" };
  if (email) intestazioni["X-Utente-Sviluppo"] = email;
  return new Request(`https://prova.invalid${percorso}`, {
    method: metodo,
    headers: intestazioni,
    body: corpo === undefined ? undefined : JSON.stringify(corpo),
  });
}

export async function chiama(
  metodo: string,
  percorso: string,
  email: string | null,
  corpo?: unknown,
): Promise<Response> {
  return applicazione.fetch(richiesta(metodo, percorso, email, corpo), AMBIENTE);
}

/** Due organizzazioni con quattro persone: il minimo per poter dimostrare un isolamento. */
export async function popolaDueOrganizzazioni(): Promise<void> {
  await env.DB.batch([
    env.DB.prepare("INSERT INTO organizzazioni (id, nome, creata_il) VALUES (?, ?, ?)").bind("agenzia-a", "Agenzia A", "2026-09-07"),
    env.DB.prepare("INSERT INTO organizzazioni (id, nome, creata_il) VALUES (?, ?, ?)").bind("agenzia-b", "Agenzia B", "2026-09-07"),
    env.DB.prepare("INSERT INTO membri (organizzazione_id, email, ruolo, aggiunto_il) VALUES (?, ?, ?, ?)").bind("agenzia-a", "capo@a.invalid", "amministratore", "2026-09-07"),
    env.DB.prepare("INSERT INTO membri (organizzazione_id, email, ruolo, aggiunto_il) VALUES (?, ?, ?, ?)").bind("agenzia-a", "socio@a.invalid", "membro", "2026-09-07"),
    env.DB.prepare("INSERT INTO membri (organizzazione_id, email, ruolo, aggiunto_il) VALUES (?, ?, ?, ?)").bind("agenzia-a", "ospite@a.invalid", "lettore", "2026-09-07"),
    env.DB.prepare("INSERT INTO membri (organizzazione_id, email, ruolo, aggiunto_il) VALUES (?, ?, ?, ?)").bind("agenzia-b", "capo@b.invalid", "amministratore", "2026-09-07"),
  ]);
}

/** Attribuisce un livello di piattaforma a un indirizzo. */
export async function nominaGestore(email: string, livello: string): Promise<void> {
  await env.DB.prepare("INSERT INTO gestori (email, livello, aggiunto_il) VALUES (?, ?, ?)")
    .bind(email, livello, "2026-09-14")
    .run();
}
