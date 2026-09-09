# -*- coding: utf-8 -*-
"""Test della simulazione probabilistica e del tornado.

Due famiglie di prove, con scopi diversi.

La prima congela le proprietà dichiarate in ADR-023, cioè quelle che rendono la
correlazione fra le variabili di scenario una scelta verificabile invece di
un'opinione: i pesi con somma dei quadrati uno, la riduzione esatta al caso
indipendente quando la correlazione è nulla, le incertezze che non si gonfiano di
nascosto, e la correlazione risultante uguale al parametro impostato fra variabili
di verso concorde e opposta fra variabili di verso discorde.

La seconda congela l'accordo con il workbook. I numeri della classe `FOGLIO` sono
quelli che Excel ha calcolato sul caso precaricato il 9 settembre 2026, letti dal
foglio Rischio dopo un ricalcolo completo, e la prova pretende che il modulo li
riproduca entro un miliardesimo relativo. Serve a impedire che le due
implementazioni divergano in silenzio: fino a oggi la simulazione esisteva solo
nelle formule del foglio, e una sola implementazione non si può verificare se non
guardandola.

Si eseguono con `python -m pytest tests` dalla radice del progetto, oppure con
`python tests/test_rischio.py` se pytest non è installato.
"""

from __future__ import annotations

import statistics
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "src"))

from immobiliare import calcoli as C  # noqa: E402
from immobiliare import rischio as R  # noqa: E402

TOLLERANZA = 1e-9


def base_del_foglio() -> R.BaseSimulazione:
    """Il caso precaricato del workbook, cella per cella.

    I valori sono quelli che le celle con nome definito contengono dopo il ricalcolo.
    Il reddito operativo netto porta la sua ultima cifra come Excel l'ha prodotto,
    perché è il risultato di una somma e non un dato inserito: arrotondarlo qui
    introdurrebbe uno scarto nostro in una prova che serve a misurare il loro.
    """
    return R.BaseSimulazione(
        canone_mensile=500.0,
        ricavo_effettivo=5335.0,
        noi_annuo=1804.8400000000001,
        costo_totale=131556.5,
        esborso=41556.5,
        prezzo=120000.0,
        mesi_sfitto=1.0,
        morosita=0.03,
        aliquota_canone=0.21,
        tasso=0.032,
        durata_anni=25,
        mutuo_importo=90000.0,
        rivalutazione=0.02,
        orizzonte_anni=25,
        costi_vendita=0.03,
        rendimento_portafoglio=0.06,
        rendimento_obiettivo=0.04,
        condominio_annuo=1200.0,
        quota_condominio=0.4,
        manutenzione_su_valore=0.01,
        ristrutturazione_su_valore=1 / 3,
        ristrutturazione_anni=40,
    )


def incertezze_del_foglio() -> R.Incertezze:
    return R.Incertezze(
        vol_canone=0.10, vol_sfitto=1.5, vol_tasso=0.0, vol_rivalutazione=0.04,
        prob_morosita_grave=0.05, mesi_persi_morosita=12.0, correlazione=0.30,
    )


class FOGLIO:
    """Quello che Excel calcola sul caso precaricato, letto il 9 settembre 2026."""

    cash_flow = (-8764.693003943572, -4654.602145616495, -3564.109809304557)
    utile_netto = (-3530.16, 579.930858327077, 1670.4231946390153)
    rendimento = (-0.026833793845229995, 0.004408226566738071, 0.012697382452702948)
    patrimonio = (137858.7812737959, 190833.64824079606, 264508.96084880445)
    montante = (-278915.6454059084, -64291.958873127616, 48350.45527920904)
    probabilita = (1.0, 1.0, 0.0, 0.0)
    tornado = (
        ("Canone", -4971.508003943572, -4128.578003943571),
        ("Costi operativi", -4197.027003943572, -4903.059003943572),
        ("Tasso del mutuo", -4369.839354613812, -4733.835866382451),
        ("Importo del mutuo", -4026.589703549215, -5073.49630433793),
        ("Durata del mutuo", -4848.605217480326, -4186.021057502889),
        ("Prezzo", -4330.043003943572, -4770.043003943572),
        ("Aliquota sul canone", -4438.008003943572, -4662.078003943572),
        ("Spese condominiali", -4502.043003943572, -4598.043003943572),
    )
    cash_flow_riferimento = -4550.043003943572


