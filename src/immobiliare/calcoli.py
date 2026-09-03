# -*- coding: utf-8 -*-
"""Funzioni di calcolo pure per la valutazione di un immobile residenziale.

Il modulo non conosce Excel e non legge file: prende numeri, restituisce numeri.
Serve a due scopi, tenere il dominio verificabile con i test e produrre il
riepilogo testuale della CLI, mentre il workbook generato da `excel_builder`
replica le stesse regole in formule vive, così che chi apre il file possa
cambiare gli input senza rieseguire Python.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Iterable, Sequence

from . import parametri as P

IMPOSTE_LUSSO = P.IMPOSTE_TRASFERIMENTO.categorie_escluse_prima_casa


# ---------------------------------------------------------------------------
# Descrizione dell'operazione
# ---------------------------------------------------------------------------

@dataclass
class Immobile:
    """Dati dell'immobile e del prezzo trattato."""

    prezzo: float
    rendita_catastale: float = 0.0
    categoria: str = "A/2"
    superficie_mq: float = 0.0
    comune: str = ""
    nuova_costruzione: bool = False
    venditore_impresa: bool = False
    """Vero se si compra da impresa costruttrice con vendita soggetta a IVA.

    L'IVA si applica quando la cessione avviene entro cinque anni dall'ultimazione
    dei lavori, o oltre i cinque anni se l'impresa opta per l'imponibilita' in atto.
    Fuori da questi casi la cessione è esente e si torna all'imposta di registro.
    """


@dataclass
class Acquirente:
    """Posizione soggettiva di chi compra, che determina le agevolazioni."""

    prima_casa: bool = True
    quota: float = 1.0
    """Quota di acquisto, fra 0 e 1. In acquisto congiunto vale 0,5 per ciascuno."""
    residenza_gia_nel_comune: bool = False
    eta: int = 35
    isee: float = 0.0
    reddito_imponibile_irpef: float = 30_000.0
    possiede_altra_prima_casa: bool = False
    prezzo_valore: bool = True
    """Se chiedere al notaio la tassazione sul valore catastale invece che sul prezzo."""


@dataclass
class Finanziamento:
    """Condizioni del mutuo ipotecario."""

    importo: float = 0.0
    tasso_annuo: float = 0.032
    durata_anni: int = 25
    tipo: str = "fisso"
    spread: float = 0.0
    istruttoria: float = 500.0
    perizia: float = 300.0
    polizza_annua: float = 180.0
    notaio_atto_mutuo: float = 1_000.0


@dataclass
class Gestione:
    """Assunzioni sulla gestione dell'immobile quando viene messo a reddito."""

    canone_mensile: float = 0.0
    regime: str = "cedolare_libero"
    """Uno fra cedolare_libero, cedolare_concordato, irpef_ordinario,
    irpef_concordato, breve_prima_unita, breve_altre_unita."""
    mesi_sfitto_annui: float = 1.0
    morosita: float = 0.03
    condominio_annuo: float = 1_200.0
    quota_condominio_a_carico_proprietario: float = 0.4
    manutenzione_su_valore: float = 0.01
    assicurazione_annua: float = 200.0
    aliquota_imu: float = P.IMU.aliquota_base
    gestione_su_canone: float = 0.0
    ricavi_lordi_brevi_annui: float = 0.0
    costi_variabili_brevi: float = P.COSTI.costi_variabili_affitto_breve_su_ricavi


# ---------------------------------------------------------------------------
# Base imponibile e imposte di trasferimento
# ---------------------------------------------------------------------------

def valore_catastale(rendita: float, prima_casa: bool) -> float:
    """Base imponibile del registro con la regola prezzo-valore.

    Rendita rivalutata del cinque per cento, moltiplicata per 110 se l'acquisto è
    agevolato prima casa e per 120 negli altri casi.
    """
    t = P.IMPOSTE_TRASFERIMENTO
    moltiplicatore = t.moltiplicatore_prima_casa if prima_casa else t.moltiplicatore_ordinario
    return rendita * t.rivalutazione_rendita * moltiplicatore


def agevolazione_applicabile(immobile: Immobile, acquirente: Acquirente) -> bool:
    """Vero se l'agevolazione prima casa spetta davvero.

    Non basta che l'acquirente la chieda: le categorie A/1, A/8 e A/9 ne sono escluse
    per definizione, e l'esclusione si riflette anche sul moltiplicatore catastale,
    che torna a centoventi. Tenere la verifica in una funzione sola evita che il
    moltiplicatore e l'aliquota si disallineino, che è il modo tipico in cui questo
    errore si presenta.
    """
    di_lusso = immobile.categoria in IMPOSTE_LUSSO
    return acquirente.prima_casa and not di_lusso


