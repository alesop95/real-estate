# -*- coding: utf-8 -*-
"""Test del generatore del workbook.

Non verificano i numeri, che sono coperti da `test_calcoli.py` e dal ricalcolo con
Excel: verificano la struttura, e in particolare il contratto piu' fragile del
progetto, cioe' la corrispondenza posizionale fra le colonne del foglio Annunci e
l'ordine con cui `annunci.esporta_in_excel` le scrive. Sono due elenchi in due file
diversi che devono restare allineati, e se divergono l'esportazione mette i prezzi
nella colonna delle note senza che nulla protesti.

Si eseguono con `python -m pytest tests`, oppure con `python tests/test_workbook.py`.
"""

from __future__ import annotations

import sys
import tempfile
from dataclasses import fields
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "src"))

from openpyxl import load_workbook  # noqa: E402

from immobiliare import annunci as A  # noqa: E402
from immobiliare import excel_builder as E  # noqa: E402

_workbook_generato: Path | None = None


def workbook() -> Path:
    """Genera il workbook una volta sola per l'intera sessione di test."""
    global _workbook_generato
    if _workbook_generato is None or not _workbook_generato.exists():
        destinazione = Path(tempfile.gettempdir()) / "valutazione-test.xlsx"
        E.genera(str(destinazione))
        _workbook_generato = destinazione
    return _workbook_generato


def test_il_workbook_si_genera_con_tutti_i_fogli():
    wb = load_workbook(workbook())
    attesi = [
        "Guida", "Cruscotto", "Parametri", "Immobile", "Mutuo", "Ammortamento", "Simulatore mutuo", "Locazione",
        "Cash flow", "Metriche", "Confronto affitto", "Scenari", "Rischio", "Comproprieta", "Checklist", "Asta", "Dossier tecnico",
        "Annunci", "Confronto immobili", "Fonti", "_Estrazioni",
    ]
    assert wb.sheetnames == attesi


def test_nomi_definiti_essenziali_presenti():
    """I nomi definiti sono il collante fra i fogli: se ne sparisce uno, le formule
    che lo usano diventano #NOME? in silenzio fino all'apertura del file."""
    wb = load_workbook(workbook())
    definiti = set(wb.defined_names)
    essenziali = {
        "prezzo", "rendita", "categoria", "prima_casa", "da_impresa", "agevolata",
        "di_lusso", "valore_catastale", "base_registro", "imposte_totali",
        "costi_accessori", "costo_totale", "esborso", "mutuo_importo", "tasso",
        "durata", "rata_mensile", "oneri_mutuo", "detrazione_anno",
        "debito_residuo_anno", "noi_annuo", "utile_locazione", "ricavo_lordo",
        "ricavo_effettivo", "flussi_tir", "flussi_tir_dal_primo",
        "cash_flow_primo_anno", "orizzonte", "data_erogazione", "rend_obiettivo",
        "ltv_conf", "aliquota_conf", "irpef_marginale", "sim_capitale",
        "sim_rata_iniziale", "sim_flussi", "sim_pagato",
        "accantonamento_ristrutturazione", "verdetto", "verifiche_aperte",
        "prob_cash_negativo", "prob_batte_alternativa", "sim_cash_flow", "vol_canone",
    }
    mancanti = essenziali - definiti
    assert not mancanti, f"nomi definiti mancanti: {sorted(mancanti)}"


def test_intestazione_annunci_allineata_all_esportazione():
    """Il contratto fra `foglio_annunci` e `esporta_in_excel`.

    Il foglio ha tre colonne in piu' rispetto ai campi del registro, che sono le
    tre calcolate da formula. Ogni campo del registro deve trovarsi nella colonna
    che l'esportazione gli assegna, e nessuna colonna di formula deve finire
    sotto un campo.
    """
    wb = load_workbook(workbook())
    ws = wb["Annunci"]

    intestazione = None
    for riga in range(1, 12):
        if ws.cell(row=riga, column=1).value == "ID":
            intestazione = riga
            break
    assert intestazione is not None, "intestazione del foglio Annunci non trovata"

    titoli = []
    colonna = 1
    while ws.cell(row=intestazione, column=colonna).value:
        titoli.append(ws.cell(row=intestazione, column=colonna).value)
        colonna += 1

    campi_registro = [f.name for f in fields(A.Annuncio)]
    # Tre colonne del foglio sono calcolate e non hanno un campo corrispondente.
    assert len(titoli) == len(campi_registro) + 3, (
        f"il foglio ha {len(titoli)} colonne e il registro {len(campi_registro)} campi: "
        "la differenza deve essere esattamente le tre colonne di formula"
    )
    for atteso, effettivo in (
        (19, "Prezzo al mq"), (22, "Scarto su OMI"), (29, "Rendimento lordo"),
    ):
        assert titoli[atteso - 1] == effettivo, (
            f"la colonna {atteso} dovrebbe essere '{effettivo}' e invece e' '{titoli[atteso - 1]}'"
        )


