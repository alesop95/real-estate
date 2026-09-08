// Verifica di un token firmato RS256, con le chiavi pubbliche passate da fuori.
//
// Serve a un caso solo, cioe' il token che Cloudflare Access mette in ogni richiesta che
// arriva all'applicazione, ma e' scritto senza sapere niente di Access: prende un token e
// un insieme di chiavi, e dice se il token e' valido, per chi, e fino a quando. La ragione
// di questa separazione e' che le chiavi vere si scaricano dal dominio dell'organizzazione,
// che in questa fase non esiste ancora: iniettandole si puo' verificare la funzione in
// locale, con una coppia di chiavi generata dal test, invece di rimandare la prova al
// giorno in cui l'account sara' aperto. Cio' che resta non verificabile e' soltanto il
// recupero delle chiavi vere, che e' una chiamata di rete e non una regola di sicurezza.
//
// Nessuna libreria: la verifica di una firma RS256 con WebCrypto e' una trentina di righe,
// e una dipendenza in piu' su un pezzo di sicurezza e' una superficie in piu' da sorvegliare.

/** Una chiave pubblica in formato JWK, come la pubblica un fornitore di identita'. */
export interface ChiaveJwk {
  kid: string;
  kty: string;
  alg?: string;
  use?: string;
  n: string;
  e: string;
}

export interface EsitoVerifica {
  valido: boolean;
  /** Presente solo se il token e' valido. */
  email?: string;
  /** Ragione del rifiuto, in forma leggibile, per il registro e non per l'utente. */
  motivo?: string;
}

interface Attese {
  /** Destinatario atteso, cioe' l'identificativo dell'applicazione in Access. */
  aud: string;
  /** Emittente atteso, cioe' il dominio dell'organizzazione. */
  iss: string;
  /** Momento di riferimento, iniettabile perche' un test non deve dipendere dall'orologio. */
  adesso?: number;
  /** Tolleranza sullo sfasamento degli orologi, in secondi. */
  scarto?: number;
}

function daBase64Url(testo: string): Uint8Array<ArrayBuffer> {
  const base64 = testo.replace(/-/g, "+").replace(/_/g, "/");
  const riempito = base64 + "=".repeat((4 - (base64.length % 4)) % 4);
  const binario = atob(riempito);
  // Il buffer si crea esplicitamente: dalla 5.7 TypeScript distingue un Uint8Array su
  // ArrayBuffer da uno su SharedArrayBuffer, e le funzioni di WebCrypto accettano solo il
  // primo. Senza questa forma il codice gira e non compila, che e' il peggiore dei due modi.
  const byte = new Uint8Array(new ArrayBuffer(binario.length));
  for (let i = 0; i < binario.length; i += 1) byte[i] = binario.charCodeAt(i);
  return byte;
}

function testoDaBase64Url(testo: string): string {
  return new TextDecoder().decode(daBase64Url(testo));
}

/**
 * Verifica firma, emittente, destinatario e scadenza, in quest'ordine.
 *
 * L'ordine non e' casuale: la firma per prima, perche' finche' non e' verificata il
 * contenuto del token e' testo che ha scritto chiunque, e ragionare su una scadenza o su un
 * indirizzo di posta non ancora autenticati e' il modo classico di farsi ingannare.
 */
export async function verificaToken(token: string, chiavi: readonly ChiaveJwk[], attese: Attese): Promise<EsitoVerifica> {
  const pezzi = token.split(".");
  if (pezzi.length !== 3) return { valido: false, motivo: "il token non ha tre parti" };
  const [intestazioneGrezza, caricoGrezzo, firmaGrezza] = pezzi;

  let intestazione: { alg?: string; kid?: string };
  let carico: { aud?: string | string[]; iss?: string; exp?: number; nbf?: number; email?: string };
  try {
    intestazione = JSON.parse(testoDaBase64Url(intestazioneGrezza));
    carico = JSON.parse(testoDaBase64Url(caricoGrezzo));
  } catch {
    return { valido: false, motivo: "intestazione o carico non sono JSON" };
  }

  if (intestazione.alg !== "RS256") {
    // Rifiutare un algoritmo diverso da quello atteso, e in particolare "none", e' la
    // prima difesa: un token che dichiara di non essere firmato non e' un token.
    return { valido: false, motivo: `algoritmo non ammesso: ${String(intestazione.alg)}` };
  }
  const chiave = chiavi.find((k) => k.kid === intestazione.kid);
  if (!chiave) return { valido: false, motivo: "nessuna chiave corrisponde al kid del token" };

  let chiavePubblica: CryptoKey;
  try {
    chiavePubblica = await crypto.subtle.importKey(
      "jwk",
      { kty: chiave.kty, n: chiave.n, e: chiave.e, alg: "RS256", ext: true },
      { name: "RSASSA-PKCS1-v1_5", hash: "SHA-256" },
      false,
      ["verify"],
    );
  } catch {
    return { valido: false, motivo: "chiave pubblica non importabile" };
  }

  const firmaValida = await crypto.subtle.verify(
    "RSASSA-PKCS1-v1_5",
    chiavePubblica,
    daBase64Url(firmaGrezza),
    new TextEncoder().encode(`${intestazioneGrezza}.${caricoGrezzo}`),
  );
  if (!firmaValida) return { valido: false, motivo: "firma non valida" };

  if (carico.iss !== attese.iss) return { valido: false, motivo: "emittente diverso da quello atteso" };

  const destinatari = Array.isArray(carico.aud) ? carico.aud : [carico.aud];
  if (!destinatari.includes(attese.aud)) {
    // Senza questo controllo un token valido emesso per un'altra applicazione della stessa
    // organizzazione aprirebbe anche questa, che e' esattamente il genere di falla che non
    // si vede finche' qualcuno non ha due applicazioni.
    return { valido: false, motivo: "destinatario diverso da quello atteso" };
  }

  const adesso = attese.adesso ?? Math.floor(Date.now() / 1000);
  const scarto = attese.scarto ?? 60;
  if (typeof carico.exp === "number" && adesso > carico.exp + scarto) {
    return { valido: false, motivo: "token scaduto" };
  }
  if (typeof carico.nbf === "number" && adesso + scarto < carico.nbf) {
    return { valido: false, motivo: "token non ancora valido" };
  }
  if (!carico.email) return { valido: false, motivo: "il token non porta un indirizzo di posta" };

  return { valido: true, email: carico.email.toLowerCase() };
}