def base_imponibile_registro(immobile: Immobile, acquirente: Acquirente) -> float:
    """Sceglie fra valore catastale e prezzo secondo l'opzione prezzo-valore.

    La regola prezzo-valore vale solo fuori campo IVA e solo se la si chiede in atto;
    senza rendita catastale nota si ripiega sul prezzo, che è il caso peggiore.
    """
    if not acquirente.prezzo_valore or immobile.rendita_catastale <= 0:
        return immobile.prezzo
    return valore_catastale(immobile.rendita_catastale, agevolazione_applicabile(immobile, acquirente))


@dataclass
class ImposteAcquisto:
    """Esito del calcolo delle imposte dovute al rogito."""

    imponibile: float
    iva: float
    registro: float
    ipotecaria: float
    catastale: float
    regime: str

    @property
    def totale(self) -> float:
        return self.iva + self.registro + self.ipotecaria + self.catastale


def imposte_acquisto(immobile: Immobile, acquirente: Acquirente) -> ImposteAcquisto:
    """Imposte dovute al rogito nei quattro casi rilevanti.

    I casi sono la combinazione fra venditore, privato o impresa con IVA, e
    agevolazione, prima casa o ordinaria. Le categorie A/1, A/8 e A/9 sono escluse
    dall'agevolazione per definizione, e in regime IVA scontano il 22%.
    """
    t = P.IMPOSTE_TRASFERIMENTO
    di_lusso = immobile.categoria in t.categorie_escluse_prima_casa
    prima_casa = agevolazione_applicabile(immobile, acquirente)

    if immobile.venditore_impresa:
        if prima_casa:
            aliquota = t.iva_prima_casa
        elif di_lusso:
            aliquota = t.iva_lusso
        else:
            aliquota = t.iva_ordinaria
        # In regime IVA la base è sempre il prezzo pattuito: il prezzo-valore non
        # si applica, perché è una regola dell'imposta di registro.
        return ImposteAcquisto(
            imponibile=immobile.prezzo,
            iva=immobile.prezzo * aliquota,
            registro=t.registro_fisso_da_impresa,
            ipotecaria=t.ipotecaria_da_impresa,
            catastale=t.catastale_da_impresa,
            regime=f"impresa con IVA {aliquota:.0%}",
        )

    imponibile = base_imponibile_registro(immobile, acquirente)
    aliquota = t.registro_prima_casa if prima_casa else t.registro_ordinario
    registro = max(imponibile * aliquota, t.registro_minimo)
    return ImposteAcquisto(
        imponibile=imponibile,
        iva=0.0,
        registro=registro,
        ipotecaria=t.ipotecaria_da_privato,
        catastale=t.catastale_da_privato,
        regime=f"privato, registro {aliquota:.0%}"
        + (" su valore catastale" if imponibile != immobile.prezzo else " su prezzo"),
    )


def provvigione_agenzia(prezzo: float, aliquota: float = P.COSTI.provvigione_agenzia_tipica) -> float:
    """Provvigione di mediazione, IVA inclusa."""
    return prezzo * aliquota * (1 + P.COSTI.iva_su_provvigione)


def imposta_sostitutiva_mutuo(importo: float, prima_casa: bool) -> float:
    """Imposta sostitutiva sul finanziamento, trattenuta dalla banca sull'erogato."""
    m = P.MUTUO
    aliquota = m.imposta_sostitutiva_prima_casa if prima_casa else m.imposta_sostitutiva_ordinaria
    return importo * aliquota


@dataclass
class CostoOperazione:
    """Fabbisogno di cassa complessivo per portare a termine l'acquisto."""

    prezzo: float
    imposte: ImposteAcquisto
    provvigione: float
    notaio_compravendita: float
    notaio_mutuo: float
    sostitutiva_mutuo: float
    istruttoria: float
    perizia: float
    altri_costi: float
    mutuo: float

    @property
    def costi_accessori(self) -> float:
        return (
            self.imposte.totale
            + self.provvigione
            + self.notaio_compravendita
            + self.notaio_mutuo
            + self.sostitutiva_mutuo
            + self.istruttoria
            + self.perizia
            + self.altri_costi
        )

    @property
    def costo_totale(self) -> float:
        """Prezzo più tutti i costi: è il denominatore corretto dei rendimenti."""
        return self.prezzo + self.costi_accessori

    @property
    def esborso_iniziale(self) -> float:
        """Cassa che serve davvero al netto della parte finanziata dalla banca."""
        return self.costo_totale - self.mutuo

    @property
    def incidenza_costi(self) -> float:
        return self.costi_accessori / self.prezzo if self.prezzo else 0.0


