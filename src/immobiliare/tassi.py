# -*- coding: utf-8 -*-
"""Tassi di mercato correnti sui mutui casa, dalla fonte ufficiale.

Il modello prende il tasso come input, perche' il tasso che conta e' quello scritto
sul preventivo. Serve pero' un metro per capire se quel preventivo e' buono, cattivo
o normale, e per sapere che tasso mettere in una simulazione fatta prima di avere un
preventivo in mano.

La fonte e' il portale dati della Banca centrale europea, che pubblica le statistiche
sui tassi bancari armonizzate, note come MIR. Sono dati ufficiali, pubblici, senza
registrazione ne' chiave, aggiornati mensilmente, e riferiti alle nuove erogazioni
in Italia: sono cioe' esattamente la media di quello che le banche italiane hanno
davvero applicato, non un tasso pubblicitario ne' una stima.

Due avvertenze sull'uso. Il dato e' medio e ha uno o due mesi di ritardo, quindi dice
dove sta il mercato, non quale tasso otterrai tu: il tuo dipende da reddito, loan to
value, eta' e banca. E la media include operazioni molto diverse fra loro, per cui il
confronto sensato si fa con la serie della propria tipologia, fisso lungo oppure
variabile, non con la media generale.
"""

from __future__ import annotations

import csv
import io
import urllib.error
import urllib.request
from dataclasses import dataclass

BASE = "https://data-api.ecb.europa.eu/service/data"
TIMEOUT_SECONDI = 45

# Serie MIR, tassi bancari sulle nuove erogazioni a famiglie per acquisto abitazione
# in Italia. La quinta posizione della chiave e' il periodo di determinazione iniziale
# del tasso, che e' cio' che distingue un fisso da un variabile.
SERIE_MUTUI = {
    "media": ("MIR/M.IT.B.A2C.A.R.A.2250.EUR.N", "Media di tutte le nuove erogazioni"),
    "variabile": ("MIR/M.IT.B.A2C.F.R.A.2250.EUR.N", "Variabile, o rifissazione entro un anno"),
    "fisso_1_5": ("MIR/M.IT.B.A2C.I.R.A.2250.EUR.N", "Rifissazione fra uno e cinque anni"),
    "fisso_5_10": ("MIR/M.IT.B.A2C.O.R.A.2250.EUR.N", "Rifissazione fra cinque e dieci anni"),
    "fisso_lungo": ("MIR/M.IT.B.A2C.P.R.A.2250.EUR.N", "Fisso oltre dieci anni"),
}

# Indici di riferimento: l'Euribor indicizza i mutui a tasso variabile.
SERIE_INDICI = {
    "euribor_3m": ("FM/M.U2.EUR.RT.MM.EURIBOR3MD_.HSTA", "Euribor 3 mesi"),
    "euribor_6m": ("FM/M.U2.EUR.RT.MM.EURIBOR6MD_.HSTA", "Euribor 6 mesi"),
}

FONTE = "https://data.ecb.europa.eu/"


class TassiNonDisponibili(RuntimeError):
    """Il portale dati non risponde, o la serie richiesta non esiste piu'."""


@dataclass
class Osservazione:
    chiave: str
    descrizione: str
    periodo: str
    valore: float

    @property
    def tasso(self) -> float:
        """Il valore come frazione, pronto per i calcoli: 3,49 per cento diventa 0,0349."""
        return self.valore / 100


def _scarica(percorso: str, osservazioni: int) -> list[tuple[str, float]]:
    """Scarica una serie in CSV e restituisce le coppie periodo e valore."""
    url = f"{BASE}/{percorso}?lastNObservations={osservazioni}&format=csvdata"
    richiesta = urllib.request.Request(
        url, headers={"Accept": "text/csv", "User-Agent": "valutazione-immobiliare/1.0"}
    )
    try:
        with urllib.request.urlopen(richiesta, timeout=TIMEOUT_SECONDI) as risposta:
            testo = risposta.read().decode("utf-8", errors="replace")
    except urllib.error.URLError as e:
        raise TassiNonDisponibili(f"portale dati BCE non raggiungibile: {e.reason}") from e

    righe = list(csv.DictReader(io.StringIO(testo)))
    if not righe:
        raise TassiNonDisponibili(f"la serie {percorso} non ha restituito osservazioni")
    esito = []
    for riga in righe:
        periodo = riga.get("TIME_PERIOD", "")
        grezzo = riga.get("OBS_VALUE", "")
        if periodo and grezzo:
            try:
                esito.append((periodo, float(grezzo)))
            except ValueError:
                continue
    return esito


