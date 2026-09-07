// Generato da tools/genera-motore.py: non modificare a mano.
//
// I valori vengono da src/immobiliare/parametri.py, che resta la sola fonte di verita'.
// Toccare questo file significa creare una seconda verita' fiscale, e la divergenza fra le
// due non produce un errore: produce un numero plausibile e sbagliato su uno dei due lati.
// Revisione dei parametri: 2026-08-28. Anno d'imposta: 2026.

export const REVISIONE = "2026-08-28";
export const ANNO_IMPOSTA = 2026;

export const imposteTrasferimento = {
  registroPrimaCasa: 0.02 as number,
  registroOrdinario: 0.09 as number,
  registroMinimo: 1000.0 as number,
  ipotecariaDaPrivato: 50.0 as number,
  catastaleDaPrivato: 50.0 as number,
  ivaPrimaCasa: 0.04 as number,
  ivaOrdinaria: 0.1 as number,
  ivaLusso: 0.22 as number,
  registroFissoDaImpresa: 200.0 as number,
  ipotecariaDaImpresa: 200.0 as number,
  catastaleDaImpresa: 200.0 as number,
  rivalutazioneRendita: 1.05 as number,
  moltiplicatorePrimaCasa: 110 as number,
  moltiplicatoreOrdinario: 120 as number,
  scontoOnorarioNotaioPrezzoValore: 0.3 as number,
  categorieEsclusePrimaCasa: ["A/1", "A/8", "A/9"] as readonly string[],
} as const;

export const costi = {
  provvigioneAgenziaTipica: 0.03 as number,
  ivaSuProvvigione: 0.22 as number,
  notaioCompravenditaMin: 1500.0 as number,
  notaioCompravenditaMax: 2500.0 as number,
  visureERelazionePreliminare: 300.0 as number,
  periziaTecnicoDiParte: 500.0 as number,
  allacciUtenze: 1500.0 as number,
  accatastamento: 800.0 as number,
  manutenzioneOrdinariaSuValore: 0.01 as number,
  condominioAnnuoTipico: 1200.0 as number,
  assicurazioneFabbricatoAnnua: 200.0 as number,
  sfittoSuCanone: 0.08 as number,
  morositaSuCanone: 0.03 as number,
  gestionePropertyManagerSuCanone: 0.1 as number,
  gestioneAffittoBreveSuRicavi: 0.2 as number,
  costiVariabiliAffittoBreveSuRicavi: 0.15 as number,
  ristrutturazioneSuValore: 0.3333333333333333 as number,
  anniFraRistrutturazioni: 40 as number,
} as const;

export const mutuo = {
  impostaSostitutivaPrimaCasa: 0.0025 as number,
  impostaSostitutivaOrdinaria: 0.02 as number,
  istruttoriaMin: 0.0 as number,
  istruttoriaMax: 800.0 as number,
  periziaMin: 200.0 as number,
  periziaMax: 400.0 as number,
  polizzaIncendioAnnuaMin: 100.0 as number,
  polizzaIncendioAnnuaMax: 250.0 as number,
  notaioAttoMutuoMin: 800.0 as number,
  notaioAttoMutuoMax: 1500.0 as number,
  ltvOrdinarioMax: 0.8 as number,
  ltvConFondoConsap: 1.0 as number,
  detrazioneInteressiAliquota: 0.19 as number,
  detrazioneInteressiMassimale: 4000.0 as number,
  mesiResidenzaPerDetrazione: 12 as number,
} as const;

export const locazione = {
  cedolareLibero: 0.21 as number,
  cedolareConcordato: 0.1 as number,
  cedolareBrevePrimaUnita: 0.21 as number,
  cedolareBreveAltreUnita: 0.26 as number,
  abbattimentoForfettarioOrdinario: 0.05 as number,
  abbattimentoForfettarioConcordato: 0.25 as number,
  registroAnnuo: 0.02 as number,
  registroMinimo: 67.0 as number,
  riduzioneBaseRegistroConcordato: 0.3 as number,
  bolloPerCopia: 16.0 as number,
  scontoCanoneConcordato: 0.15 as number,
  durataLibero: "4 + 4" as string,
  durataConcordato: "3 + 2" as string,
  durataTransitorioMesi: [1, 18] as readonly number[],
  durataStudentiMesi: [6, 36] as readonly number[],
  sogliaLocazioneBreveGiorni: 30 as number,
  maxUnitaLocazioneBreve: 2 as number,
  ritenutaIntermediari: 0.21 as number,
  cinObbligatorio: true as boolean,
  dispositiviSicurezzaObbligatori: true as boolean,
} as const;

export const irpef = {
  scaglioni: [[28000.0, 0.23], [50000.0, 0.33], [Infinity, 0.43]] as readonly (readonly number[])[],
  sogliaNeutralizzazioneBeneficio: 200000.0 as number,
  addizionaleRegionaleTipica: 0.0173 as number,
  addizionaleComunaleTipica: 0.008 as number,
} as const;

export const imu = {
  rivalutazioneRendita: 1.05 as number,
  moltiplicatoreGruppoA: 160 as number,
  moltiplicatoreC2C6C7: 160 as number,
  moltiplicatoreA10D5: 80 as number,
  moltiplicatoreC1: 55.0 as number,
  aliquotaBase: 0.0086 as number,
  aliquotaMassima: 0.0106 as number,
  aliquotaAbitazionePrincipaleLusso: 0.005 as number,
  detrazioneAbitazionePrincipale: 200.0 as number,
  riduzioneCanoneConcordato: 0.75 as number,
  riduzioneComodato: 0.5 as number,
  scadenzaAcconto: "16 giugno" as string,
  scadenzaSaldo: "16 dicembre" as string,
} as const;

export const plusvalenza = {
  anniImponibilitaOrdinaria: 5 as number,
  anniImponibilitaSuperbonus: 10 as number,
  impostaSostitutiva: 0.26 as number,
  esclusioneAbitazionePrincipale: true as boolean,
  esclusioneSuccessione: true as boolean,
} as const;

export const finanza = {
  inflazioneAttesa: 0.02 as number,
  rivalutazioneImmobileReale: 0.0 as number,
  rendimentoPortafoglioLordo: 0.06 as number,
  tassazioneRenditeFinanziarie: 0.26 as number,
  tassazioneTitoliDiStato: 0.125 as number,
  impostaBolloTitoli: 0.002 as number,
  tassoScontoReale: 0.03 as number,
  orizzonteAnalisiAnni: 30 as number,
} as const;
