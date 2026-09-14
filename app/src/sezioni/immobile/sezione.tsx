// L'area immobile: i dati di un immobile, il suo regime di acquisto e le sue verifiche.
//
// E' la prima delle sei aree in cui i ventun fogli del workbook si traducono, e il criterio
// con cui e' stata ritagliata e' quello dichiarato in docs/architettura-web.md: raccoglie cio'
// che descrive l'immobile in se', mentre costi, finanziamento, reddito, decisione e portafoglio
// restano alle altre cinque.
//
// Il file mostra e basta. Ogni regola sta altrove, e la ripartizione e' questa: la forma valida
// di un immobile viene da src/condiviso/immobile.ts, che e' lo stesso modulo che il Worker
// applica; i numeri vengono dal motore, attraverso le funzioni pure di modello.ts; il catalogo
// delle verifiche viene generato dal motore Python, che e' anche la fonte del foglio Checklist.
// Cio' che resta qui e' la disposizione e i gesti, che sono le due cose che una prova
// automatica verifica peggio e un occhio verifica meglio.

import { useCallback, useEffect, useMemo, useState } from "react";

import type { Immobile, Ipotesi } from "../../condiviso/immobile";
import { STATI_IMMOBILE, validaImmobile } from "../../condiviso/immobile";
import { ruoloSufficiente, type Ruolo } from "../../condiviso/ruoli";
import { FASI_VERIFICA, STATI_VERIFICA, type StatoVerifica } from "../../condiviso/verifiche.generate";
import type { Cliente } from "../../interfaccia/cliente";
import { euro, numero, percentuale, quando } from "../../interfaccia/formato";

import { useImmobili } from "./hook";
import {
  anteprima,
  conVerifica,
  schedaDa,
  schedaNuova,
  verificheAperte,
  verificheInScheda,
  versoInvio,
} from "./modello";
import type { Scheda } from "./tipi";

const NUOVO = "__nuovo__";

interface Proprieta {
  cliente: Cliente;
  organizzazione: string;
  ruolo: Ruolo;
}

