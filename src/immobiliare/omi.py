# -*- coding: utf-8 -*-
"""Quotazioni dell'Osservatorio del mercato immobiliare.

Le quotazioni OMI danno, per ogni zona omogenea di ogni Comune e per ogni
tipologia edilizia, l'intervallo di prezzo al metro quadro di compravendita e di
locazione. Sono la sola base pubblica e verificabile per dire se un prezzo
richiesto sta dentro il mercato della zona o fuori, e vanno preferite a qualunque
stima commerciale, che ha per definizione un interesse nel risultato.

Sulla via di accesso ai dati va detta una cosa netta, perché cambia il modo di
usare questo modulo. La fornitura ufficiale e aggiornata passa dall'area riservata
di Fisconline o Entratel: è gratuita ma richiede un'autenticazione personale che
uno script non può e non deve simulare, quindi il file va scaricato a mano una
volta a semestre e passato qui con `carica`. Il mirror open data di ondata, che
questo modulo sa scaricare da solo, è ripubblicazione della stessa fonte ma si
ferma al secondo semestre 2018: serve per l'andamento storico di una zona, non per
il prezzo di oggi. La consultazione puntuale a video, infine, resta sempre
disponibile senza registrazione sul geopoi dell'Agenzia.
"""

from __future__ import annotations

import csv
import io
import re
import urllib.request
from dataclasses import dataclass
from datetime import datetime
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

# Le condizioni della fornitura impongono di citare la fonte quando i dati
# vengono usati. Non è una cortesia bibliografica: è un obbligo assunto
# accettando le condizioni generali di accesso, e va assolto ovunque i valori
# compaiano, cioè nell'uscita a video e nel foglio delle fonti del workbook.
ATTRIBUZIONE = "Agenzia Entrate - OMI"

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

        È il metro di paragone più onesto per un singolo annuncio: se l'immobile
        promette molto di più della sua zona, o è un affare o c'è qualcosa che
        non si è capito, e la seconda ipotesi va esclusa prima di credere alla prima.
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


def _leggi_testo(percorso: Path) -> str:
    """Legge un CSV OMI riconoscendo la codifica invece di darla per scontata.

    Il mirror pubblica file già in UTF-8 e lo dichiara nel nome. La fornitura
    ufficiale dell'area riservata arriva invece nella codifica ANSI di Windows, e
    decodificarla come UTF-8 non solleva alcun errore: sostituisce ogni carattere
    accentato con il segnaposto di rimpiazzo. Il file si carica, le quotazioni si
    calcolano, e un Comune come FORLI' o una zona con l'apostrofo diventano
    irriconoscibili alla ricerca per nome. È un difetto che non si vede finché
    non si cerca proprio quel Comune, quindi si presidia qui.
    """
    grezzo = percorso.read_bytes()
    for codifica in ("utf-8-sig", "cp1252", "latin-1"):
        try:
            testo = grezzo.decode(codifica)
        except UnicodeDecodeError:
            continue
        if "�" not in testo:
            return testo
    # Ultima spiaggia: si decodifica comunque, segnalando la perdita.
    return grezzo.decode("utf-8", errors="replace")


def _apri_csv(percorso: Path):
    """Apre un CSV OMI riconoscendo delimitatore e riga di intestazione.

    Il mirror pubblica file con la virgola e l'intestazione sulla prima riga, mentre
    la fornitura ufficiale usa il punto e virgola e antepone una riga di metadati.
    Riconoscere entrambi evita di dover spiegare all'utente quale dei due ha in mano.
    """
    grezzo = _leggi_testo(percorso)
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
    """Carica un file VALORI, arricchendolo con le descrizioni del file ZONE se c'è."""
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


