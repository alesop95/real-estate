#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Converte gli accenti scritti con l'apostrofo negli accenti veri, secondo grammatica.

Perché esiste
--------------
Parte della documentazione di questo progetto, e parte del template da cui viene, scrive
gli accenti come apostrofo posticcio: `è` invece di `e` accentata, `perché` invece di
`perche` con l'acuto, `più` invece di `piu` con l'accento. Non è una convenzione
deliberata, è un residuo: nello stesso template i due documenti normativi usano gli
accenti veri mentre altri file usano l'apostrofo, e alcuni non mettono l'accento affatto.
Un testo che deve essere leggibile come tesi non può avere tre grafie della stessa
parola, quindi si converte, una volta, con uno strumento verificabile.

Perché non una sostituzione a mano
-----------------------------------
Perché la scelta fra accento grave e acuto non è meccanica, e perché esistono
apostrofi che non sono accenti mancanti e che una sostituzione ingenua distruggerebbe.
Il caso di scuola è `un po'`, che è un troncamento di `poco` e si scrive con
l'apostrofo: `un po` con l'accento grave è un errore, ed è fra i più diffusi in
italiano. Nella stessa categoria stanno gli imperativi tronchi `fa'`, `va'`, `sta'`,
`di'`, e le forme come `mo'` e `be'`.

Da qui l'impostazione dello strumento: converte soltanto ciò che sta in una lista
bianca esplicita, e tutto il resto lo segnala perché un umano decida. Non indovina.

La regola grammaticale, in breve
--------------------------------
Sulle vocali a, i, o, u finali l'accento italiano è sempre grave: citta, cosi, puo,
piu diventano con l'accento grave. Sulla e finale il segno dipende dalla parola: è
grave nel verbo essere e in parole come cioe e caffe, ed è acuto nei composti di che,
ne e se, cioè perche, poiche, benche, affinche, purche, finche, nonche, anziche, ne,
se, e in poche altre come pote e ventitre.

Il caso ambiguo dichiarato
--------------------------
`dà` può essere la terza persona dell'indicativo di dare, che si scrive con l'accento
grave, oppure il suo imperativo, che si scrive con l'apostrofo. Le due si distinguono
solo dal senso della frase, quindi lo strumento non lo converte e lo elenca fra i casi
da decidere.

Che cosa non tocca
------------------
Nei file Markdown salta i blocchi di codice recintati e i code span in linea, perché
là un apostrofo può essere sintassi e non prosa. Nei file di codice lavora solo su
commenti e stringhe di documentazione, per la stessa ragione. Conserva la fine riga, il
newline finale e l'eventuale BOM del file, come fa md-unwrap.

Uso
---
    python tools/fix-accents.py --check <percorsi>      elenca senza scrivere
    python tools/fix-accents.py <percorsi>              converte
    python tools/fix-accents.py --residui <percorsi>    elenca solo i casi non in lista

