// Le rotte, provate contro un D1 vero dentro il runtime di Cloudflare.
//
// La suite e' organizzata attorno a una sola domanda, che e' la ragione per cui esiste: due
// organizzazioni diverse non devono vedersi. Tutto il resto, cioe' che una lettura legga e
// che una scrittura scriva, e' contorno rispetto a quello.
//
// La disciplina di ADR-024 vuole che ogni rotta abbia la coppia di prove sul caso permesso e
// su quello negato. Qui il negato viene per primo in ogni gruppo, perche' un test che
// verifica solo il permesso passa anche su un'applicazione che non controlla niente.

import { env } from "cloudflare:test";
import { beforeEach, describe, expect, it } from "vitest";

import { registro, ruoloSufficiente } from "../../src/server/autorizzazione";

import { chiama, popolaDueOrganizzazioni } from "./chiamate";

const IMMOBILE = {
  titolo: "Monolocale in centro",
  comune: "Civitanova Marche",
  indirizzo: "via delle prove 1",
  prezzo: 120_000,
  superficie_mq: 55,
  categoria: "A/2",
  rendita_catastale: 450,
  stato: "da valutare",
  ipotesi: { orizzonte_anni: 25, gestione: { regime: "cedolare_libero" } },
};

beforeEach(popolaDueOrganizzazioni);

describe("identita' e appartenenza", () => {
  it("senza identita' non si entra da nessuna parte", async () => {
    const r = await chiama("GET", "/api/organizzazioni/agenzia-a/immobili", null);
    expect(r.status).toBe(401);
  });

  it("chi non e' membro riceve non trovato, non divieto", async () => {
    // La scelta e' deliberata: un divieto esplicito confermerebbe che quell'organizzazione
    // esiste, e su un prodotto multiproprieta' l'esistenza di un cliente e' gia' un'informazione.
    const r = await chiama("GET", "/api/organizzazioni/agenzia-b/immobili", "capo@a.invalid");
    expect(r.status).toBe(404);
  });

  it("la rotta su chi sono io elenca le sole appartenenze proprie", async () => {
    const r = await chiama("GET", "/api/io", "capo@a.invalid");
    expect(r.status).toBe(200);
    const corpo = (await r.json()) as { email: string; organizzazioni: { id: string; ruolo: string }[] };
    expect(corpo.email).toBe("capo@a.invalid");
    expect(corpo.organizzazioni).toEqual([{ id: "agenzia-a", nome: "Agenzia A", ruolo: "amministratore" }]);
  });

  it("un utente autenticato ma senza organizzazioni entra e non vede niente", async () => {
    const r = await chiama("GET", "/api/io", "estraneo@nessuno.invalid");
    expect(r.status).toBe(200);
    expect(((await r.json()) as { organizzazioni: unknown[] }).organizzazioni).toEqual([]);
  });
});

describe("isolamento fra organizzazioni", () => {
  it("un immobile di un'organizzazione non compare nell'elenco dell'altra", async () => {
    const creato = await chiama("POST", "/api/organizzazioni/agenzia-a/immobili", "socio@a.invalid", IMMOBILE);
    expect(creato.status).toBe(200);
    const id = ((await creato.json()) as { id: string }).id;

    const elencoA = await chiama("GET", "/api/organizzazioni/agenzia-a/immobili", "ospite@a.invalid");
    expect(((await elencoA.json()) as { immobili: unknown[] }).immobili).toHaveLength(1);

    const elencoB = await chiama("GET", "/api/organizzazioni/agenzia-b/immobili", "capo@b.invalid");
    expect(((await elencoB.json()) as { immobili: unknown[] }).immobili).toHaveLength(0);

    // E il tentativo diretto sull'identificativo, che e' il caso che conta davvero: chi ha
    // visto un identificativo altrove non deve poterlo leggere passando dalla propria
    // organizzazione. Qui la risposta e' non trovato, perche' la clausola sta nel WHERE.
    const diretto = await chiama("GET", `/api/organizzazioni/agenzia-b/immobili/${id}`, "capo@b.invalid");
    expect(diretto.status).toBe(404);
  });

  it("nemmeno la modifica e la cancellazione attraversano il confine", async () => {
    const creato = await chiama("POST", "/api/organizzazioni/agenzia-a/immobili", "socio@a.invalid", IMMOBILE);
    const id = ((await creato.json()) as { id: string }).id;

    const modifica = await chiama("PUT", `/api/organizzazioni/agenzia-b/immobili/${id}`, "capo@b.invalid", {
      ...IMMOBILE,
      titolo: "preso",
    });
    expect(modifica.status).toBe(404);

    const cancella = await chiama("DELETE", `/api/organizzazioni/agenzia-b/immobili/${id}`, "capo@b.invalid");
    expect(cancella.status).toBe(404);

    // E l'immobile e' rimasto intatto a casa sua.
    const rilettura = await chiama("GET", `/api/organizzazioni/agenzia-a/immobili/${id}`, "ospite@a.invalid");
    expect(((await rilettura.json()) as { titolo: string }).titolo).toBe(IMMOBILE.titolo);
  });
});

