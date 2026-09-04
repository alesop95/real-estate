# -*- coding: utf-8 -*-
"""Interfaccia a riga di comando del progetto.

Un solo eseguibile con sottocomandi, così che non ci siano più script che si
somigliano e che divergono nel tempo. Il workbook resta il luogo dove si lavora,
la riga di comando serve a generarlo, a popolarlo e a fare un controllo rapido
senza aprire Excel.

Esempi:
    python tools/valuta.py excel
    python tools/valuta.py riepilogo --prezzo 120000 --rendita 450 --mutuo 90000 --canone 500
    python tools/valuta.py annunci elenca
    python tools/valuta.py annunci aggiungi --link https://... --comune "..." --prezzo 89000 --mq 75
    python tools/valuta.py annunci importa --link https://...
    python tools/valuta.py annunci esporta
    python tools/valuta.py omi scarica --semestre 2018-2
    python tools/valuta.py omi importa --file "QI_xxxxx.zip"
    python tools/valuta.py omi zone --comune "NOME DEL COMUNE"
    python tools/valuta.py omi cerca --comune "NOME DEL COMUNE"
    python tools/valuta.py tassi
    python tools/valuta.py tassi --tasso 0.032 --mutuo 90000 --durata 25
    python tools/valuta.py llm stato
"""

from __future__ import annotations

import argparse
import datetime as _dt
import sys
from pathlib import Path

RADICE = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(RADICE / "src"))

from immobiliare import annunci as A  # noqa: E402
from immobiliare import calcoli as C  # noqa: E402
from immobiliare import comuni as M  # noqa: E402
from immobiliare import excel_builder as E  # noqa: E402
from immobiliare import indicatori as N  # noqa: E402
from immobiliare import omi as O  # noqa: E402
from immobiliare import parametri as P  # noqa: E402
from immobiliare import tassi as T  # noqa: E402

WORKBOOK = RADICE / "output" / "Valutazione-Immobile.xlsx"
ARCHIVIO = RADICE / "data" / "annunci.csv"


def euro(x: float) -> str:
    return f"{x:>14,.0f} EUR".replace(",", ".")


def pct(x: float) -> str:
    return f"{x:>14.2%}"


# ---------------------------------------------------------------------------

def cartella_immobile(identificativo: str):
    """La cartella che raccoglie tutto ciò che riguarda un immobile.

    Esiste perché un immobile produce più di un file: il workbook
    precompilato, il sorgente della scheda, il PDF della scheda e gli ausiliari
    di compilazione. Tenerli in cartelle diverse per tipo, come si faceva
    all'inizio con un `output/schede/` separato, ha il difetto di dividere per
    formato ciò che si consulta per immobile: chi apre la cartella di house_6
    vuole vedere tutto di house_6, non i sorgenti LaTeX di quattordici immobili
    mescolati.
    """
    return RADICE / "output" / "immobili" / identificativo


def cmd_excel(args) -> int:
    # Con `--da-annuncio` la destinazione predefinita è la cartella
    # dell'immobile e non il file-modello. La versione precedente scriveva sul
    # modello, quindi un `excel --da-annuncio house_6` senza `--output` lo
    # sostituiva con un file dedicato a quell'immobile, e il modello da cui
    # partire per il successivo non c'era più.
    if args.output:
        destinazione = Path(args.output)
    elif args.da_annuncio:
        destinazione = cartella_immobile(args.da_annuncio) / f"{args.da_annuncio}.xlsx"
    else:
        destinazione = WORKBOOK
    destinazione.parent.mkdir(parents=True, exist_ok=True)
    E.genera(str(destinazione))
    print(f"Workbook generato: {destinazione}")
    if args.con_annunci and ARCHIVIO.exists():
        registro = A.Registro(ARCHIVIO)
        scritti = A.esporta_in_excel(registro, str(destinazione))
        print(f"Annunci riversati nel foglio Annunci: {scritti}")

    if args.da_annuncio:
        if not ARCHIVIO.exists():
            print(f"Nessun registro in {ARCHIVIO}: --da-annuncio non ha da dove leggere.")
            return 1
        registro = A.Registro(ARCHIVIO)
        annuncio = next((a for a in registro.annunci if a.id == args.da_annuncio), None)
        if annuncio is None:
            disponibili = ", ".join(a.id for a in registro.annunci)
            print(f"Annuncio {args.da_annuncio!r} non a registro. Disponibili: {disponibili}")
            return 1
        try:
            esito = A.precompila_workbook(annuncio, str(destinazione))
        except ValueError as e:
            print(f"Precompilazione non possibile: {e}")
            return 1

        print()
        print(f"PRECOMPILATO DA {annuncio.id}, {annuncio.comune or 'Comune non indicato'}")
        for nome, (cella, valore, formato) in esito["scritti"].items():
            if formato == "euro":
                mostrato = euro(valore)
            elif formato == "numero":
                mostrato = f"{valore:,.0f}".replace(",", ".")
            else:
                mostrato = str(valore)
            print(f"  {nome:<16}{cella:<26}{mostrato:>18}")

        da_chiedere = [(n, c) for n, c, natura in esito["assenti"] if natura == "da_chiedere"]
        neutri = [(n, c) for n, c, natura in esito["assenti"] if natura == "neutro"]
        if da_chiedere:
            print()
            print("  Azzerati perché il registro non li ha: sono i campi da chiedere. Le")
            print("  celle sono state svuotate invece di lasciare il valore di esempio, così")
            print("  che il foglio mostri un modello visibilmente incompleto invece di uno")
            print("  apparentemente sano calcolato su dati inventati. I controlli di")
            print("  plausibilità del Cruscotto li segnalano tutti.")
            for nome, campo in da_chiedere:
                precedente = next((p for n, _, p in esito["azzerati"] if n == nome), None)
                nota = "" if precedente in (None, "") else f"   (l'esempio diceva {precedente})"
                print(f"    {nome:<16}dal campo {campo}{nota}")
        if neutri:
            print()
            print("  Lasciati vuoti a ragione, non sono lacune. I due campi del regime di")
            print("  acquisto vuoti significano eredita dal foglio Immobile, e la base d'asta")
            print("  riguarda solo le vendite giudiziarie.")
            for nome, campo in neutri:
                print(f"    {nome:<16}dal campo {campo}")
        if esito["rifiutati"]:
            print()
            print("  Rifiutati per sicurezza:")
            for nome, ragione in esito["rifiutati"]:
                print(f"    {nome:<16}{ragione}")
        print()
        print("  Restano da compilare a mano le voci che il registro non porta e che")
        print("  cambiano di più il risultato: aliquota IMU dalla delibera del Comune,")
        print("  importo e tasso del mutuo dal preventivo, e la verifica che le spese")
        print("  condominiali vengano dal consuntivo e non dalla stima dell'agenzia.")

    print()
    print("Parametri fiscali della revisione", P.REVISIONE.strftime("%d/%m/%Y"))
    print("Le celle gialle sono gli input. Verificare sempre l'aliquota IMU nella")
    print("delibera del Comune e le spese nel consuntivo condominiale.")
    return 0


