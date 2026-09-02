# -*- coding: utf-8 -*-
"""Scheda di una pagina per la trattativa, in LaTeX.

Esiste per un momento preciso del percorso: quando si entra in agenzia, o si
telefona al venditore, e servono in mano quattro numeri e un elenco. I quattro
numeri sono il costo reale dell'operazione, che non e' il prezzo, il rendimento
netto reale, il prezzo massimo che l'immobile giustifica ai propri criteri, e lo
sconto che ne consegue. L'elenco e' quello dei dati che mancano, perche' la
telefonata serve anche a chiederli.

Il workbook risponde alle stesse domande e non serve a questo: e' un file di
ventun fogli che si consulta da fermi, e in trattativa non si apre. La scheda e'
l'estrazione di cio' che si porta con se'.

Tre scelte di progetto vanno dichiarate.

La prima e' che la scheda calcola con il motore Python e non legge il workbook:
sono due implementazioni della stessa matematica, e usare la prima rende la
scheda un terzo riscontro invece di una copia.

La seconda e' che i dati mancanti non vengono taciuti ne' sostituiti con valori
plausibili: compaiono in un elenco, la scheda si dichiara incompleta in testa, e
ogni numero che dipende da un dato assente non viene stampato affatto. La prima
versione lo stampava, e il risultato e' stato istruttivo: su un immobile senza
canone atteso il prezzo massimo sostenibile risultava meno seimila euro, e la
casella della trattativa annunciava uno sconto da ottenere del centoquattro per
cento del prezzo. Aritmeticamente corretto, operativamente assurdo, e con la
faccia di un obiettivo di negoziazione.

La terza riguarda la separazione fra testo e marcatura, ed e' nata da un difetto
osservato solo guardando il PDF compilato. Le prime versioni passavano etichette
e note per la funzione che sfugge i caratteri speciali di LaTeX, e in quelle
etichette c'era del LaTeX: il documento stampava alla lettera il comando del
grassetto, e in una nota il segno di percentuale compariva preceduto da una barra
rovesciata. La regola che ne discende e' che il testo proveniente dai dati si
sfugge sempre e non contiene mai marcatura, mentre la marcatura si decide con
parametri della funzione che compone la riga; nelle note non compaiono simboli,
si scrive per cento a parole.
"""

from __future__ import annotations

from datetime import date

from . import calcoli as C
from . import parametri as P
from .annunci import CAMPI_BLOCCANTI

# I caratteri che in LaTeX hanno un significato e che nei campi di un annuncio
# compaiono davvero: il nome di un'agenzia con la e commerciale, un indirizzo con
# il cancelletto, una nota con la percentuale.
_FUGHE = {
    "\\": r"\textbackslash{}",
    "&": r"\&",
    "%": r"\%",
    "$": r"\$",
    "#": r"\#",
    "_": r"\_",
    "{": r"\{",
    "}": r"\}",
    "~": r"\textasciitilde{}",
    "^": r"\textasciicircum{}",
}


def _esc(testo) -> str:
    """Rende sicuro per LaTeX un testo che viene dai dati.

    Si applica a tutto cio' che arriva da un campo compilato a mano e mai a una
    stringa che contiene marcatura: sfuggire la marcatura la stampa alla lettera,
    ed e' esattamente il difetto che questa separazione previene.
    """
    if testo is None:
        return ""
    return "".join(_FUGHE.get(c, c) for c in str(testo))


def _euro(valore: float) -> str:
    return f"{valore:,.0f}".replace(",", ".") + r"~\euro"


def _perc(valore: float, decimali: int = 2) -> str:
    return f"{valore * 100:.{decimali}f}".replace(".", ",") + r"\,\%"


def _num(valore: float, decimali: int = 0) -> str:
    """Numero all'italiana: punto per le migliaia, virgola per i decimali."""
    grezzo = f"{valore:,.{decimali}f}"
    return grezzo.replace(",", "@").replace(".", ",").replace("@", ".")


def _riga(etichetta: str, valore: str, nota: str = "", grassetto: bool = False) -> str:
    """Compone una riga della tabella.

    L'etichetta e la nota sono testo e vengono sfuggite; il valore e' marcatura
    prodotta dalle funzioni di formato di questo modulo. Il grassetto e' un
    parametro e non un pezzo di stringa, che e' la ragione per cui questa
    funzione ha quattro argomenti invece di tre.
    """
    e = _esc(etichetta)
    v = valore
    if grassetto:
        e = r"\textbf{" + e + "}"
        v = r"\textbf{" + v + "}"
    return f"{e} & {v} & {_esc(nota)} \\\\"