def test_esportazione_scrive_nelle_colonne_giuste(tmp_path=None):
    """Esporta un annuncio noto e rilegge le celle una per una."""
    cartella = Path(tmp_path) if tmp_path else Path(tempfile.mkdtemp())
    destinazione = cartella / "esportazione.xlsx"
    E.genera(str(destinazione))

    registro = A.Registro(cartella / "annunci.csv")
    registro.aggiungi(
        A.Annuncio(
            id="house_9", stato="visitata", fonte="immobiliare.it", agenzia="Agenzia Prova",
            contatto="333 1112223", link="https://esempio.invalid/1", comune="Comune di esempio",
            provincia="XX", indirizzo="via Prova 1", tipologia="bilocale",
            destinazione_uso="abitazione", nuova_costruzione="SI", data_consegna="2027-06",
            mq=60, prezzo_richiesto=100_000, prezzo_obiettivo=93_000,
            rendita_catastale=500, categoria="A/3", canone_atteso_mese=520,
            asta="SI", base_asta=72_000, data_asta="2026-11-14",
            tribunale_procedura="Macerata RGE 55/2025",
            stato_occupazione="occupato dal debitore", note="prova",
        )
    )
    scritti = A.esporta_in_excel(registro, str(destinazione))
    assert scritti == 1

    ws = load_workbook(destinazione)["Annunci"]
    riga = None
    for r in range(1, 20):
        if ws.cell(row=r, column=1).value == "house_9":
            riga = r
            break
    assert riga is not None, "l'annuncio esportato non si trova nel foglio"

    atteso = {
        1: "house_9", 3: "visitata", 5: "Agenzia Prova", 6: "333 1112223",
        8: "Comune di esempio", 9: "XX", 12: "bilocale", 13: "abitazione",
        14: "SI", 15: "2027-06", 16: 60, 17: 100_000, 18: 93_000,
        21: None, 23: 500, 24: "A/3", 28: 520,
        # Le cinque colonne dell'asta stanno fra il rendimento lordo e il punteggio.
        30: "SI", 31: 72_000, 32: "2026-11-14", 33: "Macerata RGE 55/2025",
        34: "occupato dal debitore", 36: "prova",
    }
    for colonna, valore in atteso.items():
        effettivo = ws.cell(row=riga, column=colonna).value
        assert effettivo == valore, f"colonna {colonna}: atteso {valore!r}, trovato {effettivo!r}"

    # Le tre colonne calcolate devono essere rimaste formule, non valori.
    for colonna in (19, 22, 29):
        contenuto = ws.cell(row=riga, column=colonna).value
        assert isinstance(contenuto, str) and contenuto.startswith("="), (
            f"la colonna calcolata {colonna} e' stata sovrascritta con {contenuto!r}"
        )


def test_confronto_immobili_legge_dalla_riga_giusta():
    """Il foglio di confronto punta alla prima riga di dati del foglio Annunci."""
    wb = load_workbook(workbook())
    annunci = wb["Annunci"]
    confronto = wb["Confronto immobili"]

    prima_annunci = None
    for riga in range(1, 12):
        if annunci.cell(row=riga, column=1).value == "ID":
            prima_annunci = riga + 1
            break
    assert prima_annunci is not None

    prima_confronto = None
    for riga in range(1, 20):
        valore = confronto.cell(row=riga, column=1).value
        if isinstance(valore, str) and valore.startswith("=IF(Annunci!"):
            prima_confronto = riga
            break
    assert prima_confronto is not None, "nessuna riga di confronto trovata"
    assert f"Annunci!$A{prima_annunci}" in confronto.cell(row=prima_confronto, column=1).value


def test_piano_ammortamento_copre_quaranta_anni():
    wb = load_workbook(workbook())
    ws = wb["Ammortamento"]
    numeri = [
        ws.cell(row=riga, column=1).value
        for riga in range(1, 500)
        if isinstance(ws.cell(row=riga, column=1).value, int)
    ]
    assert max(numeri) == E.MAX_RATE == 480


def test_dossier_tecnico_ha_peso_e_contatori_coerenti():
    """Ogni documento porta un peso fra i tre ammessi, e i contatori li leggono.

    Il peso non e' decorativo: la formula del contatore dei bloccanti fa
    `COUNTIFS` sulla stringa esatta, quindi un valore scritto diversamente,
    anche solo con un'iniziale maiuscola, sparirebbe dal conteggio senza che
    nulla protesti e il cruscotto direbbe zero documenti mancanti.
    """
    wb = load_workbook(workbook())
    ws = wb["Dossier tecnico"]

    ammessi = {"bloccante", "importante", "se ricorre"}
    pesi = []
    for riga in range(1, ws.max_row + 1):
        documento = ws.cell(row=riga, column=2).value
        peso = ws.cell(row=riga, column=6).value
        # Le righe di dati sono quelle con un documento e uno stato iniziale.
        if documento and ws.cell(row=riga, column=8).value == "da chiedere":
            assert peso in ammessi, f"riga {riga}: peso {peso!r} non ammesso"
            pesi.append(peso)

    assert len(pesi) > 40, f"solo {len(pesi)} documenti in elenco"
    assert pesi.count("bloccante") > 0

    for nome in ("documenti_bloccanti_aperti", "documenti_completamento"):
        assert nome in wb.defined_names, f"nome definito {nome} assente"

    riferimento = wb.defined_names["documenti_bloccanti_aperti"].attr_text
    assert riferimento.startswith("'Dossier tecnico'!")
    cella = riferimento.split("!")[1].replace("$", "")
    formula = ws[cella].value
    assert formula.startswith("=COUNTIFS(") and '"bloccante"' in formula

