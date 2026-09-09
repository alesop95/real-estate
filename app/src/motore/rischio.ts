// Simulazione probabilistica degli esiti e analisi a tornado, porto di src/immobiliare/rischio.py.
//
// Valgono le tre regole della traduzione del motore, cioe' Python come implementazione di
// riferimento, lo stesso ordine delle operazioni e i parametri che vengono dal generatore.
// Qui se ne aggiunge una quarta, che riguarda solo questo file.
//
// Le estrazioni sono un ingresso e non un effetto collaterale. La simulazione non estrae
// nulla: riceve le estrazioni e restituisce l'esito, quindi e' una funzione pura e i vettori
// di riscontro generati dal motore Python sono ricalcolabili qui bit per bit. Se la
// simulazione estraesse per conto proprio non ci sarebbe modo di confrontarla, perche' il
// generatore pseudocasuale di Python e quello di JavaScript non producono la stessa
// sequenza e non c'e' motivo perche' dovrebbero. Chi ha bisogno di estrazioni per l'uso
// interattivo le prende da `estrazioniDaSeme`, che sta in fondo a questo file ed e'
// deliberatamente fuori dalla parte verificata contro Python.
//
// L'inversa della normale e' scritta qui invece di essere presa da una libreria, e la
// ragione e' la tolleranza: i vettori pretendono un miliardesimo relativo, e le
// approssimazioni tascabili di quella funzione si fermano a sette cifre. L'algoritmo e'
// quello di Wichura, cioe' AS 241, che e' anche quello che usa `statistics.NormalDist` di
// Python: le due implementazioni coincidono percio' per costruzione, e non per fortuna.

/** Un'estrazione grezza: il fattore comune, le quattro componenti proprie, l'evento. */
export interface Estrazione {
  comune: number;
  canone: number;
  sfitto: number;
  tasso: number;
  rivalutazione: number;
  /** Uniforme in zero-uno, estremi esclusi. */
  evento: number;
}

/** Quanto ci si sbaglia nel prevedere. Gli stessi campi di `Incertezze` in Python. */
export interface Incertezze {
  vol_canone: number;
  vol_sfitto: number;
  vol_tasso: number;
  vol_rivalutazione: number;
  prob_morosita_grave: number;
  mesi_persi_morosita: number;
  /** Intensita' del fattore comune, letta come correlazione. Vedi ADR-023. */
  correlazione: number;
}

/** Le grandezze deterministiche su cui la simulazione applica i propri scarti. */
export interface BaseSimulazione {
  canone_mensile: number;
  ricavo_effettivo: number;
  noi_annuo: number;
  costo_totale: number;
  esborso: number;
  prezzo: number;
  mesi_sfitto: number;
  morosita: number;
  /** Aliquota sul ricavo. Il foglio usa la cedolare sul canone libero anche in altri regimi. */
  aliquota_canone: number;
  tasso: number;
  durata_anni: number;
  mutuo_importo: number;
  rivalutazione: number;
  orizzonte_anni: number;
  costi_vendita: number;
  rendimento_portafoglio: number;
  rendimento_obiettivo: number;
  condominio_annuo: number;
  quota_condominio: number;
  manutenzione_su_valore: number;
  ristrutturazione_su_valore: number;
  ristrutturazione_anni: number;
}

/** Un singolo scenario, dalle estrazioni efficaci fino al montante. */
export interface EsitoScenario {
  zCanone: number;
  zSfitto: number;
  zTasso: number;
  zRivalutazione: number;
  zEvento: number;
  morositaGrave: boolean;
  canoneAnnuo: number;
  mesiSfitto: number;
  tasso: number;
  rivalutazione: number;
  ricavoEffettivo: number;
  noi: number;
  utileNetto: number;
  rataAnnua: number;
  cashFlow: number;
  valoreFinale: number;
  debitoResiduo: number;
  patrimonioFinale: number;
  montante: number;
  rendimentoNetto: number;
}

/** I tre numeri con cui si legge una distribuzione. */
export interface Distribuzione {
  peggiore5: number;
  mediana: number;
  migliore5: number;
}

/** Distribuzioni e probabilita', cioe' quello che il foglio Rischio mostra. */
export interface SintesiRischio {
  estrazioni: number;
  cashFlow: Distribuzione;
  utileNetto: Distribuzione;
  rendimentoNetto: Distribuzione;
  patrimonioFinale: Distribuzione;
  montante: Distribuzione;
  probCashNegativo: number;
  probSottoObiettivo: number;
  probPerditaCapitale: number;
  probBatteAlternativa: number;
}

