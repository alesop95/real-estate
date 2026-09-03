# -*- coding: utf-8 -*-
"""Tassi di mercato correnti sui mutui casa, dalla fonte ufficiale.

Il modello prende il tasso come input, perché il tasso che conta è quello scritto
sul preventivo. Serve però un metro per capire se quel preventivo è buono, cattivo
o normale, e per sapere che tasso mettere in una simulazione fatta prima di avere un
preventivo in mano.

La fonte è il portale dati della Banca centrale europea, che pubblica le statistiche
sui tassi bancari armonizzate, note come MIR. Sono dati ufficiali, pubblici, senza
registrazione né chiave, aggiornati mensilmente, e riferiti alle nuove erogazioni
in Italia: sono cioè esattamente la media di quello che le banche italiane hanno
davvero applicato, non un tasso pubblicitario né una stima.

Due avvertenze sull'uso. Il dato è medio e ha uno o due mesi di ritardo, quindi dice
dove sta il mercato, non quale tasso otterrai tu: il tuo dipende da reddito, loan to
value, età e banca. E la media include operazioni molto diverse fra loro, per cui il
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
# in Italia. La quinta posizione della chiave è il periodo di determinazione iniziale
# del tasso, che è ciò che distingue un fisso da un variabile.
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
    """Il portale dati non risponde, o la serie richiesta non esiste più."""


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


@dataclass
class Risalita:
    """La peggiore risalita osservata dell'indice su una finestra di N mesi.

    Serve a rispondere a una domanda che nel foglio di calcolo si risponde a
    sentimento: quanto può salire un tasso variabile. La risposta a sentimento è
    di norma un punto percentuale, perché è l'ordine di grandezza che sembra
    prudente. La risposta empirica è che fra giugno 2022 e giugno 2023 l'Euribor a
    tre mesi è salito di 3,78 punti in dodici mesi, e chi aveva simulato un punto
    aveva simulato un quinto dello scenario che si è poi verificato.

    La finestra si misura sulla serie mensile pubblicata dalla Banca centrale
    europea, che parte dal gennaio 1994, quindi copre tre cicli di politica
    monetaria completi. Non è una previsione e non è un limite superiore: è il
    peggio che i dati disponibili contengono, che è l'unico riferimento onesto in
    assenza di una previsione, e va usato come misura di sostenibilità e non di
    probabilità.
    """

    mesi: int
    variazione: float
    """Punti percentuali di aumento, cioè 3,78 e non 0,0378."""
    periodo_iniziale: str
    periodo_finale: str
    valore_iniziale: float
    valore_finale: float

    @property
    def punti(self) -> float:
        """La variazione come frazione, pronta per il modello: 3,78 diventa 0,0378."""
        return self.variazione / 100


def risalite_storiche(
    chiave: str = "euribor_3m",
    finestre: tuple[int, ...] = (12, 24, 36),
    osservazioni: int = 400,
) -> list[Risalita]:
    """Per ogni finestra, la peggiore risalita contenuta nella serie storica.

    L'algoritmo è una scansione lineare su tutte le posizioni di partenza, non un
    massimo sui soli picchi: cercare il massimo assoluto e sottrargli il minimo
    assoluto darebbe un numero più grande e privo di significato, perché i due
    estremi possono stare a vent'anni di distanza e nessun mutuo li attraversa
    nella stessa finestra. Quello che serve è la peggiore finestra di durata
    fissata, che è la cosa che un piano di ammortamento incontra davvero.
    """
    dati = serie(chiave, osservazioni)
    esito = []
    for mesi in finestre:
        if len(dati) <= mesi:
            continue
        indice = max(
            range(len(dati) - mesi),
            key=lambda i: dati[i + mesi][1] - dati[i][1],
        )
        inizio, fine = dati[indice], dati[indice + mesi]
        esito.append(
            Risalita(
                mesi=mesi,
                variazione=fine[1] - inizio[1],
                periodo_iniziale=inizio[0],
                periodo_finale=fine[0],
                valore_iniziale=inizio[1],
                valore_finale=fine[1],
            )
        )
    return esito


def estremi_storici(chiave: str = "euribor_3m", osservazioni: int = 400) -> dict:
    """Massimo, minimo e copertura temporale della serie, per contesto.

    Il massimo storico serve a un controllo di sanità che il solo scarto non da':
    una risalita di quattro punti da un livello negativo arriva a un tasso che si
    è visto, mentre la stessa risalita dal livello di oggi arriverebbe a un tasso
    che nella serie non compare. La differenza va saputa prima di decidere se lo
    scenario è pessimistico o implausibile.
    """
    dati = serie(chiave, osservazioni)
    valori = [v for _, v in dati]
    return {
        "da": dati[0][0],
        "a": dati[-1][0],
        "osservazioni": len(dati),
        "corrente": valori[-1],
        "massimo": max(valori),
        "periodo_massimo": dati[valori.index(max(valori))][0],
        "minimo": min(valori),
        "periodo_minimo": dati[valori.index(min(valori))][0],
    }


@dataclass
class Gradino:
    """Un anello della catena che porta dal tasso di politica monetaria alla rata."""

    nome: str
    valore: float
    periodo: str
    spiegazione: str
    scarto_dal_precedente: float | None = None


def catena_dei_tassi(tasso_preventivo: float | None = None) -> list[Gradino]:
    """Scompone il tasso di un mutuo negli anelli che lo determinano.

    Serve a rispondere a una domanda che il singolo numero non fa vedere: quando
    una banca offre il tre virgola due per cento, quanto di quel numero è
    politica monetaria, quanto è prezzo del tempo e del rischio di credito fra
    banche, e quanto è margine della banca. Le tre componenti si muovono per
    ragioni diverse e su tempi diversi, e distinguerle cambia il modo di trattare:
    sul primo anello non si negozia, sul terzo si.

    I quattro anelli, in ordine.

    Il primo è l'euro short-term rate, che la Banca centrale europea pubblica
    ogni giorno lavorativo TARGET2 sulle operazioni non garantite a un giorno
    concluse il giorno prima. È un tasso a consuntivo calcolato su transazioni
    davvero avvenute, non una quotazione dichiarata, ed è il riferimento più
    vicino al costo del denaro senza rischio di durata: al 1 settembre 2026 vale
    il 2,188 per cento su 895 transazioni per 61 miliardi fra 47 banche.

    Il secondo è l'Euribor a tre mesi, cioè lo stesso mercato ma su una durata
    di tre mesi invece di uno giorno. Lo scarto fra i due è il prezzo di
    prestare per tre mesi invece che per una notte, e contiene sia l'attesa su
    dove andrà la politica monetaria in quel trimestre sia il rischio che la
    controparte non restituisca. In un ciclo di rialzi atteso l'Euribor sta sopra
    l'overnight, in uno di ribassi può starci sotto: il segno di questo scarto è
    quindi una lettura di aspettativa, non una costante.

    Il terzo è il tasso medio che le banche italiane hanno davvero applicato
    alle nuove erogazioni per acquisto di abitazione, dalle statistiche
    armonizzate MIR. Lo scarto rispetto all'anello precedente è il margine del
    sistema bancario, e comprende costo del capitale di vigilanza, rischio di
    credito del mutuatario, costi operativi e profitto.

    Il quarto, se lo si passa, è il tasso del proprio preventivo, e lo scarto
    rispetto alla media dice se si sta trattando meglio o peggio del mercato.

    Un'avvertenza sulla comparabilità che va detta perché la scomposizione la
    suggerisce e i dati non la sostengono del tutto. Le due serie di mercato sono
    giornaliera e mensile, la serie MIR è mensile con uno o due mesi di ritardo,
    quindi gli anelli non sono contemporanei e gli scarti si leggono come ordini
    di grandezza. E un mutuo a tasso fisso non è indicizzato all'Euribor ma
    all'IRS di pari durata, che questo progetto non legge: sul fisso la catena
    resta valida come scomposizione concettuale e non come identità numerica.
    """
    anelli = []

    from . import indicatori as N

    try:
        estr = N.estr()
        anelli.append(
            Gradino(
                nome="Euro short-term rate, overnight",
                valore=estr.valore,
                periodo=estr.periodo,
                spiegazione="Costo del denaro a un giorno fra banche, non garantito, calcolato dalla BCE sulle transazioni del giorno lavorativo precedente",
            )
        )
    except Exception:
        pass

    try:
        eur3 = ultimo("euribor_3m")
        precedente = anelli[-1].valore if anelli else None
        anelli.append(
            Gradino(
                nome="Euribor 3 mesi",
                valore=eur3.valore,
                periodo=eur3.periodo,
                spiegazione="Lo stesso mercato su tre mesi invece di un giorno: lo scarto è il prezzo della durata più il rischio di controparte, e riflette dove il mercato si aspetta che vada la politica monetaria",
                scarto_dal_precedente=None if precedente is None else eur3.valore - precedente,
            )
        )
    except (TassiNonDisponibili, ValueError):
        pass

    try:
        mir = ultimo("variabile")
        precedente = anelli[-1].valore if anelli else None
        anelli.append(
            Gradino(
                nome="Mutui a tasso variabile, media Italia",
                valore=mir.valore,
                periodo=mir.periodo,
                spiegazione="Quello che le banche italiane hanno davvero applicato: lo scarto sull'indice è il margine del sistema, cioè costo del capitale di vigilanza, rischio di credito, costi operativi e profitto",
                scarto_dal_precedente=None if precedente is None else mir.valore - precedente,
            )
        )
    except (TassiNonDisponibili, ValueError):
        pass

    if tasso_preventivo:
        precedente = anelli[-1].valore if anelli else None
        anelli.append(
            Gradino(
                nome="Il tuo preventivo",
                valore=tasso_preventivo * 100,
                periodo="oggi",
                spiegazione="Lo scarto sulla media è l'unico anello su cui si tratta, e vale la pena chiedere un secondo preventivo se è positivo",
                scarto_dal_precedente=None if precedente is None else tasso_preventivo * 100 - precedente,
            )
        )

    return anelli


FONTE_ESTR = "https://www.ecb.europa.eu/stats/financial_markets_and_interest_rates/euro_short-term_rate/html/index.en.html"


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

    Traduce lo scarto in euro di interessi sull'intera durata, che è l'unica forma in
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
