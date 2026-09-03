# -*- coding: utf-8 -*-
"""Indicatori di contesto: tasso a breve dell'area euro e inflazione italiana.

Sono le due grandezze che il modello usa come assunzione e che quasi nessuno
verifica prima di lasciarle al valore predefinito. L'inflazione attesa entra
nella proiezione del flusso di cassa, nella rivalutazione dell'immobile e nel
confronto con il portafoglio alternativo, e un punto di scarto su venticinque
anni sposta il risultato più di quasi ogni altra ipotesi. Il tasso a breve
serve a un'altra domanda, cioè se la media mensile sui mutui, che esce con due
mesi di ritardo, sia già vecchia e in che direzione.

Nessuna delle due fonti richiede chiave o registrazione, ed entrambe degradano
senza bloccare il resto: se non rispondono, i valori restano quelli dichiarati
in `parametri.py` e il workbook funziona lo stesso.

L'idea di seguire queste due grandezze insieme viene dal canale open source
`finanza-che-conta` (https://github.com/Loenus/finanza-che-conta), che pubblica
l'euro short-term rate ogni lunedi' e l'inflazione ISTAT a ogni comunicato, ed
è anche la fonte da cui è stato individuato l'identificativo del flusso SDMX
dei prezzi al consumo. Il repository non dichiara una licenza, quindi non ne è
stato ripreso codice: qui c'è un client scritto da zero sullo stesso endpoint
pubblico.
"""

from __future__ import annotations

import csv
import io
import urllib.error
import urllib.request
from dataclasses import dataclass

TIMEOUT_SECONDI = 60
# Il servizio SDMX di ISTAT risponde in decine di secondi anche per poche righe:
# un timeout tarato sulla BCE lo farebbe fallire sempre.
TIMEOUT_ISTAT = 180

# Euro short-term rate, pubblicato dalla BCE stessa ogni giorno lavorativo. È
# l'unica grandezza di questo modulo davvero aggiornata al giorno prima, e per
# questo serve da termometro rispetto alle medie mensili sui mutui.
BASE_BCE = "https://data-api.ecb.europa.eu/service/data"
SERIE_ESTR = ("EST/B.EU000A2X2A25.WT", "Euro short-term rate, tasso overnight")
SERIE_HICP = {
    "hicp_italia": ("ICP/M.IT.N.000000.4.ANR", "Indice armonizzato Italia, variazione annua"),
    "hicp_area_euro": ("ICP/M.U2.N.000000.4.ANR", "Indice armonizzato area euro, variazione annua"),
    "hicp_italia_core": ("ICP/M.IT.N.XEF000.4.ANR", "Indice armonizzato Italia al netto di energia e alimentari"),
}

# Prezzi al consumo per l'intera collettività, il NIC, dal servizio SDMX di
# ISTAT. Il vecchio endpoint `sdmx.istat.it/SDMXWS` oggi rimanda alla home:
# l'indirizzo vivo è quello sotto. L'ordine delle dimensioni, verificato sul
# data structure definition, è FREQ.REF_AREA.DATA_TYPE.MEASURE.COICOP, e la
# chiave con i punti vuoti chiede tutte le combinazioni per l'Italia mensile.
BASE_ISTAT = "https://esploradati.istat.it/SDMXWS/rest/data"
FLUSSO_NIC = "IT1,167_744_DF_DCSP_NIC1B2015_1,1.0"
CHIAVE_NIC = "M.IT..."

# Codici della dimensione MEASURE nel flusso NIC. La corrispondenza è stata
# verificata sui valori: a dicembre 2025 la misura 7 vale 1,2 per cento, che
# coincide con l'indice armonizzato Italia dello stesso mese letto dalla BCE.
MISURE_NIC = {
    "4": ("indice", "Indice generale NIC, base 2015 uguale a cento"),
    "6": ("congiunturale", "Variazione percentuale sul mese precedente"),
    "7": ("tendenziale", "Variazione percentuale sullo stesso mese dell'anno precedente, cioè l'inflazione"),
}

FONTI = {
    "estr": "https://data.ecb.europa.eu/",
    "hicp": "https://data.ecb.europa.eu/",
    "nic_istat": "https://esploradati.istat.it/",
    "comunicati_istat": "https://www.istat.it/tag/prezzi-al-consumo/",
    "ispirazione": "https://github.com/Loenus/finanza-che-conta",
}


class IndicatoriNonDisponibili(RuntimeError):
    """La fonte non risponde, o la serie richiesta non esiste più."""


@dataclass(frozen=True)
class Osservazione:
    """Un valore con il suo periodo e la sua fonte.

    Il periodo non è un ornamento: è la metà dell'informazione. Un tasso di
    inflazione senza la data a cui si riferisce non dice se la si sta usando
    come dato corrente o come reperto.
    """

    chiave: str
    descrizione: str
    periodo: str
    valore: float
    fonte: str

    @property
    def frazione(self) -> float:
        """Il valore come frazione: 1,2 per cento diventa 0,012."""
        return self.valore / 100


def _csv_bce(percorso: str, osservazioni: int) -> list[tuple[str, float]]:
    url = f"{BASE_BCE}/{percorso}?lastNObservations={osservazioni}&format=csvdata"
    return _preleva(url, "portale dati BCE")


