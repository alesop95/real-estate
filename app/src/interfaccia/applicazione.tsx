// Il guscio: chi sei, in quale organizzazione stai guardando, quale immobile e' aperto e quale
// area lo sta mostrando.
//
// Tre stati contano davvero, e ciascuno merita una risposta diversa. Non autenticato non si
// verifica quasi mai in esercizio, perche' davanti all'applicazione sta Access e chi arriva fin
// qui ha gia' superato l'accesso: quando succede, e' una sessione scaduta, e la risposta e'
// ricaricare. Autenticato ma senza organizzazioni si verifica al primo ingresso di una persona
// nuova, ed e' il comportamento voluto dallo schema, non un errore: un utente che non e' membro di
// niente entra e non vede niente. Merita percio' un messaggio che dica cosa fare, non una pagina
// vuota che sembra un guasto.
//
// L'immobile aperto sta qui e non nelle aree, e la scelta e' la stessa dell'elenco: e' una
// proprieta' della sessione di lavoro e non di una schermata, come nel workbook il foglio Immobile
// alimenta tutti gli altri. Ne discende che cambiare area non perde il contesto, e che il server
// riceve una richiesta sola per l'elenco invece di una per area.
//
// La scelta dell'organizzazione resta sempre visibile quando ce n'e' piu' di una, e non e'
// pignoleria: su un prodotto venduto a piu' agenzie, sapere in quale perimetro si sta scrivendo e'
// la prima informazione, non un dettaglio di configurazione.

import { useCallback, useEffect, useMemo, useState } from "react";

import type { ImmobileInviato } from "../condiviso/immobile";
import { NOME_RUOLO, ruoloSufficiente } from "../condiviso/ruoli";
import { SezioneCosto } from "../sezioni/costo/sezione";
import { SezioneImmobile } from "../sezioni/immobile/sezione";
import { useImmobili } from "../sezioni/immobile/hook";

import { AREE } from "./aree";
import { creaCliente, type Cliente, type Io } from "./cliente";
import { Elenco } from "./elenco";
import type { ProprietaSezione } from "./sezione";

interface Proprieta {
  /** Iniettabile: le prove passano un cliente che parla con un server finto. */
  cliente?: Cliente;
}

export function Applicazione({ cliente: clienteEsterno }: Proprieta = {}) {
  const cliente = useMemo(() => clienteEsterno ?? creaCliente(), [clienteEsterno]);
  const [io, setIo] = useState<Io | null>(null);
  const [errore, setErrore] = useState<string | null>(null);
  const [caricamento, setCaricamento] = useState(true);
  const [organizzazione, setOrganizzazione] = useState<string | null>(null);

  const carica = useCallback(() => {
    setCaricamento(true);
    setErrore(null);
    cliente
      .io()
      .then((risposta) => {
        setIo(risposta);
        setOrganizzazione(risposta.organizzazioni[0]?.id ?? null);
        setCaricamento(false);
      })
      .catch((e: unknown) => {
        setErrore(e instanceof Error ? e.message : "errore imprevisto");
        setCaricamento(false);
      });
  }, [cliente]);

  useEffect(carica, [carica]);

  if (caricamento) {
    return <p className="attesa">Caricamento...</p>;
  }

  if (errore) {
    return (
      <main className="avvio">
        <h1>Non e' stato possibile riconoscerti</h1>
        <p className="errore" role="alert">
          {errore}
        </p>
        <p>
          Se la sessione e' scaduta basta ricaricare la pagina: l'accesso viene chiesto di nuovo e
          si rientra dove si era.
        </p>
        <button type="button" onClick={carica}>
          Riprova
        </button>
      </main>
    );
  }

  if (!io || io.organizzazioni.length === 0) {
    return (
      <main className="avvio">
        <h1>Sei entrato, ma non appartieni ancora a nessuna organizzazione</h1>
        <p>
          Non e' un errore: l'accesso identifica la persona, l'appartenenza decide che cosa vede, e
          finche' non c'e' non c'e' niente da vedere. Chiedi a chi amministra l'organizzazione di
          aggiungere {io ? io.email : "il tuo indirizzo"} fra i membri.
        </p>
      </main>
    );
  }

  return (
    <Scrivania
      cliente={cliente}
      io={io}
      organizzazione={organizzazione}
      cambiaOrganizzazione={setOrganizzazione}
    />
  );
}

