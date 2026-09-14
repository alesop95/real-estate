// I controlli che tutte le aree usano, in un posto solo.
//
// Non sono astrazioni: sono tre etichette con il loro campo, una riga di una lista di numeri e i
// due riquadri dei messaggi. Stanno qui perche' la seconda area li avrebbe riscritti identici, e
// perche' due di essi portano una decisione che non va ripetuta a mano: un campo percentuale
// mostra 3 e conserva 0,03, e un campo in euro rifiuta il valore non numerico invece di far
// entrare NaN nel calcolo, dove attraverserebbe ogni somma senza fallire e comparirebbe come un
// trattino in fondo a una colonna.

import type { ReactNode } from "react";

export function CampoTesto({
  etichetta,
  valore,
  cambia,
  suggerimento,
  nota,
}: {
  etichetta: string;
  valore: string;
  cambia: (v: string) => void;
  suggerimento?: string;
  nota?: ReactNode;
}) {
  return (
    <label>
      <span>{etichetta}</span>
      <input value={valore} placeholder={suggerimento} onChange={(e) => cambia(e.target.value)} />
      {nota && <small>{nota}</small>}
    </label>
  );
}

export function CampoNumero({
  etichetta,
  valore,
  cambia,
  passo = 1,
  minimo = 0,
  massimo,
  nota,
}: {
  etichetta: string;
  valore: number;
  cambia: (v: number) => void;
  passo?: number;
  minimo?: number;
  massimo?: number;
  nota?: ReactNode;
}) {
  return (
    <label>
      <span>{etichetta}</span>
      <input
        type="number"
        min={minimo}
        max={massimo}
        step={passo}
        value={Number.isFinite(valore) ? valore : 0}
        onChange={(e) => {
          // Un campo numerico svuotato restituisce la stringa vuota, che diventerebbe NaN.
          // Zero e' la lettura corretta di un campo vuoto in questo dominio: un costo che non
          // si dichiara e' un costo che non c'e'.
          const letto = Number(e.target.value);
          cambia(Number.isFinite(letto) ? letto : 0);
        }}
      />
      {nota && <small>{nota}</small>}
    </label>
  );
}

/**
 * Un campo percentuale: mostra 3 e conserva 0,03.
 *
 * La conversione sta qui e non nel modello di ciascuna area, perche' e' la specie di dettaglio
 * che, ripetuto, prima o poi viene dimenticato in un punto solo: un'aliquota che vale trenta
 * invece di zero virgola tre non produce un errore, produce una provvigione dieci volte tanto.
 */
export function CampoPercentuale({
  etichetta,
  frazione,
  cambia,
  passo = 0.1,
  massimo = 100,
  nota,
}: {
  etichetta: string;
  frazione: number;
  cambia: (frazione: number) => void;
  passo?: number;
  massimo?: number;
  nota?: ReactNode;
}) {
  const mostrato = Number.isFinite(frazione) ? Math.round(frazione * 10_000) / 100 : 0;
  return (
    <label>
      <span>{etichetta}</span>
      <input
        type="number"
        min={0}
        max={massimo}
        step={passo}
        value={mostrato}
        onChange={(e) => {
          const letto = Number(e.target.value);
          cambia(Number.isFinite(letto) ? letto / 100 : 0);
        }}
      />
      {nota && <small>{nota}</small>}
    </label>
  );
}

export function Interruttore({
  etichetta,
  valore,
  cambia,
}: {
  etichetta: string;
  valore: boolean;
  cambia: (v: boolean) => void;
}) {
  return (
    <label className="interruttore">
      <input type="checkbox" checked={valore} onChange={(e) => cambia(e.target.checked)} />
      <span>{etichetta}</span>
    </label>
  );
}

/** Una riga della lista dei numeri calcolati. */
export function Voce({
  nome,
  valore,
  forte,
  segno,
}: {
  nome: string;
  valore: string;
  forte?: boolean;
  /** Colora il valore quando il suo segno e' l'informazione, come in un flusso di cassa. */
  segno?: "positivo" | "negativo";
}) {
  const classi = [forte ? "forte" : "", segno ?? ""].filter(Boolean).join(" ");
  return (
    <>
      <dt>{nome}</dt>
      <dd className={classi || undefined}>{valore}</dd>
    </>
  );
}

export function Errori({ errori }: { errori: readonly string[] }) {
  if (errori.length === 0) return null;
  return (
    <ul className="errori" role="alert">
      {errori.map((e) => (
        <li key={e}>{e}</li>
      ))}
    </ul>
  );
}

export function Conferma({ messaggio }: { messaggio: string | null }) {
  if (!messaggio) return null;
  return <p className="conferma">{messaggio}</p>;
}

/** La barra delle azioni in fondo a un'area, uguale in tutte. */
export function Azioni({
  puoScrivere,
  salvataggio,
  modificata,
  nuovo,
  salva,
  extra,
}: {
  puoScrivere: boolean;
  salvataggio: boolean;
  modificata: boolean;
  nuovo: boolean;
  salva: () => void;
  extra?: ReactNode;
}) {
  return (
    <div className="azioni">
      <button type="button" onClick={salva} disabled={!puoScrivere || salvataggio}>
        {salvataggio ? "Salvataggio..." : nuovo ? "Crea immobile" : "Salva"}
      </button>
      {extra}
      {modificata && !salvataggio && <span className="non-salvato">modifiche non salvate</span>}
    </div>
  );
}