def _tabella(righe: list[str]) -> list[str]:
    """Apre e chiude una tabella a tre colonne che sta nella larghezza del testo.

    Le larghezze sommano, con la colonna dei numeri e le separazioni, meno della
    larghezza del testo su A4 con margini di 1,8 cm, che vale circa 17,4 cm. Le
    prime versioni usavano 5,6 e 8,2 centimetri e la terza colonna finiva fuori
    dalla pagina: un difetto che non compare nel sorgente ne' fra gli avvisi del
    compilatore, e che si vede solo guardando il PDF.
    """
    fuori = [r"\begin{tabular}{@{}p{4.6cm}r@{\hspace{0.45cm}}p{7.1cm}@{}}", r"\toprule"]
    fuori.extend(righe)
    fuori.append(r"\bottomrule")
    fuori.append(r"\end{tabular}")
    # La chiusura di paragrafo non e' cosmetica: senza, il titolo della sezione
    # seguente si aggiunge al paragrafo della tabella, compare a destra di essa
    # e viene sillabato a meta'. Sul PDF compilato si leggeva "Il costo rea-"
    # accanto alla prima tabella e "le, che non e' il prezzo" sulla riga sotto:
    # un difetto invisibile nel sorgente e assente dagli avvisi del compilatore.
    fuori.append(r"\par")
    return fuori


def _sezione(titolo: str) -> list[str]:
    """Titolo di sezione, con l'interruzione di paragrafo che lo separa dalla tabella.

    L'interruzione serve: senza, titolo e tabella finiscono sulla stessa riga e
    il titolo compare a sinistra della tabella invece che sopra.
    """
    return [r"\par\vspace{0.7em}", r"\textbf{" + _esc(titolo) + r"}\par\vspace{0.25em}"]


