# -*- coding: utf-8 -*-
"""Parametri normativi e fiscali dell'acquisto e della locazione residenziale in Italia.

Ogni costante porta accanto la fonte e la data di verifica. La revisione qui
dichiarata e' quella del 28 agosto 2026: i valori riflettono la legge di bilancio
2026 (legge 30 dicembre 2025, n. 199) e la guida dell'Agenzia delle Entrate sulle
locazioni brevi aggiornata ad aprile 2026.

Il modulo non calcola nulla: espone soltanto i numeri, cosi' che l'aggiornamento
annuale sia un intervento in un solo file e il resto del codice resti stabile.
"""

from __future__ import annotations

from dataclasses import dataclass
from datetime import date

REVISIONE = date(2026, 8, 28)
ANNO_IMPOSTA = 2026


# ---------------------------------------------------------------------------
# Imposte sul trasferimento
# ---------------------------------------------------------------------------

@dataclass(frozen=True)
class ImposteTrasferimento:
    """Imposte dovute al rogito, distinte per venditore e per agevolazione.

    Fonte: Agenzia delle Entrate, "L'acquisto della casa: le imposte e le
    agevolazioni fiscali".
    """

    # Acquisto da privato, o da impresa in esenzione IVA: registro proporzionale,
    # ipotecaria e catastale in misura fissa.
    registro_prima_casa: float = 0.02
    registro_ordinario: float = 0.09
    registro_minimo: float = 1_000.0
    ipotecaria_da_privato: float = 50.0
    catastale_da_privato: float = 50.0

    # Acquisto da impresa con IVA: IVA proporzionale, le altre tre in misura fissa.
    iva_prima_casa: float = 0.04
    iva_ordinaria: float = 0.10
    iva_lusso: float = 0.22          # categorie catastali A/1, A/8, A/9
    registro_fisso_da_impresa: float = 200.0
    ipotecaria_da_impresa: float = 200.0
    catastale_da_impresa: float = 200.0

    # Regola prezzo-valore, art. 1 comma 497 legge 266/2005: la base imponibile del
    # registro e' la rendita catastale rivalutata del 5% per il moltiplicatore.
    # Vale solo fuori campo IVA, per persone fisiche, su immobili a uso abitativo e
    # relative pertinenze, e va chiesta espressamente al notaio in atto.
    rivalutazione_rendita: float = 1.05
    moltiplicatore_prima_casa: int = 110
    moltiplicatore_ordinario: int = 120
    sconto_onorario_notaio_prezzo_valore: float = 0.30

    # Categorie catastali escluse dall'agevolazione prima casa.
    categorie_escluse_prima_casa: tuple = ("A/1", "A/8", "A/9")


IMPOSTE_TRASFERIMENTO = ImposteTrasferimento()


# ---------------------------------------------------------------------------
# Agevolazione prima casa
# ---------------------------------------------------------------------------

@dataclass(frozen=True)
class PrimaCasa:
    """Requisiti e termini dell'agevolazione prima casa.

    Il termine per rivendere la precedente abitazione agevolata e' passato da uno a
    due anni con la legge di bilancio 2025, art. 1 comma 116 legge 207/2024, e vale
    per gli atti dal 1 gennaio 2025 e per quelli 2024 il cui termine annuale non era
    ancora scaduto al 31 dicembre 2024. Il termine per riacquistare dopo una vendita
    infraquinquennale, invece, resta di un anno.
    """

    mesi_trasferimento_residenza: int = 18
    mesi_rivendita_precedente_agevolata: int = 24
    mesi_riacquisto_dopo_vendita: int = 12
    anni_vincolo_rivendita: int = 5
    # Credito d'imposta per riacquisto: pari all'imposta pagata sul primo acquisto
    # agevolato, entro il limite dell'imposta dovuta sul nuovo, art. 7 legge 448/1998.
    credito_riacquisto: bool = True


PRIMA_CASA = PrimaCasa()


# ---------------------------------------------------------------------------
# Costi del mutuo
# ---------------------------------------------------------------------------

