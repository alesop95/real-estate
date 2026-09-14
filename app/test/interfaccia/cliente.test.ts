// Le prove del cliente: il cliente vero contro un server finto.
//
// La funzione di recupero e' un parametro proprio per questo. Sostituire il cliente con un
// finto nelle prove delle sezioni verificherebbe le sezioni ma lascerebbe il cliente senza
// prove, ed e' il cliente a contenere le due cose che si sbagliano: la codifica di cio' che
// finisce nell'indirizzo e la lettura di un rifiuto che non e' JSON.

import { describe, expect, it } from "vitest";

import { creaCliente, ErroreApi, type Recupero } from "../../src/interfaccia/cliente";

function registratore(risposta: (url: string, opzioni?: RequestInit) => Response) {
  const chiamate: { url: string; opzioni?: RequestInit }[] = [];
  const recupera: Recupero = async (url, opzioni) => {
    chiamate.push({ url, opzioni });
    return risposta(url, opzioni);
  };
  return { chiamate, recupera };
}

const ok = (corpo: unknown) => new Response(JSON.stringify(corpo), { status: 200 });

describe("gli indirizzi che il cliente costruisce", () => {
  it("chiede le appartenenze a /api/io", async () => {
    const { chiamate, recupera } = registratore(() => ok({ email: "a@b.it", organizzazioni: [] }));
    await creaCliente(recupera).io();
    expect(chiamate[0].url).toBe("/api/io");
  });

  it("codifica l'organizzazione e l'identificativo nell'indirizzo", async () => {
    // Un identificativo e' un UUID e non contiene barre, ma il nome di un'organizzazione puo'
    // essere qualunque cosa il giorno in cui lo si scegliera' leggibile invece che casuale.
    // Concatenare senza codificare funziona finche' non funziona, e allora scrive su un'altra
    // organizzazione: e' esattamente il confine che questo progetto difende.
    const { chiamate, recupera } = registratore(() => ok({}));
    await creaCliente(recupera).leggiImmobile("studio rossi/mc", "id con spazio");
    expect(chiamate[0].url).toBe(
      "/api/organizzazioni/studio%20rossi%2Fmc/immobili/id%20con%20spazio",
    );
  });

  it("manda il corpo come JSON con il tipo dichiarato", async () => {
    const { chiamate, recupera } = registratore(() => ok({ id: "x" }));
    await creaCliente(recupera).creaImmobile("o1", {
      titolo: "t",
      comune: "",
      indirizzo: "",
      prezzo: 1,
      superficie_mq: 0,
      categoria: "A/2",
      rendita_catastale: 0,
      stato: "da valutare",
      ipotesi: {},
    });
    const inviata = chiamate[0].opzioni;
    expect(inviata?.method).toBe("POST");
    expect((inviata?.headers as Record<string, string>)["Content-Type"]).toBe("application/json");
    expect(JSON.parse(String(inviata?.body)).titolo).toBe("t");
  });
});

describe("come il cliente legge un rifiuto", () => {
  it("porta fuori gli errori di forma uno per uno", async () => {
    const { recupera } = registratore(
      () => new Response(JSON.stringify({ errori: ["titolo: manca", "prezzo: manca"] }), { status: 422 }),
    );
    await expect(creaCliente(recupera).elencaImmobili("o1")).rejects.toMatchObject({
      stato: 422,
      errori: ["titolo: manca", "prezzo: manca"],
    });
  });

  it("usa il messaggio del server quando ce n'e' uno solo", async () => {
    const { recupera } = registratore(
      () => new Response(JSON.stringify({ errore: "organizzazione non trovata" }), { status: 404 }),
    );
    await expect(creaCliente(recupera).elencaImmobili("o1")).rejects.toThrow(
      "organizzazione non trovata",
    );
  });

  it("non si rompe su un rifiuto che non e' JSON", async () => {
    // E' il caso reale della sessione di Access scaduta: risponde una pagina HTML. Senza rete
    // di sicurezza il messaggio mostrato sarebbe un errore di sintassi JSON, cioe' il piu'
    // inutile possibile per chi deve capire che gli basta ricaricare.
    const { recupera } = registratore(
      () => new Response("<html>accedi di nuovo</html>", { status: 302 }),
    );
    const errore = await creaCliente(recupera)
      .io()
      .catch((e: unknown) => e);
    expect(errore).toBeInstanceOf(ErroreApi);
    expect((errore as ErroreApi).stato).toBe(302);
    expect((errore as ErroreApi).message).toContain("302");
  });

  it("la rimozione accetta una risposta senza corpo", async () => {
    const { recupera } = registratore(() => new Response(null, { status: 204 }));
    await expect(creaCliente(recupera).rimuoviImmobile("o1", "i1")).resolves.toBeUndefined();
  });
});
