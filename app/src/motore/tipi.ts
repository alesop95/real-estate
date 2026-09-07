// Le forme di ingresso del motore di calcolo.
//
// Rispecchiano una per una le dataclass di src/immobiliare/calcoli.py, che resta
// l'implementazione di riferimento: stessi campi, stessi valori predefiniti, stessa
// semantica. La corrispondenza non e' estetica, e' la condizione perche' i vettori di
// riscontro generati da quel motore siano ricalcolabili qui senza tradurre nulla.

/** Regimi di tassazione del canone. Gli stessi nomi che usa il motore Python. */
export type Regime =
  | "cedolare_libero"
  | "cedolare_concordato"
  | "irpef_ordinario"
  | "irpef_concordato"
  | "breve_prima_unita"
  | "breve_altre_unita";

/** Dati dell'immobile e del prezzo trattato. */
export interface Immobile {
  prezzo: number;
  rendita_catastale: number;
  categoria: string;
  superficie_mq: number;
  comune: string;
  nuova_costruzione: boolean;
  /** Vero se si compra da impresa costruttrice con vendita soggetta a IVA. */
  venditore_impresa: boolean;
}

/** Posizione soggettiva di chi compra, che determina le agevolazioni. */
export interface Acquirente {
  prima_casa: boolean;
  /** Quota di acquisto, fra 0 e 1. In acquisto congiunto vale 0,5 per ciascuno. */
  quota: number;
  residenza_gia_nel_comune: boolean;
  eta: number;
  isee: number;
  reddito_imponibile_irpef: number;
  possiede_altra_prima_casa: boolean;
  /** Se chiedere al notaio la tassazione sul valore catastale invece che sul prezzo. */
  prezzo_valore: boolean;
}

/** Condizioni del mutuo ipotecario. */
export interface Finanziamento {
  importo: number;
  tasso_annuo: number;
  durata_anni: number;
  tipo: string;
  spread: number;
  istruttoria: number;
  perizia: number;
  polizza_annua: number;
  notaio_atto_mutuo: number;
}

/** Assunzioni sulla gestione dell'immobile quando viene messo a reddito. */
export interface Gestione {
  canone_mensile: number;
  regime: Regime;
  mesi_sfitto_annui: number;
  morosita: number;
  condominio_annuo: number;
  quota_condominio_a_carico_proprietario: number;
  manutenzione_su_valore: number;
  assicurazione_annua: number;
  aliquota_imu: number;
  gestione_su_canone: number;
  ricavi_lordi_brevi_annui: number;
  costi_variabili_brevi: number;
}

export interface ImposteAcquisto {
  imponibile: number;
  iva: number;
  registro: number;
  ipotecaria: number;
  catastale: number;
  regime: string;
  totale: number;
}

export interface CostoOperazione {
  prezzo: number;
  imposte: ImposteAcquisto;
  provvigione: number;
  notaioCompravendita: number;
  notaioMutuo: number;
  sostitutivaMutuo: number;
  istruttoria: number;
  perizia: number;
  altriCosti: number;
  mutuo: number;
  costiAccessori: number;
  /** Prezzo piu' tutti i costi: e' il denominatore corretto dei rendimenti. */
  costoTotale: number;
  /** Cassa che serve davvero al netto della parte finanziata dalla banca. */
  esborsoIniziale: number;
  incidenzaCosti: number;
}

export interface RataAmmortamento {
  numero: number;
  anno: number;
  quotaInteressi: number;
  quotaCapitale: number;
  rata: number;
  debitoResiduo: number;
}

export interface ContoEconomico {
  canonePotenziale: number;
  perditaSfitto: number;
  perditaMorosita: number;
  condominio: number;
  manutenzione: number;
  assicurazione: number;
  imu: number;
  gestione: number;
  imposta: number;
  /** Accantonamento annuo per la ristrutturazione di fine ciclo, per ADR-005. */
  ristrutturazione: number;
  canoneEffettivo: number;
  costiOperativi: number;
  /** Net operating income, prima delle imposte sul reddito e del mutuo. */
  noi: number;
  utileNetto: number;
}

export interface Metriche {
  rendimentoLordo: number;
  rendimentoNetto: number;
  capRate: number;
  cashOnCash: number;
  dscr: number;
  cashFlowAnnuo: number;
  paybackAnni: number;
}

export interface EffettoInflazione {
  inflazione: number;
  rendimentoNettoNominale: number;
  rendimentoNettoReale: number;
  /** Quanto sbaglia la sottrazione r meno i rispetto alla formula esatta. */
  erroreApprossimazione: number;
  erosioneRealeCanone: number;
  rivalutazioneRealeImmobile: number;
  tirNominale: number;
  tirReale: number;
  valoreFinaleNominale: number;
  valoreFinaleReale: number;
  debitoResiduoNominale: number;
  debitoResiduoReale: number;
  scontoInflazioneSulDebito: number;
  rataAnnuaRealeAFineOrizzonte: number;
  canonePersoPerMancataIndicizzazione: number;
}

export interface EsitoConfronto {
  patrimonioComprando: number;
  patrimonioAffittando: number;
  differenza: number;
  convieneComprare: boolean;
}