Senza percorsi lavora sulla radice del progetto.
"""

import argparse
import os
import re
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

# ---------------------------------------------------------------------------
# Lista bianca. La chiave è la forma con l'apostrofo, il valore quella accentata.
# Si confronta parola intera e senza distinzione di maiuscole, e la maiuscola iniziale
# viene riportata sul risultato.
# ---------------------------------------------------------------------------

# Accento acuto: i composti di che, ne, se, più poche forme verbali e numerali.
ACUTO = {
    "perche": "perché", "poiche": "poiché", "benche": "benché",
    "affinche": "affinché", "purche": "purché", "finche": "finché",
    "cosicche": "cosicché", "sicche": "sicché", "anziche": "anziché",
    "dopodiche": "dopodiché", "nonche": "nonché", "giacche": "giacché",
    "fuorche": "fuorché", "salvoche": "salvoché", "checche": "checché",
    "ne": "né", "se": "sé", "pote": "poté", "ventitre": "ventitré",
    "trentatre": "trentatré", "quarantatre": "quarantatré",
    "ventunesimo": "ventunesimo",
}

# Accento grave: il verbo essere, le vocali a i o u finali, e le e finali non composte.
GRAVE = {
    "e": "è", "cioe": "cioè", "caffe": "caffè",
    "piu": "più", "gia": "già", "cosi": "così", "puo": "può", "pero": "però",
    "cio": "ciò", "li": "lì", "la": "là", "giu": "giù",
    "pie": "piè", "ahime": "ahimè", "tre": "trè",
    # verbi al futuro e al passato remoto, terza persona
    "sara": "sarà", "verra": "verrà", "andra": "andrà", "dara": "darà",
    "fara": "farà", "stara": "starà", "avra": "avrà", "potra": "potrà",
    "dovra": "dovrà", "sapra": "saprà", "vorra": "vorrà", "terra": "terrà",
    "restera": "resterà", "diventera": "diventerà", "servira": "servirà",
    "cambiera": "cambierà", "sposta": "sposta", "ando": "andò",
    "trovo": "trovò", "risulto": "risultò", "porto": "portò",
    # sostantivi in -ita, -eta, -a tronca
    "unita": "unità", "verita": "verità", "qualita": "qualità",
    "citta": "città", "possibilita": "possibilità", "capacita": "capacità",
    "attivita": "attività", "identita": "identità", "integrita": "integrità",
    "difficolta": "difficoltà", "novita": "novità", "priorita": "priorità",
    "meta": "metà", "eta": "età", "volonta": "volontà", "puntualita": "puntualità",
    "affidabilita": "affidabilità", "compatibilita": "compatibilità",
    "disponibilita": "disponibilità", "ammissibilita": "ammissibilità",
    "praticabilita": "praticabilità", "riservatezza": "riservatezza",
    "specificita": "specificità", "regolarita": "regolarità",
    "commutativita": "commutatività", "invarianza": "invarianza",
    "portabilita": "portabilità", "leggibilita": "leggibilità",
    "tracciabilita": "tracciabilità", "immutabilita": "immutabilità",
    "eleganza": "eleganza", "densita": "densità", "brevita": "brevità",
    "utilita": "utilità", "necessita": "necessità", "curiosita": "curiosità",
    "generalita": "generalità", "particolarita": "particolarità",
    "meccanicita": "meccanicità", "riproducibilita": "riproducibilità",
    "ispezionabilita": "ispezionabilità", "sacrificabilita": "sacrificabilità",
    # prima persona del futuro
    "sapro": "saprò", "potro": "potrò", "faro": "farò", "andro": "andrò",
    "tornero": "tornerò", "scrivero": "scriverò", "leggero": "leggerò",
}

# Forme con apostrofo che NON sono accenti mancanti: non si toccano mai.
APOSTROFO_LEGITTIMO = {
    "po", "fa", "sta", "va", "di", "mo", "be", "ca", "pa", "to", "de",
    "un", "buon", "qual", "tal", "sant", "dell", "nell", "all", "sull",
    "dall", "quell", "bell", "quest", "cos", "com", "anch", "dov", "c",
    "l", "d", "n", "m", "s", "t", "v", "gl",
}

# Forme genuinamente ambigue: si elencano e non si convertono.
AMBIGUE = {
    "da": ("dà se è indicativo di dare, dà se è imperativo: dipende dalla frase"),
}

# Regola per suffisso, che rende inutile elencare a mano ogni parola.
# In italiano l'accento sulle vocali a, i, o, u in fine di parola è sempre grave: non
# esiste una parola italiana che termini con una di queste vocali accentata in modo
# acuto. La conversione di quelle uscite è quindi meccanica e non richiede una lista,
# a differenza della e finale, dove il segno dipende dalla parola e la lista serve.
#
# La regola si applica solo dopo i controlli sugli apostrofi legittimi e sui casi
# ambigui, e solo a parole di almeno due lettere, perché le forme brevi da non
# toccare sono già filtrate dai controlli precedenti. Le parole che finiscono in altre lettere, comprese quelle di altre
# lingue come what', non sono toccate e restano fra i residui da guardare.
VOCALI_SEMPRE_GRAVI = {"a": "\u00e0", "i": "\u00ec", "o": "\u00f2", "u": "\u00f9"}


def per_suffisso(parola):
    """L'accentazione ricavata dalla regola, o None se la regola non si applica."""
    # Due lettere bastano: sì diventa sì, che è una parola legittima. Le forme brevi
    # che non vanno toccate, cioè po', fa', va', di' e simili, sono già state filtrate
    # dai controlli precedenti, quindi la soglia qui serve solo a escludere le singole
    # lettere dell'elisione.
    if len(parola) < 2:
        return None
    ultima = parola[-1].lower()
    accentata = VOCALI_SEMPRE_GRAVI.get(ultima)
    if accentata is None:
        return None
    return parola[:-1] + accentata