def costo_operazione(
    immobile: Immobile,
    acquirente: Acquirente,
    finanziamento: Finanziamento,
    provvigione_pct: float = P.COSTI.provvigione_agenzia_tipica,
    notaio_compravendita: float = 2_000.0,
    altri_costi: float = 0.0,
) -> CostoOperazione:
    """Somma prezzo, imposte e costi accessori dell'operazione."""
    imposte = imposte_acquisto(immobile, acquirente)
    prima_casa = agevolazione_applicabile(immobile, acquirente)
    ha_mutuo = finanziamento.importo > 0
    return CostoOperazione(
        prezzo=immobile.prezzo,
        imposte=imposte,
        provvigione=provvigione_agenzia(immobile.prezzo, provvigione_pct),
        notaio_compravendita=notaio_compravendita,
        notaio_mutuo=finanziamento.notaio_atto_mutuo if ha_mutuo else 0.0,
        sostitutiva_mutuo=imposta_sostitutiva_mutuo(finanziamento.importo, prima_casa) if ha_mutuo else 0.0,
        istruttoria=finanziamento.istruttoria if ha_mutuo else 0.0,
        perizia=finanziamento.perizia if ha_mutuo else 0.0,
        altri_costi=altri_costi,
        mutuo=finanziamento.importo,
    )


# ---------------------------------------------------------------------------
# Mutuo: ammortamento alla francese
# ---------------------------------------------------------------------------

def rata_francese(importo: float, tasso_annuo: float, durata_anni: int, rate_per_anno: int = 12) -> float:
    """Rata costante dell'ammortamento alla francese.

    Con tasso nullo la rata è la semplice divisione del capitale per il numero di
    rate; il caso va isolato perché la formula generale divide per zero.
    """
    n = durata_anni * rate_per_anno
    if n <= 0:
        return 0.0
    i = tasso_annuo / rate_per_anno
    if i == 0:
        return importo / n
    return importo * i / (1 - (1 + i) ** (-n))


@dataclass
class RataAmmortamento:
    numero: int
    anno: int
    quota_interessi: float
    quota_capitale: float
    rata: float
    debito_residuo: float


def piano_ammortamento(
    importo: float, tasso_annuo: float, durata_anni: int, rate_per_anno: int = 12
) -> list[RataAmmortamento]:
    """Piano di ammortamento alla francese, rata per rata."""
    piano: list[RataAmmortamento] = []
    if importo <= 0 or durata_anni <= 0:
        return piano
    rata = rata_francese(importo, tasso_annuo, durata_anni, rate_per_anno)
    i = tasso_annuo / rate_per_anno
    residuo = importo
    for k in range(1, durata_anni * rate_per_anno + 1):
        interessi = residuo * i
        capitale = rata - interessi
        residuo = max(residuo - capitale, 0.0)
        piano.append(
            RataAmmortamento(
                numero=k,
                anno=(k - 1) // rate_per_anno + 1,
                quota_interessi=interessi,
                quota_capitale=capitale,
                rata=rata,
                debito_residuo=residuo,
            )
        )
    return piano


def interessi_per_anno(piano: Sequence[RataAmmortamento]) -> dict[int, float]:
    """Interessi passivi aggregati per anno di ammortamento."""
    somme: dict[int, float] = {}
    for r in piano:
        somme[r.anno] = somme.get(r.anno, 0.0) + r.quota_interessi
    return somme


def detrazione_interessi(interessi_anno: float, quota: float = 1.0, abitazione_principale: bool = True) -> float:
    """Detrazione IRPEF del 19% sugli interessi, entro il massimale di 4.000 euro.

    Il massimale è riferito all'immobile e va ripartito fra i cointestatari del
    mutuo: con due intestatari al cinquanta per cento ciascuno detrae il 19% su
    2.000 euro, non su 4.000. La detrazione spetta solo se l'immobile è adibito ad
    abitazione principale, quindi non spetta sull'immobile comprato per affittarlo.
    """
    if not abitazione_principale:
        return 0.0
    m = P.MUTUO
    massimale = m.detrazione_interessi_massimale * quota
    return min(interessi_anno, massimale) * m.detrazione_interessi_aliquota


