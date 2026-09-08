// L'identita', provata per intero in locale con una coppia di chiavi generata qui.
//
// Il pezzo che sembrava non verificabile finche' l'account non esiste, cioe' la verifica del
// token di Access, lo diventa appena le chiavi pubbliche si passano da fuori invece di
// scaricarle. Il test genera una coppia RSA, firma dei token come li firmerebbe Access, e
// prova sia il caso buono sia i modi in cui un token puo' essere falso. Cio' che resta
// davvero non provabile e' soltanto la chiamata di rete che scarica le chiavi vere, che e'
// una riga e non contiene decisioni.

import { describe, expect, it } from "vitest";

import { identita, type Ambiente } from "../../src/server/identita";
import { verificaToken, type ChiaveJwk } from "../../src/server/jwt";

const TEAM = "prova";
const AUD = "aud-di-prova";
const EMITTENTE = `https://${TEAM}.cloudflareaccess.com`;

function base64url(dati: ArrayBuffer | string): string {
  const byte = typeof dati === "string" ? new TextEncoder().encode(dati) : new Uint8Array(dati);
  let binario = "";
  for (const b of byte) binario += String.fromCharCode(b);
  return btoa(binario).replace(/\+/g, "-").replace(/\//g, "_").replace(/=+$/, "");
}

async function coppiaDiChiavi() {
  const coppia = await crypto.subtle.generateKey(
    { name: "RSASSA-PKCS1-v1_5", modulusLength: 2048, publicExponent: new Uint8Array([1, 0, 1]), hash: "SHA-256" },
    true,
    ["sign", "verify"],
  );
  const pubblica = (await crypto.subtle.exportKey("jwk", coppia.publicKey)) as ChiaveJwk;
  pubblica.kid = "chiave-1";
  return { privata: coppia.privateKey, pubblica };
}

async function firma(privata: CryptoKey, carico: Record<string, unknown>, kid = "chiave-1"): Promise<string> {
  const intestazione = base64url(JSON.stringify({ alg: "RS256", typ: "JWT", kid }));
  const corpo = base64url(JSON.stringify(carico));
  const firmato = await crypto.subtle.sign(
    "RSASSA-PKCS1-v1_5",
    privata,
    new TextEncoder().encode(`${intestazione}.${corpo}`),
  );
  return `${intestazione}.${corpo}.${base64url(firmato)}`;
}

const ADESSO = 1_800_000_000;
const caricoValido = { iss: EMITTENTE, aud: AUD, email: "Tizio@Agenzia.invalid", exp: ADESSO + 3600, nbf: ADESSO - 10 };

describe("verifica del token di Access", () => {
  it("accetta un token firmato, per il destinatario giusto e non scaduto", async () => {
    const { privata, pubblica } = await coppiaDiChiavi();
    const token = await firma(privata, caricoValido);
    const esito = await verificaToken(token, [pubblica], { aud: AUD, iss: EMITTENTE, adesso: ADESSO });
    expect(esito.valido).toBe(true);
    // L'indirizzo si normalizza in minuscolo: due grafie della stessa persona non devono
    // diventare due membri diversi, e l'appartenenza si cerca per posta.
    expect(esito.email).toBe("tizio@agenzia.invalid");
  });

  it("rifiuta un token firmato con un'altra chiave", async () => {
    const buona = await coppiaDiChiavi();
    const cattiva = await coppiaDiChiavi();
    const token = await firma(cattiva.privata, caricoValido);
    const esito = await verificaToken(token, [buona.pubblica], { aud: AUD, iss: EMITTENTE, adesso: ADESSO });
    expect(esito.valido).toBe(false);
    expect(esito.motivo).toBe("firma non valida");
  });

  it("rifiuta un token che dichiara di non essere firmato", async () => {
    // E' l'attacco piu' vecchio e piu' banale: si mette alg a none e si spera che il
    // verificatore creda all'intestazione invece di imporre l'algoritmo atteso.
    const { pubblica } = await coppiaDiChiavi();
    const intestazione = base64url(JSON.stringify({ alg: "none", typ: "JWT", kid: "chiave-1" }));
    const corpo = base64url(JSON.stringify(caricoValido));
    const esito = await verificaToken(`${intestazione}.${corpo}.`, [pubblica], { aud: AUD, iss: EMITTENTE, adesso: ADESSO });
    expect(esito.valido).toBe(false);
    expect(esito.motivo).toContain("algoritmo non ammesso");
  });

  it("rifiuta un token valido emesso per un'altra applicazione", async () => {
    const { privata, pubblica } = await coppiaDiChiavi();
    const token = await firma(privata, { ...caricoValido, aud: "un-altra-applicazione" });
    const esito = await verificaToken(token, [pubblica], { aud: AUD, iss: EMITTENTE, adesso: ADESSO });
    expect(esito.valido).toBe(false);
    expect(esito.motivo).toBe("destinatario diverso da quello atteso");
  });

  it("rifiuta un token emesso da un'altra organizzazione", async () => {
    const { privata, pubblica } = await coppiaDiChiavi();
    const token = await firma(privata, { ...caricoValido, iss: "https://altra.cloudflareaccess.com" });
    const esito = await verificaToken(token, [pubblica], { aud: AUD, iss: EMITTENTE, adesso: ADESSO });
    expect(esito.valido).toBe(false);
    expect(esito.motivo).toBe("emittente diverso da quello atteso");
  });

  it("rifiuta un token scaduto, con la tolleranza dichiarata sugli orologi", async () => {
    const { privata, pubblica } = await coppiaDiChiavi();
    const token = await firma(privata, { ...caricoValido, exp: ADESSO - 120 });
    const scaduto = await verificaToken(token, [pubblica], { aud: AUD, iss: EMITTENTE, adesso: ADESSO });
    expect(scaduto.valido).toBe(false);
    expect(scaduto.motivo).toBe("token scaduto");

    // Dentro la tolleranza di sessanta secondi resta valido: gli orologi di due macchine
    // non coincidono mai, e senza tolleranza si producono rifiuti inspiegabili.
    const appena = await firma(privata, { ...caricoValido, exp: ADESSO - 30 });
    expect((await verificaToken(appena, [pubblica], { aud: AUD, iss: EMITTENTE, adesso: ADESSO })).valido).toBe(true);
  });

  it("rifiuta un token per cui non esiste la chiave dichiarata", async () => {
    const { privata, pubblica } = await coppiaDiChiavi();
    const token = await firma(privata, caricoValido, "chiave-sconosciuta");
    const esito = await verificaToken(token, [pubblica], { aud: AUD, iss: EMITTENTE, adesso: ADESSO });
    expect(esito.valido).toBe(false);
    expect(esito.motivo).toContain("nessuna chiave");
  });
});

describe("modalita' di esecuzione", () => {
  const ambiente = (sopra: Partial<Ambiente>): Ambiente =>
    ({ DB: null as unknown as D1Database, MODALITA: "esercizio", ACCESS_TEAM: TEAM, ACCESS_AUD: AUD, ...sopra });

  it("in esercizio l'intestazione di comodo non viene nemmeno guardata", async () => {
    // E' il controllo che conta di piu' di tutta questa suite: se la scorciatoia dello
    // sviluppo restasse attiva in esercizio, chiunque potrebbe dichiararsi chiunque.
    const richiesta = new Request("https://prova.invalid/api/io", {
      headers: { "X-Utente-Sviluppo": "intruso@nessuno.invalid" },
    });
    expect(await identita(richiesta, ambiente({}), async () => [])).toBeNull();
  });

  it("in sviluppo l'intestazione identifica, ed e' l'unica strada", async () => {
    const conIntestazione = new Request("https://prova.invalid/api/io", {
      headers: { "X-Utente-Sviluppo": "Socio@A.invalid" },
    });
    const chi = await identita(conIntestazione, ambiente({ MODALITA: "sviluppo" }), async () => []);
    expect(chi?.email).toBe("socio@a.invalid");

    const senza = new Request("https://prova.invalid/api/io");
    expect(await identita(senza, ambiente({ MODALITA: "sviluppo" }), async () => [])).toBeNull();
  });

  it("una configurazione incompleta chiude, non apre", async () => {
    const { privata, pubblica } = await coppiaDiChiavi();
    const token = await firma(privata, caricoValido);
    const richiesta = new Request("https://prova.invalid/api/io", {
      headers: { "Cf-Access-Jwt-Assertion": token },
    });
    // Senza il dominio dell'organizzazione o senza il destinatario atteso non si tenta
    // nemmeno la verifica: una variabile dimenticata deve spegnere l'applicazione.
    expect(await identita(richiesta, ambiente({ ACCESS_TEAM: "" }), async () => [pubblica])).toBeNull();
    expect(await identita(richiesta, ambiente({ ACCESS_AUD: "" }), async () => [pubblica])).toBeNull();
  });

  it("se le chiavi non si recuperano non si entra", async () => {
    const { privata } = await coppiaDiChiavi();
    const token = await firma(privata, caricoValido);
    const richiesta = new Request("https://prova.invalid/api/io", {
      headers: { "Cf-Access-Jwt-Assertion": token },
    });
    const rotta = async () => {
      throw new Error("rete non disponibile");
    };
    expect(await identita(richiesta, ambiente({}), rotta)).toBeNull();
  });
});
