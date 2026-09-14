// L'amministrazione: chi fa parte di questa organizzazione, e quali organizzazioni esistono.
//
// Non e' una delle sei aree e non ne segue il contratto, perche' non lavora su un immobile:
// lavora su chi puo' vederli. La schermata ha due pannelli, e la separazione ricalca quella dei
// livelli, per ADR-029.
//
// Il primo pannello lo vede chi fa parte dell'organizzazione, e lo cambia chi ne e' amministratore:
// e' il posto in cui un'agenzia invita un collega, gli cambia ruolo o glielo revoca. Il secondo lo
// vede solo chi ha un livello sulla piattaforma, ed e' il registro delle organizzazioni: chi lo
// usa crea il contenitore di un cliente e ne nomina l'amministratore, e non vede un solo immobile
// di nessuna organizzazione di cui non sia membro.
//
// La cancellazione, in entrambi i pannelli, chiede una conferma in due tempi invece di una
// finestra di sistema. La ragione non e' estetica: una finestra di sistema si chiude per riflesso,
// e qui il gesto che si conferma porta via i dati di un cliente intero.

import { useCallback, useEffect, useState } from "react";

import type { Membro, OrganizzazioneConMembri } from "../../condiviso/organizzazione";
import {
  COSA_PUO_FARE,
  COSA_PUO_FARE_SULLA_PIATTAFORMA,
  livelloSufficiente,
  NOME_LIVELLO,
  NOME_RUOLO,
  RUOLI,
  ruoloSufficiente,
  type Ruolo,
} from "../../condiviso/ruoli";
import { Conferma, Errori } from "../../interfaccia/controlli";
import { quando } from "../../interfaccia/formato";
import type { ProprietaAmministrazione } from "../../interfaccia/sezione";

export function SezioneAmministrazione({
  cliente,
  organizzazione,
  ruolo,
  livello,
}: ProprietaAmministrazione) {
  return (
    <div className="amministrazione">
      {organizzazione && ruolo ? (
        <PannelloMembri cliente={cliente} organizzazione={organizzazione} ruolo={ruolo} />
      ) : (
        <section className="scheda">
          <h2>Chi fa parte dell'organizzazione</h2>
          <p className="avviso">
            Non appartieni ad alcuna organizzazione, quindi non c'e' un elenco di membri da mostrare.
          </p>
        </section>
      )}

      {livello && <PannelloPiattaforma cliente={cliente} livello={livello} />}
    </div>
  );
}

// ---------------------------------------------------------------------------
// Chi fa parte di questa organizzazione
// ---------------------------------------------------------------------------