def taeg_approssimato(
    importo: float, tasso_annuo: float, durata_anni: int, costi_iniziali: float, costi_annui: float
) -> float:
    """TAEG stimato, come tasso che azzera il valore attuale dei flussi.

    È un'approssimazione dichiarata: il TAEG di legge segue la convenzione della
    Banca d'Italia sull'inclusione delle singole voci, qui si includono i costi
    iniziali e un costo annuo ricorrente ripartito sulle rate.
    """
    n = durata_anni * 12
    if n <= 0 or importo <= 0:
        return 0.0
    rata = rata_francese(importo, tasso_annuo, durata_anni)
    rata_effettiva = rata + costi_annui / 12
    netto_erogato = importo - costi_iniziali
    flussi = [-netto_erogato] + [rata_effettiva] * n
    return tir(flussi) * 12


# ---------------------------------------------------------------------------
# Locazione: canoni e tassazione
# ---------------------------------------------------------------------------

def aliquota_regime(regime: str) -> float:
    """Aliquota di cedolare secca associata al regime, zero per l'IRPEF ordinaria."""
    l = P.LOCAZIONE
    return {
        "cedolare_libero": l.cedolare_libero,
        "cedolare_concordato": l.cedolare_concordato,
        "breve_prima_unita": l.cedolare_breve_prima_unita,
        "breve_altre_unita": l.cedolare_breve_altre_unita,
        "irpef_ordinario": 0.0,
        "irpef_concordato": 0.0,
    }[regime]


def irpef_lorda(imponibile: float) -> float:
    """IRPEF lorda sugli scaglioni 2026."""
    dovuta = 0.0
    precedente = 0.0
    for soglia, aliquota in P.IRPEF.scaglioni:
        if imponibile <= precedente:
            break
        quota = min(imponibile, soglia) - precedente
        dovuta += quota * aliquota
        precedente = soglia
    return dovuta


def imposta_sul_canone(canone_annuo: float, regime: str, reddito_altro: float = 0.0) -> float:
    """Imposta sul reddito da locazione secondo il regime scelto.

    In cedolare secca l'imposta è proporzionale e sostituisce IRPEF, addizionali,
    registro e bollo. In regime ordinario il canone concorre al reddito complessivo
    con l'abbattimento forfettario, e l'imposta è la differenza fra l'IRPEF con e
    senza il canone, così da catturare l'aliquota marginale effettiva.
    """
    l = P.LOCAZIONE
    if regime.startswith("cedolare") or regime.startswith("breve"):
        return canone_annuo * aliquota_regime(regime)

    abbattimento = (
        l.abbattimento_forfettario_concordato
        if regime == "irpef_concordato"
        else l.abbattimento_forfettario_ordinario
    )
    imponibile_canone = canone_annuo * (1 - abbattimento)
    marginale = irpef_lorda(reddito_altro + imponibile_canone) - irpef_lorda(reddito_altro)
    addizionali = imponibile_canone * (
        P.IRPEF.addizionale_regionale_tipica + P.IRPEF.addizionale_comunale_tipica
    )
    registro = max(canone_annuo * l.registro_annuo, l.registro_minimo)
    if regime == "irpef_concordato":
        registro = max(
            canone_annuo * (1 - l.riduzione_base_registro_concordato) * l.registro_annuo,
            l.registro_minimo,
        )
    # L'imposta di registro è dovuta per metà da ciascuna parte, salvo patto.
    return marginale + addizionali + registro / 2


def imu_annua(
    rendita: float,
    aliquota: float = P.IMU.aliquota_base,
    categoria: str = "A/2",
    abitazione_principale: bool = False,
    canone_concordato: bool = False,
    comodato: bool = False,
) -> float:
    """IMU dovuta sull'immobile.

    L'abitazione principale non di lusso è esente. Le riduzioni per canone
    concordato e per comodato si applicano all'imposta e alla base rispettivamente,
    secondo la disciplina vigente.
    """
    di_lusso = categoria in ("A/1", "A/8", "A/9")
    if abitazione_principale and not di_lusso:
        return 0.0
    base = rendita * P.IMU.rivalutazione_rendita * P.IMU.moltiplicatore_gruppo_a
    if comodato:
        base *= P.IMU.riduzione_comodato
    imposta = base * aliquota
    if abitazione_principale and di_lusso:
        imposta = max(base * P.IMU.aliquota_abitazione_principale_lusso - P.IMU.detrazione_abitazione_principale, 0.0)
    elif canone_concordato:
        imposta *= P.IMU.riduzione_canone_concordato
    return imposta


