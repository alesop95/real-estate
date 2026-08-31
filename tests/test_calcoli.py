# -*- coding: utf-8 -*-
"""Test del motore di calcolo.

Congelano il caso di riferimento descritto in `.claude/context/dev-testing.md` e le
verifiche di dominio che intercettano gli errori piu' probabili: scaglioni rimasti
a un'annualita' precedente, minimo di legge dell'imposta di registro ignorato,
prezzo-valore applicato dove non spetta, detrazione concessa dove non spetta.

Si eseguono con `python -m pytest tests` dalla radice del progetto, oppure con
`python tests/test_calcoli.py` se pytest non e' installato.
"""

from __future__ import annotations

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "src"))

from immobiliare import calcoli as C  # noqa: E402
from immobiliare import omi as O  # noqa: E402
from immobiliare import parametri as P  # noqa: E402


def caso_di_riferimento():
    immobile = C.Immobile(
        prezzo=120_000, rendita_catastale=450, categoria="A/3",
        superficie_mq=55, comune="Comune di esempio",
    )
    acquirente = C.Acquirente(prima_casa=True, prezzo_valore=True, reddito_imponibile_irpef=32_000)
    finanziamento = C.Finanziamento(importo=90_000, tasso_annuo=0.032, durata_anni=25)
    return immobile, acquirente, finanziamento


# --- base imponibile e imposte -------------------------------------------

def test_valore_catastale_prima_casa():
    # 450 * 1,05 * 110
    assert C.valore_catastale(450, prima_casa=True) == 51_975.0


def test_valore_catastale_seconda_casa():
    # 450 * 1,05 * 120
    assert C.valore_catastale(450, prima_casa=False) == 56_700.0


def test_prezzo_valore_abbassa_la_base():
    immobile, acquirente, _ = caso_di_riferimento()
    assert C.base_imponibile_registro(immobile, acquirente) == 51_975.0
    acquirente.prezzo_valore = False
    assert C.base_imponibile_registro(immobile, acquirente) == 120_000


def test_prezzo_valore_non_si_applica_con_iva():
    """Il prezzo-valore e' una regola dell'imposta di registro: con l'IVA la base
    resta il prezzo, e applicarlo comunque sottostimerebbe l'imposta."""
    immobile, acquirente, _ = caso_di_riferimento()
    immobile.venditore_impresa = True
    imposte = C.imposte_acquisto(immobile, acquirente)
    assert imposte.imponibile == 120_000
    assert imposte.iva == 120_000 * P.IMPOSTE_TRASFERIMENTO.iva_prima_casa


def test_imposte_da_privato_prima_casa():
    immobile, acquirente, _ = caso_di_riferimento()
    imposte = C.imposte_acquisto(immobile, acquirente)
    assert imposte.registro == 51_975.0 * 0.02
    assert imposte.ipotecaria == 50 and imposte.catastale == 50
    assert imposte.iva == 0
    assert round(imposte.totale, 2) == 1_139.50


def test_minimo_di_legge_del_registro():
    """Su rendite basse il minimo di mille euro diventa vincolante."""
    immobile = C.Immobile(prezzo=30_000, rendita_catastale=150, categoria="A/4")
    acquirente = C.Acquirente(prima_casa=True, prezzo_valore=True)
    imposte = C.imposte_acquisto(immobile, acquirente)
    assert imposte.registro == P.IMPOSTE_TRASFERIMENTO.registro_minimo


def test_categoria_di_lusso_esclusa_dall_agevolazione():
    immobile = C.Immobile(prezzo=500_000, rendita_catastale=3_000, categoria="A/8")
    acquirente = C.Acquirente(prima_casa=True, prezzo_valore=True)
    imposte = C.imposte_acquisto(immobile, acquirente)
    # Il moltiplicatore torna a 120 e l'aliquota al 9 per cento.
    assert imposte.imponibile == 3_000 * 1.05 * 120
    assert imposte.registro == imposte.imponibile * P.IMPOSTE_TRASFERIMENTO.registro_ordinario


def test_lusso_con_iva_sconta_aliquota_ordinaria_massima():
    immobile = C.Immobile(prezzo=500_000, rendita_catastale=3_000, categoria="A/1", venditore_impresa=True)
    imposte = C.imposte_acquisto(immobile, C.Acquirente(prima_casa=True))
    assert imposte.iva == 500_000 * P.IMPOSTE_TRASFERIMENTO.iva_lusso


# --- costo complessivo -----------------------------------------------------

