# -*- coding: utf-8 -*-
"""Test del motore di calcolo.

Congelano il caso di riferimento descritto in `.claude/context/dev-testing.md` e le
verifiche di dominio che intercettano gli errori più probabili: scaglioni rimasti
a un'annualita' precedente, minimo di legge dell'imposta di registro ignorato,
prezzo-valore applicato dove non spetta, detrazione concessa dove non spetta.

Si eseguono con `python -m pytest tests` dalla radice del progetto, oppure con
`python tests/test_calcoli.py` se pytest non è installato.
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
    """Il prezzo-valore è una regola dell'imposta di registro: con l'IVA la base
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
    """Il caso va isolato perché la formula generale dividerebbe per zero."""
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
    """Il massimale è riferito all'immobile, non alla persona: con due
    cointestatari al cinquanta per cento ciascuno detrae su duemila euro."""
    assert C.detrazione_interessi(10_000, quota=1.0) == 4_000 * 0.19
    assert C.detrazione_interessi(10_000, quota=0.5) == 2_000 * 0.19


# --- IRPEF ------------------------------------------------------------------

def test_scaglioni_irpef_2026():
    # 28.000 al 23 per cento più 2.000 al 33 per cento
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
    # Marginale al 33 per cento sul 95 per cento, più addizionali, più metà registro.
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
    il rendimento netto risulta più che doppio di quello vero."""
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
    """La fornitura ufficiale non è UTF-8, e leggerla male non solleva errori.

    Il mirror open data pubblica file già in UTF-8; la fornitura scaricata
    dall'area riservata arriva nella codifica ANSI di Windows. Decodificarla come
    UTF-8 sostituendo i caratteri illeciti non fallisce: mette il segnaposto di
    rimpiazzo al posto di ogni accento, il file si carica, le quotazioni si
    calcolano, e un Comune accentato diventa irreperibile alla ricerca per nome.
    È il modello di difetto che produce un risultato plausibile invece di un
    errore, cioè quello contro cui vale la pena scrivere un test.
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
    assert quotazioni[0].comune == accentato, "il nome del Comune è stato corrotto in lettura"
    assert chr(0xFFFD) not in quotazioni[0].comune

    # Il separatore decimale italiano e il punto delle migliaia vanno interpretati.
    assert quotazioni[0].compravendita_min == 1_400
    assert quotazioni[0].locazione_max == 6.5

    # E il Comune deve restare raggiungibile dalla ricerca per nome.
    assert len(O.cerca(quotazioni, comune=accentato)) == 1

def test_indicatori_degradano_senza_rete():
    """Il contratto del modulo è che una fonte irraggiungibile non propaghi.

    Tutte le funzioni di rete del progetto devono fallire con l'eccezione di
    dominio, mai con quella del socket, altrimenti il comando cade invece di
    degradare. Il caso insidioso è `TimeoutError`, che non discende da
    `URLError`: una cattura scritta sulla sola `URLError` sembra corretta e
    lascia passare proprio il fallimento più frequente.
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
                    # `quadro` assorbe tutto e restituisce ciò che ha raccolto.
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
    """La mappa delle misure è il punto in cui il flusso ISTAT diventa leggibile.

    I codici della dimensione MEASURE sono numeri senza significato finché non
    li si traduce, e la traduzione è stata verificata sui valori: a dicembre
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
    una risposta sbagliata, che si sarebbe letta come "quel Comune non è
    coperto". Il test costruisce due province e un semestre vecchio, e verifica
    che entrambe le province correnti si vedano e che il semestre superato resti
    fuori, perché mescolare periodi diversi falserebbe il confronto.
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
    conclusione sbagliata tratta da una risposta plausibile, che è il modo in
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
    i file del 2018 già in cache continuerebbero a essere quelli letti: il
    programma risponderebbe con dati di anni prima senza segnalare nulla. Per
    questo il riconoscimento ha tre vie in cascata, e l'ultima sbaglia al
    massimo attribuendo il file al semestre corrente, cioè facendolo vincere.
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