def vicini(a: float, b: float, tolleranza: float = TOLLERANZA) -> bool:
    return abs(a - b) <= tolleranza * max(abs(a), abs(b), 1.0)


# --- le proprietà dichiarate in ADR-023 ----------------------------------

def test_pesi_hanno_somma_dei_quadrati_uno():
    # È la proprietà che tiene le incertezze dichiarate dove sono state dichiarate:
    # la varianza di ogni estrazione efficace resta uno qualunque sia la correlazione.
    for rho in (0.0, 0.1, 0.3, 0.5, 0.99, 1.0):
        carico, proprio = R.pesi(rho)
        assert vicini(carico ** 2 + proprio ** 2, 1.0)


def test_pesi_fuori_intervallo_si_riportano_dentro():
    assert R.pesi(-0.5) == R.pesi(0.0)
    assert R.pesi(1.5) == R.pesi(1.0)


def test_correlazione_zero_torna_alla_indipendenza():
    # A correlazione nulla i pesi diventano zero e uno, quindi ogni estrazione efficace
    # è la propria componente e nient'altro: il fattore comune non entra affatto.
    inc = R.Incertezze(correlazione=0.0)
    base = base_del_foglio()
    for e in R.estrazioni_fisse(50):
        s = R.scenario(base, inc, e)
        assert vicini(s.z_canone, e.canone)
        assert vicini(s.z_sfitto, e.sfitto)
        assert vicini(s.z_tasso, e.tasso)
        assert vicini(s.z_rivalutazione, e.rivalutazione)


def test_correlazione_piena_e_solo_fattore_comune():
    inc = R.Incertezze(correlazione=1.0)
    base = base_del_foglio()
    for e in R.estrazioni_fisse(20):
        s = R.scenario(base, inc, e)
        assert vicini(s.z_canone, e.comune)
        assert vicini(s.z_sfitto, -e.comune)


def test_la_correlazione_non_gonfia_le_incertezze():
    # La varianza campionaria delle estrazioni efficaci resta uno entro l'errore di
    # campionamento, e soprattutto non cresce passando da zero a trenta per cento: era
    # il modo in cui questa modifica poteva mentire.
    base = base_del_foglio()
    estrazioni = R.estrazioni_fisse(1000)
    varianze = {}
    for rho in (0.0, 0.30):
        z = [R.scenario(base, R.Incertezze(correlazione=rho), e).z_canone for e in estrazioni]
        varianze[rho] = statistics.pvariance(z)
        assert abs(varianze[rho] - 1.0) < 0.10
    assert abs(varianze[0.0] - varianze[0.30]) < 0.02


def test_correlazione_risultante_uguale_al_parametro():
    # Fra due variabili che reagiscono nello stesso verso la correlazione risultante è il
    # parametro impostato; fra due di verso opposto è lo stesso valore col segno cambiato.
    # Su mille estrazioni l'errore di campionamento è dell'ordine di tre centesimi.
    base = base_del_foglio()
    inc = R.Incertezze(correlazione=0.30)
    esiti = [R.scenario(base, inc, e) for e in R.estrazioni_fisse(1000)]
    canone = [s.z_canone for s in esiti]
    rivalutazione = [s.z_rivalutazione for s in esiti]
    sfitto = [s.z_sfitto for s in esiti]
    assert abs(statistics.correlation(canone, rivalutazione) - 0.30) < 0.06
    assert abs(statistics.correlation(canone, sfitto) + 0.30) < 0.06


# --- le estrazioni --------------------------------------------------------