def test_costo_operazione_caso_di_riferimento():
    immobile, acquirente, finanziamento = caso_di_riferimento()
    costo = C.costo_operazione(immobile, acquirente, finanziamento, altri_costi=2_000)
    # I valori cadono su mezzo euro esatto, dove l'arrotondamento di Python va al
    # pari e quello di Excel va per eccesso: si confronta con tolleranza.
    assert abs(costo.costi_accessori - 11_556.50) < 0.01
    assert abs(costo.costo_totale - 131_556.50) < 0.01
    assert abs(costo.esborso_iniziale - 41_556.50) < 0.01
    assert round(costo.incidenza_costi, 4) == 0.0963


def test_imposta_sostitutiva_ottuplica_senza_prima_casa():
    assert C.imposta_sostitutiva_mutuo(90_000, prima_casa=True) == 225.0
    assert C.imposta_sostitutiva_mutuo(90_000, prima_casa=False) == 1_800.0


# --- mutuo ------------------------------------------------------------------

def test_rata_francese():
    assert round(C.rata_francese(90_000, 0.032, 25), 2) == 436.21


def test_rata_a_tasso_nullo():
    """Il caso va isolato perche' la formula generale dividerebbe per zero."""
    assert C.rata_francese(120_000, 0.0, 10) == 1_000.0


def test_piano_ammortamento_estingue_il_debito():
    piano = C.piano_ammortamento(90_000, 0.032, 25)
    assert len(piano) == 300
    assert round(piano[-1].debito_residuo, 2) == 0.0
    assert round(sum(r.quota_capitale for r in piano), 0) == 90_000


def test_detrazione_interessi_solo_su_abitazione_principale():
    piano = C.piano_ammortamento(90_000, 0.032, 25)
    interessi = C.interessi_per_anno(piano)[1]
    assert round(C.detrazione_interessi(interessi, 1.0, True), 2) == round(interessi * 0.19, 2)
    assert C.detrazione_interessi(interessi, 1.0, False) == 0.0


def test_massimale_detrazione_scala_con_la_quota():
    """Il massimale e' riferito all'immobile, non alla persona: con due
    cointestatari al cinquanta per cento ciascuno detrae su duemila euro."""
    assert C.detrazione_interessi(10_000, quota=1.0) == 4_000 * 0.19
    assert C.detrazione_interessi(10_000, quota=0.5) == 2_000 * 0.19


# --- IRPEF ------------------------------------------------------------------

def test_scaglioni_irpef_2026():
    # 28.000 al 23 per cento piu' 2.000 al 33 per cento
    assert C.irpef_lorda(30_000) == 7_100.0
    assert C.irpef_lorda(28_000) == 6_440.0
    # oltre i 50.000 entra il terzo scaglione al 43 per cento
    assert C.irpef_lorda(60_000) == 6_440.0 + 22_000 * 0.33 + 10_000 * 0.43


# --- locazione --------------------------------------------------------------

def test_cedolare_sostituisce_il_registro():
    assert C.imposta_sul_canone(6_000, "cedolare_libero") == 6_000 * 0.21
    assert C.imposta_sul_canone(6_000, "cedolare_concordato") == 6_000 * 0.10


def test_locazione_breve_prima_e_altre_unita():
    assert C.imposta_sul_canone(9_000, "breve_prima_unita") == 9_000 * 0.21
    assert C.imposta_sul_canone(9_000, "breve_altre_unita") == 9_000 * 0.26


def test_irpef_ordinaria_include_registro_e_addizionali():
    imposta = C.imposta_sul_canone(6_000, "irpef_ordinario", reddito_altro=32_000)
    # Marginale al 33 per cento sul 95 per cento, piu' addizionali, piu' meta' registro.
    atteso = 6_000 * 0.95 * 0.33 + 6_000 * 0.95 * (P.IRPEF.addizionale_regionale_tipica + P.IRPEF.addizionale_comunale_tipica) + max(6_000 * 0.02, 67) / 2
    assert round(imposta, 2) == round(atteso, 2)


def test_imu_esente_su_abitazione_principale_non_di_lusso():
    assert C.imu_annua(450, categoria="A/3", abitazione_principale=True) == 0.0


def test_imu_dovuta_su_immobile_locato():
    atteso = 450 * 1.05 * 160 * P.IMU.aliquota_base
    assert round(C.imu_annua(450, categoria="A/3"), 2) == round(atteso, 2)