def test_omi_quotazione_di_riferimento_preferisce_lo_stato_normale():
    """Il riferimento si prende sullo stato normale, non su quello ottimo.

    OTTIMO nella fornitura descrive l'immobile ristrutturato di recente.
    Prenderlo come termine di paragone farebbe sembrare a buon mercato qualunque
    cosa, che è il modo più rapido di convincersi che un prezzo alto sia
    giusto. La funzione restituisce anche la provenienza, perché due numeri
    senza l'indicazione della zona da cui vengono si rileggono un mese dopo come
    se fossero della zona giusta.
    """
    import tempfile

    from immobiliare import omi as O

    cartella = Path(tempfile.mkdtemp())
    intestazione = (
        "Area_territoriale;Regione;Prov;Comune_ISTAT;Comune_cat;Comune_amm;"
        "Comune_descrizione;Fascia;Zona;Cod_tip;Descr_Tipologia;Stato;"
        "Compr_min;Compr_max;Loc_min;Loc_max"
    )
    def riga(zona, stato, mn, mx):
        return (
            "CENTRO;MARCHE;MC;043013;C770;0;CIVITANOVA MARCHE;B;" + zona + ";20;"
            "Abitazioni civili;" + stato + ";" + mn + ";" + mx + ";5,0;7,0"
        )

    percorso = cartella / "QI_1_1_20252_VALORI.csv"
    percorso.write_text(
        chr(10).join([
            intestazione,
            riga("B1", "NORMALE", "1.650", "3.000"),
            riga("B1", "OTTIMO", "3.500", "5.000"),
            riga("C3", "NORMALE", "1.200", "1.850"),
        ]),
        encoding="utf-8",
    )
    quotazioni, _ = O.carica_cartella(cartella)

    # Con la zona: solo quella zona, e solo lo stato normale.
    minimo, massimo, provenienza = O.quotazione_di_riferimento(quotazioni, "Civitanova Marche", "B1")
    assert (minimo, massimo) == (1_650, 3_000), f"ottenuto {minimo}-{massimo}"
    assert "B1" in provenienza and "normale" in provenienza

    # Senza zona: tutto il Comune, con l'avvertenza che la forbice è larga.
    minimo, massimo, provenienza = O.quotazione_di_riferimento(quotazioni, "Civitanova Marche")
    assert (minimo, massimo) == (1_200, 3_000)
    assert "indicare la zona" in provenienza

    # Comune assente: nessun numero inventato.
    assert O.quotazione_di_riferimento(quotazioni, "Comune inesistente") == (0.0, 0.0, "")

def test_risalita_storica_cerca_la_finestra_e_non_gli_estremi():
    """La peggiore finestra di N mesi, non il massimo meno il minimo della serie.

    È la distinzione che rende il numero utilizzabile. Massimo assoluto meno
    minimo assoluto da' sempre un valore più grande e privo di significato,
    perché i due estremi possono stare a decenni di distanza e nessun piano di
    ammortamento li attraversa nella stessa finestra: ciò che un mutuo incontra
    davvero è la peggiore finestra di durata fissata. La serie sintetica di questo
    test è costruita perché le due misure divergano, con il minimo assoluto
    all'inizio e il massimo alla fine, lontani fra loro più della finestra.

    Il test non tocca la rete: sostituisce la funzione che scarica la serie, che è
    l'unico punto di contatto con il portale dati.
    """
    from immobiliare import tassi as T

    # Trenta osservazioni: scende da 2 a meno 1, resta bassa, poi risale a 5.
    valori = (
        [2.0, 1.0, 0.0, -1.0]          # discesa iniziale, minimo assoluto a indice 3
        + [-0.5] * 10                  # pianura lunga
        + [0.0, 0.5, 1.0, 2.0, 3.0, 4.0, 5.0]   # risalita, massimo assoluto in coda
        + [4.5] * 9
    )
    finta = [(f"2000-{i + 1:02d}", v) for i, v in enumerate(valori)]

    originale = T.serie
    T.serie = lambda chiave="euribor_3m", osservazioni=400: finta
    try:
        risalite = {r.mesi: r for r in T.risalite_storiche(finestre=(6, 12))}
        estremi = T.estremi_storici()
    finally:
        T.serie = originale

    # Escursione totale della serie: sei punti, da meno 1 a 5.
    assert abs(estremi["massimo"] - estremi["minimo"] - 6.0) < 1e-9

    # Su sei mesi la peggiore finestra vale meno di quell'escursione: la risalita
    # è graduale, quindi nessuna finestra di sei mesi la contiene per intero.
    assert 6 in risalite
    assert risalite[6].variazione < 6.0
    assert abs(risalite[6].variazione - 5.0) < 1e-9, risalite[6].variazione
    assert risalite[6].valore_iniziale == 0.0 and risalite[6].valore_finale == 5.0

    # Su dodici mesi la finestra è più larga e cattura più risalita, ma resta
    # comunque sotto l'escursione totale, perché il minimo assoluto sta troppo
    # indietro per rientrare nella stessa finestra del massimo.
    assert risalite[12].variazione > risalite[6].variazione
    assert risalite[12].variazione < 6.0

    # La proprietà che rende il valore leggibile nel modello: punti percentuali
    # nella fonte, frazione pronta per i calcoli nella proprietà.
    assert abs(risalite[6].punti - risalite[6].variazione / 100) < 1e-12

    # Una finestra più lunga della serie non produce una voce inventata.
    T.serie = lambda chiave="euribor_3m", osservazioni=400: finta
    try:
        assert T.risalite_storiche(finestre=(500,)) == []
    finally:
        T.serie = originale