describe("ruoli", () => {
  it("un lettore legge e non scrive", async () => {
    const scrittura = await chiama("POST", "/api/organizzazioni/agenzia-a/immobili", "ospite@a.invalid", IMMOBILE);
    expect(scrittura.status).toBe(403);
    const lettura = await chiama("GET", "/api/organizzazioni/agenzia-a/immobili", "ospite@a.invalid");
    expect(lettura.status).toBe(200);
  });

  it("un membro scrive e non cancella", async () => {
    const creato = await chiama("POST", "/api/organizzazioni/agenzia-a/immobili", "socio@a.invalid", IMMOBILE);
    expect(creato.status).toBe(200);
    const id = ((await creato.json()) as { id: string }).id;

    const cancella = await chiama("DELETE", `/api/organizzazioni/agenzia-a/immobili/${id}`, "socio@a.invalid");
    expect(cancella.status).toBe(403);

    const cancellaDaCapo = await chiama("DELETE", `/api/organizzazioni/agenzia-a/immobili/${id}`, "capo@a.invalid");
    expect(cancellaDaCapo.status).toBe(204);
  });

  it("la gerarchia dei ruoli e' un ordine, non un elenco di uguaglianze", () => {
    // Il difetto tipico e' una rotta che confronta per uguaglianza e nega all'amministratore
    // cio' che concede al membro. La gerarchia sta in un posto solo proprio per impedirlo.
    expect(ruoloSufficiente("amministratore", "lettore")).toBe(true);
    expect(ruoloSufficiente("amministratore", "membro")).toBe(true);
    expect(ruoloSufficiente("membro", "amministratore")).toBe(false);
    expect(ruoloSufficiente("lettore", "membro")).toBe(false);
    expect(ruoloSufficiente("lettore", "lettore")).toBe(true);
  });
});

describe("forma dei dati", () => {
  it("un corpo malformato viene rifiutato con l'elenco completo dei problemi", async () => {
    const r = await chiama("POST", "/api/organizzazioni/agenzia-a/immobili", "socio@a.invalid", {
      titolo: "",
      prezzo: "centomila",
      superficie_mq: -5,
      categoria: "Z/9",
      stato: "in trattativa avanzata",
      ipotesi: [1, 2, 3],
    });
    expect(r.status).toBe(422);
    const errori = ((await r.json()) as { errori: string[] }).errori;
    // Tutti insieme, non uno per volta: un modulo che si fa correggere un campo alla volta
    // e' un modulo che si compila tre volte.
    expect(errori.length).toBeGreaterThanOrEqual(5);
    expect(errori.some((e) => e.startsWith("titolo:"))).toBe(true);
    expect(errori.some((e) => e.startsWith("prezzo:"))).toBe(true);
    expect(errori.some((e) => e.startsWith("categoria:"))).toBe(true);
    expect(errori.some((e) => e.startsWith("stato:"))).toBe(true);
    expect(errori.some((e) => e.startsWith("ipotesi:"))).toBe(true);
  });

  it("le ipotesi tornano indietro come documento e non come testo", async () => {
    const creato = await chiama("POST", "/api/organizzazioni/agenzia-a/immobili", "socio@a.invalid", IMMOBILE);
    const corpo = (await creato.json()) as { ipotesi: Record<string, unknown> };
    expect(corpo.ipotesi).toEqual(IMMOBILE.ipotesi);
  });

  it("l'aggiornamento cambia i campi e muove la data di modifica", async () => {
    const creato = await chiama("POST", "/api/organizzazioni/agenzia-a/immobili", "socio@a.invalid", IMMOBILE);
    const prima = (await creato.json()) as { id: string; aggiornato_il: string; creato_il: string };

    const dopo = await chiama("PUT", `/api/organizzazioni/agenzia-a/immobili/${prima.id}`, "socio@a.invalid", {
      ...IMMOBILE,
      prezzo: 111_000,
      stato: "trattativa",
    });
    const aggiornato = (await dopo.json()) as { prezzo: number; stato: string; creato_il: string };
    expect(aggiornato.prezzo).toBe(111_000);
    expect(aggiornato.stato).toBe("trattativa");
    // La data di creazione non si tocca: e' il genere di campo che un aggiornamento
    // distratto sovrascrive, e poi non si recupera.
    expect(aggiornato.creato_il).toBe(prima.creato_il);
  });
});