/**
 * La parte che esiste solo quando c'e' un'identita' e almeno un'appartenenza.
 *
 * Sta in un componente a parte perche' il suo hook dell'elenco non deve nemmeno essere costruito
 * finche' non si sa in quale organizzazione guardare: una chiamata all'elenco senza organizzazione
 * e' una richiesta che il server rifiuterebbe, e farla per poi ignorarla sarebbe un rifiuto nei
 * registri di esercizio che non corrisponde a nessun problema.
 */
function Scrivania({
  cliente,
  io,
  organizzazione,
  cambiaOrganizzazione,
}: {
  cliente: Cliente;
  io: Io;
  organizzazione: string | null;
  cambiaOrganizzazione: (id: string) => void;
}) {
  const elenco = useImmobili(cliente, organizzazione);
  const [area, setArea] = useState<string>("immobile");
  const [sceltoId, setSceltoId] = useState<string | null>(null);

  const appartenenza = io.organizzazioni.find((o) => o.id === organizzazione) ?? null;
  const ruolo = appartenenza?.ruolo ?? "lettore";
  const puoScrivere = ruoloSufficiente(ruolo, "membro");

  // Cambiando organizzazione l'immobile aperto non esiste piu' in questo perimetro: si torna alla
  // scheda vuota invece di mostrare i dati di prima sotto un altro nome.
  useEffect(() => {
    setSceltoId(null);
  }, [organizzazione]);

  const immobile = elenco.immobili.find((i) => i.id === sceltoId) ?? null;

  const salva = useCallback(
    async (corpo: ImmobileInviato) => {
      const salvato = sceltoId
        ? await elenco.aggiorna(sceltoId, corpo)
        : await elenco.crea(corpo);
      setSceltoId(salvato.id);
      return salvato;
    },
    [elenco, sceltoId],
  );

  const rimuovi = useCallback(async () => {
    if (!sceltoId) return;
    await elenco.rimuovi(sceltoId);
    setSceltoId(null);
  }, [elenco, sceltoId]);

  const proprieta: ProprietaSezione = {
    immobile,
    ruolo,
    salva,
    rimuovi: sceltoId ? rimuovi : null,
  };

  const aperta = AREE.find((a) => a.chiave === area) ?? AREE[0];

  return (
    <div className="guscio">
      <header className="testata">
        <h1>Valutazione immobili</h1>
        <div className="identita">
          {io.organizzazioni.length > 1 ? (
            <label>
              <span>Organizzazione</span>
              <select
                value={organizzazione ?? ""}
                onChange={(e) => cambiaOrganizzazione(e.target.value)}
              >
                {io.organizzazioni.map((o) => (
                  <option key={o.id} value={o.id}>
                    {o.nome}
                  </option>
                ))}
              </select>
            </label>
          ) : (
            <span className="organizzazione">{io.organizzazioni[0].nome}</span>
          )}
          <span className="chi">
            {io.email}
            {appartenenza ? ` - ${NOME_RUOLO[appartenenza.ruolo]}` : ""}
          </span>
        </div>
      </header>

      <nav className="aree">
        {AREE.map((a) => (
          <button
            key={a.chiave}
            type="button"
            className={a.chiave === area ? "area scelta" : "area"}
            onClick={() => setArea(a.chiave)}
            title={a.descrizione}
          >
            {a.nome}
            {!a.disponibile && <span className="dopo">in arrivo</span>}
          </button>
        ))}
      </nav>

      <main className="scrivania">
        <Elenco
          immobili={elenco.immobili}
          sceltoId={sceltoId}
          caricamento={elenco.caricamento}
          errore={elenco.errore}
          puoCreare={puoScrivere}
          scegli={setSceltoId}
          ricarica={elenco.ricarica}
        />
        {aperta.chiave === "immobile" && <SezioneImmobile {...proprieta} />}
        {aperta.chiave === "costo" && <SezioneCosto {...proprieta} />}
        {!aperta.disponibile && (
          <section className="in-arrivo">
            <h2>{aperta.nome}</h2>
            <p>{aperta.descrizione}</p>
            <p className="nota">
              Quest'area non e' ancora scritta. Nel workbook corrisponde a: {aperta.fogli}. Le sei
              aree si scrivono una per volta, ciascuna con la propria sezione, il proprio modello e
              i propri tipi, e finche' non esiste il modo di usarla resta il foglio di calcolo.
            </p>
          </section>
        )}
      </main>
    </div>
  );
}