/** Una variabile mossa da sola, e di quanto sposta il cash flow annuo. */
export interface VoceTornado {
  variabile: string;
  meno: number;
  piu: number;
  ampiezza: number;
}

export const SCOSTAMENTO_TORNADO = 0.1;

// ---------------------------------------------------------------------------
// Inversa della normale standard, algoritmo AS 241 di Wichura
// ---------------------------------------------------------------------------

/** Quantile della normale standard. Precisione dell'ordine di 1e-16 su tutto l'intervallo. */
export function inversaNormale(p: number): number {
  const q = p - 0.5;
  if (Math.abs(q) <= 0.425) {
    const r = 0.180625 - q * q;
    const num =
      (((((((2.5090809287301226727e3 * r + 3.3430575583588128105e4) * r + 6.7265770927008700853e4) * r +
        4.5921953931549871457e4) * r + 1.3731693765509461125e4) * r + 1.9715909503065514427e3) * r +
        1.3314166789178437745e2) * r + 3.387132872796366608e0) * q;
    const den =
      ((((((5.226495278852854561e3 * r + 2.8729085735721942674e4) * r + 3.930789580009271061e4) * r +
        2.1213794301586595867e4) * r + 5.3941960214247511077e3) * r + 6.871870074920579083e2) * r +
        4.2313330701600911252e1) * r + 1.0;
    return num / den;
  }
  let r = q <= 0 ? p : 1 - p;
  r = Math.sqrt(-Math.log(r));
  let x: number;
  if (r <= 5) {
    r = r - 1.6;
    const num =
      (((((((7.7454501427834140764e-4 * r + 0.0227238449892691845833) * r + 0.24178072517745061177) * r +
        1.27045825245236838258) * r + 3.64784832476320460504) * r + 5.7694972214606914055) * r +
        4.6303378461565452959) * r + 1.42343711074968357734);
    const den =
      (((((((1.05075007164441684324e-9 * r + 5.475938084995344946e-4) * r + 0.0151986665636164571966) * r +
        0.14810397642748007459) * r + 0.68976733498510000455) * r + 1.6763848301838038494) * r +
        2.05319162663775882187) * r + 1.0);
    x = num / den;
  } else {
    r = r - 5;
    const num =
      (((((((2.01033439929228813265e-7 * r + 2.71155556874348757815e-5) * r + 0.0012426609473880784386) * r +
        0.026532189526576123093) * r + 0.29656057182850489123) * r + 1.7848265399172913358) * r +
        5.4637849111641143699) * r + 6.6579046435011037772);
    const den =
      (((((((2.04426310338993978564e-15 * r + 1.4215117583164458887e-7) * r + 1.8463183175100546818e-5) * r +
        7.868691311456132591e-4) * r + 0.0148753612908506148525) * r + 0.13692988092273580531) * r +
        0.59983220655588793769) * r + 1.0);
    x = num / den;
  }
  return q < 0 ? -x : x;
}

// ---------------------------------------------------------------------------
// Pesi e statistica compatibile con Excel
// ---------------------------------------------------------------------------

/** I due pesi della mescolanza: radice della correlazione, radice del complemento. */
export function pesi(correlazione: number): [number, number] {
  const rho = Math.min(Math.max(correlazione, 0), 1);
  return [Math.sqrt(rho), Math.sqrt(1 - rho)];
}

/** Percentile con l'interpolazione lineare di PERCENTILE.INC di Excel. */
export function percentile(valori: readonly number[], p: number): number {
  if (valori.length === 0) return 0;
  const ordinati = [...valori].sort((a, b) => a - b);
  if (ordinati.length === 1) return ordinati[0];
  const posizione = p * (ordinati.length - 1);
  const sotto = Math.floor(posizione);
  const resto = posizione - sotto;
  if (sotto + 1 >= ordinati.length) return ordinati[ordinati.length - 1];
  return ordinati[sotto] + resto * (ordinati[sotto + 1] - ordinati[sotto]);
}

/** Mediana con la convenzione di Excel, cioe' media dei due centrali se sono pari. */
export function mediana(valori: readonly number[]): number {
  if (valori.length === 0) return 0;
  const ordinati = [...valori].sort((a, b) => a - b);
  const n = ordinati.length;
  const mezzo = Math.floor(n / 2);
  return n % 2 ? ordinati[mezzo] : (ordinati[mezzo - 1] + ordinati[mezzo]) / 2;
}