def semestre_del_file(percorso: Path) -> str:
    """Semestre di un file della fornitura, nella forma AAAAS, per esempio 20252.

    Si prova nell'ordine il nome del file, che nella fornitura porta un token di
    cinque cifre, poi la riga di metadati che alcune forniture antepongono al
    tracciato, e infine la data di modifica del file.

    L'ordine è scelto perché l'errore da evitare ha una direzione. Se il
    semestre restasse ignoto, il confronto lo ordinerebbe sotto qualunque valore
    noto, e una fornitura nuova con un nome inatteso perderebbe contro i file
    vecchi già in cache: il programma continuerebbe a rispondere con dati di
    anni prima senza dire nulla. Il ripiego sulla data di modifica sbaglia al
    massimo attribuendo il file al semestre corrente, che è l'errore innocuo,
    perché lo fa vincere e non perdere.
    """
    for pezzo in percorso.stem.split("_"):
        if len(pezzo) == 5 and pezzo.isdigit() and pezzo[-1] in "12":
            return pezzo

    try:
        with percorso.open(encoding="utf-8", errors="replace") as f:
            for _ in range(2):
                riga = f.readline()
                if not riga:
                    break
                trovato = re.search(r"anno\s*(\d{4}).*?semestre\s*([12])", riga, re.IGNORECASE)
                if trovato:
                    return f"{trovato.group(1)}{trovato.group(2)}"
                trovato = re.search(r"\b(\d{4})\s*/\s*([12])\b", riga)
                if trovato:
                    return f"{trovato.group(1)}{trovato.group(2)}"
    except OSError:
        pass

    modificato = datetime.fromtimestamp(percorso.stat().st_mtime)
    return f"{modificato.year}{1 if modificato.month <= 6 else 2}"


def file_correnti(cartella: str | Path) -> list[tuple[Path, Path | None]]:
    """Coppie valori e zone del semestre più recente presente in cache.

    Restituisce tutte le coppie di quel semestre, non una sola: chi scarica per
    provincia si ritrova un file per provincia, e leggerne uno solo significava
    cercare un Comune in una provincia diversa e concludere che non esistesse.
    L'accoppiamento fra un file di valori e il suo file di zone passa per il
    prefisso comune, perché nella fornitura i due condividono l'identificativo.
    """
    cartella = Path(cartella)
    valori = sorted(cartella.glob("*VALORI*.csv"))
    if not valori:
        # Cache popolata a mano, senza la convenzione di nome della fornitura.
        soli = sorted(cartella.glob("*.csv"))
        return [(f, None) for f in soli]

    semestri = {semestre_del_file(f) for f in valori}
    piu_recente = max(semestri) if semestri != {""} else ""
    scelti = [f for f in valori if semestre_del_file(f) == piu_recente]

    zone = sorted(cartella.glob("*ZONE*.csv"))
    coppie: list[tuple[Path, Path | None]] = []
    for f in scelti:
        prefisso = f.name.replace("VALORI", "ZONE")
        gemello = next((z for z in zone if z.name == prefisso), None)
        if gemello is None:
            # Ripiego: una sola zona dello stesso semestre, se c'è.
            gemello = next((z for z in zone if semestre_del_file(z) == semestre_del_file(f)), None)
        coppie.append((f, gemello))
    return coppie


def carica_cartella(cartella: str | Path) -> tuple[list[Quotazione], list[str]]:
    """Carica tutte le quotazioni del semestre più recente in cache.

    Restituisce anche i nomi dei file letti, perché su questi dati sapere da
    quale fornitura viene un numero fa parte del numero.
    """
    quotazioni: list[Quotazione] = []
    letti: list[str] = []
    for valori, zone in file_correnti(cartella):
        quotazioni.extend(carica(valori, zone or ""))
        letti.append(valori.name)
    return quotazioni, letti


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

    È la via corretta e l'unica aggiornata. La fornitura si ottiene autenticandosi
    ai servizi telematici dell'Agenzia, che è un'autenticazione personale: uno
    script non può simularla e non deve provarci. La consultazione a video del
    servizio geopoi, dal canto suo, è un'applicazione senza API documentata e
    senza `robots.txt`, quindi in assenza di un permesso esplicito ci si astiene
    dall'automatizzarla.

    Questa funzione accetta l'archivio zip così come arriva, oppure i CSV già
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
    comune_norm = normalizza_comune(comune)
    viste: dict[str, str] = {}
    for q in quotazioni:
        if normalizza_comune(q.comune) == comune_norm and q.zona not in viste:
            viste[q.zona] = q.zona_descrizione
    return sorted(viste.items())