def test_risalite_congelate_coerenti_con_la_documentazione():
    """I valori nel codice sono quelli che le note del workbook citano.

    Le note del foglio Simulatore mutuo sono generate interpolando questi campi,
    quindi un valore cambiato nel codice e non riverificato sulla serie finirebbe
    scritto nel workbook come se fosse un dato osservato. Il test non può
    verificare la fonte, che richiede rete: verifica la coerenza interna, cioè
    che i numeri stiano nell'ordine e nel dominio che la fonte impone.
    """
    r = P.RISALITE_EURIBOR

    # Una finestra più lunga contiene quelle più corte, quindi la risalita su
    # ventiquattro mesi non può essere inferiore a quella su dodici.
    assert r.risalita_24_mesi >= r.risalita_12_mesi

    # Nessuna finestra può superare l'escursione totale della serie.
    assert max(r.risalita_12_mesi, r.risalita_24_mesi, r.risalita_36_mesi) <= r.massimo_storico - r.minimo_storico

    # Il livello corrente sta fra gli estremi, e gli estremi sono nell'ordine.
    assert r.minimo_storico <= r.livello_corrente <= r.massimo_storico

    # I valori sono in punti percentuali, non in frazioni: un 3,78 scritto come
    # 0,0378 passerebbe inosservato e produrrebbe note che dicono zero punti.
    assert r.risalita_12_mesi > 1.0, "le risalite vanno scritte in punti, non in frazione"