/**
 * L'arrotondamento di Excel, che sul mezzo si allontana da zero.
 *
 * Non e' `Math.round`, che sul negativo arrotonda verso l'alto: su meno ventidue e mezzo
 * quello darebbe meno ventidue e questo da' meno ventitre'. Nel tornado la differenza si
 * vedeva sul lato che riduce la durata del mutuo, e valeva centosettanta euro l'anno.
 */
export function arrotonda(valore: number): number {
  return valore >= 0 ? Math.floor(valore + 0.5) : -Math.floor(-valore + 0.5);
}

function fra(valore: number, minimo: number, massimo: number): number {
  return Math.min(Math.max(valore, minimo), massimo);
}

/** Rata costante dell'ammortamento alla francese, con il caso a tasso nullo isolato. */
function rataFrancese(importo: number, tassoAnnuo: number, durataAnni: number): number {
  const n = durataAnni * 12;
  if (n <= 0) return 0;
  const i = tassoAnnuo / 12;
  if (i === 0) return importo / n;
  return (importo * i) / (1 - Math.pow(1 + i, -n));
}

/** Debito residuo dopo un certo numero di anni, con il limite a tasso nullo. */
export function debitoResiduo(
  importo: number,
  tassoAnnuo: number,
  durataAnni: number,
  anniPagati: number,
): number {
  const n = durataAnni * 12;
  if (importo <= 0 || n <= 0) return 0;
  const pagate = Math.min(anniPagati, durataAnni) * 12;
  const i = tassoAnnuo / 12;
  if (i === 0) return importo * (1 - pagate / n);
  const montanteFinale = Math.pow(1 + i, n);
  return (importo * (montanteFinale - Math.pow(1 + i, pagate))) / (montanteFinale - 1);
}

// ---------------------------------------------------------------------------
// Il singolo scenario
// ---------------------------------------------------------------------------

/**
 * Un solo scenario, dalle estrazioni grezze all'esito patrimoniale.
 *
 * I segni con cui il fattore comune entra in ciascuna variabile dicono che cosa significa
 * uno scenario favorevole: canone e rivalutazione salgono, sfitto e tasso scendono, la
 * morosita' diventa meno probabile.
 */
export function scenario(
  base: BaseSimulazione,
  incertezze: Incertezze,
  estrazione: Estrazione,
): EsitoScenario {
  const [carico, proprio] = pesi(incertezze.correlazione);

  const zCanone = carico * estrazione.comune + proprio * estrazione.canone;
  const zSfitto = -carico * estrazione.comune + proprio * estrazione.sfitto;
  const zTasso = -carico * estrazione.comune + proprio * estrazione.tasso;
  const zRivalutazione = carico * estrazione.comune + proprio * estrazione.rivalutazione;
  const zEvento = carico * estrazione.comune + proprio * inversaNormale(estrazione.evento);

  const canoneAnnuo =
    Math.max(0, base.canone_mensile * (1 + zCanone * incertezze.vol_canone)) * 12;
  const mesiSfitto = fra(base.mesi_sfitto + zSfitto * incertezze.vol_sfitto, 0, 12);
  const tasso = Math.max(0, base.tasso + zTasso * incertezze.vol_tasso);
  const orizzonte = Math.max(base.orizzonte_anni, 1);
  const rivalutazione =
    base.rivalutazione + (zRivalutazione * incertezze.vol_rivalutazione) / Math.sqrt(orizzonte);

  // La morosita' grave si decide nella scala normale, dove il confronto e' esatto: ai due
  // estremi la probabilita' non passa per l'inversa, che e' il punto in cui divergerebbe.
  let morositaGrave: boolean;
  if (incertezze.prob_morosita_grave <= 0) {
    morositaGrave = false;
  } else if (incertezze.prob_morosita_grave >= 1) {
    morositaGrave = true;
  } else {
    morositaGrave = zEvento < inversaNormale(incertezze.prob_morosita_grave);
  }

  const canonePerso = morositaGrave ? (canoneAnnuo / 12) * incertezze.mesi_persi_morosita : 0;
  const ricavoEffettivo = Math.max(
    0,
    (canoneAnnuo - (canoneAnnuo / 12) * mesiSfitto) * (1 - base.morosita) - canonePerso,
  );

  const costiOperativi = base.ricavo_effettivo - base.noi_annuo;
  const noi = ricavoEffettivo - costiOperativi;
  const utileNetto = noi - ricavoEffettivo * base.aliquota_canone;
  const rataAnnua =
    base.mutuo_importo > 0 ? rataFrancese(base.mutuo_importo, tasso, base.durata_anni) * 12 : 0;
  const cashFlow = utileNetto - rataAnnua;

  const valoreFinale = base.prezzo * Math.pow(1 + rivalutazione, base.orizzonte_anni);
  const residuo = debitoResiduo(base.mutuo_importo, tasso, base.durata_anni, base.orizzonte_anni);
  const patrimonioFinale = valoreFinale * (1 - base.costi_vendita) - residuo;

  // I flussi si capitalizzano al rendimento del portafoglio alternativo, perche' un flusso
  // negativo va versato prendendolo da altrove e quel denaro ha un costo opportunita'.
  const flussiCapitalizzati =
    base.rendimento_portafoglio === 0
      ? cashFlow * base.orizzonte_anni
      : (cashFlow * (Math.pow(1 + base.rendimento_portafoglio, base.orizzonte_anni) - 1)) /
        base.rendimento_portafoglio;

  return {
    zCanone,
    zSfitto,
    zTasso,
    zRivalutazione,
    zEvento,
    morositaGrave,
    canoneAnnuo,
    mesiSfitto,
    tasso,
    rivalutazione,
    ricavoEffettivo,
    noi,
    utileNetto,
    rataAnnua,
    cashFlow,
    valoreFinale,
    debitoResiduo: residuo,
    patrimonioFinale,
    montante: patrimonioFinale + flussiCapitalizzati,
    rendimentoNetto: base.costo_totale > 0 ? utileNetto / base.costo_totale : 0,
  };
}

