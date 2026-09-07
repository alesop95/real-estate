// Motore di calcolo, porto in TypeScript di src/immobiliare/calcoli.py.
//
// Regole di questa traduzione, che valgono anche per chi la estenderà.
//
// La prima e' che l'implementazione di riferimento resta quella Python: quando i due
// motori divergono ha ragione Python fino a prova contraria, e la divergenza si scopre
// dalla suite che confronta i vettori generati da `tools/genera-motore.py`.
//
// La seconda e' che le operazioni si fanno nello stesso ordine dell'originale, anche
// dove un ordine diverso sarebbe piu' leggibile. Su numeri in doppia precisione la somma
// non e' associativa, e cambiare l'ordine sposta le ultime cifre: la tolleranza dichiarata
// dei vettori e' 1e-9 relativo, che quel genere di riordino puo' superare. Dove l'ordine
// e' stato conservato per questa ragione e non per altra, c'e' un commento.
//
// La terza e' che i parametri non si scrivono qui: vengono da `parametri.generati.ts`,
// che il generatore emette da `parametri.py`. Un'aliquota copiata a mano e' il primo
// posto in cui le due implementazioni divergono in silenzio.

import { costi, finanza, imposteTrasferimento, imu as imuP, irpef, locazione, mutuo as mutuoP, plusvalenza } from "./parametri.generati";
import type {
  Acquirente,
  ContoEconomico,
  CostoOperazione,
  EffettoInflazione,
  EsitoConfronto,
  Finanziamento,
  Gestione,
  Immobile,
  ImposteAcquisto,
  Metriche,
  RataAmmortamento,
  Regime,
} from "./tipi";

const CATEGORIE_LUSSO = imposteTrasferimento.categorieEsclusePrimaCasa;

/** Formatta una frazione come percentuale intera, cioe' il "{:.0%}" di Python. */
function percentualeIntera(frazione: number): string {
  return `${Math.round(frazione * 100)}%`;
}

// ---------------------------------------------------------------------------
// Base imponibile e imposte di trasferimento
// ---------------------------------------------------------------------------

/** Base imponibile del registro con la regola prezzo-valore. */
export function valoreCatastale(rendita: number, primaCasa: boolean): number {
  const moltiplicatore = primaCasa
    ? imposteTrasferimento.moltiplicatorePrimaCasa
    : imposteTrasferimento.moltiplicatoreOrdinario;
  return rendita * imposteTrasferimento.rivalutazioneRendita * moltiplicatore;
}

/**
 * Vero se l'agevolazione prima casa spetta davvero.
 *
 * Non basta che l'acquirente la chieda: le categorie A/1, A/8 e A/9 ne sono escluse per
 * definizione, e l'esclusione si riflette anche sul moltiplicatore catastale. Tenere la
 * verifica in una funzione sola evita che moltiplicatore e aliquota si disallineino.
 */
export function agevolazioneApplicabile(immobile: Immobile, acquirente: Acquirente): boolean {
  const diLusso = CATEGORIE_LUSSO.includes(immobile.categoria);
  return acquirente.prima_casa && !diLusso;
}

/** Sceglie fra valore catastale e prezzo secondo l'opzione prezzo-valore. */
export function baseImponibileRegistro(immobile: Immobile, acquirente: Acquirente): number {
  if (!acquirente.prezzo_valore || immobile.rendita_catastale <= 0) {
    return immobile.prezzo;
  }
  return valoreCatastale(immobile.rendita_catastale, agevolazioneApplicabile(immobile, acquirente));
}

