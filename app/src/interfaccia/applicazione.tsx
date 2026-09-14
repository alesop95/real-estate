// Il guscio: chi sei, in quale organizzazione stai guardando, e quale area e' aperta.
//
// Tre stati contano davvero, e ciascuno merita una risposta diversa. Non autenticato non si
// verifica quasi mai in esercizio, perche' davanti all'applicazione sta Access e chi arriva
// fin qui ha gia' superato l'accesso: quando succede, e' una sessione scaduta, e la risposta
// e' ricaricare. Autenticato ma senza organizzazioni si verifica invece al primo ingresso di
// una persona nuova, ed e' il comportamento voluto dallo schema, non un errore: un utente che
// non e' membro di niente entra e non vede niente. Merita percio' un messaggio che dica cosa
// fare, non una pagina vuota che sembra un guasto.
//
// La scelta dell'organizzazione resta sempre visibile quando ce n'e' piu' di una, e non e'
// pignoleria: su un prodotto venduto a piu' agenzie, sapere in quale perimetro si sta
// scrivendo e' la prima informazione, non un dettaglio di configurazione.

import { useCallback, useEffect, useMemo, useState } from "react";

import { NOME_RUOLO } from "../condiviso/ruoli";
import { SezioneImmobile } from "../sezioni/immobile/sezione";

import { AREE } from "./aree";
import { creaCliente, type Cliente, type Io } from "./cliente";

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
  const [area, setArea] = useState<string>("immobile");

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

  const appartenenza = io?.organizzazioni.find((o) => o.id === organizzazione) ?? null;

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
          Se la sessione e' scaduta basta ricaricare la pagina: l'accesso viene chiesto di nuovo
          e si rientra dove si era.
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
          Non e' un errore: l'accesso identifica la persona, l'appartenenza decide che cosa
          vede, e finche' non c'e' non c'e' niente da vedere. Chiedi a chi amministra
          l'organizzazione di aggiungere {io ? io.email : "il tuo indirizzo"} fra i membri.
        </p>
      </main>
    );
  }

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
                onChange={(e) => setOrganizzazione(e.target.value)}
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

      <main>
        {aperta.disponibile && organizzazione && appartenenza ? (
          <SezioneImmobile
            cliente={cliente}
            organizzazione={organizzazione}
            ruolo={appartenenza.ruolo}
          />
        ) : (
          <section className="in-arrivo">
            <h2>{aperta.nome}</h2>
            <p>{aperta.descrizione}</p>
            <p className="nota">
              Quest'area non e' ancora scritta. Nel workbook corrisponde a: {aperta.fogli}. Le sei
              aree si scrivono una per volta, ciascuna con la propria sezione, il proprio hook e i
              propri tipi, e finche' non esiste il modo di usarla resta il foglio di calcolo.
            </p>
          </section>
        )}
      </main>
    </div>
  );
}