function PannelloMembri({
  cliente,
  organizzazione,
  ruolo,
}: {
  cliente: ProprietaAmministrazione["cliente"];
  organizzazione: string;
  ruolo: Ruolo;
}) {
  const [membri, setMembri] = useState<Membro[]>([]);
  const [caricamento, setCaricamento] = useState(true);
  const [errori, setErrori] = useState<readonly string[]>([]);
  const [messaggio, setMessaggio] = useState<string | null>(null);
  const [inCorso, setInCorso] = useState(false);
  const [daRevocare, setDaRevocare] = useState<string | null>(null);
  const [nuovaEmail, setNuovaEmail] = useState("");
  const [nuovoRuolo, setNuovoRuolo] = useState<Ruolo>("membro");

  const puoCambiare = ruoloSufficiente(ruolo, "amministratore");

  const carica = useCallback(() => {
    setCaricamento(true);
    cliente
      .elencaMembri(organizzazione)
      .then((elenco) => {
        setMembri(elenco);
        setErrori([]);
      })
      .catch((e: unknown) => setErrori([e instanceof Error ? e.message : "errore imprevisto"]))
      .finally(() => setCaricamento(false));
  }, [cliente, organizzazione]);

  useEffect(carica, [carica]);

  /**
   * Esegue un'operazione e ne adotta l'esito, che e' l'elenco come il server l'ha lasciato.
   *
   * Non si ricostruisce lo stato a mano dopo una scrittura: il server risponde gia' con l'elenco
   * completo, e adottarlo evita la classe di difetti in cui l'interfaccia crede una cosa e il
   * database un'altra, che su un pannello dei permessi e' il posto peggiore dove averla.
   */
  async function esegui(operazione: () => Promise<Membro[]>, conferma: string) {
    setInCorso(true);
    setErrori([]);
    setMessaggio(null);
    try {
      setMembri(await operazione());
      setMessaggio(conferma);
    } catch (e: unknown) {
      setErrori([e instanceof Error ? e.message : "errore imprevisto"]);
    } finally {
      setInCorso(false);
      setDaRevocare(null);
    }
  }

  return (
    <section className="scheda">
      <header>
        <h2>Chi fa parte dell'organizzazione</h2>
        <p className="fascia">
          L'appartenenza e' per indirizzo di posta, ed e' lo stesso con cui la persona supera
          l'accesso. Chi non e' in questo elenco entra, viene riconosciuto, e non vede niente: e' il
          comportamento voluto, non un guasto.
        </p>
      </header>

      <Errori errori={errori} />
      <Conferma messaggio={messaggio} />
      {!puoCambiare && (
        <p className="avviso">
          Puoi vedere chi fa parte dell'organizzazione. Per invitare o revocare serve il ruolo di
          amministratore.
        </p>
      )}

      {caricamento ? (
        <p className="attesa">Caricamento...</p>
      ) : (
        <table className="membri">
          <thead>
            <tr>
              <th>Indirizzo</th>
              <th>Ruolo</th>
              <th>Dal</th>
              <th />
            </tr>
          </thead>
          <tbody>
            {membri.map((m) => (
              <tr key={m.email}>
                <td>{m.email}</td>
                <td>
                  {puoCambiare ? (
                    <select
                      value={m.ruolo}
                      disabled={inCorso}
                      aria-label={`Ruolo di ${m.email}`}
                      onChange={(e) =>
                        void esegui(
                          () =>
                            cliente.scriviMembro(organizzazione, {
                              email: m.email,
                              ruolo: e.target.value as Ruolo,
                            }),
                          `Ruolo di ${m.email} aggiornato.`,
                        )
                      }
                    >
                      {RUOLI.map((r) => (
                        <option key={r} value={r}>
                          {NOME_RUOLO[r]}
                        </option>
                      ))}
                    </select>
                  ) : (
                    NOME_RUOLO[m.ruolo]
                  )}
                </td>
                <td>{quando(m.aggiunto_il)}</td>
                <td>
                  {puoCambiare &&
                    (daRevocare === m.email ? (
                      <span className="conferma-in-riga">
                        <button
                          type="button"
                          className="pericolo"
                          disabled={inCorso}
                          onClick={() =>
                            void esegui(
                              () => cliente.rimuoviMembro(organizzazione, m.email),
                              `${m.email} non fa piu' parte dell'organizzazione.`,
                            )
                          }
                        >
                          Confermi la revoca?
                        </button>
                        <button type="button" onClick={() => setDaRevocare(null)}>
                          Annulla
                        </button>
                      </span>
                    ) : (
                      <button
                        type="button"
                        disabled={inCorso}
                        aria-label={`Revoca ${m.email}`}
                        onClick={() => setDaRevocare(m.email)}
                      >
                        Revoca
                      </button>
                    ))}
                </td>
              </tr>
            ))}
          </tbody>
        </table>
      )}

      {puoCambiare && (
        <fieldset disabled={inCorso}>
          <legend>Invita una persona</legend>
          <label>
            <span>Indirizzo di posta</span>
            <input
              value={nuovaEmail}
              placeholder="collega@agenzia.it"
              onChange={(e) => setNuovaEmail(e.target.value)}
            />
          </label>
          <label>
            <span>Ruolo</span>
            <select value={nuovoRuolo} onChange={(e) => setNuovoRuolo(e.target.value as Ruolo)}>
              {RUOLI.map((r) => (
                <option key={r} value={r}>
                  {NOME_RUOLO[r]}
                </option>
              ))}
            </select>
          </label>
          <small>{COSA_PUO_FARE[nuovoRuolo]}</small>
          <div className="azioni">
            <button
              type="button"
              onClick={() =>
                void esegui(() => {
                  const email = nuovaEmail;
                  setNuovaEmail("");
                  return cliente.scriviMembro(organizzazione, { email, ruolo: nuovoRuolo });
                }, "Invito registrato. La persona vedra' l'organizzazione al prossimo accesso.")
              }
            >
              Aggiungi
            </button>
          </div>
          <small>
            Non parte nessuna posta: l'accesso lo gestisce Access, e questa riga dice soltanto che
            quell'indirizzo, quando entrera', vedra' questa organizzazione.
          </small>
        </fieldset>
      )}
    </section>
  );
}

// ---------------------------------------------------------------------------
// Il registro delle organizzazioni
// ---------------------------------------------------------------------------

