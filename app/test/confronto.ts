// Confronto profondo fra un esito atteso e uno calcolato, condiviso dalle suite dei vettori.
//
// Vive in un file a parte e non dentro una suite perche' i vettori sono due famiglie, quella
// del motore e quella della simulazione del rischio, e un confronto duplicato e' un
// confronto che prima o poi diverge: la copia che sbaglia diventa la copia che assolve.

/** Gli infiniti non esistono in JSON: il generatore li scrive come stringhe. */
export function normalizza(valore: unknown): unknown {
  if (valore === "Infinity") return Infinity;
  if (valore === "-Infinity") return -Infinity;
  return valore;
}

/**
 * Confronta due esiti scendendo in ogni ramo, e riporta il percorso di ogni scarto.
 *
 * Il percorso conta piu' del valore: su centinaia di casi e un centinaio di grandezze
 * ciascuno, un messaggio che dice soltanto "atteso 1234 trovato 1235" costringe a cercare a
 * mano quale voce sia. Riportare "conto.imposta" indica subito la funzione da guardare.
 */
export function confronta(
  atteso: unknown,
  trovato: unknown,
  percorso: string,
  scarti: string[],
  tolleranzaRelativa: number,
  tolleranzaAssoluta: number,
): void {
  const a = normalizza(atteso);

  if (typeof a === "number" && typeof trovato === "number") {
    if (Number.isNaN(a) || Number.isNaN(trovato)) {
      if (!(Number.isNaN(a) && Number.isNaN(trovato))) {
        scarti.push(`${percorso}: atteso ${a}, trovato ${trovato}`);
      }
      return;
    }
    if (!Number.isFinite(a) || !Number.isFinite(trovato)) {
      if (a !== trovato) scarti.push(`${percorso}: atteso ${a}, trovato ${trovato}`);
      return;
    }
    const scarto = Math.abs(a - trovato);
    const ammesso = Math.abs(a) > 1 ? Math.abs(a) * tolleranzaRelativa : tolleranzaAssoluta;
    if (scarto > ammesso) {
      scarti.push(`${percorso}: atteso ${a}, trovato ${trovato}, scarto ${scarto.toExponential(3)}`);
    }
    return;
  }

  if (a !== null && typeof a === "object") {
    if (trovato === null || typeof trovato !== "object") {
      scarti.push(`${percorso}: atteso un oggetto, trovato ${String(trovato)}`);
      return;
    }
    const chiavi = Object.keys(a as Record<string, unknown>);
    for (const chiave of chiavi) {
      confronta(
        (a as Record<string, unknown>)[chiave],
        (trovato as Record<string, unknown>)[chiave],
        percorso ? `${percorso}.${chiave}` : chiave,
        scarti,
        tolleranzaRelativa,
        tolleranzaAssoluta,
      );
    }
    // Una chiave in piu' da questo lato non e' un errore di calcolo, ma e' un segnale che
    // le due implementazioni non descrivono piu' la stessa cosa, quindi va detto.
    for (const chiave of Object.keys(trovato as Record<string, unknown>)) {
      if (!chiavi.includes(chiave)) {
        scarti.push(`${percorso}.${chiave}: presente in TypeScript e assente nei vettori`);
      }
    }
    return;
  }

  if (a !== trovato) {
    scarti.push(`${percorso}: atteso ${JSON.stringify(a)}, trovato ${JSON.stringify(trovato)}`);
  }
}