def test_effetto_inflazione_usa_fisher_esatto_e_non_la_sottrazione():
    """Il rendimento reale è un rapporto di poteri d'acquisto, non una differenza.

    La forma che si vede scritta quasi sempre è r meno i, che è l'approssimazione
    al primo ordine della definizione. Il test fissa tre cose: che il modello usi
    la forma esatta, che l'errore dell'approssimazione sia riportato e abbia il
    segno giusto, e che le identità che rendono la formula riconoscibile valgano,
    cioè che con inflazione nulla nominale e reale coincidano e che con
    rivalutazione pari all'inflazione la rivalutazione reale sia esattamente zero.
    """
    # Definizione: (1+r)/(1+i)-1, e non r-i.
    assert abs(C.tasso_reale(0.05, 0.02) - (1.05 / 1.02 - 1)) < 1e-15
    assert abs(C.tasso_reale(0.05, 0.02) - 0.0294117647) < 1e-9

    # La sottrazione sovrastima sempre, quando entrambi i tassi sono positivi.
    assert (0.05 - 0.02) > C.tasso_reale(0.05, 0.02)

    # Con inflazione nulla non c'è niente da correggere. Il confronto è con
    # tolleranza e non esatto perché la divisione per 1.0 in binario non è
    # l'identità sui decimali che non hanno rappresentazione finita.
    assert abs(C.tasso_reale(0.037, 0.0) - 0.037) < 1e-15

    # Un'inflazione che annullerebbe il livello dei prezzi non è ammissibile.
    try:
        C.tasso_reale(0.05, -1.0)
        raise AssertionError("un'inflazione di meno cento per cento doveva essere rifiutata")
    except ValueError:
        pass

    e = C.effetto_inflazione(
        inflazione=0.02,
        rendimento_netto_nominale=0.05,
        tir_nominale=0.04,
        prezzo=120_000,
        rivalutazione_immobile=0.02,
        debito_residuo_nominale=40_000,
        rata_annua=5_200,
        canone_annuo=6_000,
        indicizzazione_canone=0.0,
        orizzonte_anni=25,
        tasso_sconto=0.03,
    )

    # Rivalutazione nominale pari all'inflazione: rivalutazione reale nulla, ed è
    # il caso del mercato residenziale italiano degli ultimi vent'anni.
    assert abs(e.rivalutazione_reale_immobile) < 1e-15

    # Il valore finale in euro di oggi torna quindi esattamente al prezzo pagato.
    assert abs(e.valore_finale_reale - 120_000) < 1e-6

    # Canone non indicizzato con inflazione al due per cento: perde il due per
    # cento reale l'anno, nella forma esatta.
    assert abs(e.erosione_reale_canone - (1 / 1.02 - 1)) < 1e-15

    # L'errore dell'approssimazione è positivo, perché la sottrazione sovrastima.
    assert e.errore_approssimazione > 0
    assert abs(e.errore_approssimazione - ((0.05 - 0.02) - C.tasso_reale(0.05, 0.02))) < 1e-15

    # Lo sconto che l'inflazione fa sul debito è positivo con inflazione positiva,
    # e vale la differenza fra il debito nominale e il suo valore in euro di oggi.
    assert e.sconto_inflazione_sul_debito > 0
    assert abs(e.debito_residuo_reale - 40_000 / 1.02 ** 25) < 1e-9
    assert abs(e.sconto_inflazione_sul_debito - (40_000 - e.debito_residuo_reale)) < 1e-9


def test_fattore_rendita_crescente_coincide_con_la_somma_esplicita():
    """La forma chiusa usata nel workbook e la somma esplicita devono coincidere.

    È la doppia implementazione applicata a una formula. Il workbook non può
    sommare n termini con n variabile in una cella singola e usa la forma chiusa
    della serie geometrica; il motore tiene la somma esplicita, che è leggibile
    e verificabile a occhio. Se le due divergono, la formula del foglio è
    sbagliata e nessuna cella andrebbe in errore per dirlo.
    """
    def somma_esplicita(crescita, sconto, anni):
        return sum((1 + crescita) ** (k - 1) / (1 + sconto) ** k for k in range(1, anni + 1))

    casi = [
        (0.02, 0.03, 25),   # il caso del modello
        (0.0, 0.03, 25),    # crescita nulla: rendita costante
        (0.05, 0.03, 30),   # crescita superiore al tasso di sconto
        (0.03, 0.03, 25),   # il caso singolare, crescita pari al tasso di sconto
        (0.02, 0.03, 1),    # un anno solo
        (-0.01, 0.03, 10),  # crescita negativa
    ]
    for crescita, sconto, anni in casi:
        chiusa = C.fattore_rendita_crescente(crescita, sconto, anni)
        esplicita = somma_esplicita(crescita, sconto, anni)
        assert abs(chiusa - esplicita) < 1e-9, (
            f"crescita {crescita}, sconto {sconto}, anni {anni}: "
            f"chiusa {chiusa}, esplicita {esplicita}"
        )

    # Il caso singolare non deve passare per il denominatore nullo.
    assert abs(C.fattore_rendita_crescente(0.03, 0.03, 25) - 25 / 1.03) < 1e-12

    # Rendita costante: il fattore è l'annualita' ordinaria.
    atteso = (1 - 1.03 ** -25) / 0.03
    assert abs(C.fattore_rendita_crescente(0.0, 0.03, 25) - atteso) < 1e-12

    # E il canone rinunciato del modello si ricostruisce dai due fattori.
    e = C.effetto_inflazione(
        inflazione=0.02, rendimento_netto_nominale=0.05, tir_nominale=0.04,
        prezzo=120_000, rivalutazione_immobile=0.02, debito_residuo_nominale=0.0,
        rata_annua=5_200, canone_annuo=6_000, indicizzazione_canone=0.0,
        orizzonte_anni=25, tasso_sconto=0.03,
    )
    dai_fattori = 6_000 * (
        C.fattore_rendita_crescente(0.02, 0.03, 25)
        - C.fattore_rendita_crescente(0.0, 0.03, 25)
    )
    assert abs(e.canone_perso_per_mancata_indicizzazione - dai_fattori) < 1e-6, (
        f"somma esplicita {e.canone_perso_per_mancata_indicizzazione}, dai fattori {dai_fattori}"
    )


