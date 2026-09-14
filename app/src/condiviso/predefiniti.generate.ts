// Generato da tools/genera-motore.py: non modificare a mano.
//
// I valori vengono dalle dataclass di ingresso di src/immobiliare/calcoli.py, che resta la
// sola fonte di verita'. Sono i predefiniti con cui l'interfaccia apre una scheda vuota, e
// devono coincidere con quelli del motore di riferimento: se divergono, lo stesso caso
// lasciato intatto da una parte e dall'altra produce due numeri diversi, e nulla fallisce.

import type { Acquirente, Finanziamento, Gestione } from "../motore/tipi";

export const ACQUIRENTE_PREDEFINITO: Acquirente = {
  prima_casa: true,
  quota: 1.0,
  residenza_gia_nel_comune: false,
  eta: 35,
  isee: 0.0,
  reddito_imponibile_irpef: 30000.0,
  possiede_altra_prima_casa: false,
  prezzo_valore: true,
};

export const FINANZIAMENTO_PREDEFINITO: Finanziamento = {
  importo: 0.0,
  tasso_annuo: 0.032,
  durata_anni: 25,
  tipo: "fisso",
  spread: 0.0,
  istruttoria: 500.0,
  perizia: 300.0,
  polizza_annua: 180.0,
  notaio_atto_mutuo: 1000.0,
};

export const GESTIONE_PREDEFINITA: Gestione = {
  canone_mensile: 0.0,
  regime: "cedolare_libero",
  mesi_sfitto_annui: 1.0,
  morosita: 0.03,
  condominio_annuo: 1200.0,
  quota_condominio_a_carico_proprietario: 0.4,
  manutenzione_su_valore: 0.01,
  assicurazione_annua: 200.0,
  aliquota_imu: 0.0086,
  gestione_su_canone: 0.0,
  ricavi_lordi_brevi_annui: 0.0,
  costi_variabili_brevi: 0.15,
};
