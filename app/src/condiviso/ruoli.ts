// I livelli di accesso e il loro ordine, che e' l'unica semantica che hanno.
//
// Ce ne sono due famiglie, e tenerle distinte e' la parte che conta.
//
// Il ruolo dice che cosa una persona puo' fare dentro un'organizzazione, ed e' la famiglia che
// governa i dati: gli immobili, le loro ipotesi, le loro verifiche. Il livello di piattaforma
// dice che cosa una persona puo' fare sul prodotto, cioe' sul registro delle organizzazioni e
// delle appartenenze, e non le da' alcun accesso ai dati che vivono dentro un'organizzazione.
// Per ADR-029 le due famiglie non si sommano e non si implicano: un superamministratore che
// voglia vedere gli immobili di un cliente deve aggiungersi fra i suoi membri, e quell'aggiunta
// lascia una riga che si puo' leggere.
//
// Le due gerarchie stanno fra le cose condivise per la stessa ragione della forma di un
// immobile, cioe' ADR-027: la domanda "questa persona puo'?" se la fanno il Worker per decidere
// e l'interfaccia per non mostrare un pulsante che produrrebbe soltanto un rifiuto. La
// tentazione, nell'interfaccia, e' scrivere una scorciatoia del tipo "abilita se il ruolo e'
// amministratore". Funziona, ed e' sbagliata nel modo peggiore: nasconde il gesto anche a chi ha
// un ruolo superiore, oppure lo mostra a chi non ce l'ha, e in nessuno dei due casi qualcosa
// fallisce.

// ---------------------------------------------------------------------------
// Dentro un'organizzazione
// ---------------------------------------------------------------------------

export const RUOLI = ["lettore", "membro", "amministratore"] as const;

export type Ruolo = (typeof RUOLI)[number];

const GERARCHIA: Record<Ruolo, number> = { lettore: 1, membro: 2, amministratore: 3 };

export function ruoloSufficiente(posseduto: Ruolo, richiesto: Ruolo): boolean {
  return GERARCHIA[posseduto] >= GERARCHIA[richiesto];
}

/** Come si scrive un ruolo quando lo si mostra a una persona. */
export const NOME_RUOLO: Record<Ruolo, string> = {
  amministratore: "amministratore",
  membro: "membro",
  lettore: "sola lettura",
};

/** Che cosa quel ruolo permette, in una riga, per chi deve sceglierlo per qualcun altro. */
export const COSA_PUO_FARE: Record<Ruolo, string> = {
  amministratore: "Tutto quello che fa un membro, piu' invitare e revocare colleghi ed eliminare immobili.",
  membro: "Legge e modifica gli immobili dell'organizzazione, e non tocca chi ne fa parte.",
  lettore: "Consulta e non modifica. E' il livello con cui si mostra una valutazione a un socio o a un consulente.",
};

// ---------------------------------------------------------------------------
// Sulla piattaforma
// ---------------------------------------------------------------------------

export const LIVELLI_PIATTAFORMA = ["supporto", "superamministratore"] as const;

export type LivelloPiattaforma = (typeof LIVELLI_PIATTAFORMA)[number];

const GERARCHIA_PIATTAFORMA: Record<LivelloPiattaforma, number> = {
  supporto: 1,
  superamministratore: 2,
};

export function livelloSufficiente(
  posseduto: LivelloPiattaforma | null,
  richiesto: LivelloPiattaforma,
): boolean {
  // Il null e' il caso ordinario e non un errore: la stragrande maggioranza di chi entra non ha
  // alcun livello di piattaforma, ed e' giusto cosi'. Trattarlo qui, invece di pretendere che
  // ogni chiamante lo controlli prima, e' cio' che rende questa funzione l'unica domanda da fare.
  if (posseduto === null) return false;
  return GERARCHIA_PIATTAFORMA[posseduto] >= GERARCHIA_PIATTAFORMA[richiesto];
}

export const NOME_LIVELLO: Record<LivelloPiattaforma, string> = {
  superamministratore: "superamministratore",
  supporto: "supporto",
};

export const COSA_PUO_FARE_SULLA_PIATTAFORMA: Record<LivelloPiattaforma, string> = {
  superamministratore:
    "Crea e rimuove organizzazioni e ne nomina il primo amministratore. Non vede gli immobili di nessuna organizzazione: per vederli deve entrarvi come membro, e l'appartenenza resta scritta.",
  supporto:
    "Legge quali organizzazioni esistono e chi ne fa parte, e non cambia niente. Nemmeno lui vede gli immobili.",
};