def test_imu_ridotta_con_canone_concordato():
    piena = C.imu_annua(450, categoria="A/3")
    ridotta = C.imu_annua(450, categoria="A/3", canone_concordato=True)
    assert round(ridotta, 2) == round(piena * 0.75, 2)


def test_accantonamento_ristrutturazione_nel_conto_economico():
    """Un rifacimento completo ogni quarant'anni, ripartito. Vedi ADR-005: senza,
    il rendimento netto risulta piu' che doppio di quello vero."""
    immobile, _, _ = caso_di_riferimento()
    conto = C.conto_economico(immobile, C.Gestione(canone_mensile=500, regime="cedolare_libero"))
    assert round(conto.ristrutturazione, 2) == round(120_000 / 3 / 40, 2)
    assert conto.ristrutturazione in [c for c in (conto.costi_operativi,)] or conto.costi_operativi > conto.ristrutturazione


def test_sfitto_e_morosita_sottratti_prima_dell_imposta():
    immobile, _, _ = caso_di_riferimento()
    gestione = C.Gestione(canone_mensile=500, regime="cedolare_libero", mesi_sfitto_annui=1, morosita=0.03)
    conto = C.conto_economico(immobile, gestione)
    assert conto.canone_potenziale == 6_000
    assert conto.perdita_sfitto == 500
    assert round(conto.perdita_morosita, 2) == round(5_500 * 0.03, 2)
    assert round(conto.imposta, 2) == round(conto.canone_effettivo * 0.21, 2)


# --- metriche ---------------------------------------------------------------

def test_metriche_caso_di_riferimento():
    immobile, acquirente, finanziamento = caso_di_riferimento()
    costo = C.costo_operazione(immobile, acquirente, finanziamento, altri_costi=2_000)
    gestione = C.Gestione(canone_mensile=500, regime="cedolare_libero", mesi_sfitto_annui=1)
    conto = C.conto_economico(immobile, gestione)
    rata = C.rata_francese(90_000, 0.032, 25) * 12
    m = C.metriche(costo, conto, rata)
    assert round(m.rendimento_lordo, 4) == 0.05
    assert round(m.rendimento_netto, 4) == 0.0052
    assert round(m.cap_rate, 4) == 0.0137
    assert round(m.cash_on_cash, 4) == -0.1095
    assert round(m.dscr, 2) == 0.34
    assert round(m.cash_flow_annuo, 0) == -4_550
    assert m.cash_flow_annuo < 0
    assert m.payback_anni == float("inf")


def test_tir_su_flussi_noti():
    """Cento investiti che rendono dieci l'anno per sempre e restituiscono il
    capitale valgono il dieci per cento."""
    flussi = [-100.0] + [10.0] * 29 + [110.0]
    assert round(C.tir(flussi), 4) == 0.10


def test_tir_nullo_se_non_c_e_cambio_di_segno():
    assert C.tir([-100.0, -10.0, -10.0]) == 0.0


def test_van_coerente_col_tir():
    flussi = [-100.0] + [10.0] * 29 + [110.0]
    assert abs(C.van(flussi, C.tir(flussi))) < 1e-4


# --- plusvalenza ------------------------------------------------------------

def test_plusvalenza_imponibile_dentro_il_quinquennio():
    plus, imposta = C.plusvalenza_su_rivendita(150_000, 130_000, anni_possesso=3)
    assert plus == 20_000
    assert imposta == 20_000 * 0.26


def test_plusvalenza_non_imponibile_oltre_il_quinquennio():
    _, imposta = C.plusvalenza_su_rivendita(150_000, 130_000, anni_possesso=6)
    assert imposta == 0.0


def test_plusvalenza_non_imponibile_se_abitazione_principale():
    _, imposta = C.plusvalenza_su_rivendita(150_000, 130_000, anni_possesso=2, abitazione_principale=True)
    assert imposta == 0.0


def test_finestra_decennale_con_superbonus():
    _, imposta = C.plusvalenza_su_rivendita(150_000, 130_000, anni_possesso=7, superbonus=True)
    assert imposta == 20_000 * 0.26


# --- confronto --------------------------------------------------------------

def test_confronto_reagisce_al_rendimento_del_portafoglio():
    """Alzando il rendimento atteso del portafoglio l'alternativa migliora: se non
    lo facesse, il confronto non starebbe misurando quello che dichiara."""
    immobile, acquirente, finanziamento = caso_di_riferimento()
    costo = C.costo_operazione(immobile, acquirente, finanziamento)
    basso = C.confronto_compra_o_affitta(costo, finanziamento, 550, 20, rendimento_portafoglio=0.02)
    alto = C.confronto_compra_o_affitta(costo, finanziamento, 550, 20, rendimento_portafoglio=0.08)
    assert alto.patrimonio_affittando > basso.patrimonio_affittando
    assert alto.differenza < basso.differenza


