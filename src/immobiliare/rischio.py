# -*- coding: utf-8 -*-
"""Simulazione probabilistica degli esiti e analisi a tornado.

Il modulo porta in Python la parte del modello che finora esisteva soltanto come formule
del foglio Rischio, cioè la distribuzione degli esiti su mille scenari e la classifica
delle ipotesi per quanto spostano il risultato. La ragione per cui viene scritta qui non è
la comodità: fino a oggi quella parte del modello aveva una sola implementazione, e una
sola implementazione non si può verificare se non guardandola, che è esattamente ciò che
questo progetto ha smesso di fare altrove. Con questa versione le due si confrontano sullo
stesso caso, e con i vettori generati da `tools/genera-motore.py` la terza
implementazione, quella TypeScript che girerà nel browser, si confronta con entrambe.

Tre scelte di forma vanno dette prima del codice, perché spiegano le firme.

Le estrazioni non si generano dentro la simulazione: si passano. La simulazione diventa
così una funzione pura del suo ingresso, quindi provabile con estrazioni scelte a mano e
confrontabile fra implementazioni che non condividono il generatore pseudocasuale, che è
il caso di Python e JavaScript. La funzione `estrazioni_fisse` produce quelle
riproducibili, con lo stesso seme e lo stesso ordine di chiamata del generatore del
workbook, così che i numeri di questo modulo e quelli del foglio nascosto siano gli stessi
e un confronto con Excel misuri il modello e non due campioni diversi.

La correlazione fra le variabili di scenario segue ADR-023, cioè il fattore comune con i
pesi pari alla radice della correlazione e alla radice del suo complemento. La proprietà
da cui non si deroga è che la somma dei quadrati dei pesi faccia uno, perché è quella che
tiene le incertezze dichiarate esattamente dove sono state dichiarate.

L'evento di morosità grave si decide nella scala normale e non in quella delle
probabilità. Il foglio calcola la cumulata della mescolanza e la confronta con la
probabilità impostata; qui si confronta la mescolanza con l'inversa della normale di
quella probabilità, che è la stessa disuguaglianza applicata in modo monotono a entrambi i
membri. È equivalente per matematica e preferibile per aritmetica, perché attraversa una
funzione in meno, e soprattutto perché l'inversa della normale si riproduce a piena
precisione in ogni linguaggio mentre la cumulata richiede una funzione degli errori che
non tutti hanno con la stessa accuratezza.
"""

from __future__ import annotations

import random
from dataclasses import dataclass
from statistics import NormalDist
from typing import Sequence

from . import calcoli as C
from . import parametri as P

SEME_PREDEFINITO = 20260831
ESTRAZIONI_PREDEFINITE = 1000
SCOSTAMENTO_TORNADO = 0.10

_NORMALE = NormalDist()


# ---------------------------------------------------------------------------
# Ingressi
# ---------------------------------------------------------------------------

@dataclass(frozen=True)
class Estrazione:
    """Un'estrazione grezza: il fattore comune, le quattro componenti proprie, l'evento.

    Le prime cinque sono normali standard, la sesta è una uniforme in zero-uno tenuta
    lontana dagli estremi perché la trasformazione che la lega al fattore comune passa per
    l'inversa della normale, che in zero e in uno diverge.
    """

    comune: float
    canone: float
    sfitto: float
    tasso: float
    rivalutazione: float
    evento: float


@dataclass(frozen=True)
class Incertezze:
    """Quanto ci si sbaglia nel prevedere, che è l'unica cosa che si imposta qui.

    I valori predefiniti sono quelli del foglio Rischio. La correlazione al trenta per
    cento è una convenzione dichiarata e non una stima, e il modo corretto di usarla è
    muoverla: se la decisione cambia, non era solida.
    """

    vol_canone: float = 0.10
    vol_sfitto: float = 1.5
    vol_tasso: float = 0.0
    vol_rivalutazione: float = 0.04
    prob_morosita_grave: float = 0.05
    mesi_persi_morosita: float = 12.0
    correlazione: float = 0.30


