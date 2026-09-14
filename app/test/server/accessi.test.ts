// I livelli di accesso, provati contro un D1 vero dentro il runtime di Cloudflare.
//
// La suite risponde a due domande, e la seconda vale piu' della prima.
//
// La prima e' che chi amministra un'organizzazione possa cambiarne i membri e nessun altro possa
// farlo. E' la disciplina ordinaria di ADR-024, cioe' la coppia di prove sul permesso e sul
// negato per ogni rotta, con il negato per primo perche' una prova che verifica solo il permesso
// passa anche su un'applicazione che non controlla niente.
//
// La seconda e' il perimetro del livello di piattaforma, che ADR-029 definisce per sottrazione:
// un superamministratore crea le organizzazioni e ne nomina gli amministratori, e non vede gli
// immobili di nessuna. E' la prova piu' importante di questo file, perche' e' la sola che
// fallirebbe se qualcuno, un giorno, aggiungesse al controllo di appartenenza una scorciatoia del
// tipo "oppure e' superamministratore": una scorciatoia che sembrerebbe comoda, che nessuna altra
// prova noterebbe, e che trasformerebbe il fornitore in un lettore silenzioso dei dati dei suoi
// clienti.

import { env } from "cloudflare:test";
import { beforeEach, describe, expect, it } from "vitest";

import { chiama, nominaGestore, popolaDueOrganizzazioni } from "./chiamate";

const MEMBRI_A = "/api/organizzazioni/agenzia-a/membri";
const ORGANIZZAZIONI = "/api/piattaforma/organizzazioni";

beforeEach(popolaDueOrganizzazioni);

async function ruoloDi(organizzazione: string, email: string): Promise<string | null> {
  const riga = await env.DB.prepare("SELECT ruolo FROM membri WHERE organizzazione_id = ? AND email = ?")
    .bind(organizzazione, email)
    .first<{ ruolo: string }>();
  return riga ? riga.ruolo : null;
}

