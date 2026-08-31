# -*- coding: utf-8 -*-
"""Quotazioni dell'Osservatorio del mercato immobiliare.

Le quotazioni OMI danno, per ogni zona omogenea di ogni Comune e per ogni
tipologia edilizia, l'intervallo di prezzo al metro quadro di compravendita e di
locazione. Sono la sola base pubblica e verificabile per dire se un prezzo
richiesto sta dentro il mercato della zona o fuori, e vanno preferite a qualunque
stima commerciale, che ha per definizione un interesse nel risultato.

Sulla via di accesso ai dati va detta una cosa netta, perche' cambia il modo di
usare questo modulo. La fornitura ufficiale e aggiornata passa dall'area riservata
di Fisconline o Entratel: e' gratuita ma richiede un'autenticazione personale che
uno script non puo' e non deve simulare, quindi il file va scaricato a mano una
volta a semestre e passato qui con `carica`. Il mirror open data di ondata, che
questo modulo sa scaricare da solo, e' ripubblicazione della stessa fonte ma si
ferma al secondo semestre 2018: serve per l'andamento storico di una zona, non per
il prezzo di oggi. La consultazione puntuale a video, infine, resta sempre
disponibile senza registrazione sul geopoi dell'Agenzia.
"""

from __future__ import annotations

import csv
import io
import urllib.request
from dataclasses import dataclass
from pathlib import Path

MIRROR = "https://raw.githubusercontent.com/ondata/quotazioni-immobiliari-agenzia-entrate/master/data"

SEMESTRI_MIRROR = {
    "2016-1": "QI_294586_1_20161",
    "2016-2": "QI_294583_1_20162",
    "2017-1": "QI_294582_1_20171",
    "2017-2": "QI_294581_1_20172",
    "2018-1": "QI_294585_1_20181",
    "2018-2": "QI_294577_1_20182",
}

CONSULTAZIONE_A_VIDEO = "https://www1.agenziaentrate.gov.it/servizi/geopoi_omi/index.php"
FORNITURA_UFFICIALE = "https://www.agenziaentrate.gov.it/portale/schede/fabbricatiterreni/omi/forniture-dati-omi-cittadini"


@dataclass
class Quotazione:
    """Una riga di quotazione: una tipologia, in una zona, in un semestre."""

    comune: str
    provincia: str
    fascia: str
    zona: str
    zona_descrizione: str
    tipologia: str
    stato: str
    compravendita_min: float
    compravendita_max: float
    locazione_min: float
    locazione_max: float

    @property
    def compravendita_media(self) -> float:
        return (self.compravendita_min + self.compravendita_max) / 2

    @property
    def locazione_media(self) -> float:
        return (self.locazione_min + self.locazione_max) / 2

    @property
    def rendimento_lordo_implicito(self) -> float:
        """Rendimento lordo che il mercato della zona esprime, canone su prezzo.

        E' il metro di paragone piu' onesto per un singolo annuncio: se l'immobile
        promette molto di piu' della sua zona, o e' un affare o c'e' qualcosa che
        non si e' capito, e la seconda ipotesi va esclusa prima di credere alla prima.
        """
        if not self.compravendita_media:
            return 0.0
        return self.locazione_media * 12 / self.compravendita_media


def _numero(valore: str) -> float:
    """Converte i numeri OMI, che usano la virgola come separatore decimale."""
    testo = (valore or "").strip().replace(".", "").replace(",", ".")
    try:
        return float(testo)
    except ValueError:
        return 0.0


def _apri_csv(percorso: Path):
    """Apre un CSV OMI riconoscendo delimitatore e riga di intestazione.

    Il mirror pubblica file con la virgola e l'intestazione sulla prima riga, mentre
    la fornitura ufficiale usa il punto e virgola e antepone una riga di metadati.
    Riconoscere entrambi evita di dover spiegare all'utente quale dei due ha in mano.
    """
    grezzo = percorso.read_text(encoding="utf-8-sig", errors="replace")
    righe = grezzo.splitlines()
    indice = 0
    for i, riga in enumerate(righe[:5]):
        if "Comune_descrizione" in riga or "Comune_amm" in riga:
            indice = i
            break
    intestazione = righe[indice]
    delimitatore = ";" if intestazione.count(";") > intestazione.count(",") else ","
    return csv.DictReader(io.StringIO("\n".join(righe[indice:])), delimiter=delimitatore)


