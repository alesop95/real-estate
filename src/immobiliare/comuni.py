"""Parametri comunali: dove si leggono, e che cosa risulta verificato e quando.

Due voci del modello non hanno un valore nazionale e vanno lette Comune per Comune: l'aliquota
IMU e l'imposta di soggiorno. Il registro delle fonti le dichiara da sempre come lacune, con la
stessa formula, cioè che l'unica fonte corretta è l'atto del Comune. Questo modulo non le risolve
inventando un valore: risolve il problema che le rendeva scomode, cioè ritrovare l'atto.

Il punto di partenza è che i due dati non sono fissi, e trattarli come tali sarebbe il difetto
peggiore possibile qui. L'aliquota IMU si ridelibera ogni anno: l'atto acquista efficacia per
l'anno se pubblicato sul portale del federalismo fiscale entro il 28 ottobre, e in mancanza
resta in vigore quello dell'anno prima. L'imposta di soggiorno cambia con ogni nuovo regolamento
o delibera di tariffe. Una tabella di valori congelati diventerebbe quindi una fonte di numeri
scaduti che sembrano verificati, che è esattamente ciò che il registro delle fonti esiste per
impedire. Per questo qui si tengono due cose diverse e separate: il collegamento all'atto, che è
stabile e si può costruire, e il valore che una persona ha letto in quell'atto, con la data in cui
l'ha fatto, che è un dato con una scadenza dichiarata.

Sull'IMU il collegamento si costruisce e non si conserva. Il Dipartimento delle finanze pubblica
i regolamenti e le delibere di tutti i Comuni in una applicazione interrogabile per codice
catastale del Comune e sigla della provincia, e quei due parametri bastano ad atterrare sulla
pagina del Comune giusto. Entrambi si leggono dalla fornitura OMI che il progetto ha già in
cache, nelle colonne `Comune_amm` e `Prov` del file delle zone, quindi non serve una tabella di
codici da mantenere: per i duecentoventicinque Comuni delle Marche oggi in cache il collegamento
esiste già, e per una regione nuova basta importarne la fornitura. L'unico passaggio che
resta manuale è la scelta dell'anno, che quella applicazione fa con un modulo e non con un
parametro nell'indirizzo.

Sull'imposta di soggiorno non esiste un registro nazionale interrogabile, e va detto invece di
farlo sembrare: il collegamento all'atto del singolo Comune si conserva nel registro delle
verifiche, una riga per Comune, perché è l'unico modo di non ricercarlo ogni volta.

Il modulo non fa rete. Costruisce indirizzi e legge file locali, così resta fuori dalla catena
che produce il workbook, secondo il principio già dichiarato per il generatore.
"""
from __future__ import annotations

import csv
import io
import datetime as _dt
from dataclasses import dataclass
from pathlib import Path

from . import omi

# Applicazione del Dipartimento delle finanze che pubblica regolamenti e delibere IMU di ogni
# Comune. I due parametri sono il codice catastale del Comune e la sigla della provincia; la
# pagina che ne risulta chiede soltanto l'anno. Verificato il 3 settembre 2026 su Civitanova
# Marche, codice C770, provincia MC.
MEF_DELIBERE = ("https://www1.finanze.gov.it/finanze2/dipartimentopolitichefiscali/"
                "fiscalitalocale/nuova_imu/sceltaanno.htm")

# Pagine istituzionali di contorno, per chi vuole capire l'adempimento invece di leggere un atto.
MEF_RICERCA = ("https://www.finanze.gov.it/it/fiscalita/fiscalita-regionale-e-locale/"
               "Imposta-municipale-propria-IMU/Regolamenti-e-aliquote-ricerca/")
MEF_ADEMPIMENTI = ("https://www.finanze.gov.it/it/fiscalita/fiscalita-regionale-e-locale/"
                   "Imposta-municipale-propria-IMU/regolamenti-e-aliquote-adempimenti-da-parte-"
                   "dei-comuni/")

ATTRIBUZIONE_MEF = "MEF - Dipartimento delle finanze"

