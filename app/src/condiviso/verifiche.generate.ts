// Generato da tools/genera-motore.py: non modificare a mano.
//
// Le voci vengono da src/immobiliare/verifiche.py, che resta la sola fonte di verita' e
// che alimenta anche il foglio Checklist del workbook. Modificare questo file significa
// creare un secondo catalogo: non produrrebbe un errore, produrrebbe due elenchi di
// verifiche legali diversi fra il foglio e l'applicazione, che e' il genere di divergenza
// che si scopre davanti a un notaio.

/** Gli stati che una verifica puo' assumere. */
export type StatoVerifica =
  | "da fare"
  | "in corso"
  | "fatto"
  | "non applicabile"
  | "n.a.";

export const STATI_VERIFICA = [
  "da fare", "in corso", "fatto", "non applicabile", "n.a."
] as const;

/** Le fasi nell'ordine in cui si incontrano, che non e' quello alfabetico. */
export const FASI_VERIFICA = [
  "Prima della proposta",
  "Nella proposta",
  "Mutuo",
  "Prima del rogito",
  "Nuova costruzione",
  "Se si affitta",
] as const;

export type FaseVerifica = (typeof FASI_VERIFICA)[number];

export interface Verifica {
  /** Chiave stabile, costruita dalla posizione nel catalogo: sopravvive a un cambio di testo. */
  id: string;
  fase: FaseVerifica;
  verifica: string;
  percheConta: string;
  fonte: string;
  chi: string;
  statoIniziale: StatoVerifica;
  note: string;
}

