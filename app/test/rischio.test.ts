// Verifica della simulazione del rischio contro i vettori generati dal motore Python.
//
// Vale quanto detto in motore.test.ts, con una differenza che riguarda la natura di cio' che
// si verifica. La simulazione non e' una funzione degli input soltanto: e' una funzione degli
// input e delle estrazioni. I vettori portano percio' anche il campione di estrazioni con cui
// sono stati prodotti, e la suite lo passa alla simulazione invece di estrarre per conto
// proprio: due generatori pseudocasuali diversi non producono la stessa sequenza, e sperare
// che lo facciano sarebbe l'unico modo di rendere questo confronto inutile.
//
// Oltre ai vettori ci sono tre gruppi di prove che i vettori non possono coprire. Il primo e'
// l'inversa della normale, confrontata con i quantili che Python calcola con lo stesso
// algoritmo: se divergesse, divergerebbe la decisione sulla morosita' grave e la simulazione
// direbbe numeri diversi su un caso su venti. Il secondo sono le proprieta' dichiarate in
// ADR-023, verificate qui perche' sono la specifica e non un esito. Il terzo e' il generatore
// di estrazioni per l'uso interattivo, che sta fuori dai vettori per costruzione e di cui va
// provato l'unico requisito che ha, cioe' la riproducibilita' dallo stesso seme.

import { describe, expect, it } from "vitest";

import { REVISIONE } from "../src/motore/parametri.generati";
import {
  arrotonda,
  cashFlowRiferimento,
  debitoResiduo,
  estrazioniDaSeme,
  inversaNormale,
  mediana,
  percentile,
  pesi,
  scenario,
  simula,
  tornado,
  type BaseSimulazione,
  type Estrazione,
  type Incertezze,
} from "../src/motore/rischio";
import { confronta } from "./confronto";
import vettori from "./vettori.rischio.json";

type Documento = {
  generatoDa: string;
  revisioneParametri: string;
  tolleranzaRelativa: number;
  tolleranzaAssoluta: number;
  semeEstrazioni: number;
  estrazioni: number[][];
  casi: number;
  vettori: {
    n: number;
    ingresso: { base: BaseSimulazione; incertezze: Incertezze };
    atteso: unknown;
  }[];
};

const documento = vettori as unknown as Documento;

/** Le estrazioni del documento nella forma che la simulazione accetta. */
const estrazioni: Estrazione[] = documento.estrazioni.map(
  ([comune, canone, sfitto, tasso, rivalutazione, evento]) => ({
    comune,
    canone,
    sfitto,
    tasso,
    rivalutazione,
    evento,
  }),
);

function calcola(base: BaseSimulazione, incertezze: Incertezze) {
  return {
    sintesi: simula(base, incertezze, estrazioni),
    scenari: estrazioni.slice(0, 3).map((e) => scenario(base, incertezze, e)),
    tornado: tornado(base),
    cashFlowRiferimento: cashFlowRiferimento(base),
  };
}

