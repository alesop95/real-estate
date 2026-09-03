#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Ripristina gli accenti mancanti del tutto, dove la parola senza accento non esiste.

Perche' esiste, e perche' e' diverso da fix-accents
--------------------------------------------------
`fix-accents.py` corregge le forme scritte con l'apostrofo al posto dell'accento, e ha
un vantaggio grosso: l'apostrofo e' un marcatore, quindi lo strumento sa dove guardare.
Qui il problema e' l'opposto e piu' insidioso: parole a cui l'accento manca del tutto,
senza alcun segno che le denunci. Nel materiale ereditato si leggono frasi come "e gia
progettato", "densita sopra completezza", "piu di un estratto", dove nulla distingue a
prima vista un errore da una parola corretta.

Non esiste un modo automatico di risolvere il caso generale, e va detto subito invece di
farlo scoprire a chi legge il codice. La congiunzione e il verbo essere si scrivono con
le stesse due lettere a meno dell'accento, e distinguerli richiede di capire la frase.
Lo stesso vale per la e il la con l'accento, per si e l'affermazione, per ne e il ne
pronominale. Su quelle forme nessuno strumento puo' decidere, e questo non ci prova.

La strategia, che e' l'unica onesta
-----------------------------------
Si converte soltanto dove la forma senza accento non e' una parola italiana. Piu senza
accento non esiste, quindi puo' solo essere piu con l'accento; lo stesso per gia, cosi,
puo, perche, cioe, e per tutte le uscite in -ita, -eta, -ita che senza accento non
significano nulla. Su queste la conversione e' sicura per costruzione, non per euristica.

Tutto il resto si conta e si riporta, e la decisione resta a chi conosce il testo. Il
rapporto separa quindi cio' che lo strumento ha fatto da cio' che ha visto e non ha
toccato, e la seconda lista e' quella che vale la pena leggere.

Le trappole che questa lista ha gia' incontrato
----------------------------------------------
Diverse forme sembravano sicure e non lo sono, e stanno fra le ambigue proprio per
questo. Il gruppo piu' insidioso e' quello dei sostantivi in -ita che coincidono con
la terza persona di un verbo in -itare: eredita, necessita, facilita, mobilita,
nobilita e abilita. Nei testi di questo progetto sono quasi sempre il verbo, come in
un pezzo che si eredita adottando una libreria, e accentarli sarebbe un errore.
Fuori da quel gruppo restano onesta, che e' anche l'aggettivo femminile e in "la risposta
onesta" non vuole l'accento, e unita, che e' anche il participio di unire. Sono tutti
promemoria del fatto che la lista delle sicure si compila guardando i contesti reali del
progetto, non il vocabolario.

Esiste per fortuna una categoria di forme composte su cui il dubbio non c'e': c'e senza
accento non esiste in italiano, perche' e' sempre la contrazione di ci e il verbo essere.
Lo stesso per dov'e e com'e. Quelle si convertono.

Che cosa non guarda
-------------------
I blocchi di codice recintati e i code span, gli indirizzi web e i percorsi di file, dove
una parola senza accento e' un identificatore e non prosa. Nei file di codice lavora solo
su commenti, docstring e stringhe a doppi apici. Conserva fine riga, BOM e newline finale.

Uso
---
    python tools/fix-missing-accents.py --autotest
    python tools/fix-missing-accents.py --check <percorsi>
    python tools/fix-missing-accents.py --ambigue <percorsi>
    python tools/fix-missing-accents.py <percorsi>