export const VERIFICHE: readonly Verifica[] = [
  {
    id: "v01",
    fase: "Prima della proposta",
    verifica: "Visura catastale aggiornata e planimetria depositata",
    percheConta: "L'atto è nullo se manca la dichiarazione di conformità fra planimetria e stato di fatto. Non ogni difformità però produce nullità: la Cassazione distingue le irregolarità significative dai difetti minori.",
    fonte: "Agenzia delle Entrate, servizi catastali",
    chi: "Acquirente o tecnico",
    statoIniziale: "da fare",
    note: "",
  },
  {
    id: "v02",
    fase: "Prima della proposta",
    verifica: "Conformità urbanistica ed edilizia",
    percheConta: "È la corrispondenza fra lo stato di fatto e tutti i titoli edilizi della storia del fabbricato. È cosa diversa dalla conformità catastale e va verificata separatamente: è la difformità che blocca davvero la vendita e il mutuo.",
    fonte: "Accesso agli atti in Comune, titoli edilizi",
    chi: "Tecnico di parte",
    statoIniziale: "da fare",
    note: "",
  },
  {
    id: "v03",
    fase: "Prima della proposta",
    verifica: "Stato legittimo e tolleranze costruttive",
    percheConta: "Il decreto Salva Casa ha ampliato le tolleranze dell'articolo 34-bis del DPR 380/2001 per le difformità realizzate prima del 24 maggio 2024, e ha dato valore probatorio alle dichiarazioni del tecnico. Sapere in quale regime ricade l'immobile cambia il costo della regolarizzazione.",
    fonte: "Relazione del tecnico, DL 69/2024 convertito in legge 105/2024",
    chi: "Tecnico di parte",
    statoIniziale: "da fare",
    note: "",
  },
  {
    id: "v04",
    fase: "Prima della proposta",
    verifica: "Visura ipotecaria ventennale",
    percheConta: "Rivela ipoteche, pignoramenti, sequestri, diritti di terzi, servitu' e trascrizioni pregiudizievoli. L'ipoteca del venditore va cancellata prima o contestualmente al rogito.",
    fonte: "Conservatoria dei registri immobiliari",
    chi: "Notaio o visurista",
    statoIniziale: "da fare",
    note: "",
  },
  {
    id: "v05",
    fase: "Prima della proposta",
    verifica: "Atto di provenienza e continuità delle trascrizioni",
    percheConta: "Dice come il venditore è diventato proprietario. Una provenienza per donazione è un rischio concreto per il mutuo, perché l'immobile è aggredibile dai legittimari lesi.",
    fonte: "Atto notarile di acquisto o successione",
    chi: "Notaio",
    statoIniziale: "da fare",
    note: "",
  },
  {
    id: "v06",
    fase: "Prima della proposta",
    verifica: "Quotazioni OMI della zona e comparabili reali",
    percheConta: "Ancora il prezzo a un riferimento verificabile invece che alla richiesta dell'agenzia. Le quotazioni OMI sono semestrali, gratuite e pubbliche.",
    fonte: "Osservatorio del mercato immobiliare, Agenzia delle Entrate",
    chi: "Acquirente",
    statoIniziale: "da fare",
    note: "",
  },
  {
    id: "v07",
    fase: "Prima della proposta",
    verifica: "Spese condominiali e liberatoria dell'amministratore",
    percheConta: "L'acquirente risponde in solido con il venditore delle spese dell'anno in corso e di quello precedente. Vanno letti anche i verbali delle ultime assemblee, per i lavori deliberati e non ancora pagati.",
    fonte: "Consuntivi, riparti, verbali, regolamento",
    chi: "Amministratore",
    statoIniziale: "da fare",
    note: "",
  },
  {
    id: "v08",
    fase: "Nella proposta",
    verifica: "Condizione sospensiva o risolutiva legata al mutuo",
    percheConta: "Senza clausola, se la banca non delibera si perde la caparra e si deve comunque la provvigione. Con la sospensiva il contratto non produce effetti finché la banca non eroga; con la risolutiva il contratto si scioglie se la condizione non si avvera entro il termine.",
    fonte: "Testo della proposta, articoli 1353 e seguenti del codice civile",
    chi: "Acquirente e legale",
    statoIniziale: "da fare",
    note: "",
  },
  {
    id: "v09",
    fase: "Nella proposta",
    verifica: "Provvigione dell'agenzia legata all'avveramento della condizione",
    percheConta: "La provvigione matura alla conclusione dell'affare. Se la condizione non si avvera e nulla è stato pattuito, l'agenzia può comunque pretenderla: va escluso espressamente per iscritto.",
    fonte: "Testo della proposta",
    chi: "Acquirente e legale",
    statoIniziale: "da fare",
    note: "",
  },
  {
    id: "v10",
    fase: "Nella proposta",
    verifica: "Termine per la stipula del definitivo",
    percheConta: "Senza un termine, l'obbligo di concludere resta indeterminato e diventa difficile far valere l'inadempimento della controparte.",
    fonte: "Testo della proposta",
    chi: "Acquirente e legale",
    statoIniziale: "da fare",
    note: "",
  },
  {
    id: "v11",
    fase: "Nella proposta",
    verifica: "Stato di fatto e di diritto e garanzia di libertà da gravami",
    percheConta: "Va scritto che l'immobile è trasferito libero da ipoteche, pesi, vincoli, pegni e da qualsivoglia gravame, e che il venditore garantisce la conformità urbanistica e catastale.",
    fonte: "Testo della proposta",
    chi: "Acquirente e legale",
    statoIniziale: "da fare",
    note: "",
  },
  {
    id: "v12",
    fase: "Nella proposta",
    verifica: "Natura delle somme versate, acconto o caparra confirmatoria",
    percheConta: "La caparra confirmatoria da' diritto al doppio in caso di inadempimento del venditore; l'acconto no. La differenza va scritta, non lasciata implicita.",
    fonte: "Articolo 1385 del codice civile",
    chi: "Acquirente e legale",
    statoIniziale: "da fare",
    note: "",
  },
  {
    id: "v13",
    fase: "Mutuo",
    verifica: "Farsi consegnare il PIES di ogni banca interpellata",
    percheConta: "Il Prospetto Informativo Europeo Standardizzato è il documento personalizzato che la banca deve consegnare gratuitamente prima che il cliente sia vincolato, ed è l'unico modo per confrontare offerte diverse sulla stessa base. Contiene anche una tabella di ammortamento esemplificativa.",
    fonte: "Banca d'Italia, guida al mutuo ipotecario",
    chi: "Acquirente",
    statoIniziale: "da fare",
    note: "",
  },
  {
    id: "v14",
    fase: "Mutuo",
    verifica: "Usare i sette giorni di riflessione sull'offerta vincolante",
    percheConta: "Ricevuta l'offerta vincolante il consumatore ha diritto ad almeno sette giorni di riflessione, durante i quali l'offerta resta ferma per la banca e può essere accettata in qualsiasi momento. Sono giorni per confrontare, non per aspettare.",
    fonte: "Banca d'Italia, guida al mutuo ipotecario",
    chi: "Acquirente",
    statoIniziale: "da fare",
    note: "",
  },
  {
    id: "v15",
    fase: "Mutuo",
    verifica: "Verificare che il tasso non sia usurario",
    percheConta: "Al momento della firma il tasso non può superare la soglia d'usura, determinata sul tasso effettivo globale medio pubblicato trimestralmente. È un controllo di un minuto che si fa una volta sola.",
    fonte: "Banca d'Italia, tassi effettivi globali medi",
    chi: "Acquirente",
    statoIniziale: "da fare",
    note: "",
  },
  {
    id: "v16",
    fase: "Mutuo",
    verifica: "Confrontare la polizza della banca con il mercato",
    percheConta: "La polizza incendio e scoppio è obbligatoria ma il cliente può presentarne una reperita altrove, purchè di protezione equivalente, e la banca deve accettarla. Se si accetta quella proposta dalla banca, il cliente ha diritto di sapere quanta provvigione la compagnia paga alla banca stessa.",
    fonte: "Banca d'Italia, guida al mutuo ipotecario",
    chi: "Acquirente",
    statoIniziale: "da fare",
    note: "",
  },
  {
    id: "v17",
    fase: "Mutuo",
    verifica: "Controllare la propria posizione in Centrale dei Rischi",
    percheConta: "L'accesso ai propri dati è gratuito e si fa online. Una segnalazione dimenticata o una pratica ancora aperta presso un mediatore creditizio pesa sulla delibera: l'incarico di mediazione si può revocare per iscritto, e con esso decade la richiesta in corso.",
    fonte: "Banca d'Italia, accesso alla Centrale dei Rischi",
    chi: "Acquirente",
    statoIniziale: "da fare",
    note: "",
  },
  {
    id: "v18",
    fase: "Mutuo",
    verifica: "Sapere che la portabilità è gratuita per legge",
    percheConta: "Trasferire il mutuo a un'altra banca, cioè la surroga, è per legge senza spese né penali, e non richiede il consenso della banca di partenza. In pratica se ne ottiene una nella vita del mutuo: le banche identificano il surrogatore seriale e negano la delibera, e le surroghe hanno spesso spread più alti proprio per questo.",
    fonte: "Banca d'Italia, guida al mutuo ipotecario",
    chi: "Acquirente",
    statoIniziale: "n.a.",
    note: "",
  },
  {
    id: "v19",
    fase: "Prima del rogito",
    verifica: "Attestato di prestazione energetica",
    percheConta: "È obbligatorio allegarlo all'atto e va indicato negli annunci. Determina anche la classe da cui partire per ogni valutazione di adeguamento futuro.",
    fonte: "APE in corso di validità",
    chi: "Venditore",
    statoIniziale: "da fare",
    note: "",
  },
  {
    id: "v20",
    fase: "Prima del rogito",
    verifica: "Dichiarazione di conformità o rispondenza degli impianti",
    percheConta: "Per gli impianti realizzati dopo il 2008 serve la dichiarazione di conformità ai sensi del DM 37/2008; per i più vecchi può bastare la dichiarazione di rispondenza rilasciata da un tecnico abilitato.",
    fonte: "Dichiarazione dell'installatore o del tecnico",
    chi: "Venditore",
    statoIniziale: "da fare",
    note: "",
  },
  {
    id: "v21",
    fase: "Prima del rogito",
    verifica: "Trascrizione del preliminare se i tempi sono lunghi",
    percheConta: "La trascrizione ai sensi dell'articolo 2645-bis protegge da ipoteche e pignoramenti iscritti dopo la firma e da' privilegio sul credito restitutorio. Ha un costo, e su tempi lunghi o su venditori a rischio lo vale.",
    fonte: "Preliminare in forma notarile",
    chi: "Notaio",
    statoIniziale: "da fare",
    note: "",
  },
  {
    id: "v22",
    fase: "Prima del rogito",
    verifica: "Verifica dei requisiti prima casa e delle dichiarazioni in atto",
    percheConta: "Residenza nel Comune o impegno a trasferirla entro diciotto mesi, assenza di altra abitazione nel Comune, assenza di altra prima casa agevolata in Italia salvo rivendita entro due anni. In comunione legale entrambi i coniugi devono intervenire in atto e rendere le dichiarazioni.",
    fonte: "Guida dell'Agenzia delle Entrate sulle agevolazioni prima casa",
    chi: "Notaio",
    statoIniziale: "da fare",
    note: "",
  },
  {
    id: "v23",
    fase: "Prima del rogito",
    verifica: "Opzione prezzo-valore richiesta espressamente",
    percheConta: "Va chiesta in atto e comporta la tassazione sul valore catastale, il blocco dell'accertamento di valore e la riduzione del trenta per cento dell'onorario notarile.",
    fonte: "Articolo 1 comma 497 legge 266/2005",
    chi: "Notaio",
    statoIniziale: "da fare",
    note: "",
  },
  {
    id: "v24",
    fase: "Nuova costruzione",
    verifica: "Fideiussione a garanzia degli acconti",
    percheConta: "Il decreto legislativo 122/2005 impone al costruttore di consegnare una fideiussione bancaria o assicurativa a garanzia di tutte le somme versate prima del trasferimento. La tutela non è rinunciabile e ogni patto contrario è nullo.",
    fonte: "Decreto legislativo 122/2005",
    chi: "Notaio",
    statoIniziale: "n.a.",
    note: "",
  },
  {
    id: "v25",
    fase: "Nuova costruzione",
    verifica: "Polizza indennitaria decennale postuma",
    percheConta: "Copre i danni materiali da rovina totale o parziale e da gravi difetti costruttivi per dieci anni dall'ultimazione. Va consegnata all'atto e gli estremi vanno indicati nel rogito.",
    fonte: "Decreto legislativo 122/2005, articolo 4",
    chi: "Notaio",
    statoIniziale: "n.a.",
    note: "",
  },
  {
    id: "v26",
    fase: "Nuova costruzione",
    verifica: "Permesso di costruire, agibilità e accatastamento",
    percheConta: "La banca non delibera prima dell'accatastamento definitivo. Vanno verificati il titolo edilizio, il collaudo, l'agibilita' e la corrispondenza fra progetto approvato e stato realizzato.",
    fonte: "Titoli edilizi e certificato di agibilità",
    chi: "Tecnico di parte",
    statoIniziale: "n.a.",
    note: "",
  },
  {
    id: "v27",
    fase: "Nuova costruzione",
    verifica: "Capitolato, extracapitolato e cronoprogramma",
    percheConta: "Distinguere cosa è incluso nel prezzo da cosa è extra evita la sorpresa più cara dell'acquisto sulla carta. Il cronoprogramma con le penali per il ritardo va scritto.",
    fonte: "Contratto di appalto e capitolato",
    chi: "Acquirente",
    statoIniziale: "n.a.",
    note: "",
  },
  {
    id: "v28",
    fase: "Se si affitta",
    verifica: "Codice identificativo nazionale e adempimenti della locazione breve",
    percheConta: "Dal 2026 il CIN va indicato in ogni annuncio e comunicazione. Servono inoltre la comunicazione alla questura degli alloggiati, i dispositivi di sicurezza obbligatori e il rispetto dei regolamenti comunali e condominiali.",
    fonte: "Ministero del turismo, banca dati strutture ricettive",
    chi: "Proprietario",
    statoIniziale: "n.a.",
    note: "",
  },
  {
    id: "v29",
    fase: "Se si affitta",
    verifica: "Accordo territoriale e attestazione, se canone concordato",
    percheConta: "Il canone concordato richiede l'attestazione di conformità rilasciata da un'associazione firmataria dell'accordo territoriale del Comune, senza la quale i benefici fiscali decadono.",
    fonte: "Accordo territoriale del Comune",
    chi: "Proprietario",
    statoIniziale: "n.a.",
    note: "",
  },
  {
    id: "v30",
    fase: "Se si affitta",
    verifica: "Verifica del regolamento condominiale",
    percheConta: "Un regolamento contrattuale può vietare la locazione turistica o l'uso diverso dall'abitazione. Va letto prima di costruire un piano su affitti brevi.",
    fonte: "Regolamento condominiale trascritto",
    chi: "Proprietario",
    statoIniziale: "n.a.",
    note: "",
  },
] as const;