# Termine di pubblicazione oltre il quale l'atto dell'anno non può più cambiare: 28 ottobre.
TERMINE_PUBBLICAZIONE = (10, 28)

REGISTRO_PREDEFINITO = Path("data/comuni-verifiche.csv")

CAMPI_REGISTRO = (
    "comune",
    "provincia",
    "codice_catastale",
    "aliquota_imu_altri",
    "aliquota_imu_principale",
    "imposta_soggiorno_notte",
    "link_delibera_imu",
    "link_imposta_soggiorno",
    "verificato_il",
    "note",
)


@dataclass(frozen=True)
class Comune:
    """Identificazione amministrativa di un Comune, come serve a costruire i collegamenti."""

    nome: str
    provincia: str
    regione: str
    codice_catastale: str
    codice_istat: str

    @property
    def link_delibere_imu(self) -> str:
        """Pagina del Dipartimento delle finanze con gli atti IMU di questo Comune."""
        return MEF_DELIBERE + "?cc=" + self.codice_catastale + "&pr=" + self.provincia


@dataclass(frozen=True)
class Verifica:
    """Che cosa una persona ha letto negli atti di un Comune, e quando."""

    comune: str
    provincia: str = ""
    codice_catastale: str = ""
    aliquota_imu_altri: float | None = None
    aliquota_imu_principale: float | None = None
    imposta_soggiorno_notte: float | None = None
    link_delibera_imu: str = ""
    link_imposta_soggiorno: str = ""
    verificato_il: _dt.date | None = None
    note: str = ""


def _righe_zone(cartella: str | Path = "data/omi"):
    """Le righe dei file di zona presenti in cache, da cui si ricavano i codici dei Comuni."""
    for _valori, zone in omi.file_correnti(cartella):
        if zone is None:
            continue
        for riga in omi._apri_csv(Path(zone)):
            yield riga


def elenca(cartella: str | Path = "data/omi") -> dict[str, Comune]:
    """I Comuni ricavabili dalla fornitura in cache, per nome normalizzato.

    La fornitura ripete ogni Comune una volta per zona, quindi la prima riga utile vince e le
    successive si scartano: i codici non cambiano fra le zone dello stesso Comune.
    """
    trovati: dict[str, Comune] = {}
    for riga in _righe_zone(cartella):
        nome = (riga.get("Comune_descrizione") or "").strip()
        codice = (riga.get("Comune_amm") or "").strip()
        if not nome or not codice:
            continue
        chiave = omi.normalizza_comune(nome)
        if chiave in trovati:
            continue
        trovati[chiave] = Comune(
            nome=nome,
            provincia=(riga.get("Prov") or "").strip(),
            regione=(riga.get("Regione") or "").strip(),
            codice_catastale=codice,
            codice_istat=(riga.get("Comune_ISTAT") or "").strip(),
        )
    return trovati


def trova(nome: str, cartella: str | Path = "data/omi") -> Comune | None:
    """Il Comune corrispondente al nome, con la normalizzazione già usata per le quotazioni."""
    return elenca(cartella).get(omi.normalizza_comune(nome))


def simili(nome: str, cartella: str | Path = "data/omi", massimo: int = 8) -> list[str]:
    """Nomi vicini a quello cercato, per rispondere con una proposta invece che con un no."""
    cercato = omi.normalizza_comune(nome)
    if not cercato:
        return []
    proposte = []
    for chiave, comune in elenca(cartella).items():
        if cercato in chiave or chiave.startswith(cercato[:4]):
            proposte.append(comune.nome)
    return sorted(proposte)[:massimo]


def _decimale(valore: str) -> float | None:
    testo = (valore or "").strip().replace(",", ".")
    if not testo:
        return None
    try:
        return float(testo)
    except ValueError:
        return None


def _data(valore: str) -> _dt.date | None:
    testo = (valore or "").strip()
    if not testo:
        return None
    try:
        return _dt.date.fromisoformat(testo)
    except ValueError:
        return None