# Un token candidato: parola alfabetica seguita da apostrofo dritto o tipografico,
# non seguita da un'altra lettera (per non colpire l'elisione come dell'area).
CANDIDATO = re.compile(r"\b([A-Za-z]+)['’](?![A-Za-z])")

# Impostata dalla riga di comando. Quando è vera, dà viene trattata
# come indicativo e convertita. Resta falsa per default perché la
# scelta prudente è non decidere al posto di chi conosce il testo.
DA_INDICATIVO = False


def maiuscola_come(originale, sostituto):
    """Riporta sul sostituto la maiuscola iniziale dell'originale."""
    if originale[:1].isupper():
        return sostituto[:1].upper() + sostituto[1:]
    return sostituto


def segmenta_markdown(testo):
    """Divide il testo in tratti (tipo, contenuto) la cui concatenazione è l'originale.

    Il tipo vale "prosa" dove la conversione si applica e "verbatim" dove non si applica.
    Sono verbatim i blocchi recintati da tre backtick o tre tilde, comprese le righe di
    recinto, e i code span in linea. La prudenza è la stessa di md-unwrap: dentro un
    blocco di codice un apostrofo può essere sintassi, e riscriverlo cambierebbe il
    significato del documento.

    L'invariante che questa funzione garantisce, e che l'autotest verifica, è che la
    concatenazione dei contenuti sia identica al testo di partenza: ogni a capo sta
    dentro un tratto e nessuno viene aggiunto in fase di ricomposizione.
    """
    tratti = []
    dentro_recinto = False
    recinto = None
    # Si itera conservando l'a capo dentro la riga, così la concatenazione è esatta.
    for riga in testo.splitlines(keepends=True):
        nudo = riga.rstrip("\n")
        m = re.match(r"^\s*(`{3,}|~{3,})", nudo)
        if not dentro_recinto and m:
            dentro_recinto, recinto = True, m.group(1)[0] * 3
            tratti.append(("verbatim", riga))
            continue
        if dentro_recinto:
            tratti.append(("verbatim", riga))
            if re.match(r"^\s*" + re.escape(recinto), nudo):
                dentro_recinto = False
            continue
        # Fuori dai recinti la riga si spezza sui code span in linea.
        for pezzo in re.split(r"(`+[^`\n]*`+)", riga):
            if not pezzo:
                continue
            tratti.append(("verbatim" if pezzo.startswith("`") else "prosa", pezzo))
    return tratti


def converti_prosa(testo, statistiche, residui, ambigui, per_regola=None):
    if per_regola is None:
        per_regola = set()

    def sostituisci(m):
        parola = m.group(1)
        chiave = parola.lower()
        if chiave in APOSTROFO_LEGITTIMO:
            return m.group(0)
        if chiave in AMBIGUE:
            if chiave == "da" and DA_INDICATIVO:
                statistiche[chiave] = statistiche.get(chiave, 0) + 1
                return maiuscola_come(parola, "dà")
            ambigui[chiave] = ambigui.get(chiave, 0) + 1
            return m.group(0)
        if chiave in ACUTO:
            statistiche[chiave] = statistiche.get(chiave, 0) + 1
            return maiuscola_come(parola, ACUTO[chiave])
        if chiave in GRAVE:
            statistiche[chiave] = statistiche.get(chiave, 0) + 1
            return maiuscola_come(parola, GRAVE[chiave])
        # Nessuna lista la contiene: si tenta la regola per suffisso, che copre tutte
        # le uscite in a, i, o, u senza bisogno di enumerarle.
        dalla_regola = per_suffisso(parola)
        if dalla_regola is not None:
            statistiche[chiave] = statistiche.get(chiave, 0) + 1
            per_regola.add(chiave)
            return dalla_regola
        residui[chiave] = residui.get(chiave, 0) + 1
        return m.group(0)

    return CANDIDATO.sub(sostituisci, testo)


