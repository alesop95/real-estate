// La forma di un'organizzazione e di un'appartenenza, e le regole che le validano.
//
// Sta fra le cose condivise per la ragione di ADR-027: la stessa regola vale dalle due parti e si
// scrive una volta. Qui pero' c'e' un motivo in piu' e piu' stringente, che riguarda la posta
// elettronica.
//
// L'appartenenza e' per indirizzo di posta e non per identificativo utente, perche' l'identita'
// arriva da Access, che di una persona conosce l'indirizzo con cui ha superato l'accesso. Ne
// discende che il confronto fra l'indirizzo scritto in una riga di `membri` e quello che Access
// consegna deve riuscire carattere per carattere: un indirizzo salvato con un'iniziale maiuscola,
// o con uno spazio in coda incollato da una mail, produce una persona che entra, e' identificata,
// e non appartiene a niente. Non e' un errore che si vede: e' un utente che chiama dicendo "non
// vedo nulla" mentre nel pannello la sua riga c'e'. La normalizzazione sta quindi qui, dove la
// applicano sia chi scrive dal browser sia chi valida sul server, e non in uno dei due.

import { LIVELLI_PIATTAFORMA, RUOLI, type LivelloPiattaforma, type Ruolo } from "./ruoli";

/**
 * La forma di un indirizzo di posta, volutamente permissiva.
 *
 * Non si tenta la validazione esatta di un indirizzo, che e' un problema noto per essere senza
 * soluzione ragionevole: si escludono le forme che certamente non sono indirizzi, cioe' quelle
 * senza chiocciola, senza punto nel dominio o con spazi. Il controllo vero lo fa Access, che a
 * quell'indirizzo ci manda un codice: se non arriva, l'indirizzo era sbagliato.
 */
export const FORMA_EMAIL = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;

/**
 * La forma dell'identificativo di un'organizzazione.
 *
 * Compare negli indirizzi delle rotte, quindi si tiene a lettere minuscole, cifre e trattini: non
 * per pudore ma perche' un identificativo che richiede di essere codificato per stare in un
 * indirizzo e' un identificativo che prima o poi qualcuno concatenera' senza codificarlo.
 */
export const FORMA_ID_ORGANIZZAZIONE = /^[a-z0-9][a-z0-9-]{1,62}[a-z0-9]$/;

export interface Organizzazione {
  id: string;
  nome: string;
  creata_il: string;
}

export interface Membro {
  email: string;
  ruolo: Ruolo;
  aggiunto_il: string;
}

export interface Gestore {
  email: string;
  livello: LivelloPiattaforma;
  aggiunto_il: string;
}

/** Un'organizzazione come la vede chi amministra la piattaforma: con quanti membri ha. */
export interface OrganizzazioneConMembri extends Organizzazione {
  membri: number;
  amministratori: number;
}

/**
 * Porta un indirizzo alla forma in cui si confronta.
 *
 * Minuscole e spazi tolti, che sono le due differenze che nella pratica separano l'indirizzo
 * scritto in un pannello da quello che Access consegna.
 */
export function normalizzaEmail(grezzo: string): string {
  return grezzo.trim().toLowerCase();
}

/** Che cosa si manda per creare un'organizzazione: identificativo, nome e primo amministratore. */
export interface OrganizzazioneInviata {
  id: string;
  nome: string;
  amministratore: string;
}

/**
 * Valida la creazione di un'organizzazione.
 *
 * Il primo amministratore e' obbligatorio, e non e' una comodita': un'organizzazione creata senza
 * amministratore e' un'organizzazione che nessuno puo' amministrare, e per ripararla servirebbe
 * di nuovo una scrittura a mano nel database, cioe' esattamente cio' che questo insieme di rotte
 * esiste per togliere di mezzo. Nascere gia' amministrata e' una proprieta' della creazione, non
 * un passo successivo che qualcuno potrebbe dimenticare.
 */
export function validaOrganizzazione(corpo: unknown): {
  errori: string[];
  valore?: OrganizzazioneInviata;
} {
  const errori: string[] = [];
  if (corpo === null || typeof corpo !== "object") return { errori: ["il corpo non e' un oggetto"] };
  const d = corpo as Record<string, unknown>;

  const id = typeof d.id === "string" ? d.id.trim().toLowerCase() : "";
  if (!id) errori.push("id: manca");
  else if (!FORMA_ID_ORGANIZZAZIONE.test(id)) {
    errori.push("id: da tre a sessantaquattro caratteri fra lettere minuscole, cifre e trattini");
  }

  const nome = typeof d.nome === "string" ? d.nome.trim() : "";
  if (!nome) errori.push("nome: manca");
  else if (nome.length > 200) errori.push("nome: oltre 200 caratteri");

  const amministratore = typeof d.amministratore === "string" ? normalizzaEmail(d.amministratore) : "";
  if (!amministratore) errori.push("amministratore: manca");
  else if (!FORMA_EMAIL.test(amministratore)) errori.push("amministratore: non sembra un indirizzo di posta");

  if (errori.length) return { errori };
  return { errori: [], valore: { id, nome, amministratore } };
}

export interface AppartenenzaInviata {
  email: string;
  ruolo: Ruolo;
}

/** Valida l'aggiunta o il cambio di ruolo di un membro. */
export function validaAppartenenza(corpo: unknown): {
  errori: string[];
  valore?: AppartenenzaInviata;
} {
  const errori: string[] = [];
  if (corpo === null || typeof corpo !== "object") return { errori: ["il corpo non e' un oggetto"] };
  const d = corpo as Record<string, unknown>;

  const email = typeof d.email === "string" ? normalizzaEmail(d.email) : "";
  if (!email) errori.push("email: manca");
  else if (!FORMA_EMAIL.test(email)) errori.push("email: non sembra un indirizzo di posta");

  const ruolo = typeof d.ruolo === "string" ? d.ruolo : "";
  if (!ruolo) errori.push("ruolo: manca");
  else if (!(RUOLI as readonly string[]).includes(ruolo)) {
    errori.push(`ruolo: uno fra ${RUOLI.join(", ")}`);
  }

  if (errori.length) return { errori };
  return { errori: [], valore: { email, ruolo: ruolo as Ruolo } };
}

/** Valida l'attribuzione di un livello di piattaforma. */
export function validaGestore(corpo: unknown): {
  errori: string[];
  valore?: { email: string; livello: LivelloPiattaforma };
} {
  const errori: string[] = [];
  if (corpo === null || typeof corpo !== "object") return { errori: ["il corpo non e' un oggetto"] };
  const d = corpo as Record<string, unknown>;

  const email = typeof d.email === "string" ? normalizzaEmail(d.email) : "";
  if (!email) errori.push("email: manca");
  else if (!FORMA_EMAIL.test(email)) errori.push("email: non sembra un indirizzo di posta");

  const livello = typeof d.livello === "string" ? d.livello : "";
  if (!livello) errori.push("livello: manca");
  else if (!(LIVELLI_PIATTAFORMA as readonly string[]).includes(livello)) {
    errori.push(`livello: uno fra ${LIVELLI_PIATTAFORMA.join(", ")}`);
  }

  if (errori.length) return { errori };
  return { errori: [], valore: { email, livello: livello as LivelloPiattaforma } };
}