"""

import argparse
import os
import re
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

# ---------------------------------------------------------------------------
# Forme sicure: senza accento non sono parole italiane, quindi la conversione non
# richiede di capire la frase. Ordinate per famiglia, cosi' che si veda la regolarita'.
# ---------------------------------------------------------------------------
SICURE = {
    # avverbi e verbi elementari
    "piu": "più", "gia": "già", "cosi": "così", "puo": "può", "cioe": "cioè",
    "giu": "giù", "virtu": "virtù",
    # composti di che, con l'accento acuto
    "perche": "perché", "poiche": "poiché", "benche": "benché",
    "affinche": "affinché", "purche": "purché", "finche": "finché",
    "nonche": "nonché", "anziche": "anziché", "cosicche": "cosicché",
    "sicche": "sicché", "dopodiche": "dopodiché", "giacche": "giacché",
    "fuorche": "fuorché",
    # uscite in -ita e -eta: senza accento non significano nulla
    "citta": "città", "qualita": "qualità", "densita": "densità",
    "verita": "verità", "attivita": "attività", "possibilita": "possibilità",
    "capacita": "capacità", "identita": "identità", "integrita": "integrità",
    "difficolta": "difficoltà", "novita": "novità", "priorita": "priorità",
    "volonta": "volontà", "velocita": "velocità", "modalita": "modalità",
    "personalita": "personalità", "proprieta": "proprietà",
    "quantita": "quantità", "profondita": "profondità",
    "conformita": "conformità", "probabilita": "probabilità",
    "entita": "entità", "liberta": "libertà", "fedelta": "fedeltà",
    "comunita": "comunità", "responsabilita": "responsabilità",
    "ambiguita": "ambiguità", "funzionalita": "funzionalità",
    "facolta": "facoltà", "severita": "severità",
    "accessibilita": "accessibilità", "parita": "parità", "rarita": "rarità",
    "legalita": "legalità", "opportunita": "opportunità",
    "impossibilita": "impossibilità", "polarita": "polarità",
    "plausibilita": "plausibilità", "vulnerabilita": "vulnerabilità",
    "operativita": "operatività", "complessita": "complessità",
    "reciprocita": "reciprocità", "formalita": "formalità",
    "fattibilita": "fattibilità", "comodita": "comodità", "realta": "realtà",
    "affidabilita": "affidabilità", "compatibilita": "compatibilità",
    "disponibilita": "disponibilità", "ammissibilita": "ammissibilità",
    "praticabilita": "praticabilità", "specificita": "specificità",
    "regolarita": "regolarità", "portabilita": "portabilità",
    "leggibilita": "leggibilità", "tracciabilita": "tracciabilità",
    "immutabilita": "immutabilità", "utilita": "utilità",
    "curiosita": "curiosità",
    "generalita": "generalità", "riproducibilita": "riproducibilità",
    "ispezionabilita": "ispezionabilità", "verificabilita": "verificabilità",
    "falsificabilita": "falsificabilità", "recuperabilita": "recuperabilità",
    "copiabilita": "copiabilità", "replicabilita": "replicabilità",
    "discontinuita": "discontinuità", "continuita": "continuità",
    "elettricita": "elettricità", "casualita": "casualità",
    "ricorsivita": "ricorsività", "involutivita": "involutività",
    "ufficialita": "ufficialità", "popolarita": "popolarità",
    "fragilita": "fragilità", "puntualita": "puntualità",
    "meccanicita": "meccanicità",
    "particolarita": "particolarità", "retrocompatibilita": "retrocompatibilità",
    "indisponibilita": "indisponibilità", "commutativita": "commutatività",
}

# Composte in cui la forma senza accento non esiste: si convertono senza dubbio.
COMPOSTE = {
    r"\bc'e\b": "c'è",
    r"\bC'e\b": "C'è",
    r"\bdov'e\b": "dov'è",
    r"\bDov'e\b": "Dov'è",
    r"\bcom'e\b": "com'è",
    r"\bCom'e\b": "Com'è",
}

# ---------------------------------------------------------------------------
# Forme ambigue: si contano e non si toccano. Il motivo accanto a ciascuna serve a chi
# legge il rapporto e deve decidere, e serve a non ridiscutere la classificazione.
# ---------------------------------------------------------------------------
AMBIGUE = {
    "e": "congiunzione oppure il verbo essere",
    "la": "articolo o pronome oppure l'avverbio di luogo con l'accento",
    "li": "pronome oppure l'avverbio di luogo con l'accento",
    "si": "pronome o particella oppure l'affermazione con l'accento",
    "ne": "pronome o particella oppure la negazione con l'accento",
    "se": "congiunzione oppure il pronome riflessivo con l'accento",
    "da": "preposizione oppure il verbo dare con l'accento",
    "tre": "il numero oppure la fine di ventitre con l'accento",
    "meta": "il traguardo oppure la frazione con l'accento",
    "unita": "participio di unire oppure il sostantivo con l'accento",
    "abilita": "terza persona di abilitare oppure il sostantivo con l'accento",
    "onesta": "aggettivo femminile oppure il sostantivo con l'accento",
    "sara": "nome proprio oppure il futuro di essere con l'accento",
    "terra": "il suolo oppure il futuro di tenere con l'accento",
    "eta": "la lettera greca oppure il sostantivo con l'accento",
    "pero": "l'albero oppure la congiunzione con l'accento",
    "porto": "prima persona di portare oppure il passato remoto con l'accento",
    "trovo": "idem",
    "ando": "idem",
    "capito": "participio oppure il passato remoto con l'accento",
    "eredita": "terza persona di ereditare oppure il sostantivo con l'accento",
    "necessita": "terza persona di necessitare oppure il sostantivo con l'accento",
    "facilita": "terza persona di facilitare oppure il sostantivo con l'accento",
    "mobilita": "terza persona di mobilitare oppure il sostantivo con l'accento",
    "nobilita": "terza persona di nobilitare oppure il sostantivo con l'accento",
}

# ---------------------------------------------------------------------------
# La e isolata: ambigua da sola, decidibile in certi contesti.
# ---------------------------------------------------------------------------
# La congiunzione e il verbo essere differiscono per il solo accento, quindi la forma
# nuda resta fra le ambigue. Esistono pero' contesti sintattici in cui la congiunzione e'
# impossibile, e la' la conversione non e' un'euristica ma una deduzione.
#
# Il primo gruppo e' strutturale. Dopo una negazione serve un verbo, quindi "non e" puo'
# essere solo il verbo essere. Dopo la congiunzione "ed" non puo' seguirne un'altra, e la
# forma "ed e" e' quindi sempre il verbo. Dopo il relativo "che", in una prosa che non sia
# un elenco, segue il predicato.
#
# Il secondo gruppo e' lessicale: la e seguita da un aggettivo o da un participio in
# funzione predicativa. Una congiunzione non regge un aggettivo isolato, mentre il verbo
# essere lo pretende: in "e necessariamente manuale" o in "e possibile" la congiunzione
# non ha nulla da coordinare. La lista tiene solo le forme che nel corpus di questi
# progetti ricorrono, perche' una lista esaustiva di aggettivi italiani sarebbe piu'
# fragile e non piu' utile.
E_STRUTTURALI = (
    (r"\bnon e\b(?![\w'])", "non \u00e8"),
    (r"\bNon e\b(?![\w'])", "Non \u00e8"),
    (r"\bed e\b(?![\w'])", "ed \u00e8"),
    (r"\bEd e\b(?![\w'])", "Ed \u00e8"),
    (r"\bche e\b(?![\w'])", "che \u00e8"),
    (r"\bChe e\b(?![\w'])", "Che \u00e8"),
)

# Aggettivi e participi che dopo la e impongono la lettura verbale.
def converti_e(testo, fatte):
    """Applica i soli contesti in cui la congiunzione e' grammaticalmente impossibile."""
    for pattern, reso in E_STRUTTURALI:
        nuovo, n = re.subn(pattern, reso, testo)
        if n:
            fatte[reso] = fatte.get(reso, 0) + n
            testo = nuovo
    return testo