def elabora(percorso, statistiche, residui, ambigui):
    """Converte un file conservandone la forma binaria: fine riga, BOM, newline finale."""
    with open(percorso, "rb") as f:
        grezzo = f.read()

    bom = grezzo.startswith(b"\xef\xbb\xbf")
    corpo = grezzo[3:] if bom else grezzo
    crlf = b"\r\n" in corpo
    testo = corpo.decode("utf-8").replace("\r\n", "\n")

    if percorso.lower().endswith(".py"):
        nuovo = converti_python(testo, statistiche, residui, ambigui)
    elif percorso.lower().endswith(".md"):
        tratti = segmenta_markdown(testo)
        # Invariante: la concatenazione dei tratti è il testo di partenza. Se non lo
        # fosse, la conversione produrrebbe un file diverso per un motivo che non è
        # la conversione, quindi si preferisce fallire.
        if "".join(c for _, c in tratti) != testo:
            raise AssertionError("segmentazione non fedele su %s" % percorso)
        nuovo = "".join(
            converti_prosa(c, statistiche, residui, ambigui) if t == "prosa" else c
            for t, c in tratti)
    else:
        nuovo = converti_prosa(testo, statistiche, residui, ambigui)

    if nuovo == testo:
        return False, None
    uscita = nuovo.replace("\n", "\r\n") if crlf else nuovo
    dati = uscita.encode("utf-8")
    if bom:
        dati = b"\xef\xbb\xbf" + dati
    return True, dati


# ---------------------------------------------------------------------------
# Modalità Python, deliberatamente più prudente di quella Markdown.
# ---------------------------------------------------------------------------
# In un file di codice l'apostrofo non è solo punteggiatura: delimita le stringhe. Una
# stringa come 'tipo' offre al riconoscitore la sequenza tipo seguita da apostrofo, che
# la regola per suffisso trasformerebbe in tipo con l'accento, rompendo il programma. Il
# rischio non è teorico: nel repository esistono 'voci', 'tipo', 'metà e altre chiavi
# che finiscono in una vocale.
#
# Da qui due limitazioni. La prima è dove si converte: soltanto nei commenti, nelle
# stringhe di documentazione e nelle stringhe delimitate da doppi apici, mai in quelle
# delimitate da apici singoli, il cui apostrofo di chiusura è precisamente ciò che
# confonde il riconoscitore. La seconda è come si converte: solo con la lista bianca,
# senza la regola per suffisso, perché anche dentro un commento può comparire il nome
# di una chiave citata fra apici singoli.
# Nei file di codice il riconoscitore va reso più stretto di un elemento: la parola
# non deve essere preceduta da un apostrofo. La ragione è che dentro un docstring o
# un commento si citano gli identificatori fra apici singoli, e in una citazione come
# quella la sequenza che il riconoscitore vede è la parola seguita dall'apostrofo di
# chiusura, indistinguibile da un accento mancante. Il lookbehind risolve il caso
# senza euristiche: se prima della parola c'e' un apostrofo, quello che segue è una
# chiusura di citazione. Con questa distinzione la regola per suffisso torna sicura
# anche qui, e non serve elencare a mano le decine di parole che finiscono in -ita.
# Una sola lettera basta come candidata, perché le forme di una lettera sono tutte
# nell'elenco degli apostrofi legittimi dell'elisione e vengono scartate là.
_AP = chr(39) + chr(0x2019)
CANDIDATO_CODICE = re.compile(
    r"(?<![A-Za-z" + _AP + r"])([A-Za-z]+)[" + _AP + r"](?![A-Za-z])")

STRINGA_DOPPIA = re.compile(r'"(?:[^"\\\n]|\\.)*"')
DOCSTRING = re.compile(r'"""(?:.|\n)*?"""')