@dataclass(frozen=True)
class BaseSimulazione:
    """Le grandezze deterministiche su cui la simulazione applica i propri scarti.

    Sono le stesse celle che il foglio Rischio legge per nome dagli altri fogli, e la
    corrispondenza è voluta: chi confronta questo modulo con il workbook deve poter mettere
    le due cose una accanto all'altra senza tradurre nulla. Si costruisce a mano per una
    prova, oppure con `base_da_modello` a partire dagli oggetti del motore.

    Sull'aliquota va detta una cosa che il foglio non dice. La simulazione tassa il ricavo
    effettivo con la cedolare secca sul canone libero qualunque sia il regime scelto
    altrove, perché la formula del foglio nascosto cita quella cella e non quella del
    regime selezionato. Qui l'aliquota è un parametro, con lo stesso valore predefinito,
    così che il confronto con Excel resti esatto e chi vuole l'aliquota del regime scelto
    la passi.
    """

    canone_mensile: float
    ricavo_effettivo: float
    noi_annuo: float
    costo_totale: float
    esborso: float
    prezzo: float
    mesi_sfitto: float = 1.0
    morosita: float = 0.03
    aliquota_canone: float = P.LOCAZIONE.cedolare_libero
    tasso: float = 0.032
    durata_anni: int = 25
    mutuo_importo: float = 0.0
    rivalutazione: float = 0.02
    orizzonte_anni: int = 25
    costi_vendita: float = 0.03
    rendimento_portafoglio: float = P.FINANZA.rendimento_portafoglio_lordo
    rendimento_obiettivo: float = 0.04
    condominio_annuo: float = 1_200.0
    quota_condominio: float = 0.4
    manutenzione_su_valore: float = 0.01
    ristrutturazione_su_valore: float = P.COSTI.ristrutturazione_su_valore
    ristrutturazione_anni: int = P.COSTI.anni_fra_ristrutturazioni


# ---------------------------------------------------------------------------
# Esiti
# ---------------------------------------------------------------------------

@dataclass(frozen=True)
class EsitoScenario:
    """Un singolo scenario, dalle estrazioni efficaci fino al montante."""

    z_canone: float
    z_sfitto: float
    z_tasso: float
    z_rivalutazione: float
    z_evento: float
    morosita_grave: bool
    canone_annuo: float
    mesi_sfitto: float
    tasso: float
    rivalutazione: float
    ricavo_effettivo: float
    noi: float
    utile_netto: float
    rata_annua: float
    cash_flow: float
    valore_finale: float
    debito_residuo: float
    patrimonio_finale: float
    montante: float
    rendimento_netto: float


@dataclass(frozen=True)
class Distribuzione:
    """I tre numeri con cui si legge una distribuzione: la coda cattiva, il centro, la buona."""

    peggiore_5: float
    mediana: float
    migliore_5: float


@dataclass(frozen=True)
class SintesiRischio:
    """Distribuzioni e probabilità, cioè quello che il foglio Rischio mostra."""

    estrazioni: int
    cash_flow: Distribuzione
    utile_netto: Distribuzione
    rendimento_netto: Distribuzione
    patrimonio_finale: Distribuzione
    montante: Distribuzione
    prob_cash_negativo: float
    prob_sotto_obiettivo: float
    prob_perdita_capitale: float
    prob_batte_alternativa: float


@dataclass(frozen=True)
class VoceTornado:
    """Una variabile mossa da sola, e di quanto sposta il cash flow annuo."""

    variabile: str
    meno: float
    piu: float
    ampiezza: float


# ---------------------------------------------------------------------------
# Estrazioni e pesi
# ---------------------------------------------------------------------------

def estrazioni_fisse(
    quante: int = ESTRAZIONI_PREDEFINITE, seme: int = SEME_PREDEFINITO
) -> list[Estrazione]:
    """Le estrazioni riproducibili, nello stesso ordine con cui le scrive il workbook.

    L'ordine delle chiamate e l'arrotondamento a sei decimali non sono dettagli: il foglio
    nascosto conserva i valori arrotondati e calcola da quelli, quindi chi confronta questo
    modulo con Excel su un caso reale deve partire dagli stessi numeri. L'uniforme si tiene
    a un milionesimo dagli estremi per la ragione detta in `Estrazione`.
    """
    generatore = random.Random(seme)
    fuori: list[Estrazione] = []
    for _ in range(quante):
        cinque = [round(generatore.gauss(0, 1), 6) for _ in range(5)]
        uniforme = round(min(max(generatore.random(), 1e-6), 1 - 1e-6), 6)
        fuori.append(Estrazione(*cinque, uniforme))
    return fuori