def leggi_registro(percorso: str | Path = REGISTRO_PREDEFINITO) -> dict[str, Verifica]:
    """Il registro delle verifiche comunali, per nome normalizzato. Assente vale vuoto."""
    percorso = Path(percorso)
    if not percorso.exists():
        return {}
    testo = percorso.read_text(encoding="utf-8")
    lettore = csv.DictReader(io.StringIO(testo), delimiter=";")
    registro: dict[str, Verifica] = {}
    for riga in lettore:
        nome = (riga.get("comune") or "").strip()
        if not nome or nome.startswith("#"):
            continue
        registro[omi.normalizza_comune(nome)] = Verifica(
            comune=nome,
            provincia=(riga.get("provincia") or "").strip(),
            codice_catastale=(riga.get("codice_catastale") or "").strip(),
            aliquota_imu_altri=_decimale(riga.get("aliquota_imu_altri", "")),
            aliquota_imu_principale=_decimale(riga.get("aliquota_imu_principale", "")),
            imposta_soggiorno_notte=_decimale(riga.get("imposta_soggiorno_notte", "")),
            link_delibera_imu=(riga.get("link_delibera_imu") or "").strip(),
            link_imposta_soggiorno=(riga.get("link_imposta_soggiorno") or "").strip(),
            verificato_il=_data(riga.get("verificato_il", "")),
            note=(riga.get("note") or "").strip(),
        )
    return registro


def verifica_di(nome: str, registro: dict[str, Verifica]) -> Verifica | None:
    """La riga di registro di un Comune, cercata come si cerca una quotazione.

    Esiste perché la chiave del registro è il nome passato per la normalizzazione di `omi`, e
    chi chiama non deve conoscere quella convenzione: se un giorno cambiasse, cambierebbe qui.
    """
    return registro.get(omi.normalizza_comune(nome))


def stato_verifica(verificato_il: _dt.date | None, anno: int,
                   oggi: _dt.date | None = None) -> tuple[str, str]:
    """Se la lettura di un atto vale ancora per l'anno d'imposta chiesto, e perché.

    La regola discende dal termine del 28 ottobre. Un atto pubblicato entro quella data ha
    efficacia per l'anno; dopo quella data, per l'anno in corso non può più arrivarne uno nuovo.
    Ne seguono tre esiti. Una lettura fatta dopo il termine dell'anno chiesto è definitiva.
    Una lettura fatta nello stesso anno ma prima del termine è provvisoria, perché il Comune
    può ancora deliberare. Una lettura fatta in un anno precedente non vale per l'anno chiesto,
    perché o è stata superata da un atto nuovo o è stata prorogata per silenzio, e le due cose
    non si distinguono senza guardare l'atto.
    """
    if verificato_il is None:
        return "assente", "nessuna lettura registrata"
    oggi = oggi or _dt.date.today()
    termine = _dt.date(anno, *TERMINE_PUBBLICAZIONE)
    if verificato_il.year > anno:
        return "successiva", ("letta il " + verificato_il.isoformat() + ", dopo l'anno chiesto")
    if verificato_il.year < anno:
        return "scaduta", ("letta il " + verificato_il.isoformat() + ", riferita al "
                           + str(verificato_il.year) + " e non all'anno chiesto")
    if verificato_il > termine:
        return "definitiva", ("letta il " + verificato_il.isoformat()
                              + ", dopo il termine di pubblicazione del " + termine.isoformat())
    if oggi > termine:
        return "da rileggere", ("letta il " + verificato_il.isoformat()
                                + ", prima del termine del " + termine.isoformat()
                                + ", che è ormai passato: un atto nuovo può essere arrivato dopo")
    return "provvisoria", ("letta il " + verificato_il.isoformat()
                           + ", ma il Comune può deliberare fino al " + termine.isoformat())


def cosa_manca(verifica: Verifica | None) -> list[str]:
    """Le voci comunali non ancora lette, nell'ordine in cui conviene procurarsele."""
    mancanti = []
    if verifica is None or verifica.aliquota_imu_altri is None:
        mancanti.append("aliquota IMU per gli immobili diversi dall'abitazione principale")
    if verifica is None or verifica.imposta_soggiorno_notte is None:
        mancanti.append("imposta di soggiorno per notte, se il Comune l'ha istituita")
    return mancanti
