// Le rotte degli immobili, e la validazione di cio' che arriva dal browser.
//
// Sulla validazione vale una precisazione, perche' il confine e' sottile e altrove in questo
// progetto si e' detto il contrario. Il calcolo non ha bisogno di essere protetto: gira nel
// browser, e chi ne alterasse le formule ingannerebbe solo se stesso. La forma dei dati e'
// un'altra cosa: una riga scritta male non danneggia chi la scrive, danneggia l'elenco
// dell'organizzazione, cioe' anche i colleghi, e rompe un ordinamento o una somma per tutti.
// Il server quindi non si fida della forma, pur non avendo ragione di diffidare dei numeri.

import type { Contesto } from "./autorizzazione";

/** Il documento delle ipotesi di valutazione, che il motore legge e il database non guarda. */
type Ipotesi = Record<string, unknown>;

export interface ImmobileInviato {
  titolo: string;
  comune: string;
  indirizzo: string;
  prezzo: number;
  superficie_mq: number;
  categoria: string;
  rendita_catastale: number;
  stato: string;
  ipotesi: Ipotesi;
}

const STATI = ["da valutare", "in valutazione", "trattativa", "scartato", "acquistato"];
const CATEGORIE = /^[A-C]\/\d{1,2}$/;

/**
 * Controlla la forma e restituisce l'elenco dei problemi, vuoto se va bene.
 *
 * Restituisce tutti gli errori e non il primo, perche' un modulo che si fa correggere un
 * campo per volta e' un modulo che si compila tre volte.
 */
export function validaImmobile(corpo: unknown): { errori: string[]; valore?: ImmobileInviato } {
  const errori: string[] = [];
  if (corpo === null || typeof corpo !== "object") return { errori: ["il corpo non e' un oggetto"] };
  const d = corpo as Record<string, unknown>;

  const testo = (campo: string, obbligatorio: boolean, massimo = 200): string => {
    const v = d[campo];
    if (v === undefined || v === null) {
      if (obbligatorio) errori.push(`${campo}: manca`);
      return "";
    }
    if (typeof v !== "string") {
      errori.push(`${campo}: deve essere testo`);
      return "";
    }
    const pulito = v.trim();
    if (obbligatorio && !pulito) errori.push(`${campo}: non puo' essere vuoto`);
    if (pulito.length > massimo) errori.push(`${campo}: oltre ${massimo} caratteri`);
    return pulito;
  };

  const numero = (campo: string, minimo: number, massimo: number): number => {
    const v = d[campo];
    if (v === undefined || v === null) return 0;
    if (typeof v !== "number" || !Number.isFinite(v)) {
      errori.push(`${campo}: deve essere un numero finito`);
      return 0;
    }
    if (v < minimo || v > massimo) errori.push(`${campo}: fuori dall'intervallo ${minimo} - ${massimo}`);
    return v;
  };

  const titolo = testo("titolo", true);
  const comune = testo("comune", false);
  const indirizzo = testo("indirizzo", false);
  const categoria = testo("categoria", false, 8) || "A/2";
  if (categoria && !CATEGORIE.test(categoria)) errori.push("categoria: forma attesa tipo A/2");
  const stato = testo("stato", false) || "da valutare";
  if (stato && !STATI.includes(stato)) errori.push(`stato: uno fra ${STATI.join(", ")}`);

  // Gli estremi non sono arbitrari: un prezzo di dieci milioni o una superficie di
  // diecimila metri non appartengono al residenziale che questo strumento valuta, e
  // lasciarli passare significa vedere una graduatoria dominata da un errore di battitura.
  const prezzo = numero("prezzo", 0, 10_000_000);
  const superficie = numero("superficie_mq", 0, 10_000);
  const rendita = numero("rendita_catastale", 0, 100_000);

  const ipotesi = d.ipotesi === undefined ? {} : d.ipotesi;
  if (ipotesi === null || typeof ipotesi !== "object" || Array.isArray(ipotesi)) {
    errori.push("ipotesi: deve essere un oggetto");
  } else if (JSON.stringify(ipotesi).length > 20_000) {
    errori.push("ipotesi: documento oltre i 20.000 caratteri");
  }

  if (errori.length) return { errori };
  return {
    errori: [],
    valore: {
      titolo,
      comune,
      indirizzo,
      prezzo,
      superficie_mq: superficie,
      categoria,
      rendita_catastale: rendita,
      stato,
      ipotesi: ipotesi as Ipotesi,
    },
  };
}