def test_omi_legge_la_fornitura_in_codifica_ansi():
    """La fornitura ufficiale non e' UTF-8, e leggerla male non solleva errori.

    Il mirror open data pubblica file gia' in UTF-8; la fornitura scaricata
    dall'area riservata arriva nella codifica ANSI di Windows. Decodificarla come
    UTF-8 sostituendo i caratteri illeciti non fallisce: mette il segnaposto di
    rimpiazzo al posto di ogni accento, il file si carica, le quotazioni si
    calcolano, e un Comune accentato diventa irreperibile alla ricerca per nome.
    E' il modello di difetto che produce un risultato plausibile invece di un
    errore, cioe' quello contro cui vale la pena scrivere un test.
    """
    import tempfile

    accentato = "FORL" + chr(0x00CC)
    righe = [
        "QUOTAZIONI IMMOBILIARI - Anno 2026 Semestre 1;;;;;;;;;",
        "Area_territoriale;Regione;Prov;Comune_ISTAT;Comune_cat;Comune_amm;"
        "Comune_descrizione;Fascia;Zona;Cod_tip;Descr_Tipologia;Stato;"
        "Compr_min;Compr_max;Loc_min;Loc_max",
        "NORD-EST;EMILIA ROMAGNA;FC;040012;D704;0;" + accentato + ";B;B1;20;"
        "Abitazioni civili;NORMALE;1.400;1.900;4,5;6,5",
    ]
    percorso = Path(tempfile.gettempdir()) / "omi-fornitura-ansi.csv"
    percorso.write_bytes(chr(10).join(righe).encode("cp1252"))

    quotazioni = O.carica(percorso)
    assert len(quotazioni) == 1
    assert quotazioni[0].comune == accentato, "il nome del Comune e' stato corrotto in lettura"
    assert chr(0xFFFD) not in quotazioni[0].comune

    # Il separatore decimale italiano e il punto delle migliaia vanno interpretati.
    assert quotazioni[0].compravendita_min == 1_400
    assert quotazioni[0].locazione_max == 6.5

    # E il Comune deve restare raggiungibile dalla ricerca per nome.
    assert len(O.cerca(quotazioni, comune=accentato)) == 1

def test_indicatori_degradano_senza_rete():
    """Il contratto del modulo e' che una fonte irraggiungibile non propaghi.

    Tutte le funzioni di rete del progetto devono fallire con l'eccezione di
    dominio, mai con quella del socket, altrimenti il comando cade invece di
    degradare. Il caso insidioso e' `TimeoutError`, che non discende da
    `URLError`: una cattura scritta sulla sola `URLError` sembra corretta e
    lascia passare proprio il fallimento piu' frequente.
    """
    import urllib.error
    import urllib.request

    from immobiliare import indicatori as N

    originale = urllib.request.urlopen
    for eccezione in (TimeoutError("read timed out"),
                      urllib.error.URLError("nessuna rete"),
                      OSError("connessione rifiutata")):
        def esplode(*a, **k):
            raise eccezione
        urllib.request.urlopen = esplode
        try:
            for chiamata in (N.estr, N.hicp, N.nic_istat, N.quadro):
                if chiamata is N.quadro:
                    # `quadro` assorbe tutto e restituisce cio' che ha raccolto.
                    assert chiamata() == []
                else:
                    try:
                        chiamata()
                        raise AssertionError(f"{chiamata.__name__} non ha sollevato nulla")
                    except N.IndicatoriNonDisponibili:
                        pass
        finally:
            urllib.request.urlopen = originale


def test_misure_nic_coprono_indice_e_variazioni():
    """La mappa delle misure e' il punto in cui il flusso ISTAT diventa leggibile.

    I codici della dimensione MEASURE sono numeri senza significato finche' non
    li si traduce, e la traduzione e' stata verificata sui valori: a dicembre
    2025 la misura 7 vale 1,2 per cento e coincide con l'indice armonizzato
    Italia dello stesso mese letto dalla BCE. Se la mappa perde una voce, il
    comando stampa un'etichetta generica invece di dire quale sia l'inflazione.
    """
    from immobiliare import indicatori as N

    assert set(N.MISURE_NIC) >= {"4", "6", "7"}
    assert N.MISURE_NIC["7"][0] == "tendenziale"
    assert N.MISURE_NIC["6"][0] == "congiunturale"

    # La chiave del flusso deve avere tante posizioni quante le dimensioni del
    # data structure definition: FREQ, REF_AREA, DATA_TYPE, MEASURE, COICOP.
    assert N.CHIAVE_NIC.count(".") == 4

    campione = N.Osservazione("nic_tendenziale", "prova", "2025-12", 1.2, "fonte")
    assert abs(campione.frazione - 0.012) < 1e-12