describe("integrita' del database", () => {
  it("un membro non puo' appartenere a un'organizzazione che non esiste", async () => {
    // La difesa e' nello schema e non nel codice: se un giorno una rotta scrivesse
    // un'appartenenza senza controllare, il database la rifiuterebbe comunque.
    await expect(
      env.DB.prepare("INSERT INTO membri (organizzazione_id, email, ruolo, aggiunto_il) VALUES (?, ?, ?, ?)")
        .bind("agenzia-inesistente", "tizio@x.invalid", "membro", "2026-09-07")
        .run(),
    ).rejects.toThrow();
  });

  it("un ruolo inventato viene rifiutato dallo schema", async () => {
    await expect(
      env.DB.prepare("INSERT INTO membri (organizzazione_id, email, ruolo, aggiunto_il) VALUES (?, ?, ?, ?)")
        .bind("agenzia-a", "tizio@x.invalid", "padrone", "2026-09-07")
        .run(),
    ).rejects.toThrow();
  });

  it("cancellare un'organizzazione porta via i suoi immobili e le sue appartenenze", async () => {
    await chiama("POST", "/api/organizzazioni/agenzia-a/immobili", "socio@a.invalid", IMMOBILE);
    await env.DB.prepare("DELETE FROM organizzazioni WHERE id = ?").bind("agenzia-a").run();
    const rimasti = await env.DB.prepare("SELECT COUNT(*) AS n FROM immobili").first<{ n: number }>();
    const membri = await env.DB.prepare("SELECT COUNT(*) AS n FROM membri WHERE organizzazione_id = ?").bind("agenzia-a").first<{ n: number }>();
    expect(rimasti?.n).toBe(0);
    expect(membri?.n).toBe(0);
  });
});

describe("il registro delle rotte", () => {
  it("ogni rotta dichiara il proprio requisito, e il requisito e' di una delle due famiglie", () => {
    // Il registro esiste per questo: non si puo' scrivere una rotta autorizzata senza passare da
    // `rotta` o da `rottaPiattaforma`, ed entrambe pretendono il requisito. Il test verifica che
    // nessuna rotta sia stata aggiunta altrove, cioe' che il numero e le forme siano quelle attese.
    expect(registro).toHaveLength(11);
    for (const r of registro) {
      if (r.requisito.tipo === "organizzazione") {
        expect(r.percorso.startsWith("/api/organizzazioni/:org/")).toBe(true);
        expect(["lettore", "membro", "amministratore"]).toContain(r.requisito.ruoloMinimo);
      } else {
        expect(r.percorso.startsWith("/api/piattaforma/")).toBe(true);
        expect(["supporto", "superamministratore"]).toContain(r.requisito.livelloMinimo);
      }
    }
  });

  it("nessuna scrittura sotto un'organizzazione si accontenta del lettore", () => {
    const scritture = registro.filter(
      (r) => r.metodo !== "get" && r.requisito.tipo === "organizzazione",
    );
    expect(scritture.length).toBeGreaterThan(0);
    expect(
      scritture.every((r) => r.requisito.tipo === "organizzazione" && r.requisito.ruoloMinimo !== "lettore"),
    ).toBe(true);
  });

  it("ogni cancellazione chiede il livello piu' alto della sua famiglia", () => {
    const cancellazioni = registro.filter((r) => r.metodo === "delete");
    expect(cancellazioni.length).toBeGreaterThan(0);
    for (const r of cancellazioni) {
      if (r.requisito.tipo === "organizzazione") expect(r.requisito.ruoloMinimo).toBe("amministratore");
      else expect(r.requisito.livelloMinimo).toBe("superamministratore");
    }
  });

  it("nessuna rotta di piattaforma vive sotto un'organizzazione, e viceversa", () => {
    // E' la separazione di ADR-029 vista dal registro: le due famiglie non si mescolano nemmeno
    // negli indirizzi, cosi' che leggere un percorso basti a sapere quale porta si sta aprendo.
    for (const r of registro) {
      const sottoOrganizzazione = r.percorso.startsWith("/api/organizzazioni/");
      expect(sottoOrganizzazione).toBe(r.requisito.tipo === "organizzazione");
    }
  });
});