def cmd_scheda(args) -> int:
    """Scheda di una pagina per la trattativa, in LaTeX."""
    if not ARCHIVIO.exists():
        print(f"Nessun registro in {ARCHIVIO}.")
        return 1
    registro = A.Registro(ARCHIVIO)
    annuncio = next((a for a in registro.annunci if a.id == args.id), None)
    if annuncio is None:
        disponibili = ", ".join(a.id for a in registro.annunci)
        print(f"Annuncio {args.id!r} non a registro. Disponibili: {disponibili}")
        return 1

    from immobiliare import scheda as S

    sorgente = S.costruisci(
        annuncio,
        mutuo=args.mutuo,
        tasso=args.tasso,
        durata=args.durata,
        imu_aliquota=args.imu,
        rendimento_obiettivo=args.obiettivo,
    )

    destinazione = Path(args.output) if args.output else cartella_immobile(annuncio.id) / f"{annuncio.id}.tex"
    destinazione.parent.mkdir(parents=True, exist_ok=True)
    destinazione.write_text(sorgente, encoding="utf-8")
    print(f"Sorgente della scheda: {destinazione}")

    mancanti = [c for c, _, _ in A.CAMPI_BLOCCANTI if not getattr(annuncio, c, None)]
    if mancanti:
        print()
        print(f"La scheda e' marcata incompleta: mancano {len(mancanti)} dati bloccanti")
        print(f"  {', '.join(mancanti)}")
        print("I numeri restano calcolati su ciò che c'è, e la scheda lo dichiara in testa.")

    print()
    print("Per ottenere il PDF:")
    relativo = destinazione.relative_to(RADICE) if destinazione.is_relative_to(RADICE) else destinazione
    print(f"  powershell -NoProfile -ExecutionPolicy Bypass -File scripts\\build.ps1 -Main {relativo}")
    print(f"  bash scripts/build.sh --main {str(relativo).replace(chr(92), '/')}")
    print()
    print("La cartella output non è versionata, ed è voluto: la scheda porta il prezzo")
    print("obiettivo, che è la propria strategia di acquisto.")
    return 0


def cmd_riepilogo(args) -> int:
    immobile = C.Immobile(
        prezzo=args.prezzo,
        rendita_catastale=args.rendita,
        categoria=args.categoria,
        superficie_mq=args.mq,
        comune=args.comune,
        venditore_impresa=args.da_impresa,
    )
    acquirente = C.Acquirente(
        prima_casa=not args.no_prima_casa,
        quota=args.quota,
        prezzo_valore=not args.no_prezzo_valore,
        reddito_imponibile_irpef=args.reddito,
    )
    finanziamento = C.Finanziamento(
        importo=args.mutuo, tasso_annuo=args.tasso, durata_anni=args.durata
    )
    costo = C.costo_operazione(
        immobile, acquirente, finanziamento,
        provvigione_pct=args.provvigione, notaio_compravendita=args.notaio,
        altri_costi=args.altri_costi,
    )
    imposte = costo.imposte

    print("=" * 74)
    print(f"  {args.comune or 'Immobile'} - {immobile.prezzo:,.0f} EUR".replace(",", "."))
    print("=" * 74)
    print()
    print("COSTO DELL'OPERAZIONE")
    print(f"  Regime                    {imposte.regime}")
    print(f"  Base imponibile           {euro(imposte.imponibile)}")
    if imposte.iva:
        print(f"  IVA                       {euro(imposte.iva)}")
    print(f"  Imposta di registro       {euro(imposte.registro)}")
    print(f"  Ipotecaria e catastale    {euro(imposte.ipotecaria + imposte.catastale)}")
    print(f"  Totale imposte            {euro(imposte.totale)}")
    print(f"  Provvigione con IVA       {euro(costo.provvigione)}")
    print(f"  Notaio compravendita      {euro(costo.notaio_compravendita)}")
    if costo.mutuo:
        print(f"  Oneri del mutuo           {euro(costo.notaio_mutuo + costo.sostitutiva_mutuo + costo.istruttoria + costo.perizia)}")
    print(f"  Altri costi               {euro(costo.altri_costi)}")
    print(f"  {'-' * 60}")
    print(f"  Costi accessori           {euro(costo.costi_accessori)}   ({costo.incidenza_costi:.1%} del prezzo)")
    print(f"  Costo totale              {euro(costo.costo_totale)}")
    print(f"  Esborso iniziale          {euro(costo.esborso_iniziale)}")

    if finanziamento.importo:
        rata = C.rata_francese(finanziamento.importo, finanziamento.tasso_annuo, finanziamento.durata_anni)
        piano = C.piano_ammortamento(finanziamento.importo, finanziamento.tasso_annuo, finanziamento.durata_anni)
        interessi = sum(r.quota_interessi for r in piano)
        per_anno = C.interessi_per_anno(piano)
        print()
        print("MUTUO")
        print(f"  Rata mensile              {euro(rata)}")
        print(f"  Loan to value             {pct(finanziamento.importo / immobile.prezzo)}")
        print(f"  Interessi totali          {euro(interessi)}")
        detrazione = C.detrazione_interessi(per_anno[1], acquirente.quota, args.abitazione_principale)
        print(f"  Detrazione primo anno     {euro(detrazione)}" + ("" if args.abitazione_principale else "   (nulla: non è abitazione principale)"))
    else:
        rata = 0.0

    if args.canone:
        print()
        print("MESSA A REDDITO, CONFRONTO FRA REGIMI")
        print(f"  {'Regime':<24}{'NOI':>16}{'Utile netto':>16}{'Rend. netto':>16}")
        for regime, etichetta in [
            ("cedolare_libero", "Cedolare 21%"),
            ("cedolare_concordato", "Cedolare concordato 10%"),
            ("irpef_ordinario", "IRPEF ordinaria"),
        ]:
            # Senza un canone concordato esplicito si applica lo sconto tipico
            # dichiarato in `parametri`. Usare lo stesso canone del libero darebbe al
            # concordato l'aliquota ridotta senza il minor canone che la giustifica,
            # e lo farebbe vincere sempre: un confronto così non è un confronto.
            if regime.endswith("concordato"):
                canone = args.canone_concordato or args.canone * (1 - P.LOCAZIONE.sconto_canone_concordato)
            else:
                canone = args.canone
            gestione = C.Gestione(
                canone_mensile=canone,
                regime=regime,
                mesi_sfitto_annui=args.sfitto,
                condominio_annuo=args.condominio,
                aliquota_imu=args.imu,
            )
            conto = C.conto_economico(immobile, gestione, acquirente.reddito_imponibile_irpef)
            # Il conto economico include già l'accantonamento per la ristrutturazione
            # di fine ciclo, che pesa uguale su ogni regime ma va sottratto: ignorarlo
            # gonfia tutti i rendimenti. Vedi ADR-005.
            print(f"  {etichetta:<24}{conto.noi:>12,.0f} EUR{conto.utile_netto:>12,.0f} EUR{conto.utile_netto / costo.costo_totale:>15.2%}".replace(",", "."))

        if not args.canone_concordato:
            sconto = P.LOCAZIONE.sconto_canone_concordato
            print(f"  Il canone concordato e' stimato con lo sconto tipico del {sconto:.0%} sul libero,")
            print(f"  cioe' {args.canone * (1 - sconto):,.0f} EUR al mese. Il valore vero viene dall'accordo".replace(",", "."))
            print("  territoriale del Comune: si passa con --canone-concordato.")

        gestione = C.Gestione(
            canone_mensile=args.canone, regime=args.regime, mesi_sfitto_annui=args.sfitto,
            condominio_annuo=args.condominio, aliquota_imu=args.imu,
        )
        conto = C.conto_economico(immobile, gestione, acquirente.reddito_imponibile_irpef)
        metriche = C.metriche(costo, conto, rata * 12)
        print()
        print(f"INDICATORI, regime {args.regime}")
        print(f"  Rendimento lordo          {pct(metriche.rendimento_lordo)}")
        print(f"  Rendimento netto          {pct(metriche.rendimento_netto)}")
        print(f"  Cap rate                  {pct(metriche.cap_rate)}")
        print(f"  Cash on cash              {pct(metriche.cash_on_cash)}")
        print(f"  DSCR                      {metriche.dscr:>14.2f}" + ("   (sotto 1: il reddito non copre la rata)" if metriche.dscr < 1 else ""))
        print(f"  Cash flow annuo           {euro(metriche.cash_flow_annuo)}")

        flussi = [-costo.esborso_iniziale] + [metriche.cash_flow_annuo] * args.orizzonte
        valore_finale = immobile.prezzo * (1 + args.rivalutazione) ** args.orizzonte
        residuo = 0.0
        if finanziamento.importo:
            piano = C.piano_ammortamento(finanziamento.importo, finanziamento.tasso_annuo, finanziamento.durata_anni)
            indice = min(args.orizzonte * 12, len(piano)) - 1
            residuo = piano[indice].debito_residuo if indice >= 0 else 0.0
        flussi[-1] += valore_finale * 0.97 - residuo
        print(f"  TIR su {args.orizzonte} anni            {pct(C.tir(flussi))}")
        print()
        print("  Il TIR qui assume un cash flow costante nel tempo. Il foglio Cash flow del")
        print("  workbook indicizza invece i costi all'inflazione e da' un valore più basso:")
        print("  per una decisione vale quello, questo serve solo a scremare in fretta.")

    print()
    print("Fonti dei parametri: foglio Fonti del workbook, oppure docs/fonti.md.")
    print(f"Revisione fiscale: {P.REVISIONE.strftime('%d/%m/%Y')}.")
    return 0