def test_estrazioni_fisse_sono_riproducibili():
    assert R.estrazioni_fisse(10) == R.estrazioni_fisse(10)
    assert R.estrazioni_fisse(10) != R.estrazioni_fisse(10, seme=1)


def test_uniforme_dell_evento_resta_lontana_dagli_estremi():
    # Serve perché la mescolanza passa per l'inversa della normale, che in zero e in uno
    # diverge: senza il taglio una riga su un milione farebbe cadere la simulazione.
    for e in R.estrazioni_fisse(1000):
        assert 0.0 < e.evento < 1.0


# --- statistica compatibile con Excel ------------------------------------

def test_percentile_interpola_come_excel():
    # PERCENTILE.INC su quattro valori: posizione 0,05*(4-1) = 0,15 fra il primo e il
    # secondo, quindi 1 + 0,15 = 1,15. Una convenzione diversa darebbe 1 oppure 1,3.
    assert vicini(R.percentile([1, 2, 3, 4], 0.05), 1.15)
    assert vicini(R.percentile([1, 2, 3, 4], 0.95), 3.85)
    assert vicini(R.percentile([4, 1, 3, 2], 0.50), 2.5)


def test_mediana_media_i_due_centrali():
    assert vicini(R.mediana([1, 2, 3, 4]), 2.5)
    assert vicini(R.mediana([3, 1, 2]), 2.0)


def test_arrotonda_come_excel_e_non_come_python():
    # Excel allontana il mezzo da zero, Python lo porta al pari. È la differenza che
    # faceva dare ventidue anni al modulo dove il foglio dava ventitre'.
    assert R.arrotonda(22.5) == 23
    assert R.arrotonda(27.5) == 28
    assert R.arrotonda(-22.5) == -23
    assert round(22.5) == 22


# --- il singolo scenario --------------------------------------------------

def test_debito_residuo_a_fine_piano_e_nullo():
    assert vicini(R.debito_residuo(90_000, 0.032, 25, 25), 0.0)
    assert vicini(R.debito_residuo(90_000, 0.032, 25, 30), 0.0)


def test_debito_residuo_prima_di_pagare_e_tutto_il_capitale():
    assert vicini(R.debito_residuo(90_000, 0.032, 25, 0), 90_000)


def test_debito_residuo_a_tasso_nullo_e_lineare():
    # A tasso nullo la formula chiusa del foglio divide per zero: qui vale il limite,
    # cioè il capitale rimborsato in parti uguali.
    assert vicini(R.debito_residuo(90_000, 0.0, 25, 10), 90_000 * 15 / 25)


def test_debito_residuo_coincide_con_il_piano_di_ammortamento():
    # La formula chiusa e la ricorsione rata per rata devono dire la stessa cosa: è il
    # controllo che lega questo modulo al motore che il resto del progetto usa.
    piano = C.piano_ammortamento(90_000, 0.032, 25)
    atteso = piano[10 * 12 - 1].debito_residuo
    assert abs(R.debito_residuo(90_000, 0.032, 25, 10) - atteso) < 1e-6


def test_senza_incertezze_lo_scenario_torna_al_caso_deterministico():
    # Con tutte le incertezze a zero la simulazione non deve inventare niente: il cash
    # flow di un qualunque scenario coincide con quello di riferimento del tornado.
    base = base_del_foglio()
    inc = R.Incertezze(vol_canone=0, vol_sfitto=0, vol_tasso=0, vol_rivalutazione=0,
                       prob_morosita_grave=0, correlazione=0.3)
    riferimento = R.cash_flow_riferimento(base)
    for e in R.estrazioni_fisse(20):
        assert vicini(R.scenario(base, inc, e).cash_flow, riferimento)


def test_morosita_grave_ai_due_estremi_della_probabilita():
    base = base_del_foglio()
    estrazioni = R.estrazioni_fisse(50)
    mai = R.Incertezze(prob_morosita_grave=0.0)
    sempre = R.Incertezze(prob_morosita_grave=1.0)
    assert not any(R.scenario(base, mai, e).morosita_grave for e in estrazioni)
    assert all(R.scenario(base, sempre, e).morosita_grave for e in estrazioni)