/** Imposte dovute al rogito nei quattro casi rilevanti. */
export function imposteAcquisto(immobile: Immobile, acquirente: Acquirente): ImposteAcquisto {
  const t = imposteTrasferimento;
  const diLusso = t.categorieEsclusePrimaCasa.includes(immobile.categoria);
  const primaCasa = agevolazioneApplicabile(immobile, acquirente);

  if (immobile.venditore_impresa) {
    const aliquota = primaCasa ? t.ivaPrimaCasa : diLusso ? t.ivaLusso : t.ivaOrdinaria;
    // In regime IVA la base e' sempre il prezzo pattuito: il prezzo-valore non si
    // applica, perche' e' una regola dell'imposta di registro.
    const iva = immobile.prezzo * aliquota;
    return {
      imponibile: immobile.prezzo,
      iva,
      registro: t.registroFissoDaImpresa,
      ipotecaria: t.ipotecariaDaImpresa,
      catastale: t.catastaleDaImpresa,
      regime: `impresa con IVA ${percentualeIntera(aliquota)}`,
      totale: iva + t.registroFissoDaImpresa + t.ipotecariaDaImpresa + t.catastaleDaImpresa,
    };
  }

  const imponibile = baseImponibileRegistro(immobile, acquirente);
  const aliquota = primaCasa ? t.registroPrimaCasa : t.registroOrdinario;
  const registro = Math.max(imponibile * aliquota, t.registroMinimo);
  return {
    imponibile,
    iva: 0,
    registro,
    ipotecaria: t.ipotecariaDaPrivato,
    catastale: t.catastaleDaPrivato,
    regime:
      `privato, registro ${percentualeIntera(aliquota)}` +
      (imponibile !== immobile.prezzo ? " su valore catastale" : " su prezzo"),
    totale: 0 + registro + t.ipotecariaDaPrivato + t.catastaleDaPrivato,
  };
}

/** Provvigione di mediazione, IVA inclusa. */
export function provvigioneAgenzia(prezzo: number, aliquota: number = costi.provvigioneAgenziaTipica): number {
  return prezzo * aliquota * (1 + costi.ivaSuProvvigione);
}

/** Imposta sostitutiva sul finanziamento, trattenuta dalla banca sull'erogato. */
export function impostaSostitutivaMutuo(importo: number, primaCasa: boolean): number {
  const aliquota = primaCasa ? mutuoP.impostaSostitutivaPrimaCasa : mutuoP.impostaSostitutivaOrdinaria;
  return importo * aliquota;
}

/** Somma prezzo, imposte e costi accessori dell'operazione. */
export function costoOperazione(
  immobile: Immobile,
  acquirente: Acquirente,
  finanziamento: Finanziamento,
  provvigionePct: number = costi.provvigioneAgenziaTipica,
  notaioCompravendita = 2_000,
  altriCosti = 0,
): CostoOperazione {
  const imposte = imposteAcquisto(immobile, acquirente);
  const primaCasa = agevolazioneApplicabile(immobile, acquirente);
  const haMutuo = finanziamento.importo > 0;

  const provvigione = provvigioneAgenzia(immobile.prezzo, provvigionePct);
  const notaioMutuo = haMutuo ? finanziamento.notaio_atto_mutuo : 0;
  const sostitutivaMutuo = haMutuo ? impostaSostitutivaMutuo(finanziamento.importo, primaCasa) : 0;
  const istruttoria = haMutuo ? finanziamento.istruttoria : 0;
  const perizia = haMutuo ? finanziamento.perizia : 0;

  // Ordine dei termini identico alla proprieta' `costi_accessori` dell'originale.
  const costiAccessori =
    imposte.totale + provvigione + notaioCompravendita + notaioMutuo + sostitutivaMutuo + istruttoria + perizia + altriCosti;
  const costoTotale = immobile.prezzo + costiAccessori;

  return {
    prezzo: immobile.prezzo,
    imposte,
    provvigione,
    notaioCompravendita,
    notaioMutuo,
    sostitutivaMutuo,
    istruttoria,
    perizia,
    altriCosti,
    mutuo: finanziamento.importo,
    costiAccessori,
    costoTotale,
    esborsoIniziale: costoTotale - finanziamento.importo,
    incidenzaCosti: immobile.prezzo ? costiAccessori / immobile.prezzo : 0,
  };
}

// ---------------------------------------------------------------------------
// Mutuo: ammortamento alla francese
// ---------------------------------------------------------------------------

/** Rata costante dell'ammortamento alla francese. */
export function rataFrancese(importo: number, tassoAnnuo: number, durataAnni: number, ratePerAnno = 12): number {
  const n = durataAnni * ratePerAnno;
  if (n <= 0) return 0;
  const i = tassoAnnuo / ratePerAnno;
  // Con tasso nullo la rata e' la divisione del capitale per il numero di rate: il caso
  // va isolato perche' la formula generale divide per zero.
  if (i === 0) return importo / n;
  return (importo * i) / (1 - Math.pow(1 + i, -n));
}