def test_scheda_sfugge_i_dati_e_non_inventa_il_prezzo_massimo():
    """Due garanzie della scheda di trattativa, entrambe nate da difetti osservati.

    La prima riguarda la separazione fra testo e marcatura. I campi di un annuncio
    sono compilati a mano e contengono caratteri che in LaTeX hanno un significato:
    il nome di un'agenzia con la e commerciale, un indirizzo col cancelletto, una
    nota con la percentuale. Vanno sfuggiti, e insieme non va sfuggita la marcatura
    che la scheda produce: le prime versioni passavano per la funzione di fuga
    anche le etichette, che contenevano il comando del grassetto, e il PDF lo
    stampava alla lettera.

    La seconda riguarda i numeri che dipendono da un dato assente. Il prezzo
    massimo sostenibile è il prezzo a cui il rendimento raggiunge l'obiettivo,
    quindi dipende dal canone: senza canone la prima versione stampava meno
    seimila euro e annunciava uno sconto da ottenere del centoquattro per cento
    del prezzo. Aritmeticamente corretto, operativamente assurdo, e con la faccia
    di un obiettivo di negoziazione. La scheda deve rifiutarsi di stamparlo.
    """
    from immobiliare import annunci as A
    from immobiliare import scheda as S

    # Un annuncio con caratteri ostili in tutti i campi testuali.
    ostile = A.Annuncio(
        id="house_x", comune="Comune & Frazione", indirizzo="via Rossi #12 (100% ok)",
        zona_omi="B_5", mq=60, prezzo_richiesto=100_000, canone_atteso_mese=500,
        rendita_catastale=400, categoria="A/3", spese_condominio_anno=900,
        quotazione_omi_min=1500, quotazione_omi_max=2500,
    )
    sorgente = S.costruisci(ostile, mutuo=70_000)

    # I caratteri speciali dei dati sono sfuggiti.
    assert r"Comune \& Frazione" in sorgente
    assert r"\#12" in sorgente
    assert r"100\% ok" in sorgente
    assert r"B\_5" in sorgente

    # E la marcatura prodotta dalla scheda non è stata sfuggita: se lo fosse,
    # comparirebbe la forma con la barra rovesciata resa visibile.
    assert r"\textbackslash{}textbf" not in sorgente
    assert r"\textbf{Costo totale}" in sorgente

    # Il documento è completo e a pagina singola.
    assert sorgente.startswith("\\documentclass")
    assert sorgente.rstrip().endswith(r"\end{document}")
    assert sorgente.count(r"\begin{document}") == 1

    # Con tutti i dati, il prezzo massimo si calcola e la casella lo riporta.
    assert "Il numero da portare in trattativa" in sorgente
    assert "non è calcolabile" not in sorgente

    # Senza canone, la stessa casella si rifiuta e dice perché.
    senza_canone = A.Annuncio(
        id="house_y", comune="Comune di prova", mq=60, prezzo_richiesto=100_000,
        rendita_catastale=400, categoria="A/3", spese_condominio_anno=900,
        zona_omi="B5",
    )
    sorgente2 = S.costruisci(senza_canone)
    assert "non è calcolabile" in sorgente2
    assert "Scheda incompleta" in sorgente2
    # E i rendimenti non compaiono affatto, invece di comparire a zero.
    assert "Rendimento netto reale" not in sorgente2
    assert "Cash flow annuo" not in sorgente2

    # Senza rendita catastale la scheda dichiara che il prezzo-valore non si
    # applica, che è la voce che cambia di più il costo dell'operazione.
    senza_rendita = A.Annuncio(
        id="house_z", comune="Comune di prova", mq=60, prezzo_richiesto=100_000,
        canone_atteso_mese=500, categoria="A/3", spese_condominio_anno=900, zona_omi="B5",
    )
    sorgente3 = S.costruisci(senza_rendita)
    assert "prezzo-valore non si applica" in sorgente3

    # La mappa dei campi bloccanti è condivisa col comando che li elenca: una
    # copia locale divergerebbe, e la scheda direbbe di chiedere cose diverse.
    assert S.CAMPI_BLOCCANTI is A.CAMPI_BLOCCANTI