describe("chi puo' vedere e cambiare i membri di un'organizzazione", () => {
  it("un lettore non vede nemmeno l'elenco dei membri", async () => {
    const r = await chiama("GET", MEMBRI_A, "ospite@a.invalid");
    expect(r.status).toBe(403);
  });

  it("un membro vede l'elenco, perche' sapere con chi si condivide un archivio non e' un privilegio", async () => {
    const r = await chiama("GET", MEMBRI_A, "socio@a.invalid");
    expect(r.status).toBe(200);
    const { membri } = (await r.json()) as { membri: { email: string; ruolo: string }[] };
    expect(membri.map((m) => m.email).sort()).toEqual([
      "capo@a.invalid",
      "ospite@a.invalid",
      "socio@a.invalid",
    ]);
    // L'amministratore per primo: e' l'ordine dichiarato dalla rotta, e serve a chi guarda.
    expect(membri[0].ruolo).toBe("amministratore");
  });

  it("un estraneo non sa nemmeno che l'organizzazione esiste", async () => {
    const r = await chiama("GET", MEMBRI_A, "capo@b.invalid");
    expect(r.status).toBe(404);
  });

  it("un membro non puo' aggiungere nessuno", async () => {
    const r = await chiama("PUT", MEMBRI_A, "socio@a.invalid", {
      email: "nuovo@a.invalid",
      ruolo: "membro",
    });
    expect(r.status).toBe(403);
    expect(await ruoloDi("agenzia-a", "nuovo@a.invalid")).toBeNull();
  });

  it("un amministratore aggiunge un membro, e l'indirizzo viene normalizzato", async () => {
    // La normalizzazione non e' cosmetica: l'appartenenza e' per posta elettronica, e Access
    // consegna l'indirizzo in minuscolo. Una riga salvata con la maiuscola produce una persona
    // che entra, e' identificata, e non appartiene a niente, mentre nel pannello la sua riga c'e'.
    const r = await chiama("PUT", MEMBRI_A, "capo@a.invalid", {
      email: "  Nuovo@A.Invalid  ",
      ruolo: "membro",
    });
    expect(r.status).toBe(200);
    expect(await ruoloDi("agenzia-a", "nuovo@a.invalid")).toBe("membro");
  });

  it("cambiare il ruolo di chi c'e' gia' non crea una seconda riga", async () => {
    await chiama("PUT", MEMBRI_A, "capo@a.invalid", { email: "socio@a.invalid", ruolo: "lettore" });
    const quante = await env.DB.prepare(
      "SELECT COUNT(*) AS quanti FROM membri WHERE organizzazione_id = ? AND email = ?",
    )
      .bind("agenzia-a", "socio@a.invalid")
      .first<{ quanti: number }>();
    expect(quante?.quanti).toBe(1);
    expect(await ruoloDi("agenzia-a", "socio@a.invalid")).toBe("lettore");
  });

  it("rifiuta un ruolo che non esiste invece di scriverlo", async () => {
    const r = await chiama("PUT", MEMBRI_A, "capo@a.invalid", {
      email: "nuovo@a.invalid",
      ruolo: "padrone",
    });
    expect(r.status).toBe(422);
    const { errori } = (await r.json()) as { errori: string[] };
    expect(errori.some((e) => e.startsWith("ruolo:"))).toBe(true);
  });

  it("rifiuta un indirizzo che non e' un indirizzo", async () => {
    const r = await chiama("PUT", MEMBRI_A, "capo@a.invalid", { email: "senza chiocciola", ruolo: "membro" });
    expect(r.status).toBe(422);
  });

  it("un amministratore di un'altra organizzazione non tocca questa", async () => {
    const r = await chiama("PUT", MEMBRI_A, "capo@b.invalid", {
      email: "intruso@b.invalid",
      ruolo: "amministratore",
    });
    expect(r.status).toBe(404);
    expect(await ruoloDi("agenzia-a", "intruso@b.invalid")).toBeNull();
  });
});

describe("l'organizzazione non resta senza amministratori", () => {
  it("l'ultimo amministratore non si puo' retrocedere", async () => {
    // Il caso concreto da cui nasce: l'unico amministratore si retrocede a membro per vedere come
    // si presenta l'applicazione con meno permessi, e poi non puo' piu' rimettersi amministratore,
    // perche' per farlo servirebbe il ruolo che si e' appena tolto.
    const r = await chiama("PUT", MEMBRI_A, "capo@a.invalid", {
      email: "capo@a.invalid",
      ruolo: "membro",
    });
    expect(r.status).toBe(409);
    expect(await ruoloDi("agenzia-a", "capo@a.invalid")).toBe("amministratore");
  });

  it("l'ultimo amministratore non si puo' revocare", async () => {
    const r = await chiama("DELETE", `${MEMBRI_A}/capo%40a.invalid`, "capo@a.invalid");
    expect(r.status).toBe(409);
    expect(await ruoloDi("agenzia-a", "capo@a.invalid")).toBe("amministratore");
  });

  it("con due amministratori il primo puo' andarsene", async () => {
    await chiama("PUT", MEMBRI_A, "capo@a.invalid", {
      email: "socio@a.invalid",
      ruolo: "amministratore",
    });
    const r = await chiama("DELETE", `${MEMBRI_A}/capo%40a.invalid`, "capo@a.invalid");
    expect(r.status).toBe(200);
    expect(await ruoloDi("agenzia-a", "capo@a.invalid")).toBeNull();
    expect(await ruoloDi("agenzia-a", "socio@a.invalid")).toBe("amministratore");
  });

  it("revocare un membro che non c'e' non e' un successo silenzioso", async () => {
    const r = await chiama("DELETE", `${MEMBRI_A}/nessuno%40a.invalid`, "capo@a.invalid");
    expect(r.status).toBe(404);
  });

  it("revocare un lettore non tocca l'invariante", async () => {
    const r = await chiama("DELETE", `${MEMBRI_A}/ospite%40a.invalid`, "capo@a.invalid");
    expect(r.status).toBe(200);
    expect(await ruoloDi("agenzia-a", "ospite@a.invalid")).toBeNull();
  });
});