@dataclass
class ContoEconomico:
    """Conto economico annuo dell'immobile messo a reddito."""

    canone_potenziale: float
    perdita_sfitto: float
    perdita_morosita: float
    condominio: float
    manutenzione: float
    assicurazione: float
    imu: float
    gestione: float
    imposta: float
    ristrutturazione: float = 0.0
    """Accantonamento annuo per la ristrutturazione di fine ciclo. Vedi ADR-005:
    è un costo ricorrente, non un evento futuro da tenere fuori dal rendimento."""

    @property
    def canone_effettivo(self) -> float:
        return self.canone_potenziale - self.perdita_sfitto - self.perdita_morosita

    @property
    def costi_operativi(self) -> float:
        return (
            self.condominio + self.manutenzione + self.assicurazione
            + self.imu + self.gestione + self.ristrutturazione
        )

    @property
    def noi(self) -> float:
        """Net operating income, prima delle imposte sul reddito e del mutuo."""
        return self.canone_effettivo - self.costi_operativi

    @property
    def utile_netto(self) -> float:
        return self.noi - self.imposta


def conto_economico(immobile: Immobile, gestione: Gestione, reddito_altro: float = 0.0) -> ContoEconomico:
    """Costruisce il conto economico annuo a partire dalle assunzioni di gestione."""
    breve = gestione.regime.startswith("breve")
    if breve:
        potenziale = gestione.ricavi_lordi_brevi_annui
        sfitto = 0.0
        morosita = 0.0
        gestione_costo = potenziale * (gestione.gestione_su_canone + gestione.costi_variabili_brevi)
    else:
        potenziale = gestione.canone_mensile * 12
        sfitto = gestione.canone_mensile * gestione.mesi_sfitto_annui
        morosita = (potenziale - sfitto) * gestione.morosita
        gestione_costo = (potenziale - sfitto - morosita) * gestione.gestione_su_canone

    effettivo = potenziale - sfitto - morosita
    concordato = "concordato" in gestione.regime
    return ContoEconomico(
        canone_potenziale=potenziale,
        perdita_sfitto=sfitto,
        perdita_morosita=morosita,
        condominio=gestione.condominio_annuo * gestione.quota_condominio_a_carico_proprietario,
        manutenzione=immobile.prezzo * gestione.manutenzione_su_valore,
        assicurazione=gestione.assicurazione_annua,
        imu=imu_annua(
            immobile.rendita_catastale,
            gestione.aliquota_imu,
            immobile.categoria,
            abitazione_principale=False,
            canone_concordato=concordato,
        ),
        gestione=gestione_costo,
        imposta=imposta_sul_canone(effettivo, gestione.regime, reddito_altro),
        ristrutturazione=immobile.prezzo * P.COSTI.ristrutturazione_su_valore / P.COSTI.anni_fra_ristrutturazioni,
    )


# ---------------------------------------------------------------------------
# Metriche di rendimento
# ---------------------------------------------------------------------------

def tir(flussi: Sequence[float], tolleranza: float = 1e-7, iterazioni: int = 200) -> float:
    """Tasso interno di rendimento, per bisezione su un intervallo ampio.

    La bisezione è preferita a Newton perché non diverge sui flussi immobiliari,
    dove il primo termine è un esborso grande e i successivi sono piccoli e di segno
    costante. Restituisce zero se non esiste un cambio di segno nell'intervallo.
    """
    def van(tasso: float) -> float:
        return sum(f / (1 + tasso) ** k for k, f in enumerate(flussi))

    basso, alto = -0.9999, 10.0
    v_basso, v_alto = van(basso), van(alto)
    if v_basso * v_alto > 0:
        return 0.0
    for _ in range(iterazioni):
        medio = (basso + alto) / 2
        v_medio = van(medio)
        if abs(v_medio) < tolleranza:
            return medio
        if v_basso * v_medio < 0:
            alto, v_alto = medio, v_medio
        else:
            basso, v_basso = medio, v_medio
    return (basso + alto) / 2


def van(flussi: Sequence[float], tasso: float) -> float:
    """Valore attuale netto della serie di flussi al tasso indicato."""
    return sum(f / (1 + tasso) ** k for k, f in enumerate(flussi))


@dataclass
class Metriche:
    """Indicatori sintetici dell'investimento."""

    rendimento_lordo: float
    rendimento_netto: float
    cap_rate: float
    cash_on_cash: float
    dscr: float
    cash_flow_annuo: float
    payback_anni: float