def test_registro_riletto_non_duplica_gli_annunci():
    """Rileggere il file da disco deve sostituire, non accodare.

    Il costruttore chiama gia' `carica`, quindi chiamarlo di nuovo per rileggere
    il file, cosa che viene naturale dopo averlo modificato, raddoppiava
    l'elenco. Nessun errore: un registro che conta il doppio, un foglio di
    confronto con le righe ripetute e una graduatoria che sembra piu' ricca di
    quello che e'. E' il difetto che produce un risultato plausibile.
    """
    import tempfile

    from immobiliare import annunci as A

    percorso = Path(tempfile.mkdtemp()) / "annunci.csv"
    registro = A.Registro(percorso)
    registro.aggiungi(A.Annuncio(id="x_1", comune="Comune di esempio", mq=50, prezzo_richiesto=100_000))
    registro.aggiungi(A.Annuncio(id="x_2", comune="Comune di esempio", mq=60, prezzo_richiesto=120_000))
    registro.salva()

    riletto = A.Registro(percorso)
    assert len(riletto.annunci) == 2
    riletto.carica()
    riletto.carica()
    assert len(riletto.annunci) == 2, f"il registro si e' duplicato: {len(riletto.annunci)} righe"
    assert [a.id for a in riletto.annunci] == ["x_1", "x_2"]

def test_numero_riconosce_il_separatore_delle_migliaia_italiano():
    """Un punto in un annuncio italiano quasi sempre separa le migliaia.

    Il modello locale restituisce a volte i numeri come stringhe, cosi' come li
    trova nel testo. Trattare 175.000 come decimale produce un prezzo di
    centosettantacinque euro: nessun errore, nessuna eccezione, un immobile che
    nel confronto risulta regalato. La discriminante e' quante cifre seguono il
    punto, tre per le migliaia e una o due per i decimali, ed e' l'unica euristica
    che regge sui valori che questo dominio incontra davvero, cioe' prezzi,
    superfici, canoni e rendite.
    """
    from immobiliare import annunci as A

    casi = [
        ("175.000", 175_000.0),      # migliaia: il caso che rompeva
        ("1.500.000", 1_500_000.0),  # due separatori
        ("89.000 EUR", 89_000.0),    # con valuta appesa
        ("612,45", 612.45),          # decimale all'italiana
        ("1.234,56", 1_234.56),      # migliaia e decimale insieme
        ("612.45", 612.45),          # due cifre dopo il punto: decimale
        ("620 al mese", 620.0),
        ("95", 95.0),
        ("2,5", 2.5),
        ("", 0.0),
        ("nessun dato", 0.0),
    ]
    for testo, atteso in casi:
        ottenuto = A._numero(testo)
        assert abs(ottenuto - atteso) < 1e-9, f"{testo!r}: atteso {atteso}, ottenuto {ottenuto}"

    # I numeri veri passano intatti.
    assert A._numero(175_000) == 175_000.0
    assert A._numero(612.45) == 612.45


def test_schema_di_estrazione_copre_i_campi_che_decidono():
    """Lo schema passato al modello e' cio' che il modello puo' trovare.

    Rendita catastale, categoria e canone compaiono di rado in un annuncio, ma
    quando ci sono valgono piu' di tutto il resto: la prima sblocca il
    prezzo-valore, la seconda decide moltiplicatore ed esclusione
    dall'agevolazione, il terzo determina l'intero calcolo del rendimento.
    Ometterli dallo schema significa non trovarli mai anche quando sono scritti
    in chiaro, e il modello non sbaglia nulla: non gli e' stato chiesto.
    """
    from immobiliare import annunci as A

    for campo in ("rendita_catastale", "categoria", "canone_atteso_mese",
                  "comune", "mq", "prezzo_richiesto", "spese_condominio_anno"):
        assert campo in A.CAMPI_ESTRAIBILI, f"{campo} non e' nello schema di estrazione"

    # Ogni campo dello schema deve esistere davvero nella dataclass, altrimenti
    # il modello lo estrae e la costruzione dell'annuncio lo scarta in silenzio.
    nomi = {f.name for f in __import__("dataclasses").fields(A.Annuncio)}
    for campo in A.CAMPI_ESTRAIBILI:
        assert campo in nomi, f"lo schema chiede {campo}, che non e' un campo di Annuncio"

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
            except Exception as e:
                falliti.append((nome, f"{e.__class__.__name__}: {e}"))
    print(f"{superati} test superati, {len(falliti)} falliti")
    for nome, errore in falliti:
        print(f"  FALLITO {nome}: {errore}")
    raise SystemExit(1 if falliti else 0)
