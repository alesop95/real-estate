#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Normalizza i trattini lunghi nel trattino breve, come prescrive la regola di stile.

Perché' esiste
--------------
La regola `interaction-style` dice che i trattini lunghi non si usano e che sono ammessi
solo quelli brevi. La regola c'era, la verifica no, e nel repository se ne contano
centinaia: la maggior parte nel materiale ereditato dal template e negli handoff scritti
prima che la regola fosse scritta. Questo strumento la applica e la rende verificabile.

I segni che tocca, e perché' sono più' di uno
---------------------------------------------
Non basta cercare il trattino em. Nei testi che passano da un elaboratore di testo o da
un generatore compaiono almeno cinque segni distinti che a video somigliano a un
trattino: il trattino em, il trattino en, la barra orizzontale, il trattino da cifre e il
segno meno matematico. Il segno meno merita una nota, perché' e' il più' insidioso: e' un
operatore matematico, non punteggiatura, e in un testo tecnico un lettore che copia una
formula ottiene un carattere che nessun compilatore accetta.

Il caso che non si tocca, e perché' e' importante
------------------------------------------------
Esiste nel repository uno strumento la cui tabella di sostituzione contiene proprio
questi caratteri, perché' il suo compito e' rimuoverli dai documenti convertiti. Passare
questo strumento su quello lo renderebbe incapace di riconoscere cio' che deve
sostituire: e' lo stesso genere di errore per cui `fix-accents.py` esclude il proprio
sorgente. Le esclusioni si dichiarano in `tools/dashes-exclude.txt`, una per riga con il
motivo dopo un cancelletto, e un'esclusione senza motivo viene rifiutata.

Che cosa non tocca comunque
---------------------------
Nei Markdown salta i blocchi di codice recintati, perché' la' un trattino può' essere un
dato o un frammento di output e non prosa. Nei file Python lavora solo su commenti,
docstring e stringhe a doppi apici. Conserva fine riga, BOM e newline finale.

Uso
---
    python tools/fix-dashes.py --check <percorsi>
    python tools/fix-dashes.py <percorsi>
