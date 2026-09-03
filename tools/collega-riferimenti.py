#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""collega-riferimenti - converte i nomi di file Markdown citati fra apici inversi in collegamenti.

La documentazione di questo progetto cita i propri file scrivendone il nome fra apici inversi, che
per un lettore è un indice e per un visualizzatore Markdown è testo. Il costo si vede aprendo la
cartella come vault Obsidian: il grafo dei collegamenti risulta quasi vuoto anche se la
documentazione è densamente interconnessa, e la misura che ha motivato questo strumento contava
quarantanove note e quindici archi, con un solo nodo di grado maggiore di uno. Convertire quelle
citazioni serve prima di tutto al lettore, perché un indice cliccabile funziona in Obsidian, su
GitHub e nell'editor, e solo di conseguenza al grafo.

La forma prodotta tiene il nome fra apici inversi dentro il testo del collegamento, cioè parentesi
quadre attorno al nome in monospazio e percorso fra tonde. Un code span dentro il testo di un
collegamento è Markdown standard, reso da GitHub come da Obsidian, quindi la convenzione
tipografica del progetto, che vuole i nomi di file in monospazio, non viene sacrificata alla
navigabilità. Il percorso è relativo alla nota che lo contiene, come prescrive la configurazione del
vault, e passa alla forma con parentesi angolari quando contiene tonde, perché altrimenti la prima
tonda di chiusura interrompe il collegamento.

Quattro scelte delimitano cosa lo strumento fa, e sono la ragione per cui la conversione è
automatizzabile senza rileggere ogni frase. Il frontmatter YAML e le righe dentro i blocchi
recintati restano intatti, perché un collegamento in un blocco preformattato resta testo per
costruzione e perché l'indice di `CLAUDE.md` vive in blocchi di quel tipo. Un nome nudo che nel
progetto esiste in più di un posto non si indovina mai: `README.md` citato dentro `docs/` può voler
dire il README della cartella o quello di radice, e la differenza la sa solo la frase, quindi lo
span resta testo. Di ogni bersaglio si collega la prima citazione per file e non tutte, perché
l'arco nel grafo è lo stesso e la prosa non si riempie di collegamenti ripetuti; per essere
idempotente lo strumento conta come prima citazione anche un collegamento che il file già porta,
altrimenti ogni corsa collegherebbe la citazione successiva fino a esaurirle. L'eccezione sono i
file elencati in `INDICI`, il cui mestiere è indicizzare altri file: lì ogni citazione diventa un
collegamento, perché un indice si legge saltando alla riga che interessa e una riga di tabella che
non collega è inutile a chi la sta guardando.

Uso:

    python tools/collega-riferimenti.py --check      elenca le citazioni convertibili, non scrive
    python tools/collega-riferimenti.py              converte e riscrive i file