# ---------------------------------------------------------------------------

def cmd_annunci(args) -> int:
    registro = A.Registro(ARCHIVIO)

    if args.azione == "mancanti":
        """Che cosa manca su ogni immobile, e che cosa quel dato blocca.

        Il registro accetta un immobile col solo link, ed è giusto, perché
        altrimenti non si registrerebbe nulla. La conseguenza è che a metà
        percorso non si sa più quale immobile sia pronto per la valutazione e
        quale aspetti un dato, e la domanda non ha una risposta a vista: le
        celle vuote di un CSV di trentacinque colonne non si contano a occhio.
        Questo comando la risponde, e non elenca i campi vuoti ma quelli che
        bloccano un calcolo, dicendo quale.
        """
        # La mappa vive in `annunci.CAMPI_BLOCCANTI`, perché la usa anche la
        # scheda di trattativa: due copie divergerebbero, e la divergenza non
        # produrrebbe un errore ma una scheda che dice di chiedere una cosa
        # diversa da quella che questo comando segnala.
        BLOCCHI = A.CAMPI_BLOCCANTI

        if not registro.annunci:
            print("Registro vuoto.")
            return 0

        pronti, incompleti = [], []
        for a in sorted(registro.annunci, key=lambda x: (-x.punteggio, x.id)):
            mancano = [(campo, blocca, come) for campo, blocca, come in BLOCCHI
                       if not getattr(a, campo)]
            if mancano:
                incompleti.append((a, mancano))
            else:
                pronti.append(a)

        # Una riga per immobile. L'informazione su cosa blocca un campo e come si
        # ottiene è per campo e non per immobile, quindi sta nella legenda in
        # fondo e non ripetuta quattordici volte: ripeterla trasformerebbe una
        # risposta da dieci secondi in centoventisei righe da leggere.
        print("CHE COSA MANCA, un immobile per riga")
        print()
        print(f"  {'ID':<10}{'prio':>4}  {'comune':<20}{'manca':>6}  campi da chiedere")
        print("  " + "-" * 96)
        for a, mancano in incompleti:
            nomi = ", ".join(campo for campo, _, _ in mancano)
            for indice, riga in enumerate(_a_capo(nomi, 52)):
                if indice == 0:
                    print(f"  {a.id:<10}{a.punteggio:>4}  {a.comune[:19]:<20}{len(mancano):>6}  {riga}")
                else:
                    print(f"  {'':<10}{'':>4}  {'':<20}{'':>6}  {riga}")
        for a in pronti:
            print(f"  {a.id:<10}{a.punteggio:>4}  {a.comune[:19]:<20}{0:>6}  pronto per la valutazione completa")

        # La legenda: solo i campi che mancano davvero a qualcuno, perché una
        # legenda che spiega campi che nessuno deve chiedere è rumore.
        da_chiedere = {campo for _, mancano in incompleti for campo, _, _ in mancano}
        if da_chiedere:
            print()
            print("CHE COSA BLOCCA CIASCUN CAMPO, e come si ottiene")
            print()
            for campo, blocca, come in BLOCCHI:
                if campo not in da_chiedere:
                    continue
                quanti = sum(1 for _, mancano in incompleti
                             if campo in {c for c, _, _ in mancano})
                print(f"  {campo}   manca su {quanti} immobili")
                for riga in _a_capo(f"blocca {blocca}", 92):
                    print(f"    {riga}")
                for riga in _a_capo(f"come: {come}", 92):
                    print(f"    {riga}")
                print()

        print(f"{len(pronti)} pronti su {len(registro.annunci)} a registro.")
        if pronti:
            print()
            print("Su uno dei pronti si genera il workbook precompilato con:")
            print(f"  python tools/valuta.py excel --con-annunci --da-annuncio {pronti[0].id}")
        else:
            print("Il lavoro utile adesso è chiedere i dati mancanti, non rifare i conti.")
            comuni = sorted({a.comune for a, _ in incompleti if a.comune})
            senza_rendita = [a.id for a, m in incompleti
                             if "rendita_catastale" in {c for c, _, _ in m}]
            if senza_rendita:
                print()
                print(f"La rendita catastale manca su {len(senza_rendita)} immobili e si chiede")
                print("con una mail sola all'agenzia, insieme alla superficie calpestabile e al")
                print("consuntivo condominiale: sono i tre dati che sbloccano tutto il resto.")
            if comuni:
                print()
                print("Comuni coinvolti, per la delibera IMU da cercare: " + ", ".join(comuni))
        return 0

    if args.azione == "confronta":
        """Graduatoria degli immobili a registro, ordinata per scarto sulla zona.

        Risponde alla domanda che viene prima di ogni altra, cioè quale merita
        un'ora di lavoro, e la risponde senza aprire Excel. Il criterio di
        ordinamento è lo scarto sulla quotazione di zona e non il prezzo,
        perché fra immobili di taglia diversa il prezzo non dice nulla.
        """
        quotazioni, _ = O.carica_cartella(RADICE / "data" / "omi")
        completi = [a for a in registro.annunci if a.mq and a.prezzo_richiesto]
        if not completi:
            print("Nessun annuncio con superficie e prezzo. Prima: annunci aggiungi oppure importa.")
            return 1

        def canone_di_zona(annuncio):
            """Canone mensile atteso dalla zona, non dall'annuncio."""
            if not (annuncio.zona_omi and quotazioni):
                return None
            normali = [
                r for r in O.cerca(quotazioni, annuncio.comune, zona=annuncio.zona_omi)
                if r.stato.strip().upper().startswith("NORMALE")
            ]
            if not normali:
                return None
            minimo = min(r.locazione_min for r in normali) * annuncio.mq
            massimo = max(r.locazione_max for r in normali) * annuncio.mq
            return minimo, massimo

        def segnalazioni(annuncio):
            """Bandiere rosse ricavate dalle note, che restano testo libero.

            È un'euristica dichiarata, non una classificazione: le note le
            scrive una persona e queste parole chiave sono quelle che quella
            persona ha usato finora. Serve a non perdere di vista un immobile
            già locato o da ristrutturare mentre si guarda una tabella.
            """
            note = (annuncio.note or "").lower()
            trovate = []
            if "locato" in note or "affittato" in note:
                trovate.append("locato")
            if "ristrutturare" in note:
                trovate.append("da ristrutturare")
            # Le due frasi esatte, non le parole singole: "ipotesi" da solo
            # pescava "ogni ipotesi abitativa" su un annuncio che non c'entrava,
            # e un flag che compare dove non serve smette di voler dire qualcosa.
            # Il primo tentativo di correzione ancorava la ricerca al contesto
            # con uno split, ed era troppo furbo: perdeva i casi in cui la frase
            # stava lontana dall'ancora. Due frasi intere bastano e si leggono.
            if "per ipotesi" in note or "da confermare" in note:
                trovate.append("zona incerta")
            if "destinazione ufficio" in note or "cambio d uso" in note or "cambio d'uso" in note:
                trovate.append("uso non abitativo")
            if "discordante" in note or "contraddizione" in note or "incoerenti" in note:
                trovate.append("dati incoerenti")
            # Questa non viene dalle note ma dal campo, e non è un difetto
            # dell'immobile: è l'avviso che quella riga non è commensurabile
            # alle altre a colpo d'occhio, perché paga l'IVA sul prezzo intero
            # invece dell'imposta di registro sul valore catastale.
            if annuncio.venditore_impresa == "SI":
                trovate.append("IVA, non registro")
            if not annuncio.rendita_catastale:
                trovate.append("manca rendita")
            return trovate

        completi.sort(key=lambda a: (a.scarto_su_omi if a.zona_omi else 9.9, -a.punteggio))

        print(f"{'ID':<10}{'prio':>4}  {'comune':<12}{'zona':<5}{'mq':>5}{'prezzo':>10}"
              f"{'EUR/mq':>9}{'scarto':>8}  {'canone di zona':<16}{'lordo':>13}  segnalazioni")
        print("-" * 132)
        for a in completi:
            zona = a.zona_omi or "-"
            scarto = f"{a.scarto_su_omi:+.0%}" if a.zona_omi and a.quotazione_omi_min else "n.d."
            intervallo = canone_di_zona(a)
            if intervallo:
                lo, hi = intervallo
                canone = f"{lo:,.0f}-{hi:,.0f}".replace(",", ".")
                lordo = f"{lo * 12 / a.prezzo_richiesto:.1%}-{hi * 12 / a.prezzo_richiesto:.1%}"
            else:
                canone, lordo = "zona non indicata", ""
            # I numeri si formattano prima e da soli: applicare la sostituzione
            # del separatore all'intera riga mangerebbe anche le virgole che
            # separano le segnalazioni, trasformando un elenco in una frase rotta.
            prezzo = f"{a.prezzo_richiesto:>10,.0f}".replace(",", ".")
            al_mq = f"{a.prezzo_mq:>9,.0f}".replace(",", ".")
            print(f"{a.id:<10}{a.punteggio:>4}  {a.comune[:11]:<12}{zona:<5}{a.mq:>5.0f}"
                  f"{prezzo}{al_mq}{scarto:>8}  "
                  f"{canone:<16}{lordo:>13}  {', '.join(segnalazioni(a))}")

        incompleti = [a for a in registro.annunci if not (a.mq and a.prezzo_richiesto)]
        print()
        print(f"{len(completi)} immobili confrontabili su {len(registro.annunci)} a registro.")
        if incompleti:
            print(f"Senza superficie o prezzo, quindi fuori dal confronto: {', '.join(a.id for a in incompleti)}.")
        senza_zona = [a.id for a in completi if not a.zona_omi]
        if senza_zona:
            print(f"Senza zona OMI, quindi con lo scarto calcolato sull'intero Comune: {', '.join(senza_zona)}.")
            print("La zona si trova con: python tools/valuta.py omi zone --comune \"...\"")
        print()
        print("Il canone di zona viene dalle quotazioni OMI di locazione, non dall'annuncio:")
        print(f"e' quanto la zona paga per quella superficie. Fonte: {O.ATTRIBUZIONE}.")
        return 0
    if args.azione == "omi":
        # Aggancia il registro alla fornitura in cache. È il passo che rende
        # utile la colonna dello scarto nel workbook, che senza quotazioni resta
        # vuota e fa sembrare il confronto fra immobili più povero di quanto sia.
        cartella_omi = RADICE / "data" / "omi"
        quotazioni, letti = O.carica_cartella(cartella_omi)
        if not quotazioni:
            print("Nessuna fornitura OMI in data/omi. Prima: python tools/valuta.py omi importa --file ...")
            return 1

        aggiornati = 0
        senza = []
        for annuncio in registro.annunci:
            if args.id and annuncio.id != args.id:
                continue
            if not annuncio.comune:
                senza.append((annuncio.id, "manca il Comune"))
                continue
            minimo, massimo, provenienza = O.quotazione_di_riferimento(
                quotazioni, annuncio.comune, annuncio.zona_omi, args.tipologia_omi or "Abitazioni civili"
            )
            if not minimo:
                simili = O.comuni_simili(quotazioni, annuncio.comune)
                motivo = f"Comune non trovato; forse: {', '.join(simili[:3])}" if simili else "Comune non trovato"
                senza.append((annuncio.id, motivo))
                continue
            annuncio.quotazione_omi_min = minimo
            annuncio.quotazione_omi_max = massimo
            aggiornati += 1
            scarto = annuncio.scarto_su_omi
            print(f"  {annuncio.id:<10}{minimo:>8,.0f} - {massimo:<8,.0f} EUR/mq".replace(",", ".")
                  + (f"  scarto {scarto:+.0%}" if scarto else "  scarto non calcolabile")
                  + f"   [{provenienza}]")

        for identificativo, motivo in senza:
            print(f"  {identificativo:<10}non aggiornato: {motivo}")

        if aggiornati:
            registro.salva()
            print()
            print(f"Aggiornati {aggiornati} annunci in {registro.percorso}.")
            print(f"Fornitura: {', '.join(letti)} - fonte: {O.ATTRIBUZIONE}")
            print("Per riversarli nel workbook: python tools/valuta.py excel --con-annunci")
        return 0 if aggiornati else 1
    if args.azione == "elenca":
        if not registro.annunci:
            print("Nessun annuncio in archivio.")
            return 0
        print(f"{'ID':<10}{'Stato':<16}{'Comune':<22}{'Mq':>5}{'Prezzo':>12}{'EUR/mq':>9}{'Rend.':>8}  Link")
        print("-" * 130)
        for a in registro.ordina_per_convenienza():
            print(
                f"{a.id:<10}{a.stato:<16}{a.comune[:21]:<22}{a.mq:>5.0f}"
                f"{a.prezzo_richiesto:>12,.0f}{a.prezzo_mq:>9,.0f}".replace(",", ".")
                + f"{a.rendimento_lordo:>8.1%}  {a.link[:52]}"
            )
        print(f"\n{len(registro.annunci)} annunci in {ARCHIVIO}")
        return 0

    if args.azione == "aggiungi":
        annuncio = A.Annuncio(
            link=args.link or "", comune=args.comune or "", provincia=args.provincia or "",
            indirizzo=args.indirizzo or "", tipologia=args.tipologia or "",
            destinazione_uso=args.destinazione or "", mq=args.mq or 0.0,
            prezzo_richiesto=args.prezzo or 0.0, prezzo_obiettivo=args.obiettivo or 0.0,
            canone_atteso_mese=args.canone or 0.0,
            fonte=args.fonte or (args.link.split("/")[2] if args.link else ""),
            agenzia=args.agenzia or "", contatto=args.contatto or "",
            nuova_costruzione="SI" if args.nuova else "NO",
            data_consegna=args.consegna or "", note=args.note or "",
            punteggio=args.punteggio or 0, zona_omi=args.zona_omi or "",
            rendita_catastale=args.rendita or 0.0, categoria=args.categoria or "",
            spese_condominio_anno=args.condominio or 0.0, piano=args.piano or "",
            classe_energetica=args.classe_energetica or "",
            prima_casa=args.prima_casa or "", venditore_impresa=args.venditore_impresa or "",
            quotazione_omi_min=args.quotazione_omi_min or 0.0,
            quotazione_omi_max=args.quotazione_omi_max or 0.0,
        )
        try:
            registro.aggiungi(annuncio)
        except ValueError as e:
            print(f"Non aggiunto: {e}")
            return 1
        registro.salva()
        print(f"Aggiunto {annuncio.id} in {ARCHIVIO}")
        return 0

    if args.azione == "modifica":
        if not args.id:
            print("Serve --id.")
            return 2
        annuncio = registro.trova(args.id)
        if annuncio is None:
            print(f"Nessun annuncio con id {args.id}")
            return 1
        modifiche = {
            "punteggio": args.punteggio, "zona_omi": args.zona_omi, "stato": args.stato,
            "comune": args.comune, "provincia": args.provincia, "indirizzo": args.indirizzo,
            "tipologia": args.tipologia, "mq": args.mq, "prezzo_richiesto": args.prezzo,
            "prezzo_obiettivo": args.obiettivo, "canone_atteso_mese": args.canone,
            "agenzia": args.agenzia, "contatto": args.contatto, "note": args.note,
            # I campi bloccanti, aggiunti perché senza di loro il percorso si
            # interrompeva: `annunci mancanti` li chiedeva e nulla li accettava.
            "rendita_catastale": args.rendita, "categoria": args.categoria,
            "spese_condominio_anno": args.condominio, "piano": args.piano,
            "classe_energetica": args.classe_energetica,
            "prima_casa": args.prima_casa, "venditore_impresa": args.venditore_impresa,
            "quotazione_omi_min": args.quotazione_omi_min,
            "quotazione_omi_max": args.quotazione_omi_max,
        }
        applicate = []
        for campo, valore in modifiche.items():
            if valore is None or valore == "":
                continue
            setattr(annuncio, campo, valore)
            applicate.append(f"{campo}={valore}")
        if not applicate:
            print("Nessun campo da modificare: indicare almeno un'opzione.")
            return 2
        registro.salva()
        print(f"Aggiornato {annuncio.id}: {', '.join(applicate)}")
        return 0

    if args.azione == "rimuovi":
        if registro.rimuovi(args.id):
            registro.salva()
            print(f"Rimosso {args.id}")
            return 0
        print(f"Nessun annuncio con id {args.id}")
        return 1

    if args.azione == "importa":
        testo = ""
        if args.file:
            testo = Path(args.file).read_text(encoding="utf-8", errors="replace")
        elif args.link:
            consentito, motivo = A.robots_consente(args.link)
            print(f"Controllo robots.txt: {motivo}")
            if not consentito:
                print()
                print("Il prelievo automatico non è consentito da questo sito. Le vie corrette sono")
                print("due: aprire la pagina nel browser, copiare il testo dell'annuncio in un file e")
                print("passarlo con --file, oppure inserire i dati a mano con il sottocomando aggiungi.")
                return 2
            try:
                testo = A.testo_da_html(A.scarica_pagina(args.link))
            except A.PrelievoBloccato as e:
                # Il robots.txt consentiva il percorso e il server ha negato lo
                # stesso: è la protezione anti bot, non un guasto, e non si
                # insiste. Il messaggio dell'eccezione porta già le alternative.
                print(str(e))
                return 2
            except Exception as e:
                print(f"Prelievo fallito: {e}")
                return 1
        else:
            print("Serve --link oppure --file.")
            return 2

        try:
            dati = A.struttura_con_modello_locale(testo, args.link or "")
        except Exception as e:
            print(f"Strutturazione con il modello locale fallita: {e}")
            print("Verificare l'host con: python tools/valuta.py llm stato")
            return 1

        campi_validi = {f for f in registro.colonne}
        annuncio = A.Annuncio(**{k: v for k, v in dati.items() if k in campi_validi and v not in (None, "")})
        try:
            registro.aggiungi(annuncio)
        except ValueError as e:
            print(f"Non aggiunto: {e}")
            return 1
        registro.salva()
        print(f"Aggiunto {annuncio.id}: {annuncio.comune} {annuncio.mq:.0f} mq {annuncio.prezzo_richiesto:,.0f} EUR".replace(",", "."))
        return 0

    if args.azione == "esporta":
        if not WORKBOOK.exists():
            print("Il workbook non esiste: generarlo prima con il sottocomando excel.")
            return 1
        scritti = A.esporta_in_excel(registro, str(WORKBOOK))
        print(f"{scritti} annunci scritti nel foglio Annunci di {WORKBOOK}")
        return 0

    return 2