def carica(percorso_valori: str | Path, percorso_zone: str | Path = "") -> list[Quotazione]:
    """Carica un file VALORI, arricchendolo con le descrizioni del file ZONE se c'e'."""
    percorso_valori = Path(percorso_valori)
    descrizioni: dict[tuple[str, str], str] = {}
    if percorso_zone:
        for riga in _apri_csv(Path(percorso_zone)):
            chiave = (riga.get("Comune_descrizione", ""), riga.get("Zona", ""))
            descrizioni[chiave] = (riga.get("Zona_Descr", "") or "").strip("'")

    quotazioni: list[Quotazione] = []
    for riga in _apri_csv(percorso_valori):
        comune = riga.get("Comune_descrizione", "")
        zona = riga.get("Zona", "")
        quotazioni.append(
            Quotazione(
                comune=comune,
                provincia=riga.get("Prov", ""),
                fascia=riga.get("Fascia", ""),
                zona=zona,
                zona_descrizione=descrizioni.get((comune, zona), ""),
                tipologia=riga.get("Descr_Tipologia", ""),
                stato=riga.get("Stato", ""),
                compravendita_min=_numero(riga.get("Compr_min", "")),
                compravendita_max=_numero(riga.get("Compr_max", "")),
                locazione_min=_numero(riga.get("Loc_min", "")),
                locazione_max=_numero(riga.get("Loc_max", "")),
            )
        )
    return quotazioni


def scarica_dal_mirror(semestre: str, cartella: str | Path = "data/omi") -> tuple[Path, Path]:
    """Scarica dal mirror open data la coppia di file di un semestre storico.

    I file sono di circa venti megabyte l'uno e coprono l'intero territorio
    nazionale: si scaricano una volta sola e restano in cache sul disco.
    """
    if semestre not in SEMESTRI_MIRROR:
        disponibili = ", ".join(sorted(SEMESTRI_MIRROR))
        raise ValueError(
            f"semestre {semestre} non presente nel mirror. Disponibili: {disponibili}. "
            f"Per i semestri recenti la fornitura va richiesta dall'area riservata: {FORNITURA_UFFICIALE}"
        )
    cartella = Path(cartella)
    cartella.mkdir(parents=True, exist_ok=True)
    prefisso = SEMESTRI_MIRROR[semestre]
    percorsi = []
    for suffisso in ("VALORI", "ZONE"):
        nome = f"{prefisso}_{suffisso}_utf8.csv"
        destinazione = cartella / nome
        if not destinazione.exists():
            richiesta = urllib.request.Request(
                f"{MIRROR}/{nome}", headers={"User-Agent": "valutazione-immobiliare/1.0"}
            )
            with urllib.request.urlopen(richiesta, timeout=300) as risposta:
                destinazione.write_bytes(risposta.read())
        percorsi.append(destinazione)
    return percorsi[0], percorsi[1]