def metriche(
    costo: CostoOperazione,
    conto: ContoEconomico,
    rata_annua: float,
) -> Metriche:
    """Indicatori calcolati sul costo totale, non sul solo prezzo.

    La distinzione è sostanziale: usare il prezzo come denominatore gonfia il
    rendimento del dieci-quindici per cento, perché ignora imposte, notaio e
    provvigione, che sono capitale immobilizzato a tutti gli effetti.
    """
    cash_flow = conto.utile_netto - rata_annua
    return Metriche(
        rendimento_lordo=conto.canone_potenziale / costo.prezzo if costo.prezzo else 0.0,
        rendimento_netto=conto.utile_netto / costo.costo_totale if costo.costo_totale else 0.0,
        cap_rate=conto.noi / costo.costo_totale if costo.costo_totale else 0.0,
        cash_on_cash=cash_flow / costo.esborso_iniziale if costo.esborso_iniziale else 0.0,
        dscr=conto.noi / rata_annua if rata_annua else float("inf"),
        cash_flow_annuo=cash_flow,
        payback_anni=costo.esborso_iniziale / cash_flow if cash_flow > 0 else float("inf"),
    )


# ---------------------------------------------------------------------------
# Effetto dell'inflazione: dal rendimento nominale a quello reale
# ---------------------------------------------------------------------------

def tasso_reale(tasso_nominale: float, inflazione: float) -> float:
    """Tasso reale esatto, per l'equazione di Fisher: (1+r)/(1+i)-1.

    La forma che si vede scritta quasi sempre è la sottrazione, cioè r meno i,
    e non è la definizione: è la sua approssimazione al primo ordine. Le due
    coincidono solo nel limite di tassi piccoli, perché la differenza fra loro
    vale i*(1+r_reale)/(1+i) circa, quindi cresce col prodotto dei due tassi.

    Sui numeri di questo dominio la differenza non è trascurabile come sembra.
    Con un rendimento nominale del cinque per cento e un'inflazione del due, la
    sottrazione da' il tre per cento e la formula esatta il 2,94: sei centesimi
    di punto, cioè il due per cento del rendimento reale stesso. Su venticinque
    anni di capitalizzazione quella differenza si compone e sposta il montante
    finale di alcuni punti percentuali. Il modello usa quindi sempre la forma
    esatta, e mostra accanto l'errore che si commetterebbe con l'altra, perché
    la sottrazione resta utile per il conto a mente e va saputa per quello che è.

    La ragione per cui la forma esatta è quella giusta si vede scrivendo cosa
    significa un rendimento reale: è il rapporto fra il potere d'acquisto finale
    e quello iniziale. Un euro investito diventa (1+r) euro nominali, che al
    livello dei prezzi finale comprano (1+r)/(1+i) volte quello che comprava un
    euro all'inizio. Il rendimento reale è quel rapporto meno uno, per
    definizione e non per approssimazione.
    """
    if inflazione <= -1:
        raise ValueError("inflazione non ammissibile: renderebbe nullo il livello dei prezzi")
    return (1 + tasso_nominale) / (1 + inflazione) - 1


def deflaziona(valore_nominale: float, inflazione: float, anni: float) -> float:
    """Riporta un importo futuro al potere d'acquisto di oggi.

    È l'operazione che distingue un patrimonio finale da un patrimonio finale
    utilizzabile. Duecentomila euro fra venticinque anni con un'inflazione del
    due per cento comprano quello che oggi comprano circa centoventiduemila: la
    differenza non è una perdita contabile, è potere d'acquisto che non c'è.
    """
    return valore_nominale / (1 + inflazione) ** anni


def fattore_rendita_crescente(crescita: float, sconto: float, anni: int) -> float:
    """Valore attuale di una rendita unitaria che cresce a tasso costante.

    La rendita paga 1 al primo anno, (1+g) al secondo, (1+g)^(n-1) all'ultimo, e
    ogni pagamento si attualizza al tasso s. La somma vale

        F = somma per k da 1 a n di (1+g)^(k-1) / (1+s)^k

    ed è una serie geometrica di ragione q = (1+g)/(1+s), che si chiude in

        F = q * (1 - q^n) / ((1+g) * (1 - q))

    La forma chiusa esiste per una ragione pratica e non estetica: la stessa
    grandezza serve dentro il workbook, dove una somma su n termini con n
    variabile richiederebbe una formula matriciale oppure una colonna di
    appoggio, e nessuna delle due è ispezionabile come una cella singola. Il
    workbook usa quindi la forma chiusa, questo modulo tiene anche la somma
    esplicita in `effetto_inflazione`, e un test verifica che coincidano: è la
    doppia implementazione applicata a una formula invece che a un modello.

    Il caso q uguale a uno, cioè crescita pari al tasso di sconto, annulla il
    denominatore e va trattato a parte: allora ogni termine vale 1/(1+g) e la
    somma è n/(1+g). Non è un caso di scuola, perché assumere una crescita del
    canone pari al tasso di sconto reale è un'ipotesi che qualcuno fa davvero.
    """
    if sconto <= -1 or crescita <= -1:
        raise ValueError("tassi non ammissibili")
    q = (1 + crescita) / (1 + sconto)
    if abs(q - 1) < 1e-12:
        return anni / (1 + crescita)
    return q * (1 - q ** anni) / ((1 + crescita) * (1 - q))