RECINTO = re.compile(r"^\s*(`{3,}|~{3,})")
CODE_SPAN = re.compile(r"`+[^`\n]*`+")
INDIRIZZO = re.compile(r"(?:https?://|ftp://|www\.)\S+")
PERCORSO = re.compile(r"[\w./\\-]*[/\\][\w./\\-]+")
STRINGA_DOPPIA = re.compile(r'"(?:[^"\\\n]|\\.)*"')
DOCSTRING = re.compile(r'"""(?:.|\n)*?"""')

# Il candidato: parola intera, senza distinzione di maiuscole, non attaccata a trattini o
# a caratteri di parola. Il trattino conta come confine perche' nei nomi di file compaiono
# forme come identita-pokemon, che sono identificatori e non prosa.
def costruisci_regex(chiavi):
    alternative = "|".join(sorted(chiavi, key=len, reverse=True))
    return re.compile(r"(?<![\w\-])(" + alternative + r")(?![\w\-])", re.I)


SICURE_RE = costruisci_regex(SICURE)
AMBIGUE_RE = costruisci_regex(AMBIGUE)


def maiuscola_come(originale, sostituto):
    if originale[:1].isupper():
        return sostituto[:1].upper() + sostituto[1:]
    return sostituto


def converti_frammento(testo, fatte, viste):
    """Converte le sicure in un frammento di prosa e conta le ambigue."""
    for m in AMBIGUE_RE.finditer(testo):
        chiave = m.group(1).lower()
        viste[chiave] = viste.get(chiave, 0) + 1

    def sostituisci(m):
        parola = m.group(1)
        chiave = parola.lower()
        atteso = SICURE.get(chiave)
        if atteso is None:
            return m.group(0)
        if parola == atteso:
            return m.group(0)
        fatte[chiave] = fatte.get(chiave, 0) + 1
        return maiuscola_come(parola, atteso)

    testo = SICURE_RE.sub(sostituisci, testo)
    testo = converti_e(testo, fatte)
    for pattern, reso in COMPOSTE.items():
        nuovo, n = re.subn(pattern, reso, testo)
        if n:
            fatte[reso] = fatte.get(reso, 0) + n
            testo = nuovo
    return testo