describe("simulazione del rischio contro i vettori del motore Python", () => {
  it("usa i parametri della stessa revisione con cui i vettori sono stati generati", () => {
    expect(REVISIONE).toBe(documento.revisioneParametri);
  });

  it("porta con se' le estrazioni con cui i vettori sono stati prodotti", () => {
    expect(documento.estrazioni.length).toBeGreaterThan(32);
    expect(documento.vettori.length).toBe(documento.casi);
    expect(documento.vettori.length).toBeGreaterThan(40);
    for (const e of estrazioni) {
      expect(e.evento).toBeGreaterThan(0);
      expect(e.evento).toBeLessThan(1);
    }
  });

  it("il confronto sa fallire: un valore alterato viene visto", () => {
    const vettore = documento.vettori[0];
    const trovato = calcola(vettore.ingresso.base, vettore.ingresso.incertezze);
    const attesoGuasto = JSON.parse(JSON.stringify(vettore.atteso)) as Record<string, any>;
    attesoGuasto.sintesi.cashFlow.mediana = attesoGuasto.sintesi.cashFlow.mediana + 0.001;
    attesoGuasto.tornado[0].variabile = "una variabile che non esiste";

    const scarti: string[] = [];
    confronta(attesoGuasto, trovato, "", scarti, documento.tolleranzaRelativa, documento.tolleranzaAssoluta);
    expect(scarti.length).toBe(2);
    expect(scarti.some((s) => s.startsWith("sintesi.cashFlow.mediana:"))).toBe(true);
    expect(scarti.some((s) => s.startsWith("tornado.0.variabile:"))).toBe(true);

    const nessuno: string[] = [];
    confronta(vettore.atteso, trovato, "", nessuno, documento.tolleranzaRelativa, documento.tolleranzaAssoluta);
    expect(nessuno).toEqual([]);
  });

  it("riproduce ogni vettore entro la tolleranza dichiarata", () => {
    const fallimenti: string[] = [];
    for (const vettore of documento.vettori) {
      const scarti: string[] = [];
      const trovato = calcola(vettore.ingresso.base, vettore.ingresso.incertezze);
      confronta(
        vettore.atteso,
        trovato,
        "",
        scarti,
        documento.tolleranzaRelativa,
        documento.tolleranzaAssoluta,
      );
      if (scarti.length) {
        const b = vettore.ingresso.base;
        const i = vettore.ingresso.incertezze;
        const contesto = `caso ${vettore.n} [correlazione ${i.correlazione}, morosita ${i.prob_morosita_grave}, mutuo ${b.mutuo_importo}, portafoglio ${b.rendimento_portafoglio}]`;
        fallimenti.push(`${contesto}\n    ${scarti.join("\n    ")}`);
      }
    }
    expect(fallimenti.join("\n  "), `${fallimenti.length} casi su ${documento.vettori.length} divergono`).toBe("");
  });
});

describe("inversa della normale standard", () => {
  it("riproduce i quantili che Python calcola con lo stesso algoritmo", () => {
    // Valori di riferimento presi da statistics.NormalDist().inv_cdf, che usa AS 241 come
    // questa implementazione: coprono il ramo centrale, quello intermedio e quello di coda.
    const riferimenti: Array<[number, number]> = [
      [0.5, 0.0],
      [0.05, -1.6448536269514726],
      [0.975, 1.9599639845400536],
      [0.9, 1.2815515655446008],
      [0.925, 1.439531470938456],
      [0.001, -3.090232306167813],
      [1e-10, -6.361340902404056],
      [1 - 1e-10, 6.361340889697421],
    ];
    for (const [p, atteso] of riferimenti) {
      const trovato = inversaNormale(p);
      const ammesso = Math.max(Math.abs(atteso) * 1e-12, 1e-12);
      expect(Math.abs(trovato - atteso), `p = ${p}`).toBeLessThanOrEqual(ammesso);
    }
  });

  it("e' antisimmetrica rispetto a un mezzo", () => {
    for (const p of [0.01, 0.2, 0.37, 0.49]) {
      expect(Math.abs(inversaNormale(p) + inversaNormale(1 - p))).toBeLessThan(1e-12);
    }
  });
});

describe("le proprieta' dichiarate in ADR-023", () => {
  const base = () => documento.vettori[0].ingresso.base;
  const incertezze = (correlazione: number): Incertezze => ({
    ...documento.vettori[0].ingresso.incertezze,
    correlazione,
  });

  it("i pesi hanno somma dei quadrati uno", () => {
    for (const rho of [0, 0.1, 0.3, 0.5, 0.99, 1]) {
      const [carico, proprio] = pesi(rho);
      expect(Math.abs(carico * carico + proprio * proprio - 1)).toBeLessThan(1e-12);
    }
  });

  it("a correlazione nulla ogni estrazione efficace e' la propria componente", () => {
    const inc = incertezze(0);
    for (const e of estrazioni.slice(0, 20)) {
      const s = scenario(base(), inc, e);
      expect(Math.abs(s.zCanone - e.canone)).toBeLessThan(1e-12);
      expect(Math.abs(s.zSfitto - e.sfitto)).toBeLessThan(1e-12);
      expect(Math.abs(s.zTasso - e.tasso)).toBeLessThan(1e-12);
      expect(Math.abs(s.zRivalutazione - e.rivalutazione)).toBeLessThan(1e-12);
    }
  });

  it("a correlazione piena conta solo il fattore comune, col verso di ciascuna variabile", () => {
    const inc = incertezze(1);
    for (const e of estrazioni.slice(0, 20)) {
      const s = scenario(base(), inc, e);
      expect(Math.abs(s.zCanone - e.comune)).toBeLessThan(1e-12);
      expect(Math.abs(s.zSfitto + e.comune)).toBeLessThan(1e-12);
    }
  });

  it("la correlazione non gonfia le incertezze dichiarate", () => {
    const varianza = (rho: number): number => {
      const z = estrazioni.map((e) => scenario(base(), incertezze(rho), e).zCanone);
      const media = z.reduce((a, b) => a + b, 0) / z.length;
      return z.reduce((a, b) => a + (b - media) * (b - media), 0) / z.length;
    };
    // Su sessantaquattro estrazioni l'errore di campionamento e' largo, quindi il confine
    // stretto e' sulla differenza fra le due varianze e non sul loro valore.
    expect(Math.abs(varianza(0) - varianza(0.3))).toBeLessThan(0.05);
    expect(Math.abs(varianza(0.3) - 1)).toBeLessThan(0.35);
  });
});