def pesi(correlazione: float) -> tuple[float, float]:
    """I due pesi della mescolanza: radice della correlazione, radice del complemento.

    Fuori dall'intervallo zero-uno la radice non esiste, quindi il valore si riporta dentro
    invece di produrre un numero immaginario o un errore: un'interfaccia che accetta una
    correlazione del centoventi per cento è un problema di validazione, non un motivo per
    far cadere una simulazione.
    """
    rho = min(max(correlazione, 0.0), 1.0)
    return rho ** 0.5, (1.0 - rho) ** 0.5


# ---------------------------------------------------------------------------
# Statistica compatibile con Excel
# ---------------------------------------------------------------------------

def percentile(valori: Sequence[float], p: float) -> float:
    """Percentile con l'interpolazione lineare di PERCENTILE.INC di Excel.

    Replicare la convenzione di Excel invece di usarne una qualsiasi serve al confronto:
    due percentili calcolati con convenzioni diverse differiscono di poco e sempre, e uno
    scarto piccolo e sistematico è il modo peggiore di sbagliare, perché somiglia a un
    errore di arrotondamento e non lo è.
    """
    if not valori:
        return 0.0
    ordinati = sorted(valori)
    if len(ordinati) == 1:
        return ordinati[0]
    posizione = p * (len(ordinati) - 1)
    sotto = int(posizione)
    resto = posizione - sotto
    if sotto + 1 >= len(ordinati):
        return ordinati[-1]
    return ordinati[sotto] + resto * (ordinati[sotto + 1] - ordinati[sotto])


def mediana(valori: Sequence[float]) -> float:
    """Mediana con la convenzione di Excel, cioè media dei due centrali se sono pari."""
    if not valori:
        return 0.0
    ordinati = sorted(valori)
    n = len(ordinati)
    mezzo = n // 2
    if n % 2:
        return ordinati[mezzo]
    return (ordinati[mezzo - 1] + ordinati[mezzo]) / 2


def _distribuzione(valori: Sequence[float]) -> Distribuzione:
    return Distribuzione(
        peggiore_5=percentile(valori, 0.05),
        mediana=mediana(valori),
        migliore_5=percentile(valori, 0.95),
    )


def _fra(valore: float, minimo: float, massimo: float) -> float:
    """Il MEDIAN a tre argomenti del foglio, che in Excel si usa come limitatore."""
    return min(max(valore, minimo), massimo)


def arrotonda(valore: float) -> int:
    """L'arrotondamento di Excel, che sul mezzo si allontana da zero.

    La funzione integrata di Python arrotonda invece il mezzo al pari, ed è la ragione per
    cui la prima versione di questo modulo dava una durata di ventidue anni dove il foglio
    ne dava ventitre': venticinque anni ridotti del dieci per cento fanno ventidue e mezzo,
    che qui diventa ventitre' e con l'arrotondamento bancario diventa ventidue. Lo scarto
    sul cash flow era di centosettanta euro l'anno, quindi non nel rumore, e si presentava
    su un lato solo del tornado, che è il modo in cui una differenza di convenzione somiglia
    a un difetto del modello.
    """
    if valore >= 0:
        return int(valore + 0.5)
    return -int(-valore + 0.5)


# ---------------------------------------------------------------------------
# Il singolo scenario
# ---------------------------------------------------------------------------

def debito_residuo(importo: float, tasso_annuo: float, durata_anni: int, anni_pagati: float) -> float:
    """Debito residuo dopo un certo numero di anni di ammortamento alla francese.

    La formula chiusa del foglio divide per la differenza fra due montanti, che a tasso
    nullo è zero: il foglio in quel caso restituirebbe un errore di divisione, e siccome un
    tasso fisso a zero è raro ma non impossibile il caso è trattato qui per quello che è,
    cioè il limite in cui il capitale si rimborsa in parti uguali.
    """
    n = durata_anni * 12
    if importo <= 0 or n <= 0:
        return 0.0
    pagate = min(anni_pagati, durata_anni) * 12
    i = tasso_annuo / 12
    if i == 0:
        return importo * (1 - pagate / n)
    montante_finale = (1 + i) ** n
    return importo * (montante_finale - (1 + i) ** pagate) / (montante_finale - 1)


