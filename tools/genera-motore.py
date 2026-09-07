#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""genera-motore - produce i parametri TypeScript e i vettori di riscontro dal motore Python.

Il motore di calcolo esiste in Python ed è verificato da settantasette test; l'applicazione web
ne ha bisogno nel browser, e la via scelta con ADR-024 è riscriverlo in TypeScript tenendo quello
Python come implementazione di riferimento. Una seconda implementazione di un modello finanziario
è il modo classico in cui due parti dello stesso prodotto cominciano a dire numeri diversi, quindi
la riscrittura è accettabile solo con il presidio che questo strumento costruisce, e che ha due
pezzi distinti.

Il primo pezzo sono i parametri. Non si trascrivono a mano: si leggono dalle dataclass congelate di
`parametri.py` e si emettono in TypeScript, così l'aliquota che cambia con la legge di bilancio si
aggiorna in un posto solo e l'altro lato la eredita. Un'aliquota copiata a mano è il primo posto in
cui le due implementazioni divergono, e la divergenza non si vede: produce un numero plausibile.

Il secondo pezzo sono i vettori di riscontro. Il motore Python viene eseguito su un campione
sistematico di casi, e per ciascuno si registra l'intero esito. La suite TypeScript ricalcola gli
stessi casi e confronta ogni valore entro la tolleranza dichiarata. Il campione non è casuale: è il
prodotto cartesiano di alcune scelte discrete che cambiano ramo nel codice, cioè venditore privato o
impresa, agevolazione o no, prezzo-valore attivo o no, categoria ordinaria o di lusso, regime di
locazione, presenza del mutuo, più i casi limite che nella pratica rompono le formule, cioè rendita
a zero, tasso a zero, durata a zero, canone a zero, mutuo pari all'intero prezzo.

La tolleranza è dichiarata qui e non dopo aver visto gli scarti, che è la sola sequenza onesta:
1e-9 in termini relativi sui valori di modulo maggiore di uno, 1e-9 in termini assoluti sotto. Non è
una tolleranza di comodo: le due implementazioni eseguono le stesse operazioni nello stesso ordine su
numeri in doppia precisione, quindi devono coincidere fino all'ultimo bit significativo, e uno scarto
maggiore significa che una delle due fa qualcosa di diverso.

Uso:

    python tools/genera-motore.py            scrive parametri e vettori
    python tools/genera-motore.py --check    verifica che siano aggiornati, senza scrivere