/** Piano di ammortamento alla francese, rata per rata. */
export function pianoAmmortamento(
  importo: number,
  tassoAnnuo: number,
  durataAnni: number,
  ratePerAnno = 12,
): RataAmmortamento[] {
  const piano: RataAmmortamento[] = [];
  if (importo <= 0 || durataAnni <= 0) return piano;
  const rata = rataFrancese(importo, tassoAnnuo, durataAnni, ratePerAnno);
  const i = tassoAnnuo / ratePerAnno;
  let residuo = importo;
  for (let k = 1; k <= durataAnni * ratePerAnno; k += 1) {
    const interessi = residuo * i;
    const capitale = rata - interessi;
    residuo = Math.max(residuo - capitale, 0);
    piano.push({
      numero: k,
      anno: Math.floor((k - 1) / ratePerAnno) + 1,
      quotaInteressi: interessi,
      quotaCapitale: capitale,
      rata,
      debitoResiduo: residuo,
    });
  }
  return piano;
}

/** Interessi passivi aggregati per anno di ammortamento. */
export function interessiPerAnno(piano: readonly RataAmmortamento[]): Map<number, number> {
  const somme = new Map<number, number>();
  for (const r of piano) {
    somme.set(r.anno, (somme.get(r.anno) ?? 0) + r.quotaInteressi);
  }
  return somme;
}

/**
 * Detrazione IRPEF del 19% sugli interessi, entro il massimale di 4.000 euro.
 *
 * Il massimale e' riferito all'immobile e va ripartito fra i cointestatari del mutuo. La
 * detrazione spetta solo se l'immobile e' adibito ad abitazione principale, quindi non
 * spetta sull'immobile comprato per affittarlo.
 */
export function detrazioneInteressi(interessiAnno: number, quota = 1, abitazionePrincipale = true): number {
  if (!abitazionePrincipale) return 0;
  const massimale = mutuoP.detrazioneInteressiMassimale * quota;
  return Math.min(interessiAnno, massimale) * mutuoP.detrazioneInteressiAliquota;
}

/** TAEG stimato, come tasso che azzera il valore attuale dei flussi. */
export function taegApprossimato(
  importo: number,
  tassoAnnuo: number,
  durataAnni: number,
  costiIniziali: number,
  costiAnnui: number,
): number {
  const n = durataAnni * 12;
  if (n <= 0 || importo <= 0) return 0;
  const rata = rataFrancese(importo, tassoAnnuo, durataAnni);
  const rataEffettiva = rata + costiAnnui / 12;
  const nettoErogato = importo - costiIniziali;
  const flussi = [-nettoErogato, ...Array<number>(n).fill(rataEffettiva)];
  return tir(flussi) * 12;
}

// ---------------------------------------------------------------------------
// Locazione: canoni e tassazione
// ---------------------------------------------------------------------------

/** Aliquota di cedolare secca associata al regime, zero per l'IRPEF ordinaria. */
export function aliquotaRegime(regime: Regime): number {
  switch (regime) {
    case "cedolare_libero":
      return locazione.cedolareLibero;
    case "cedolare_concordato":
      return locazione.cedolareConcordato;
    case "breve_prima_unita":
      return locazione.cedolareBrevePrimaUnita;
    case "breve_altre_unita":
      return locazione.cedolareBreveAltreUnita;
    case "irpef_ordinario":
    case "irpef_concordato":
      return 0;
    default: {
      // Il tipo Regime esclude gli altri valori: se questo ramo si raggiunge, qualcuno ha
      // aggiunto un regime al motore Python e non qui, ed e' meglio saperlo subito.
      const mai: never = regime;
      throw new Error(`regime non riconosciuto: ${String(mai)}`);
    }
  }
}

/** IRPEF lorda sugli scaglioni dell'anno d'imposta. */
export function irpefLorda(imponibile: number): number {
  let dovuta = 0;
  let precedente = 0;
  for (const [soglia, aliquota] of irpef.scaglioni) {
    if (imponibile <= precedente) break;
    const quota = Math.min(imponibile, soglia) - precedente;
    dovuta += quota * aliquota;
    precedente = soglia;
  }
  return dovuta;
}