def costruisci(
    annuncio,
    mutuo: float = 0.0,
    tasso: float = 0.032,
    durata: int = 25,
    imu_aliquota: float = None,
    rendimento_obiettivo: float = 0.04,
    inflazione: float = None,
) -> str:
    """Restituisce il sorgente LaTeX della scheda di un annuncio.

    I parametri con un valore predefinito sono quelli che il registro non porta e
    che cambiano il risultato: importo e condizioni del mutuo vengono dal
    preventivo, l'aliquota IMU dalla delibera del Comune, il rendimento obiettivo
    e' una scelta di chi valuta. Il valore predefinito dell'IMU e' l'aliquota
    base di legge, e la scheda lo dichiara come tale invece di lasciarlo passare
    per un dato: e' lo stesso presidio dei controlli del Cruscotto.
    """
    imu = P.IMU.aliquota_base if imu_aliquota is None else imu_aliquota
    infl = P.FINANZA.inflazione_attesa if inflazione is None else inflazione
    prezzo = annuncio.prezzo_obiettivo or annuncio.prezzo_richiesto

    mancanti = [
        (campo, blocca)
        for campo, blocca, _ in CAMPI_BLOCCANTI
        if not getattr(annuncio, campo, None)
    ]
    # Tre condizioni che decidono che cosa la scheda puo' dire, separate perche'
    # bloccano cose diverse: senza prezzo non esiste operazione, senza canone non
    # esistono rendimenti ne' prezzo massimo, senza rendita il prezzo-valore non
    # si applica e le imposte cambiano di parecchio.
    ha_prezzo = prezzo > 0
    ha_canone = annuncio.canone_atteso_mese > 0
    ha_rendita = annuncio.rendita_catastale > 0

    immobile = C.Immobile(
        prezzo=prezzo,
        rendita_catastale=annuncio.rendita_catastale,
        categoria=annuncio.categoria or "A/3",
        superficie_mq=annuncio.mq,
        comune=annuncio.comune,
        venditore_impresa=annuncio.venditore_impresa == "SI",
    )
    acquirente = C.Acquirente(prima_casa=annuncio.prima_casa != "NO", prezzo_valore=True)
    finanziamento = C.Finanziamento(importo=mutuo, tasso_annuo=tasso, durata_anni=durata)
    gestione = C.Gestione(
        canone_mensile=annuncio.canone_atteso_mese,
        condominio_annuo=annuncio.spese_condominio_anno,
        aliquota_imu=imu,
    )

    costo = C.costo_operazione(immobile, acquirente, finanziamento)
    conto = C.conto_economico(immobile, gestione)
    rata_annua = C.rata_francese(mutuo, tasso, durata) * 12 if mutuo else 0.0
    metriche = C.metriche(costo, conto, rata_annua)
    reale = C.tasso_reale(metriche.rendimento_netto, infl)

    # Il prezzo massimo, con la scomposizione della trattazione: quota marginale
    # del prezzo, parte fissa, costi annui che scalano col prezzo.
    if immobile.venditore_impresa:
        k_fiscale = (
            P.IMPOSTE_TRASFERIMENTO.iva_prima_casa
            if acquirente.prima_casa
            else P.IMPOSTE_TRASFERIMENTO.iva_ordinaria
        )
    elif ha_rendita:
        k_fiscale = 0.0
    else:
        k_fiscale = (
            P.IMPOSTE_TRASFERIMENTO.registro_prima_casa
            if acquirente.prima_casa
            else P.IMPOSTE_TRASFERIMENTO.registro_ordinario
        )
    k = k_fiscale + P.COSTI.provvigione_agenzia_tipica * (1 + P.COSTI.iva_su_provvigione)
    parte_fissa = costo.costi_accessori - prezzo * k
    m = P.COSTI.manutenzione_ordinaria_su_valore + (
        P.COSTI.ristrutturazione_su_valore / P.COSTI.anni_fra_ristrutturazioni
    )
    denominatore = rendimento_obiettivo * (1 + k) + m
    prezzo_massimo = (
        (conto.utile_netto + prezzo * m - rendimento_obiettivo * parte_fissa) / denominatore
        if denominatore and ha_prezzo and ha_canone
        else None
    )

    oggi = date.today().strftime("%d/%m/%Y")
    c = []
    c.append(r"\documentclass[10pt,a4paper]{article}")
    c.append(r"\usepackage[utf8]{inputenc}")
    c.append(r"\usepackage[T1]{fontenc}")
    c.append(r"\usepackage[italian]{babel}")
    c.append(r"\usepackage[a4paper,margin=1.8cm]{geometry}")
    c.append(r"\usepackage{booktabs}")
    c.append(r"\usepackage{xcolor}")
    c.append(r"\usepackage{array}")
    c.append(r"\newcommand{\euro}{\texteuro}")
    c.append(r"\pagestyle{empty}")
    c.append(r"\setlength{\parindent}{0pt}")
    c.append(r"\begin{document}")

    c.append(r"\begin{center}")
    c.append(r"{\Large\bfseries Scheda di trattativa}\\[0.25em]")
    titolo = f"{annuncio.id} - {annuncio.comune or 'Comune non indicato'}"
    if annuncio.indirizzo:
        titolo += f", {annuncio.indirizzo}"
    c.append(r"{\large " + _esc(titolo) + r"}\\[0.25em]")
    c.append(r"{\small Preparata il " + oggi + r". Parametri fiscali della revisione "
             + P.REVISIONE.strftime("%d/%m/%Y") + r".}")
    c.append(r"\end{center}")

    if mancanti:
        avviso = (
            f"Mancano {len(mancanti)} dati che il registro non ha, elencati in fondo. "
            "I numeri sono calcolati su cio' che c'e' e vanno letti come provvisori. "
        )
        if not ha_rendita:
            avviso += (
                "In particolare manca la rendita catastale, quindi l'opzione prezzo-valore non "
                "si applica e le imposte risultano calcolate sul prezzo intero: e' la voce che, "
                "arrivando, abbassa di piu' il costo dell'operazione. "
            )
        if not ha_canone:
            avviso += (
                "E manca il canone atteso, quindi rendimenti, cash flow e prezzo massimo non "
                "sono calcolabili e non compaiono."
            )
        c.append(r"\par\vspace{0.4em}")
        c.append(r"\colorbox{yellow!30}{\parbox{\dimexpr\linewidth-2\fboxsep}{\small\textbf{Scheda incompleta.} "
                 + _esc(avviso) + r"}}")

    # ------------------------------------------------------------- il prezzo
    righe = [_riga("Prezzo richiesto", _euro(annuncio.prezzo_richiesto))]
    if annuncio.prezzo_obiettivo:
        righe.append(_riga("Prezzo obiettivo", _euro(annuncio.prezzo_obiettivo),
                           "e' quello usato in tutti i conti di questa scheda"))
    if annuncio.mq:
        righe.append(_riga("Superficie", _num(annuncio.mq) + r"~m$^2$",
                           "verificare se commerciale o calpestabile"))
        if ha_prezzo:
            righe.append(_riga("Prezzo al metro quadro", _euro(prezzo / annuncio.mq)))
    if annuncio.zona_omi:
        righe.append(_riga("Zona OMI", _esc(annuncio.zona_omi)))
    if annuncio.quotazione_omi_min and annuncio.quotazione_omi_max:
        righe.append(_riga("Quotazione di zona",
                           _euro(annuncio.quotazione_omi_min) + " -- " + _euro(annuncio.quotazione_omi_max),
                           "intervallo medio di zona per tipologia, su superficie commerciale"))
        righe.append(_riga("Scarto sulla media di zona", _perc(annuncio.scarto_su_omi, 1),
                           "sotto la media non e' di per se' un affare: una ragione c'e' sempre"))
    c.extend(_sezione("Il prezzo, e come sta rispetto alla zona"))
    c.extend(_tabella(righe))

    # ---------------------------------------------------------- il costo reale
    if immobile.venditore_impresa:
        nota_base = "nel regime IVA la base imponibile e' il prezzo"
    elif ha_rendita:
        nota_base = "con il prezzo-valore la base e' il valore catastale e non il prezzo"
    else:
        nota_base = "senza rendita catastale il prezzo-valore non si applica: la base e' il prezzo"

    righe = [
        _riga("Regime di acquisto", _esc(costo.imposte.regime)),
        _riga("Base imponibile", _euro(costo.imposte.imponibile), nota_base),
        _riga("Imposte sul trasferimento", _euro(costo.imposte.totale)),
        _riga("Provvigione con IVA", _euro(costo.provvigione)),
        _riga("Notaio e altri costi", _euro(costo.notaio_compravendita + costo.altri_costi)),
    ]
    if mutuo:
        righe.append(_riga("Oneri del mutuo", _euro(
            costo.notaio_mutuo + costo.sostitutiva_mutuo + costo.istruttoria + costo.perizia)))
    righe.append(r"\midrule")
    righe.append(_riga("Costi accessori", _euro(costo.costi_accessori),
                       "incidenza sul prezzo: " + _num(costo.incidenza_costi * 100, 1) + " per cento"))
    righe.append(_riga("Costo totale", _euro(costo.costo_totale),
                       "e' il denominatore di ogni rendimento di questa scheda", grassetto=True))
    righe.append(_riga("Cassa necessaria al rogito", _euro(costo.esborso_iniziale),
                       "costo totale meno il mutuo erogato"))
    c.extend(_sezione("Il costo reale, che non e' il prezzo"))
    c.extend(_tabella(righe))

    # --------------------------------------------------- reddito e rendimento
    c.extend(_sezione("Il reddito e il rendimento"))
    if not ha_canone:
        c.append(r"{\small Non calcolabili: manca il canone atteso, e da esso dipendono ricavo "
                 r"effettivo, reddito operativo netto, utile, tutti i rendimenti e il cash flow. "
                 r"Il canone si stima dagli annunci di affitto comparabili nella stessa zona, "
                 r"oppure dalle quotazioni OMI di locazione, con il comando \texttt{omi cerca}.}\par")
    else:
        righe = [
            _riga("Canone annuo potenziale", _euro(conto.canone_potenziale)),
            _riga("Ricavo effettivo", _euro(conto.canone_effettivo),
                  "al netto di un mese di sfitto e dell'accantonamento per morosita'"),
            _riga("Reddito operativo netto", _euro(conto.noi),
                  "dopo i costi del proprietario, prima delle imposte sul reddito"),
            _riga("Utile netto annuo", _euro(conto.utile_netto)),
            r"\midrule",
            _riga("Rendimento lordo", _perc(metriche.rendimento_lordo),
                  "il numero degli annunci, il meno informativo"),
            _riga("Rendimento netto nominale", _perc(metriche.rendimento_netto), grassetto=True),
            _riga("Rendimento netto reale", _perc(reale),
                  "al netto di un'inflazione del " + _num(infl * 100, 1)
                  + " per cento: e' il rendimento in potere d'acquisto", grassetto=True),
            _riga("Cap rate", _perc(metriche.cap_rate)),
        ]
        if mutuo:
            dscr = "n.d." if metriche.dscr == float("inf") else _num(metriche.dscr, 2)
            righe.append(_riga("Cash on cash", _perc(metriche.cash_on_cash),
                               "sul capitale proprio: con la leva puo' essere negativo"))
            righe.append(_riga("Debt service coverage ratio", dscr,
                               "sotto uno il reddito non copre la rata"))
            righe.append(_riga("Rata mensile", _euro(rata_annua / 12)))
        righe.append(_riga("Cash flow annuo", _euro(metriche.cash_flow_annuo),
                           "diviso dodici e' l'impegno mensile di tasca propria"))
        c.extend(_tabella(righe))

    # ------------------------------------------------------ il numero da usare
    c.append(r"\par\vspace{0.7em}")
    if prezzo_massimo is None:
        c.append(r"\colorbox{yellow!30}{\parbox{\dimexpr\linewidth-2\fboxsep}{"
                 r"\textbf{Il numero da portare in trattativa non e' calcolabile.}\\[0.3em]"
                 r"Il prezzo massimo sostenibile e' il prezzo a cui il rendimento netto raggiunge "
                 r"l'obiettivo, quindi dipende dal canone: senza il canone atteso l'equazione non "
                 r"ha dati, e una cifra stampata qui sarebbe inventata. E' la ragione per cui "
                 r"questa casella e' vuota invece di contenere un numero.}}")
    else:
        sconto = prezzo_massimo - prezzo
        colore = "green!15" if sconto >= 0 else "red!12"
        testo = (
            r"\textbf{Il numero da portare in trattativa}\\[0.3em]"
            r"Al rendimento netto obiettivo del " + _num(rendimento_obiettivo * 100, 1)
            + r" per cento l'immobile giustifica un prezzo massimo di \textbf{"
            + _euro(max(prezzo_massimo, 0.0)) + r"}. "
        )
        if prezzo_massimo <= 0:
            testo += (
                r"Il valore risulta negativo, e la lettura corretta non e' che si debba chiedere "
                r"piu' del prezzo: e' che a quel rendimento obiettivo l'operazione non e' "
                r"giustificabile a nessun prezzo positivo, perche' i costi fissi e i costi annui "
                r"che scalano col prezzo eccedono cio' che il canone produce."
            )
        elif sconto < 0:
            testo += (
                r"Rispetto al prezzo usato in questa scheda lo sconto da ottenere e' di \textbf{"
                + _euro(abs(sconto)) + r"}, cioe' il " + _num(abs(sconto) / prezzo * 100, 1)
                + r" per cento del prezzo."
            )
        else:
            testo += (
                r"Il prezzo trattato e' quindi sotto quello che l'immobile giustifica, con un "
                r"margine di \textbf{" + _euro(sconto) + r"}."
            )
        c.append(r"\colorbox{" + colore + r"}{\parbox{\dimexpr\linewidth-2\fboxsep}{" + testo + r"}}")

    # ----------------------------------------------------------- cosa manca
    if mancanti:
        c.extend(_sezione("Che cosa chiedere, e che cosa sblocca"))
        c.append(r"\begin{tabular}{@{}p{4.6cm}p{12.1cm}@{}}")
        c.append(r"\toprule")
        for campo, blocca in mancanti:
            c.append(f"{_esc(campo)} & {_esc(blocca)} \\\\")
        c.append(r"\bottomrule")
        c.append(r"\end{tabular}")
        c.append(r"\par")

    # ------------------------------------------------------------ avvertenze
    assunzioni = (
        "Assunzioni non presenti nel registro e usate in questa scheda: aliquota IMU al "
        + _num(imu * 100, 2) + " per cento"
        + (", che e' il valore base di legge e va sostituito con quello della delibera del Comune"
           if abs(imu - P.IMU.aliquota_base) < 1e-12 else "")
        + ("; nessun mutuo, quindi il capitale e' interamente proprio" if not mutuo else
           "; mutuo di " + _num(mutuo) + " euro al " + _num(tasso * 100, 2)
           + " per cento su " + str(durata) + " anni")
        + "; un mese di sfitto atteso all'anno e accantonamento per morosita' al "
        + _num(P.COSTI.morosita_su_canone * 100) + " per cento; regime di locazione a cedolare secca."
    )
    c.append(r"\par\vspace{0.7em}")
    c.append(r"{\footnotesize " + _esc(assunzioni))
    c.append(
        r"\\[0.4em] Questa scheda e' uno strumento di analisi personale e non costituisce "
        r"consulenza fiscale, legale o finanziaria. Prima di firmare qualunque cosa le posizioni "
        r"soggettive vanno confermate da un notaio e da un commercialista, e la conformita' "
        r"urbanistica e catastale da un tecnico abilitato. Le verifiche da chiudere prima della "
        r"proposta stanno nel foglio Checklist del workbook, i documenti da farsi consegnare nel "
        r"foglio Dossier tecnico: una proposta accettata e' gia' un contratto.}"
    )
    c.append(r"\end{document}")

    return "\n".join(c) + "\n"