function PannelloPiattaforma({
  cliente,
  livello,
}: {
  cliente: ProprietaAmministrazione["cliente"];
  livello: NonNullable<ProprietaAmministrazione["livello"]>;
}) {
  const [organizzazioni, setOrganizzazioni] = useState<OrganizzazioneConMembri[]>([]);
  const [caricamento, setCaricamento] = useState(true);
  const [errori, setErrori] = useState<readonly string[]>([]);
  const [messaggio, setMessaggio] = useState<string | null>(null);
  const [inCorso, setInCorso] = useState(false);
  const [daRimuovere, setDaRimuovere] = useState<string | null>(null);
  const [nuova, setNuova] = useState({ id: "", nome: "", amministratore: "" });

  const puoCreare = livelloSufficiente(livello, "superamministratore");

  const carica = useCallback(() => {
    setCaricamento(true);
    cliente
      .elencaOrganizzazioni()
      .then((elenco) => {
        setOrganizzazioni(elenco);
        setErrori([]);
      })
      .catch((e: unknown) => setErrori([e instanceof Error ? e.message : "errore imprevisto"]))
      .finally(() => setCaricamento(false));
  }, [cliente]);

  useEffect(carica, [carica]);

  async function esegui(operazione: () => Promise<OrganizzazioneConMembri[]>, conferma: string) {
    setInCorso(true);
    setErrori([]);
    setMessaggio(null);
    try {
      setOrganizzazioni(await operazione());
      setMessaggio(conferma);
    } catch (e: unknown) {
      setErrori([e instanceof Error ? e.message : "errore imprevisto"]);
    } finally {
      setInCorso(false);
      setDaRimuovere(null);
    }
  }

  return (
    <section className="scheda">
      <header>
        <h2>Organizzazioni</h2>
        <p className="fascia">
          {COSA_PUO_FARE_SULLA_PIATTAFORMA[livello]} Il tuo livello e' {NOME_LIVELLO[livello]}.
        </p>
      </header>

      <Errori errori={errori} />
      <Conferma messaggio={messaggio} />

      {caricamento ? (
        <p className="attesa">Caricamento...</p>
      ) : (
        <table className="membri">
          <thead>
            <tr>
              <th>Organizzazione</th>
              <th>Identificativo</th>
              <th>Membri</th>
              <th>Dal</th>
              <th />
            </tr>
          </thead>
          <tbody>
            {organizzazioni.map((o) => (
              <tr key={o.id}>
                <td>{o.nome}</td>
                <td className="identificativo">{o.id}</td>
                <td>
                  {o.membri}
                  {o.amministratori === 0 && (
                    <span className="senza-amministratore"> senza amministratore</span>
                  )}
                </td>
                <td>{quando(o.creata_il)}</td>
                <td>
                  {puoCreare &&
                    (daRimuovere === o.id ? (
                      <span className="conferma-in-riga">
                        <button
                          type="button"
                          className="pericolo"
                          disabled={inCorso}
                          onClick={() =>
                            void esegui(
                              () => cliente.rimuoviOrganizzazione(o.id),
                              `${o.nome} e' stata rimossa, con i suoi membri e i suoi immobili.`,
                            )
                          }
                        >
                          Confermi? Porta via tutto
                        </button>
                        <button type="button" onClick={() => setDaRimuovere(null)}>
                          Annulla
                        </button>
                      </span>
                    ) : (
                      <button
                        type="button"
                        disabled={inCorso}
                        aria-label={`Rimuovi ${o.nome}`}
                        onClick={() => setDaRimuovere(o.id)}
                      >
                        Rimuovi
                      </button>
                    ))}
                </td>
              </tr>
            ))}
          </tbody>
        </table>
      )}

      {puoCreare && (
        <fieldset disabled={inCorso}>
          <legend>Nuova organizzazione</legend>
          <label>
            <span>Nome</span>
            <input
              value={nuova.nome}
              placeholder="Agenzia Rossi"
              onChange={(e) => setNuova((n) => ({ ...n, nome: e.target.value }))}
            />
          </label>
          <label>
            <span>Identificativo</span>
            <input
              value={nuova.id}
              placeholder="agenzia-rossi"
              onChange={(e) => setNuova((n) => ({ ...n, id: e.target.value }))}
            />
          </label>
          <small>
            Compare negli indirizzi, quindi lettere minuscole, cifre e trattini. Non si cambia
            piu': conviene sceglierlo breve e stabile.
          </small>
          <label>
            <span>Primo amministratore</span>
            <input
              value={nuova.amministratore}
              placeholder="titolare@agenzia.it"
              onChange={(e) => setNuova((n) => ({ ...n, amministratore: e.target.value }))}
            />
          </label>
          <small>
            Obbligatorio: un'organizzazione senza amministratore non la potrebbe amministrare
            nessuno, e per ripararla servirebbe una scrittura a mano nel database.
          </small>
          <div className="azioni">
            <button
              type="button"
              onClick={() =>
                void esegui(() => {
                  const corpo = { ...nuova };
                  setNuova({ id: "", nome: "", amministratore: "" });
                  return cliente.creaOrganizzazione(corpo);
                }, "Organizzazione creata, con il suo amministratore.")
              }
            >
              Crea
            </button>
          </div>
        </fieldset>
      )}
    </section>
  );
}