/**
 * Imposta sul reddito da locazione secondo il regime scelto.
 *
 * In cedolare secca l'imposta e' proporzionale e sostituisce IRPEF, addizionali, registro
 * e bollo. In regime ordinario il canone concorre al reddito complessivo con l'abbattimento
 * forfettario, e l'imposta e' la differenza fra l'IRPEF con e senza il canone, cosi' da
 * catturare l'aliquota marginale effettiva.
 */
export function impostaSulCanone(canoneAnnuo: number, regime: Regime, redditoAltro = 0): number {
  if (regime.startsWith("cedolare") || regime.startsWith("breve")) {
    return canoneAnnuo * aliquotaRegime(regime);
  }

  const abbattimento =
    regime === "irpef_concordato"
      ? locazione.abbattimentoForfettarioConcordato
      : locazione.abbattimentoForfettarioOrdinario;
  const imponibileCanone = canoneAnnuo * (1 - abbattimento);
  const marginale = irpefLorda(redditoAltro + imponibileCanone) - irpefLorda(redditoAltro);
  const addizionali = imponibileCanone * (irpef.addizionaleRegionaleTipica + irpef.addizionaleComunaleTipica);
  let registro = Math.max(canoneAnnuo * locazione.registroAnnuo, locazione.registroMinimo);
  if (regime === "irpef_concordato") {
    registro = Math.max(
      canoneAnnuo * (1 - locazione.riduzioneBaseRegistroConcordato) * locazione.registroAnnuo,
      locazione.registroMinimo,
    );
  }
  // L'imposta di registro e' dovuta per meta' da ciascuna parte, salvo patto.
  return marginale + addizionali + registro / 2;
}

/** IMU dovuta sull'immobile. */
export function imuAnnua(
  rendita: number,
  aliquota: number = imuP.aliquotaBase,
  categoria = "A/2",
  abitazionePrincipale = false,
  canoneConcordato = false,
  comodato = false,
): number {
  const diLusso = categoria === "A/1" || categoria === "A/8" || categoria === "A/9";
  if (abitazionePrincipale && !diLusso) return 0;
  let base = rendita * imuP.rivalutazioneRendita * imuP.moltiplicatoreGruppoA;
  if (comodato) base *= imuP.riduzioneComodato;
  let imposta = base * aliquota;
  if (abitazionePrincipale && diLusso) {
    imposta = Math.max(base * imuP.aliquotaAbitazionePrincipaleLusso - imuP.detrazioneAbitazionePrincipale, 0);
  } else if (canoneConcordato) {
    imposta *= imuP.riduzioneCanoneConcordato;
  }
  return imposta;
}

/** Costruisce il conto economico annuo a partire dalle assunzioni di gestione. */
export function contoEconomico(immobile: Immobile, gestione: Gestione, redditoAltro = 0): ContoEconomico {
  const breve = gestione.regime.startsWith("breve");
  let potenziale: number;
  let sfitto: number;
  let morosita: number;
  let gestioneCosto: number;
  if (breve) {
    potenziale = gestione.ricavi_lordi_brevi_annui;
    sfitto = 0;
    morosita = 0;
    gestioneCosto = potenziale * (gestione.gestione_su_canone + gestione.costi_variabili_brevi);
  } else {
    potenziale = gestione.canone_mensile * 12;
    sfitto = gestione.canone_mensile * gestione.mesi_sfitto_annui;
    morosita = (potenziale - sfitto) * gestione.morosita;
    gestioneCosto = (potenziale - sfitto - morosita) * gestione.gestione_su_canone;
  }

  const effettivo = potenziale - sfitto - morosita;
  const concordato = gestione.regime.includes("concordato");
  const condominio = gestione.condominio_annuo * gestione.quota_condominio_a_carico_proprietario;
  const manutenzione = immobile.prezzo * gestione.manutenzione_su_valore;
  const assicurazione = gestione.assicurazione_annua;
  const imu = imuAnnua(immobile.rendita_catastale, gestione.aliquota_imu, immobile.categoria, false, concordato);
  const ristrutturazione = (immobile.prezzo * costi.ristrutturazioneSuValore) / costi.anniFraRistrutturazioni;
  const imposta = impostaSulCanone(effettivo, gestione.regime, redditoAltro);

  // Ordine identico alla proprieta' `costi_operativi` dell'originale.
  const costiOperativi = condominio + manutenzione + assicurazione + imu + gestioneCosto + ristrutturazione;
  const noi = effettivo - costiOperativi;

  return {
    canonePotenziale: potenziale,
    perditaSfitto: sfitto,
    perditaMorosita: morosita,
    condominio,
    manutenzione,
    assicurazione,
    imu,
    gestione: gestioneCosto,
    imposta,
    ristrutturazione,
    canoneEffettivo: effettivo,
    costiOperativi,
    noi,
    utileNetto: noi - imposta,
  };
}