def _cache_omi_finta(nome_comune: str = "CIVITANOVA MARCHE", codice: str = "C770",
                     provincia: str = "MC"):
    """Una cache OMI minima con la coppia valori e zone, come la produce la fornitura."""
    import tempfile

    cartella = Path(tempfile.mkdtemp())
    intestazione_valori = (
        "Area_territoriale;Regione;Prov;Comune_ISTAT;Comune_cat;Comune_amm;"
        "Comune_descrizione;Fascia;Zona;Cod_tip;Descr_Tipologia;Stato;"
        "Compr_min;Compr_max;Loc_min;Loc_max"
    )
    intestazione_zone = (
        "Area_territoriale;Regione;Prov;Comune_ISTAT;Comune_cat;Sez;Comune_amm;"
        "Comune_descrizione;Fascia;Zona_Descr;Zona;LinkZona;Cod_tip_prev;"
        "Descr_tip_prev;Stato_prev;Microzona"
    )
    valori = [
        "QUOTAZIONI IMMOBILIARI",
        intestazione_valori,
        "CENTRO;MARCHE;" + provincia + ";11043013;K3AN;" + codice + ";" + nome_comune
        + ";B;B1;20;Abitazioni civili;NORMALE;1.100;1.600;4,0;6,0",
    ]
    zone = [
        "QUOTAZIONI IMMOBILIARI : Informazioni di Zona OMI",
        intestazione_zone,
        "CENTRO;MARCHE;" + provincia + ";11043013;K3AN; ;" + codice + ";" + nome_comune
        + ";B;'SEZIONE PORTO';B1;MC00000339;20;Abitazioni civili;N;1;",
    ]
    (cartella / "QI_1_1_20252_VALORI.csv").write_text(chr(10).join(valori), encoding="utf-8")
    (cartella / "QI_1_1_20252_ZONE.csv").write_text(chr(10).join(zone), encoding="utf-8")
    return cartella


def test_comuni_costruisce_il_collegamento_agli_atti_dal_codice_della_fornitura():
    """Il collegamento agli atti IMU si costruisce, non si conserva.

    Una tabella di collegamenti per Comune invecchierebbe come invecchia una tabella di
    aliquote, e per giunta andrebbe compilata ottomila volte. L'applicazione del
    Dipartimento delle finanze accetta due parametri, il codice catastale del Comune e la
    sigla della provincia, ed entrambi stanno gia' nella fornitura OMI in cache: il
    collegamento e' quindi una funzione dei dati che il progetto ha, e vale per ogni Comune
    della regione importata senza che nessuno lo scriva a mano.
    """
    from immobiliare import comuni as M

    cartella = _cache_omi_finta()
    comune = M.trova("Civitanova Marche", cartella)

    assert comune is not None
    assert comune.codice_catastale == "C770"
    assert comune.provincia == "MC"
    # La forma esatta e' quella verificata a mano sul portale il 3 settembre 2026.
    assert comune.link_delibere_imu.endswith("sceltaanno.htm?cc=C770&pr=MC")
    # E il nome si cerca come lo scrive una persona, non come lo scrive la fornitura.
    assert M.trova("CIVITANOVA MARCHE", cartella) == comune
    assert M.trova("Comune inesistente", cartella) is None