def converti_prosa(testo, fatte, viste):
    """Converte la prosa proteggendo indirizzi, percorsi e code span.

    Le tre categorie protette si sostituiscono con un segnaposto prima della conversione
    e si ripristinano dopo, invece di essere saltate riga per riga: un indirizzo puo'
    contenere una forma sicura, e convertirla lo renderebbe irraggiungibile.
    """
    protetti = []

    def proteggi(m):
        protetti.append(m.group(0))
        return "\x00%d\x00" % (len(protetti) - 1)

    for pattern in (CODE_SPAN, INDIRIZZO, PERCORSO):
        testo = pattern.sub(proteggi, testo)

    testo = converti_frammento(testo, fatte, viste)

    def ripristina(m):
        return protetti[int(m.group(1))]

    return re.sub(r"\x00(\d+)\x00", ripristina, testo)


def converti_markdown(testo, fatte, viste):
    fuori, dentro, recinto = [], False, None
    for riga in testo.splitlines(keepends=True):
        nudo = riga.rstrip("\n")
        m = RECINTO.match(nudo)
        if not dentro and m:
            dentro, recinto = True, m.group(1)[0] * 3
            fuori.append(riga)
            continue
        if dentro:
            fuori.append(riga)
            if re.match(r"^\s*" + re.escape(recinto), nudo):
                dentro = False
            continue
        fuori.append(converti_prosa(riga, fatte, viste))
    return "".join(fuori)


def converti_python(testo, fatte, viste):
    testo = DOCSTRING.sub(lambda m: converti_prosa(m.group(0), fatte, viste), testo)
    testo = STRINGA_DOPPIA.sub(lambda m: converti_prosa(m.group(0), fatte, viste), testo)
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
        righe.append(prima + converti_prosa(riga[pos:], fatte, viste))
    return "\n".join(righe)


def elabora(percorso, fatte, viste):
    with open(percorso, "rb") as f:
        grezzo = f.read()
    bom = grezzo.startswith(b"\xef\xbb\xbf")
    corpo = grezzo[3:] if bom else grezzo
    crlf = b"\r\n" in corpo
    testo = corpo.decode("utf-8").replace("\r\n", "\n")

    basso = percorso.lower()
    if basso.endswith(".ly"):
        return False, None
    if basso.endswith(".py"):
        nuovo = converti_python(testo, fatte, viste)
    elif basso.endswith((".md", ".lytex")):
        nuovo = converti_markdown(testo, fatte, viste)
    else:
        nuovo = converti_prosa(testo, fatte, viste)

    if nuovo == testo:
        return False, None
    uscita = nuovo.replace("\n", "\r\n") if crlf else nuovo
    dati = uscita.encode("utf-8")
    return True, (b"\xef\xbb\xbf" + dati) if bom else dati


def autotest():
    """Prove interne, con i casi che hanno motivato ciascuna scelta."""
    casi = [
        ("e piu di gia", "e più di già"),
        ("perche cosi", "perché così"),
        ("la densita e la qualita", "la densità e la qualità"),
        ("Piu chiaro", "Più chiaro"),
        # composte inequivocabili
        ("c'e un problema", "c'è un problema"),
        ("dov'e finito", "dov'è finito"),
        # ambigue: non si toccano, nemmeno quando sarebbero giuste
        ("la risposta onesta", "la risposta onesta"),
        ("abilita la ricerca", "abilita la ricerca"),
        ("la meta del lavoro", "la meta del lavoro"),
        ("falso e vero", "falso e vero"),
        # identificatori: il trattino e' un confine, quindi non si tocca
        ("06-identita-pokemon.md", "06-identita-pokemon.md"),
        ("qualita_media = 3", "qualita_media = 3"),
        # gia' accentato: nessun doppio intervento
        ("è già più", "è già più"),
        # la e decidibile per contesto strutturale
        ("questo non e vero", "questo non \u00e8 vero"),
        ("ed e per questo", "ed \u00e8 per questo"),
        ("il fatto che e noto", "il fatto che \u00e8 noto"),
        ("Non e possibile", "Non \u00e8 possibile"),
        # La e nuda resta intatta in ogni altro contesto, compresi quelli in cui a
        # occhio sarebbe il verbo: e' il prezzo di non sbagliare sulle coordinazioni,
        # dove il secondo membro e' proprio un aggettivo o un participio.
        ("e necessario farlo", "e necessario farlo"),
        ("documentato e verificato", "documentato e verificato"),
        ("il codice e la prosa", "il codice e la prosa"),
        ("lettura e scrittura", "lettura e scrittura"),
    ]
    fallite = 0
    for ingresso, atteso in casi:
        f, v = {}, {}
        ottenuto = converti_prosa(ingresso, f, v)
        if ottenuto != atteso:
            print("  FALLITO  %r -> %r, atteso %r" % (ingresso, ottenuto, atteso))
            fallite += 1

    # Protezioni: indirizzo, code span, blocco recintato.
    f, v = {}, {}
    if converti_prosa("vedi http://x.it/qualita/piu ora", f, v) != \
            "vedi http://x.it/qualita/piu ora":
        print("  FALLITO  un indirizzo e' stato modificato")
        fallite += 1
    f, v = {}, {}
    if converti_prosa("il campo `qualita` e piu", f, v) != "il campo `qualita` e più":
        print("  FALLITO  un code span e' stato modificato")
        fallite += 1
    f, v = {}, {}
    doc = "prosa piu\n\n```\ncodice qualita\n```\n\naltra gia\n"
    reso = converti_markdown(doc, f, v)
    if "codice qualita" not in reso or "prosa più" not in reso or "altra già" not in reso:
        print("  FALLITO  il blocco recintato non e' stato protetto")
        fallite += 1

    print("autotest: %d casi, %d falliti" % (len(casi) + 3, fallite))
    return 1 if fallite else 0


