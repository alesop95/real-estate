// Come si scrive un numero quando lo legge una persona.
//
// Sta in un modulo perche' la formattazione e' una decisione e non un dettaglio: il
// separatore delle migliaia, quante cifre si mostrano e quando si arrotonda cambiano che
// cosa il lettore crede di sapere. Mostrare un rendimento come 5,4% o come 5,42% non e' lo
// stesso: la seconda forma promette una precisione che il modello non ha, perche' dipende da
// un canone stimato e da un tasso che cambiera'.
//
// I formattatori si costruiscono una volta e non a ogni chiamata: costruirne uno dentro una
// funzione chiamata per ogni cella di una tabella e' uno dei modi piu' silenziosi di rendere
// lenta un'interfaccia che ricalcola mentre si digita.

const EURO_INTERO = new Intl.NumberFormat("it-IT", {
  style: "currency",
  currency: "EUR",
  maximumFractionDigits: 0,
});

const EURO_CENTESIMI = new Intl.NumberFormat("it-IT", {
  style: "currency",
  currency: "EUR",
  minimumFractionDigits: 2,
  maximumFractionDigits: 2,
});

const NUMERO = new Intl.NumberFormat("it-IT", { maximumFractionDigits: 0 });

const PERCENTUALE = new Intl.NumberFormat("it-IT", {
  style: "percent",
  minimumFractionDigits: 1,
  maximumFractionDigits: 1,
});

const DATA = new Intl.DateTimeFormat("it-IT", { dateStyle: "medium", timeStyle: "short" });

/** Un importo che si legge a colpo d'occhio: senza centesimi, che su un prezzo non dicono nulla. */
export function euro(valore: number): string {
  if (!Number.isFinite(valore)) return "-";
  return EURO_INTERO.format(valore);
}

/** Un importo dove i centesimi contano davvero, per esempio una rata. */
export function euroPreciso(valore: number): string {
  if (!Number.isFinite(valore)) return "-";
  return EURO_CENTESIMI.format(valore);
}

export function numero(valore: number): string {
  if (!Number.isFinite(valore)) return "-";
  return NUMERO.format(valore);
}

/** Una frazione mostrata come percentuale. Riceve 0,054 e scrive 5,4%. */
export function percentuale(frazione: number): string {
  if (!Number.isFinite(frazione)) return "-";
  return PERCENTUALE.format(frazione);
}

/**
 * Una data ISO come la scrive il server, mostrata nel fuso di chi guarda.
 *
 * Il server scrive sempre in tempo universale, che e' la sola scelta che non si rompe quando
 * due colleghi della stessa agenzia lavorano da due fusi diversi: la conversione si fa qui,
 * dove si sa chi sta leggendo, e non li' dove non si sa.
 */
export function quando(iso: string): string {
  const d = new Date(iso);
  return Number.isNaN(d.getTime()) ? "-" : DATA.format(d);
}