// ---------------------------------------------------------------------------
// Metriche di rendimento
// ---------------------------------------------------------------------------

/**
 * Somma dei flussi attualizzati, con il termine che sfonda la precisione trattato.
 *
 * Riproduce `_valore_attuale` del motore Python, compresa la gestione dei due estremi che
 * la bisezione visita. A tasso vicino a meno uno il fattore di sconto scende sotto il minimo
 * rappresentabile e diventa zero: il valore corretto e' un infinito col segno del flusso, non
 * uno zero. A tasso dieci il fattore supera il massimo e diventa infinito: il flusso
 * attualizzato e' allora indistinguibile da zero e il termine non contribuisce. In JavaScript
 * nessuno dei due casi solleva un'eccezione, a differenza di Python, ma vanno trattati
 * comunque, perche' altrimenti si otterrebbe NaN dalla divisione di infinito per infinito.
 */
function valoreAttuale(flussi: readonly number[], tasso: number): number {
  let totale = 0;
  for (let k = 0; k < flussi.length; k += 1) {
    const f = flussi[k];
    const fattore = Math.pow(1 + tasso, k);
    if (!Number.isFinite(fattore)) continue;
    if (fattore === 0) {
      if (f === 0) continue;
      return f > 0 ? Infinity : -Infinity;
    }
    totale += f / fattore;
  }
  return totale;
}

/** Valore attuale netto della serie di flussi al tasso indicato. */
export function van(flussi: readonly number[], tasso: number): number {
  return valoreAttuale(flussi, tasso);
}

/**
 * Tasso interno di rendimento, per bisezione su un intervallo ampio.
 *
 * La bisezione e' preferita a Newton perche' non diverge sui flussi immobiliari, dove il
 * primo termine e' un esborso grande e i successivi sono piccoli e di segno costante.
 * Restituisce zero se non esiste un cambio di segno nell'intervallo.
 */
export function tir(flussi: readonly number[], tolleranza = 1e-7, iterazioni = 200): number {
  let basso = -0.9999;
  let alto = 10;
  let vBasso = valoreAttuale(flussi, basso);
  const vAlto = valoreAttuale(flussi, alto);
  if (vBasso * vAlto > 0) return 0;
  for (let n = 0; n < iterazioni; n += 1) {
    const medio = (basso + alto) / 2;
    const vMedio = valoreAttuale(flussi, medio);
    if (Math.abs(vMedio) < tolleranza) return medio;
    if (vBasso * vMedio < 0) {
      alto = medio;
    } else {
      basso = medio;
      vBasso = vMedio;
    }
  }
  return (basso + alto) / 2;
}

/**
 * Indicatori calcolati sul costo totale, non sul solo prezzo.
 *
 * La distinzione e' sostanziale: usare il prezzo come denominatore gonfia il rendimento del
 * dieci-quindici per cento, perche' ignora imposte, notaio e provvigione, che sono capitale
 * immobilizzato a tutti gli effetti.
 */
export function metriche(costo: CostoOperazione, conto: ContoEconomico, rataAnnua: number): Metriche {
  const cashFlow = conto.utileNetto - rataAnnua;
  return {
    rendimentoLordo: costo.prezzo ? conto.canonePotenziale / costo.prezzo : 0,
    rendimentoNetto: costo.costoTotale ? conto.utileNetto / costo.costoTotale : 0,
    capRate: costo.costoTotale ? conto.noi / costo.costoTotale : 0,
    cashOnCash: costo.esborsoIniziale ? cashFlow / costo.esborsoIniziale : 0,
    dscr: rataAnnua ? conto.noi / rataAnnua : Infinity,
    cashFlowAnnuo: cashFlow,
    paybackAnni: cashFlow > 0 ? costo.esborsoIniziale / cashFlow : Infinity,
  };
}