def test_comuni_stato_verifica_segue_il_termine_del_28_ottobre():
    """Una lettura non e' valida per sempre, e la scadenza ha una data precisa.

    L'atto comunale ha efficacia per l'anno se pubblicato entro il 28 ottobre di
    quell'anno. Ne discende che una lettura fatta prima di quel termine e' provvisoria,
    perche' il Comune puo' ancora deliberare, e che una lettura dell'anno prima non vale,
    perche' o e' stata superata o e' stata prorogata per silenzio e le due cose non si
    distinguono senza aprire l'atto. Senza questa distinzione un valore letto a marzo
    verrebbe usato a dicembre come se fosse definitivo.
    """
    import datetime as dt

    from immobiliare import comuni as M

    marzo = dt.date(2026, 3, 10)
    novembre = dt.date(2026, 11, 5)

    assert M.stato_verifica(None, 2026, marzo)[0] == "assente"
    assert M.stato_verifica(marzo, 2026, marzo)[0] == "provvisoria"
    assert M.stato_verifica(novembre, 2026, novembre)[0] == "definitiva"
    # Letta prima del termine, ma consultata quando il termine e' passato: va riletta.
    assert M.stato_verifica(marzo, 2026, novembre)[0] == "da rileggere"
    # Letta l'anno prima: non vale per l'anno chiesto.
    assert M.stato_verifica(dt.date(2025, 11, 5), 2026, marzo)[0] == "scaduta"


def test_comuni_registro_tiene_separato_il_collegamento_dal_valore():
    """Sapere dove sta il dato e sapere il dato sono due cose diverse.

    Il registro conserva un collegamento verificato anche quando nessuno ha ancora letto il
    valore che quel collegamento porta, e in quel caso il comando deve continuare a dichiarare
    la voce mancante invece di tacere. E' la proprieta' per cui il registro esiste: senza,
    basterebbe un collegamento salvato per far credere che il dato sia acquisito.

    L'altra proprieta' verificata qui riguarda la scrittura del file. Le note contengono punti
    e virgola, che sono il delimitatore: una riga scritta senza virgolette si tronca a meta' e
    il troncamento non solleva errori, si limita a perdere l'informazione. Il caso reale c'e'
    gia' stato, quindi vale congelarlo.
    """
    import tempfile

    from immobiliare import comuni as M

    cartella = Path(tempfile.mkdtemp())
    percorso = cartella / "comuni-verifiche.csv"
    percorso.write_text(
        "comune;provincia;codice_catastale;aliquota_imu_altri;aliquota_imu_principale;"
        "imposta_soggiorno_notte;link_delibera_imu;link_imposta_soggiorno;verificato_il;note"
        + chr(10)
        + "COMUNE DI PROVA;XX;A000;;;;;https://esempio.invalid/atti;;solo il collegamento"
        + chr(10),
        encoding="utf-8",
    )
    prova = M.verifica_di("Comune di prova", M.leggi_registro(percorso))
    assert prova is not None
    assert prova.link_imposta_soggiorno == "https://esempio.invalid/atti"
    assert prova.imposta_soggiorno_notte is None
    assert len(M.cosa_manca(prova)) == 2
    # Un Comune assente non e' un errore: e' semplicemente tutto da leggere.
    assert len(M.cosa_manca(None)) == 2

    # Sul registro vero: l'imposta di soggiorno risulta letta con la sua data, l'aliquota IMU no.
    radice = Path(__file__).resolve().parent.parent
    civitanova = M.verifica_di("Civitanova Marche", M.leggi_registro(radice / M.REGISTRO_PREDEFINITO))
    assert civitanova is not None
    assert civitanova.imposta_soggiorno_notte == 1.00
    assert civitanova.verificato_il is not None
    assert civitanova.aliquota_imu_altri is None
    assert M.cosa_manca(civitanova) == [
        "aliquota IMU per gli immobili diversi dall'abitazione principale"
    ]
    # La nota contiene punti e virgola e deve arrivare intera: il campo e' quotato nel file.
    assert ";" in civitanova.note
    assert civitanova.note.rstrip().endswith(".")


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
