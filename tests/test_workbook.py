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
        "Guida", "Parametri", "Immobile", "Mutuo", "Ammortamento", "Locazione",
        "Cash flow", "Metriche", "Confronto affitto", "Scenari", "Checklist",
        "Annunci", "Confronto immobili", "Fonti",
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
        "ltv_conf", "aliquota_conf", "irpef_marginale",
        "accantonamento_ristrutturazione",
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
            rendita_catastale=500, categoria="A/3", canone_atteso_mese=520, note="prova",
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
        21: None, 23: 500, 24: "A/3", 28: 520, 31: "prova",
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
