// L'ingresso del Worker: monta le rotte e serve l'applicazione.
//
// Il file e' volutamente corto e senza logica. Tutto cio' che decide qualcosa sta altrove:
// l'identita' in identita.ts, l'autorizzazione in autorizzazione.ts, il comportamento delle
// singole rotte in immobili.ts, membri.ts e piattaforma.ts. Qui c'e' soltanto la mappa, che e'
// l'unico posto dove si legge in una schermata che cosa espone l'applicazione e con quale
// requisito: un ruolo dentro un'organizzazione per le rotte che toccano i dati, un livello di
// piattaforma per quelle che amministrano il prodotto.

import { Hono } from "hono";

import { livelloDi, rotta, rottaPiattaforma, type Ruolo } from "./autorizzazione";
import { identita, type Ambiente } from "./identita";
import {
  aggiornaImmobile,
  creaImmobile,
  elencaImmobili,
  leggiImmobile,
  rimuoviImmobile,
} from "./immobili";
import { elencaMembri, rimuoviMembro, scriviMembro } from "./membri";
import { creaOrganizzazione, elencaOrganizzazioni, rimuoviOrganizzazione } from "./piattaforma";

const app = new Hono<{ Bindings: Ambiente }>();

/**
 * Chi sono io, a quali organizzazioni appartengo e che livello ho sulla piattaforma.
 *
 * E' l'unica rotta che non passa dal registro delle rotte autorizzate, e la ragione e' che non
 * puo': serve proprio a scoprire di quali organizzazioni si e' membri, quindi non esiste
 * un'organizzazione su cui verificare l'appartenenza. Non espone dati di nessuna organizzazione,
 * solo cio' che riguarda chi chiama, e per questo l'eccezione e' innocua.
 *
 * Il livello di piattaforma torna qui e non da una rotta propria per una ragione di sostanza:
 * l'interfaccia deve sapere se mostrare il pannello di amministrazione prima di poterlo chiedere,
 * e una rotta che rispondesse "non ti e' permesso" costringerebbe a interrogarla sempre e a
 * trattare il rifiuto come un esito ordinario, che e' il modo in cui un rifiuto smette di essere
 * notato. Torna null per la stragrande maggioranza di chi entra, ed e' il caso normale.
 */
app.get("/api/io", async (c) => {
  const chi = await identita(c.req.raw, c.env);
  if (!chi) return c.json({ errore: "non autenticato" }, 401);
  const esito = await c.env.DB.prepare(
    `SELECT o.id, o.nome, m.ruolo
       FROM membri m JOIN organizzazioni o ON o.id = m.organizzazione_id
      WHERE m.email = ?
      ORDER BY o.nome`,
  )
    .bind(chi.email)
    .all<{ id: string; nome: string; ruolo: Ruolo }>();
  return c.json({
    email: chi.email,
    organizzazioni: esito.results ?? [],
    livello: await livelloDi(c.env.DB, chi.email),
  });
});

const IMMOBILI = "/api/organizzazioni/:org/immobili";

rotta(app, "get", IMMOBILI, "lettore", (ctx) => elencaImmobili(ctx));

rotta(app, "get", `${IMMOBILI}/:id`, "lettore", (ctx, c) => leggiImmobile(ctx, c.req.param("id")));

rotta(app, "post", IMMOBILI, "membro", async (ctx, c) => {
  const corpo = await c.req.json().catch(() => null);
  return creaImmobile(ctx, corpo, crypto.randomUUID(), new Date().toISOString());
});

rotta(app, "put", `${IMMOBILI}/:id`, "membro", async (ctx, c) => {
  const corpo = await c.req.json().catch(() => null);
  return aggiornaImmobile(ctx, c.req.param("id"), corpo, new Date().toISOString());
});

rotta(app, "delete", `${IMMOBILI}/:id`, "amministratore", (ctx, c) => rimuoviImmobile(ctx, c.req.param("id")));

// Chi fa parte dell'organizzazione. L'elenco lo vede un membro, perche' sapere con chi si
// condivide un archivio non e' un privilegio; cambiarlo e' dell'amministratore.
const MEMBRI = "/api/organizzazioni/:org/membri";

rotta(app, "get", MEMBRI, "membro", (ctx) => elencaMembri(ctx));

rotta(app, "put", MEMBRI, "amministratore", async (ctx, c) => {
  const corpo = await c.req.json().catch(() => null);
  return scriviMembro(ctx, corpo, new Date().toISOString());
});

rotta(app, "delete", `${MEMBRI}/:email`, "amministratore", (ctx, c) =>
  rimuoviMembro(ctx, decodeURIComponent(c.req.param("email"))),
);

// L'amministrazione del prodotto. Per ADR-029 queste rotte non danno accesso ai dati di
// nessuna organizzazione: creano il contenitore e ne nominano l'amministratore.
const ORGANIZZAZIONI = "/api/piattaforma/organizzazioni";

rottaPiattaforma(app, "get", ORGANIZZAZIONI, "supporto", (ctx) => elencaOrganizzazioni(ctx));

rottaPiattaforma(app, "post", ORGANIZZAZIONI, "superamministratore", async (ctx, c) => {
  const corpo = await c.req.json().catch(() => null);
  return creaOrganizzazione(ctx, corpo, new Date().toISOString());
});

rottaPiattaforma(app, "delete", `${ORGANIZZAZIONI}/:id`, "superamministratore", (ctx, c) =>
  rimuoviOrganizzazione(ctx, c.req.param("id")),
);

app.all("/api/*", (c) => c.json({ errore: "rotta non trovata" }, 404));

/**
 * Tutto cio' che non e' l'interfaccia di programmazione e' l'applicazione.
 *
 * Serve perche' l'interfaccia e' una pagina sola con piu' indirizzi: /immobili/abc esiste
 * per chi naviga e per chi salva un collegamento, ma non esiste come file, quindi la
 * richiesta arriva fin qui e la risposta corretta e' la pagina, che poi legge l'indirizzo e
 * mostra la sezione giusta. La stessa cosa la farebbe l'impostazione "single-page-application"
 * delle risorse statiche, che pero' scatta prima del Worker e risponderebbe la pagina anche a
 * /api/qualcosa: il ripiego sta qui, dopo le rotte, cosi' una chiamata sbagliata
 * all'interfaccia di programmazione continua a ricevere un 404 in JSON e non venti kilobyte
 * di HTML che nessun programma sa leggere.
 *
 * La richiesta non si inoltra tale e quale: si chiede sempre la radice. Chiedere al legame
 * un percorso che non esiste otterrebbe il suo 404, cioe' esattamente il caso che si sta
 * cercando di evitare.
 */
app.all("*", async (c) => {
  if (!c.env.ASSETS) {
    return c.text(
      "L'interfaccia non e' costruita. In sviluppo si apre da Vite, con \"npm run sviluppo\"; " +
        "per provarla dentro il Worker serve prima \"npm run costruisci\".",
      503,
    );
  }
  const radice = new URL("/", c.req.url);
  return c.env.ASSETS.fetch(new Request(radice, { headers: c.req.raw.headers }));
});

export default app;