def converti_lista_bianca(testo, statistiche, residui, ambigui):
    """La conversione per i file di codice.

    Si distingue da converti_prosa in un punto solo, il riconoscitore: qui una
    parola preceduta da apostrofo non è candidata, perché in un file di codice
    quello è il delimitatore di una citazione e non un accento mancante. Con
    quella garanzia la regola per suffisso si può applicare anche qui.
    """
    def sostituisci(m):
        parola = m.group(1)
        chiave = parola.lower()
        if chiave in APOSTROFO_LEGITTIMO:
            return m.group(0)
        if chiave in AMBIGUE:
            if chiave == "da" and DA_INDICATIVO:
                statistiche[chiave] = statistiche.get(chiave, 0) + 1
                return maiuscola_come(parola, "d\u00e0")
            ambigui[chiave] = ambigui.get(chiave, 0) + 1
            return m.group(0)
        if chiave in ACUTO:
            statistiche[chiave] = statistiche.get(chiave, 0) + 1
            return maiuscola_come(parola, ACUTO[chiave])
        if chiave in GRAVE:
            statistiche[chiave] = statistiche.get(chiave, 0) + 1
            return maiuscola_come(parola, GRAVE[chiave])
        dalla_regola = per_suffisso(parola)
        if dalla_regola is not None:
            statistiche[chiave] = statistiche.get(chiave, 0) + 1
            return dalla_regola
        residui[chiave] = residui.get(chiave, 0) + 1
        return m.group(0)

    return CANDIDATO_CODICE.sub(sostituisci, testo)


def converti_python(testo, statistiche, residui, ambigui):
    """Converte solo docstring, stringhe a doppi apici e commenti.

    L'ordine conta: prima i docstring, che possono contenere qualunque cosa, poi le
    stringhe a doppi apici che restano, poi i commenti sulle righe rimaste. I tre
    insiemi non si sovrappongono perché ciascun passaggio lavora su ciò che il
    precedente non ha consumato, e le sostituzioni non allungano né accorciano il testo
    in modo che sposti gli indici degli altri, perché avvengono in una sola passata di
    espressione regolare per categoria.
    """
    def in_docstring(m):
        return converti_lista_bianca(m.group(0), statistiche, residui, ambigui)

    testo = DOCSTRING.sub(in_docstring, testo)

    def in_stringa(m):
        return converti_lista_bianca(m.group(0), statistiche, residui, ambigui)

    testo = STRINGA_DOPPIA.sub(in_stringa, testo)

    # I commenti: si converte solo la parte dopo il cancelletto, e solo se il cancelletto
    # non è dentro una stringa. La verifica è approssimata contando gli apici prima di
    # esso, che è sufficiente su codice normalmente formattato e prudente in caso di
    # dubbio, perché in caso di conteggio dispari la riga viene lasciata stare.
    righe = []
    for riga in testo.split("\n"):
        pos = riga.find("#")
        if pos < 0:
            righe.append(riga)
            continue
        prima = riga[:pos]
        if prima.count('"') % 2 or prima.count("'") % 2:
            righe.append(riga)
            continue
        righe.append(prima + converti_lista_bianca(
            riga[pos:], statistiche, residui, ambigui))
    return "\n".join(righe)


def raccogli(percorsi, estensioni):
    # Uno strumento che riscrive testo italiano non deve riscrivere il proprio sorgente:
    # i suoi casi di prova contengono di proposito le sequenze che cerca, e una corsa su
    # se stesso li altererebbe. E' accaduto due volte durante lo sviluppo, e la difesa
    # e' strutturale invece che mnemonica.
    # Gli strumenti tipografici della stessa famiglia si escludono a vicenda, non solo se
    # stessi: i loro casi di prova contengono di proposito le sequenze che cercano, e una
    # corsa incrociata li altera. E' accaduto tre volte durante lo sviluppo.
    FAMIGLIA = {"fix-accents.py", "fix-missing-accents.py", "fix-dashes.py"}
    IO_STESSO = os.path.abspath(__file__)
    file = []
    for p in percorsi:
        ap = p if os.path.isabs(p) else os.path.join(ROOT, p)
        if os.path.isfile(ap):
            if os.path.abspath(ap) != IO_STESSO and os.path.basename(ap) not in FAMIGLIA:
                file.append(ap)
            continue
        for radice, cartelle, nomi in os.walk(ap):
            cartelle[:] = [c for c in cartelle
                           if c not in (".git", "__pycache__", "node_modules",
                                        ".venv", "_notes")]
            for n in sorted(nomi):
                if os.path.splitext(n)[1].lower() in estensioni:
                    completo = os.path.join(radice, n)
                    if os.path.abspath(completo) != IO_STESSO and n not in FAMIGLIA:
                        file.append(completo)
    return file