def main():
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("percorsi", nargs="*", default=["."])
    ap.add_argument("--autotest", action="store_true")
    ap.add_argument("--check", action="store_true", help="non scrive, riporta")
    ap.add_argument("--ambigue", action="store_true",
                    help="riporta solo le forme ambigue viste, da decidere a mano")
    ap.add_argument("--ext", default=".md,.tex,.txt,.py,.lytex")
    args = ap.parse_args()

    if args.autotest:
        return autotest()

    estensioni = set(e if e.startswith(".") else "." + e for e in args.ext.split(","))
    # Gli strumenti tipografici della stessa famiglia si escludono a vicenda, non solo
    # se stessi. La ragione e' che i loro casi di prova contengono di proposito le
    # sequenze che gli strumenti cercano: una corsa di questo su fix-accents.py ne ha
    # convertito i dati di test e ne ha rotto otto casi. E' la terza volta che questo
    # genere di ricorsione morde, e la difesa e' strutturale.
    FAMIGLIA = {"fix-accents.py", "fix-missing-accents.py", "fix-dashes.py"}
    io_stesso = os.path.abspath(__file__)
    file = []
    for p in args.percorsi or ["."]:
        ap_ = p if os.path.isabs(p) else os.path.join(ROOT, p)
        if os.path.isfile(ap_):
            if os.path.abspath(ap_) != io_stesso and os.path.basename(ap_) not in FAMIGLIA:
                file.append(ap_)
            continue
        for radice, cartelle, nomi in os.walk(ap_):
            cartelle[:] = [c for c in cartelle
                           if c not in (".git", "__pycache__", "node_modules",
                                        ".venv", "_notes", "build")]
            for n in sorted(nomi):
                if os.path.splitext(n)[1].lower() in estensioni:
                    completo = os.path.join(radice, n)
                    if (os.path.abspath(completo) != io_stesso
                            and n not in FAMIGLIA):
                        file.append(completo)

    fatte, viste, cambiati = {}, {}, []
    for percorso in file:
        try:
            cambia, dati = elabora(percorso, fatte, viste)
        except UnicodeDecodeError:
            continue
        if cambia:
            cambiati.append(os.path.relpath(percorso, ROOT))
            if not args.check and not args.ambigue:
                with open(percorso, "wb") as f:
                    f.write(dati)

    if args.ambigue:
        print("forme ambigue viste, che nessuno strumento puo' decidere:")
        for k, v in sorted(viste.items(), key=lambda x: -x[1]):
            print("  %-10s x%-6d %s" % (k, v, AMBIGUE[k]))
        return 0

    print("%d file esaminati, %d %s" % (
        len(file), len(cambiati), "da modificare" if args.check else "modificati"))
    if fatte:
        print("\n%d accenti ripristinati, %d forme:" % (sum(fatte.values()), len(fatte)))
        for k, v in sorted(fatte.items(), key=lambda x: -x[1])[:20]:
            reso = SICURE.get(k, k)
            print("  %-20s -> %-20s x%d" % (k, reso, v))
    if viste:
        tot = sum(viste.values())
        print("\n%d occorrenze di %d forme ambigue non toccate: rilanciare con --ambigue"
              % (tot, len(viste)))
    return 0


if __name__ == "__main__":
    sys.exit(main())