// ---------------------------------------------------------------------------
// Effetto dell'inflazione
// ---------------------------------------------------------------------------

/**
 * Tasso reale esatto, per l'equazione di Fisher: (1+r)/(1+i)-1.
 *
 * La forma che si vede scritta quasi sempre e' la sottrazione, cioe' r meno i, e non e' la
 * definizione: e' la sua approssimazione al primo ordine. Il modello usa sempre la forma
 * esatta e mostra accanto l'errore che si commetterebbe con l'altra.
 */
export function tassoReale(tassoNominale: number, inflazione: number): number {
  if (inflazione <= -1) {
    throw new Error("inflazione non ammissibile: renderebbe nullo il livello dei prezzi");
  }
  return (1 + tassoNominale) / (1 + inflazione) - 1;
}

/** Riporta un importo futuro al potere d'acquisto di oggi. */
export function deflaziona(valoreNominale: number, inflazione: number, anni: number): number {
  return valoreNominale / Math.pow(1 + inflazione, anni);
}

/**
 * Valore attuale di una rendita unitaria che cresce a tasso costante.
 *
 * Il caso in cui la crescita coincide col tasso di sconto annulla il denominatore e va
 * trattato a parte: allora ogni termine vale 1/(1+g) e la somma e' n/(1+g). Non e' un caso
 * di scuola, perche' assumere una crescita del canone pari al tasso di sconto reale e'
 * un'ipotesi che qualcuno fa davvero.
 */
export function fattoreRenditaCrescente(crescita: number, sconto: number, anni: number): number {
  if (sconto <= -1 || crescita <= -1) throw new Error("tassi non ammissibili");
  const q = (1 + crescita) / (1 + sconto);
  if (Math.abs(q - 1) < 1e-12) return anni / (1 + crescita);
  return (q * (1 - Math.pow(q, anni))) / ((1 + crescita) * (1 - q));
}

/** Scompone l'effetto dell'inflazione sulle grandezze dell'operazione. */
export function effettoInflazione(argomenti: {
  inflazione: number;
  rendimentoNettoNominale: number;
  tirNominale: number;
  prezzo: number;
  rivalutazioneImmobile: number;
  debitoResiduoNominale: number;
  rataAnnua: number;
  canoneAnnuo: number;
  indicizzazioneCanone: number;
  orizzonteAnni: number;
  tassoSconto: number;
}): EffettoInflazione {
  const a = argomenti;
  const reale = tassoReale(a.rendimentoNettoNominale, a.inflazione);
  const valoreFinale = a.prezzo * Math.pow(1 + a.rivalutazioneImmobile, a.orizzonteAnni);
  const debitoReale = deflaziona(a.debitoResiduoNominale, a.inflazione, a.orizzonteAnni);

  // Il canone perso: differenza fra un canone indicizzato all'inflazione piena e quello
  // indicizzato come dichiarato, attualizzata al tasso di sconto. La somma segue l'ordine
  // dell'originale, anno per anno crescente.
  let perso = 0;
  for (let anno = 1; anno <= a.orizzonteAnni; anno += 1) {
    const pieno = a.canoneAnnuo * Math.pow(1 + a.inflazione, anno - 1);
    const effettivo = a.canoneAnnuo * Math.pow(1 + a.indicizzazioneCanone, anno - 1);
    perso += (pieno - effettivo) / Math.pow(1 + a.tassoSconto, anno);
  }

  return {
    inflazione: a.inflazione,
    rendimentoNettoNominale: a.rendimentoNettoNominale,
    rendimentoNettoReale: reale,
    erroreApprossimazione: a.rendimentoNettoNominale - a.inflazione - reale,
    erosioneRealeCanone: tassoReale(a.indicizzazioneCanone, a.inflazione),
    rivalutazioneRealeImmobile: tassoReale(a.rivalutazioneImmobile, a.inflazione),
    tirNominale: a.tirNominale,
    tirReale: tassoReale(a.tirNominale, a.inflazione),
    valoreFinaleNominale: valoreFinale,
    valoreFinaleReale: deflaziona(valoreFinale, a.inflazione, a.orizzonteAnni),
    debitoResiduoNominale: a.debitoResiduoNominale,
    debitoResiduoReale: debitoReale,
    scontoInflazioneSulDebito: a.debitoResiduoNominale - debitoReale,
    rataAnnuaRealeAFineOrizzonte: deflaziona(a.rataAnnua, a.inflazione, a.orizzonteAnni),
    canonePersoPerMancataIndicizzazione: perso,
  };
}

