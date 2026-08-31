# -*- coding: utf-8 -*-
"""Interfaccia a riga di comando del progetto.

Un solo eseguibile con sottocomandi, cosi' che non ci siano piu' script che si
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
import sys
from pathlib import Path

RADICE = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(RADICE / "src"))

from immobiliare import annunci as A  # noqa: E402
from immobiliare import calcoli as C  # noqa: E402
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

def cmd_excel(args) -> int:
    destinazione = Path(args.output) if args.output else WORKBOOK
    destinazione.parent.mkdir(parents=True, exist_ok=True)
    E.genera(str(destinazione))
    print(f"Workbook generato: {destinazione}")
    if args.con_annunci and ARCHIVIO.exists():
        registro = A.Registro(ARCHIVIO)
        scritti = A.esporta_in_excel(registro, str(destinazione))
        print(f"Annunci riversati nel foglio Annunci: {scritti}")
    print()
    print("Parametri fiscali della revisione", P.REVISIONE.strftime("%d/%m/%Y"))
    print("Le celle gialle sono gli input. Verificare sempre l'aliquota IMU nella")
    print("delibera del Comune e le spese nel consuntivo condominiale.")
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
        print(f"  Detrazione primo anno     {euro(detrazione)}" + ("" if args.abitazione_principale else "   (nulla: non e' abitazione principale)"))
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
            # e lo farebbe vincere sempre: un confronto cosi' non e' un confronto.
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
            # Il conto economico include gia' l'accantonamento per la ristrutturazione
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
        print("  workbook indicizza invece i costi all'inflazione e da' un valore piu' basso:")
        print("  per una decisione vale quello, questo serve solo a scremare in fretta.")

    print()
    print("Fonti dei parametri: foglio Fonti del workbook, oppure docs/fonti.md.")
    print(f"Revisione fiscale: {P.REVISIONE.strftime('%d/%m/%Y')}.")
    return 0


# ---------------------------------------------------------------------------

def cmd_annunci(args) -> int:
    registro = A.Registro(ARCHIVIO)

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
        )
        try:
            registro.aggiungi(annuncio)
        except ValueError as e:
            print(f"Non aggiunto: {e}")
            return 1
        registro.salva()
        print(f"Aggiunto {annuncio.id} in {ARCHIVIO}")
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
                print("Il prelievo automatico non e' consentito da questo sito. Le vie corrette sono")
                print("due: aprire la pagina nel browser, copiare il testo dell'annuncio in un file e")
                print("passarlo con --file, oppure inserire i dati a mano con il sottocomando aggiungi.")
                return 2
            try:
                testo = A.testo_da_html(A.scarica_pagina(args.link))
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
            # il valore predefinito del modulo e' relativo, e lanciando il comando
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
        print(f"  Interessi in piu' o meno  {euro(confronto.differenza_interessi)}   sull'intera durata")
        print()
        print("  Il dato di mercato e' una media con uno o due mesi di ritardo: dice dove sta")
        print("  il mercato, non quale tasso otterrai tu, che dipende da reddito, loan to value,")
        print("  eta' e banca. Serve a sapere se vale la pena chiedere un altro preventivo.")

    print()
    print(f"Fonte: {T.FONTE}")
    return 0


def cmd_indicatori(args) -> int:
    """Indicatori di contesto: tasso a breve dell'area euro e inflazione italiana.

    Serve a decidere se le due assunzioni piu' pesanti del modello, cioe'
    l'inflazione attesa e il tasso, siano ancora ragionevoli. Ogni valore esce
    con il suo periodo, perche' un dato senza data non dice se lo si sta usando
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
    print("  Il periodo va guardato. L'euro short-term rate e' del giorno lavorativo")
    print("  precedente; le serie mensili escono con qualche settimana di ritardo e")
    print("  ISTAT ribasa il NIC ogni cinque anni, quindi una serie ferma a un dicembre")
    print("  significa che il dato corrente sta in un flusso diverso, non che l'inflazione")
    print("  si sia fermata. Il comunicato di riferimento e' su www.istat.it.")
    return 0


def cmd_llm(args) -> int:
    from immobiliare.llm_locale import ClienteLocale, LlmNonDisponibile

    cliente = ClienteLocale()
    print(f"Host: {cliente.host}")
    try:
        modelli = cliente.modelli()
    except LlmNonDisponibile as e:
        print(f"Non raggiungibile: {e}")
        print("L'importazione automatica degli annunci restera' indisponibile;")
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
    p.set_defaults(funzione=cmd_excel)

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
    p.add_argument("azione", choices=["elenca", "aggiungi", "importa", "esporta", "rimuovi"])
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
    p.set_defaults(funzione=cmd_annunci)

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