@dataclass
class EffettoInflazione:
    """Che cosa fa l'inflazione a questa operazione, voce per voce.

    Il risultato interessante è che l'inflazione non agisce nella stessa
    direzione su tutte le componenti, e in un acquisto a leva le direzioni si
    compensano solo in parte. Il debito è nominale, quindi l'inflazione lo
    erode a favore di chi lo ha contratto; la rata di un mutuo a tasso fisso è
    nominale, quindi si alleggerisce in termini reali anno dopo anno; il canone
    è indicizzabile solo in parte e solo in alcuni regimi, quindi perde terreno;
    l'immobile si rivaluta nominalmente, e in termini reali solo se la
    rivalutazione supera l'inflazione, cosa che nel mercato residenziale italiano
    degli ultimi vent'anni non è accaduta.
    """

    inflazione: float
    rendimento_netto_nominale: float
    rendimento_netto_reale: float
    errore_approssimazione: float
    """Quanto sbaglia la sottrazione r meno i rispetto alla formula esatta."""
    erosione_reale_canone: float
    """Variazione reale annua del canone: negativa se l'indicizzazione non copre l'inflazione."""
    rivalutazione_reale_immobile: float
    tir_nominale: float
    tir_reale: float
    valore_finale_nominale: float
    valore_finale_reale: float
    debito_residuo_nominale: float
    debito_residuo_reale: float
    sconto_inflazione_sul_debito: float
    """Quanto vale, in euro di oggi, l'erosione del debito operata dall'inflazione."""
    rata_annua_reale_a_fine_orizzonte: float
    canone_perso_per_mancata_indicizzazione: float
    """Valore attuale del canone a cui si rinuncia non indicizzando, sull'orizzonte."""


def effetto_inflazione(
    inflazione: float,
    rendimento_netto_nominale: float,
    tir_nominale: float,
    prezzo: float,
    rivalutazione_immobile: float,
    debito_residuo_nominale: float,
    rata_annua: float,
    canone_annuo: float,
    indicizzazione_canone: float,
    orizzonte_anni: int,
    tasso_sconto: float,
) -> EffettoInflazione:
    """Scompone l'effetto dell'inflazione sulle grandezze dell'operazione.

    Sull'ultima voce vale una nota, perché quantifica una scelta fiscale che di
    solito si fa guardando solo l'aliquota. La cedolare secca sostituisce
    l'IRPEF sul canone con un'aliquota fissa, ed è quasi sempre conveniente sul
    breve; in cambio, per l'articolo 3 comma 11 del d.lgs. 23/2011, chi la opta
    rinuncia per la durata dell'opzione all'aggiornamento ISTAT del canone. Su un
    contratto quattro più quattro con un'inflazione del due per cento, la
    rinuncia costa un canone che a fine periodo vale in termini reali il quindici
    per cento in meno, e su un orizzonte di venticinque anni la somma attualizzata
    di quel mancato aggiornamento è confrontabile con il risparmio d'imposta che
    l'aveva motivata. Il modello calcola l'una e l'altra grandezza e lascia il
    confronto a chi decide, perché dipende dall'aliquota marginale personale.
    """
    reale = tasso_reale(rendimento_netto_nominale, inflazione)
    valore_finale = prezzo * (1 + rivalutazione_immobile) ** orizzonte_anni
    debito_reale = deflaziona(debito_residuo_nominale, inflazione, orizzonte_anni)

    # Il canone perso: differenza fra un canone indicizzato all'inflazione piena
    # e quello indicizzato come dichiarato, attualizzata al tasso di sconto.
    perso = 0.0
    for anno in range(1, orizzonte_anni + 1):
        pieno = canone_annuo * (1 + inflazione) ** (anno - 1)
        effettivo = canone_annuo * (1 + indicizzazione_canone) ** (anno - 1)
        perso += (pieno - effettivo) / (1 + tasso_sconto) ** anno

    return EffettoInflazione(
        inflazione=inflazione,
        rendimento_netto_nominale=rendimento_netto_nominale,
        rendimento_netto_reale=reale,
        errore_approssimazione=(rendimento_netto_nominale - inflazione) - reale,
        erosione_reale_canone=tasso_reale(indicizzazione_canone, inflazione),
        rivalutazione_reale_immobile=tasso_reale(rivalutazione_immobile, inflazione),
        tir_nominale=tir_nominale,
        tir_reale=tasso_reale(tir_nominale, inflazione),
        valore_finale_nominale=valore_finale,
        valore_finale_reale=deflaziona(valore_finale, inflazione, orizzonte_anni),
        debito_residuo_nominale=debito_residuo_nominale,
        debito_residuo_reale=debito_reale,
        sconto_inflazione_sul_debito=debito_residuo_nominale - debito_reale,
        rata_annua_reale_a_fine_orizzonte=deflaziona(rata_annua, inflazione, orizzonte_anni),
        canone_perso_per_mancata_indicizzazione=perso,
    )