def cmd_comune(args) -> int:
    """Dove leggere i due parametri che nessuna fonte nazionale fornisce, e cosa risulta letto."""
    cartella = RADICE / "data" / "omi"
    anno = args.anno or _dt.date.today().year

    if args.elenca:
        conosciuti = M.elenca(cartella)
        righe = [c for c in conosciuti.values()
                 if not args.provincia or c.provincia.upper() == args.provincia.upper()]
        if not righe:
            print("Nessun Comune in cache" + (f" per la provincia {args.provincia}." if args.provincia else "."))
            print("La fornitura OMI si importa con: python tools/valuta.py omi importa --file ...")
            return 1
        for c in sorted(righe, key=lambda x: x.nome):
            print(f"  {c.codice_catastale:<6} {c.provincia:<3} {c.nome}")
        print()
        print(f"{len(righe)} Comuni, dai file OMI in cache.")
        return 0

    if not args.nome:
        print("Serve --nome con il Comune, oppure --elenca.")
        return 2

    comune = M.trova(args.nome, cartella)
    if comune is None:
        print(f"Comune non trovato in cache: {args.nome}")
        vicini = M.simili(args.nome, cartella)
        if vicini:
            print("Forse cerchi uno di questi:")
            for nome in vicini:
                print(f"  {nome}")
        else:
            print("La fornitura OMI della sua regione non è in cache: importarla con")
            print("  python tools/valuta.py omi importa --file \"QI_xxxxx.zip\"")
        return 1

    registro = M.leggi_registro(RADICE / M.REGISTRO_PREDEFINITO)
    verifica = M.verifica_di(comune.nome, registro)

    print(f"{comune.nome} ({comune.provincia}), {comune.regione.title()}")
    print(f"  codice catastale {comune.codice_catastale}, ISTAT {comune.codice_istat}")
    print()
    print(f"Aliquote IMU {anno}, atti del Comune sul portale del Dipartimento delle finanze:")
    print(f"  {comune.link_delibere_imu}")
    print(f"  la pagina apre sul Comune giusto e chiede solo l'anno, che è un modulo e non un")
    print(f"  parametro dell'indirizzo. Un atto vale per l'anno se pubblicato entro il 28 ottobre.")
    print()

    if verifica and verifica.aliquota_imu_altri is not None:
        stato, perche = M.stato_verifica(verifica.verificato_il, anno)
        print(f"Aliquota registrata per gli altri immobili: {verifica.aliquota_imu_altri:.3%}")
        if verifica.aliquota_imu_principale is not None:
            print(f"Aliquota registrata per l'abitazione principale: {verifica.aliquota_imu_principale:.3%}")
        print(f"  verifica {stato}: {perche}")
    else:
        print("Aliquota IMU: nessun valore registrato, va letta nell'atto e poi annotata.")
    print()

    print("Imposta di soggiorno: non esiste un registro nazionale, la fonte è l'atto del Comune.")
    if verifica and verifica.link_imposta_soggiorno:
        print(f"  {verifica.link_imposta_soggiorno}")
    if verifica and verifica.imposta_soggiorno_notte is not None:
        stato, perche = M.stato_verifica(verifica.verificato_il, anno)
        print(f"  registrata a {verifica.imposta_soggiorno_notte:.2f} euro a notte per persona")
        print(f"  verifica {stato}: {perche}")
    elif not (verifica and verifica.link_imposta_soggiorno):
        print("  nessun collegamento registrato per questo Comune: si cerca sul sito del Comune")
        print("  il regolamento e la delibera delle tariffe, e si annota qui il collegamento.")
    print()

    mancanti = M.cosa_manca(verifica)
    if mancanti:
        print("Manca ancora:")
        for voce in mancanti:
            print(f"  {voce}")
        print(f"Si annotano in {M.REGISTRO_PREDEFINITO.as_posix()}, una riga per Comune, con la data di lettura.")
    else:
        print("Nulla da procurarsi: entrambe le voci risultano lette.")
    if verifica and verifica.note:
        print()
        print(f"Nota: {verifica.note}")
    print()
    print(f"Fonte dei codici: {O.ATTRIBUZIONE}. Atti IMU: {M.ATTRIBUZIONE_MEF}.")
    return 0