def scenario(base: BaseSimulazione, incertezze: Incertezze, estrazione: Estrazione) -> EsitoScenario:
    """Un solo scenario, dalle estrazioni grezze all'esito patrimoniale.

    Il verso con cui il fattore comune entra in ciascuna variabile è la parte che dice che
    cosa significa uno scenario favorevole: canone e rivalutazione salgono, sfitto e tasso
    scendono, la morosità diventa meno probabile. Cambiare quei segni cambia il significato
    della correlazione, quindi stanno qui e non in una tabella di configurazione.
    """
    carico, proprio = pesi(incertezze.correlazione)

    z_canone = carico * estrazione.comune + proprio * estrazione.canone
    z_sfitto = -carico * estrazione.comune + proprio * estrazione.sfitto
    z_tasso = -carico * estrazione.comune + proprio * estrazione.tasso
    z_rivalutazione = carico * estrazione.comune + proprio * estrazione.rivalutazione
    z_evento = carico * estrazione.comune + proprio * _NORMALE.inv_cdf(estrazione.evento)

    canone_annuo = max(0.0, base.canone_mensile * (1 + z_canone * incertezze.vol_canone)) * 12
    mesi_sfitto = _fra(base.mesi_sfitto + z_sfitto * incertezze.vol_sfitto, 0.0, 12.0)
    tasso = max(0.0, base.tasso + z_tasso * incertezze.vol_tasso)
    orizzonte = max(base.orizzonte_anni, 1)
    rivalutazione = (
        base.rivalutazione + z_rivalutazione * incertezze.vol_rivalutazione / orizzonte ** 0.5
    )

    # La morosità grave si decide qui, e il confronto sta nella scala normale per la ragione
    # spiegata in testa al modulo. Ai due estremi la probabilità non passa per l'inversa,
    # che è il punto in cui divergerebbe.
    if incertezze.prob_morosita_grave <= 0:
        morosita_grave = False
    elif incertezze.prob_morosita_grave >= 1:
        morosita_grave = True
    else:
        morosita_grave = z_evento < _NORMALE.inv_cdf(incertezze.prob_morosita_grave)

    canone_perso = canone_annuo / 12 * incertezze.mesi_persi_morosita if morosita_grave else 0.0
    ricavo_effettivo = max(
        0.0,
        (canone_annuo - canone_annuo / 12 * mesi_sfitto) * (1 - base.morosita) - canone_perso,
    )

    costi_operativi = base.ricavo_effettivo - base.noi_annuo
    noi = ricavo_effettivo - costi_operativi
    utile_netto = noi - ricavo_effettivo * base.aliquota_canone
    rata_annua = (
        C.rata_francese(base.mutuo_importo, tasso, base.durata_anni) * 12
        if base.mutuo_importo > 0
        else 0.0
    )
    cash_flow = utile_netto - rata_annua

    valore_finale = base.prezzo * (1 + rivalutazione) ** base.orizzonte_anni
    residuo = debito_residuo(base.mutuo_importo, tasso, base.durata_anni, base.orizzonte_anni)
    patrimonio_finale = valore_finale * (1 - base.costi_vendita) - residuo

    # I flussi si capitalizzano al rendimento del portafoglio alternativo invece di essere
    # sommati a valore nominale, perché un flusso negativo va versato prendendolo da altrove
    # e quel denaro ha un costo opportunità. A rendimento nullo la somma geometrica degenera
    # e si usa il prodotto, che ne è il limite.
    if base.rendimento_portafoglio == 0:
        flussi_capitalizzati = cash_flow * base.orizzonte_anni
    else:
        crescita = (1 + base.rendimento_portafoglio) ** base.orizzonte_anni - 1
        flussi_capitalizzati = cash_flow * crescita / base.rendimento_portafoglio

    return EsitoScenario(
        z_canone=z_canone,
        z_sfitto=z_sfitto,
        z_tasso=z_tasso,
        z_rivalutazione=z_rivalutazione,
        z_evento=z_evento,
        morosita_grave=morosita_grave,
        canone_annuo=canone_annuo,
        mesi_sfitto=mesi_sfitto,
        tasso=tasso,
        rivalutazione=rivalutazione,
        ricavo_effettivo=ricavo_effettivo,
        noi=noi,
        utile_netto=utile_netto,
        rata_annua=rata_annua,
        cash_flow=cash_flow,
        valore_finale=valore_finale,
        debito_residuo=residuo,
        patrimonio_finale=patrimonio_finale,
        montante=patrimonio_finale + flussi_capitalizzati,
        rendimento_netto=utile_netto / base.costo_totale if base.costo_totale > 0 else 0.0,
    )