def autotest():
    """Prove minime dello strumento, eseguibili senza toccare il repository.

    I casi si costruiscono concatenando Q, che è l'apostrofo ottenuto dal suo
    codepoint, invece di scriverlo dentro le stringhe letterali. Così il file di
    questo strumento non contiene le sequenze che lo strumento stesso cerca, e una
    corsa su se stesso non può alterare i propri dati di prova.
    """
    Q = chr(39)
    DQ = chr(34)
    casi = [
        ("Il dato e" + Q + " rotto.", "Il dato \u00e8 rotto."),
        ("perche" + Q + " e" + Q + " cosi" + Q, "perch\u00e9 \u00e8 cos\u00ec"),
        ("E" + Q + " un caso.", "\u00c8 un caso."),
        ("piu" + Q + " di gia" + Q, "pi\u00f9 di gi\u00e0"),
        ("ne" + Q + " l" + Q + "uno ne" + Q + " l" + Q + "altro",
         "n\u00e9 l" + Q + "uno n\u00e9 l" + Q + "altro"),
        ("se" + Q + " stesso", "s\u00e9 stesso"),
        # apostrofi legittimi: non si toccano
        ("un po" + Q + " di tempo", "un po" + Q + " di tempo"),
        ("fa" + Q + " cosi" + Q, "fa" + Q + " cos\u00ec"),
        ("l" + Q + "unita" + Q + " e" + Q + " l" + Q + "area",
         "l" + Q + "unit\u00e0 \u00e8 l" + Q + "area"),
        # elisione: non è un accento e non si tocca
        ("dell" + Q + "area e" + Q + " quella", "dell" + Q + "area \u00e8 quella"),
        # ambiguo: si lascia, salvo il flag
        ("da" + Q + " un risultato", "da" + Q + " un risultato"),
        # regola per suffisso
        ("la modalita" + Q + " e" + Q + " attiva", "la modalit\u00e0 \u00e8 attiva"),
        ("la proprieta" + Q + " di X", "la propriet\u00e0 di X"),
        ("lo segnalera" + Q + " dopo", "lo segnaler\u00e0 dopo"),
        ("si" + Q + " e no", "s\u00ec e no"),
        ("virtu" + Q + " e vizi", "virt\u00f9 e vizi"),
        ("pie" + Q + " di pagina", "pi\u00e8 di pagina"),
        # parola non italiana: la regola non si applica
        ("what" + Q + " resta", "what" + Q + " resta"),
    ]
    # ATTENZIONE: questo blocco contiene di proposito apostrofi che lo strumento non
    # deve toccare. Se una corsa dello strumento su se stesso lo modificasse, il difetto
    # sarebbe nello strumento e non qui: è accaduto una volta, ed è la ragione per cui
    # nella modalità codice il riconoscitore esclude le parole precedute da apostrofo.
    casi_python = [
        # le chiavi fra apici singoli non si toccano, nemmeno se finiscono in vocale
        ("d = {" + Q + "tipo" + Q + ": 1, " + Q + "voci" + Q + ": 2}",
         "d = {" + Q + "tipo" + Q + ": 1, " + Q + "voci" + Q + ": 2}"),
        ("x = " + Q + "meta" + Q, "x = " + Q + "meta" + Q),
        ("# " + Q + "campi" + Q + " e " + Q + "parola" + Q + " restano",
         "# " + Q + "campi" + Q + " e " + Q + "parola" + Q + " restano"),
        # il commento si converte
        ("x = 1  # questo e" + Q + " un commento",
         "x = 1  # questo \u00e8 un commento"),
        # la stringa a doppi apici si converte
        ("t = " + DQ + "il dato e" + Q + " rotto" + DQ,
         "t = " + DQ + "il dato è rotto" + DQ),
        # una parola italiana non preceduta da apostrofo si converte per suffisso
        ("# il valore di personalita" + Q + " conta",
         "# il valore di personalit\u00e0 conta"),
        # e le due cose convivono sulla stessa riga
        ("# " + Q + "tipo" + Q + " e la modalita" + Q + " scelta",
         "# " + Q + "tipo" + Q + " e la modalit\u00e0 scelta"),
    ]
    fallite = 0
    for ingresso, atteso in casi:
        st, re_, am = {}, {}, {}
        ottenuto = converti_prosa(ingresso, st, re_, am)
        if ottenuto != atteso:
            print("  FALLITO  %r -> %r, atteso %r" % (ingresso, ottenuto, atteso))
            fallite += 1
    for ingresso, atteso in casi_python:
        st, re_, am = {}, {}, {}
        ottenuto = converti_python(ingresso, st, re_, am)
        if ottenuto != atteso:
            print("  FALLITO py  %r -> %r, atteso %r" % (ingresso, ottenuto, atteso))
            fallite += 1

    # Fedeltà della segmentazione, compresi recinti e code span.
    doc = ("Prosa con è dentro.\n\n```python\nx = \"è\"\n```\n\n"
           "Altra prosa con `codice è` in linea e più testo.\n")
    tratti = segmenta_markdown(doc)
    if "".join(c for _, c in tratti) != doc:
        print("  FALLITO  la segmentazione non ricompone l'originale")
        fallite += 1
    st, re_, am = {}, {}, {}
    reso = "".join(converti_prosa(c, st, re_, am) if t == "prosa" else c
                   for t, c in tratti)
    if "x = \"è\"" not in reso:
        print("  FALLITO  il blocco di codice è stato toccato")
        fallite += 1
    if "`codice è`" not in reso:
        print("  FALLITO  il code span in linea è stato toccato")
        fallite += 1
    if "Prosa con \u00e8 dentro" not in reso:
        print("  FALLITO  la prosa fuori dai recinti non è stata convertita")
        fallite += 1

    print("autotest: %d casi, %d falliti" % (len(casi) + len(casi_python) + 4, fallite))
    return 1 if fallite else 0