@dataclass(frozen=True)
class Mutuo:
    """Oneri fiscali e accessori del finanziamento ipotecario.

    L'imposta sostitutiva assorbe registro, bollo, ipotecarie e catastali sul
    contratto di finanziamento, DPR 601/1973 artt. 15-20: 0,25% se il mutuo e' per
    l'acquisto della prima casa, 2% negli altri casi. La banca la trattiene
    direttamente dall'erogato.
    """

    imposta_sostitutiva_prima_casa: float = 0.0025
    imposta_sostitutiva_ordinaria: float = 0.02

    # Intervalli di mercato osservati, da sovrascrivere con il preventivo reale.
    istruttoria_min: float = 0.0
    istruttoria_max: float = 800.0
    perizia_min: float = 200.0
    perizia_max: float = 400.0
    polizza_incendio_annua_min: float = 100.0
    polizza_incendio_annua_max: float = 250.0
    notaio_atto_mutuo_min: float = 800.0
    notaio_atto_mutuo_max: float = 1_500.0

    # Loan to value oltre il quale serve una garanzia esterna.
    ltv_ordinario_max: float = 0.80
    ltv_con_fondo_consap: float = 1.00

    # Detrazione IRPEF degli interessi passivi sul mutuo dell'abitazione principale:
    # 19% su un massimale di 4.000 euro di interessi e oneri accessori, art. 15
    # comma 1 lett. b TUIR, quindi al massimo 760 euro l'anno. Richiede il
    # trasferimento della residenza entro 12 mesi.
    detrazione_interessi_aliquota: float = 0.19
    detrazione_interessi_massimale: float = 4_000.0
    mesi_residenza_per_detrazione: int = 12


MUTUO = Mutuo()


@dataclass(frozen=True)
class FondoConsap:
    """Fondo di garanzia per la prima casa gestito da Consap.

    Garanzia statale sulla quota capitale, che permette alle banche di erogare oltre
    l'80% del valore dell'immobile. La misura potenziata all'80% per under 36 e altre
    categorie prioritarie con ISEE entro 40.000 euro e' prorogata al 31 dicembre 2027.
    """

    garanzia_standard: float = 0.50
    garanzia_potenziata: float = 0.80
    isee_massimo_potenziata: float = 40_000.0
    eta_massima_under36: int = 36
    scadenza_misura_potenziata: date = date(2027, 12, 31)
    # L'esenzione da registro, ipotecaria, catastale e il credito d'imposta IVA per
    # gli under 36, art. 64 DL 73/2021, NON e' piu' in vigore: e' scaduta il
    # 31 dicembre 2023, salvo la coda sui preliminari registrati entro tale data.
    esenzione_imposte_under36_attiva: bool = False


FONDO_CONSAP = FondoConsap()


# ---------------------------------------------------------------------------
# Imposte sul possesso
# ---------------------------------------------------------------------------

@dataclass(frozen=True)
class Imu:
    """Imposta municipale propria.

    Base imponibile: rendita catastale rivalutata del 5% moltiplicata per il
    coefficiente di categoria, 160 per i fabbricati del gruppo A esclusa A/10.
    L'abitazione principale e' esente, salvo A/1, A/8 e A/9 che restano imponibili
    con detrazione di 200 euro. L'aliquota base e' lo 0,86%, che i Comuni possono
    azzerare o portare fino all'1,06%: il valore reale va letto nella delibera
    comunale dell'anno.
    """

    rivalutazione_rendita: float = 1.05
    moltiplicatore_gruppo_a: int = 160
    moltiplicatore_c2_c6_c7: int = 160
    moltiplicatore_a10_d5: int = 80
    moltiplicatore_c1: float = 55.0
    aliquota_base: float = 0.0086
    aliquota_massima: float = 0.0106
    aliquota_abitazione_principale_lusso: float = 0.005
    detrazione_abitazione_principale: float = 200.0
    # Riduzioni: 50% per immobile concesso in comodato a parenti in linea retta entro
    # il primo grado alle condizioni di legge, 25% di sconto sull'imposta per i
    # contratti a canone concordato, cioe' imposta ridotta al 75%.
    riduzione_canone_concordato: float = 0.75
    riduzione_comodato: float = 0.50
    scadenza_acconto: str = "16 giugno"
    scadenza_saldo: str = "16 dicembre"


IMU = Imu()


# ---------------------------------------------------------------------------
# Tassazione dei canoni
# ---------------------------------------------------------------------------