def cmd_omi(args) -> int:
    if args.azione == "scarica":
        try:
            valori, zone = O.scarica_dal_mirror(args.semestre)
        except ValueError as e:
            print(e)
            return 2
        print(f"Scaricati:\n  {valori}\n  {zone}")
        return 0

    if args.azione == "importa":
        if not args.file:
            print("Serve --file con l'archivio zip o il CSV scaricato dall'area riservata.")
            print(f"Percorso a video: {O.FORNITURA_UFFICIALE}")
            return 2
        try:
            # Il percorso di destinazione va ancorato alla radice del progetto:
            # il valore predefinito del modulo è relativo, e lanciando il comando
            # da un'altra cartella l'archivio finirebbe in un `data/omi` diverso da
            # quello che gli altri sottocomandi leggono, con l'effetto di
            # un'importazione riuscita e una ricerca che non trova nulla.
            estratti = O.importa_fornitura(args.file, RADICE / "data" / "omi")
        except (FileNotFoundError, ValueError) as e:
            print(f"Importazione fallita: {e}")
            return 1
        print(f"Importati {len(estratti)} file in {RADICE / 'data' / 'omi'}:")
        for f in estratti:
            print(f"  {f.name}")
        print()
        print("Ora sono interrogabili con: python tools/valuta.py omi cerca --comune \"...\"")
        return 0

    if args.azione == "zone":
        cartella = RADICE / "data" / "omi"
        quotazioni, letti = O.carica_cartella(cartella)
        if not quotazioni:
            print("Nessun file OMI in data/omi.")
            return 1
        elenco = O.elenca_zone(quotazioni, args.comune)
        if not elenco:
            print(f"Nessuna zona per {args.comune}.")
            simili = O.comuni_simili(quotazioni, args.comune)
            if simili:
                print("Forse cerchi uno di questi:")
                for nome in simili:
                    print(f"  {nome}")
            return 1
        print(f"Zone omogenee di {args.comune}")
        for codice, descrizione in elenco:
            print(f"  {codice:<8} {descrizione}")
        print()
        print(f"Fonte: {O.ATTRIBUZIONE}")
        return 0

    if args.azione == "cerca":
        cartella = RADICE / "data" / "omi"
        quotazioni, letti = O.carica_cartella(cartella)
        if not quotazioni:
            print("Nessun file OMI in data/omi. Scaricare prima un semestre, oppure")
            print(f"richiedere la fornitura aggiornata dall'area riservata: {O.FORNITURA_UFFICIALE}")
            return 1
        righe = O.cerca(quotazioni, args.comune, args.tipologia, args.zona or "")
        if not righe:
            print(f"Nessuna quotazione per {args.comune}, tipologia {args.tipologia}.")
            simili = O.comuni_simili(quotazioni, args.comune)
            if simili:
                print("Nella fornitura i nomi sono abbreviati: forse cerchi uno di questi.")
                for nome in simili:
                    print(f"  {nome}")
            return 1
        etichetta = letti[0] if len(letti) == 1 else f"{len(letti)} file del semestre in cache"
        print(f"{args.comune} - {args.tipologia} - {etichetta}")
        print(f"{'Zona':<8}{'Descrizione':<44}{'Stato':<12}{'Vendita EUR/mq':>18}{'Affitto EUR/mq mese':>22}{'Rend.':>8}")
        print("-" * 116)
        for q in righe:
            print(
                f"{q.zona:<8}{q.zona_descrizione[:43]:<44}{q.stato[:11]:<12}"
                f"{q.compravendita_min:>8,.0f} - {q.compravendita_max:<7,.0f}".replace(",", ".")
                + f"{q.locazione_min:>12,.1f} - {q.locazione_max:<7,.1f}".replace(",", ".")
                + f"{q.rendimento_lordo_implicito:>8.1%}"
            )
        sintesi = O.sintesi_comune(quotazioni, args.comune, args.tipologia)
        if sintesi:
            print()
            print(f"Media di compravendita del Comune: {sintesi['compravendita_media']:,.0f} EUR/mq".replace(",", "."))
            print(f"Rendimento lordo medio implicito:  {sintesi['rendimento_lordo_medio']:.2%}")
        print()
        print("Attenzione alla data del semestre: il mirror open data si ferma al 2018.")
        print(f"Per il dato corrente: {O.CONSULTAZIONE_A_VIDEO}")
        print(f"Fonte: {O.ATTRIBUZIONE}")
        return 0

    return 2