describe("il livello di piattaforma, e cio' che non da'", () => {
  it("chi non ha alcun livello non vede il registro delle organizzazioni", async () => {
    const r = await chiama("GET", ORGANIZZAZIONI, "capo@a.invalid");
    expect(r.status).toBe(403);
  });

  it("senza identita' non si arriva nemmeno al controllo del livello", async () => {
    const r = await chiama("GET", ORGANIZZAZIONI, null);
    expect(r.status).toBe(401);
  });

  it("il supporto legge il registro, con quanti membri ha ciascuna", async () => {
    await nominaGestore("aiuto@piattaforma.invalid", "supporto");
    const r = await chiama("GET", ORGANIZZAZIONI, "aiuto@piattaforma.invalid");
    expect(r.status).toBe(200);
    const { organizzazioni } = (await r.json()) as {
      organizzazioni: { id: string; membri: number; amministratori: number }[];
    };
    expect(organizzazioni.map((o) => o.id)).toEqual(["agenzia-a", "agenzia-b"]);
    expect(organizzazioni[0].membri).toBe(3);
    expect(organizzazioni[0].amministratori).toBe(1);
  });

  it("il supporto non crea niente", async () => {
    await nominaGestore("aiuto@piattaforma.invalid", "supporto");
    const r = await chiama("POST", ORGANIZZAZIONI, "aiuto@piattaforma.invalid", {
      id: "agenzia-c",
      nome: "Agenzia C",
      amministratore: "capo@c.invalid",
    });
    expect(r.status).toBe(403);
  });

  it("il superamministratore crea l'organizzazione e il suo primo amministratore insieme", async () => {
    // Le due scritture stanno in un lotto: se la seconda fallisse dopo la prima resterebbe
    // un'organizzazione che nessuno puo' amministrare, e ripararla richiederebbe di nuovo una
    // scrittura a mano nel database, cioe' esattamente cio' che queste rotte tolgono di mezzo.
    await nominaGestore("io@piattaforma.invalid", "superamministratore");
    const r = await chiama("POST", ORGANIZZAZIONI, "io@piattaforma.invalid", {
      id: "agenzia-c",
      nome: "Agenzia C",
      amministratore: "Capo@C.Invalid",
    });
    expect(r.status).toBe(200);
    expect(await ruoloDi("agenzia-c", "capo@c.invalid")).toBe("amministratore");
  });

  it("non si creano due organizzazioni con lo stesso identificativo", async () => {
    await nominaGestore("io@piattaforma.invalid", "superamministratore");
    const r = await chiama("POST", ORGANIZZAZIONI, "io@piattaforma.invalid", {
      id: "agenzia-a",
      nome: "Un'altra Agenzia A",
      amministratore: "capo@c.invalid",
    });
    expect(r.status).toBe(409);
  });

  it("un'organizzazione non nasce senza amministratore", async () => {
    await nominaGestore("io@piattaforma.invalid", "superamministratore");
    const r = await chiama("POST", ORGANIZZAZIONI, "io@piattaforma.invalid", {
      id: "agenzia-c",
      nome: "Agenzia C",
    });
    expect(r.status).toBe(422);
    const { errori } = (await r.json()) as { errori: string[] };
    expect(errori.some((e) => e.startsWith("amministratore:"))).toBe(true);
  });

  it("rifiuta un identificativo che dovrebbe essere codificato per stare in un indirizzo", async () => {
    await nominaGestore("io@piattaforma.invalid", "superamministratore");
    const r = await chiama("POST", ORGANIZZAZIONI, "io@piattaforma.invalid", {
      id: "agenzia c/mc",
      nome: "Agenzia C",
      amministratore: "capo@c.invalid",
    });
    expect(r.status).toBe(422);
  });

  it("rimuovere un'organizzazione porta via i suoi membri e i suoi immobili", async () => {
    await nominaGestore("io@piattaforma.invalid", "superamministratore");
    await env.DB.prepare(
      `INSERT INTO immobili (id, organizzazione_id, titolo, comune, indirizzo, prezzo, superficie_mq,
                             categoria, rendita_catastale, stato, ipotesi, creato_il, aggiornato_il)
       VALUES ('x1', 'agenzia-a', 't', '', '', 1, 1, 'A/2', 0, 'da valutare', '{}', 'ora', 'ora')`,
    ).run();

    const r = await chiama("DELETE", `${ORGANIZZAZIONI}/agenzia-a`, "io@piattaforma.invalid");
    expect(r.status).toBe(200);

    const membri = await env.DB.prepare(
      "SELECT COUNT(*) AS quanti FROM membri WHERE organizzazione_id = 'agenzia-a'",
    ).first<{ quanti: number }>();
    const immobili = await env.DB.prepare(
      "SELECT COUNT(*) AS quanti FROM immobili WHERE organizzazione_id = 'agenzia-a'",
    ).first<{ quanti: number }>();
    expect(membri?.quanti).toBe(0);
    expect(immobili?.quanti).toBe(0);
  });

  it("un superamministratore non vede gli immobili di un'organizzazione di cui non e' membro", async () => {
    // La prova che definisce ADR-029. Fallirebbe se qualcuno aggiungesse al controllo di
    // appartenenza una scorciatoia del tipo "oppure e' superamministratore": comoda, invisibile a
    // ogni altra prova, e sufficiente a trasformare il fornitore in un lettore silenzioso dei
    // dati dei suoi clienti.
    await nominaGestore("io@piattaforma.invalid", "superamministratore");
    const elenco = await chiama("GET", "/api/organizzazioni/agenzia-a/immobili", "io@piattaforma.invalid");
    expect(elenco.status).toBe(404);
    const membri = await chiama("GET", MEMBRI_A, "io@piattaforma.invalid");
    expect(membri.status).toBe(404);
  });

  it("per vedere i dati di un cliente deve entrarvi, e l'appartenenza resta scritta", async () => {
    // Il rovescio della prova precedente, ed e' cio' che rende onesta la promessa: la difesa non
    // e' impossibilita' ma tracciabilita'. Dirlo qui evita che qualcuno, fra sei mesi, prometta
    // a un cliente la cosa sbagliata.
    await nominaGestore("io@piattaforma.invalid", "superamministratore");
    await chiama("PUT", MEMBRI_A, "capo@a.invalid", {
      email: "io@piattaforma.invalid",
      ruolo: "lettore",
    });
    const elenco = await chiama("GET", "/api/organizzazioni/agenzia-a/immobili", "io@piattaforma.invalid");
    expect(elenco.status).toBe(200);
    expect(await ruoloDi("agenzia-a", "io@piattaforma.invalid")).toBe("lettore");
  });
});

describe("chi sono io", () => {
  it("riporta il livello di piattaforma quando c'e'", async () => {
    await nominaGestore("io@piattaforma.invalid", "superamministratore");
    const r = await chiama("GET", "/api/io", "io@piattaforma.invalid");
    const corpo = (await r.json()) as { livello: string | null; organizzazioni: unknown[] };
    expect(corpo.livello).toBe("superamministratore");
    // E non appartiene ad alcuna organizzazione: il livello non ne implica nessuna.
    expect(corpo.organizzazioni).toEqual([]);
  });

  it("riporta null per chi non ne ha, che e' il caso ordinario", async () => {
    const r = await chiama("GET", "/api/io", "capo@a.invalid");
    const corpo = (await r.json()) as { livello: string | null };
    expect(corpo.livello).toBeNull();
  });
});