interface RigaImmobile {
  id: string;
  organizzazione_id: string;
  titolo: string;
  comune: string;
  indirizzo: string;
  prezzo: number;
  superficie_mq: number;
  categoria: string;
  rendita_catastale: number;
  stato: string;
  ipotesi: string;
  creato_il: string;
  aggiornato_il: string;
}

function versoFuori(riga: RigaImmobile) {
  const { ipotesi, organizzazione_id, ...resto } = riga;
  return { ...resto, organizzazione: organizzazione_id, ipotesi: JSON.parse(ipotesi) as Ipotesi };
}

export async function elencaImmobili(ctx: Contesto): Promise<Response> {
  // Il filtro per organizzazione non e' un'opzione dell'interrogazione: e' l'interrogazione.
  // Ogni SELECT di questo file ha questa clausola, ed e' la ragione per cui l'indice del
  // database e' costruito su quella colonna per prima.
  const esito = await ctx.db
    .prepare(
      "SELECT * FROM immobili WHERE organizzazione_id = ? ORDER BY aggiornato_il DESC, id ASC",
    )
    .bind(ctx.organizzazione)
    .all<RigaImmobile>();
  return Response.json({ immobili: (esito.results ?? []).map(versoFuori) });
}

export async function leggiImmobile(ctx: Contesto, id: string): Promise<Response> {
  const riga = await ctx.db
    .prepare("SELECT * FROM immobili WHERE id = ? AND organizzazione_id = ?")
    .bind(id, ctx.organizzazione)
    .first<RigaImmobile>();
  if (!riga) return Response.json({ errore: "immobile non trovato" }, { status: 404 });
  return Response.json(versoFuori(riga));
}

export async function creaImmobile(ctx: Contesto, corpo: unknown, id: string, adesso: string): Promise<Response> {
  const { errori, valore } = validaImmobile(corpo);
  if (!valore) return Response.json({ errori }, { status: 422 });

  await ctx.db
    .prepare(
      `INSERT INTO immobili
         (id, organizzazione_id, titolo, comune, indirizzo, prezzo, superficie_mq,
          categoria, rendita_catastale, stato, ipotesi, creato_il, aggiornato_il)
       VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)`,
    )
    .bind(
      id,
      ctx.organizzazione,
      valore.titolo,
      valore.comune,
      valore.indirizzo,
      valore.prezzo,
      valore.superficie_mq,
      valore.categoria,
      valore.rendita_catastale,
      valore.stato,
      JSON.stringify(valore.ipotesi),
      adesso,
      adesso,
    )
    .run();
  return leggiImmobile(ctx, id);
}

export async function aggiornaImmobile(ctx: Contesto, id: string, corpo: unknown, adesso: string): Promise<Response> {
  const { errori, valore } = validaImmobile(corpo);
  if (!valore) return Response.json({ errori }, { status: 422 });

  // La clausola sull'organizzazione sta anche qui, e non solo nella lettura che la precede:
  // un aggiornamento che si fidasse di un controllo fatto prima sarebbe corretto oggi e
  // scoperto domani, il giorno in cui qualcuno riordina le righe.
  const esito = await ctx.db
    .prepare(
      `UPDATE immobili
          SET titolo = ?, comune = ?, indirizzo = ?, prezzo = ?, superficie_mq = ?,
              categoria = ?, rendita_catastale = ?, stato = ?, ipotesi = ?, aggiornato_il = ?
        WHERE id = ? AND organizzazione_id = ?`,
    )
    .bind(
      valore.titolo,
      valore.comune,
      valore.indirizzo,
      valore.prezzo,
      valore.superficie_mq,
      valore.categoria,
      valore.rendita_catastale,
      valore.stato,
      JSON.stringify(valore.ipotesi),
      adesso,
      id,
      ctx.organizzazione,
    )
    .run();

  if (!esito.meta.changes) return Response.json({ errore: "immobile non trovato" }, { status: 404 });
  return leggiImmobile(ctx, id);
}

export async function rimuoviImmobile(ctx: Contesto, id: string): Promise<Response> {
  const esito = await ctx.db
    .prepare("DELETE FROM immobili WHERE id = ? AND organizzazione_id = ?")
    .bind(id, ctx.organizzazione)
    .run();
  if (!esito.meta.changes) return Response.json({ errore: "immobile non trovato" }, { status: 404 });
  return new Response(null, { status: 204 });
}
