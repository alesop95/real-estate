// Chi sta chiamando: dal token di Access a un indirizzo di posta, oppure niente.
//
// L'applicazione non ha un proprio sistema di credenziali, per ADR-024: davanti a essa sta
// Cloudflare Access, che identifica la persona e aggiunge a ogni richiesta un token firmato.
// Qui si fa una cosa sola, cioe' trasformare quel token in un indirizzo verificato, e si
// rifiuta tutto il resto.
//
// Il punto delicato e' la modalita' di sviluppo. In locale Access non c'e', quindi serve un
// modo per dire "sono questa persona" senza un token vero, e quel modo, se restasse attivo
// in esercizio, sarebbe una porta aperta con l'insegna. La difesa e' che la modalita' non si
// deduce dall'assenza di configurazione ma si dichiara: il valore predefinito e' esercizio,
// e in esercizio l'intestazione di comodo non viene nemmeno letta.

import { verificaToken, type ChiaveJwk } from "./jwt";

export interface Ambiente {
  DB: D1Database;
  MODALITA: string;
  ACCESS_TEAM: string;
  ACCESS_AUD: string;
}

export interface Identita {
  email: string;
}

/** Come si recuperano le chiavi pubbliche dell'organizzazione. Iniettabile per i test. */
export type FonteChiavi = (team: string) => Promise<readonly ChiaveJwk[]>;

const INTESTAZIONE_TOKEN = "Cf-Access-Jwt-Assertion";
const INTESTAZIONE_SVILUPPO = "X-Utente-Sviluppo";

/**
 * Scarica le chiavi pubbliche dell'organizzazione Zero Trust.
 *
 * E' l'unico pezzo di questo modulo che non e' verificabile in locale, perche' e' una
 * chiamata di rete verso un dominio che esistera' solo quando l'account sara' aperto. Per
 * questo la funzione e' un parametro e non una chiamata diretta: la logica di verifica si
 * prova con chiavi generate dal test, e qui resta soltanto il recupero.
 */
export const chiaviDaAccess: FonteChiavi = async (team) => {
  const risposta = await fetch(`https://${team}.cloudflareaccess.com/cdn-cgi/access/certs`);
  if (!risposta.ok) throw new Error(`chiavi di Access non recuperabili: ${risposta.status}`);
  const documento = (await risposta.json()) as { keys?: ChiaveJwk[] };
  return documento.keys ?? [];
};

/**
 * L'identita' di chi chiama, o null se la richiesta non e' autenticata.
 *
 * Non solleva eccezioni e non decide che cosa fare del rifiuto: quella e' una scelta della
 * rotta, e tenerla fuori da qui rende questa funzione riusabile anche dove un anonimo e'
 * ammesso, per esempio su una pagina pubblica di sola lettura, che oggi non esiste ma non e'
 * esclusa.
 */
export async function identita(
  richiesta: Request,
  ambiente: Ambiente,
  fonteChiavi: FonteChiavi = chiaviDaAccess,
): Promise<Identita | null> {
  if (ambiente.MODALITA === "sviluppo") {
    const email = richiesta.headers.get(INTESTAZIONE_SVILUPPO);
    return email ? { email: email.toLowerCase() } : null;
  }

  const token = richiesta.headers.get(INTESTAZIONE_TOKEN);
  if (!token) return null;
  if (!ambiente.ACCESS_TEAM || !ambiente.ACCESS_AUD) {
    // Senza configurazione non si tenta di verificare e non si lascia passare: una
    // variabile dimenticata deve chiudere l'applicazione, non aprirla.
    return null;
  }

  let chiavi: readonly ChiaveJwk[];
  try {
    chiavi = await fonteChiavi(ambiente.ACCESS_TEAM);
  } catch {
    return null;
  }

  const esito = await verificaToken(token, chiavi, {
    aud: ambiente.ACCESS_AUD,
    iss: `https://${ambiente.ACCESS_TEAM}.cloudflareaccess.com`,
  });
  return esito.valido && esito.email ? { email: esito.email } : null;
}