def main():
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("--autotest", action="store_true", help="esegue le prove interne")
    ap.add_argument("--da-indicativo", action="store_true",
                    help="converte dà nella forma con accento grave. Da usare solo dopo aver letto i contesti e accertato che nessuno sia un imperativo, perché l'imperativo di dare si scrive con l'apostrofo")
    ap.add_argument("percorsi", nargs="*", default=["."])
    ap.add_argument("--check", action="store_true", help="non scrive, riporta")
    ap.add_argument("--residui", action="store_true",
                    help="elenca solo le forme non in lista bianca")
    ap.add_argument("--ext", default=".md,.tex,.txt",
                    help="estensioni da trattare, separate da virgola")
    args = ap.parse_args()

    if args.autotest:
        return autotest()

    global DA_INDICATIVO
    DA_INDICATIVO = args.da_indicativo

    estensioni = set(e if e.startswith(".") else "." + e
                     for e in args.ext.split(","))
    file = raccogli(args.percorsi or ["."], estensioni)

    statistiche, residui, ambigui = {}, {}, {}
    cambiati = []

    for percorso in file:
        try:
            cambia, dati = elabora(percorso, statistiche, residui, ambigui)
        except UnicodeDecodeError:
            print("saltato, non è UTF-8: %s" % percorso)
            continue
        if cambia:
            rel = os.path.relpath(percorso, ROOT)
            cambiati.append(rel)
            if not args.check and not args.residui:
                with open(percorso, "wb") as f:
                    f.write(dati)

    if args.residui:
        if residui:
            print("forme con apostrofo non in lista bianca, %d distinte:" % len(residui))
            for k, v in sorted(residui.items(), key=lambda x: -x[1]):
                print("  %-24s x%d" % (k + "'", v))
        else:
            print("nessun residuo")
        return 0

    print("%d file esaminati, %d %s" % (
        len(file), len(cambiati),
        "da modificare" if args.check else "modificati"))
    if statistiche:
        tot = sum(statistiche.values())
        print("\n%d sostituzioni, %d forme distinte:" % (tot, len(statistiche)))
        for k, v in sorted(statistiche.items(), key=lambda x: -x[1])[:25]:
            reso = ACUTO.get(k) or GRAVE.get(k)
            print("  %-16s -> %-16s x%d" % (k + "'", reso, v))
    if ambigui:
        print("\nda decidere a mano, non convertite:")
        for k, v in sorted(ambigui.items()):
            print("  %s' x%d: %s" % (k, v, AMBIGUE[k]))
    if residui:
        print("\n%d forme non riconosciute, rilanciare con --residui per l'elenco"
              % len(residui))
    return 0


if __name__ == "__main__":
    sys.exit(main())