def _preleva(url: str, etichetta: str) -> list[tuple[str, float]]:
    richiesta = urllib.request.Request(
        url, headers={"Accept": "text/csv", "User-Agent": "valutazione-immobiliare/1.0"}
    )
    try:
        with urllib.request.urlopen(richiesta, timeout=TIMEOUT_SECONDI) as risposta:
            testo = risposta.read().decode("utf-8", errors="replace")
    except (urllib.error.URLError, TimeoutError, OSError) as e:
        # `TimeoutError` sul socket non discende da `URLError`: catturare solo
        # quest'ultima farebbe uscire l'eccezione dal modulo e cadere l'intero
        # comando invece di degradare, che è il contratto di questo file.
        raise IndicatoriNonDisponibili(f"{etichetta} non raggiungibile: {e}") from e

    esito: list[tuple[str, float]] = []
    for riga in csv.DictReader(io.StringIO(testo)):
        periodo = riga.get("TIME_PERIOD", "")
        grezzo = riga.get("OBS_VALUE", "")
        if not periodo or not grezzo:
            continue
        try:
            esito.append((periodo, float(grezzo)))
        except ValueError:
            continue
    if not esito:
        raise IndicatoriNonDisponibili(f"{etichetta}: nessuna osservazione restituita")
    return esito


def estr(osservazioni: int = 1) -> Osservazione:
    """Ultimo euro short-term rate disponibile."""
    percorso, descrizione = SERIE_ESTR
    dati = _csv_bce(percorso, osservazioni)
    periodo, valore = dati[-1]
    return Osservazione("estr", descrizione, periodo, valore, FONTI["estr"])


def hicp(chiave: str = "hicp_italia", osservazioni: int = 1) -> Osservazione:
    """Inflazione armonizzata dal portale dati della BCE."""
    if chiave not in SERIE_HICP:
        raise ValueError(f"serie sconosciuta: {chiave}. Disponibili: {', '.join(sorted(SERIE_HICP))}")
    percorso, descrizione = SERIE_HICP[chiave]
    dati = _csv_bce(percorso, osservazioni)
    periodo, valore = dati[-1]
    return Osservazione(chiave, descrizione, periodo, valore, FONTI["hicp"])


def _misure_nic(osservazioni: int = 1) -> list[dict]:
    """Righe grezze del flusso NIC, con tutte le dimensioni."""
    url = (
        f"{BASE_ISTAT}/{FLUSSO_NIC}/{CHIAVE_NIC}"
        f"?lastNObservations={osservazioni}&format=csv"
    )
    richiesta = urllib.request.Request(
        url, headers={"Accept": "text/csv", "User-Agent": "valutazione-immobiliare/1.0"}
    )
    try:
        with urllib.request.urlopen(richiesta, timeout=TIMEOUT_ISTAT) as risposta:
            testo = risposta.read().decode("utf-8", errors="replace")
    except (urllib.error.URLError, TimeoutError, OSError) as e:
        raise IndicatoriNonDisponibili(f"servizio SDMX di ISTAT non raggiungibile: {e}") from e
    righe = [r for r in csv.DictReader(io.StringIO(testo)) if r.get("OBS_VALUE")]
    if not righe:
        raise IndicatoriNonDisponibili("il flusso dei prezzi al consumo non ha restituito osservazioni")
    return righe


def nic_istat(osservazioni: int = 1) -> list[Osservazione]:
    """Indice nazionale dei prezzi al consumo, indice generale.

    Restituisce le misure disponibili per l'ultimo periodo pubblicato. Il
    periodo va guardato: ISTAT ribasa l'indice ogni cinque anni e il flusso
    della base precedente smette di ricevere osservazioni, quindi un valore
    fermo a un dicembre è il segnale che la serie corrente è altrove.
    """
    righe = _misure_nic(osservazioni)
    esito: list[Osservazione] = []
    for riga in righe:
        coicop = riga.get("E_COICOP_REV_ISTAT", "")
        # 00 è l'indice generale; le altre voci sono le divisioni di spesa.
        if coicop != "00":
            continue
        misura = riga.get("MEASURE", "")
        nome, descrizione = MISURE_NIC.get(misura, (f"misura_{misura}", f"NIC, misura {misura}"))
        esito.append(
            Osservazione(
                chiave=f"nic_{nome}",
                descrizione=descrizione,
                periodo=riga.get("TIME_PERIOD", ""),
                valore=float(riga["OBS_VALUE"]),
                fonte=FONTI["nic_istat"],
            )
        )
    if not esito:
        raise IndicatoriNonDisponibili("nessuna misura sull'indice generale nel flusso restituito")
    return esito


def quadro() -> list[Osservazione]:
    """Tutti gli indicatori raggiungibili, saltando quelli che non rispondono."""
    esito: list[Osservazione] = []
    try:
        esito.append(estr())
    except IndicatoriNonDisponibili:
        pass
    for chiave in SERIE_HICP:
        try:
            esito.append(hicp(chiave))
        except IndicatoriNonDisponibili:
            pass
    try:
        esito.extend(nic_istat())
    except IndicatoriNonDisponibili:
        pass
    return esito