def _a_capo(testo: str, larghezza: int) -> list[str]:
    """Manda a capo un testo lungo su più righe, senza spezzare le parole."""
    righe, corrente = [], ""
    for parola in testo.split():
        if corrente and len(corrente) + 1 + len(parola) > larghezza:
            righe.append(corrente)
            corrente = parola
        else:
            corrente = f"{corrente} {parola}".strip()
    if corrente:
        righe.append(corrente)
    return righe


def cmd_tassi(args) -> int:
    """Tassi correnti di mercato, e confronto con il tasso di un preventivo."""
    try:
        quadro = T.quadro_corrente()
    except T.TassiNonDisponibili as e:
        print(f"Non disponibili: {e}")
        print("Il modello continua a funzionare: il tasso resta un input da preventivo.")
        return 1

    print("Tassi correnti sulle nuove erogazioni in Italia, fonte Banca centrale europea")
    print()
    print(f"  {'Serie':<40}{'Periodo':>10}{'Tasso':>10}")
    print("  " + "-" * 60)
    for o in quadro:
        print(f"  {o.descrizione:<40}{o.periodo:>10}{o.valore:>9.2f}%")

    # La catena. Sta prima del confronto col preventivo perché risponde alla
    # domanda che viene prima: di che cosa è fatto il tasso che ti offrono.
    catena = T.catena_dei_tassi(args.tasso)
    if catena:
        print()
        print("DA DOVE VIENE IL TASSO, anello per anello")
        print(f"  {'Anello':<44}{'Valore':>9}{'Periodo':>12}{'Scarto':>10}")
        print("  " + "-" * 75)
        for g in catena:
            scarto = "" if g.scarto_dal_precedente is None else f"{g.scarto_dal_precedente:+.2f} p"
            print(f"  {g.nome:<44}{g.valore:>8.3f}%{g.periodo:>12}{scarto:>10}")
        print()
        for g in catena:
            print(f"  {g.nome}")
            for riga in _a_capo(g.spiegazione, 88):
                print(f"    {riga}")
        print()
        print("  Gli anelli non sono contemporanei: l'overnight è del giorno lavorativo")
        print("  precedente, l'Euribor è mensile, la media dei mutui è mensile con uno o due")
        print("  mesi di ritardo. Gli scarti si leggono come ordini di grandezza, non come")
        print("  identità contabili. E un mutuo a tasso fisso non è indicizzato all'Euribor")
        print("  ma all'IRS di pari durata: sul fisso la catena vale come scomposizione")
        print("  concettuale, non come somma esatta.")
        print()
        print(f"  Definizione e metodo dell'overnight: {T.FONTE_ESTR}")

    if args.tasso:
        try:
            confronto = T.confronta_preventivo(args.tasso, args.mutuo, args.durata, args.serie)
        except (T.TassiNonDisponibili, ValueError) as e:
            print()
            print(f"Confronto non possibile: {e}")
            return 1
        print()
        importo = f"{args.mutuo:,.0f}".replace(",", ".")
        print(f"CONFRONTO CON IL PREVENTIVO, su {importo} EUR in {args.durata} anni")
        print(f"  Riferimento               {confronto.riferimento.descrizione}, {confronto.riferimento.periodo}")
        print(f"  Tasso di mercato          {confronto.riferimento.valore:>13.2f}%")
        print(f"  Tasso del preventivo      {args.tasso * 100:>13.2f}%")
        print(f"  Scarto                    {confronto.scarto * 100:>+13.2f} punti   ({confronto.giudizio})")
        print(f"  Rata a mercato            {euro(confronto.rata_riferimento)}")
        print(f"  Rata del preventivo       {euro(confronto.rata_offerta)}")
        print(f"  Interessi in più o meno  {euro(confronto.differenza_interessi)}   sull'intera durata")
        print()
        print("  Il dato di mercato è una media con uno o due mesi di ritardo: dice dove sta")
        print("  il mercato, non quale tasso otterrai tu, che dipende da reddito, loan to value,")
        print("  età e banca. Serve a sapere se vale la pena chiedere un altro preventivo.")

    if getattr(args, "risalita", False):
        try:
            risalite = T.risalite_storiche(args.indice)
            estremi = T.estremi_storici(args.indice)
        except (T.TassiNonDisponibili, ValueError) as e:
            print()
            print(f"Serie storica non disponibile: {e}")
            return 1

        atteso = P.RISALITE_EURIBOR
        print()
        print("RISALITE STORICHE DELL'INDICE, cioè quanto può salire un variabile")
        print(f"  Serie                     {T.SERIE_INDICI[args.indice][1]}")
        print(f"  Copertura                 {estremi['da']} / {estremi['a']}, {estremi['osservazioni']} osservazioni mensili")
        print(f"  Livello corrente          {estremi['corrente']:>13.2f}%")
        print(f"  Massimo storico           {estremi['massimo']:>13.2f}%   {estremi['periodo_massimo']}")
        print(f"  Minimo storico            {estremi['minimo']:>13.2f}%   {estremi['periodo_minimo']}")
        print()
        print(f"  {'Finestra':<12}{'Rialzo':>10}{'Da':>10}{'Livello':>10}{'A':>10}{'Livello':>10}")
        print("  " + "-" * 62)
        for ri in risalite:
            print(f"  {str(ri.mesi) + ' mesi':<12}{ri.variazione:>+9.2f}p"
                  f"{ri.periodo_iniziale:>10}{ri.valore_iniziale:>9.2f}%"
                  f"{ri.periodo_finale:>10}{ri.valore_finale:>9.2f}%")

        # Il confronto con la costante congelata in parametri.py è il punto del
        # comando: dice se il valore scritto nel workbook è ancora quello che i
        # dati contengono, oppure se la serie ha prodotto una finestra peggiore.
        congelate = {12: atteso.risalita_12_mesi, 24: atteso.risalita_24_mesi, 36: atteso.risalita_36_mesi}
        print()
        print(f"  Confronto con i valori congelati in parametri.py, verificati il {atteso.verificato_il.strftime('%d/%m/%Y')}")
        disallineate = []
        for ri in risalite:
            riferimento = congelate.get(ri.mesi)
            if riferimento is None:
                continue
            scarto = ri.variazione - riferimento
            stato = "invariato" if abs(scarto) < 0.01 else f"cambiato di {scarto:+.2f} punti"
            print(f"    {ri.mesi:>2} mesi: nel codice {riferimento:>5.2f}p, nei dati {ri.variazione:>5.2f}p   {stato}")
            if abs(scarto) >= 0.01:
                disallineate.append(ri)
        if disallineate:
            print()
            print("  I valori nel codice non coincidono più con la serie: aggiornare")
            print("  RISALITE_EURIBOR in src/immobiliare/parametri.py, spostare verificato_il")
            print("  e rigenerare il workbook, perché le note del foglio Simulatore mutuo")
            print("  citano quei numeri.")
        else:
            print()
            print("  Nessuna finestra peggiore di quelle già registrate: il workbook è allineato.")

        print()
        print("  Come si usa questo numero. Nel foglio Simulatore mutuo si compila il percorso")
        print("  del tasso a gradini con un terzo, due terzi e l'intera risalita, si legge la")
        print("  rata massima raggiunta e si decide se è sostenibile. Non è una previsione:")
        print("  è il peggio che i dati contengono, che in assenza di previsione è il solo")
        print("  riferimento onesto per una prova di sostenibilità.")

    print()
    print(f"Fonte: {T.FONTE}")
    return 0