def test_morosita_grave_toglie_i_mesi_impostati():
    base = base_del_foglio()
    inc = R.Incertezze(vol_canone=0, vol_sfitto=0, vol_tasso=0, vol_rivalutazione=0,
                       correlazione=0.0, mesi_persi_morosita=6.0, prob_morosita_grave=0.5)
    # Con correlazione nulla l'evento dipende solo dalla propria uniforme: sotto la
    # probabilità impostata è moroso, sopra no.
    moroso = R.scenario(base, inc, R.Estrazione(0, 0, 0, 0, 0, 0.01))
    sano = R.scenario(base, inc, R.Estrazione(0, 0, 0, 0, 0, 0.99))
    assert moroso.morosita_grave and not sano.morosita_grave
    canone_mensile = sano.canone_annuo / 12
    perso = (sano.ricavo_effettivo - moroso.ricavo_effettivo)
    assert vicini(perso, canone_mensile * 6.0)


def test_mesi_di_sfitto_restano_fra_zero_e_dodici():
    base = base_del_foglio()
    inc = R.Incertezze(correlazione=0.0, vol_sfitto=1.5)
    giu = R.scenario(base, inc, R.Estrazione(0, 0, -50, 0, 0, 0.5))
    su = R.scenario(base, inc, R.Estrazione(0, 0, 50, 0, 0, 0.5))
    assert giu.mesi_sfitto == 0.0
    assert su.mesi_sfitto == 12.0


def test_canone_e_tasso_non_diventano_negativi():
    base = base_del_foglio()
    inc = R.Incertezze(correlazione=0.0, vol_canone=0.10, vol_tasso=0.01)
    s = R.scenario(base, inc, R.Estrazione(0, -100, 0, -100, 0, 0.5))
    assert s.canone_annuo == 0.0
    assert s.tasso == 0.0


def test_montante_a_rendimento_nullo_somma_i_flussi():
    base = R.BaseSimulazione(
        canone_mensile=500.0, ricavo_effettivo=5335.0, noi_annuo=1804.84,
        costo_totale=131556.5, esborso=41556.5, prezzo=120000.0,
        rendimento_portafoglio=0.0, orizzonte_anni=10,
    )
    inc = R.Incertezze(vol_canone=0, vol_sfitto=0, vol_tasso=0, vol_rivalutazione=0,
                       prob_morosita_grave=0)
    s = R.scenario(base, inc, R.Estrazione(0, 0, 0, 0, 0, 0.5))
    assert vicini(s.montante, s.patrimonio_finale + s.cash_flow * 10)


# --- la simulazione e il tornado -----------------------------------------

def test_percentili_ordinati_e_probabilita_ben_formate():
    s = R.simula(base_del_foglio(), incertezze_del_foglio())
    for dist in (s.cash_flow, s.utile_netto, s.rendimento_netto, s.patrimonio_finale, s.montante):
        assert dist.peggiore_5 <= dist.mediana <= dist.migliore_5
    for p in (s.prob_cash_negativo, s.prob_sotto_obiettivo, s.prob_perdita_capitale,
              s.prob_batte_alternativa):
        assert 0.0 <= p <= 1.0
    assert s.estrazioni == 1000


def test_simulazione_senza_estrazioni_non_cade():
    s = R.simula(base_del_foglio(), incertezze_del_foglio(), [])
    assert s.estrazioni == 0
    assert s.cash_flow.mediana == 0.0


def test_tornado_ha_le_otto_voci_del_foglio_nell_ordine_del_foglio():
    voci = R.tornado(base_del_foglio())
    assert [v.variabile for v in voci] == [nome for nome, _, _ in FOGLIO.tornado]
    for v in voci:
        assert v.ampiezza >= 0
        assert vicini(v.ampiezza, abs(v.piu - v.meno))