"""

import argparse
import os
import re
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
ESCLUSIONI = os.path.join(ROOT, "tools", "dashes-exclude.txt")

# I cinque segni, con il nome per il rapporto. Tutti diventano il trattino breve.
SEGNI = {
    "—": "trattino em",
    "–": "trattino en",
    "―": "barra orizzontale",
    "‒": "trattino da cifre",
    "−": "segno meno",
}
BREVE = "-"

RECINTO = re.compile(r"^\s*(`{3,}|~{3,})")
STRINGA_DOPPIA = re.compile(r'"(?:[^"\\\n]|\\.)*"')
DOCSTRING = re.compile(r'"""(?:.|\n)*?"""')


def sostituisci(testo, conteggio):
    for segno in SEGNI:
        if segno in testo:
            conteggio[segno] = conteggio.get(segno, 0) + testo.count(segno)
            testo = testo.replace(segno, BREVE)
    return testo


def converti_markdown(testo, conteggio):
    """Converte la prosa e lascia intatti i blocchi recintati."""
    fuori = []
    dentro_recinto = False
    recinto = None
    for riga in testo.splitlines(keepends=True):
        nudo = riga.rstrip("\n")
        m = RECINTO.match(nudo)
        if not dentro_recinto and m:
            dentro_recinto, recinto = True, m.group(1)[0] * 3
            fuori.append(riga)
            continue
        if dentro_recinto:
            fuori.append(riga)
            if re.match(r"^\s*" + re.escape(recinto), nudo):
                dentro_recinto = False
            continue
        fuori.append(sostituisci(riga, conteggio))
    return "".join(fuori)


def converti_python(testo, conteggio):
    testo = DOCSTRING.sub(lambda m: sostituisci(m.group(0), conteggio), testo)
    testo = STRINGA_DOPPIA.sub(lambda m: sostituisci(m.group(0), conteggio), testo)
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
        righe.append(prima + sostituisci(riga[pos:], conteggio))
    return "\n".join(righe)


def leggi_esclusioni():
    esclusi, malformate = {}, []
    if not os.path.exists(ESCLUSIONI):
        return esclusi, malformate
    with open(ESCLUSIONI, "rb") as f:
        for riga in f.read().decode("utf-8").splitlines():
            riga = riga.strip()
            if not riga or riga.startswith("##"):
                continue
            if "#" not in riga:
                malformate.append(riga)
                continue
            percorso, motivo = riga.split("#", 1)
            percorso, motivo = percorso.strip(), motivo.strip()
            if not percorso or not motivo:
                malformate.append(riga)
                continue
            esclusi[os.path.normpath(percorso)] = motivo
    return esclusi, malformate


def elabora(percorso, conteggio):
    with open(percorso, "rb") as f:
        grezzo = f.read()
    bom = grezzo.startswith(b"\xef\xbb\xbf")
    corpo = grezzo[3:] if bom else grezzo
    crlf = b"\r\n" in corpo
    testo = corpo.decode("utf-8").replace("\r\n", "\n")

    if percorso.lower().endswith(".py"):
        nuovo = converti_python(testo, conteggio)
    elif percorso.lower().endswith(".md"):
        nuovo = converti_markdown(testo, conteggio)
    else:
        nuovo = sostituisci(testo, conteggio)

    if nuovo == testo:
        return False, None
    uscita = nuovo.replace("\n", "\r\n") if crlf else nuovo
    dati = uscita.encode("utf-8")
    return True, (b"\xef\xbb\xbf" + dati) if bom else dati


def autotest():
    """Prove interne: i cinque segni si normalizzano, il verbatim resta intatto."""
    casi = [
        ("un testo — con em dash", "un testo - con em dash"),
        ("pagine 10–12", "pagine 10-12"),
        ("valore −5", "valore -5"),
        ("barra ― orizzontale", "barra - orizzontale"),
        ("cifre ‒ separate", "cifre - separate"),
        ("un trattino - normale resta", "un trattino - normale resta"),
    ]
    fallite = 0
    for ingresso, atteso in casi:
        c = {}
        ottenuto = sostituisci(ingresso, c)
        if ottenuto != atteso:
            print("  FALLITO  %r -> %r, atteso %r" % (ingresso, ottenuto, atteso))
            fallite += 1

    # Il blocco recintato non si tocca: la' un trattino puo' essere un dato.
    c = {}
    # Il documento di prova si costruisce concatenando, invece di scriverlo come
    # letterale multiriga: gli a capo dentro una stringa letterale renderebbero il
    # sorgente non valido, e il segno cercato si passa per codepoint cosi' che questo
    # file non contenga il carattere che lo strumento normalizza.
    EM = "\u2014"
    doc = ("prosa " + EM + " qui\n\n```\n"
           "codice " + EM + " la\n```\n\n"
           "altra " + EM + " prosa\n")
    reso = converti_markdown(doc, c)
    if "codice " + EM + " la" not in reso:
        print("  FALLITO  il blocco recintato e' stato modificato")
        fallite += 1
    if "prosa - qui" not in reso or "altra - prosa" not in reso:
        print("  FALLITO  la prosa fuori dal recinto non e' stata normalizzata")
        fallite += 1

    print("autotest: %d casi, %d falliti" % (len(casi) + 2, fallite))
    return 1 if fallite else 0


def main():
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("percorsi", nargs="*", default=["."])
    ap.add_argument("--check", action="store_true")
    ap.add_argument("--autotest", action="store_true",
                    help="esegue le prove interne")
    ap.add_argument("--ext", default=".md,.tex,.txt,.py")
    args = ap.parse_args()

    if args.autotest:
        return autotest()

    estensioni = set(e if e.startswith(".") else "." + e for e in args.ext.split(","))
    esclusi, malformate = leggi_esclusioni()
    if malformate:
        print("esclusioni senza motivo, rifiutate:")
        for r in malformate:
            print("  %s" % r)
        return 1

    # Gli strumenti tipografici della stessa famiglia si escludono a vicenda, non solo se
    # stessi: i loro casi di prova contengono di proposito le sequenze che cercano, e una
    # corsa incrociata li altera. E' accaduto tre volte durante lo sviluppo.
    FAMIGLIA = {"fix-accents.py", "fix-missing-accents.py", "fix-dashes.py"}
    io_stesso = os.path.abspath(__file__)
    file = []
    for p in args.percorsi or ["."]:
        ap_ = p if os.path.isabs(p) else os.path.join(ROOT, p)
        if os.path.isfile(ap_):
            file.append(ap_)
            continue
        for radice, cartelle, nomi in os.walk(ap_):
            cartelle[:] = [c for c in cartelle
                           if c not in (".git", "__pycache__", "node_modules",
                                        ".venv", "_notes")]
            for n in sorted(nomi):
                if os.path.splitext(n)[1].lower() in estensioni:
                    file.append(os.path.join(radice, n))

    conteggio, cambiati, saltati = {}, [], []
    for percorso in file:
        rel = os.path.normpath(os.path.relpath(percorso, ROOT))
        if (os.path.abspath(percorso) == io_stesso
                or os.path.basename(percorso) in FAMIGLIA or rel in esclusi):
            saltati.append(rel)
            continue
        try:
            cambia, dati = elabora(percorso, conteggio)
        except UnicodeDecodeError:
            continue
        if cambia:
            cambiati.append(rel)
            if not args.check:
                with open(percorso, "wb") as f:
                    f.write(dati)

    print("%d file esaminati, %d %s, %d esclusi" % (
        len(file), len(cambiati),
        "da modificare" if args.check else "modificati", len(saltati)))
    if conteggio:
        print("\nsostituzioni per segno:")
        for segno, n in sorted(conteggio.items(), key=lambda x: -x[1]):
            print("  U+%04X %-22s x%d" % (ord(segno), SEGNI[segno], n))
    if saltati and args.check:
        print("\nesclusi per dichiarazione:")
        for r in saltati:
            motivo = esclusi.get(r)
            if motivo is None:
                motivo = ("e' questo strumento"
                          if os.path.basename(r) == os.path.basename(__file__)
                          else "e' uno strumento della stessa famiglia tipografica, i cui "
                               "casi di prova contengono di proposito i segni cercati")
            print("  %s: %s" % (r, motivo))
    return 0


if __name__ == "__main__":
    sys.exit(main())