def plusvalenza_su_rivendita(
    prezzo_vendita: float,
    costo_acquisto: float,
    anni_possesso: float,
    abitazione_principale: bool = False,
    superbonus: bool = False,
) -> tuple[float, float]:
    """Plusvalenza e imposta sostitutiva dovuta in caso di rivendita.

    Restituisce la coppia plusvalenza lorda e imposta. L'imponibilita' decade oltre
    i cinque anni, o oltre i dieci per gli immobili con superbonus, e non scatta se
    l'immobile è stato abitazione principale per la maggior parte del periodo.
    """
    p = P.PLUSVALENZA
    plus = max(prezzo_vendita - costo_acquisto, 0.0)
    soglia = p.anni_imponibilita_superbonus if superbonus else p.anni_imponibilita_ordinaria
    if anni_possesso >= soglia or abitazione_principale:
        return plus, 0.0
    return plus, plus * p.imposta_sostitutiva


# ---------------------------------------------------------------------------
# Confronto fra comprare e restare in affitto investendo la differenza
# ---------------------------------------------------------------------------

@dataclass
class EsitoConfronto:
    patrimonio_comprando: float
    patrimonio_affittando: float

    @property
    def differenza(self) -> float:
        return self.patrimonio_comprando - self.patrimonio_affittando

    @property
    def conviene_comprare(self) -> bool:
        return self.differenza > 0


def confronto_compra_o_affitta(
    costo: CostoOperazione,
    finanziamento: Finanziamento,
    canone_alternativo_mensile: float,
    anni: int,
    rivalutazione_immobile: float = P.FINANZA.inflazione_attesa,
    rendimento_portafoglio: float = P.FINANZA.rendimento_portafoglio_lordo,
    tassazione_portafoglio: float = P.FINANZA.tassazione_rendite_finanziarie,
    costi_ricorrenti_proprietario: float = 0.0,
    inflazione_canone: float = P.FINANZA.inflazione_attesa,
) -> EsitoConfronto:
    """Confronta il patrimonio finale nei due scenari, a parità di esborso.

    L'impostazione riprende quella dei fogli di Paolo Coletti: chi compra immobilizza
    l'anticipo e paga rata e costi ricorrenti, chi affitta investe l'anticipo e ogni
    anno investe o disinveste la differenza fra quanto avrebbe speso comprando e
    quanto spende in affitto. Alla fine si confrontano il valore dell'immobile al
    netto del debito residuo e il valore del portafoglio al netto dell'imposta sul
    capital gain.
    """
    rata_mensile = rata_francese(finanziamento.importo, finanziamento.tasso_annuo, finanziamento.durata_anni)
    piano = piano_ammortamento(finanziamento.importo, finanziamento.tasso_annuo, finanziamento.durata_anni)

    valore_immobile = costo.prezzo * (1 + rivalutazione_immobile) ** anni
    rate_pagate = min(anni * 12, len(piano))
    debito_residuo = piano[rate_pagate - 1].debito_residuo if rate_pagate else finanziamento.importo
    patrimonio_comprando = valore_immobile - debito_residuo

    # Chi affitta parte investendo l'anticipo che l'altro ha immobilizzato.
    portafoglio = costo.esborso_iniziale
    versato = costo.esborso_iniziale
    canone = canone_alternativo_mensile * 12
    for anno in range(1, anni + 1):
        uscita_proprietario = (rata_mensile * 12 if anno * 12 <= len(piano) else 0.0) + costi_ricorrenti_proprietario
        differenza = uscita_proprietario - canone
        portafoglio = portafoglio * (1 + rendimento_portafoglio) + differenza
        versato += differenza
        canone *= 1 + inflazione_canone

    guadagno = max(portafoglio - versato, 0.0)
    patrimonio_affittando = portafoglio - guadagno * tassazione_portafoglio
    return EsitoConfronto(patrimonio_comprando, patrimonio_affittando)
