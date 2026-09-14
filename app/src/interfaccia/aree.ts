// Le sei aree, dichiarate tutte e sei anche se ne esiste una.
//
// La scelta di elencare anche quelle non ancora scritte non e' una promessa all'utente: e' il
// modo in cui il percorso resta leggibile. I ventun fogli del workbook si traducono in queste
// sei, e chi arriva dall'uno all'altro deve poter riconoscere dove e' finito il foglio che
// usava. Un'area non ancora scritta lo dice apertamente, invece di non esistere e lasciare
// credere che il modello si sia ristretto.
//
// L'ordine e' quello del percorso di valutazione e non l'alfabetico, per la stessa ragione per
// cui l'indice del workbook raggruppa i fogli in fasi: si comincia dall'immobile e si finisce
// dalla decisione, e il portafoglio sta in fondo perche' e' il passo che si fa quando di
// immobili ce ne sono molti.

export interface Area {
  chiave: string;
  nome: string;
  /** Che cosa ci si fa, in una riga: e' quanto serve a scegliere dove andare. */
  descrizione: string;
  /** Quali fogli del workbook confluiscono qui, per chi arriva da quello. */
  fogli: string;
  disponibile: boolean;
}

export const AREE: readonly Area[] = [
  {
    chiave: "immobile",
    nome: "Immobile",
    descrizione: "I dati dell'immobile, il regime di acquisto e le verifiche da chiudere prima di firmare.",
    fogli: "Immobile, Checklist",
    disponibile: true,
  },
  {
    chiave: "costo",
    nome: "Costo dell'operazione",
    descrizione: "Imposte, provvigione, notaio e accessori: quanto serve davvero per comprare.",
    fogli: "Costo operazione, Dossier tecnico",
    disponibile: false,
  },
  {
    chiave: "finanziamento",
    nome: "Finanziamento",
    descrizione: "Mutuo, simulatore del tasso e piano di ammortamento fino a chiusura.",
    fogli: "Mutuo, Simulatore mutuo, Ammortamento",
    disponibile: false,
  },
  {
    chiave: "reddito",
    nome: "Messa a reddito",
    descrizione: "I quattro regimi di tassazione del canone a confronto, e il conto economico.",
    fogli: "Locazione, Regimi, Flusso di cassa",
    disponibile: false,
  },
  {
    chiave: "decisione",
    nome: "Decisione",
    descrizione: "Cruscotto, scenari, rischio su mille simulazioni e confronto con l'affitto.",
    fogli: "Cruscotto, Scenari, Rischio, Confronto affitto",
    disponibile: false,
  },
  {
    chiave: "portafoglio",
    nome: "Portafoglio",
    descrizione: "Il registro degli immobili in valutazione e la graduatoria per scarto sulla zona.",
    fogli: "Confronto immobili",
    disponibile: false,
  },
];