Con `--check` esce con codice diverso da zero se i file su disco non corrispondono a quelli che il
motore Python produrrebbe adesso: è il controllo da eseguire dopo aver toccato `parametri.py` o
`calcoli.py`, perché in quel momento i vettori sul disco sono scaduti e la suite TypeScript
starebbe verificando un modello vecchio.
"""
import dataclasses
import io
import json
import math
import os
import sys
from itertools import product
from pathlib import Path

RADICE = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(RADICE / "src"))

from immobiliare import calcoli as C  # noqa: E402
from immobiliare import parametri as P  # noqa: E402

DESTINAZIONE_PARAMETRI = Path("app/src/motore/parametri.generati.ts")
DESTINAZIONE_VETTORI = Path("app/test/vettori.generati.json")

TOLLERANZA_RELATIVA = 1e-9
TOLLERANZA_ASSOLUTA = 1e-9

# Le dataclass di parametri.py che il motore usa. FONDO_CONSAP, PRIMA_CASA e RISALITE_EURIBOR non
# entrano perché nessuna funzione di calcolo le legge: le usano il generatore del workbook e la
# riga di comando, che restano in Python.
GRUPPI = {
    "imposteTrasferimento": "IMPOSTE_TRASFERIMENTO",
    "costi": "COSTI",
    "mutuo": "MUTUO",
    "locazione": "LOCAZIONE",
    "irpef": "IRPEF",
    "imu": "IMU",
    "plusvalenza": "PLUSVALENZA",
    "finanza": "FINANZA",
}


def _cammello(nome: str) -> str:
    """Da nome_con_trattini_bassi a nomeInCammello, che è la convenzione TypeScript."""
    pezzi = nome.split("_")
    return pezzi[0] + "".join(p.capitalize() for p in pezzi[1:])


def _valore_ts(v) -> str:
    if isinstance(v, bool):
        return "true" if v else "false"
    if isinstance(v, float) and math.isinf(v):
        # repr in Python scrive inf, che in TypeScript non esiste: la soglia piu' alta
        # degli scaglioni IRPEF e' proprio questa, quindi il caso non e' teorico.
        return "Infinity" if v > 0 else "-Infinity"
    if isinstance(v, float) and math.isnan(v):
        return "NaN"
    if isinstance(v, (int, float)):
        return repr(v)
    if isinstance(v, str):
        return json.dumps(v, ensure_ascii=False)
    if isinstance(v, (tuple, list)):
        return "[" + ", ".join(_valore_ts(x) for x in v) + "]"
    raise TypeError(f"tipo non emettibile in TypeScript: {type(v)}")


def _tipo_ts(v) -> str:
    if isinstance(v, bool):
        return "boolean"
    if isinstance(v, (int, float)):
        return "number"
    if isinstance(v, str):
        return "string"
    if isinstance(v, (tuple, list)):
        if not v:
            return "never[]"
        interno = sorted({_tipo_ts(x) for x in v})
        # Un tipo composto va fra parentesi prima del suffisso, altrimenti
        # "readonly readonly number[][]" non compila.
        if len(interno) == 1 and " " not in interno[0]:
            return "readonly " + interno[0] + "[]"
        return "readonly (" + " | ".join(interno) + ")[]"
    raise TypeError(f"tipo non descrivibile: {type(v)}")


def genera_parametri() -> str:
    righe = [
        "// Generato da tools/genera-motore.py: non modificare a mano.",
        "//",
        "// I valori vengono da src/immobiliare/parametri.py, che resta la sola fonte di verita'.",
        "// Toccare questo file significa creare una seconda verita' fiscale, e la divergenza fra le",
        "// due non produce un errore: produce un numero plausibile e sbagliato su uno dei due lati.",
        f"// Revisione dei parametri: {P.REVISIONE}. Anno d'imposta: {P.ANNO_IMPOSTA}.",
        "",
        f"export const REVISIONE = {json.dumps(str(P.REVISIONE))};",
        f"export const ANNO_IMPOSTA = {P.ANNO_IMPOSTA};",
        "",
    ]
    for nome_ts, nome_py in GRUPPI.items():
        istanza = getattr(P, nome_py)
        righe.append(f"export const {nome_ts} = {{")
        for campo in dataclasses.fields(istanza):
            valore = getattr(istanza, campo.name)
            righe.append(f"  {_cammello(campo.name)}: {_valore_ts(valore)} as {_tipo_ts(valore)},")
        righe.append("} as const;")
        righe.append("")
    return "\n".join(righe)


# ---------------------------------------------------------------------------
# I casi: prodotto cartesiano delle scelte che cambiano ramo, più i limiti
# ---------------------------------------------------------------------------

def _casi_sistematici():
    for (venditore_impresa, prima_casa, prezzo_valore, categoria, regime, mutuo) in product(
        (False, True),
        (True, False),
        (True, False),
        ("A/2", "A/1"),
        ("cedolare_libero", "cedolare_concordato", "irpef_ordinario", "irpef_concordato",
         "breve_prima_unita", "breve_altre_unita"),
        (0.0, 96_000.0),
    ):
        yield {
            "immobile": {
                "prezzo": 120_000.0,
                "rendita_catastale": 450.0,
                "categoria": categoria,
                "superficie_mq": 55.0,
                "comune": "Civitanova Marche",
                "nuova_costruzione": False,
                "venditore_impresa": venditore_impresa,
            },
            "acquirente": {
                "prima_casa": prima_casa,
                "quota": 1.0,
                "residenza_gia_nel_comune": True,
                "eta": 31,
                "isee": 0.0,
                "reddito_imponibile_irpef": 35_000.0,
                "possiede_altra_prima_casa": False,
                "prezzo_valore": prezzo_valore,
            },
            "finanziamento": {
                "importo": mutuo,
                "tasso_annuo": 0.032,
                "durata_anni": 25,
                "tipo": "fisso",
                "spread": 0.0,
                "istruttoria": 500.0,
                "perizia": 300.0,
                "polizza_annua": 180.0,
                "notaio_atto_mutuo": 1_000.0,
            },
            "gestione": {
                "canone_mensile": 500.0,
                "regime": regime,
                "mesi_sfitto_annui": 1.0,
                "morosita": 0.03,
                "condominio_annuo": 1_200.0,
                "quota_condominio_a_carico_proprietario": 0.4,
                "manutenzione_su_valore": 0.01,
                "assicurazione_annua": 200.0,
                "aliquota_imu": 0.0086,
                "gestione_su_canone": 0.0,
                "ricavi_lordi_brevi_annui": 9_000.0,
                "costi_variabili_brevi": 0.15,
            },
            "orizzonte_anni": 25,
            "reddito_altro": 35_000.0,
            "rivalutazione_immobile": 0.02,
            "canone_alternativo_mensile": 550.0,
            "inflazione": 0.02,
            "indicizzazione_canone": 0.0,
        }


def _casi_limite():
    """I casi che nella pratica rompono le formule, uno per volta."""
    base = next(iter(_casi_sistematici()))

    def variante(**modifiche):
        import copy
        c = copy.deepcopy(base)
        for percorso, valore in modifiche.items():
            gruppo, _, campo = percorso.partition(".")
            if campo:
                c[gruppo][campo] = valore
            else:
                c[gruppo] = valore
        return c

    yield variante(**{"immobile.rendita_catastale": 0.0})
    yield variante(**{"finanziamento.tasso_annuo": 0.0, "finanziamento.importo": 96_000.0})
    yield variante(**{"finanziamento.durata_anni": 0, "finanziamento.importo": 96_000.0})
    yield variante(**{"finanziamento.importo": 120_000.0})
    yield variante(**{"gestione.canone_mensile": 0.0, "gestione.ricavi_lordi_brevi_annui": 0.0})
    yield variante(**{"gestione.mesi_sfitto_annui": 12.0})
    yield variante(**{"gestione.morosita": 1.0})
    yield variante(**{"immobile.prezzo": 1.0})
    yield variante(**{"reddito_altro": 0.0, "gestione.regime": "irpef_ordinario"})
    yield variante(**{"reddito_altro": 250_000.0, "gestione.regime": "irpef_ordinario"})
    yield variante(**{"orizzonte_anni": 1})
    yield variante(**{"orizzonte_anni": 40})
    yield variante(**{"inflazione": 0.0})
    yield variante(**{"inflazione": 0.10, "indicizzazione_canone": 0.10})
    yield variante(**{"gestione.aliquota_imu": 0.0})
    yield variante(**{"gestione.gestione_su_canone": 0.10})
    yield variante(**{"rivalutazione_immobile": 0.0})
    yield variante(**{"rivalutazione_immobile": 0.05})
    yield variante(**{"canone_alternativo_mensile": 0.0})


def _numero(x):
    """Serializza un numero rendendo espliciti gli infiniti, che JSON non ammette."""
    if isinstance(x, float) and math.isinf(x):
        return "Infinity" if x > 0 else "-Infinity"
    return x


def calcola(caso) -> dict:
    """Esegue il motore Python sul caso e restituisce l'intero esito, voce per voce."""
    immobile = C.Immobile(**caso["immobile"])
    acquirente = C.Acquirente(**caso["acquirente"])
    finanziamento = C.Finanziamento(**caso["finanziamento"])
    gestione = C.Gestione(**caso["gestione"])
    orizzonte = caso["orizzonte_anni"]
    reddito_altro = caso["reddito_altro"]

    imposte = C.imposte_acquisto(immobile, acquirente)
    costo = C.costo_operazione(immobile, acquirente, finanziamento)
    piano = C.piano_ammortamento(finanziamento.importo, finanziamento.tasso_annuo, finanziamento.durata_anni)
    interessi = C.interessi_per_anno(piano)
    rata_mensile = C.rata_francese(finanziamento.importo, finanziamento.tasso_annuo, finanziamento.durata_anni)
    conto = C.conto_economico(immobile, gestione, reddito_altro)
    met = C.metriche(costo, conto, rata_mensile * 12)

    rate_pagate = min(orizzonte * 12, len(piano))
    debito_residuo = piano[rate_pagate - 1].debito_residuo if rate_pagate else finanziamento.importo
    rivalutazione = caso["rivalutazione_immobile"]
    valore_finale = immobile.prezzo * (1 + rivalutazione) ** orizzonte

    flussi = [-costo.esborso_iniziale] + [met.cash_flow_annuo] * orizzonte
    flussi[-1] += valore_finale - debito_residuo
    tir = C.tir(flussi)

    inflazione = caso["inflazione"]
    eff = C.effetto_inflazione(
        inflazione=inflazione,
        rendimento_netto_nominale=met.rendimento_netto,
        tir_nominale=tir,
        prezzo=immobile.prezzo,
        rivalutazione_immobile=rivalutazione,
        debito_residuo_nominale=debito_residuo,
        rata_annua=rata_mensile * 12,
        canone_annuo=conto.canone_effettivo,
        indicizzazione_canone=caso["indicizzazione_canone"],
        orizzonte_anni=orizzonte,
        tasso_sconto=P.FINANZA.rendimento_portafoglio_lordo,
    )
    plus, imposta_plus = C.plusvalenza_su_rivendita(valore_finale, costo.costo_totale, orizzonte)
    confronto = C.confronto_compra_o_affitta(
        costo, finanziamento, caso["canone_alternativo_mensile"], orizzonte,
        rivalutazione_immobile=rivalutazione,
    )

    return {
        "imposte": {
            "imponibile": imposte.imponibile,
            "iva": imposte.iva,
            "registro": imposte.registro,
            "ipotecaria": imposte.ipotecaria,
            "catastale": imposte.catastale,
            "totale": imposte.totale,
            "regime": imposte.regime,
        },
        "agevolazioneApplicabile": C.agevolazione_applicabile(immobile, acquirente),
        "baseImponibileRegistro": C.base_imponibile_registro(immobile, acquirente),
        "valoreCatastale": C.valore_catastale(immobile.rendita_catastale, C.agevolazione_applicabile(immobile, acquirente)),
        "costo": {
            "provvigione": costo.provvigione,
            "notaioCompravendita": costo.notaio_compravendita,
            "notaioMutuo": costo.notaio_mutuo,
            "sostitutivaMutuo": costo.sostitutiva_mutuo,
            "istruttoria": costo.istruttoria,
            "perizia": costo.perizia,
            "costiAccessori": costo.costi_accessori,
            "costoTotale": costo.costo_totale,
            "esborsoIniziale": costo.esborso_iniziale,
            "incidenzaCosti": costo.incidenza_costi,
        },
        "mutuo": {
            "rataMensile": rata_mensile,
            "rateTotali": len(piano),
            "interessiPrimoAnno": interessi.get(1, 0.0),
            "interessiTotali": sum(r.quota_interessi for r in piano),
            "debitoResiduoAOrizzonte": debito_residuo,
            "detrazioneInteressiPrimoAnno": C.detrazione_interessi(interessi.get(1, 0.0)),
            "detrazioneSeLocato": C.detrazione_interessi(interessi.get(1, 0.0), abitazione_principale=False),
            "taegApprossimato": C.taeg_approssimato(
                finanziamento.importo, finanziamento.tasso_annuo, finanziamento.durata_anni,
                costo.sostitutiva_mutuo + costo.istruttoria + costo.perizia, finanziamento.polizza_annua,
            ),
        },
        "conto": {
            "canonePotenziale": conto.canone_potenziale,
            "perditaSfitto": conto.perdita_sfitto,
            "perditaMorosita": conto.perdita_morosita,
            "canoneEffettivo": conto.canone_effettivo,
            "condominio": conto.condominio,
            "manutenzione": conto.manutenzione,
            "assicurazione": conto.assicurazione,
            "imu": conto.imu,
            "gestione": conto.gestione,
            "ristrutturazione": conto.ristrutturazione,
            "costiOperativi": conto.costi_operativi,
            "noi": conto.noi,
            "imposta": conto.imposta,
            "utileNetto": conto.utile_netto,
        },
        "metriche": {
            "rendimentoLordo": met.rendimento_lordo,
            "rendimentoNetto": met.rendimento_netto,
            "capRate": met.cap_rate,
            "cashOnCash": met.cash_on_cash,
            "dscr": _numero(met.dscr),
            "cashFlowAnnuo": met.cash_flow_annuo,
            "paybackAnni": _numero(met.payback_anni),
        },
        "tir": tir,
        "van": C.van(flussi, P.FINANZA.rendimento_portafoglio_lordo),
        "inflazione": {
            "rendimentoNettoReale": eff.rendimento_netto_reale,
            "erroreApprossimazione": eff.errore_approssimazione,
            "erosioneRealeCanone": eff.erosione_reale_canone,
            "rivalutazioneRealeImmobile": eff.rivalutazione_reale_immobile,
            "tirReale": eff.tir_reale,
            "valoreFinaleNominale": eff.valore_finale_nominale,
            "valoreFinaleReale": eff.valore_finale_reale,
            "debitoResiduoReale": eff.debito_residuo_reale,
            "scontoInflazioneSulDebito": eff.sconto_inflazione_sul_debito,
            "rataAnnuaRealeAFineOrizzonte": eff.rata_annua_reale_a_fine_orizzonte,
            "canonePersoPerMancataIndicizzazione": eff.canone_perso_per_mancata_indicizzazione,
        },
        "plusvalenza": {"lorda": plus, "imposta": imposta_plus},
        "confronto": {
            "patrimonioComprando": confronto.patrimonio_comprando,
            "patrimonioAffittando": confronto.patrimonio_affittando,
            "differenza": confronto.differenza,
            "convieneComprare": confronto.conviene_comprare,
        },
        "fattoreRenditaCrescente": C.fattore_rendita_crescente(0.02, 0.04, orizzonte),
        "fattoreRenditaCrescenteDegenere": C.fattore_rendita_crescente(0.04, 0.04, orizzonte),
        "irpefLorda": C.irpef_lorda(reddito_altro),
    }


