// I ruoli e il loro ordine, che e' l'unica semantica che hanno.
//
// Sta fra le cose condivise dal 14 settembre 2026 perche' la domanda "questa persona puo'
// scrivere?" si fa da due parti e per due scopi diversi. Il Worker la fa per decidere, ed e'
// l'unica risposta che conta: quella e' la difesa. L'interfaccia la fa per non mostrare un
// pulsante che produrrebbe soltanto un rifiuto, ed e' cortesia, non sicurezza.
//
// La tentazione, in un caso cosi', e' scrivere nell'interfaccia una scorciatoia del tipo
// "abilita se il ruolo e' amministratore". Funziona, ed e' sbagliata nel modo peggiore:
// nasconde il pulsante anche a chi il ruolo ce l'ha piu' alto, oppure lo mostra a chi non
// ce l'ha, a seconda di come e' stata scritta, e in nessuno dei due casi qualcosa fallisce.
// Con la gerarchia in un posto solo, la domanda si fa con la stessa funzione dalle due parti
// e un ruolo nuovo si aggiunge qui e non in venti confronti sparsi.

export type Ruolo = "amministratore" | "membro" | "lettore";

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