def ultimo(chiave: str, osservazioni: int = 1) -> Osservazione:
    """Ultima osservazione disponibile di una serie."""
    catalogo = {**SERIE_MUTUI, **SERIE_INDICI}
    if chiave not in catalogo:
        disponibili = ", ".join(sorted(catalogo))
        raise ValueError(f"serie sconosciuta: {chiave}. Disponibili: {disponibili}")
    percorso, descrizione = catalogo[chiave]
    dati = _scarica(percorso, osservazioni)
    periodo, valore = dati[-1]
    return Osservazione(chiave, descrizione, periodo, valore)


def serie(chiave: str, osservazioni: int = 24) -> list[tuple[str, float]]:
    """Andamento di una serie, per vedere se il mercato sale o scende."""
    catalogo = {**SERIE_MUTUI, **SERIE_INDICI}
    percorso, _ = catalogo[chiave]
    return _scarica(percorso, osservazioni)


def quadro_corrente() -> list[Osservazione]:
    """Tutte le serie in un colpo solo, saltando quelle che non rispondono."""
    esito = []
    for chiave in list(SERIE_MUTUI) + list(SERIE_INDICI):
        try:
            esito.append(ultimo(chiave))
        except (TassiNonDisponibili, ValueError):
            continue
    if not esito:
        raise TassiNonDisponibili("nessuna serie disponibile: verificare la connessione")
    return esito


@dataclass
class Confronto:
    """Esito del raffronto fra il tasso di un preventivo e il mercato."""

    tasso_offerto: float
    riferimento: Osservazione
    rata_offerta: float
    rata_riferimento: float
    interessi_offerti: float
    interessi_riferimento: float

    @property
    def scarto(self) -> float:
        """Differenza in punti percentuali. Negativo significa meglio del mercato."""
        return self.tasso_offerto - self.riferimento.tasso

    @property
    def differenza_interessi(self) -> float:
        """Quanto costa lo scarto, in euro, sull'intera durata."""
        return self.interessi_offerti - self.interessi_riferimento

    @property
    def giudizio(self) -> str:
        punti = self.scarto * 100
        if punti <= -0.30:
            return "sensibilmente sotto la media di mercato"
        if punti <= -0.10:
            return "sotto la media di mercato"
        if punti < 0.10:
            return "in linea con la media di mercato"
        if punti < 0.30:
            return "sopra la media di mercato"
        return "sensibilmente sopra la media di mercato"


def confronta_preventivo(
    tasso_offerto: float, importo: float, durata_anni: int, chiave: str = "fisso_lungo"
) -> Confronto:
    """Confronta il tasso di un preventivo con la media di mercato della sua tipologia.

    Traduce lo scarto in euro di interessi sull'intera durata, che e' l'unica forma in
    cui un decimo di punto diventa una cifra su cui vale la pena trattare.
    """
    from .calcoli import rata_francese

    riferimento = ultimo(chiave)
    rata_offerta = rata_francese(importo, tasso_offerto, durata_anni)
    rata_riferimento = rata_francese(importo, riferimento.tasso, durata_anni)
    rate = durata_anni * 12
    return Confronto(
        tasso_offerto=tasso_offerto,
        riferimento=riferimento,
        rata_offerta=rata_offerta,
        rata_riferimento=rata_riferimento,
        interessi_offerti=rata_offerta * rate - importo,
        interessi_riferimento=rata_riferimento * rate - importo,
    )