function distribuzione(valori: readonly number[]): Distribuzione {
  return {
    peggiore5: percentile(valori, 0.05),
    mediana: mediana(valori),
    migliore5: percentile(valori, 0.95),
  };
}

/** La simulazione completa: percentili, mediane e le quattro probabilita' che contano. */
export function simula(
  base: BaseSimulazione,
  incertezze: Incertezze,
  estrazioni: readonly Estrazione[],
): SintesiRischio {
  const esiti = estrazioni.map((e) => scenario(base, incertezze, e));
  const n = esiti.length;
  if (n === 0) {
    const vuota: Distribuzione = { peggiore5: 0, mediana: 0, migliore5: 0 };
    return {
      estrazioni: 0,
      cashFlow: vuota,
      utileNetto: vuota,
      rendimentoNetto: vuota,
      patrimonioFinale: vuota,
      montante: vuota,
      probCashNegativo: 0,
      probSottoObiettivo: 0,
      probPerditaCapitale: 0,
      probBatteAlternativa: 0,
    };
  }

  const cash = esiti.map((e) => e.cashFlow);
  const utili = esiti.map((e) => e.utileNetto);
  const rendimenti = esiti.map((e) => e.rendimentoNetto);
  const patrimoni = esiti.map((e) => e.patrimonioFinale);
  const montanti = esiti.map((e) => e.montante);
  const sogliaAlternativa =
    base.esborso * Math.pow(1 + base.rendimento_portafoglio, base.orizzonte_anni);
  const quota = (predicato: (v: number) => boolean, valori: readonly number[]) =>
    valori.filter(predicato).length / n;

  return {
    estrazioni: n,
    cashFlow: distribuzione(cash),
    utileNetto: distribuzione(utili),
    rendimentoNetto: distribuzione(rendimenti),
    patrimonioFinale: distribuzione(patrimoni),
    montante: distribuzione(montanti),
    probCashNegativo: quota((v) => v < 0, cash),
    probSottoObiettivo: quota((v) => v < base.rendimento_obiettivo, rendimenti),
    probPerditaCapitale: quota((v) => v < base.esborso, patrimoni),
    probBatteAlternativa: quota((v) => v > sogliaAlternativa, montanti),
  };
}

// ---------------------------------------------------------------------------
// Tornado
// ---------------------------------------------------------------------------

interface Leve {
  canone?: number;
  costi?: number;
  tasso?: number;
  importo?: number;
  durata?: number;
  prezzo?: number;
  aliquota?: number;
  condominio?: number;
}