def test_omi_legge_tutte_le_province_dello_stesso_semestre():
    """Chi scarica per provincia si ritrova un file per provincia.

    La versione precedente leggeva il solo ultimo file in ordine alfabetico, e
    l'effetto era che cercare un Comune di una provincia diversa da quella
    sorteggiata dall'ordinamento restituiva "nessuna quotazione". Non un errore:
    una risposta sbagliata, che si sarebbe letta come "quel Comune non e'
    coperto". Il test costruisce due province e un semestre vecchio, e verifica
    che entrambe le province correnti si vedano e che il semestre superato resti
    fuori, perche' mescolare periodi diversi falserebbe il confronto.
    """
    import tempfile

    from immobiliare import omi as O

    cartella = Path(tempfile.mkdtemp())
    intestazione = (
        "Area_territoriale;Regione;Prov;Comune_ISTAT;Comune_cat;Comune_amm;"
        "Comune_descrizione;Fascia;Zona;Cod_tip;Descr_Tipologia;Stato;"
        "Compr_min;Compr_max;Loc_min;Loc_max"
    )

    def scrivi(nome, comune, prezzo):
        riga = (
            "CENTRO;MARCHE;MC;043013;C770;0;" + comune + ";B;B1;20;"
            "Abitazioni civili;NORMALE;" + prezzo + ";2.000;5,0;7,0"
        )
        (cartella / nome).write_text(
            "QUOTAZIONI IMMOBILIARI" + chr(10) + intestazione + chr(10) + riga,
            encoding="utf-8",
        )

    scrivi("QI_1_1_20261_VALORI.csv", "CIVITANOVA MARCHE", "1.500")
    scrivi("QI_2_1_20261_VALORI.csv", "MACERATA", "1.200")
    scrivi("QI_3_1_20182_VALORI.csv", "CIVITANOVA MARCHE", "900")

    assert O.semestre_del_file(cartella / "QI_1_1_20261_VALORI.csv") == "20261"

    quotazioni, letti = O.carica_cartella(cartella)
    comuni = {q.comune for q in quotazioni}
    assert comuni == {"CIVITANOVA MARCHE", "MACERATA"}, f"trovati {comuni}"
    assert len(letti) == 2, f"letti {letti}"

    # Il semestre superato non deve entrare: il vecchio valore di Civitanova
    # era 900, quello corrente 1.500.
    civitanova = [q for q in quotazioni if q.comune == "CIVITANOVA MARCHE"]
    assert len(civitanova) == 1
    assert civitanova[0].compravendita_min == 1_500

def test_omi_trova_i_comuni_scritti_come_li_scrive_la_fornitura():
    """I nomi nella fornitura non sono quelli che digita una persona.

    Nella stessa provincia convivono SANT`ELPIDIO A MARE, con l'accento grave al
    posto dell'apostrofo, e S BENEDETTO DEL TRONTO, con il prefisso abbreviato.
    Un confronto letterale risponde "nessuna quotazione" a chi scrive il nome
    corretto, e quel silenzio si legge come "Comune non coperto": una
    conclusione sbagliata tratta da una risposta plausibile, che e' il modo in
    cui questo genere di difetto fa danno.
    """
    import tempfile

    from immobiliare import omi as O

    cartella = Path(tempfile.mkdtemp())
    intestazione = (
        "Area_territoriale;Regione;Prov;Comune_ISTAT;Comune_cat;Comune_amm;"
        "Comune_descrizione;Fascia;Zona;Cod_tip;Descr_Tipologia;Stato;"
        "Compr_min;Compr_max;Loc_min;Loc_max"
    )
    righe = [
        "QUOTAZIONI IMMOBILIARI",
        intestazione,
        "CENTRO;MARCHE;AP;044007;D542;0;SANT" + chr(96) + "ELPIDIO A MARE;B;B1;20;"
        "Abitazioni civili;NORMALE;810;1.050;2,3;3,0",
        "CENTRO;MARCHE;AP;044066;H769;0;S BENEDETTO DEL TRONTO;B;B1;20;"
        "Abitazioni civili;NORMALE;1.900;2.700;6,0;8,0",
    ]
    percorso = cartella / "QI_9_1_20261_VALORI.csv"
    percorso.write_text(chr(10).join(righe), encoding="utf-8")

    quotazioni, _ = O.carica_cartella(cartella)

    # Entrambi si trovano digitando il nome come lo scriverebbe una persona.
    assert len(O.cerca(quotazioni, "Sant'Elpidio a Mare")) == 1
    assert len(O.cerca(quotazioni, "San Benedetto del Tronto")) == 1
    # E anche nella forma della fornitura, che deve restare valida.
    assert len(O.cerca(quotazioni, "S BENEDETTO DEL TRONTO")) == 1

    # Un nome inesistente non deve produrre falsi positivi.
    assert O.cerca(quotazioni, "Civitanuova") == []

    # La normalizzazione collassa i prefissi agiografici e gli apostrofi.
    assert O.normalizza_comune("Sant'Elpidio") == O.normalizza_comune("SANT" + chr(96) + "ELPIDIO")
    assert O.normalizza_comune("San Benedetto") == O.normalizza_comune("S BENEDETTO")