def importa_fornitura(percorso: str | Path, cartella: str | Path = "data/omi") -> list[Path]:
    """Ingerisce la fornitura ufficiale scaricata a mano dall'area riservata.

    E' la via corretta e l'unica aggiornata. La fornitura si ottiene autenticandosi
    ai servizi telematici dell'Agenzia, che e' un'autenticazione personale: uno
    script non puo' simularla e non deve provarci. La consultazione a video del
    servizio geopoi, dal canto suo, e' un'applicazione senza API documentata e
    senza `robots.txt`, quindi in assenza di un permesso esplicito ci si astiene
    dall'automatizzarla.

    Questa funzione accetta l'archivio zip cosi' come arriva, oppure i CSV gia'
    estratti, li normalizza nella cartella di cache e restituisce i percorsi utili.

    Il percorso a video, una volta sola per semestre:
    servizi telematici dell'Agenzia, area riservata, Servizi ipotecari e catastali
    e Osservatorio del mercato immobiliare, Forniture OMI, Quotazioni immobiliari,
    scelta del semestre e dell'ambito territoriale, poi scarico del prodotto.
    """
    import shutil
    import zipfile

    percorso = Path(percorso)
    cartella = Path(cartella)
    cartella.mkdir(parents=True, exist_ok=True)
    if not percorso.exists():
        raise FileNotFoundError(f"non trovo {percorso}")

    estratti: list[Path] = []
    if percorso.suffix.lower() == ".zip":
        with zipfile.ZipFile(percorso) as z:
            for nome in z.namelist():
                if nome.lower().endswith(".csv"):
                    destinazione = cartella / Path(nome).name
                    with z.open(nome) as sorgente, destinazione.open("wb") as uscita:
                        shutil.copyfileobj(sorgente, uscita)
                    estratti.append(destinazione)
    elif percorso.suffix.lower() == ".csv":
        destinazione = cartella / percorso.name
        shutil.copyfile(percorso, destinazione)
        estratti.append(destinazione)
    else:
        raise ValueError(f"formato non riconosciuto: {percorso.suffix}. Attesi .zip o .csv")

    if not estratti:
        raise ValueError("nessun CSV trovato nell'archivio")
    return estratti


def elenca_zone(quotazioni: list[Quotazione], comune: str) -> list[tuple[str, str]]:
    """Zone omogenee di un Comune, per scegliere quella dell'immobile."""
    comune_norm = comune.strip().upper()
    viste: dict[str, str] = {}
    for q in quotazioni:
        if q.comune.strip().upper() == comune_norm and q.zona not in viste:
            viste[q.zona] = q.zona_descrizione
    return sorted(viste.items())


def cerca(
    quotazioni: list[Quotazione],
    comune: str,
    tipologia: str = "Abitazioni civili",
    zona: str = "",
) -> list[Quotazione]:
    """Filtra le quotazioni per Comune, tipologia e, se indicata, zona."""
    comune_norm = comune.strip().upper()
    tip_norm = tipologia.strip().lower()
    risultati = [
        q
        for q in quotazioni
        if q.comune.strip().upper() == comune_norm and tip_norm in q.tipologia.lower()
    ]
    if zona:
        zona_norm = zona.strip().upper()
        risultati = [
            q
            for q in risultati
            if q.zona.upper() == zona_norm or zona_norm in q.zona_descrizione.upper()
        ]
    return risultati


def sintesi_comune(quotazioni: list[Quotazione], comune: str, tipologia: str = "Abitazioni civili") -> dict:
    """Riassume in un dizionario l'intervallo di prezzi e canoni di un Comune."""
    righe = cerca(quotazioni, comune, tipologia)
    if not righe:
        return {}
    compr_min = min(q.compravendita_min for q in righe if q.compravendita_min) if any(q.compravendita_min for q in righe) else 0.0
    compr_max = max(q.compravendita_max for q in righe)
    loc_min = min((q.locazione_min for q in righe if q.locazione_min), default=0.0)
    loc_max = max(q.locazione_max for q in righe)
    medio = sum(q.compravendita_media for q in righe) / len(righe)
    rendimenti = [q.rendimento_lordo_implicito for q in righe if q.rendimento_lordo_implicito]
    return {
        "comune": comune,
        "zone": len(righe),
        "compravendita_min": compr_min,
        "compravendita_max": compr_max,
        "compravendita_media": medio,
        "locazione_min": loc_min,
        "locazione_max": loc_max,
        "rendimento_lordo_medio": sum(rendimenti) / len(rendimenti) if rendimenti else 0.0,
    }