def cmd_indicatori(args) -> int:
    """Indicatori di contesto: tasso a breve dell'area euro e inflazione italiana.

    Serve a decidere se le due assunzioni più pesanti del modello, cioè
    l'inflazione attesa e il tasso, siano ancora ragionevoli. Ogni valore esce
    con il suo periodo, perché un dato senza data non dice se lo si sta usando
    come corrente o come reperto.
    """
    print("Indicatori di contesto")
    print()

    righe = []
    try:
        e = N.estr()
        righe.append((e.descrizione, e.periodo, f"{e.valore:.3f}%", "BCE, giornaliero"))
    except N.IndicatoriNonDisponibili as errore:
        print(f"  euro short-term rate non disponibile: {errore}")

    for chiave in ("hicp_italia", "hicp_area_euro", "hicp_italia_core"):
        try:
            o = N.hicp(chiave)
            righe.append((o.descrizione, o.periodo, f"{o.valore:.1f}%", "BCE, mensile"))
        except N.IndicatoriNonDisponibili:
            pass

    try:
        for o in N.nic_istat():
            unita = "" if o.chiave == "nic_indice" else "%"
            righe.append((o.descrizione, o.periodo, f"{o.valore:.1f}{unita}", "ISTAT, mensile"))
    except N.IndicatoriNonDisponibili as errore:
        print(f"  prezzi al consumo ISTAT non disponibili: {errore}")

    if not righe:
        print("  Nessuna fonte raggiungibile. I valori restano quelli di parametri.py.")
        return 1

    larghezza = max(len(r[0]) for r in righe)
    print(f"  {'Indicatore':<{larghezza}}  {'Periodo':<12}{'Valore':>10}   Fonte")
    print("  " + "-" * (larghezza + 40))
    for descrizione, periodo, valore, fonte in righe:
        print(f"  {descrizione:<{larghezza}}  {periodo:<12}{valore:>10}   {fonte}")

    print()
    print(f"  Inflazione assunta nel modello: {P.FINANZA.inflazione_attesa:.1%}")
    print("  Si cambia in parametri.py, oppure nella cella gialla del foglio Parametri.")
    print()
    print("  Il periodo va guardato. L'euro short-term rate è del giorno lavorativo")
    print("  precedente; le serie mensili escono con qualche settimana di ritardo e")
    print("  ISTAT ribasa il NIC ogni cinque anni, quindi una serie ferma a un dicembre")
    print("  significa che il dato corrente sta in un flusso diverso, non che l'inflazione")
    print("  si sia fermata. Il comunicato di riferimento è su www.istat.it.")
    return 0


def cmd_llm(args) -> int:
    from immobiliare.llm_locale import ClienteLocale, LlmNonDisponibile

    cliente = ClienteLocale()
    print(f"Host: {cliente.host}")
    try:
        modelli = cliente.modelli()
    except LlmNonDisponibile as e:
        print(f"Non raggiungibile: {e}")
        print("L'importazione automatica degli annunci resterà indisponibile;")
        print("l'inserimento manuale e tutto il resto del progetto funzionano lo stesso.")
        return 1
    print(f"Modello predefinito: {cliente.modello}" + ("" if cliente.modello in modelli else "  (non installato)"))
    print("Modelli disponibili:")
    for m in modelli:
        print(f"  {m}")
    return 0


# ---------------------------------------------------------------------------

