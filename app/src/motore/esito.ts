// L'esito completo di una valutazione: da una descrizione dell'operazione a tutti i numeri.
//
// Esiste per due ragioni che coincidono. La prima e' che l'interfaccia ha bisogno di una
// funzione sola da chiamare quando un input cambia, invece di orchestrare quindici chiamate
// nell'ordine giusto: il calcolo non vive nelle sezioni, vive qui. La seconda e' che i
// vettori di riscontro generati dal motore Python hanno esattamente questa forma, quindi la
// suite di verifica confronta la funzione che l'applicazione usa davvero, e non una scritta
// per il test. Se le due cose fossero separate, la verifica sarebbe su codice morto.
//
// L'ordine delle chiamate e la scelta di che cosa passare a chi rispecchiano `calcola` in
// tools/genera-motore.py: quello e' il contratto.

import {
  agevolazioneApplicabile,
  baseImponibileRegistro,
  confrontoCompraOAffitta,
  contoEconomico,
  costoOperazione,
  detrazioneInteressi,
  effettoInflazione,
  fattoreRenditaCrescente,
  imposteAcquisto,
  interessiPerAnno,
  irpefLorda,
  metriche,
  pianoAmmortamento,
  plusvalenzaSuRivendita,
  rataFrancese,
  taegApprossimato,
  tir,
  valoreCatastale,
  van,
} from "./motore";
import { finanza } from "./parametri.generati";
import type { Acquirente, Finanziamento, Gestione, Immobile } from "./tipi";

/** Tutto ciò che descrive un'operazione da valutare. */
export interface Ingresso {
  immobile: Immobile;
  acquirente: Acquirente;
  finanziamento: Finanziamento;
  gestione: Gestione;
  orizzonte_anni: number;
  reddito_altro: number;
  rivalutazione_immobile: number;
  canone_alternativo_mensile: number;
  inflazione: number;
  indicizzazione_canone: number;
}