@dataclass(frozen=True)
class Locazione:
    """Regimi contrattuali e loro tassazione.

    Le aliquote di cedolare secca in vigore nel 2026 sono: 21% sui contratti a canone
    libero, 10% sui contratti a canone concordato nei Comuni ad alta tensione
    abitativa e sui contratti per studenti universitari, 21% sulla prima unita'
    destinata a locazione breve e 26% dalla seconda in poi.

    Dal 1 gennaio 2026 il regime delle locazioni brevi si applica a un massimo di due
    unita' immobiliari per periodo d'imposta: dalla terza scatta la presunzione di
    attivita' d'impresa con obbligo di partita IVA. La soglia era di quattro unita'
    fino al 31 dicembre 2025.
    """

    cedolare_libero: float = 0.21
    cedolare_concordato: float = 0.10
    cedolare_breve_prima_unita: float = 0.21
    cedolare_breve_altre_unita: float = 0.26

    # Regime ordinario IRPEF: base imponibile ridotta forfettariamente.
    abbattimento_forfettario_ordinario: float = 0.05   # imponibile 95%
    abbattimento_forfettario_concordato: float = 0.25  # imponibile 75%

    # Imposta di registro annuale in regime ordinario, a carico per meta' di ciascuna
    # parte salvo diverso accordo; la cedolare secca la sostituisce.
    registro_annuo: float = 0.02
    registro_minimo: float = 67.0
    riduzione_base_registro_concordato: float = 0.30
    bollo_per_copia: float = 16.0

    # Sconto tipico del canone concordato rispetto al libero. Non e' un valore di
    # legge: il canone concordato deriva dall'accordo territoriale del Comune, e la
    # forbice osservata sta fra il dieci e il venti per cento. Serve come default
    # dichiarato, perche' confrontare i due regimi allo stesso canone attribuisce al
    # concordato il vantaggio fiscale senza il costo che lo giustifica.
    sconto_canone_concordato: float = 0.15

    # Durate legali.
    durata_libero: str = "4 + 4"
    durata_concordato: str = "3 + 2"
    durata_transitorio_mesi: tuple = (1, 18)
    durata_studenti_mesi: tuple = (6, 36)
    soglia_locazione_breve_giorni: int = 30

    # Locazioni brevi: soglie e obblighi.
    max_unita_locazione_breve: int = 2
    ritenuta_intermediari: float = 0.21
    cin_obbligatorio: bool = True
    dispositivi_sicurezza_obbligatori: bool = True


LOCAZIONE = Locazione()


@dataclass(frozen=True)
class Irpef:
    """Scaglioni IRPEF 2026.

    La legge di bilancio 2026 ha ridotto la seconda aliquota dal 35% al 33% per i
    redditi fra 28.000 e 50.000 euro; il beneficio e' neutralizzato oltre i 200.000
    euro di reddito complessivo.
    """

    scaglioni: tuple = (
        (28_000.0, 0.23),
        (50_000.0, 0.33),
        (float("inf"), 0.43),
    )
    soglia_neutralizzazione_beneficio: float = 200_000.0
    addizionale_regionale_tipica: float = 0.0173
    addizionale_comunale_tipica: float = 0.008


IRPEF = Irpef()


# ---------------------------------------------------------------------------
# Plusvalenza in caso di rivendita
# ---------------------------------------------------------------------------

@dataclass(frozen=True)
class Plusvalenza:
    """Tassazione della plusvalenza da cessione, art. 67 comma 1 lett. b TUIR.

    La plusvalenza e' imponibile se fra acquisto e rivendita passano meno di cinque
    anni, salvo che l'immobile sia stato adibito ad abitazione principale del cedente
    o dei suoi familiari per la maggior parte del periodo. In atto si puo' chiedere al
    notaio l'imposta sostitutiva del 26% in luogo dell'IRPEF.

    Per gli immobili oggetto di interventi agevolati con superbonus conclusi da meno
    di dieci anni la finestra si estende a dieci anni, art. 1 commi 64-67 legge
    213/2023, con esclusioni per successione e per abitazione principale.
    """

    anni_imponibilita_ordinaria: int = 5
    anni_imponibilita_superbonus: int = 10
    imposta_sostitutiva: float = 0.26
    esclusione_abitazione_principale: bool = True
    esclusione_successione: bool = True


PLUSVALENZA = Plusvalenza()


# ---------------------------------------------------------------------------
# Costi accessori e assunzioni di gestione
# ---------------------------------------------------------------------------