describe("statistica compatibile con Excel", () => {
  it("il percentile interpola come PERCENTILE.INC", () => {
    expect(percentile([1, 2, 3, 4], 0.05)).toBeCloseTo(1.15, 12);
    expect(percentile([1, 2, 3, 4], 0.95)).toBeCloseTo(3.85, 12);
    expect(percentile([4, 1, 3, 2], 0.5)).toBeCloseTo(2.5, 12);
    expect(percentile([], 0.5)).toBe(0);
  });

  it("la mediana media i due centrali", () => {
    expect(mediana([1, 2, 3, 4])).toBe(2.5);
    expect(mediana([3, 1, 2])).toBe(2);
  });

  it("l'arrotondamento allontana il mezzo da zero, come Excel e non come Math.round", () => {
    expect(arrotonda(22.5)).toBe(23);
    expect(arrotonda(27.5)).toBe(28);
    expect(arrotonda(-22.5)).toBe(-23);
    expect(Math.round(-22.5)).toBe(-22);
  });

  it("il debito residuo va a zero a fine piano e vale tutto prima di pagare", () => {
    expect(Math.abs(debitoResiduo(90000, 0.032, 25, 25))).toBeLessThan(1e-9);
    expect(debitoResiduo(90000, 0.032, 25, 0)).toBeCloseTo(90000, 9);
    expect(debitoResiduo(90000, 0, 25, 10)).toBeCloseTo((90000 * 15) / 25, 9);
    expect(debitoResiduo(0, 0.032, 25, 5)).toBe(0);
  });
});

describe("estrazioni per l'uso interattivo", () => {
  it("dallo stesso seme danno sempre la stessa sequenza", () => {
    expect(estrazioniDaSeme(20, 7)).toEqual(estrazioniDaSeme(20, 7));
    expect(estrazioniDaSeme(20, 7)).not.toEqual(estrazioniDaSeme(20, 8));
  });

  it("danno normali standard e uniformi dentro l'intervallo aperto", () => {
    const campione = estrazioniDaSeme(4000, 20260909);
    const valori = campione.flatMap((e) => [e.comune, e.canone, e.sfitto, e.tasso, e.rivalutazione]);
    const media = valori.reduce((a, b) => a + b, 0) / valori.length;
    const varianza =
      valori.reduce((a, b) => a + (b - media) * (b - media), 0) / valori.length;
    expect(Math.abs(media)).toBeLessThan(0.05);
    expect(Math.abs(varianza - 1)).toBeLessThan(0.1);
    for (const e of campione) {
      expect(e.evento).toBeGreaterThan(0);
      expect(e.evento).toBeLessThan(1);
    }
  });

  it("servono la simulazione senza cambiarne il significato", () => {
    // Estrazioni diverse dalle stesse ipotesi devono dare una distribuzione simile, non
    // identica: e' il senso di una simulazione. Qui si chiede solo che la mediana del cash
    // flow resti dello stesso ordine, che e' il controllo che intercetta un generatore rotto.
    const { base, incertezze } = documento.vettori[0].ingresso;
    const prima = simula(base, incertezze, estrazioniDaSeme(1000, 1)).cashFlow.mediana;
    const seconda = simula(base, incertezze, estrazioniDaSeme(1000, 2)).cashFlow.mediana;
    const riferimento = cashFlowRiferimento(base);
    expect(Math.abs(prima - seconda)).toBeLessThan(Math.abs(riferimento) + 1000);
  });
});