def test_senza_mutuo_il_tornado_non_muove_le_voci_del_mutuo():
    base = R.BaseSimulazione(
        canone_mensile=500.0, ricavo_effettivo=5335.0, noi_annuo=1804.84,
        costo_totale=131556.5, esborso=41556.5, prezzo=120000.0, mutuo_importo=0.0,
    )
    voci = {v.variabile: v for v in R.tornado(base)}
    for nome in ("Tasso del mutuo", "Importo del mutuo", "Durata del mutuo"):
        assert voci[nome].ampiezza == 0.0


# --- accordo con il workbook ---------------------------------------------

def test_distribuzioni_coincidono_con_il_foglio_rischio():
    s = R.simula(base_del_foglio(), incertezze_del_foglio(), R.estrazioni_fisse(1000))
    coppie = (
        (s.cash_flow, FOGLIO.cash_flow),
        (s.utile_netto, FOGLIO.utile_netto),
        (s.rendimento_netto, FOGLIO.rendimento),
        (s.patrimonio_finale, FOGLIO.patrimonio),
        (s.montante, FOGLIO.montante),
    )
    for mia, sua in coppie:
        for valore, atteso in zip((mia.peggiore_5, mia.mediana, mia.migliore_5), sua):
            assert vicini(valore, atteso), (valore, atteso)


def test_probabilita_coincidono_con_il_foglio_rischio():
    s = R.simula(base_del_foglio(), incertezze_del_foglio(), R.estrazioni_fisse(1000))
    mie = (s.prob_cash_negativo, s.prob_sotto_obiettivo, s.prob_perdita_capitale,
           s.prob_batte_alternativa)
    for valore, atteso in zip(mie, FOGLIO.probabilita):
        assert vicini(valore, atteso)


def test_tornado_coincide_con_il_foglio_rischio():
    base = base_del_foglio()
    voci = R.tornado(base)
    for voce, (nome, meno, piu) in zip(voci, FOGLIO.tornado):
        assert voce.variabile == nome
        assert vicini(voce.meno, meno), (nome, voce.meno, meno)
        assert vicini(voce.piu, piu), (nome, voce.piu, piu)
    assert vicini(R.cash_flow_riferimento(base), FOGLIO.cash_flow_riferimento)


def test_base_da_modello_riproduce_il_caso_del_foglio():
    # Il ponte con il resto del motore: gli stessi input dai quali il workbook parte
    # devono produrre la stessa base, altrimenti la simulazione girerebbe su un caso
    # diverso da quello valutato.
    immobile = C.Immobile(prezzo=120_000, rendita_catastale=450, categoria="A/3", superficie_mq=55)
    acquirente = C.Acquirente(prima_casa=True, prezzo_valore=True, reddito_imponibile_irpef=32_000)
    finanziamento = C.Finanziamento(importo=90_000, tasso_annuo=0.032, durata_anni=25)
    gestione = C.Gestione(canone_mensile=500, regime="cedolare_libero")
    costo = C.costo_operazione(immobile, acquirente, finanziamento)
    conto = C.conto_economico(immobile, gestione, 32_000)
    base = R.base_da_modello(immobile, gestione, finanziamento, costo, conto)
    assert vicini(base.ricavo_effettivo, 5335.0)
    assert vicini(base.aliquota_canone, 0.21)
    assert base.durata_anni == 25 and base.mutuo_importo == 90_000


if __name__ == "__main__":
    superati = 0
    falliti = []
    for nome, funzione in sorted(globals().items()):
        if nome.startswith("test_") and callable(funzione):
            try:
                funzione()
                superati += 1
            except AssertionError as e:
                falliti.append((nome, e))
            except Exception as e:  # errore vero, non asserzione
                falliti.append((nome, f"{e.__class__.__name__}: {e}"))
    print(f"{superati} test superati, {len(falliti)} falliti")
    for nome, errore in falliti:
        print(f"  FALLITO {nome}: {errore}")
    raise SystemExit(1 if falliti else 0)