@dataclass(frozen=True)
class CostiAccessori:
    """Costi non fiscali dell'operazione e della gestione.

    Sono valori di mercato indicativi: vanno sempre sostituiti con i preventivi reali.
    La provvigione di agenzia e' soggetta a IVA al 22% ed e' dovuta, salvo patto
    contrario, alla conclusione dell'affare, cioe' all'accettazione della proposta,
    non al rogito.
    """

    provvigione_agenzia_tipica: float = 0.03
    iva_su_provvigione: float = 0.22
    notaio_compravendita_min: float = 1_500.0
    notaio_compravendita_max: float = 2_500.0
    visure_e_relazione_preliminare: float = 300.0
    perizia_tecnico_di_parte: float = 500.0
    allacci_utenze: float = 1_500.0
    accatastamento: float = 800.0

    # Gestione ricorrente, in percentuale sul valore o sul canone.
    manutenzione_ordinaria_su_valore: float = 0.01
    condominio_annuo_tipico: float = 1_200.0
    assicurazione_fabbricato_annua: float = 200.0
    sfitto_su_canone: float = 0.08
    morosita_su_canone: float = 0.03
    gestione_property_manager_su_canone: float = 0.10
    gestione_affitto_breve_su_ricavi: float = 0.20
    costi_variabili_affitto_breve_su_ricavi: float = 0.15

    # Ammortamento della ristrutturazione periodica, secondo l'impostazione usata da
    # Paolo Coletti nel foglio "rendita immobiliare": un rifacimento completo costa
    # circa un terzo del valore dell'immobile e si ripete ogni quarant'anni.
    ristrutturazione_su_valore: float = 1.0 / 3.0
    anni_fra_ristrutturazioni: int = 40


COSTI = CostiAccessori()


# ---------------------------------------------------------------------------
# Assunzioni finanziarie per il confronto con l'alternativa
# ---------------------------------------------------------------------------

@dataclass(frozen=True)
class Finanza:
    """Assunzioni per attualizzare e per confrontare con un portafoglio titoli.

    Il rendimento atteso del portafoglio alternativo serve al confronto fra comprare
    con mutuo e restare in affitto investendo la differenza. Sono assunzioni, non
    previsioni, e vanno dichiarate come tali.
    """

    inflazione_attesa: float = 0.02
    rivalutazione_immobile_reale: float = 0.0
    rendimento_portafoglio_lordo: float = 0.06
    tassazione_rendite_finanziarie: float = 0.26
    tassazione_titoli_di_stato: float = 0.125
    imposta_bollo_titoli: float = 0.002
    tasso_sconto_reale: float = 0.03
    orizzonte_analisi_anni: int = 30


FINANZA = Finanza()


# ---------------------------------------------------------------------------
# Risalite storiche dell'indice dei mutui a tasso variabile
# ---------------------------------------------------------------------------

@dataclass(frozen=True)
class RisaliteEuribor:
    """Le peggiori risalite dell'Euribor a tre mesi contenute nella serie BCE.

    Esistono per sostituire un numero inventato con un numero osservato. Chi
    simula un mutuo a tasso variabile deve scegliere di quanto far salire il tasso,
    e la scelta spontanea e' un punto percentuale, perche' e' l'ordine di grandezza
    che suona prudente. Fra giugno 2022 e giugno 2023 l'Euribor a tre mesi e' salito
    di 3,78 punti in dodici mesi: chi aveva simulato un punto aveva simulato un
    quinto dello scenario che si e' verificato, e la rata che ne e' uscita non era
    quella che aveva dichiarato sostenibile.

    I valori sono in punti percentuali e non in frazioni, come li pubblica la
    fonte. Si rileggono in qualunque momento con `python tools/valuta.py tassi
    --risalita`, che li ricalcola sulla serie corrente e segnala se si sono
    spostati: la scansione e' la stessa di `tassi.risalite_storiche`, quindi il
    confronto e' fra la stessa misura calcolata in due momenti diversi.

    Perche' la finestra e non il massimo assoluto. Il massimo della serie e' il 7,58
    per cento del marzo 1995 e il minimo il meno 0,58 del dicembre 2021: la loro
    differenza sono piu' di otto punti, un numero grande e privo di significato,
    perche' i due estremi distano ventisei anni e nessun piano di ammortamento li
    attraversa nella stessa finestra. Cio' che un mutuo incontra davvero e' la
    peggiore finestra di durata fissata, ed e' quella che questi valori misurano.
    """

    indice: str = "Euribor 3 mesi"
    serie: str = "FM/M.U2.EUR.RT.MM.EURIBOR3MD_.HSTA"
    verificato_il: date = date(2026, 9, 1)
    copertura: str = "1994-01 / 2026-08, 392 osservazioni mensili"
    livello_corrente: float = 2.51
    massimo_storico: float = 7.58
    periodo_massimo: str = "1995-03"
    minimo_storico: float = -0.58
    periodo_minimo: str = "2021-12"
    risalita_12_mesi: float = 3.78
    finestra_12_mesi: str = "2022-06 / 2023-06, da -0,24 a 3,54"
    risalita_24_mesi: float = 4.54
    finestra_24_mesi: str = "2021-11 / 2023-11, da -0,57 a 3,97"
    risalita_36_mesi: float = 4.49
    finestra_36_mesi: str = "2020-11 / 2023-11, da -0,52 a 3,97"