/**
 * Plusvalenza e imposta sostitutiva dovuta in caso di rivendita.
 *
 * L'imponibilita' decade oltre i cinque anni, o oltre i dieci per gli immobili con
 * superbonus, e non scatta se l'immobile e' stato abitazione principale.
 */
export function plusvalenzaSuRivendita(
  prezzoVendita: number,
  costoAcquisto: number,
  anniPossesso: number,
  abitazionePrincipale = false,
  superbonus = false,
): { lorda: number; imposta: number } {
  const plus = Math.max(prezzoVendita - costoAcquisto, 0);
  const soglia = superbonus ? plusvalenza.anniImponibilitaSuperbonus : plusvalenza.anniImponibilitaOrdinaria;
  if (anniPossesso >= soglia || abitazionePrincipale) return { lorda: plus, imposta: 0 };
  return { lorda: plus, imposta: plus * plusvalenza.impostaSostitutiva };
}

// ---------------------------------------------------------------------------
// Confronto fra comprare e restare in affitto investendo la differenza
// ---------------------------------------------------------------------------

/**
 * Confronta il patrimonio finale nei due scenari, a parita' di esborso.
 *
 * Chi compra immobilizza l'anticipo e paga rata e costi ricorrenti; chi affitta investe
 * l'anticipo e ogni anno investe o disinveste la differenza fra quanto avrebbe speso
 * comprando e quanto spende in affitto. Alla fine si confrontano il valore dell'immobile al
 * netto del debito residuo e il valore del portafoglio al netto dell'imposta sul capital gain.
 */
export function confrontoCompraOAffitta(
  costo: CostoOperazione,
  finanziamento: Finanziamento,
  canoneAlternativoMensile: number,
  anni: number,
  rivalutazioneImmobile: number = finanza.inflazioneAttesa,
  rendimentoPortafoglio: number = finanza.rendimentoPortafoglioLordo,
  tassazionePortafoglio: number = finanza.tassazioneRenditeFinanziarie,
  costiRicorrentiProprietario = 0,
  inflazioneCanone: number = finanza.inflazioneAttesa,
): EsitoConfronto {
  const rataMensile = rataFrancese(finanziamento.importo, finanziamento.tasso_annuo, finanziamento.durata_anni);
  const piano = pianoAmmortamento(finanziamento.importo, finanziamento.tasso_annuo, finanziamento.durata_anni);

  const valoreImmobile = costo.prezzo * Math.pow(1 + rivalutazioneImmobile, anni);
  const ratePagate = Math.min(anni * 12, piano.length);
  const debitoResiduo = ratePagate ? piano[ratePagate - 1].debitoResiduo : finanziamento.importo;
  const patrimonioComprando = valoreImmobile - debitoResiduo;

  // Chi affitta parte investendo l'anticipo che l'altro ha immobilizzato.
  let portafoglio = costo.esborsoIniziale;
  let versato = costo.esborsoIniziale;
  let canone = canoneAlternativoMensile * 12;
  for (let anno = 1; anno <= anni; anno += 1) {
    const uscitaProprietario = (anno * 12 <= piano.length ? rataMensile * 12 : 0) + costiRicorrentiProprietario;
    const differenza = uscitaProprietario - canone;
    portafoglio = portafoglio * (1 + rendimentoPortafoglio) + differenza;
    versato += differenza;
    canone *= 1 + inflazioneCanone;
  }

  const guadagno = Math.max(portafoglio - versato, 0);
  const patrimonioAffittando = portafoglio - guadagno * tassazionePortafoglio;
  const differenza = patrimonioComprando - patrimonioAffittando;
  return {
    patrimonioComprando,
    patrimonioAffittando,
    differenza,
    convieneComprare: differenza > 0,
  };
}