def test_omi_riconosce_il_semestre_anche_senza_token_nel_nome():
    """Un nome di file inatteso non deve far vincere la fornitura vecchia.

    Il rischio ha una direzione precisa. Se il semestre di una fornitura nuova
    restasse ignoto, il confronto lo ordinerebbe sotto qualunque valore noto, e
    i file del 2018 gia' in cache continuerebbero a essere quelli letti: il
    programma risponderebbe con dati di anni prima senza segnalare nulla. Per
    questo il riconoscimento ha tre vie in cascata, e l'ultima sbaglia al
    massimo attribuendo il file al semestre corrente, cioe' facendolo vincere.
    """
    import tempfile

    from immobiliare import omi as O

    cartella = Path(tempfile.mkdtemp())
    intestazione = (
        "Area_territoriale;Regione;Prov;Comune_ISTAT;Comune_cat;Comune_amm;"
        "Comune_descrizione;Fascia;Zona;Cod_tip;Descr_Tipologia;Stato;"
        "Compr_min;Compr_max;Loc_min;Loc_max"
    )
    riga = (
        "CENTRO;MARCHE;MC;043013;C770;0;CIVITANOVA MARCHE;B;B1;20;"
        "Abitazioni civili;NORMALE;1.500;2.000;5,0;7,0"
    )

    # Prima via: il token di cinque cifre nel nome.
    dal_nome = cartella / "QI_1_1_20252_VALORI.csv"
    dal_nome.write_text(intestazione + chr(10) + riga, encoding="utf-8")
    assert O.semestre_del_file(dal_nome) == "20252"

    # Seconda via: la riga di metadati anteposta al tracciato.
    dai_metadati = cartella / "quotazioni_regione_VALORI.csv"
    dai_metadati.write_text(
        "QUOTAZIONI IMMOBILIARI - Anno 2025 Semestre 2" + chr(10) + intestazione + chr(10) + riga,
        encoding="utf-8",
    )
    assert O.semestre_del_file(dai_metadati) == "20252"

    # Terza via: la data di modifica. Non conosciamo il valore, ma deve essere
    # una forma valida e, soprattutto, deve battere una fornitura del 2018.
    senza_indizi = cartella / "sconosciuto_VALORI.csv"
    senza_indizi.write_text(intestazione + chr(10) + riga, encoding="utf-8")
    ripiego = O.semestre_del_file(senza_indizi)
    assert len(ripiego) == 5 and ripiego.isdigit() and ripiego[-1] in "12"
    assert ripiego > "20182", "il ripiego non deve perdere contro una fornitura vecchia"

if __name__ == "__main__":
    superati = 0
    falliti = []
    for nome, funzione in sorted(globals().items()):
        if nome.startswith("test_") and callable(funzione):
            try:
                funzione()
                superati += 1
            except AssertionError as e:
                falliti.append((nome, e))
            except Exception as e:  # errore vero, non asserzione
                falliti.append((nome, f"{e.__class__.__name__}: {e}"))
    print(f"{superati} test superati, {len(falliti)} falliti")
    for nome, errore in falliti:
        print(f"  FALLITO {nome}: {errore}")
    raise SystemExit(1 if falliti else 0)