def simula(
    base: BaseSimulazione,
    incertezze: Incertezze | None = None,
    estrazioni: Sequence[Estrazione] | None = None,
) -> SintesiRischio:
    """La simulazione completa: percentili, mediane e le quattro probabilità che contano.

    Le probabilità usano il confronto stretto o largo del foglio, che su mille scenari non
    è un dettaglio: la probabilità di cash flow negativo conta gli scenari strettamente
    sotto zero, quella di battere l'alternativa quelli strettamente sopra il montante del
    portafoglio.
    """
    incertezze = incertezze or Incertezze()
    estrazioni = estrazioni if estrazioni is not None else estrazioni_fisse()
    esiti = [scenario(base, incertezze, e) for e in estrazioni]
    n = len(esiti)
    if n == 0:
        vuota = Distribuzione(0.0, 0.0, 0.0)
        return SintesiRischio(0, vuota, vuota, vuota, vuota, vuota, 0.0, 0.0, 0.0, 0.0)

    cash = [e.cash_flow for e in esiti]
    utili = [e.utile_netto for e in esiti]
    rendimenti = [e.rendimento_netto for e in esiti]
    patrimoni = [e.patrimonio_finale for e in esiti]
    montanti = [e.montante for e in esiti]
    soglia_alternativa = base.esborso * (1 + base.rendimento_portafoglio) ** base.orizzonte_anni

    return SintesiRischio(
        estrazioni=n,
        cash_flow=_distribuzione(cash),
        utile_netto=_distribuzione(utili),
        rendimento_netto=_distribuzione(rendimenti),
        patrimonio_finale=_distribuzione(patrimoni),
        montante=_distribuzione(montanti),
        prob_cash_negativo=sum(1 for v in cash if v < 0) / n,
        prob_sotto_obiettivo=sum(1 for v in rendimenti if v < base.rendimento_obiettivo) / n,
        prob_perdita_capitale=sum(1 for v in patrimoni if v < base.esborso) / n,
        prob_batte_alternativa=sum(1 for v in montanti if v > soglia_alternativa) / n,
    )


# ---------------------------------------------------------------------------
# Tornado
# ---------------------------------------------------------------------------

def _cash_flow(
    base: BaseSimulazione,
    fattore_canone: float = 1.0,
    fattore_costi: float = 1.0,
    fattore_tasso: float = 1.0,
    fattore_importo: float = 1.0,
    fattore_durata: float = 1.0,
    fattore_prezzo: float = 1.0,
    fattore_aliquota: float = 1.0,
    fattore_condominio: float = 1.0,
) -> float:
    """Il cash flow annuo deterministico, con una leva per ciascuna variabile del tornado.

    Il foglio scrive otto formule diverse, una per variabile, ognuna col proprio fattore
    infilato al punto giusto. Qui la formula è una sola e i fattori sono parametri, che è la
    stessa cosa detta in modo che non si possa sbagliare a copiare: nel foglio, otto formule
    quasi identiche sono otto occasioni di scrivere il fattore nel posto sbagliato.
    """
    ricavo = base.ricavo_effettivo * fattore_canone
    costi = (base.ricavo_effettivo - base.noi_annuo) * fattore_costi
    # Il prezzo entra nei costi operativi attraverso manutenzione e accantonamento per la
    # ristrutturazione, che sono quote del valore: lo scostamento agisce su quelle due voci
    # e non sul prezzo, che a questo punto della catena è già stato pagato.
    if fattore_prezzo != 1.0:
        delta = fattore_prezzo - 1.0
        costi += base.prezzo * base.manutenzione_su_valore * delta
        if base.ristrutturazione_anni > 0:
            costi += (
                base.prezzo * base.ristrutturazione_su_valore / base.ristrutturazione_anni * delta
            )
    if fattore_condominio != 1.0:
        costi += base.condominio_annuo * base.quota_condominio * (fattore_condominio - 1.0)
    # L'imposta si calcola sul ricavo mosso, non su quello base: è la sola variabile che
    # entra due volte nella formula, e il foglio la scrive due volte per questo.
    imposta = ricavo * base.aliquota_canone * fattore_aliquota
    durata = arrotonda(base.durata_anni * fattore_durata) if fattore_durata != 1.0 else base.durata_anni
    rata = (
        C.rata_francese(base.mutuo_importo * fattore_importo, base.tasso * fattore_tasso, durata) * 12
        if base.mutuo_importo > 0
        else 0.0
    )
    return ricavo - costi - imposta - rata