RISALITE_EURIBOR = RisaliteEuribor()


# ---------------------------------------------------------------------------
# Registro delle fonti
# ---------------------------------------------------------------------------

FONTI = {
    "imposte_acquisto": "https://www.agenziaentrate.gov.it/portale/acquisto-di-una-casa-le-imposte",
    "agevolazioni_prima_casa": "https://www.agenziaentrate.gov.it/portale/aree-tematiche/casa/agevolazioni/agevolazioni-per-acquisto-della-prima-casa",
    "locazioni_brevi": "https://www.agenziaentrate.gov.it/portale/le-locazioni-brevi-e-la-cedolare-secca",
    "registrazione_locazione": "https://www.agenziaentrate.gov.it/portale/schede/fabbricatiterreni/registrazione-di-un-nuovo-contratto/quanto-si-paga-regime-ordinario",
    "quotazioni_omi": "https://www.agenziaentrate.gov.it/portale/schede/fabbricatiterreni/omi/banche-dati/quotazioni-immobiliari",
    "omi_open_data": "https://github.com/ondata/quotazioni-immobiliari-agenzia-entrate",
    "prima_casa_due_anni": "https://www.fiscoetasse.com/new-rassegna-stampa/2617-prima-casa-nuovo-termine-di-2-anni-anche-al-credito-dimposta.html",
    "cedolare_2026": "https://www.fiscoetasse.com/new-rassegna-stampa/2970-cedolare-secca-affitti-brevi-le-novita-dal-2026.html",
    "irpef_2026": "https://www.fiscoetasse.com/new-rassegna-stampa/2990-irpef-2026-le-aliquote-di-questanno.html",
    "plusvalenza": "https://biblus.acca.it/plusvalenza-immobiliare/",
    "detrazione_interessi": "https://www.mutuionline.it/guide-mutui/domande-frequenti/detrazione-degli-interessi-del-mutuo-prima-casa-2026-regole-limiti-e-casi-particolari.asp",
    "fondo_consap": "https://www.consap.it/",
    "conformita_pagliai": "https://www.studiotecnicopagliai.it/conformita-catastale-urbanistica-compravendite-immobiliari/",
    "salva_casa_tolleranze": "https://www.studiotecnicopagliai.it/nuove-tolleranze-costruttive-edilizie-col-decreto-salva-casa/",
    "immobili_da_costruire": "https://www.notaiotassitani.it/tutele-acquisto-immobili-da-costruire/",
    "imu_2026": "https://www.immobiliare.it/news/economia/tasse-imposte-e-normative/quali-sono-le-nuove-aliquote-imu-per-il-2026-500307/",
    "tassi_bce": "https://data.ecb.europa.eu/",
    "guida_mutuo_bankitalia": "https://www.bancaditalia.it/pubblicazioni/guide-bi/guida-mutuo/",
    "usura_tegm": "https://www.bancaditalia.it/compiti/vigilanza/compiti-vigilanza/tegm/",
    "lr_marche_turismo": "https://www.consiglio.marche.it/banche_dati_e_documentazione/leggi/",
    "coletti_roi_immobiliare": "https://www.youtube.com/watch?v=6z-jTLyDwUE",
    "coletti_valutazione_investimenti": "https://www.youtube.com/watch?v=YeZREEV2HtY",
    "coletti_rendita": "https://www.paolocoletti.com/wp-content/uploads/youtube/rendita%20immobiliare.xlsx",
    "coletti_casa_o_affitto": "https://www.paolocoletti.com/wp-content/uploads/youtube/acquisto%20casa%20o%20affitto.xlsx",
    "coletti_mutuo_investimento": "https://www.paolocoletti.com/wp-content/uploads/youtube/mutuo_con_investimento.xlsx",
}
