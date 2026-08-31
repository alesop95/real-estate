# -*- coding: utf-8 -*-
"""Generatore del workbook di valutazione, con formule vive.

Il workbook non e' un rapporto stampato: e' il modello stesso. Ogni numero
derivato e' una formula Excel, non un valore calcolato in Python e incollato, cosi'
che chi apre il file possa cambiare il prezzo o il tasso e vedere ricalcolare tutto
senza rieseguire nulla. Le celle gialle sono gli input, quelle grigie il calcolato,
quelle verdi i risultati di sintesi.

I riferimenti fra fogli passano per nomi definiti, registrati in `_nome`, cosi' che
le formule si leggano come `prezzo * reg_prima` invece che come `Immobile!$B$12`.
"""

from __future__ import annotations

from datetime import date

from openpyxl import Workbook
from openpyxl.formatting.rule import CellIsRule, ColorScaleRule
from openpyxl.utils import get_column_letter
from openpyxl.workbook.defined_name import DefinedName
from openpyxl.worksheet.datavalidation import DataValidation

from . import parametri as P
from . import stile as S

MAX_RATE = 480          # 40 anni di rate mensili
MAX_ANNI = 40
ORIZZONTE_MAX = 40


class Costruttore:
    """Costruisce il workbook e tiene il registro dei nomi definiti."""

    def __init__(self) -> None:
        self.wb = Workbook()
        self.wb.remove(self.wb.active)
        self.nomi: dict[str, str] = {}

    # -- infrastruttura ----------------------------------------------------

    def nome(self, chiave: str, ws, cella: str) -> str:
        """Registra un nome definito che punta a una cella e lo restituisce."""
        riferimento = f"'{ws.title}'!${cella[0]}${cella[1:]}" if cella[1:].isdigit() else f"'{ws.title}'!{cella}"
        self.wb.defined_names.add(DefinedName(chiave, attr_text=riferimento))
        self.nomi[chiave] = chiave
        return chiave

    def nome_intervallo(self, chiave: str, ws, intervallo: str) -> str:
        self.wb.defined_names.add(DefinedName(chiave, attr_text=f"'{ws.title}'!{intervallo}"))
        self.nomi[chiave] = chiave
        return chiave

    def salva(self, percorso: str) -> None:
        self.wb.save(percorso)

    # -- fogli -------------------------------------------------------------

    def costruisci(self) -> None:
        self.foglio_guida()
        self.foglio_parametri()
        self.foglio_immobile()
        self.foglio_mutuo()
        self.foglio_ammortamento()
        self.foglio_simulatore()
        self.foglio_locazione()
        self.foglio_cashflow()
        self.foglio_metriche()
        self.foglio_confronto()
        self.foglio_scenari()
        self.foglio_checklist()
        # Il foglio Annunci va costruito prima del confronto, che ne legge le righe
        # a partire da `self.riga_annunci`.
        self.foglio_annunci()
        self.foglio_confronto_immobili()
        self.foglio_fonti()

    # ------------------------------------------------------------------ guida
    def foglio_guida(self) -> None:
        ws = self.wb.create_sheet("Guida")
        ws.sheet_view.showGridLines = False
        S.larghezze_colonne(ws, {"A": 34, "B": 22, "C": 62, "D": 18, "E": 18, "F": 18, "G": 18, "H": 18})
        r = S.titolo(
            ws,
            1,
            "Valutazione di un investimento immobiliare",
            f"Modello aggiornato al {P.REVISIONE.strftime('%d/%m/%Y')} con i parametri fiscali {P.ANNO_IMPOSTA}. "
            "Le celle gialle sono gli input da compilare, le grigie sono calcolate, le verdi sono i risultati di sintesi.",
        )

        r = S.sezione(ws, r, "Come si usa")
        passi = [
            ("1. Immobile", "Prezzo, rendita catastale, tipo di venditore e agevolazione. Da qui escono le imposte di trasferimento e il costo totale dell'operazione."),
            ("2. Mutuo", "Importo, tasso e durata. Genera il piano di ammortamento e la detrazione degli interessi anno per anno."),
            ("3. Locazione", "Canone atteso e regime fiscale. Confronta cedolare secca, canone concordato, IRPEF ordinaria e locazione breve sullo stesso immobile."),
            ("4. Cash flow", "Proiezione annuale su un orizzonte scelto, con rivalutazione, sfitto, manutenzione e uscita finale."),
            ("5. Metriche", "Rendimento lordo e netto, cap rate, cash on cash, DSCR, TIR e valore attuale netto."),
            ("6. Confronto affitto", "Comprare con mutuo oppure restare in affitto investendo la differenza, a parita' di esborso."),
            ("7. Scenari", "Sensibilita' del cash flow al tasso e al canone, e del rendimento al prezzo."),
            ("8. Checklist", "Verifiche legali, urbanistiche, catastali e condominiali da chiudere prima della proposta e prima del rogito."),
            ("9. Annunci", "Registro degli immobili in valutazione, con link, prezzo al metro quadro e rendimento lordo calcolati."),
        ]
        for etichetta, testo in passi:
            c = ws.cell(row=r, column=1, value=etichetta)
            c.font = S.ETICHETTA_BOLD
            c.alignment = S.SINISTRA
            d = ws.cell(row=r, column=2, value=testo)
            d.font = S.ETICHETTA
            d.alignment = S.SINISTRA
            ws.merge_cells(start_row=r, start_column=2, end_row=r, end_column=8)
            ws.row_dimensions[r].height = 30
            r += 1
        r += 1

        r = S.sezione(ws, r, "Le tre domande a cui il modello risponde")
        for testo in [
            "Quanta cassa serve davvero per chiudere l'operazione, contando imposte, notaio, provvigione e oneri del mutuo, e non solo il prezzo.",
            "Quanto rende l'immobile al netto di tutto, e come si confronta con l'alternativa di non comprarlo.",
            "Quali verifiche legali e tecniche vanno chiuse prima di firmare, perche' una proposta accettata e' gia' un contratto.",
        ]:
            r = S.nota_riga(ws, r, testo)
        r += 1

        r = S.sezione(ws, r, "Avvertenza")
        for testo in [
            "Questo file e' uno strumento di analisi personale, non una consulenza fiscale, legale o finanziaria. Le aliquote sono quelle vigenti alla data di revisione indicata sopra e cambiano con ogni legge di bilancio: prima di firmare qualunque cosa vanno riverificate sulle fonti elencate nel foglio Fonti, e le posizioni soggettive vanno confermate da un notaio e da un commercialista.",
            "Il modello ignora deliberatamente la ristrutturazione come voce di progetto, secondo il perimetro con cui e' stato costruito. La ristrutturazione periodica di fine ciclo, invece, resta come costo ricorrente ammortizzato, perche' un immobile che si tiene quarant'anni va rifatto almeno una volta e ignorarlo falsa il rendimento.",
            "L'aliquota IMU e le spese condominiali sono le due voci che cambiano di piu' da un immobile all'altro: l'aliquota va letta nella delibera del Comune dell'anno in corso, le spese nel consuntivo condominiale degli ultimi due esercizi.",
        ]:
            r = S.nota_riga(ws, r, testo)

    # -------------------------------------------------------------- parametri
    def foglio_parametri(self) -> None:
        ws = self.wb.create_sheet("Parametri")
        ws.sheet_view.showGridLines = False
        S.larghezze_colonne(ws, {"A": 46, "B": 14, "C": 58, "D": 46})
        r = S.titolo(
            ws,
            1,
            "Parametri fiscali e di mercato",
            "Ogni valore e' modificabile: se cambia la legge si aggiorna qui e tutto il modello segue. "
            "La colonna delle note dice da dove viene il numero.",
            4,
        )

        def riga(chiave, etichetta, valore, formato, nota, fonte=""):
            nonlocal r
            e = ws.cell(row=r, column=1, value=etichetta)
            e.font = S.ETICHETTA
            e.alignment = S.SINISTRA
            v = ws.cell(row=r, column=2, value=valore)
            v.number_format = formato
            v.fill = S.FILL_INPUT
            v.border = S.BORDO
            v.alignment = S.DESTRA
            n = ws.cell(row=r, column=3, value=nota)
            n.font = S.NOTA
            n.alignment = S.SINISTRA
            if fonte:
                f = ws.cell(row=r, column=4, value=fonte)
                f.font = S.NOTA
                f.alignment = S.SINISTRA
            if chiave:
                self.nome(chiave, ws, f"B{r}")
            r += 1

        t = P.IMPOSTE_TRASFERIMENTO
        r = S.sezione(ws, r, "Imposte sul trasferimento, acquisto da privato o esente IVA", 4)
        riga("reg_prima", "Imposta di registro, prima casa", t.registro_prima_casa, S.PERC, "Sulla base imponibile, che con il prezzo-valore e' il valore catastale.", P.FONTI["imposte_acquisto"])
        riga("reg_ord", "Imposta di registro, aliquota ordinaria", t.registro_ordinario, S.PERC, "Seconda casa o mancanza dei requisiti prima casa.")
        riga("reg_min", "Imposta di registro, minimo di legge", t.registro_minimo, S.EURO, "Si paga comunque, anche se la percentuale darebbe meno.")
        riga("ipo_priv", "Imposta ipotecaria, da privato", t.ipotecaria_da_privato, S.EURO, "Misura fissa.")
        riga("cat_priv", "Imposta catastale, da privato", t.catastale_da_privato, S.EURO, "Misura fissa.")
        r += 1

        r = S.sezione(ws, r, "Imposte sul trasferimento, acquisto da impresa con IVA", 4)
        riga("iva_prima", "IVA, prima casa", t.iva_prima_casa, S.PERC, "Cessione entro cinque anni dall'ultimazione, o con opzione dell'impresa.")
        riga("iva_ord", "IVA, aliquota ordinaria abitativa", t.iva_ordinaria, S.PERC, "Abitazione non di lusso senza requisiti prima casa.")
        riga("iva_lusso", "IVA, categorie A/1, A/8, A/9", t.iva_lusso, S.PERC, "Immobili di pregio, ville e castelli: nessuna agevolazione.")
        riga("fisso_impresa", "Registro, ipotecaria e catastale in misura fissa", t.registro_fisso_da_impresa, S.EURO, "Duecento euro ciascuna, quindi seicento in totale.")
        r += 1

        r = S.sezione(ws, r, "Regola prezzo-valore", 4)
        riga("riv_rendita", "Rivalutazione della rendita catastale", t.rivalutazione_rendita, S.NUMERO_DEC, "Coefficiente fisso del cinque per cento.")
        riga("molt_prima", "Moltiplicatore, prima casa", t.moltiplicatore_prima_casa, S.NUMERO, "Valore catastale uguale a rendita per 1,05 per 110.")
        riga("molt_ord", "Moltiplicatore, altri fabbricati abitativi", t.moltiplicatore_ordinario, S.NUMERO, "Valore catastale uguale a rendita per 1,05 per 120.")
        r = S.nota_riga(ws, r, "Il prezzo-valore vale solo fuori campo IVA, per persone fisiche, su immobili abitativi e pertinenze, e va chiesto espressamente al notaio in atto. Porta con se' anche la riduzione del trenta per cento dell'onorario notarile e il blocco dell'accertamento di valore.", 4)
        r += 1

        m = P.MUTUO
        r = S.sezione(ws, r, "Mutuo", 4)
        riga("sost_prima", "Imposta sostitutiva, mutuo prima casa", m.imposta_sostitutiva_prima_casa, S.PERC, "Trattenuta dalla banca sull'erogato. Assorbe registro, bollo, ipotecarie e catastali sul finanziamento.")
        riga("sost_ord", "Imposta sostitutiva, altri mutui", m.imposta_sostitutiva_ordinaria, S.PERC, "Otto volte l'aliquota agevolata: pesa molto sulle seconde case.")
        riga("detr_aliq", "Detrazione IRPEF sugli interessi passivi", m.detrazione_interessi_aliquota, S.PERC, "Solo su abitazione principale, con residenza trasferita entro dodici mesi.")
        riga("detr_max", "Massimale annuo di interessi detraibili", m.detrazione_interessi_massimale, S.EURO, "Riferito all'immobile: va diviso fra i cointestatari del mutuo.")
        riga("ltv_max", "Loan to value oltre cui serve garanzia esterna", m.ltv_ordinario_max, S.PERC, "Sopra questa soglia serve il fondo Consap o una garanzia integrativa.")
        r += 1

        l = P.LOCAZIONE
        r = S.sezione(ws, r, "Tassazione dei canoni", 4)
        riga("ced_libero", "Cedolare secca, canone libero", l.cedolare_libero, S.PERC, "Contratti 4 piu' 4 e transitori a canone libero.", P.FONTI["locazioni_brevi"])
        riga("ced_conc", "Cedolare secca, canone concordato", l.cedolare_concordato, S.PERC, "Contratti 3 piu' 2 e studenti, nei Comuni ad alta tensione abitativa.")
        riga("ced_breve1", "Cedolare secca, locazione breve prima unita'", l.cedolare_breve_prima_unita, S.PERC, "Una sola unita' per periodo d'imposta, a scelta in dichiarazione.")
        riga("ced_breve2", "Cedolare secca, locazione breve dalla seconda", l.cedolare_breve_altre_unita, S.PERC, "Dal 2026 il regime copre al massimo due unita': dalla terza scatta la presunzione di impresa.")
        riga("abbatt_ord", "Abbattimento forfettario, IRPEF ordinaria", l.abbattimento_forfettario_ordinario, S.PERC, "Imponibile pari al novantacinque per cento del canone.")
        riga("abbatt_conc", "Abbattimento forfettario, canone concordato", l.abbattimento_forfettario_concordato, S.PERC, "Imponibile pari al settantacinque per cento del canone.")
        riga("reg_loc", "Imposta di registro annuale sul canone", l.registro_annuo, S.PERC, "Solo in regime ordinario: la cedolare secca la sostituisce. Meta' per parte.")
        riga("reg_loc_min", "Imposta di registro, minimo", l.registro_minimo, S.EURO, "Per la prima annualita'.")
        r += 1

        r = S.sezione(ws, r, "IRPEF e addizionali", 4)
        riga("irpef_s1", "Primo scaglione, soglia", 28000, S.EURO, "Aliquota del ventitre' per cento fino a questa soglia.", P.FONTI["irpef_2026"])
        riga("irpef_a1", "Primo scaglione, aliquota", 0.23, S.PERC, "")
        riga("irpef_s2", "Secondo scaglione, soglia", 50000, S.EURO, "Ridotta dal trentacinque al trentatre' per cento dalla legge di bilancio 2026.")
        riga("irpef_a2", "Secondo scaglione, aliquota", 0.33, S.PERC, "")
        riga("irpef_a3", "Terzo scaglione, aliquota", 0.43, S.PERC, "Oltre i cinquantamila euro.")
        riga("addizionali", "Addizionali regionale e comunale, stima", P.IRPEF.addizionale_regionale_tipica + P.IRPEF.addizionale_comunale_tipica, S.PERC, "Variano per Regione e Comune: qui una stima prudenziale complessiva.")
        r += 1

        i = P.IMU
        r = S.sezione(ws, r, "IMU", 4)
        riga("imu_molt", "Moltiplicatore catastale, gruppo A", i.moltiplicatore_gruppo_a, S.NUMERO, "Base imponibile uguale a rendita per 1,05 per 160.")
        riga("imu_base", "Aliquota base", i.aliquota_base, S.PERC, "I Comuni possono azzerarla o portarla all'1,06 per cento: leggere la delibera.", P.FONTI["imu_2026"])
        riga("imu_conc", "Quota dovuta con canone concordato", i.riduzione_canone_concordato, S.PERC, "Sconto del venticinque per cento sull'imposta.")
        r += 1

        c = P.COSTI
        r = S.sezione(ws, r, "Costi accessori e di gestione", 4)
        riga("iva_provv", "IVA sulla provvigione di agenzia", c.iva_su_provvigione, S.PERC, "La provvigione e' dovuta alla conclusione dell'affare, cioe' all'accettazione della proposta.")
        riga("ristrutt_pct", "Ristrutturazione di fine ciclo, quota del valore", c.ristrutturazione_su_valore, S.PERC, "Un rifacimento completo costa circa un terzo del valore dell'immobile.")
        riga("ristrutt_anni", "Anni fra due ristrutturazioni complete", c.anni_fra_ristrutturazioni, S.NUMERO, "Impostazione ripresa dal foglio rendita immobiliare di Paolo Coletti.", P.FONTI["coletti_rendita"])
        r += 1

        f = P.FINANZA
        r = S.sezione(ws, r, "Assunzioni finanziarie", 4)
        riga("infl", "Inflazione attesa", f.inflazione_attesa, S.PERC, "Usata per indicizzare canone e valore nominale dell'immobile.")
        riga("rend_port", "Rendimento lordo atteso del portafoglio alternativo", f.rendimento_portafoglio_lordo, S.PERC, "Assunzione, non previsione. Serve solo al confronto con il non comprare.")
        riga("tax_port", "Tassazione delle rendite finanziarie", f.tassazione_rendite_finanziarie, S.PERC, "Dodici e mezzo per cento sui titoli di Stato, ventisei sul resto.")
        riga("tasso_sconto", "Tasso di sconto reale per il valore attuale netto", f.tasso_sconto_reale, S.PERC, "Il costo opportunita' del capitale immobilizzato.")
        r += 1

        p = P.PLUSVALENZA
        r = S.sezione(ws, r, "Rivendita", 4)
        riga("plus_anni", "Anni entro cui la plusvalenza e' imponibile", p.anni_imponibilita_ordinaria, S.NUMERO, "Dieci anni se l'immobile ha avuto interventi con superbonus.")
        riga("plus_aliq", "Imposta sostitutiva sulla plusvalenza", p.imposta_sostitutiva, S.PERC, "Alternativa alla tassazione IRPEF, si chiede al notaio in atto.", P.FONTI["plusvalenza"])
        riga("costi_vendita", "Costi di vendita, quota del prezzo", 0.03, S.PERC, "Provvigione di agenzia in uscita, APE, pratiche.")

    # --------------------------------------------------------------- immobile
    def foglio_immobile(self) -> None:
        ws = self.wb.create_sheet("Immobile")
        ws.sheet_view.showGridLines = False
        S.larghezze_colonne(ws, {"A": 44, "B": 18, "C": 66, "D": 16, "E": 16, "F": 16, "G": 16, "H": 16})
        r = S.titolo(
            ws,
            1,
            "Immobile e costo dell'operazione",
            "Il costo totale, non il prezzo, e' il denominatore corretto di ogni rendimento: comprende imposte, notaio, provvigione e oneri del mutuo.",
        )

        si_no = DataValidation(type="list", formula1='"SI,NO"', allow_blank=False)
        ws.add_data_validation(si_no)
        categorie = DataValidation(type="list", formula1='"A/1,A/2,A/3,A/4,A/5,A/6,A/7,A/8,A/9,A/11"', allow_blank=True)
        ws.add_data_validation(categorie)

        r = S.sezione(ws, r, "Identificazione")
        r = S.campo(ws, r, "Riferimento interno", "house_1", input_utente=True, nota="Lo stesso identificativo usato nel foglio Annunci.")
        r = S.campo(ws, r, "Comune", "", input_utente=True, nota="Serve a ritrovare la delibera IMU e la zona OMI di riferimento.")
        r = S.campo(ws, r, "Indirizzo", "", input_utente=True)
        r = S.campo(ws, r, "Link annuncio", "", input_utente=True)
        riga_mq = r
        r = S.campo(ws, r, "Superficie commerciale", 55, S.NUMERO, input_utente=True, nota="Metri quadri commerciali, non calpestabili: e' la base del prezzo al metro quadro di mercato.")
        self.nome("mq", ws, f"B{riga_mq}")
        riga_cat = r
        r = S.campo(ws, r, "Categoria catastale", "A/3", input_utente=True, nota="A/1, A/8 e A/9 sono escluse dall'agevolazione prima casa e scontano IVA al ventidue per cento.")
        categorie.add(ws.cell(row=riga_cat, column=2))
        self.nome("categoria", ws, f"B{riga_cat}")
        riga_rendita = r
        r = S.campo(ws, r, "Rendita catastale", 450, S.EURO_DEC, input_utente=True, nota="Si legge nella visura catastale. Serve al prezzo-valore e all'IMU.")
        self.nome("rendita", ws, f"B{riga_rendita}")
        r += 1

        r = S.sezione(ws, r, "Prezzo e natura dell'operazione")
        riga_richiesto = r
        r = S.campo(ws, r, "Prezzo richiesto", 130000, S.EURO, input_utente=True)
        self.nome("prezzo_richiesto", ws, f"B{riga_richiesto}")
        riga_prezzo = r
        r = S.campo(ws, r, "Prezzo trattato, da mettere in proposta", 120000, S.EURO, input_utente=True, nota="E' il prezzo su cui si costruisce tutta l'analisi.")
        self.nome("prezzo", ws, f"B{riga_prezzo}")
        riga_impresa = r
        r = S.campo(ws, r, "Venditore impresa con IVA", "NO", input_utente=True, nota="SI se si compra da impresa costruttrice entro cinque anni dall'ultimazione, o con opzione per l'imponibilita'.")
        si_no.add(ws.cell(row=riga_impresa, column=2))
        self.nome("da_impresa", ws, f"B{riga_impresa}")
        riga_nuova = r
        r = S.campo(ws, r, "Nuova costruzione", "NO", input_utente=True, nota="Attiva le verifiche del decreto legislativo 122/2005 nella checklist: fideiussione e polizza decennale postuma.")
        si_no.add(ws.cell(row=riga_nuova, column=2))
        self.nome("nuova_costruzione", ws, f"B{riga_nuova}")
        riga_prima = r
        r = S.campo(ws, r, "Agevolazione prima casa", "SI", input_utente=True, nota="Richiede residenza nel Comune entro diciotto mesi e assenza di altra prima casa agevolata, salvo rivendita entro due anni.")
        si_no.add(ws.cell(row=riga_prima, column=2))
        self.nome("prima_casa", ws, f"B{riga_prima}")
        riga_pv = r
        r = S.campo(ws, r, "Opzione prezzo-valore", "SI", input_utente=True, nota="Da chiedere al notaio in atto. Non si applica se si compra da impresa con IVA.")
        si_no.add(ws.cell(row=riga_pv, column=2))
        self.nome("usa_prezzo_valore", ws, f"B{riga_pv}")
        riga_quota = r
        r = S.campo(ws, r, "Quota di acquisto", 1.0, S.PERC, input_utente=True, nota="Cinquanta per cento se si compra in due. Incide sul massimale della detrazione degli interessi.")
        self.nome("quota", ws, f"B{riga_quota}")
        riga_abit = r
        r = S.campo(ws, r, "Destinato ad abitazione principale", "NO", input_utente=True, nota="SI se ci si va a vivere: abilita la detrazione degli interessi e l'esenzione IMU. NO se si compra per affittarlo.")
        si_no.add(ws.cell(row=riga_abit, column=2))
        self.nome("abitazione_principale", ws, f"B{riga_abit}")
        r += 1

        r = S.sezione(ws, r, "Base imponibile e imposte di trasferimento", secondaria=True)
        # L'ordine conta: il moltiplicatore catastale dipende dall'agevolazione
        # effettivamente applicabile, non da quella richiesta, quindi le due celle di
        # controllo vanno calcolate prima del valore catastale. Usare la prima casa
        # richiesta darebbe il moltiplicatore 110 anche su una categoria di lusso, che
        # dall'agevolazione e' esclusa, e sottostimerebbe l'imposta.
        riga_lusso = r
        r = S.campo(ws, r, "Categoria di lusso", '=IF(OR(categoria="A/1",categoria="A/8",categoria="A/9"),"SI","NO")', nota="Esclude in ogni caso l'agevolazione prima casa.")
        self.nome("di_lusso", ws, f"B{riga_lusso}")
        riga_agev = r
        r = S.campo(ws, r, "Agevolazione effettivamente applicabile", '=IF(AND(prima_casa="SI",di_lusso="NO"),"SI","NO")', nota="Prima casa richiesta e categoria ammessa.")
        self.nome("agevolata", ws, f"B{riga_agev}")
        riga_vc = r
        r = S.campo(ws, r, "Valore catastale", '=rendita*riv_rendita*IF(agevolata="SI",molt_prima,molt_ord)', S.EURO, nota="Rendita per 1,05 per il moltiplicatore di categoria: 110 se agevolata, 120 altrimenti.")
        self.nome("valore_catastale", ws, f"B{riga_vc}")
        riga_base = r
        r = S.campo(
            ws, r, "Base imponibile del registro",
            '=IF(da_impresa="SI",prezzo,IF(AND(usa_prezzo_valore="SI",rendita>0),valore_catastale,prezzo))',
            S.EURO, nota="Con il prezzo-valore si tassa il valore catastale, che di norma e' molto piu' basso del prezzo.",
        )
        self.nome("base_registro", ws, f"B{riga_base}")
        r += 1

        riga_iva = r
        r = S.campo(ws, r, "IVA", '=IF(da_impresa="SI",prezzo*IF(agevolata="SI",iva_prima,IF(di_lusso="SI",iva_lusso,iva_ord)),0)', S.EURO)
        self.nome("imp_iva", ws, f"B{riga_iva}")
        riga_reg = r
        r = S.campo(ws, r, "Imposta di registro", '=IF(da_impresa="SI",fisso_impresa,MAX(base_registro*IF(agevolata="SI",reg_prima,reg_ord),reg_min))', S.EURO)
        self.nome("imp_registro", ws, f"B{riga_reg}")
        riga_ipo = r
        r = S.campo(ws, r, "Imposta ipotecaria", '=IF(da_impresa="SI",fisso_impresa,ipo_priv)', S.EURO)
        self.nome("imp_ipo", ws, f"B{riga_ipo}")
        riga_cat2 = r
        r = S.campo(ws, r, "Imposta catastale", '=IF(da_impresa="SI",fisso_impresa,cat_priv)', S.EURO)
        self.nome("imp_cat", ws, f"B{riga_cat2}")
        riga_imposte = r
        r = S.campo(ws, r, "Totale imposte di trasferimento", "=imp_iva+imp_registro+imp_ipo+imp_cat", S.EURO, risultato=True)
        self.nome("imposte_totali", ws, f"B{riga_imposte}")
        r = S.nota_riga(ws, r, "Confronto utile: se si comprasse senza agevolazione prima casa, le imposte sarebbero quelle indicate qui sotto. La differenza e' il valore economico del bonus, da pesare contro il fatto che il bonus si consuma e non si puo' riusare su un acquisto futuro finche' non si rivende.")
        riga_senza = r
        r = S.campo(
            ws, r, "Imposte senza agevolazione prima casa",
            '=IF(da_impresa="SI",prezzo*IF(di_lusso="SI",iva_lusso,iva_ord)+3*fisso_impresa,MAX(IF(AND(usa_prezzo_valore="SI",rendita>0),rendita*riv_rendita*molt_ord,prezzo)*reg_ord,reg_min)+ipo_priv+cat_priv)',
            S.EURO, nota="Scenario alternativo, per quantificare il beneficio.",
        )
        self.nome("imposte_senza_agev", ws, f"B{riga_senza}")
        riga_benef = r
        r = S.campo(ws, r, "Valore del bonus prima casa", "=imposte_senza_agev-imposte_totali", S.EURO, risultato=True)
        self.nome("valore_bonus", ws, f"B{riga_benef}")
        r += 1

        r = S.sezione(ws, r, "Costi accessori dell'operazione", secondaria=True)
        riga_provv_pct = r
        r = S.campo(ws, r, "Provvigione di agenzia", 0.03, S.PERC, input_utente=True, nota="Percentuale sul prezzo, al netto di IVA. Mettere zero se si tratta direttamente col privato.")
        self.nome("provv_pct", ws, f"B{riga_provv_pct}")
        riga_provv = r
        r = S.campo(ws, r, "Provvigione, IVA inclusa", "=prezzo*provv_pct*(1+iva_provv)", S.EURO, nota="Dovuta alla conclusione dell'affare: pattuire in proposta che nulla e' dovuto se la condizione sospensiva del mutuo non si avvera.")
        self.nome("provvigione", ws, f"B{riga_provv}")
        riga_notaio = r
        r = S.campo(ws, r, "Notaio, atto di compravendita", 2000, S.EURO, input_utente=True, nota="Con il prezzo-valore l'onorario scende del trenta per cento. Chiedere sempre due o tre preventivi scritti.")
        self.nome("notaio_cv", ws, f"B{riga_notaio}")
        riga_altri = r
        r = S.campo(ws, r, "Altri costi", 2000, S.EURO, input_utente=True, nota="Visure, relazione notarile preliminare, tecnico di parte, allacci, accatastamento, arredo minimo.")
        self.nome("altri_costi", ws, f"B{riga_altri}")
        r += 1

        r = S.sezione(ws, r, "Sintesi del fabbisogno di cassa", secondaria=True)
        riga_acc = r
        r = S.campo(ws, r, "Totale costi accessori", "=imposte_totali+provvigione+notaio_cv+altri_costi+oneri_mutuo", S.EURO, nota="Gli oneri del mutuo arrivano dal foglio Mutuo.")
        self.nome("costi_accessori", ws, f"B{riga_acc}")
        riga_tot = r
        r = S.campo(ws, r, "Costo totale dell'operazione", "=prezzo+costi_accessori", S.EURO, risultato=True)
        self.nome("costo_totale", ws, f"B{riga_tot}")
        riga_inc = r
        r = S.campo(ws, r, "Incidenza dei costi sul prezzo", "=costi_accessori/prezzo", S.PERC, nota="Sotto il sei per cento e' un'operazione leggera, sopra il dieci va capito quale voce pesa.")
        self.nome("incidenza_costi", ws, f"B{riga_inc}")
        riga_esb = r
        r = S.campo(ws, r, "Esborso iniziale, cassa necessaria", "=costo_totale-mutuo_importo", S.EURO, risultato=True, nota="E' il capitale proprio davvero immobilizzato: il denominatore del cash on cash.")
        self.nome("esborso", ws, f"B{riga_esb}")
        riga_mq_prezzo = r
        r = S.campo(ws, r, "Prezzo al metro quadro", "=IF(mq>0,prezzo/mq,0)", S.EURO, nota="Da confrontare con le quotazioni OMI della zona, foglio Fonti.")
        self.nome("prezzo_mq", ws, f"B{riga_mq_prezzo}")
        riga_sconto = r
        r = S.campo(ws, r, "Sconto ottenuto sul richiesto", "=IF(prezzo_richiesto>0,1-prezzo/prezzo_richiesto,0)", S.PERC)

        ws.conditional_formatting.add(
            f"B{riga_inc}",
            CellIsRule(operator="greaterThan", formula=["0.10"], fill=S.FILL_ATTENZIONE),
        )

    # ------------------------------------------------------------------ mutuo
    def foglio_mutuo(self) -> None:
        ws = self.wb.create_sheet("Mutuo")
        ws.sheet_view.showGridLines = False
        S.larghezze_colonne(ws, {"A": 44, "B": 18, "C": 64, "D": 12, "E": 16, "F": 16, "G": 16, "H": 16})
        r = S.titolo(
            ws,
            1,
            "Mutuo ipotecario",
            "Ammortamento alla francese a rata costante. La detrazione degli interessi spetta solo se l'immobile e' abitazione principale con residenza trasferita entro dodici mesi.",
        )

        r = S.sezione(ws, r, "Condizioni del finanziamento")
        riga_imp = r
        r = S.campo(ws, r, "Importo del mutuo", 90000, S.EURO, input_utente=True)
        self.nome("mutuo_importo", ws, f"B{riga_imp}")
        riga_ltv = r
        r = S.campo(ws, r, "Loan to value sul prezzo", "=IF(prezzo>0,mutuo_importo/prezzo,0)", S.PERC, nota="Oltre l'ottanta per cento serve il fondo Consap o una garanzia integrativa, e il tasso peggiora.")
        self.nome("ltv", ws, f"B{riga_ltv}")
        riga_alert = r
        r = S.campo(ws, r, "Serve garanzia esterna", '=IF(ltv>ltv_max,"SI, oltre la soglia","no")', nota="Il fondo di garanzia prima casa Consap copre fino all'ottanta per cento per under 36 con ISEE entro quarantamila euro, misura prorogata al 31 dicembre 2027.")
        riga_tasso = r
        r = S.campo(ws, r, "Tasso annuo nominale", 0.032, S.PERC, input_utente=True, nota="TAN del preventivo. Per il variabile mettere Euribor piu' spread e usare il foglio Scenari. Per sapere se il preventivo e' in linea col mercato: python tools/valuta.py tassi --tasso 0,032")
        self.nome("tasso", ws, f"B{riga_tasso}")
        riga_durata = r
        r = S.campo(ws, r, "Durata in anni", 25, S.NUMERO, input_utente=True)
        self.nome("durata", ws, f"B{riga_durata}")
        r += 1

        r = S.sezione(ws, r, "Oneri del mutuo", secondaria=True)
        riga_sost = r
        r = S.campo(ws, r, "Imposta sostitutiva", '=mutuo_importo*IF(agevolata="SI",sost_prima,sost_ord)', S.EURO, nota="Zero virgola venticinque per cento sulla prima casa, due per cento negli altri casi.")
        self.nome("sostitutiva", ws, f"B{riga_sost}")
        riga_istr = r
        r = S.campo(ws, r, "Spese di istruttoria", 500, S.EURO, input_utente=True, nota="Spesso azzerate nelle offerte commerciali: verificare sul foglio informativo.")
        self.nome("istruttoria", ws, f"B{riga_istr}")
        riga_per = r
        r = S.campo(ws, r, "Perizia", 300, S.EURO, input_utente=True)
        self.nome("perizia", ws, f"B{riga_per}")
        riga_not = r
        r = S.campo(ws, r, "Notaio, atto di mutuo", 1000, S.EURO, input_utente=True, nota="Fattura distinta da quella della compravendita, e detraibile fra gli oneri accessori se prima casa.")
        self.nome("notaio_mutuo", ws, f"B{riga_not}")
        riga_pol_modo = r
        r = S.campo(ws, r, "Polizza incendio, forma del premio", "annuo", input_utente=True, nota="annuo per il premio ricorrente, unico per il premio anticipato in un'unica soluzione, che le banche propongono spesso finanziandolo dentro il mutuo.")
        modo_pol = DataValidation(type="list", formula1='"annuo,unico"', allow_blank=False)
        ws.add_data_validation(modo_pol)
        modo_pol.add(ws.cell(row=riga_pol_modo, column=2))
        self.nome("polizza_forma", ws, f"B{riga_pol_modo}")
        riga_pol_imp = r
        r = S.campo(ws, r, "Polizza incendio e scoppio, importo", 180, S.EURO, input_utente=True, nota="Se la forma e' annua e' il premio di ogni anno; se e' unica e' il totale per l'intera durata, che sul mercato si osserva attorno a cinque euro ogni mille di capitale.")
        self.nome("polizza_importo", ws, f"B{riga_pol_imp}")
        riga_pol = r
        r = S.campo(ws, r, "Polizza, costo annuo equivalente", '=IF(polizza_forma="unico",IF(durata>0,polizza_importo/durata,0),polizza_importo)', S.EURO_DEC, nota="Il premio unico si ripartisce sulla durata per poterlo confrontare con quello annuo.")
        self.nome("polizza", ws, f"B{riga_pol}")
        r = S.nota_riga(ws, r, "La polizza incendio e scoppio e' obbligatoria per legge ma non e' obbligatorio comprarla dalla banca: il cliente puo' presentarne una reperita altrove, purche' di protezione equivalente, e la banca deve accettarla. Se invece si accetta quella proposta, il cliente ha diritto di sapere quanta provvigione la compagnia paga alla banca. Le polizze vita o sulla perdita dell'impiego non sono mai obbligatorie e la concessione del credito non puo' esservi subordinata.")
        riga_pol_vita = r
        r = S.campo(ws, r, "Polizza vita o impiego, premio annuo", 0, S.EURO, input_utente=True, nota="Facoltativa per legge: la banca non puo' subordinare la concessione del credito alla sua sottoscrizione.")
        self.nome("polizza_facoltativa", ws, f"B{riga_pol_vita}")
        riga_oneri = r
        r = S.campo(ws, r, "Oneri iniziali del mutuo", '=IF(mutuo_importo>0,sostitutiva+istruttoria+perizia+notaio_mutuo+IF(polizza_forma="unico",polizza_importo,0),0)', S.EURO, risultato=True, nota="Comprende il premio unico della polizza, se scelto: e' cassa che esce al rogito e va nel costo dell'operazione.")
        self.nome("oneri_mutuo", ws, f"B{riga_oneri}")
        r += 1

        r = S.sezione(ws, r, "Rata e costo del debito", secondaria=True)
        riga_rata = r
        r = S.campo(ws, r, "Rata mensile", "=IF(mutuo_importo>0,PMT(tasso/12,durata*12,-mutuo_importo),0)", S.EURO_DEC, risultato=True)
        self.nome("rata_mensile", ws, f"B{riga_rata}")
        riga_rata_a = r
        r = S.campo(ws, r, "Rata annua", "=rata_mensile*12", S.EURO)
        self.nome("rata_annua", ws, f"B{riga_rata_a}")
        riga_tot_int = r
        r = S.campo(ws, r, "Interessi totali sull'intera durata", "=rata_mensile*durata*12-mutuo_importo", S.EURO, risultato=True, nota="E' il vero prezzo del debito: confrontarlo con il valore del bonus prima casa mette le cose in prospettiva.")
        self.nome("interessi_totali", ws, f"B{riga_tot_int}")
        riga_costo_deb = r
        r = S.campo(ws, r, "Costo totale del debito", "=interessi_totali+oneri_mutuo+polizza*durata+polizza_facoltativa*durata", S.EURO)
        riga_taeg = r
        r = S.campo(
            ws, r, "Tasso effettivo stimato",
            "=IF(mutuo_importo>0,RATE(durata*12,-(rata_mensile+(polizza+polizza_facoltativa)/12),mutuo_importo-oneri_mutuo)*12,0)",
            S.PERC, nota="Stima interna, non il TAEG di legge: include oneri iniziali e premi assicurativi ripartiti sulle rate.",
        )
        riga_reddito = r
        r = S.campo(ws, r, "Reddito netto mensile del richiedente", 1800, S.EURO, input_utente=True)
        self.nome("reddito_mensile", ws, f"B{riga_reddito}")
        riga_rr = r
        r = S.campo(ws, r, "Rapporto rata reddito", "=IF(reddito_mensile>0,rata_mensile/reddito_mensile,0)", S.PERC, nota="Le banche si fermano di norma a un terzo del reddito netto: sopra il trentacinque per cento la pratica difficilmente passa.")
        ws.conditional_formatting.add(
            f"B{riga_rr}", CellIsRule(operator="greaterThan", formula=["0.35"], fill=S.FILL_ATTENZIONE)
        )
        r += 1

        r = S.sezione(ws, r, "Interessi e detrazione, anno per anno", secondaria=True)
        r = S.nota_riga(ws, r, "La detrazione vale il diciannove per cento degli interessi entro un massimale di quattromila euro riferito all'immobile, quindi da dividere per la quota se il mutuo e' cointestato. Spetta solo sull'abitazione principale: sull'immobile comprato per affittare non spetta, e la colonna resta a zero.")
        intestazione = r
        r = S.intestazioni(ws, r, ["Anno", "Interessi", "Capitale rimborsato", "Debito residuo", "Detrazione IRPEF", "Rata annua", "Beneficio netto"], [10, 16, 18, 16, 18, 16, 16])
        prima_riga_tab = r
        for anno in range(1, MAX_ANNI + 1):
            ws.cell(row=r, column=1, value=anno).number_format = S.NUMERO
            ws.cell(row=r, column=2, value=f'=IF({anno}<=durata,SUMIFS(Ammortamento!$D:$D,Ammortamento!$H:$H,$A{r}),0)').number_format = S.EURO
            ws.cell(row=r, column=3, value=f'=IF({anno}<=durata,SUMIFS(Ammortamento!$E:$E,Ammortamento!$H:$H,$A{r}),0)').number_format = S.EURO
            ws.cell(row=r, column=4, value=f'=IF({anno}<=durata,MAX(0,mutuo_importo-SUM($C${prima_riga_tab}:$C{r})),0)').number_format = S.EURO
            ws.cell(row=r, column=5, value=f'=IF(abitazione_principale="SI",MIN($B{r},detr_max*quota)*detr_aliq,0)').number_format = S.EURO
            ws.cell(row=r, column=6, value=f'=IF({anno}<=durata,rata_annua,0)').number_format = S.EURO
            ws.cell(row=r, column=7, value=f"=$F{r}-$E{r}").number_format = S.EURO
            for col in range(1, 8):
                ws.cell(row=r, column=col).border = S.BORDO
                if col > 1:
                    ws.cell(row=r, column=col).fill = S.FILL_CALCOLO
            r += 1
        ultima_riga_tab = r - 1
        self.nome_intervallo("interessi_anno", ws, f"$B${prima_riga_tab}:$B${ultima_riga_tab}")
        self.nome_intervallo("detrazione_anno", ws, f"$E${prima_riga_tab}:$E${ultima_riga_tab}")
        self.nome_intervallo("rata_anno", ws, f"$F${prima_riga_tab}:$F${ultima_riga_tab}")
        self.nome_intervallo("debito_residuo_anno", ws, f"$D${prima_riga_tab}:$D${ultima_riga_tab}")
        ws.freeze_panes = ws.cell(row=prima_riga_tab, column=1)
        r += 1
        c = ws.cell(row=r, column=1, value="Totale detrazione sull'intera durata")
        c.font = S.ETICHETTA_BOLD
        v = ws.cell(row=r, column=5, value=f"=SUM($E${prima_riga_tab}:$E${ultima_riga_tab})")
        v.number_format = S.EURO
        v.fill = S.FILL_RISULTATO
        v.font = S.ETICHETTA_BOLD

    # ----------------------------------------------------------- ammortamento
    def foglio_ammortamento(self) -> None:
        ws = self.wb.create_sheet("Ammortamento")
        ws.sheet_view.showGridLines = False
        r = S.titolo(ws, 1, "Piano di ammortamento", "Una riga per rata. Le righe oltre la durata restano vuote.", 8)
        r = S.intestazioni(
            ws, r,
            ["N. rata", "Data", "Debito iniziale", "Quota interessi", "Quota capitale", "Rata", "Debito residuo", "Anno"],
            [10, 14, 18, 18, 18, 16, 18, 10],
        )
        prima = r
        for k in range(1, MAX_RATE + 1):
            ws.cell(row=r, column=1, value=k).number_format = S.NUMERO
            ws.cell(row=r, column=2, value=f'=IF($A{r}<=durata*12,EDATE(data_erogazione,$A{r}),"")').number_format = S.DATA
            if k == 1:
                ws.cell(row=r, column=3, value='=IF($A{0}<=durata*12,mutuo_importo,"")'.format(r)).number_format = S.EURO_DEC
            else:
                ws.cell(row=r, column=3, value=f'=IF($A{r}<=durata*12,$G{r-1},"")').number_format = S.EURO_DEC
            ws.cell(row=r, column=4, value=f'=IF($A{r}<=durata*12,$C{r}*tasso/12,"")').number_format = S.EURO_DEC
            ws.cell(row=r, column=5, value=f'=IF($A{r}<=durata*12,$F{r}-$D{r},"")').number_format = S.EURO_DEC
            ws.cell(row=r, column=6, value=f'=IF($A{r}<=durata*12,rata_mensile,"")').number_format = S.EURO_DEC
            ws.cell(row=r, column=7, value=f'=IF($A{r}<=durata*12,MAX(0,$C{r}-$E{r}),"")').number_format = S.EURO_DEC
            ws.cell(row=r, column=8, value=f'=IF($A{r}<=durata*12,INT(($A{r}-1)/12)+1,"")').number_format = S.NUMERO
            for col in range(1, 9):
                ws.cell(row=r, column=col).border = S.BORDO
            r += 1
        ws.freeze_panes = ws.cell(row=prima, column=1)

    # ------------------------------------------------------ simulatore mutuo
    def foglio_simulatore(self) -> None:
        """Simulatore del mutuo con rimborsi volontari e percorso del tasso.

        Il foglio Ammortamento risponde alla domanda semplice, cioe' come si spegne
        il debito se non succede nulla. Questo risponde alle due domande che si
        fanno davvero durante la vita di un mutuo: che cosa succede se verso denaro
        in anticipo, e che cosa succede se il tasso si muove.

        L'impianto riprende il foglio "calcolatore mutuo" di Paolo Coletti, che
        ricalcola la rata mese per mese sul debito residuo effettivo: e' l'unico
        modo di rappresentare correttamente un rimborso volontario, perche' dopo un
        versamento straordinario o la rata scende, a parita' di durata, o la durata
        si accorcia, a parita' di rata, e sono due scelte diverse che si dichiarano
        alla banca.

        Sulla conversione del tasso annuo in mensile convivono due convenzioni. Le
        banche italiane dividono per dodici, ed e' quella usata dal resto del
        workbook; la conversione finanziariamente esatta e' il tasso equivalente
        composto. La differenza e' piccola ma non nulla, e qui si sceglie con una
        cella invece di nasconderla.
        """
        ws = self.wb.create_sheet("Simulatore mutuo")
        ws.sheet_view.showGridLines = False
        S.larghezze_colonne(ws, {"A": 44, "B": 18, "C": 62})
        r = S.titolo(
            ws,
            1,
            "Simulatore: rimborsi volontari e percorso del tasso",
            "Indipendente dal foglio Mutuo, cosi' si puo' provare uno scenario senza toccare l'analisi principale. I valori di partenza sono ripresi da li'.",
        )

        r = S.sezione(ws, r, "Condizioni di partenza")
        riga = r
        r = S.campo(ws, r, "Capitale erogato", "=mutuo_importo", S.EURO, input_utente=True, nota="Ripreso dal foglio Mutuo: si puo' sovrascrivere con un altro importo.")
        self.nome("sim_capitale", ws, f"B{riga}")
        riga = r
        r = S.campo(ws, r, "Durata in mesi", "=durata*12", S.NUMERO, input_utente=True)
        self.nome("sim_mesi", ws, f"B{riga}")
        riga = r
        r = S.campo(ws, r, "Tasso annuo di partenza", "=tasso", S.PERC, input_utente=True)
        self.nome("sim_tasso", ws, f"B{riga}")
        riga = r
        r = S.campo(ws, r, "Conversione del tasso mensile", "banca", input_utente=True, nota="banca per la divisione per dodici, che e' la convenzione dei contratti italiani; composta per il tasso equivalente finanziariamente esatto.")
        conv = DataValidation(type="list", formula1='"banca,composta"', allow_blank=False)
        ws.add_data_validation(conv)
        conv.add(ws.cell(row=riga, column=2))
        self.nome("sim_convenzione", ws, f"B{riga}")
        r += 1

        r = S.sezione(ws, r, "Percorso del tasso, per il variabile", secondaria=True)
        riga = r
        r = S.campo(ws, r, "Variazione del tasso", 0.0, S.PERC, input_utente=True, nota="Punti percentuali aggiunti o tolti al tasso di partenza. Un punto in piu' su un variabile e' uno scenario ordinario, non estremo.")
        self.nome("sim_shock", ws, f"B{riga}")
        riga = r
        r = S.campo(ws, r, "Mese in cui la variazione entra in vigore", 25, S.NUMERO, input_utente=True, nota="Prima di questo mese vale il tasso di partenza.")
        self.nome("sim_shock_mese", ws, f"B{riga}")
        r = S.nota_riga(ws, r, "Per un tasso fisso si lascia la variazione a zero. Per un variabile si prova a spostarla, e la riga della rata massima dice se lo scenario resta sostenibile: e' la sola domanda che conta davvero prima di firmare un variabile.")
        r = S.nota_riga(ws, r, "Una precisazione che cambia il risultato. Il mutuo a tasso variabile italiano tiene ferma la scadenza e sposta l'aumento sulla rata, quindi per simulare un rialzo dei tassi va scelto sotto l'effetto \"riduci rata\". Con \"riduci durata\" la rata resta quella di partenza e a crescere e' il numero di mesi: e' il funzionamento del mutuo a rata costante e durata variabile, che esiste ma e' meno diffuso, e in caso di forte rialzo puo' allungare il piano oltre la scadenza contrattuale.")
        r += 1

        r = S.sezione(ws, r, "Rimborsi volontari", secondaria=True)
        riga = r
        r = S.campo(ws, r, "Versamento mensile aggiuntivo", 0.0, S.EURO, input_utente=True, nota="Somma che si aggiunge a ogni rata, oltre a quella dovuta.")
        self.nome("sim_extra_mese", ws, f"B{riga}")
        riga = r
        r = S.campo(ws, r, "Versamento una tantum", 0.0, S.EURO, input_utente=True, nota="Una somma sola, per esempio una liquidazione o un premio.")
        self.nome("sim_extra_unico", ws, f"B{riga}")
        riga = r
        r = S.campo(ws, r, "Mese del versamento una tantum", 37, S.NUMERO, input_utente=True)
        self.nome("sim_extra_mese_unico", ws, f"B{riga}")
        riga = r
        r = S.campo(ws, r, "Effetto del rimborso", "riduci durata", input_utente=True, nota="riduci durata tiene ferma la rata e accorcia il piano; riduci rata tiene ferma la scadenza e abbassa la rata. Va dichiarato alla banca: non lo sceglie il foglio.")
        eff = DataValidation(type="list", formula1='"riduci durata,riduci rata"', allow_blank=False)
        ws.add_data_validation(eff)
        eff.add(ws.cell(row=riga, column=2))
        self.nome("sim_effetto", ws, f"B{riga}")
        r = S.nota_riga(ws, r, "Sul se convenga rimborsare in anticipo la regola e' una sola, e non e' quella che si sente ripetere. Non conta che all'inizio si paghino soprattutto interessi: il denaro e' fungibile e ogni mese la scelta e' la stessa, cioe' estinguere adesso oppure pagare gli interessi per rimandare la decisione. Conviene rimborsare se non si trova un impiego che renda, al netto delle imposte, almeno quanto il tasso del mutuo. Restano due argomenti non finanziari: non avere debiti fa dormire meglio, e un mutuo estinto oggi non si riottiene domani.")
        r += 1

        r = S.sezione(ws, r, "Esito della simulazione", secondaria=True)
        riga_rata0 = r
        r = S.campo(ws, r, "Rata iniziale", "=IF(sim_capitale>0,PMT(sim_tasso_mensile,sim_mesi,-sim_capitale),0)", S.EURO_DEC, risultato=True)
        self.nome("sim_rata_iniziale", ws, f"B{riga_rata0}")
        riga = r
        r = S.campo(ws, r, "Tasso mensile applicato", '=IF(sim_convenzione="composta",(1+sim_tasso)^(1/12)-1,sim_tasso/12)', "0.0000%")
        self.nome("sim_tasso_mensile", ws, f"B{riga}")
        riga_int = r
        r = S.campo(ws, r, "Interessi totali pagati", "=SUM(sim_interessi)", S.EURO, risultato=True)
        riga_base = r
        r = S.campo(ws, r, "Interessi senza rimborsi volontari", "=sim_rata_iniziale*sim_mesi-sim_capitale", S.EURO, nota="Il piano di partenza, a tasso invariato e senza versamenti aggiuntivi.")
        riga_risp = r
        r = S.campo(ws, r, "Interessi risparmiati", f"=B{riga_base}-B{riga_int}", S.EURO, risultato=True, nota="Positivo se i rimborsi volontari, o un tasso in discesa, hanno ridotto il costo del debito.")
        riga_dur = r
        r = S.campo(ws, r, "Durata effettiva in mesi", "=COUNTIF(sim_pagato,\">0\")", S.NUMERO, risultato=True, nota="Piu' bassa della durata contrattuale se i rimborsi hanno accorciato il piano.")
        r = S.campo(ws, r, "Anni risparmiati", f"=(sim_mesi-B{riga_dur})/12", S.NUMERO_DEC)
        r = S.campo(ws, r, "Rata massima raggiunta", "=MAX(sim_rate)", S.EURO_DEC, risultato=True, nota="Solo la rata dovuta, senza i versamenti volontari. Su un tasso variabile e' il numero che dice se lo scenario e' sostenibile, e va confrontato con il reddito.")
        r = S.campo(ws, r, "Massimo esborso in un mese", "=MAX(sim_pagato)", S.EURO_DEC, nota="Comprende anche l'eventuale versamento una tantum.")
        r = S.campo(ws, r, "Totale versato", "=SUM(sim_pagato)", S.EURO)
        r = S.campo(ws, r, "Costo effettivo annuo", "=IFERROR(IRR(sim_flussi)*12,\"non calcolabile\")", S.PERC, nota="Tasso interno dei flussi del solo mutuo: coincide col nominale se non ci sono rimborsi ne' variazioni di tasso.")
        r += 1

        intest = ["Mese", "Data", "Tasso annuo", "Tasso mensile", "Debito iniziale",
                  "Interessi maturati", "Rata dovuta", "Versamento extra", "Totale pagato",
                  "Quota interessi", "Quota capitale", "Debito residuo", "Flusso"]
        r = S.intestazioni(ws, r, intest, [8, 13, 13, 13, 16, 16, 14, 14, 14, 14, 14, 16, 14])
        prima = r

        # Riga zero: erogazione. Serve al tasso interno, che altrimenti non avrebbe
        # l'incasso iniziale contro cui misurare i pagamenti.
        ws.cell(row=r, column=1, value=0).number_format = S.NUMERO
        ws.cell(row=r, column=2, value="=data_erogazione").number_format = S.DATA
        ws.cell(row=r, column=12, value="=sim_capitale").number_format = S.EURO
        ws.cell(row=r, column=13, value="=sim_capitale").number_format = S.EURO
        for col in (6, 9, 10, 11):
            ws.cell(row=r, column=col, value=0).number_format = S.EURO
        for col in range(1, 14):
            ws.cell(row=r, column=col).border = S.BORDO
            ws.cell(row=r, column=col).fill = S.FILL_CALCOLO
        r += 1

        for mese in range(1, MAX_RATE + 1):
            p = r - 1                       # riga precedente
            attivo = f"$L{p}>0.005"         # finche' resta debito, oltre l'arrotondamento
            ws.cell(row=r, column=1, value=mese).number_format = S.NUMERO
            ws.cell(row=r, column=2, value=f"=EDATE(data_erogazione,$A{r})").number_format = S.DATA
            ws.cell(row=r, column=3, value=f"=sim_tasso+IF($A{r}>=sim_shock_mese,sim_shock,0)").number_format = S.PERC
            ws.cell(row=r, column=4, value=f'=IF(sim_convenzione="composta",(1+$C{r})^(1/12)-1,$C{r}/12)').number_format = "0.0000%"
            ws.cell(row=r, column=5, value=f"=IF({attivo},$L{p},0)").number_format = S.EURO_DEC
            ws.cell(row=r, column=6, value=f"=$E{r}*$D{r}").number_format = S.EURO_DEC
            # La rata dovuta: costante nella modalita' che accorcia il piano, ricalcolata
            # sui mesi che restano in quella che abbassa la rata. In entrambi i casi non
            # puo' superare quanto serve a chiudere il debito.
            ws.cell(
                row=r, column=7,
                value=(
                    f'=IF(NOT({attivo}),0,MIN($E{r}+$F{r},'
                    f'IF(sim_effetto="riduci rata",'
                    f'PMT($D{r},MAX(sim_mesi-$A{r}+1,1),-$E{r}),sim_rata_iniziale)))'
                ),
            ).number_format = S.EURO_DEC
            ws.cell(
                row=r, column=8,
                value=(
                    f"=IF(NOT({attivo}),0,MIN($E{r}+$F{r}-$G{r},"
                    f"sim_extra_mese+IF($A{r}=sim_extra_mese_unico,sim_extra_unico,0)))"
                ),
            ).number_format = S.EURO_DEC
            ws.cell(row=r, column=9, value=f"=$G{r}+$H{r}").number_format = S.EURO_DEC
            ws.cell(row=r, column=10, value=f"=MIN($I{r},$F{r})").number_format = S.EURO_DEC
            ws.cell(row=r, column=11, value=f"=$I{r}-$J{r}").number_format = S.EURO_DEC
            ws.cell(row=r, column=12, value=f"=MAX(0,$E{r}+$F{r}-$I{r})").number_format = S.EURO_DEC
            ws.cell(row=r, column=13, value=f"=-$I{r}").number_format = S.EURO_DEC
            for col in range(1, 14):
                ws.cell(row=r, column=col).border = S.BORDO
                ws.cell(row=r, column=col).fill = S.FILL_CALCOLO
            r += 1

        ultima = r - 1
        self.nome_intervallo("sim_interessi", ws, f"$J${prima+1}:$J${ultima}")
        self.nome_intervallo("sim_pagato", ws, f"$I${prima+1}:$I${ultima}")
        self.nome_intervallo("sim_rate", ws, f"$G${prima+1}:$G${ultima}")
        self.nome_intervallo("sim_flussi", ws, f"$M${prima}:$M${ultima}")
        ws.freeze_panes = ws.cell(row=prima, column=3)

    # -------------------------------------------------------------- locazione
    def foglio_locazione(self) -> None:
        ws = self.wb.create_sheet("Locazione")
        ws.sheet_view.showGridLines = False
        S.larghezze_colonne(ws, {"A": 44, "B": 18, "C": 60, "D": 18, "E": 18, "F": 18, "G": 18, "H": 18})
        r = S.titolo(
            ws,
            1,
            "Messa a reddito",
            "Quattro regimi a confronto sullo stesso immobile. Il canone effettivo non e' quello di contratto: sfitto e morosita' vanno tolti prima, non dopo.",
        )

        r = S.sezione(ws, r, "Ipotesi di ricavo")
        riga_canone = r
        r = S.campo(ws, r, "Canone mensile atteso, canone libero", 500, S.EURO, input_utente=True, nota="Da verificare sulle quotazioni OMI di locazione della zona e sugli annunci reali comparabili.")
        self.nome("canone_mese", ws, f"B{riga_canone}")
        riga_canone_conc = r
        r = S.campo(ws, r, "Canone mensile a canone concordato", 420, S.EURO, input_utente=True, nota="Deriva dall'accordo territoriale del Comune, con attestazione di un'associazione firmataria. Di norma inferiore del dieci-venti per cento al libero.")
        self.nome("canone_conc_mese", ws, f"B{riga_canone_conc}")
        riga_brevi = r
        r = S.campo(ws, r, "Ricavi lordi annui da locazione breve", 9000, S.EURO, input_utente=True, nota="Tariffa media per notte moltiplicata per le notti occupate attese. Va stimata sui dati reali della zona, non sul picco di agosto.")
        self.nome("ricavi_brevi", ws, f"B{riga_brevi}")
        riga_sfitto = r
        r = S.campo(ws, r, "Mesi di sfitto attesi all'anno", 1, S.NUMERO_DEC, input_utente=True, nota="Un mese l'anno e' l'assunzione prudenziale standard. Fra un contratto e l'altro il vuoto e' di norma piu' lungo.")
        self.nome("mesi_sfitto", ws, f"B{riga_sfitto}")
        riga_moros = r
        r = S.campo(ws, r, "Accantonamento per morosita'", 0.03, S.PERC, input_utente=True, nota="Uno sfratto per morosita' richiede un anno e mezzo e nel frattempo il canone non entra ma le imposte si pagano lo stesso.")
        self.nome("morosita_pct", ws, f"B{riga_moros}")
        r += 1

        r = S.sezione(ws, r, "Costi ricorrenti a carico del proprietario", secondaria=True)
        riga_cond = r
        r = S.campo(ws, r, "Spese condominiali annue totali", 1200, S.EURO, input_utente=True, nota="Dal consuntivo condominiale, non dalla stima dell'agenzia. Chiedere anche il verbale dell'ultima assemblea per i lavori deliberati.")
        self.nome("condominio", ws, f"B{riga_cond}")
        riga_quota_cond = r
        r = S.campo(ws, r, "Quota a carico del proprietario", 0.4, S.PERC, input_utente=True, nota="La ripartizione fra proprietario e inquilino segue la tabella degli oneri accessori: straordinaria al proprietario, ordinaria all'inquilino.")
        self.nome("quota_condominio", ws, f"B{riga_quota_cond}")
        riga_manut = r
        r = S.campo(ws, r, "Manutenzione ordinaria, quota del valore", 0.01, S.PERC, input_utente=True, nota="Un per cento del valore l'anno e' la regola empirica: caldaia, infissi, elettrodomestici, tinteggiature fra un inquilino e l'altro.")
        self.nome("manut_pct", ws, f"B{riga_manut}")
        riga_ass = r
        r = S.campo(ws, r, "Assicurazione fabbricato", 200, S.EURO, input_utente=True)
        self.nome("assicurazione", ws, f"B{riga_ass}")
        riga_imu_a = r
        r = S.campo(ws, r, "Aliquota IMU deliberata dal Comune", P.IMU.aliquota_base, S.PERC, input_utente=True, nota="Da leggere nella delibera comunale dell'anno, non dal valore base di legge.")
        self.nome("imu_aliquota", ws, f"B{riga_imu_a}")
        riga_gest = r
        r = S.campo(ws, r, "Gestione affidata a terzi, quota del canone", 0.0, S.PERC, input_utente=True, nota="Un property manager costa il dieci per cento sul lungo periodo, il venti sul breve.")
        self.nome("gestione_pct", ws, f"B{riga_gest}")
        riga_costi_brevi = r
        r = S.campo(ws, r, "Costi variabili della locazione breve", 0.15, S.PERC, input_utente=True, nota="Pulizie, biancheria, utenze, commissioni dei portali, consumabili. Sono sui ricavi, non sull'utile.")
        self.nome("costi_brevi_pct", ws, f"B{riga_costi_brevi}")
        riga_marg = r
        r = S.campo(ws, r, "Aliquota marginale IRPEF del contribuente", 0.33, S.PERC, input_utente=True, nota="Lo scaglione in cui cade l'ultimo euro di reddito: 23 per cento fino a ventottomila euro, 33 fino a cinquantamila, 43 oltre. Serve solo al confronto con il regime ordinario.")
        self.nome("irpef_marginale", ws, f"B{riga_marg}")
        r += 1

        r = S.sezione(ws, r, "Costo figurativo del proprio tempo", secondaria=True)
        r = S.nota_riga(ws, r, "Gestire un immobile locato costa tempo: registrare e rinnovare i contratti, seguire le assemblee, cercare l'artigiano il 23 dicembre, selezionare gli inquilini, rincorrere un pagamento in ritardo. E' un costo reale che quasi nessuna analisi mette a bilancio, e non metterlo significa confrontare il rendimento di un immobile con quello di un investimento finanziario che di tempo non ne chiede. Va dato un valore alle proprie ore e va calcolato.")
        riga_ore = r
        r = S.campo(ws, r, "Ore all'anno dedicate alla gestione", 30, S.NUMERO, input_utente=True, nota="Trenta ore l'anno e' l'ordine di grandezza di una locazione lunga che va liscia. Una locazione breve gestita in proprio sta su un altro ordine di grandezza, dalle duecento ore in su.")
        self.nome("ore_gestione", ws, f"B{riga_ore}")
        riga_valore_ora = r
        r = S.campo(ws, r, "Valore di un'ora del proprio tempo", 0, S.EURO, input_utente=True, nota="Zero per escludere questa voce dal conto. Un riferimento onesto e' il proprio costo orario netto, oppure quanto si pagherebbe qualcuno per farlo al posto proprio.")
        self.nome("valore_ora", ws, f"B{riga_valore_ora}")
        riga_costo_tempo = r
        r = S.campo(ws, r, "Costo figurativo annuo", "=ore_gestione*valore_ora", S.EURO, nota="Entra nel conto economico come una qualsiasi altra voce di costo. Se resta a zero il modello si comporta come prima.")
        self.nome("costo_tempo", ws, f"B{riga_costo_tempo}")
        riga_coef = r
        r = S.campo(ws, r, "Moltiplicatore del tempo per la locazione breve", 6, S.NUMERO_DEC, input_utente=True, nota="Quante volte il tempo della locazione lunga. La locazione breve non e' un investimento passivo: e' piu' vicina a un mestiere, e va confrontata con gli altri regimi tenendone conto.")
        self.nome("coefficiente_tempo_breve", ws, f"B{riga_coef}")
        r += 1

        r = S.sezione(ws, r, "Confronto fra regimi", secondaria=True)
        r = S.intestazioni(
            ws, r,
            ["Voce", "Cedolare libero", "Cedolare concordato", "IRPEF ordinaria", "Locazione breve"],
            [42, 20, 20, 20, 20],
        )
        base = r

        def riga_conf(etichetta, f_lib, f_conc, f_irp, f_brev, formato=S.EURO, risultato=False):
            nonlocal r
            e = ws.cell(row=r, column=1, value=etichetta)
            e.font = S.ETICHETTA_BOLD if risultato else S.ETICHETTA
            e.alignment = S.SINISTRA
            for i, f in enumerate([f_lib, f_conc, f_irp, f_brev], start=2):
                c = ws.cell(row=r, column=i, value=f)
                c.number_format = formato
                c.border = S.BORDO
                c.fill = S.FILL_RISULTATO if risultato else S.FILL_CALCOLO
                if risultato:
                    c.font = S.ETICHETTA_BOLD
            r += 1

        riga_conf("Canone o ricavo lordo annuo", "=canone_mese*12", "=canone_conc_mese*12", "=canone_mese*12", "=ricavi_brevi")
        riga_pot = base
        riga_conf("Perdita per sfitto", "=-canone_mese*mesi_sfitto", "=-canone_conc_mese*mesi_sfitto", "=-canone_mese*mesi_sfitto", "=0",)
        riga_sf = base + 1
        riga_conf(
            "Accantonamento morosita'",
            f"=-(B{riga_pot}+B{riga_sf})*morosita_pct",
            f"=-(C{riga_pot}+C{riga_sf})*morosita_pct",
            f"=-(D{riga_pot}+D{riga_sf})*morosita_pct",
            "=0",
        )
        riga_mo = base + 2
        riga_conf(
            "Ricavo effettivo",
            f"=SUM(B{riga_pot}:B{riga_mo})",
            f"=SUM(C{riga_pot}:C{riga_mo})",
            f"=SUM(D{riga_pot}:D{riga_mo})",
            f"=SUM(E{riga_pot}:E{riga_mo})",
        )
        riga_eff = base + 3
        riga_conf("Spese condominiali a carico", "=-condominio*quota_condominio", "=-condominio*quota_condominio", "=-condominio*quota_condominio", "=-condominio")
        riga_conf("Manutenzione ordinaria", "=-prezzo*manut_pct", "=-prezzo*manut_pct", "=-prezzo*manut_pct", "=-prezzo*manut_pct")
        riga_conf("Assicurazione", "=-assicurazione", "=-assicurazione", "=-assicurazione", "=-assicurazione")
        riga_conf(
            "Costo figurativo del proprio tempo",
            "=-costo_tempo", "=-costo_tempo", "=-costo_tempo",
            "=-costo_tempo*coefficiente_tempo_breve",
        )
        riga_conf(
            "Accantonamento ristrutturazione di fine ciclo",
            "=-accantonamento_ristrutturazione", "=-accantonamento_ristrutturazione",
            "=-accantonamento_ristrutturazione", "=-accantonamento_ristrutturazione",
        )
        riga_conf(
            "IMU",
            "=-rendita*riv_rendita*imu_molt*imu_aliquota",
            "=-rendita*riv_rendita*imu_molt*imu_aliquota*imu_conc",
            "=-rendita*riv_rendita*imu_molt*imu_aliquota",
            "=-rendita*riv_rendita*imu_molt*imu_aliquota",
        )
        riga_conf(
            "Gestione e costi variabili",
            f"=-B{riga_eff}*gestione_pct",
            f"=-C{riga_eff}*gestione_pct",
            f"=-D{riga_eff}*gestione_pct",
            f"=-E{riga_eff}*(gestione_pct+costi_brevi_pct)",
        )
        riga_gest_r = base + 10
        riga_conf(
            "Reddito operativo netto",
            f"=B{riga_eff}+SUM(B{base+4}:B{riga_gest_r})",
            f"=C{riga_eff}+SUM(C{base+4}:C{riga_gest_r})",
            f"=D{riga_eff}+SUM(D{base+4}:D{riga_gest_r})",
            f"=E{riga_eff}+SUM(E{base+4}:E{riga_gest_r})",
            risultato=True,
        )
        riga_noi = base + 11
        riga_conf(
            "Imposta sul reddito da locazione",
            f"=-B{riga_eff}*ced_libero",
            f"=-C{riga_eff}*ced_conc",
            f"=-(D{riga_eff}*(1-abbatt_ord)*(irpef_marginale+addizionali)+MAX(D{riga_eff}*reg_loc,reg_loc_min)/2)",
            f"=-E{riga_eff}*ced_breve1",
        )
        riga_imp = base + 12
        riga_conf(
            "Utile netto annuo",
            f"=B{riga_noi}+B{riga_imp}",
            f"=C{riga_noi}+C{riga_imp}",
            f"=D{riga_noi}+D{riga_imp}",
            f"=E{riga_noi}+E{riga_imp}",
            risultato=True,
        )
        riga_utile = base + 13
        riga_conf(
            "Rendimento lordo sul prezzo",
            f"=B{riga_pot}/prezzo", f"=C{riga_pot}/prezzo", f"=D{riga_pot}/prezzo", f"=E{riga_pot}/prezzo",
            formato=S.PERC,
        )
        riga_conf(
            "Rendimento netto sul costo totale",
            f"=B{riga_utile}/costo_totale", f"=C{riga_utile}/costo_totale",
            f"=D{riga_utile}/costo_totale", f"=E{riga_utile}/costo_totale",
            formato=S.PERC, risultato=True,
        )
        r += 1
        riga_scelta = r
        r = S.campo(
            ws, r, "Regime scelto per la proiezione",
            "cedolare_libero", input_utente=True,
            nota="Uno fra cedolare_libero, cedolare_concordato, irpef_ordinario, breve. Alimenta il foglio Cash flow.",
        )
        dv = DataValidation(type="list", formula1='"cedolare_libero,cedolare_concordato,irpef_ordinario,breve"', allow_blank=False)
        ws.add_data_validation(dv)
        dv.add(ws.cell(row=riga_scelta, column=2))
        self.nome("regime_scelto", ws, f"B{riga_scelta}")

        riga_sel_noi = r
        r = S.campo(
            ws, r, "Reddito operativo netto del regime scelto",
            f'=IF(regime_scelto="cedolare_libero",B{riga_noi},IF(regime_scelto="cedolare_concordato",C{riga_noi},IF(regime_scelto="irpef_ordinario",D{riga_noi},E{riga_noi})))',
            S.EURO, risultato=True,
        )
        self.nome("noi_annuo", ws, f"B{riga_sel_noi}")
        riga_sel_utile = r
        r = S.campo(
            ws, r, "Utile netto annuo del regime scelto",
            f'=IF(regime_scelto="cedolare_libero",B{riga_utile},IF(regime_scelto="cedolare_concordato",C{riga_utile},IF(regime_scelto="irpef_ordinario",D{riga_utile},E{riga_utile})))',
            S.EURO, risultato=True,
        )
        self.nome("utile_locazione", ws, f"B{riga_sel_utile}")
        riga_sel_canone = r
        r = S.campo(
            ws, r, "Ricavo lordo annuo del regime scelto",
            f'=IF(regime_scelto="cedolare_libero",B{riga_pot},IF(regime_scelto="cedolare_concordato",C{riga_pot},IF(regime_scelto="irpef_ordinario",D{riga_pot},E{riga_pot})))',
            S.EURO,
        )
        self.nome("ricavo_lordo", ws, f"B{riga_sel_canone}")
        riga_sel_eff = r
        r = S.campo(
            ws, r, "Ricavo effettivo del regime scelto",
            f'=IF(regime_scelto="cedolare_libero",B{riga_eff},IF(regime_scelto="cedolare_concordato",C{riga_eff},IF(regime_scelto="irpef_ordinario",D{riga_eff},E{riga_eff})))',
            S.EURO,
        )
        self.nome("ricavo_effettivo", ws, f"B{riga_sel_eff}")
        r += 1

        r = S.sezione(ws, r, "Vincoli e adempimenti del regime scelto", secondaria=True)
        for testo in [
            "Cedolare secca: si opta in sede di registrazione o per le annualita' successive, sostituisce IRPEF, addizionali, registro e bollo, ma comporta la rinuncia all'aggiornamento ISTAT del canone per tutta la durata dell'opzione.",
            "Canone concordato: il canone e' vincolato dall'accordo territoriale del Comune e serve l'attestazione di conformita' rilasciata da un'associazione firmataria. In cambio si ha la cedolare al dieci per cento e, nella maggior parte dei Comuni, lo sconto del venticinque per cento sull'IMU.",
            "IRPEF ordinaria: conviene solo con redditi bassi o con molti oneri da far valere. Il canone concorre al reddito complessivo e puo' spostare l'intero reddito in uno scaglione superiore.",
            "Locazione breve: dal 2026 il regime copre al massimo due unita' per periodo d'imposta, dalla terza scatta la presunzione di impresa con obbligo di partita IVA. Servono il codice identificativo nazionale in ogni annuncio, la comunicazione alla questura degli alloggiati, i dispositivi di sicurezza obbligatori dal 2025 e il rispetto dei regolamenti comunali e condominiali.",
        ]:
            r = S.nota_riga(ws, r, testo)

    # ---------------------------------------------------------------- cashflow
    def foglio_cashflow(self) -> None:
        ws = self.wb.create_sheet("Cash flow")
        ws.sheet_view.showGridLines = False
        S.larghezze_colonne(ws, {"A": 40, "B": 18, "C": 58})
        r = S.titolo(
            ws,
            1,
            "Proiezione del flusso di cassa",
            "Un anno per riga. L'ultimo anno incorpora la vendita: valore rivalutato, meno debito residuo, meno costi di uscita e imposta sulla plusvalenza.",
        )

        r = S.sezione(ws, r, "Assunzioni della proiezione")
        riga_or = r
        r = S.campo(ws, r, "Orizzonte di analisi in anni", 25, S.NUMERO, input_utente=True, nota="Quanti anni si pensa di tenere l'immobile. Oltre i costi di ingresso pesano meno.")
        self.nome("orizzonte", ws, f"B{riga_or}")
        riga_riv = r
        r = S.campo(ws, r, "Rivalutazione nominale annua dell'immobile", 0.02, S.PERC, input_utente=True, nota="In termini reali il mattone italiano e' rimasto sostanzialmente fermo per vent'anni: mettere qui l'inflazione e' gia' un'ipotesi ottimistica.")
        self.nome("riv_immobile", ws, f"B{riga_riv}")
        riga_ind = r
        r = S.campo(ws, r, "Indicizzazione annua del canone", 0.0, S.PERC, input_utente=True, nota="Con la cedolare secca l'aggiornamento ISTAT non si puo' applicare: lasciare zero.")
        self.nome("indicizzazione", ws, f"B{riga_ind}")
        riga_data = r
        r = S.campo(ws, r, "Data di erogazione del mutuo", date(2026, 9, 1), S.DATA, input_utente=True)
        self.nome("data_erogazione", ws, f"B{riga_data}")
        riga_ristr = r
        r = S.campo(ws, r, "Accantonamento annuo per ristrutturazione di fine ciclo", "=prezzo*ristrutt_pct/ristrutt_anni", S.EURO, nota="Un rifacimento completo ogni quarant'anni, spalmato. Ignorarlo e' l'errore piu' comune nelle valutazioni ottimistiche.")
        self.nome("accantonamento_ristrutturazione", ws, f"B{riga_ristr}")
        r += 2

        # I costi operativi della colonna D comprendono gia' l'accantonamento per la
        # ristrutturazione, perche' quest'ultimo e' una riga del conto economico nel
        # foglio Locazione ed entra quindi nel reddito operativo netto. Una colonna
        # separata qui lo conterebbe due volte.
        intest = [
            "Anno", "Ricavo lordo", "Ricavo effettivo", "Costi operativi",
            "Imposta sul reddito", "Rata mutuo", "Detrazione interessi", "Cash flow netto",
            "Cash flow cumulato", "Valore immobile", "Debito residuo", "Patrimonio netto", "Flusso per TIR",
        ]
        r = S.intestazioni(ws, r, intest, [8, 16, 16, 18, 16, 16, 16, 18, 18, 18, 16, 18, 18])
        prima = r

        # Anno zero: esce solo l'esborso iniziale.
        ws.cell(row=r, column=1, value=0).number_format = S.NUMERO
        for col in range(2, 10):
            ws.cell(row=r, column=col, value=0).number_format = S.EURO
        ws.cell(row=r, column=9, value="=-esborso").number_format = S.EURO
        ws.cell(row=r, column=10, value="=prezzo").number_format = S.EURO
        ws.cell(row=r, column=11, value="=mutuo_importo").number_format = S.EURO
        ws.cell(row=r, column=12, value="=prezzo-mutuo_importo").number_format = S.EURO
        ws.cell(row=r, column=13, value="=-esborso").number_format = S.EURO
        for col in range(1, 14):
            ws.cell(row=r, column=col).border = S.BORDO
            ws.cell(row=r, column=col).fill = S.FILL_CALCOLO
        r += 1

        for anno in range(1, ORIZZONTE_MAX + 1):
            attivo = f"$A{r}<=orizzonte"
            ws.cell(row=r, column=1, value=anno).number_format = S.NUMERO
            ws.cell(row=r, column=2, value=f'=IF({attivo},ricavo_lordo*(1+indicizzazione)^($A{r}-1),0)').number_format = S.EURO
            ws.cell(row=r, column=3, value=f'=IF({attivo},ricavo_effettivo*(1+indicizzazione)^($A{r}-1),0)').number_format = S.EURO
            ws.cell(row=r, column=4, value=f'=IF({attivo},-(ricavo_effettivo-noi_annuo)*(1+infl)^($A{r}-1),0)').number_format = S.EURO
            ws.cell(row=r, column=5, value=f'=IF({attivo},-(noi_annuo-utile_locazione)*(1+indicizzazione)^($A{r}-1),0)').number_format = S.EURO
            ws.cell(row=r, column=6, value=f'=IF(AND({attivo},$A{r}<=durata),-rata_annua,0)').number_format = S.EURO
            ws.cell(row=r, column=7, value=f'=IF({attivo},INDEX(detrazione_anno,MIN($A{r},{MAX_ANNI})),0)').number_format = S.EURO
            ws.cell(row=r, column=8, value=f"=SUM($C{r}:$G{r})").number_format = S.EURO
            ws.cell(row=r, column=9, value=f"=$I{r-1}+$H{r}").number_format = S.EURO
            ws.cell(row=r, column=10, value=f'=IF({attivo},prezzo*(1+riv_immobile)^$A{r},0)').number_format = S.EURO
            ws.cell(row=r, column=11, value=f'=IF({attivo},INDEX(debito_residuo_anno,MIN($A{r},{MAX_ANNI})),0)').number_format = S.EURO
            ws.cell(row=r, column=12, value=f'=IF({attivo},$J{r}-$K{r},0)').number_format = S.EURO
            ws.cell(
                row=r, column=13,
                value=(
                    f'=IF({attivo},$H{r}+IF($A{r}=orizzonte,'
                    f'$J{r}*(1-costi_vendita)-$K{r}-IF($A{r}<plus_anni,MAX(0,$J{r}-costo_totale)*plus_aliq,0),0),0)'
                ),
            ).number_format = S.EURO
            for col in range(1, 14):
                ws.cell(row=r, column=col).border = S.BORDO
                ws.cell(row=r, column=col).fill = S.FILL_CALCOLO
            r += 1

        ultima = r - 1
        self.nome_intervallo("flussi_tir", ws, f"$M${prima}:$M${ultima}")
        self.nome_intervallo("flussi_tir_dal_primo", ws, f"$M${prima+1}:$M${ultima}")
        self.nome_intervallo("cash_flow_annuo_serie", ws, f"$H${prima+1}:$H${ultima}")
        self.nome("cash_flow_primo_anno", ws, f"H{prima+1}")
        ws.freeze_panes = ws.cell(row=prima, column=2)

        ws.conditional_formatting.add(
            f"H{prima+1}:H{ultima}",
            CellIsRule(operator="lessThan", formula=["0"], fill=S.FILL_ATTENZIONE),
        )

    # ---------------------------------------------------------------- metriche
    def foglio_metriche(self) -> None:
        ws = self.wb.create_sheet("Metriche")
        ws.sheet_view.showGridLines = False
        S.larghezze_colonne(ws, {"A": 46, "B": 20, "C": 74})
        r = S.titolo(
            ws,
            1,
            "Indicatori di sintesi",
            "Tutti i rendimenti sono calcolati sul costo totale dell'operazione, non sul prezzo: usare il prezzo gonfia il risultato di circa un decimo.",
        )

        r = S.sezione(ws, r, "Capitale impiegato")
        r = S.campo(ws, r, "Prezzo", "=prezzo", S.EURO)
        r = S.campo(ws, r, "Costi accessori", "=costi_accessori", S.EURO)
        r = S.campo(ws, r, "Costo totale", "=costo_totale", S.EURO, risultato=True)
        r = S.campo(ws, r, "Capitale proprio immobilizzato", "=esborso", S.EURO, risultato=True)
        r = S.campo(ws, r, "Leva finanziaria", "=IF(esborso>0,costo_totale/esborso,0)", S.NUMERO_DEC, nota="Quante volte il capitale proprio: la leva amplifica sia il rendimento sia la perdita.")
        r += 1

        r = S.sezione(ws, r, "Redditivita' corrente", secondaria=True)
        r = S.campo(ws, r, "Rendimento lordo", "=ricavo_lordo/prezzo", S.PERC, nota="Canone annuo diviso prezzo. E' il numero che si legge negli annunci, ed e' il meno informativo.")
        r = S.campo(ws, r, "Rendimento netto", "=utile_locazione/costo_totale", S.PERC, risultato=True, nota="Utile dopo costi e imposte, sul costo totale. Fra il lordo e il netto si perdono di norma due punti e mezzo.")
        r = S.campo(ws, r, "Cap rate", "=noi_annuo/costo_totale", S.PERC, nota="Reddito operativo netto sul costo totale, prima delle imposte sul reddito e del mutuo. Serve a confrontare immobili fra loro, a prescindere da come sono finanziati.")
        riga_coc = r
        r = S.campo(ws, r, "Cash on cash", "=IF(esborso>0,cash_flow_primo_anno/esborso,0)", S.PERC, risultato=True, nota="Cassa netta del primo anno sul capitale proprio. Con la leva puo' essere negativo anche se l'operazione e' sana.")
        riga_dscr = r
        r = S.campo(ws, r, "Debt service coverage ratio", "=IF(rata_annua>0,noi_annuo/rata_annua,\"n.d.\")", S.NUMERO_DEC, nota="Sotto 1 il reddito non copre la rata e la differenza esce dalla tasca del proprietario ogni mese.")
        r = S.campo(ws, r, "Cash flow del primo anno", "=cash_flow_primo_anno", S.EURO, risultato=True)
        r = S.campo(ws, r, "Cash flow mensile", "=cash_flow_primo_anno/12", S.EURO_DEC)
        r += 1

        r = S.sezione(ws, r, "Redditivita' sull'intero orizzonte", secondaria=True)
        r = S.campo(ws, r, "Tasso interno di rendimento", "=IFERROR(IRR(flussi_tir),\"non calcolabile\")", S.PERC, risultato=True, nota="Include l'uscita finale. E' il numero da confrontare con il rendimento atteso di un portafoglio alternativo.")
        r = S.campo(ws, r, "Valore attuale netto", "=IFERROR(NPV(tasso_sconto,flussi_tir_dal_primo)-esborso,\"non calcolabile\")", S.EURO, nota="Positivo se l'operazione batte il tasso di sconto scelto nei parametri.")
        r = S.campo(ws, r, "Cassa cumulata a fine orizzonte", "=SUM(cash_flow_annuo_serie)", S.EURO)
        r = S.campo(ws, r, "Multiplo sul capitale proprio", "=IF(esborso>0,SUM(flussi_tir)/esborso+1,0)", S.NUMERO_DEC)
        r = S.campo(ws, r, "Anni per rientrare del capitale proprio", "=IF(cash_flow_primo_anno>0,esborso/cash_flow_primo_anno,\"mai, con questo cash flow\")", S.NUMERO_DEC)
        r += 1

        r = S.sezione(ws, r, "Concentrazione del patrimonio", secondaria=True)
        riga_patr = r
        r = S.campo(ws, r, "Patrimonio complessivo, immobili inclusi", 0, S.EURO, input_utente=True, nota="Somma di immobili gia' posseduti, liquidita' e investimenti finanziari, incluso questo acquisto. Zero per saltare il controllo.")
        self.nome("patrimonio_totale", ws, f"B{riga_patr}")
        riga_imm = r
        r = S.campo(ws, r, "Valore immobiliare complessivo dopo questo acquisto", 0, S.EURO, input_utente=True, nota="Prima casa, seconde case, quote ereditate e questo immobile.")
        self.nome("patrimonio_immobiliare", ws, f"B{riga_imm}")
        riga_quota_imm = r
        r = S.campo(ws, r, "Quota immobiliare del patrimonio", "=IF(patrimonio_totale>0,patrimonio_immobiliare/patrimonio_totale,\"n.d.\")", S.PERC, risultato=True)
        r = S.campo(
            ws, r, "Lettura della concentrazione",
            f'=IF(patrimonio_totale=0,"controllo non attivo",IF(B{riga_quota_imm}>0.66,"molto concentrato: oltre due terzi in immobili",'
            f'IF(B{riga_quota_imm}>0.33,"concentrato: oltre un terzo in immobili","entro un terzo del patrimonio")))',
            risultato=True,
        )
        for testo in [
            "Il controllo esiste perche' e' il rischio che il rendimento non vede. Un immobile e' un singolo bene, in una singola via, di un singolo Comune, comprato in un singolo momento del ciclo: porta insieme rischio di timing, di ciclo economico, di tasso e di localizzazione, e non si vende in tre giorni. Chi ha due terzi del patrimonio in mattone non ha un portafoglio diversificato, ha una scommessa sul mercato immobiliare della sua zona.",
            "Va poi sfatata un'aspettativa ricorrente: l'immobiliare non decorrela dall'azionario quando servirebbe. Nelle recessioni i due si muovono insieme, perche' e' la stessa contrazione del credito e della domanda a colpirli. Cio' che ha decorrelato nei momenti di crisi, in modo diverso a seconda dello scenario, e' stato semmai il reddito fisso o il bene rifugio.",
            "L'abitazione principale merita un discorso a parte. Il suo trattamento fiscale, dall'esenzione IMU alla detrazione degli interessi, e' un vantaggio che nessun altro investimento replica, ma resta un capitale che non si puo' diversificare, ne' rendere liquido, ne' bilanciare con il resto. E' la ragione per cui va contata nella concentrazione anche se non e' un investimento.",
        ]:
            r = S.nota_riga(ws, r, testo, 3)
        r += 1

        r = S.sezione(ws, r, "Lettura", secondaria=True)
        riga_verdetto = r
        r = S.campo(
            ws, r, "Sintesi automatica",
            '=IF(IFERROR(IRR(flussi_tir),-1)<0,"Operazione in perdita sull\'orizzonte scelto",'
            'IF(IFERROR(IRR(flussi_tir),0)<tasso_sconto,"Rende meno del costo opportunita\' del capitale",'
            'IF(IFERROR(IRR(flussi_tir),0)<rend_port,"Rende, ma meno del portafoglio alternativo",'
            '"Batte il portafoglio alternativo sulle assunzioni date")))',
            risultato=True,
        )
        ws.cell(row=riga_verdetto, column=2).alignment = S.SINISTRA
        for testo in [
            "Il verdetto automatico confronta il tasso interno di rendimento con il tasso di sconto e con il rendimento atteso del portafoglio alternativo. Sono tutte assunzioni impostate nel foglio Parametri: cambiandole cambia il verdetto, ed e' esattamente il punto.",
            "Il tasso interno di rendimento non pesa il rischio. Un immobile ha rischio di sfitto, di morosita', di deterioramento, di illiquidita' e di concentrazione su un singolo bene in una singola via di un singolo Comune. Un portafoglio diversificato con lo stesso rendimento atteso non e' la stessa cosa, e la differenza va messa a mano nel giudizio.",
            "Il modello non prezza il lavoro. Gestire un immobile in affitto significa registrare i contratti, seguire le assemblee, rincorrere le manutenzioni, gestire l'inquilino che non paga. Quel tempo ha un costo che nessuna cella cattura.",
        ]:
            r = S.nota_riga(ws, r, testo, 3)

    # --------------------------------------------------------------- confronto
    def foglio_confronto(self) -> None:
        ws = self.wb.create_sheet("Confronto affitto")
        ws.sheet_view.showGridLines = False
        S.larghezze_colonne(ws, {"A": 44, "B": 20, "C": 66})
        r = S.titolo(
            ws,
            1,
            "Comprare oppure restare in affitto investendo la differenza",
            "Confronto a parita' di esborso, nell'impostazione dei fogli di Paolo Coletti: chi non compra investe l'anticipo e ogni anno la differenza fra la rata piu' i costi da proprietario e il canone che paga.",
        )

        r = S.sezione(ws, r, "Assunzioni del confronto")
        riga_can_alt = r
        r = S.campo(ws, r, "Canone mensile che si pagherebbe restando in affitto", 550, S.EURO, input_utente=True, nota="Per un immobile equivalente a quello che si comprerebbe, non per quello in cui si vive oggi.")
        self.nome("canone_alternativo", ws, f"B{riga_can_alt}")
        riga_costi_prop = r
        r = S.campo(ws, r, "Costi annui del proprietario", "=condominio*quota_condominio+prezzo*manut_pct+assicurazione+accantonamento_ristrutturazione+IF(abitazione_principale=\"SI\",0,rendita*riv_rendita*imu_molt*imu_aliquota)", S.EURO, nota="Condominio a carico, manutenzione, assicurazione, accantonamento per la ristrutturazione, IMU se non e' abitazione principale.")
        self.nome("costi_proprietario", ws, f"B{riga_costi_prop}")
        r += 1

        r = S.intestazioni(ws, r, ["Anno", "Uscite comprando", "Uscite affittando", "Differenza investita", "Portafoglio", "Versato", "Valore immobile", "Debito residuo"], [8, 20, 20, 20, 20, 18, 20, 18])
        prima = r
        ws.cell(row=r, column=1, value=0).number_format = S.NUMERO
        ws.cell(row=r, column=2, value="=esborso").number_format = S.EURO
        ws.cell(row=r, column=3, value=0).number_format = S.EURO
        ws.cell(row=r, column=4, value="=esborso").number_format = S.EURO
        ws.cell(row=r, column=5, value="=esborso").number_format = S.EURO
        ws.cell(row=r, column=6, value="=esborso").number_format = S.EURO
        ws.cell(row=r, column=7, value="=prezzo").number_format = S.EURO
        ws.cell(row=r, column=8, value="=mutuo_importo").number_format = S.EURO
        for col in range(1, 9):
            ws.cell(row=r, column=col).border = S.BORDO
            ws.cell(row=r, column=col).fill = S.FILL_CALCOLO
        r += 1

        for anno in range(1, ORIZZONTE_MAX + 1):
            attivo = f"$A{r}<=orizzonte"
            ws.cell(row=r, column=1, value=anno).number_format = S.NUMERO
            ws.cell(row=r, column=2, value=f'=IF({attivo},IF($A{r}<=durata,rata_annua,0)+costi_proprietario*(1+infl)^($A{r}-1)-IF(abitazione_principale="SI",INDEX(detrazione_anno,MIN($A{r},{MAX_ANNI})),0),0)').number_format = S.EURO
            ws.cell(row=r, column=3, value=f'=IF({attivo},canone_alternativo*12*(1+infl)^($A{r}-1),0)').number_format = S.EURO
            ws.cell(row=r, column=4, value=f"=$B{r}-$C{r}").number_format = S.EURO
            ws.cell(row=r, column=5, value=f'=IF({attivo},$E{r-1}*(1+rend_port)+$D{r},0)').number_format = S.EURO
            ws.cell(row=r, column=6, value=f'=IF({attivo},$F{r-1}+$D{r},0)').number_format = S.EURO
            ws.cell(row=r, column=7, value=f'=IF({attivo},prezzo*(1+riv_immobile)^$A{r},0)').number_format = S.EURO
            ws.cell(row=r, column=8, value=f'=IF({attivo},INDEX(debito_residuo_anno,MIN($A{r},{MAX_ANNI})),0)').number_format = S.EURO
            for col in range(1, 9):
                ws.cell(row=r, column=col).border = S.BORDO
                ws.cell(row=r, column=col).fill = S.FILL_CALCOLO
            r += 1
        ultima = r - 1
        self.nome_intervallo("conf_portafoglio", ws, f"$E${prima}:$E${ultima}")
        self.nome_intervallo("conf_versato", ws, f"$F${prima}:$F${ultima}")
        self.nome_intervallo("conf_valore", ws, f"$G${prima}:$G${ultima}")
        self.nome_intervallo("conf_debito", ws, f"$H${prima}:$H${ultima}")
        r += 1

        r = S.sezione(ws, r, "Esito a fine orizzonte", secondaria=True)
        riga_pc = r
        r = S.campo(ws, r, "Patrimonio comprando", "=INDEX(conf_valore,orizzonte+1)*(1-costi_vendita)-INDEX(conf_debito,orizzonte+1)", S.EURO, risultato=True, nota="Valore dell'immobile al netto dei costi di vendita e del debito residuo.")
        r = S.campo(ws, r, "Portafoglio lordo affittando", "=INDEX(conf_portafoglio,orizzonte+1)", S.EURO)
        r = S.campo(ws, r, "Capitale versato nel portafoglio", "=INDEX(conf_versato,orizzonte+1)", S.EURO)
        riga_pa = r
        r = S.campo(ws, r, "Patrimonio affittando, al netto dell'imposta", "=INDEX(conf_portafoglio,orizzonte+1)-MAX(0,INDEX(conf_portafoglio,orizzonte+1)-INDEX(conf_versato,orizzonte+1))*tax_port", S.EURO, risultato=True)
        riga_diff = r
        r = S.campo(ws, r, "Differenza a favore dell'acquisto", f"=B{riga_pc}-B{riga_pa}", S.EURO, risultato=True)
        riga_verd = r
        r = S.campo(ws, r, "Esito", f'=IF(B{riga_diff}>0,"Conviene comprare","Conviene restare in affitto e investire la differenza")', risultato=True)
        ws.cell(row=riga_verd, column=2).alignment = S.SINISTRA
        r += 1
        for testo in [
            "Il confronto e' sensibile a tre soli numeri: il rendimento atteso del portafoglio, la rivalutazione dell'immobile e il canone alternativo. Cambiando il primo di un punto l'esito spesso si ribalta, il che dice quanto poco vada preso come verdetto e quanto vada preso come mappa di sensibilita'.",
            "Il modello assume disciplina perfetta di chi affitta: investe davvero ogni euro di differenza, ogni anno, senza toccarlo. Nella realta' quasi nessuno lo fa, e il mutuo funziona come piano di accumulo forzato. E' un vantaggio comportamentale reale che il foglio non sa misurare.",
            "Restano fuori dal conto la sicurezza abitativa, la liberta' di ristrutturare, il rischio di sfratto e il vincolo di mobilita' lavorativa. Sono decisivi nella scelta di dove vivere e irrilevanti nella scelta di dove investire: e' la ragione per cui le due domande vanno tenute separate.",
        ]:
            r = S.nota_riga(ws, r, testo, 3)

    # ----------------------------------------------------------------- scenari
    def foglio_scenari(self) -> None:
        ws = self.wb.create_sheet("Scenari")
        ws.sheet_view.showGridLines = False
        S.larghezze_colonne(ws, {"A": 30, "B": 16, "C": 16, "D": 16, "E": 16, "F": 16, "G": 16, "H": 16})
        r = S.titolo(
            ws,
            1,
            "Sensibilita'",
            "Il valore centrale di ogni tabella e' lo scenario base. Le variazioni sono quelle che si osservano davvero: mezzo punto di tasso, un decimo di canone, un decimo di prezzo.",
        )

        r = S.sezione(ws, r, "Cash flow annuo al variare di tasso e canone")
        r = S.nota_riga(ws, r, "Righe: tasso del mutuo. Colonne: canone mensile. Il cash flow e' il reddito operativo netto meno l'imposta e meno la rata, ricalcolati per ciascuna combinazione. Le celle rosse sono quelle in cui l'immobile costa piu' di quanto rende.")
        variazioni_tasso = [-0.010, -0.005, 0.0, 0.005, 0.010, 0.015]
        variazioni_canone = [-0.20, -0.10, 0.0, 0.10, 0.20]

        r = S.intestazioni(ws, r, ["Tasso \\ canone"] + [f"{v:+.0%}" for v in variazioni_canone], [24, 16, 16, 16, 16, 16])
        prima = r
        for dt in variazioni_tasso:
            c = ws.cell(row=r, column=1, value=f"=TEXT(tasso{dt:+f},\"0.00%\")")
            c.font = S.ETICHETTA_BOLD
            c.fill = S.FILL_CALCOLO
            c.border = S.BORDO
            for j, dc in enumerate(variazioni_canone, start=2):
                canone = f"canone_mese*12*(1+{dc})"
                effettivo = f"({canone}-canone_mese*mesi_sfitto*(1+{dc}))*(1-morosita_pct)"
                costi = "(condominio*quota_condominio+prezzo*manut_pct+assicurazione+rendita*riv_rendita*imu_molt*imu_aliquota+accantonamento_ristrutturazione)"
                imposta = f"{effettivo}*ced_libero"
                rata = f"IF(mutuo_importo>0,PMT((tasso{dt:+f})/12,durata*12,-mutuo_importo)*12,0)"
                cella = ws.cell(row=r, column=j, value=f"={effettivo}-{costi}-{imposta}-{rata}")
                cella.number_format = S.EURO
                cella.border = S.BORDO
                cella.fill = S.FILL_CALCOLO
            r += 1
        ultima = r - 1
        ws.conditional_formatting.add(
            f"B{prima}:F{ultima}",
            CellIsRule(operator="lessThan", formula=["0"], fill=S.FILL_ATTENZIONE),
        )
        ws.conditional_formatting.add(
            f"B{prima}:F{ultima}",
            ColorScaleRule(start_type="min", start_color="F8CBAD", mid_type="num", mid_value=0, mid_color="FFF2CC", end_type="max", end_color="C6E0B4"),
        )
        r += 2

        r = S.sezione(ws, r, "Rendimento netto al variare del prezzo", secondaria=True)
        r = S.nota_riga(ws, r, "Il prezzo entra due volte: al numeratore attraverso la manutenzione, al denominatore attraverso il costo totale e attraverso le imposte, che con il prezzo-valore restano pero' ancorate alla rendita catastale e non scendono con il prezzo.")
        variazioni_prezzo = [-0.20, -0.15, -0.10, -0.05, 0.0, 0.05, 0.10]
        r = S.intestazioni(ws, r, ["Variazione prezzo", "Prezzo", "Imposte", "Costo totale", "Utile netto", "Rendimento netto", "Cash flow"], [20, 16, 16, 18, 16, 18, 16])
        prima2 = r
        for dp in variazioni_prezzo:
            prezzo_v = f"prezzo*(1+{dp})"
            imposte_v = (
                f'IF(da_impresa="SI",{prezzo_v}*IF(agevolata="SI",iva_prima,IF(di_lusso="SI",iva_lusso,iva_ord))+3*fisso_impresa,'
                f'MAX(IF(AND(usa_prezzo_valore="SI",rendita>0),valore_catastale,{prezzo_v})*IF(agevolata="SI",reg_prima,reg_ord),reg_min)+ipo_priv+cat_priv)'
            )
            costo_v = f"{prezzo_v}+{imposte_v}+{prezzo_v}*provv_pct*(1+iva_provv)+notaio_cv+altri_costi+oneri_mutuo"
            utile_v = f"utile_locazione-({prezzo_v}-prezzo)*manut_pct"
            ws.cell(row=r, column=1, value=f"{dp:+.0%}").font = S.ETICHETTA_BOLD
            ws.cell(row=r, column=2, value=f"={prezzo_v}").number_format = S.EURO
            ws.cell(row=r, column=3, value=f"={imposte_v}").number_format = S.EURO
            ws.cell(row=r, column=4, value=f"={costo_v}").number_format = S.EURO
            ws.cell(row=r, column=5, value=f"={utile_v}").number_format = S.EURO
            ws.cell(row=r, column=6, value=f"=({utile_v})/({costo_v})").number_format = S.PERC
            ws.cell(row=r, column=7, value=f"={utile_v}-rata_annua").number_format = S.EURO
            for col in range(1, 8):
                ws.cell(row=r, column=col).border = S.BORDO
                ws.cell(row=r, column=col).fill = S.FILL_CALCOLO
            r += 1
        ultima2 = r - 1
        ws.conditional_formatting.add(
            f"F{prima2}:F{ultima2}",
            ColorScaleRule(start_type="min", start_color="F8CBAD", end_type="max", end_color="C6E0B4"),
        )
        r += 2

        r = S.sezione(ws, r, "Prezzo massimo sostenibile", secondaria=True)
        riga_obiettivo = r
        r = S.campo(ws, r, "Rendimento netto obiettivo", 0.04, S.PERC, input_utente=True, nota="Il rendimento sotto il quale l'operazione non ha senso rispetto alle alternative. Lo usa anche il foglio Confronto immobili per dare l'esito di ciascun annuncio.")
        self.nome("rend_obiettivo", ws, f"B{riga_obiettivo}")
        r = S.campo(ws, r, "Costo totale sostenibile a quel rendimento", f"=utile_locazione/B{riga_obiettivo}", S.EURO)
        riga_costo_sost = r - 1
        r = S.campo(ws, r, "Prezzo massimo corrispondente", f"=B{riga_costo_sost}/(1+incidenza_costi)", S.EURO, risultato=True, nota="Approssimazione: assume che l'incidenza percentuale dei costi accessori resti quella dello scenario base.")
        r = S.campo(ws, r, "Scarto rispetto al prezzo trattato", f"=B{riga_costo_sost}/(1+incidenza_costi)-prezzo", S.EURO, nota="Se negativo, il prezzo trattato e' sopra quello che l'immobile puo' giustificare a quel rendimento.")
        r = S.campo(ws, r, "Canone minimo per un cash flow non negativo", "=(rata_annua+condominio*quota_condominio+prezzo*manut_pct+assicurazione+rendita*riv_rendita*imu_molt*imu_aliquota+accantonamento_ristrutturazione)/((12-mesi_sfitto)*(1-morosita_pct)*(1-ced_libero))", S.EURO_DEC, risultato=True, nota="Canone mensile sotto il quale l'immobile assorbe cassa invece di generarla.")

    # ---------------------------------------------------------------- checklist
    def foglio_checklist(self) -> None:
        ws = self.wb.create_sheet("Checklist")
        ws.sheet_view.showGridLines = False
        r = S.titolo(
            ws,
            1,
            "Verifiche prima di firmare",
            "Una proposta di acquisto accettata dal venditore e' gia' un contratto preliminare vincolante: le verifiche vanno chiuse prima, oppure vanno trasformate in condizioni scritte nella proposta stessa.",
            7,
        )
        r = S.intestazioni(
            ws, r,
            ["Fase", "Verifica", "Perche' conta", "Documento o fonte", "Chi la fa", "Stato", "Note"],
            [16, 40, 62, 34, 20, 14, 30],
        )
        prima = r

        voci = [
            ("Prima della proposta", "Visura catastale aggiornata e planimetria depositata",
             "L'atto e' nullo se manca la dichiarazione di conformita' fra planimetria e stato di fatto. Non ogni difformita' pero' produce nullita': la Cassazione distingue le irregolarita' significative dai difetti minori.",
             "Agenzia delle Entrate, servizi catastali", "Acquirente o tecnico", "da fare", ""),
            ("Prima della proposta", "Conformita' urbanistica ed edilizia",
             "E' la corrispondenza fra lo stato di fatto e tutti i titoli edilizi della storia del fabbricato. E' cosa diversa dalla conformita' catastale e va verificata separatamente: e' la difformita' che blocca davvero la vendita e il mutuo.",
             "Accesso agli atti in Comune, titoli edilizi", "Tecnico di parte", "da fare", ""),
            ("Prima della proposta", "Stato legittimo e tolleranze costruttive",
             "Il decreto Salva Casa ha ampliato le tolleranze dell'articolo 34-bis del DPR 380/2001 per le difformita' realizzate prima del 24 maggio 2024, e ha dato valore probatorio alle dichiarazioni del tecnico. Sapere in quale regime ricade l'immobile cambia il costo della regolarizzazione.",
             "Relazione del tecnico, DL 69/2024 convertito in legge 105/2024", "Tecnico di parte", "da fare", ""),
            ("Prima della proposta", "Visura ipotecaria ventennale",
             "Rivela ipoteche, pignoramenti, sequestri, diritti di terzi, servitu' e trascrizioni pregiudizievoli. L'ipoteca del venditore va cancellata prima o contestualmente al rogito.",
             "Conservatoria dei registri immobiliari", "Notaio o visurista", "da fare", ""),
            ("Prima della proposta", "Atto di provenienza e continuita' delle trascrizioni",
             "Dice come il venditore e' diventato proprietario. Una provenienza per donazione e' un rischio concreto per il mutuo, perche' l'immobile e' aggredibile dai legittimari lesi.",
             "Atto notarile di acquisto o successione", "Notaio", "da fare", ""),
            ("Prima della proposta", "Quotazioni OMI della zona e comparabili reali",
             "Ancora il prezzo a un riferimento verificabile invece che alla richiesta dell'agenzia. Le quotazioni OMI sono semestrali, gratuite e pubbliche.",
             "Osservatorio del mercato immobiliare, Agenzia delle Entrate", "Acquirente", "da fare", ""),
            ("Prima della proposta", "Spese condominiali e liberatoria dell'amministratore",
             "L'acquirente risponde in solido con il venditore delle spese dell'anno in corso e di quello precedente. Vanno letti anche i verbali delle ultime assemblee, per i lavori deliberati e non ancora pagati.",
             "Consuntivi, riparti, verbali, regolamento", "Amministratore", "da fare", ""),
            ("Nella proposta", "Condizione sospensiva o risolutiva legata al mutuo",
             "Senza clausola, se la banca non delibera si perde la caparra e si deve comunque la provvigione. Con la sospensiva il contratto non produce effetti finche' la banca non eroga; con la risolutiva il contratto si scioglie se la condizione non si avvera entro il termine.",
             "Testo della proposta, articoli 1353 e seguenti del codice civile", "Acquirente e legale", "da fare", ""),
            ("Nella proposta", "Provvigione dell'agenzia legata all'avveramento della condizione",
             "La provvigione matura alla conclusione dell'affare. Se la condizione non si avvera e nulla e' stato pattuito, l'agenzia puo' comunque pretenderla: va escluso espressamente per iscritto.",
             "Testo della proposta", "Acquirente e legale", "da fare", ""),
            ("Nella proposta", "Termine per la stipula del definitivo",
             "Senza un termine, l'obbligo di concludere resta indeterminato e diventa difficile far valere l'inadempimento della controparte.",
             "Testo della proposta", "Acquirente e legale", "da fare", ""),
            ("Nella proposta", "Stato di fatto e di diritto e garanzia di libertà da gravami",
             "Va scritto che l'immobile e' trasferito libero da ipoteche, pesi, vincoli, pegni e da qualsivoglia gravame, e che il venditore garantisce la conformita' urbanistica e catastale.",
             "Testo della proposta", "Acquirente e legale", "da fare", ""),
            ("Nella proposta", "Natura delle somme versate, acconto o caparra confirmatoria",
             "La caparra confirmatoria da' diritto al doppio in caso di inadempimento del venditore; l'acconto no. La differenza va scritta, non lasciata implicita.",
             "Articolo 1385 del codice civile", "Acquirente e legale", "da fare", ""),
            ("Mutuo", "Farsi consegnare il PIES di ogni banca interpellata",
             "Il Prospetto Informativo Europeo Standardizzato e' il documento personalizzato che la banca deve consegnare gratuitamente prima che il cliente sia vincolato, ed e' l'unico modo per confrontare offerte diverse sulla stessa base. Contiene anche una tabella di ammortamento esemplificativa.",
             "Banca d'Italia, guida al mutuo ipotecario", "Acquirente", "da fare", ""),
            ("Mutuo", "Usare i sette giorni di riflessione sull'offerta vincolante",
             "Ricevuta l'offerta vincolante il consumatore ha diritto ad almeno sette giorni di riflessione, durante i quali l'offerta resta ferma per la banca e puo' essere accettata in qualsiasi momento. Sono giorni per confrontare, non per aspettare.",
             "Banca d'Italia, guida al mutuo ipotecario", "Acquirente", "da fare", ""),
            ("Mutuo", "Verificare che il tasso non sia usurario",
             "Al momento della firma il tasso non puo' superare la soglia d'usura, determinata sul tasso effettivo globale medio pubblicato trimestralmente. E' un controllo di un minuto che si fa una volta sola.",
             "Banca d'Italia, tassi effettivi globali medi", "Acquirente", "da fare", ""),
            ("Mutuo", "Confrontare la polizza della banca con il mercato",
             "La polizza incendio e scoppio e' obbligatoria ma il cliente puo' presentarne una reperita altrove, purche' di protezione equivalente, e la banca deve accettarla. Se si accetta quella proposta dalla banca, il cliente ha diritto di sapere quanta provvigione la compagnia paga alla banca stessa.",
             "Banca d'Italia, guida al mutuo ipotecario", "Acquirente", "da fare", ""),
            ("Mutuo", "Controllare la propria posizione in Centrale dei Rischi",
             "L'accesso ai propri dati e' gratuito e si fa online. Una segnalazione dimenticata o una pratica ancora aperta presso un mediatore creditizio pesa sulla delibera: l'incarico di mediazione si puo' revocare per iscritto, e con esso decade la richiesta in corso.",
             "Banca d'Italia, accesso alla Centrale dei Rischi", "Acquirente", "da fare", ""),
            ("Mutuo", "Sapere che la portabilita' e' gratuita per legge",
             "Trasferire il mutuo a un'altra banca, cioe' la surroga, e' per legge senza spese ne' penali, e non richiede il consenso della banca di partenza. In pratica se ne ottiene una nella vita del mutuo: le banche identificano il surrogatore seriale e negano la delibera, e le surroghe hanno spesso spread piu' alti proprio per questo.",
             "Banca d'Italia, guida al mutuo ipotecario", "Acquirente", "n.a.", ""),
            ("Prima del rogito", "Attestato di prestazione energetica",
             "E' obbligatorio allegarlo all'atto e va indicato negli annunci. Determina anche la classe da cui partire per ogni valutazione di adeguamento futuro.",
             "APE in corso di validita'", "Venditore", "da fare", ""),
            ("Prima del rogito", "Dichiarazione di conformita' o rispondenza degli impianti",
             "Per gli impianti realizzati dopo il 2008 serve la dichiarazione di conformita' ai sensi del DM 37/2008; per i piu' vecchi puo' bastare la dichiarazione di rispondenza rilasciata da un tecnico abilitato.",
             "Dichiarazione dell'installatore o del tecnico", "Venditore", "da fare", ""),
            ("Prima del rogito", "Trascrizione del preliminare se i tempi sono lunghi",
             "La trascrizione ai sensi dell'articolo 2645-bis protegge da ipoteche e pignoramenti iscritti dopo la firma e da' privilegio sul credito restitutorio. Ha un costo, e su tempi lunghi o su venditori a rischio lo vale.",
             "Preliminare in forma notarile", "Notaio", "da fare", ""),
            ("Prima del rogito", "Verifica dei requisiti prima casa e delle dichiarazioni in atto",
             "Residenza nel Comune o impegno a trasferirla entro diciotto mesi, assenza di altra abitazione nel Comune, assenza di altra prima casa agevolata in Italia salvo rivendita entro due anni. In comunione legale entrambi i coniugi devono intervenire in atto e rendere le dichiarazioni.",
             "Guida dell'Agenzia delle Entrate sulle agevolazioni prima casa", "Notaio", "da fare", ""),
            ("Prima del rogito", "Opzione prezzo-valore richiesta espressamente",
             "Va chiesta in atto e comporta la tassazione sul valore catastale, il blocco dell'accertamento di valore e la riduzione del trenta per cento dell'onorario notarile.",
             "Articolo 1 comma 497 legge 266/2005", "Notaio", "da fare", ""),
            ("Nuova costruzione", "Fideiussione a garanzia degli acconti",
             "Il decreto legislativo 122/2005 impone al costruttore di consegnare una fideiussione bancaria o assicurativa a garanzia di tutte le somme versate prima del trasferimento. La tutela non e' rinunciabile e ogni patto contrario e' nullo.",
             "Decreto legislativo 122/2005", "Notaio", "n.a.", ""),
            ("Nuova costruzione", "Polizza indennitaria decennale postuma",
             "Copre i danni materiali da rovina totale o parziale e da gravi difetti costruttivi per dieci anni dall'ultimazione. Va consegnata all'atto e gli estremi vanno indicati nel rogito.",
             "Decreto legislativo 122/2005, articolo 4", "Notaio", "n.a.", ""),
            ("Nuova costruzione", "Permesso di costruire, agibilita' e accatastamento",
             "La banca non delibera prima dell'accatastamento definitivo. Vanno verificati il titolo edilizio, il collaudo, l'agibilita' e la corrispondenza fra progetto approvato e stato realizzato.",
             "Titoli edilizi e certificato di agibilita'", "Tecnico di parte", "n.a.", ""),
            ("Nuova costruzione", "Capitolato, extracapitolato e cronoprogramma",
             "Distinguere cosa e' incluso nel prezzo da cosa e' extra evita la sorpresa piu' cara dell'acquisto sulla carta. Il cronoprogramma con le penali per il ritardo va scritto.",
             "Contratto di appalto e capitolato", "Acquirente", "n.a.", ""),
            ("Se si affitta", "Codice identificativo nazionale e adempimenti della locazione breve",
             "Dal 2026 il CIN va indicato in ogni annuncio e comunicazione. Servono inoltre la comunicazione alla questura degli alloggiati, i dispositivi di sicurezza obbligatori e il rispetto dei regolamenti comunali e condominiali.",
             "Ministero del turismo, banca dati strutture ricettive", "Proprietario", "n.a.", ""),
            ("Se si affitta", "Accordo territoriale e attestazione, se canone concordato",
             "Il canone concordato richiede l'attestazione di conformita' rilasciata da un'associazione firmataria dell'accordo territoriale del Comune, senza la quale i benefici fiscali decadono.",
             "Accordo territoriale del Comune", "Proprietario", "n.a.", ""),
            ("Se si affitta", "Verifica del regolamento condominiale",
             "Un regolamento contrattuale puo' vietare la locazione turistica o l'uso diverso dall'abitazione. Va letto prima di costruire un piano su affitti brevi.",
             "Regolamento condominiale trascritto", "Proprietario", "n.a.", ""),
        ]

        stato = DataValidation(type="list", formula1='"da fare,in corso,fatto,non applicabile,n.a."', allow_blank=True)
        ws.add_data_validation(stato)

        for fase, verifica, perche, fonte, chi, st, note in voci:
            ws.cell(row=r, column=1, value=fase).alignment = S.SINISTRA
            ws.cell(row=r, column=2, value=verifica).alignment = S.SINISTRA
            ws.cell(row=r, column=2).font = S.ETICHETTA_BOLD
            ws.cell(row=r, column=3, value=perche).alignment = S.SINISTRA
            ws.cell(row=r, column=4, value=fonte).alignment = S.SINISTRA
            ws.cell(row=r, column=5, value=chi).alignment = S.SINISTRA
            c = ws.cell(row=r, column=6, value=st)
            c.fill = S.FILL_INPUT
            c.alignment = S.CENTRO
            stato.add(c)
            ws.cell(row=r, column=7, value=note).fill = S.FILL_INPUT
            for col in range(1, 8):
                ws.cell(row=r, column=col).border = S.BORDO
            ws.row_dimensions[r].height = 46
            r += 1

        ultima = r - 1
        ws.auto_filter.ref = f"A{prima-1}:G{ultima}"
        ws.freeze_panes = ws.cell(row=prima, column=1)
        ws.conditional_formatting.add(
            f"F{prima}:F{ultima}",
            CellIsRule(operator="equal", formula=['"fatto"'], fill=S.FILL_RISULTATO),
        )
        ws.conditional_formatting.add(
            f"F{prima}:F{ultima}",
            CellIsRule(operator="equal", formula=['"da fare"'], fill=S.FILL_ATTENZIONE),
        )
        r += 1
        r = S.campo(ws, r, "Verifiche ancora aperte", f'=COUNTIF(F{prima}:F{ultima},"da fare")+COUNTIF(F{prima}:F{ultima},"in corso")', S.NUMERO, risultato=True)

    # ----------------------------------------------------------------- annunci
    def foglio_annunci(self) -> None:
        ws = self.wb.create_sheet("Annunci")
        ws.sheet_view.showGridLines = False
        r = S.titolo(
            ws,
            1,
            "Registro degli immobili in valutazione",
            "Un immobile per riga. Le colonne calcolate danno prezzo al metro quadro, rendimento lordo e scarto rispetto alla quotazione OMI della zona, cosi' che il confronto sia immediato. Il file si popola anche dalla riga di comando con lo strumento annunci.",
            26,
        )
        # L'ordine delle colonne e' contrattuale: `annunci.esporta_in_excel` scrive
        # posizione per posizione e le tre colonne di formula non vanno mai toccate.
        colonne = [
            ("ID", 12), ("Data", 12), ("Stato", 16), ("Fonte", 18), ("Agenzia", 22),
            ("Contatto", 20), ("Link", 40), ("Comune", 20), ("Prov.", 8),
            ("Zona OMI", 12), ("Indirizzo", 28), ("Tipologia", 16),
            ("Destinazione d'uso", 22), ("Nuova costr.", 12), ("Data consegna", 14),
            ("Mq", 8), ("Prezzo richiesto", 16), ("Prezzo obiettivo", 16),
            ("Prezzo al mq", 14), ("Quotazione OMI min", 16), ("Quotazione OMI max", 16),
            ("Scarto su OMI", 14), ("Rendita catastale", 16), ("Categoria", 12),
            ("Piano", 8), ("Classe energetica", 14), ("Spese condominio anno", 18),
            ("Canone atteso mese", 16), ("Rendimento lordo", 14), ("Punteggio", 10),
            ("Note", 46),
        ]
        CALCOLATE = (19, 22, 29)   # prezzo al mq, scarto su OMI, rendimento lordo
        TOTALE = len(colonne)
        r = S.intestazioni(ws, r, [c[0] for c in colonne], [c[1] for c in colonne])
        prima = r

        stato = DataValidation(type="list", formula1='"da contattare,contattato,visita fissata,visitata,proposta fatta,scartato,acquistato"', allow_blank=True)
        ws.add_data_validation(stato)
        nuova = DataValidation(type="list", formula1='"SI,NO"', allow_blank=True)
        ws.add_data_validation(nuova)
        uso = DataValidation(type="list", formula1='"abitazione,ufficio,negozio,box,magazzino,altro"', allow_blank=True)
        ws.add_data_validation(uso)

        # Riga dimostrativa, con dati interamente di fantasia: mostra il formato
        # atteso di ogni colonna senza esporre l'annuncio, l'agenzia o il recapito di
        # nessuno. Il dominio `.invalid` e' riservato dalla RFC 2606 e non risolve.
        esempi = [
            ("house_1", date(2026, 1, 1), "da contattare", "portale.invalid", "Agenzia di esempio",
             "000 0000000", "https://portale.invalid/annuncio/1", "Comune di esempio",
             "XX", "D4", "via di esempio 1", "trilocale", "abitazione", "NO", "pronto",
             75, 89000, 82000, None, 1100, 1450, None, 420, "A/3", "1", "E", 900, 550, None, 7,
             "Riga di esempio: sovrascriverla o cancellarla al primo uso"),
        ]
        for e in esempi:
            for i, valore in enumerate(e, start=1):
                c = ws.cell(row=r, column=i, value=valore)
                c.border = S.BORDO
                c.fill = S.FILL_CALCOLO if i in CALCOLATE else S.FILL_INPUT
            r += 1

        for riga in range(prima, prima + 200):
            ws.cell(row=riga, column=2).number_format = S.DATA
            for colonna in (17, 18, 20, 21, 27, 28):
                ws.cell(row=riga, column=colonna).number_format = S.EURO
            ws.cell(row=riga, column=23).number_format = S.EURO_DEC
            # Prezzo al metro quadro, sul prezzo richiesto: e' quello confrontabile
            # con la quotazione di zona, mentre l'obiettivo e' una propria ipotesi.
            ws.cell(row=riga, column=19, value=f'=IF(N($P{riga})>0,$Q{riga}/$P{riga},"")').number_format = S.EURO
            ws.cell(
                row=riga, column=22,
                value=f'=IFERROR(IF(AND(N($T{riga})>0,N($U{riga})>0),$S{riga}/AVERAGE($T{riga},$U{riga})-1,""),"")',
            ).number_format = S.PERC
            ws.cell(
                row=riga, column=29,
                value=f'=IFERROR(IF(N($Q{riga})>0,$AB{riga}*12/$Q{riga},""),"")',
            ).number_format = S.PERC
            stato.add(ws.cell(row=riga, column=3))
            nuova.add(ws.cell(row=riga, column=14))
            uso.add(ws.cell(row=riga, column=13))
            for col in range(1, TOTALE + 1):
                ws.cell(row=riga, column=col).border = S.BORDO
                if col in CALCOLATE:
                    ws.cell(row=riga, column=col).fill = S.FILL_CALCOLO
                elif riga >= prima + len(esempi):
                    ws.cell(row=riga, column=col).fill = S.FILL_INPUT

        ultima = prima + 199
        self.riga_annunci = prima
        ws.auto_filter.ref = f"A{prima-1}:{get_column_letter(TOTALE)}{ultima}"
        ws.freeze_panes = ws.cell(row=prima, column=8)
        # Sopra la quotazione di zona il colore vira al rosso, sotto al verde.
        ws.conditional_formatting.add(
            f"V{prima}:V{ultima}",
            ColorScaleRule(start_type="min", start_color="C6E0B4", mid_type="num", mid_value=0, mid_color="FFF2CC", end_type="max", end_color="F8CBAD"),
        )
        ws.conditional_formatting.add(
            f"AC{prima}:AC{ultima}",
            ColorScaleRule(start_type="min", start_color="F8CBAD", end_type="max", end_color="C6E0B4"),
        )

    # ------------------------------------------------------ confronto immobili
    def foglio_confronto_immobili(self) -> None:
        """Applica il modello a ogni riga del registro annunci, una per riga.

        Il resto del workbook valuta un immobile alla volta, in profondita'. Questo
        foglio fa il movimento opposto: prende gli annunci gia' raccolti e li mette
        in fila con le stesse regole, per rispondere alla domanda che viene prima,
        cioe' quale dei candidati meriti la valutazione approfondita.

        Le colonne intermedie esistono apposta e non vanno compattate: ogni formula
        legge la colonna precedente invece di ricalcolare tutto da capo, il che
        rende ciascuna cella leggibile e ispezionabile quando un numero sorprende.
        """
        ws = self.wb.create_sheet("Confronto immobili")
        ws.sheet_view.showGridLines = False
        S.larghezze_colonne(ws, {"A": 34, "B": 18, "C": 56})
        r = S.titolo(
            ws,
            1,
            "Confronto fra gli immobili in valutazione",
            "Una riga per annuncio, alimentata dal foglio Annunci. Il prezzo usato e' l'obiettivo se compilato, altrimenti il richiesto.",
        )

        r = S.sezione(ws, r, "Assunzioni comuni a tutti gli immobili")
        riga_ltv = r
        r = S.campo(ws, r, "Loan to value applicato a ogni immobile", 0.75, S.PERC, input_utente=True, nota="Serve a confrontare a parita' di leva. Zero per confrontare gli acquisti in contanti.")
        self.nome("ltv_conf", ws, f"B{riga_ltv}")
        riga_aliq = r
        r = S.campo(ws, r, "Aliquota sul canone", "=ced_libero", S.PERC, nota="Predefinita alla cedolare secca a canone libero. Si puo' sovrascrivere con 10% per il concordato o con l'aliquota marginale per il regime ordinario.", input_utente=True)
        self.nome("aliquota_conf", ws, f"B{riga_aliq}")
        r = S.nota_riga(ws, r, "Tutto il resto arriva dagli altri fogli: tasso e durata dal foglio Mutuo, sfitto, morosita', manutenzione, assicurazione e aliquota IMU dal foglio Locazione, provvigione, notaio e altri costi dal foglio Immobile, soglia di rendimento dal foglio Scenari.")
        r = S.nota_riga(ws, r, "Un'assunzione va dichiarata perche' non e' innocua: il regime di acquisto, cioe' prima casa oppure no, venditore privato oppure impresa con IVA, e opzione prezzo-valore, e' quello impostato nel foglio Immobile e viene applicato a tutti gli immobili della lista. Se si confrontano un usato da privato e un nuovo da costruttore, il confronto delle imposte non e' valido e vanno valutati separatamente.")
        r += 1

        intest = [
            "ID", "Comune", "Mq", "Prezzo", "Prezzo al mq", "Rendita", "Canone annuo",
            "Spese cond.", "Imposte acq.", "Mutuo", "Costi accessori", "Costo totale",
            "Esborso", "Ricavo effettivo", "Costi operativi", "NOI", "Imposta canone",
            "Utile netto", "Rata annua", "Cash flow", "Rend. lordo", "Rend. netto",
            "Cap rate", "Cash on cash", "DSCR", "Scarto su OMI", "Esito",
        ]
        larghezze = [12, 20, 8, 14, 12, 12, 14, 12, 14, 14, 16, 14, 14, 16, 16, 14, 14,
                     14, 14, 14, 12, 12, 12, 12, 10, 14, 16]
        r = S.intestazioni(ws, r, intest, larghezze)
        prima = r
        origine = self.riga_annunci

        for indice in range(60):
            s = origine + indice          # riga corrispondente nel foglio Annunci
            vuoto = f'$A{r}=""'
            ws.cell(row=r, column=1, value=f"=IF(Annunci!$A{s}=\"\",\"\",Annunci!$A{s})")
            ws.cell(row=r, column=2, value=f'=IF({vuoto},"",Annunci!$H{s})')
            ws.cell(row=r, column=3, value=f'=IF({vuoto},"",Annunci!$P{s})').number_format = S.NUMERO
            ws.cell(row=r, column=4, value=f'=IF({vuoto},"",IF(N(Annunci!$R{s})>0,Annunci!$R{s},Annunci!$Q{s}))').number_format = S.EURO
            ws.cell(row=r, column=5, value=f'=IF(OR({vuoto},N($C{r})=0),"",$D{r}/$C{r})').number_format = S.EURO
            ws.cell(row=r, column=6, value=f'=IF({vuoto},"",Annunci!$W{s})').number_format = S.EURO_DEC
            ws.cell(row=r, column=7, value=f'=IF({vuoto},"",Annunci!$AB{s}*12)').number_format = S.EURO
            ws.cell(row=r, column=8, value=f'=IF({vuoto},"",Annunci!$AA{s})').number_format = S.EURO
            ws.cell(
                row=r, column=9,
                value=(
                    f'=IF({vuoto},"",IF(da_impresa="SI",'
                    f'$D{r}*IF(agevolata="SI",iva_prima,IF(di_lusso="SI",iva_lusso,iva_ord))+3*fisso_impresa,'
                    f'MAX(IF(AND(usa_prezzo_valore="SI",$F{r}>0),$F{r}*riv_rendita*IF(agevolata="SI",molt_prima,molt_ord),$D{r})'
                    f'*IF(agevolata="SI",reg_prima,reg_ord),reg_min)+ipo_priv+cat_priv))'
                ),
            ).number_format = S.EURO
            ws.cell(row=r, column=10, value=f'=IF({vuoto},"",$D{r}*ltv_conf)').number_format = S.EURO
            ws.cell(
                row=r, column=11,
                value=(
                    f'=IF({vuoto},"",$I{r}+$D{r}*provv_pct*(1+iva_provv)+notaio_cv+altri_costi'
                    f'+IF($J{r}>0,$J{r}*IF(agevolata="SI",sost_prima,sost_ord)+istruttoria+perizia+notaio_mutuo,0))'
                ),
            ).number_format = S.EURO
            ws.cell(row=r, column=12, value=f'=IF({vuoto},"",$D{r}+$K{r})').number_format = S.EURO
            ws.cell(row=r, column=13, value=f'=IF({vuoto},"",$L{r}-$J{r})').number_format = S.EURO
            ws.cell(row=r, column=14, value=f'=IF({vuoto},"",($G{r}-Annunci!$AB{s}*mesi_sfitto)*(1-morosita_pct))').number_format = S.EURO
            ws.cell(
                row=r, column=15,
                value=(
                    f'=IF({vuoto},"",$H{r}*quota_condominio+$D{r}*manut_pct+assicurazione'
                    f'+$F{r}*riv_rendita*imu_molt*imu_aliquota+$D{r}*ristrutt_pct/ristrutt_anni)'
                ),
            ).number_format = S.EURO
            ws.cell(row=r, column=16, value=f'=IF({vuoto},"",$N{r}-$O{r})').number_format = S.EURO
            ws.cell(row=r, column=17, value=f'=IF({vuoto},"",$N{r}*aliquota_conf)').number_format = S.EURO
            ws.cell(row=r, column=18, value=f'=IF({vuoto},"",$P{r}-$Q{r})').number_format = S.EURO
            ws.cell(row=r, column=19, value=f'=IF({vuoto},"",IF($J{r}>0,PMT(tasso/12,durata*12,-$J{r})*12,0))').number_format = S.EURO
            ws.cell(row=r, column=20, value=f'=IF({vuoto},"",$R{r}-$S{r})').number_format = S.EURO
            ws.cell(row=r, column=21, value=f'=IF(OR({vuoto},N($D{r})=0),"",$G{r}/$D{r})').number_format = S.PERC
            ws.cell(row=r, column=22, value=f'=IF(OR({vuoto},N($L{r})=0),"",$R{r}/$L{r})').number_format = S.PERC
            ws.cell(row=r, column=23, value=f'=IF(OR({vuoto},N($L{r})=0),"",$P{r}/$L{r})').number_format = S.PERC
            ws.cell(row=r, column=24, value=f'=IF(OR({vuoto},N($M{r})=0),"",$T{r}/$M{r})').number_format = S.PERC
            ws.cell(row=r, column=25, value=f'=IF(OR({vuoto},N($S{r})=0),"",$P{r}/$S{r})').number_format = S.NUMERO_DEC
            ws.cell(row=r, column=26, value=f'=IF({vuoto},"",Annunci!$V{s})').number_format = S.PERC
            ws.cell(
                row=r, column=27,
                value=(
                    f'=IF({vuoto},"",IF(NOT(ISNUMBER($V{r})),"",'
                    f'IF($V{r}>=rend_obiettivo,"sopra soglia","sotto soglia")))'
                ),
            )
            for col in range(1, 28):
                cella = ws.cell(row=r, column=col)
                cella.border = S.BORDO
                cella.fill = S.FILL_CALCOLO
            r += 1

        ultima = r - 1
        ws.freeze_panes = ws.cell(row=prima, column=3)
        ws.auto_filter.ref = f"A{prima-1}:AA{ultima}"
        for colonna, verso in (("V", "alto"), ("X", "alto"), ("T", "alto")):
            ws.conditional_formatting.add(
                f"{colonna}{prima}:{colonna}{ultima}",
                ColorScaleRule(start_type="min", start_color="F8CBAD", end_type="max", end_color="C6E0B4"),
            )
        ws.conditional_formatting.add(
            f"Z{prima}:Z{ultima}",
            ColorScaleRule(start_type="min", start_color="C6E0B4", mid_type="num", mid_value=0, mid_color="FFF2CC", end_type="max", end_color="F8CBAD"),
        )
        ws.conditional_formatting.add(
            f"AA{prima}:AA{ultima}",
            CellIsRule(operator="equal", formula=['"sopra soglia"'], fill=S.FILL_RISULTATO),
        )
        ws.conditional_formatting.add(
            f"AA{prima}:AA{ultima}",
            CellIsRule(operator="equal", formula=['"sotto soglia"'], fill=S.FILL_ATTENZIONE),
        )

        r += 1
        for testo in [
            "Le righe si popolano da sole man mano che il foglio Annunci si riempie: restano vuote finche' non c'e' un identificativo nella riga corrispondente. Gli annunci arrivano anche dalla riga di comando, con `python tools/valuta.py excel --con-annunci`.",
            "La colonna del cash flow e' quella che separa le operazioni sostenibili da quelle che assorbono cassa ogni mese, e non coincide quasi mai con l'ordine del rendimento lordo. Il debt service coverage ratio sotto uno dice la stessa cosa in forma di soglia.",
            "Questo foglio serve a scegliere quale immobile approfondire, non a decidere. Per l'immobile che sopravvive alla selezione si compila il foglio Immobile con i suoi dati reali, si verifica l'aliquota IMU nella delibera del Comune e le spese nel consuntivo condominiale, e si legge il foglio Metriche.",
        ]:
            r = S.nota_riga(ws, r, testo, 6)

    # ------------------------------------------------------------------- fonti
    def foglio_fonti(self) -> None:
        ws = self.wb.create_sheet("Fonti")
        ws.sheet_view.showGridLines = False
        r = S.titolo(
            ws,
            1,
            "Fonti",
            "Ogni numero del modello risale a una fonte verificabile. Le fonti istituzionali prevalgono sempre su quelle divulgative: queste ultime servono a orientarsi, non a decidere.",
            4,
        )
        r = S.intestazioni(ws, r, ["Categoria", "Fonte", "Cosa fornisce", "Link"], [22, 46, 62, 70])
        prima = r

        fonti = [
            ("Istituzionale", "Agenzia delle Entrate, l'acquisto della casa e le imposte", "Aliquote di registro, IVA, ipotecaria e catastale; regola prezzo-valore e moltiplicatori.", P.FONTI["imposte_acquisto"]),
            ("Istituzionale", "Agenzia delle Entrate, agevolazioni prima casa", "Requisiti, termini, decadenza e credito d'imposta per riacquisto.", P.FONTI["agevolazioni_prima_casa"]),
            ("Istituzionale", "Agenzia delle Entrate, locazioni brevi e cedolare secca", "Aliquote 21 e 26 per cento, soglia di due unita' dal 2026, obblighi degli intermediari. Guida aggiornata ad aprile 2026.", P.FONTI["locazioni_brevi"]),
            ("Istituzionale", "Agenzia delle Entrate, registrazione dei contratti di locazione", "Imposta di registro sui canoni, minimi e riduzione per il canone concordato.", P.FONTI["registrazione_locazione"]),
            ("Istituzionale", "Osservatorio del mercato immobiliare, quotazioni", "Prezzi al metro quadro di compravendita e locazione per zona omogenea, semestrali e gratuiti.", P.FONTI["quotazioni_omi"]),
            ("Dati aperti", "ondata, quotazioni immobiliari Agenzia Entrate", "Le stesse quotazioni OMI ripubblicate in CSV pronti all'uso, senza registrazione ai servizi telematici.", P.FONTI["omi_open_data"]),
            ("Istituzionale", "Banca d'Italia, guida al mutuo ipotecario", "Diritti del cliente in forma ufficiale: PIES, sette giorni di riflessione sull'offerta vincolante, portabilita' gratuita, verifica del tasso d'usura, liberta' di scelta della polizza, accesso alla Centrale dei Rischi.", "https://www.bancaditalia.it/pubblicazioni/guide-bi/guida-mutuo/"),
            ("Istituzionale", "Banca centrale europea, portale dati", "Tassi bancari armonizzati sulle nuove erogazioni per acquisto abitazione in Italia, ed Euribor. Sono la media di quello che le banche hanno davvero applicato, non un tasso pubblicitario. Interrogabili con python tools/valuta.py tassi.", "https://data.ecb.europa.eu/"),
            ("Istituzionale", "Consap, fondo di garanzia per la prima casa", "Garanzia statale fino all'ottanta per cento per under 36 con ISEE entro quarantamila euro, prorogata al 31 dicembre 2027.", P.FONTI["fondo_consap"]),
            ("Tecnica", "Carlo Pagliai, conformita' catastale e urbanistica nelle compravendite", "Differenza fra le due conformita', obblighi di legge, nullita' dell'atto e verifiche da fare.", P.FONTI["conformita_pagliai"]),
            ("Tecnica", "Carlo Pagliai, tolleranze costruttive dopo il Salva Casa", "Nuovo perimetro dell'articolo 34-bis del DPR 380/2001 e valore probatorio delle dichiarazioni del tecnico.", P.FONTI["salva_casa_tolleranze"]),
            ("Tecnica", "Carlo Pagliai, canale Telegram", "Aggiornamenti quotidiani su giurisprudenza urbanistica e commerciabilita' degli immobili.", "https://t.me/pagliaicarlo"),
            ("Notarile", "Tutele nell'acquisto di immobili da costruire", "Fideiussione obbligatoria e polizza decennale postuma del decreto legislativo 122/2005.", P.FONTI["immobili_da_costruire"]),
            ("Fiscale", "Fisco e Tasse, cedolare secca affitti brevi dal 2026", "Soglia di due appartamenti e conferma delle aliquote 21 e 26 per cento.", P.FONTI["cedolare_2026"]),
            ("Fiscale", "Fisco e Tasse, aliquote IRPEF 2026", "Scaglioni 23, 33 e 43 per cento dopo la riduzione della seconda aliquota.", P.FONTI["irpef_2026"]),
            ("Fiscale", "Fisco e Tasse, prima casa e termine di due anni", "Estensione da uno a due anni del termine per rivendere la precedente abitazione agevolata.", P.FONTI["prima_casa_due_anni"]),
            ("Fiscale", "BibLus, plusvalenza immobiliare infraquinquennale", "Perimetro dell'articolo 67 del TUIR, imposta sostitutiva del 26 per cento e finestra decennale post superbonus.", P.FONTI["plusvalenza"]),
            ("Fiscale", "MutuiOnline, detrazione degli interessi del mutuo prima casa 2026", "Massimale di quattromila euro, aliquota del diciannove per cento, requisito di residenza entro dodici mesi.", P.FONTI["detrazione_interessi"]),
            ("Divulgativa", "Paolo Coletti, foglio rendita immobiliare", "Impostazione del rendimento immobiliare su quarant'anni con sfitto, ristrutturazione periodica e confronto con l'indice azionario. File del 17 febbraio 2022: il metodo resta valido, le aliquote no.", P.FONTI["coletti_rendita"]),
            ("Divulgativa", "Paolo Coletti, foglio acquisto casa o affitto", "Confronto fra comprare e affittare con ammortamento dei costi di acquisto sugli anni di permanenza. File del 17 febbraio 2022.", P.FONTI["coletti_casa_o_affitto"]),
            ("Divulgativa", "Paolo Coletti, foglio mutuo con investimento", "Mutuo confrontato con l'investimento della liquidita' in BTP o azioni, con detrazione degli interessi modellata anno per anno. File del 29 settembre 2025.", P.FONTI["coletti_mutuo_investimento"]),
            ("Divulgativa", "Paolo Coletti, indice dei materiali", "Elenco completo dei fogli di calcolo e dei notebook pubblicati.", "https://www.paolocoletti.com/youtube/"),
            ("Divulgativa", "Bite Salad, gestione di una casa in affitto con Excel", "Modello di tracciamento dei movimenti reali di un immobile locato e calcolo del ROI anno per anno, rivisto dallo stesso Coletti.", "https://www.bitesalad.com/2024/12/affitto-excel-coletti/"),
            ("Community", "Reddit r/ItaliaPersonalFinance, comprare casa for dummies", "Guida della community ai passaggi dell'acquisto.", "https://www.reddit.com/r/ItaliaPersonalFinance/comments/17i7wfz/comprare_casa_for_dummies/"),
            ("Community", "Reddit r/ItaliaPersonalFinance, perche' comprare per affittare e' un pessimo investimento", "Tesi critica sul rendimento reale della locazione residenziale.", "https://www.reddit.com/r/ItaliaPersonalFinance/comments/1k9dfbv/"),
            ("Community", "Reddit r/ItaliaPersonalFinance, acquistare per affitti brevi non e' investire", "Distinzione fra investimento e attivita' imprenditoriale nella locazione turistica.", "https://www.reddit.com/r/ItaliaPersonalFinance/comments/1r7zufg/acquistando_un_immobile_per_affitti_brevi_non/"),
            ("Community", "Reddit r/ItaliaPersonalFinance, il simulatore mutui piu' preciso del web", "Confronto fra simulatori di ammortamento.", "https://www.reddit.com/r/ItaliaPersonalFinance/comments/1jg5mp8/"),
            ("Community", "Wiki open source di Italia Personal Finance", "Raccolta di contenuti e fogli di calcolo della community italiana.", "https://github.com/emish89/italiapersonalfinance"),
            ("Software", "Sossoldi", "Applicazione open source di tracciamento del patrimonio netto, utile a inquadrare l'immobile dentro il patrimonio complessivo.", "https://github.com/napitek/sossoldi"),
            ("Software", "ai-realestate-claude", "Motore di analisi immobiliare con punteggio della proprieta', flussi di cassa e rapporti in PDF. Mercato statunitense.", "https://github.com/zubair-trabzada/ai-realestate-claude"),
            ("Software", "RealEstateInvestmentCal", "Calcolatore in Streamlit con ROI annuo e TIR con e senza leva finanziaria.", "https://github.com/moonnstarr/RealEstateInvestmentCal"),
            ("Software", "rental-property-calculator", "Analisi di annunci con cash flow, cap rate e cash on cash.", "https://github.com/gmlesher/rental-property-calculator"),
            ("Software", "Rental Property Deal Analyzer", "Oltre venti metriche e punteggio del contratto, con estrazione dei dati dall'annuncio.", "https://github.com/berkcankapusuzoglu/Rental-Property-Deal-Analyzer"),
            ("Software", "awesome-real-estate-investing", "Raccolta curata di strumenti, piattaforme e progetti per l'investimento immobiliare.", "https://github.com/Deal-Scale/awesome-real-estate-investing"),
            ("Software", "awesome-real-estate", "Seconda raccolta curata, orientata ai progetti open source del settore.", "https://github.com/etewiah/awesome-real-estate"),
            ("Software", "Idealista Immobiliare Scraper", "Estrazione di annunci dai due portali italiani. Da usare solo nel rispetto dei termini di servizio e del file robots.txt.", "https://github.com/martapanc/Idealista-Immobiliare-Scraper"),
            ("Software", "immobiscraper", "Scraper per immobiliare.it che restituisce un DataFrame.", "https://github.com/Stemanz/immobiscraper"),
            ("Software", "ammortamento", "Generatore di piani di ammortamento alla francese in Python.", "https://github.com/ferromauro/ammortamento"),
        ]
        for categoria, nome, cosa, link in fonti:
            ws.cell(row=r, column=1, value=categoria).alignment = S.SINISTRA
            c = ws.cell(row=r, column=2, value=nome)
            c.alignment = S.SINISTRA
            c.font = S.ETICHETTA_BOLD
            ws.cell(row=r, column=3, value=cosa).alignment = S.SINISTRA
            l = ws.cell(row=r, column=4, value=link)
            l.hyperlink = link
            l.font = S.LINK
            l.alignment = S.SINISTRA
            for col in range(1, 5):
                ws.cell(row=r, column=col).border = S.BORDO
            ws.row_dimensions[r].height = 32
            r += 1
        ws.auto_filter.ref = f"A{prima-1}:D{r-1}"
        ws.freeze_panes = ws.cell(row=prima, column=1)


def genera(percorso: str) -> str:
    """Genera il workbook e restituisce il percorso scritto."""
    c = Costruttore()
    c.costruisci()
    c.salva(percorso)
    return percorso