Con `--check` esce con codice diverso da zero se resta qualcosa da convertire, così da poter stare
in un controllo prima del commit accanto a `python tools/md-unwrap.py --check .`.
"""
import io
import os
import re
import sys
from pathlib import Path

# Cartelle fuori dall'indice del vault: codice, artefatti e materiale che non è documentazione.
# `dossier` porta trascrizioni verbatim di conversazioni esterne, che per la regola di stile
# conservano la formattazione della fonte e non si riscrivono.
SKIP_DIRS = {'src', 'tools', 'tests', 'scripts', 'output', 'data',
             '.pytest_cache', '.obsidian', '.git', '__pycache__', 'dossier'}

# La scheda del vault cita i nomi come oggetto di discussione, non come navigazione: convertirli le
# darebbe il grado di un hub e distorcerebbe il grafo che quella scheda descrive.
ESCLUSI = {'docs/vault-obsidian.md'}

# I file il cui mestiere è indicizzare: qui la regola della prima citazione non vale.
INDICI = {'docs/README.md', '.claude/memory/index.md', '.claude/context/studio-didattico-master.md'}

SPAN = re.compile(r'`([^`\n]+?\.md)`')
FENCE = re.compile(r'^\s*(```|~~~)')
ESISTENTE = re.compile(r'\]\(<([^>]+?\.md)>\)|\]\(([^)\s]+?\.md)\)')


def raccogli(radice):
    """Tutti i file Markdown dentro il perimetro indicizzato, in percorsi con la barra normale."""
    trovati = []
    for root, dirs, files in os.walk(radice):
        dirs[:] = [d for d in dirs if d not in SKIP_DIRS]
        for f in files:
            if f.endswith('.md'):
                rel = os.path.relpath(os.path.join(root, f), radice)
                trovati.append(Path(rel).as_posix())
    return sorted(trovati)


def risolvi(contenuto, sorgente, indice, per_base):
    """Dal testo dello span al percorso reale, oppure None quando non si deve indovinare."""
    c = contenuto.strip()
    if c.startswith('./'):
        c = c[2:]
    if '/' not in c and len(per_base.get(c, [])) > 1:
        return None
    base = os.path.dirname(sorgente)
    for tentativo in (os.path.join(base, c), c):
        t = Path(os.path.normpath(tentativo)).as_posix()
        if t in indice:
            return t
    if '/' not in c:
        candidati = per_base.get(c, [])
        if len(candidati) == 1:
            return candidati[0]
    return None


def relativo(destinazione, sorgente):
    """Percorso della destinazione relativo alla nota, in forma angolare se contiene tonde."""
    rel = Path(os.path.relpath(destinazione, os.path.dirname(sorgente) or '.')).as_posix()
    if any(ch in rel for ch in '()% '):
        return '<' + rel + '>'
    return rel


def converti_file(percorso, sorgente, indice, per_base, scrivi, tutte=False):
    testo = io.open(percorso, encoding='utf-8', newline='').read()
    righe = testo.split('\n')
    dentro_fence = False
    dentro_front = bool(righe) and righe[0].strip() == '---'
    cambi = []

    # I bersagli che il file collega già contano come prima citazione fatta: senza questo una
    # seconda corsa collegherebbe la citazione successiva dello stesso bersaglio, e lo strumento
    # aggiungerebbe collegamenti a ogni passaggio invece di convergere.
    base_sorgente = os.path.dirname(sorgente)
    visti = set()
    for m in ESISTENTE.finditer(testo):
        grezzo = m.group(1) or m.group(2)
        visti.add(Path(os.path.normpath(os.path.join(base_sorgente, grezzo))).as_posix())

    for i, riga in enumerate(righe):
        if dentro_front:
            if i > 0 and riga.strip() == '---':
                dentro_front = False
            continue
        if FENCE.match(riga):
            dentro_fence = not dentro_fence
            continue
        if dentro_fence:
            continue

        nuova = riga
        spostamento = 0
        for m in SPAN.finditer(riga):
            contenuto = m.group(1)
            prima = riga[m.start() - 1] if m.start() > 0 else ''
            dopo = riga[m.end():m.end() + 2]
            if prima == '[' or dopo.startswith(']('):
                continue
            dest = risolvi(contenuto, sorgente, indice, per_base)
            if dest is None or dest == sorgente:
                continue
            if not tutte:
                if dest in visti:
                    continue
                visti.add(dest)
            sostituto = '[`' + contenuto + '`](' + relativo(dest, sorgente) + ')'
            a = m.start() + spostamento
            b = m.end() + spostamento
            nuova = nuova[:a] + sostituto + nuova[b:]
            spostamento += len(sostituto) - (b - a)
            cambi.append((i + 1, contenuto, dest))
        righe[i] = nuova

    if cambi and scrivi:
        io.open(percorso, 'w', encoding='utf-8', newline='').write('\n'.join(righe))
    return cambi


def main(argv):
    solo_controllo = '--check' in argv
    radice = '.'
    indice = set(raccogli(radice))
    per_base = {}
    for n in indice:
        per_base.setdefault(os.path.basename(n), []).append(n)

    totale = 0
    for sorgente in sorted(indice):
        if sorgente in ESCLUSI:
            continue
        cambi = converti_file(os.path.join(radice, sorgente), sorgente, indice,
                              per_base, not solo_controllo, sorgente in INDICI)
        if cambi:
            totale += len(cambi)
            print(sorgente + '  (' + str(len(cambi)) + ')')
            for numero, contenuto, dest in cambi:
                print('    riga ' + str(numero).rjust(4) + '  ' + contenuto + '  ->  ' + dest)

    verbo = 'da convertire' if solo_controllo else 'convertiti'
    print(str(len(indice)) + ' file esaminati, ' + str(totale) + ' riferimenti ' + verbo)
    return 1 if (solo_controllo and totale) else 0


if __name__ == '__main__':
    sys.exit(main(sys.argv[1:]))
