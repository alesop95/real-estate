// La forma di un immobile e la regola che la valida, scritte una volta per due lati.
//
// Fino al 14 settembre 2026 questo codice stava dentro src/server/immobili.ts, cioe' dentro
// il Worker, ed era l'unico posto in cui la forma fosse definita. Andava bene finche' il solo
// chiamante era una prova automatica; smette di andare bene appena esiste un modulo che
// compila e invia quei campi, perche' a quel punto la forma esiste in due posti e le due
// copie divergono nella direzione peggiore. Non divergono verso il rifiuto, che sarebbe
// rumoroso: divergono verso il silenzio, cioe' un modulo che accetta un valore che il server
// rifiutera' dopo, mostrando all'utente un errore che il modulo avrebbe potuto dirgli prima.
//
// La scelta e' quindi che la regola stia qui e che la importino entrambi. Il browser la usa
// per dire subito che cosa non va; il server la riapplica identica perche' un controllo fatto
// solo nel browser non e' un controllo, e' un suggerimento: chiunque puo' parlare
// all'interfaccia di programmazione senza passare dalla pagina. La differenza fra i due usi
// non e' la regola, e' la conseguenza. Nel browser evita una richiesta inutile, nel Worker
// protegge l'elenco dell'organizzazione, cioe' anche i colleghi di chi ha sbagliato.
//
// Vale ripetere il confine, perche' altrove in questo progetto si e' detto il contrario. Il
// calcolo non ha bisogno di essere protetto: gira nel browser, e chi ne alterasse le formule
// ingannerebbe solo se stesso. La forma dei dati e' un'altra cosa: una riga scritta male non
// danneggia chi la scrive, danneggia l'elenco condiviso e rompe un ordinamento o una somma
// per tutti. Il server quindi non si fida della forma, pur non avendo ragione di diffidare
// dei numeri.

/** Il documento delle ipotesi di valutazione, che il motore legge e il database non guarda. */
export type Ipotesi = Record<string, unknown>;

/** Gli stati in cui puo' trovarsi un immobile lungo il percorso di valutazione. */
export const STATI_IMMOBILE = ["da valutare", "in valutazione", "trattativa", "scartato", "acquistato"] as const;

export type StatoImmobile = (typeof STATI_IMMOBILE)[number];

/**
 * Le categorie catastali ammesse.
 *
 * Il gruppo A e' l'abitativo, il B il collettivo, il C le pertinenze: un box e una cantina
 * sono C/6 e C/2 e vanno accettati, perche' si comprano insieme all'abitazione. I gruppi D
 * ed E, cioe' l'industriale e lo speciale, restano fuori: non sono il residenziale che
 * questo strumento valuta, e lasciarli entrare significherebbe applicare loro aliquote che
 * non sono le loro.
 */
export const FORMA_CATEGORIA = /^[A-C]\/\d{1,2}$/;

/** Quanto puo' pesare il documento delle ipotesi. Oltre, non e' piu' un documento. */
export const MASSIMO_IPOTESI = 20_000;

/** I campi che il browser invia e che il server accetta. Nessun valore calcolato. */
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

/** Un immobile come torna dall'interfaccia di programmazione: i campi inviati piu' la storia. */
export interface Immobile extends ImmobileInviato {
  id: string;
  organizzazione: string;
  creato_il: string;
  aggiornato_il: string;
}

/**
 * Un immobile appena cominciato.
 *
 * Sta qui e non nella sezione perche' i valori predefiniti sono parte della forma: la
 * categoria A/2 e lo stato "da valutare" sono gli stessi che il server assegna a chi non li
 * manda, e tenerli in due posti riprodurrebbe esattamente la divergenza che questo modulo
 * esiste per chiudere.
 */
export function immobileNuovo(): ImmobileInviato {
  return {
    titolo: "",
    comune: "",
    indirizzo: "",
    prezzo: 0,
    superficie_mq: 0,
    categoria: "A/2",
    rendita_catastale: 0,
    stato: "da valutare",
    ipotesi: {},
  };
}

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
  if (categoria && !FORMA_CATEGORIA.test(categoria)) errori.push("categoria: forma attesa tipo A/2");
  const stato = testo("stato", false) || "da valutare";
  if (stato && !(STATI_IMMOBILE as readonly string[]).includes(stato)) {
    errori.push(`stato: uno fra ${STATI_IMMOBILE.join(", ")}`);
  }

  // Gli estremi non sono arbitrari: un prezzo di dieci milioni o una superficie di
  // diecimila metri non appartengono al residenziale che questo strumento valuta, e
  // lasciarli passare significa vedere una graduatoria dominata da un errore di battitura.
  const prezzo = numero("prezzo", 0, 10_000_000);
  const superficie = numero("superficie_mq", 0, 10_000);
  const rendita = numero("rendita_catastale", 0, 100_000);

  const ipotesi = d.ipotesi === undefined ? {} : d.ipotesi;
  if (ipotesi === null || typeof ipotesi !== "object" || Array.isArray(ipotesi)) {
    errori.push("ipotesi: deve essere un oggetto");
  } else if (JSON.stringify(ipotesi).length > MASSIMO_IPOTESI) {
    errori.push(`ipotesi: documento oltre i ${MASSIMO_IPOTESI.toLocaleString("it-IT")} caratteri`);
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