def principale(argomenti=None) -> int:
    parser = argparse.ArgumentParser(
        prog="immobiliare",
        description="Valutazione di un investimento immobiliare residenziale in Italia.",
    )
    sub = parser.add_subparsers(dest="comando", required=True)

    p = sub.add_parser("excel", help="genera il workbook di valutazione")
    p.add_argument("--output", help="percorso di destinazione")
    p.add_argument("--con-annunci", action="store_true", help="riversa anche l'archivio annunci")
    p.add_argument("--da-annuncio", metavar="ID", help="precompila le celle di input coi dati di un immobile a registro, per esempio house_6")
    p.set_defaults(funzione=cmd_excel)

    p = sub.add_parser("scheda", help="scheda di una pagina per la trattativa, in LaTeX")
    p.add_argument("--id", required=True, help="identificativo dell'immobile a registro, per esempio house_6")
    p.add_argument("--output", help="percorso del .tex; default output/immobili/<id>/<id>.tex")
    p.add_argument("--mutuo", type=float, default=0.0, help="importo del mutuo dal preventivo")
    p.add_argument("--tasso", type=float, default=0.032, help="TAN in forma decimale")
    p.add_argument("--durata", type=int, default=25)
    p.add_argument("--imu", type=float, help="aliquota IMU dalla delibera del Comune; default il valore base di legge, e la scheda lo dichiara")
    p.add_argument("--obiettivo", type=float, default=0.04, help="rendimento netto obiettivo, per il prezzo massimo")
    p.set_defaults(funzione=cmd_scheda)

    p = sub.add_parser("riepilogo", help="calcolo rapido a video, senza Excel")
    p.add_argument("--prezzo", type=float, required=True)
    p.add_argument("--rendita", type=float, default=0.0, help="rendita catastale")
    p.add_argument("--categoria", default="A/2")
    p.add_argument("--mq", type=float, default=0.0)
    p.add_argument("--comune", default="")
    p.add_argument("--da-impresa", action="store_true", help="acquisto da impresa con IVA")
    p.add_argument("--no-prima-casa", action="store_true")
    p.add_argument("--no-prezzo-valore", action="store_true")
    p.add_argument("--quota", type=float, default=1.0)
    p.add_argument("--reddito", type=float, default=30000.0, help="reddito imponibile IRPEF")
    p.add_argument("--mutuo", type=float, default=0.0)
    p.add_argument("--tasso", type=float, default=0.032)
    p.add_argument("--durata", type=int, default=25)
    p.add_argument("--provvigione", type=float, default=0.03)
    p.add_argument("--notaio", type=float, default=2000.0)
    p.add_argument("--altri-costi", type=float, default=2000.0)
    p.add_argument("--abitazione-principale", action="store_true")
    p.add_argument("--canone", type=float, default=0.0, help="canone mensile atteso")
    p.add_argument("--canone-concordato", type=float, default=0.0)
    p.add_argument("--regime", default="cedolare_libero")
    p.add_argument("--sfitto", type=float, default=1.0, help="mesi di sfitto attesi")
    p.add_argument("--condominio", type=float, default=1200.0)
    p.add_argument("--imu", type=float, default=P.IMU.aliquota_base)
    p.add_argument("--orizzonte", type=int, default=25)
    p.add_argument("--rivalutazione", type=float, default=0.02)
    p.set_defaults(funzione=cmd_riepilogo)

    p = sub.add_parser("annunci", help="registro degli immobili in valutazione")
    p.add_argument("azione", choices=["elenca", "confronta", "mancanti", "aggiungi", "modifica", "importa", "esporta", "rimuovi", "omi"])
    p.add_argument("--id")
    p.add_argument("--link")
    p.add_argument("--file", help="file di testo con l'annuncio copiato dal browser")
    p.add_argument("--comune")
    p.add_argument("--provincia")
    p.add_argument("--indirizzo")
    p.add_argument("--tipologia")
    p.add_argument("--destinazione", help="destinazione d'uso: abitazione, ufficio, negozio")
    p.add_argument("--fonte")
    p.add_argument("--agenzia")
    p.add_argument("--contatto")
    p.add_argument("--nuova", action="store_true", help="nuova costruzione")
    p.add_argument("--consegna", help="data prevista di consegna, o 'pronto'")
    p.add_argument("--mq", type=float)
    p.add_argument("--prezzo", type=float, help="prezzo richiesto")
    p.add_argument("--obiettivo", type=float, help="prezzo obiettivo da mettere in proposta")
    p.add_argument("--canone", type=float)
    p.add_argument("--note")
    p.add_argument("--stato", help="uno fra: " + ", ".join(A.STATI_ANNUNCIO))
    p.add_argument("--punteggio", type=int, help="priorità da 0 a 10, 10 è la massima")
    p.add_argument("--zona", dest="zona_omi", help="zona OMI, per agganciare la quotazione giusta")
    # I campi che `annunci mancanti` indica come bloccanti devono essere
    # scrivibili da qui: fino al 2 settembre 2026 il comando diceva di
    # procurarsi rendita catastale, categoria e spese condominiali, e poi non
    # c'era modo di scriverle se non aprendo il CSV a mano. Un comando che
    # chiede un dato e non lo accetta è un percorso interrotto a metà.
    p.add_argument("--rendita", type=float, help="rendita catastale in euro, dalla visura: sblocca il prezzo-valore")
    p.add_argument("--categoria", help="categoria catastale, per esempio A/2 o A/3")
    p.add_argument("--condominio", type=float, help="spese condominiali annue, dal consuntivo")
    p.add_argument("--piano")
    p.add_argument("--classe", dest="classe_energetica", help="classe energetica, una lettera fra A4 e G")
    p.add_argument("--prima-casa", dest="prima_casa", choices=["SI", "NO"], help="regime della riga; se omesso eredita dal foglio Immobile")
    p.add_argument("--impresa", dest="venditore_impresa", choices=["SI", "NO"], help="venditore impresa con IVA; se omesso eredita dal foglio Immobile")
    p.add_argument("--quotazione-min", dest="quotazione_omi_min", type=float, help="quotazione OMI minima, di norma scritta da `annunci omi`")
    p.add_argument("--quotazione-max", dest="quotazione_omi_max", type=float, help="quotazione OMI massima")
    p.add_argument("--tipologia-omi", dest="tipologia_omi", default="", help="tipologia edilizia OMI, per l'azione omi")
    p.set_defaults(funzione=cmd_annunci)

    p = sub.add_parser("comune", help="parametri comunali: dove si leggono e cosa risulta letto")
    p.add_argument("--nome", default="", help="nome del Comune, come nella fornitura OMI")
    p.add_argument("--anno", type=int, default=0, help="anno d'imposta, predefinito l'anno corrente")
    p.add_argument("--elenca", action="store_true", help="elenca i Comuni in cache con i loro codici")
    p.add_argument("--provincia", default="", help="sigla della provincia, per restringere --elenca")
    p.set_defaults(funzione=cmd_comune)

    p = sub.add_parser("omi", help="quotazioni dell'Osservatorio del mercato immobiliare")
    p.add_argument("azione", choices=["scarica", "importa", "zone", "cerca"])
    p.add_argument("--file", help="archivio zip o CSV della fornitura ufficiale, per importa")
    p.add_argument("--semestre", default="2018-2")
    p.add_argument("--comune", default="")
    p.add_argument("--zona", default="")
    p.add_argument("--tipologia", default="Abitazioni civili")
    p.set_defaults(funzione=cmd_omi)

    p = sub.add_parser("tassi", help="tassi correnti di mercato sui mutui casa")
    p.add_argument("--tasso", type=float, help="TAN del preventivo da confrontare, in forma decimale")
    p.add_argument("--mutuo", type=float, default=100000.0, help="importo su cui quantificare lo scarto")
    p.add_argument("--durata", type=int, default=25)
    p.add_argument("--serie", default="fisso_lungo", choices=sorted(T.SERIE_MUTUI), help="tipologia di riferimento")
    p.add_argument("--risalita", action="store_true", help="peggiori risalite storiche dell'indice, e confronto con i valori congelati nel codice")
    p.add_argument("--indice", default="euribor_3m", choices=sorted(T.SERIE_INDICI), help="indice su cui misurare le risalite")
    p.set_defaults(funzione=cmd_tassi)

    p = sub.add_parser("indicatori", help="tasso a breve e inflazione, per tarare le assunzioni")
    p.set_defaults(funzione=cmd_indicatori)

    p = sub.add_parser("llm", help="stato del modello linguistico locale")
    p.add_argument("azione", choices=["stato"], nargs="?", default="stato")
    p.set_defaults(funzione=cmd_llm)

    args = parser.parse_args(argomenti)
    return args.funzione(args)


if __name__ == "__main__":
    raise SystemExit(principale())