export function esitoCompleto(ingresso: Ingresso) {
  const { immobile, acquirente, finanziamento, gestione } = ingresso;
  const orizzonte = ingresso.orizzonte_anni;
  const redditoAltro = ingresso.reddito_altro;
  const rivalutazione = ingresso.rivalutazione_immobile;

  const imposte = imposteAcquisto(immobile, acquirente);
  const costo = costoOperazione(immobile, acquirente, finanziamento);
  const piano = pianoAmmortamento(finanziamento.importo, finanziamento.tasso_annuo, finanziamento.durata_anni);
  const interessi = interessiPerAnno(piano);
  const rataMensile = rataFrancese(finanziamento.importo, finanziamento.tasso_annuo, finanziamento.durata_anni);
  const conto = contoEconomico(immobile, gestione, redditoAltro);
  const met = metriche(costo, conto, rataMensile * 12);

  const ratePagate = Math.min(orizzonte * 12, piano.length);
  const debitoResiduo = ratePagate ? piano[ratePagate - 1].debitoResiduo : finanziamento.importo;
  const valoreFinale = immobile.prezzo * Math.pow(1 + rivalutazione, orizzonte);

  // I flussi per il tasso interno: l'esborso iniziale, poi il flusso di cassa annuo, e
  // sull'ultimo anno anche la vendita al netto del debito. Stesso ordine dell'originale.
  const flussi = [-costo.esborsoIniziale, ...Array<number>(orizzonte).fill(met.cashFlowAnnuo)];
  flussi[flussi.length - 1] += valoreFinale - debitoResiduo;
  const tirCalcolato = tir(flussi);

  const interessiPrimoAnno = interessi.get(1) ?? 0;
  const inflazione = effettoInflazione({
    inflazione: ingresso.inflazione,
    rendimentoNettoNominale: met.rendimentoNetto,
    tirNominale: tirCalcolato,
    prezzo: immobile.prezzo,
    rivalutazioneImmobile: rivalutazione,
    debitoResiduoNominale: debitoResiduo,
    rataAnnua: rataMensile * 12,
    canoneAnnuo: conto.canoneEffettivo,
    indicizzazioneCanone: ingresso.indicizzazione_canone,
    orizzonteAnni: orizzonte,
    tassoSconto: finanza.rendimentoPortafoglioLordo,
  });
  const plus = plusvalenzaSuRivendita(valoreFinale, costo.costoTotale, orizzonte);
  const confronto = confrontoCompraOAffitta(
    costo,
    finanziamento,
    ingresso.canone_alternativo_mensile,
    orizzonte,
    rivalutazione,
  );

  return {
    imposte: {
      imponibile: imposte.imponibile,
      iva: imposte.iva,
      registro: imposte.registro,
      ipotecaria: imposte.ipotecaria,
      catastale: imposte.catastale,
      totale: imposte.totale,
      regime: imposte.regime,
    },
    agevolazioneApplicabile: agevolazioneApplicabile(immobile, acquirente),
    baseImponibileRegistro: baseImponibileRegistro(immobile, acquirente),
    valoreCatastale: valoreCatastale(immobile.rendita_catastale, agevolazioneApplicabile(immobile, acquirente)),
    costo: {
      provvigione: costo.provvigione,
      notaioCompravendita: costo.notaioCompravendita,
      notaioMutuo: costo.notaioMutuo,
      sostitutivaMutuo: costo.sostitutivaMutuo,
      istruttoria: costo.istruttoria,
      perizia: costo.perizia,
      costiAccessori: costo.costiAccessori,
      costoTotale: costo.costoTotale,
      esborsoIniziale: costo.esborsoIniziale,
      incidenzaCosti: costo.incidenzaCosti,
    },
    mutuo: {
      rataMensile,
      rateTotali: piano.length,
      interessiPrimoAnno,
      interessiTotali: piano.reduce((somma, r) => somma + r.quotaInteressi, 0),
      debitoResiduoAOrizzonte: debitoResiduo,
      detrazioneInteressiPrimoAnno: detrazioneInteressi(interessiPrimoAnno),
      detrazioneSeLocato: detrazioneInteressi(interessiPrimoAnno, 1, false),
      taegApprossimato: taegApprossimato(
        finanziamento.importo,
        finanziamento.tasso_annuo,
        finanziamento.durata_anni,
        costo.sostitutivaMutuo + costo.istruttoria + costo.perizia,
        finanziamento.polizza_annua,
      ),
    },
    conto: {
      canonePotenziale: conto.canonePotenziale,
      perditaSfitto: conto.perditaSfitto,
      perditaMorosita: conto.perditaMorosita,
      canoneEffettivo: conto.canoneEffettivo,
      condominio: conto.condominio,
      manutenzione: conto.manutenzione,
      assicurazione: conto.assicurazione,
      imu: conto.imu,
      gestione: conto.gestione,
      ristrutturazione: conto.ristrutturazione,
      costiOperativi: conto.costiOperativi,
      noi: conto.noi,
      imposta: conto.imposta,
      utileNetto: conto.utileNetto,
    },
    metriche: {
      rendimentoLordo: met.rendimentoLordo,
      rendimentoNetto: met.rendimentoNetto,
      capRate: met.capRate,
      cashOnCash: met.cashOnCash,
      dscr: met.dscr,
      cashFlowAnnuo: met.cashFlowAnnuo,
      paybackAnni: met.paybackAnni,
    },
    tir: tirCalcolato,
    van: van(flussi, finanza.rendimentoPortafoglioLordo),
    inflazione: {
      rendimentoNettoReale: inflazione.rendimentoNettoReale,
      erroreApprossimazione: inflazione.erroreApprossimazione,
      erosioneRealeCanone: inflazione.erosioneRealeCanone,
      rivalutazioneRealeImmobile: inflazione.rivalutazioneRealeImmobile,
      tirReale: inflazione.tirReale,
      valoreFinaleNominale: inflazione.valoreFinaleNominale,
      valoreFinaleReale: inflazione.valoreFinaleReale,
      debitoResiduoReale: inflazione.debitoResiduoReale,
      scontoInflazioneSulDebito: inflazione.scontoInflazioneSulDebito,
      rataAnnuaRealeAFineOrizzonte: inflazione.rataAnnuaRealeAFineOrizzonte,
      canonePersoPerMancataIndicizzazione: inflazione.canonePersoPerMancataIndicizzazione,
    },
    plusvalenza: { lorda: plus.lorda, imposta: plus.imposta },
    confronto: {
      patrimonioComprando: confronto.patrimonioComprando,
      patrimonioAffittando: confronto.patrimonioAffittando,
      differenza: confronto.differenza,
      convieneComprare: confronto.convieneComprare,
    },
    fattoreRenditaCrescente: fattoreRenditaCrescente(0.02, 0.04, orizzonte),
    fattoreRenditaCrescenteDegenere: fattoreRenditaCrescente(0.04, 0.04, orizzonte),
    irpefLorda: irpefLorda(redditoAltro),
  };
}

export type Esito = ReturnType<typeof esitoCompleto>;