def cash_flow_riferimento(base: BaseSimulazione) -> float:
    """Il valore centrale rispetto a cui il tornado misura gli scostamenti."""
    return _cash_flow(base)


def tornado(base: BaseSimulazione, scostamento: float = SCOSTAMENTO_TORNADO) -> list[VoceTornado]:
    """Ogni variabile mossa da sola in meno e in più, e l'ampiezza che ne risulta.

    L'ordine è quello di dichiarazione, che è anche quello del foglio: la lettura per
    ampiezza decrescente, che è il modo in cui un tornado si guarda, resta di chi mostra i
    dati. Restituire una lista già ordinata renderebbe il confronto con il foglio un
    confronto fra due ordini diversi, e nasconderebbe il fatto che nel foglio l'ordine di
    lettura lo dà una scala di colore e non la posizione delle righe.
    """
    giu = 1 - scostamento
    su = 1 + scostamento
    leve = [
        ("Canone", "fattore_canone"),
        ("Costi operativi", "fattore_costi"),
        ("Tasso del mutuo", "fattore_tasso"),
        ("Importo del mutuo", "fattore_importo"),
        ("Durata del mutuo", "fattore_durata"),
        ("Prezzo", "fattore_prezzo"),
        ("Aliquota sul canone", "fattore_aliquota"),
        ("Spese condominiali", "fattore_condominio"),
    ]
    voci: list[VoceTornado] = []
    for etichetta, leva in leve:
        meno = _cash_flow(base, **{leva: giu})
        piu = _cash_flow(base, **{leva: su})
        voci.append(VoceTornado(etichetta, meno, piu, abs(piu - meno)))
    return voci


# ---------------------------------------------------------------------------
# Costruzione della base dagli oggetti del motore
# ---------------------------------------------------------------------------

def base_da_modello(
    immobile: C.Immobile,
    gestione: C.Gestione,
    finanziamento: C.Finanziamento,
    costo: C.CostoOperazione,
    conto: C.ContoEconomico,
    orizzonte_anni: int = 25,
    rivalutazione: float = 0.02,
    rendimento_obiettivo: float = 0.04,
    costi_vendita: float = 0.03,
    aliquota_canone: float | None = None,
) -> BaseSimulazione:
    """Assembla la base dagli oggetti che il resto del motore produce già.

    Serve a non far ricopiare a mano venti numeri che esistono altrove, che è il modo in cui
    una simulazione finisce per girare su un caso diverso da quello valutato. Il ricavo
    effettivo e il reddito operativo netto sono quelli del conto economico, quindi del
    regime scelto là, mentre l'aliquota resta separata perché il foglio usa la cedolare sul
    canone libero anche quando il regime è un altro.
    """
    return BaseSimulazione(
        canone_mensile=gestione.canone_mensile,
        ricavo_effettivo=conto.canone_effettivo,
        noi_annuo=conto.noi,
        costo_totale=costo.costo_totale,
        esborso=costo.esborso_iniziale,
        prezzo=immobile.prezzo,
        mesi_sfitto=gestione.mesi_sfitto_annui,
        morosita=gestione.morosita,
        aliquota_canone=P.LOCAZIONE.cedolare_libero if aliquota_canone is None else aliquota_canone,
        tasso=finanziamento.tasso_annuo,
        durata_anni=finanziamento.durata_anni,
        mutuo_importo=finanziamento.importo,
        rivalutazione=rivalutazione,
        orizzonte_anni=orizzonte_anni,
        costi_vendita=costi_vendita,
        rendimento_obiettivo=rendimento_obiettivo,
        condominio_annuo=gestione.condominio_annuo,
        quota_condominio=gestione.quota_condominio_a_carico_proprietario,
        manutenzione_su_valore=gestione.manutenzione_su_valore,
    )