def genera_vettori() -> str:
    casi = list(_casi_sistematici()) + list(_casi_limite())
    vettori = [{"n": i + 1, "ingresso": caso, "atteso": calcola(caso)} for i, caso in enumerate(casi)]
    documento = {
        "generatoDa": "tools/genera-motore.py",
        "revisioneParametri": str(P.REVISIONE),
        "tolleranzaRelativa": TOLLERANZA_RELATIVA,
        "tolleranzaAssoluta": TOLLERANZA_ASSOLUTA,
        "casi": len(vettori),
        "vettori": vettori,
    }
    return json.dumps(documento, ensure_ascii=False, indent=1) + "\n"


def main(argv) -> int:
    solo_controllo = "--check" in argv
    uscite = {
        RADICE / DESTINAZIONE_PARAMETRI: genera_parametri(),
        RADICE / DESTINAZIONE_VETTORI: genera_vettori(),
    }
    scaduti = []
    for percorso, contenuto in uscite.items():
        attuale = percorso.read_text(encoding="utf-8") if percorso.exists() else None
        if attuale == contenuto:
            continue
        scaduti.append(percorso)
        if not solo_controllo:
            percorso.parent.mkdir(parents=True, exist_ok=True)
            io.open(percorso, "w", encoding="utf-8", newline="\n").write(contenuto)

    if solo_controllo:
        for percorso in scaduti:
            print("scaduto: " + os.path.relpath(percorso, RADICE).replace(os.sep, "/"))
        print(f"{len(uscite)} file esaminati, {len(scaduti)} scaduti")
        return 1 if scaduti else 0

    for percorso in uscite:
        print("scritto: " + os.path.relpath(percorso, RADICE).replace(os.sep, "/"))
    vettori = json.loads(uscite[RADICE / DESTINAZIONE_VETTORI])
    print(f"{vettori['casi']} casi di riscontro, parametri alla revisione {vettori['revisioneParametri']}")
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