def normalizza_comune(nome: str) -> str:
    """Riduce un nome di Comune alla forma con cui si può confrontare.

    Nella fornitura i nomi non sono scritti come li scrive una persona. Gli
    apostrofi possono essere accento grave o apostrofo tipografico invece di
    quello dritto, e i prefissi agiografici sono abbreviati in modi diversi:
    nella stessa provincia convivono SANT`ELPIDIO A MARE e S BENEDETTO DEL
    TRONTO. Un confronto letterale su questi nomi risponde "nessuna quotazione"
    a chi digita il nome corretto, e quel silenzio si legge come "Comune non
    coperto", che è una conclusione sbagliata presa su una risposta plausibile.
    """
    testo = (nome or "").strip().upper()
    for apostrofo in ("`", "’", "´", "'"):
        testo = testo.replace(apostrofo, " ")
    testo = testo.replace(".", " ").replace("-", " ")
    parole = []
    for parola in testo.split():
        # SAN, SANT, SANTA, SANTO e le loro abbreviazioni collassano su S.
        if parola in ("SAN", "SANT", "SANTA", "SANTO", "SS", "S"):
            parola = "S"
        parole.append(parola)
    return " ".join(parole)


def comuni_simili(quotazioni: list[Quotazione], comune: str, massimo: int = 8) -> list[str]:
    """Nomi presenti nei dati che somigliano a quello cercato.

    Serve a trasformare un risultato vuoto in un suggerimento. Confronta prima
    la forma normalizzata, poi l'inclusione di una parola significativa, così
    che chi cerca Porto Sant'Elpidio trovi PORTO SANT`ELPIDIO anche digitando
    l'apostrofo giusto, e chi cerca San Benedetto del Tronto arrivi comunque a
    S BENEDETTO DEL TRONTO.
    """
    cercato = normalizza_comune(comune)
    if not cercato:
        return []
    parole = [p for p in cercato.split() if len(p) > 2]
    candidati: list[str] = []
    for nome in sorted({q.comune for q in quotazioni}):
        normalizzato = normalizza_comune(nome)
        if normalizzato == cercato:
            return [nome]
        if cercato in normalizzato or (parole and all(p in normalizzato for p in parole)):
            candidati.append(nome)
        if len(candidati) >= massimo:
            break
    return candidati


def cerca(
    quotazioni: list[Quotazione],
    comune: str,
    tipologia: str = "Abitazioni civili",
    zona: str = "",
) -> list[Quotazione]:
    """Filtra le quotazioni per Comune, tipologia e, se indicata, zona."""
    comune_norm = normalizza_comune(comune)
    tip_norm = tipologia.strip().lower()
    risultati = [
        q
        for q in quotazioni
        if normalizza_comune(q.comune) == comune_norm and tip_norm in q.tipologia.lower()
    ]
    if zona:
        zona_norm = zona.strip().upper()
        risultati = [
            q
            for q in risultati
            if q.zona.upper() == zona_norm or zona_norm in q.zona_descrizione.upper()
        ]
    return risultati


def quotazione_di_riferimento(
    quotazioni: list[Quotazione],
    comune: str,
    zona: str = "",
    tipologia: str = "Abitazioni civili",
) -> tuple[float, float, str]:
    """Intervallo di prezzo da usare come riferimento per un annuncio.

    Restituisce minimo, massimo e una dicitura che dice da dove vengono, perché
    i due numeri da soli non bastano a giudicarli. Con la zona indicata si usa
    quella zona, ed è il confronto giusto; senza, si ripiega sull'intero Comune,
    che su un Comune di costa mette insieme il lungomare e le zone agricole e
    produce una forbice così larga da non dire quasi nulla. La dicitura serve a
    ricordarlo a chi legge il numero un mese dopo.

    Sullo stato conservativo la scelta è di restare su NORMALE quando c'è:
    OTTIMO descrive un immobile ristrutturato di recente, e assumerlo come
    riferimento farebbe sembrare a buon mercato qualunque cosa.
    """
    righe = cerca(quotazioni, comune, tipologia, zona)
    if not righe:
        return 0.0, 0.0, ""

    normali = [r for r in righe if r.stato.strip().upper().startswith("NORMALE")]
    scelte = normali or righe
    stato = "stato normale" if normali else "tutti gli stati"

    minimo = min(r.compravendita_min for r in scelte if r.compravendita_min) if scelte else 0.0
    massimo = max(r.compravendita_max for r in scelte if r.compravendita_max) if scelte else 0.0

    if zona:
        provenienza = f"zona {zona.strip().upper()}, {stato}"
    else:
        provenienza = f"intero Comune, {stato}, {len(scelte)} righe: forbice larga, indicare la zona"
    return minimo, massimo, provenienza


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