export function SezioneImmobile({ cliente, organizzazione, ruolo }: Proprieta) {
  const elenco = useImmobili(cliente, organizzazione);
  const [selezione, setSelezione] = useState<string>(NUOVO);
  const [scheda, setScheda] = useState<Scheda>(schedaNuova);
  const [ipotesiOriginali, setIpotesiOriginali] = useState<Ipotesi>({});
  const [errori, setErrori] = useState<readonly string[]>([]);
  const [messaggio, setMessaggio] = useState<string | null>(null);
  const [salvataggio, setSalvataggio] = useState(false);

  const puoScrivere = ruoloSufficiente(ruolo, "membro");
  const puoCancellare = ruoloSufficiente(ruolo, "amministratore");

  const apri = useCallback((immobile: Immobile | null) => {
    setErrori([]);
    setMessaggio(null);
    if (!immobile) {
      setSelezione(NUOVO);
      setScheda(schedaNuova());
      setIpotesiOriginali({});
      return;
    }
    setSelezione(immobile.id);
    setScheda(schedaDa(immobile));
    setIpotesiOriginali(immobile.ipotesi);
  }, []);

  // Se l'organizzazione cambia, l'immobile aperto non esiste piu' in questo perimetro: si
  // torna alla scheda vuota invece di mostrare i dati di prima sotto un altro nome.
  useEffect(() => {
    apri(null);
  }, [organizzazione, apri]);

  const numeri = useMemo(() => anteprima(scheda), [scheda]);
  const verifiche = useMemo(() => verificheInScheda(scheda), [scheda]);
  const aperte = useMemo(() => verificheAperte(scheda), [scheda]);

  const campo = <C extends keyof Scheda>(nome: C, valore: Scheda[C]) => {
    setScheda((s) => ({ ...s, [nome]: valore }));
    setMessaggio(null);
  };

  const regime = (nome: keyof Scheda["regime"], valore: boolean) => {
    setScheda((s) => ({ ...s, regime: { ...s.regime, [nome]: valore } }));
    setMessaggio(null);
  };

  async function salva() {
    const corpo = versoInvio(scheda, ipotesiOriginali);
    // La stessa funzione che il Worker applichera'. Non e' una seconda validazione: e' la
    // prima applicazione della stessa, fatta dove costa zero invece che dopo un giro di rete.
    const { errori: problemi } = validaImmobile(corpo);
    if (problemi.length) {
      setErrori(problemi);
      return;
    }
    setErrori([]);
    setSalvataggio(true);
    try {
      const salvato =
        selezione === NUOVO
          ? await elenco.crea(corpo)
          : await elenco.aggiorna(selezione, corpo);
      apri(salvato);
      setMessaggio(`Salvato alle ${quando(salvato.aggiornato_il)}.`);
    } catch (e: unknown) {
      setErrori([e instanceof Error ? e.message : "errore imprevisto nel salvataggio"]);
    } finally {
      setSalvataggio(false);
    }
  }

  async function cancella() {
    if (selezione === NUOVO) return;
    setSalvataggio(true);
    try {
      await elenco.rimuovi(selezione);
      apri(null);
      setMessaggio("Immobile rimosso.");
    } catch (e: unknown) {
      setErrori([e instanceof Error ? e.message : "errore imprevisto nella rimozione"]);
    } finally {
      setSalvataggio(false);
    }
  }

  return (
    <div className="area-immobile">
      <aside className="elenco">
        <div className="elenco-testa">
          <h2>Immobili</h2>
          <button type="button" onClick={() => apri(null)} disabled={!puoScrivere}>
            Nuovo
          </button>
        </div>
        {elenco.caricamento && <p className="attesa">Caricamento...</p>}
        {elenco.errore && (
          <p className="errore" role="alert">
            {elenco.errore}{" "}
            <button type="button" onClick={elenco.ricarica}>
              riprova
            </button>
          </p>
        )}
        {!elenco.caricamento && !elenco.errore && elenco.immobili.length === 0 && (
          <p className="vuoto">
            Nessun immobile in questa organizzazione. Il primo si crea qui: bastano un titolo e
            un prezzo, il resto si aggiunge quando lo si conosce.
          </p>
        )}
        <ul>
          {elenco.immobili.map((i) => (
            <li key={i.id}>
              <button
                type="button"
                className={i.id === selezione ? "voce scelta" : "voce"}
                onClick={() => apri(i)}
              >
                <span className="voce-titolo">{i.titolo}</span>
                <span className="voce-dettaglio">
                  {euro(i.prezzo)}
                  {i.comune ? ` - ${i.comune}` : ""}
                </span>
                <span className="voce-stato">{i.stato}</span>
              </button>
            </li>
          ))}
        </ul>
      </aside>

      <section className="scheda">
        <header>
          <h2>{selezione === NUOVO ? "Nuovo immobile" : scheda.titolo || "Immobile"}</h2>
          <p className="fascia">
            Qui si scrive. I numeri della fascia di destra sono calcolati dal motore mentre si
            digita, e non si salvano: si ricavano ogni volta dagli input, che e' la ragione per
            cui non possono diventare falsi quando cambia un'aliquota.
          </p>
        </header>

        {errori.length > 0 && (
          <ul className="errori" role="alert">
            {errori.map((e) => (
              <li key={e}>{e}</li>
            ))}
          </ul>
        )}
        {messaggio && <p className="conferma">{messaggio}</p>}
        {!puoScrivere && (
          <p className="avviso">
            Il tuo ruolo in questa organizzazione e' di sola lettura: puoi consultare, non
            modificare.
          </p>
        )}

        <div className="griglia">
          <fieldset disabled={!puoScrivere}>
            <legend>Anagrafica</legend>
            <label>
              <span>Titolo</span>
              <input
                value={scheda.titolo}
                onChange={(e) => campo("titolo", e.target.value)}
                placeholder="Trilocale via Roma"
              />
            </label>
            <label>
              <span>Comune</span>
              <input value={scheda.comune} onChange={(e) => campo("comune", e.target.value)} />
            </label>
            <label>
              <span>Indirizzo</span>
              <input
                value={scheda.indirizzo}
                onChange={(e) => campo("indirizzo", e.target.value)}
              />
            </label>
            <label>
              <span>Stato</span>
              <select value={scheda.stato} onChange={(e) => campo("stato", e.target.value)}>
                {STATI_IMMOBILE.map((s) => (
                  <option key={s} value={s}>
                    {s}
                  </option>
                ))}
              </select>
            </label>
          </fieldset>

          <fieldset disabled={!puoScrivere}>
            <legend>Prezzo e consistenza</legend>
            <label>
              <span>Prezzo richiesto</span>
              <input
                type="number"
                min={0}
                step={1000}
                value={scheda.prezzo}
                onChange={(e) => campo("prezzo", Number(e.target.value))}
              />
            </label>
            <label>
              <span>Superficie commerciale, mq</span>
              <input
                type="number"
                min={0}
                step={1}
                value={scheda.superficie_mq}
                onChange={(e) => campo("superficie_mq", Number(e.target.value))}
              />
            </label>
            <label>
              <span>Categoria catastale</span>
              <input
                value={scheda.categoria}
                onChange={(e) => campo("categoria", e.target.value)}
                placeholder="A/2"
              />
            </label>
            <label>
              <span>Rendita catastale</span>
              <input
                type="number"
                min={0}
                step={1}
                value={scheda.rendita_catastale}
                onChange={(e) => campo("rendita_catastale", Number(e.target.value))}
              />
              <small>
                E' il dato che sblocca il prezzo-valore. Si chiede al venditore insieme alla
                superficie calpestabile, con una richiesta sola.
              </small>
            </label>
          </fieldset>

          <fieldset disabled={!puoScrivere}>
            <legend>Regime di acquisto</legend>
            <Interruttore
              etichetta="Si chiede l'agevolazione prima casa"
              valore={scheda.regime.prima_casa}
              cambia={(v) => regime("prima_casa", v)}
            />
            <Interruttore
              etichetta="Si chiede il prezzo-valore"
              valore={scheda.regime.prezzo_valore}
              cambia={(v) => regime("prezzo_valore", v)}
            />
            <Interruttore
              etichetta="Venditore impresa, con IVA"
              valore={scheda.regime.venditore_impresa}
              cambia={(v) => regime("venditore_impresa", v)}
            />
            <Interruttore
              etichetta="Nuova costruzione"
              valore={scheda.regime.nuova_costruzione}
              cambia={(v) => regime("nuova_costruzione", v)}
            />
            <small>
              Nel workbook questi quattro valori valgono per l'intera lista. Qui sono di questo
              immobile: e' il modo in cui il limite dichiarato del foglio sparisce invece di
              essere aggirato.
            </small>
          </fieldset>

          <aside className="numeri">
            <h3>Quanto costa il trasferimento</h3>
            <dl>
              <Voce nome="Regime" valore={numeri.regime} />
              <Voce nome="Base imponibile" valore={euro(numeri.imponibile)} />
              {numeri.iva > 0 && <Voce nome="IVA" valore={euro(numeri.iva)} />}
              <Voce nome="Imposta di registro" valore={euro(numeri.registro)} />
              <Voce nome="Ipotecaria" valore={euro(numeri.ipotecaria)} />
              <Voce nome="Catastale" valore={euro(numeri.catastale)} />
              <Voce nome="Totale imposte" valore={euro(numeri.imposteTotali)} forte />
              <Voce nome="Sul prezzo" valore={percentuale(numeri.incidenzaImposte)} />
              <Voce nome="Valore catastale" valore={euro(numeri.valoreCatastale)} />
              <Voce
                nome="Prezzo al mq"
                valore={numeri.prezzoAlMq === null ? "manca la superficie" : euro(numeri.prezzoAlMq)}
              />
              <Voce
                nome="Agevolazione prima casa"
                valore={numeri.agevolazioneApplicabile ? "spetta" : "non spetta"}
              />
            </dl>
            <p className="nota">
              Sono le sole voci che questa area determina per intero. Provvigione, notaio e costi
              del mutuo dipendono da scelte che stanno nell'area del costo dell'operazione, e non
              vengono stimate qui: un numero indicativo accanto a numeri esatti si ricorda come
              esatto.
            </p>
            <p className="nota">
              Verifiche ancora aperte: <strong>{numero(aperte)}</strong> su {verifiche.length}.
            </p>
          </aside>
        </div>

        <details className="verifiche" open>
          <summary>Verifiche prima di firmare ({numero(aperte)} aperte)</summary>
          <p className="fascia">
            Una proposta di acquisto accettata dal venditore e' gia' un contratto preliminare
            vincolante: le verifiche vanno chiuse prima, oppure vanno trasformate in condizioni
            scritte nella proposta stessa. L'elenco e' lo stesso del foglio Checklist, e viene
            dalla stessa fonte.
          </p>
          {FASI_VERIFICA.map((fase) => {
            const diFase = verifiche.filter((v) => v.fase === fase);
            if (diFase.length === 0) return null;
            return (
              <div key={fase} className="fase">
                <h4>{fase}</h4>
                <ul>
                  {diFase.map((v) => (
                    <li key={v.id}>
                      <div className="verifica-testa">
                        <strong>{v.verifica}</strong>
                        <select
                          value={v.stato}
                          disabled={!puoScrivere}
                          aria-label={`Stato: ${v.verifica}`}
                          onChange={(e) =>
                            setScheda((s) =>
                              conVerifica(s, v.id, { stato: e.target.value as StatoVerifica }),
                            )
                          }
                        >
                          {STATI_VERIFICA.map((s) => (
                            <option key={s} value={s}>
                              {s}
                            </option>
                          ))}
                        </select>
                      </div>
                      <p className="perche">{v.percheConta}</p>
                      <p className="fonte">
                        {v.fonte} - la fa: {v.chi}
                      </p>
                      <input
                        className="note"
                        value={v.note}
                        disabled={!puoScrivere}
                        placeholder="Note"
                        aria-label={`Note: ${v.verifica}`}
                        onChange={(e) =>
                          setScheda((s) => conVerifica(s, v.id, { note: e.target.value }))
                        }
                      />
                    </li>
                  ))}
                </ul>
              </div>
            );
          })}
        </details>

        <div className="azioni">
          <button type="button" onClick={salva} disabled={!puoScrivere || salvataggio}>
            {salvataggio ? "Salvataggio..." : selezione === NUOVO ? "Crea immobile" : "Salva"}
          </button>
          {selezione !== NUOVO && (
            <button
              type="button"
              className="pericolo"
              onClick={cancella}
              disabled={!puoCancellare || salvataggio}
            >
              Elimina
            </button>
          )}
        </div>
      </section>
    </div>
  );
}

function Voce({ nome, valore, forte }: { nome: string; valore: string; forte?: boolean }) {
  return (
    <>
      <dt>{nome}</dt>
      <dd className={forte ? "forte" : undefined}>{valore}</dd>
    </>
  );
}

function Interruttore({
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