/** Il cash flow annuo deterministico, con una leva per ciascuna variabile del tornado. */
function cashFlowConLeve(base: BaseSimulazione, leve: Leve = {}): number {
  const {
    canone = 1,
    costi: fattoreCosti = 1,
    tasso: fattoreTasso = 1,
    importo = 1,
    durata: fattoreDurata = 1,
    prezzo = 1,
    aliquota = 1,
    condominio = 1,
  } = leve;

  const ricavo = base.ricavo_effettivo * canone;
  let costi = (base.ricavo_effettivo - base.noi_annuo) * fattoreCosti;
  // Il prezzo entra nei costi operativi attraverso manutenzione e accantonamento per la
  // ristrutturazione, che sono quote del valore: lo scostamento agisce su quelle due voci e
  // non sul prezzo, che a questo punto della catena e' gia' stato pagato.
  if (prezzo !== 1) {
    const delta = prezzo - 1;
    costi += base.prezzo * base.manutenzione_su_valore * delta;
    if (base.ristrutturazione_anni > 0) {
      costi +=
        ((base.prezzo * base.ristrutturazione_su_valore) / base.ristrutturazione_anni) * delta;
    }
  }
  if (condominio !== 1) {
    costi += base.condominio_annuo * base.quota_condominio * (condominio - 1);
  }
  const imposta = ricavo * base.aliquota_canone * aliquota;
  const durata = fattoreDurata !== 1 ? arrotonda(base.durata_anni * fattoreDurata) : base.durata_anni;
  const rata =
    base.mutuo_importo > 0
      ? rataFrancese(base.mutuo_importo * importo, base.tasso * fattoreTasso, durata) * 12
      : 0;
  return ricavo - costi - imposta - rata;
}

/** Il valore centrale rispetto a cui il tornado misura gli scostamenti. */
export function cashFlowRiferimento(base: BaseSimulazione): number {
  return cashFlowConLeve(base);
}

/**
 * Ogni variabile mossa da sola in meno e in piu', e l'ampiezza che ne risulta.
 *
 * L'ordine e' quello di dichiarazione, che e' anche quello del foglio: mostrare le voci per
 * ampiezza decrescente, che e' il modo in cui un tornado si guarda, spetta a chi le mostra.
 */
export function tornado(
  base: BaseSimulazione,
  scostamento: number = SCOSTAMENTO_TORNADO,
): VoceTornado[] {
  const giu = 1 - scostamento;
  const su = 1 + scostamento;
  const leve: Array<[string, keyof Leve]> = [
    ["Canone", "canone"],
    ["Costi operativi", "costi"],
    ["Tasso del mutuo", "tasso"],
    ["Importo del mutuo", "importo"],
    ["Durata del mutuo", "durata"],
    ["Prezzo", "prezzo"],
    ["Aliquota sul canone", "aliquota"],
    ["Spese condominiali", "condominio"],
  ];
  return leve.map(([variabile, leva]) => {
    const meno = cashFlowConLeve(base, { [leva]: giu });
    const piu = cashFlowConLeve(base, { [leva]: su });
    return { variabile, meno, piu, ampiezza: Math.abs(piu - meno) };
  });
}

// ---------------------------------------------------------------------------
// Estrazioni per l'uso interattivo
// ---------------------------------------------------------------------------

/**
 * Estrazioni riproducibili a partire da un seme, per l'uso nel browser.
 *
 * Sta fuori dalla parte verificata contro Python, e va detto perche': le estrazioni di
 * Python vengono dal suo Mersenne Twister e queste da un generatore diverso, quindi le due
 * sequenze non coincidono ne' possono. Cio' che deve coincidere e' l'esito a estrazioni
 * date, e quello i vettori lo verificano. Qui l'unico requisito e' che lo stesso seme dia
 * sempre la stessa sequenza, perche' una simulazione che cambia risposta a ogni ridisegno
 * dell'interfaccia non e' uno strumento di decisione.
 *
 * Il generatore e' mulberry32, scelto perche' sta in cinque righe leggibili e ha un periodo
 * di due alla trentadue, che su mille estrazioni per sessione e' abbondante. Le normali si
 * ottengono con Box-Muller in forma polare, che consuma due uniformi per due normali.
 */
export function estrazioniDaSeme(quante: number, seme: number): Estrazione[] {
  let stato = seme >>> 0;
  const uniforme = (): number => {
    stato = (stato + 0x6d2b79f5) >>> 0;
    let t = stato;
    t = Math.imul(t ^ (t >>> 15), t | 1);
    t ^= t + Math.imul(t ^ (t >>> 7), t | 61);
    return ((t ^ (t >>> 14)) >>> 0) / 4294967296;
  };
  // Box-Muller richiede un'uniforme strettamente positiva, altrimenti il logaritmo diverge.
  const normale = (): number => {
    let u = 0;
    while (u === 0) u = uniforme();
    return Math.sqrt(-2 * Math.log(u)) * Math.cos(2 * Math.PI * uniforme());
  };
  const fuori: Estrazione[] = [];
  for (let k = 0; k < quante; k += 1) {
    fuori.push({
      comune: normale(),
      canone: normale(),
      sfitto: normale(),
      tasso: normale(),
      rivalutazione: normale(),
      evento: fra(uniforme(), 1e-6, 1 - 1e-6),
    });
  }
  return fuori;
}
