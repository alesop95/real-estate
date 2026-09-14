// L'area immobile: i dati di un immobile, il suo regime di acquisto e le sue verifiche.
//
// E' la prima delle sei aree in cui i ventun fogli del workbook si traducono, e il criterio con
// cui e' stata ritagliata e' quello dichiarato in docs/architettura-web.md: raccoglie cio' che
// descrive l'immobile in se', mentre costi, finanziamento, reddito, decisione e portafoglio
// restano alle altre cinque.
//
// Il file mostra e basta. Ogni regola sta altrove, e la ripartizione e' questa: la forma valida di
// un immobile viene da src/condiviso/immobile.ts, che e' lo stesso modulo che il Worker applica;
// la forma del documento delle ipotesi da src/condiviso/ipotesi.ts; i numeri dal motore,
// attraverso le funzioni pure di modello.ts; il catalogo delle verifiche dal motore Python, che e'
// anche la fonte del foglio Checklist; e il ciclo di modifica e salvataggio da useBozza, che tutte
// le aree condividono. Cio' che resta qui e' la disposizione e i gesti.

import { useMemo } from "react";

import { STATI_IMMOBILE } from "../../condiviso/immobile";
import { ruoloSufficiente } from "../../condiviso/ruoli";
import { FASI_VERIFICA, STATI_VERIFICA, type StatoVerifica } from "../../condiviso/verifiche.generate";
import { useBozza } from "../../interfaccia/bozza";
import {
  Azioni,
  CampoNumero,
  CampoTesto,
  Conferma,
  Errori,
  Interruttore,
  Voce,
} from "../../interfaccia/controlli";
import { euro, numero, percentuale } from "../../interfaccia/formato";
import type { ProprietaSezione } from "../../interfaccia/sezione";

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

export function SezioneImmobile({ immobile, ruolo, salva, rimuovi }: ProprietaSezione) {
  const stato = useBozza<Scheda>(
    immobile,
    (i) => (i ? schedaDa(i) : schedaNuova()),
    (scheda, i) => versoInvio(scheda, i?.ipotesi ?? {}),
    salva,
  );
  const scheda = stato.bozza;

  const puoScrivere = ruoloSufficiente(ruolo, "membro");
  const puoCancellare = ruoloSufficiente(ruolo, "amministratore") && rimuovi !== null;

  const numeri = useMemo(() => anteprima(scheda), [scheda]);
  const verifiche = useMemo(() => verificheInScheda(scheda), [scheda]);
  const aperte = useMemo(() => verificheAperte(scheda), [scheda]);

  const campo = <C extends keyof Scheda>(nome: C, valore: Scheda[C]) =>
    stato.cambia((s) => ({ ...s, [nome]: valore }));

  const regime = (nome: keyof Scheda["regime"], valore: boolean) =>
    stato.cambia((s) => ({ ...s, regime: { ...s.regime, [nome]: valore } }));

  return (
    <section className="scheda">
      <header>
        <h2>{immobile ? scheda.titolo || "Immobile" : "Nuovo immobile"}</h2>
        <p className="fascia">
          Qui si scrive. I numeri della colonna di destra sono calcolati dal motore mentre si
          digita, e non si salvano: si ricavano ogni volta dagli input, che e' la ragione per cui
          non possono diventare falsi quando cambia un'aliquota.
        </p>
      </header>

      <Errori errori={stato.errori} />
      <Conferma messaggio={stato.messaggio} />
      {!puoScrivere && (
        <p className="avviso">
          Il tuo ruolo in questa organizzazione e' di sola lettura: puoi consultare, non modificare.
        </p>
      )}

      <div className="griglia">
        <fieldset disabled={!puoScrivere}>
          <legend>Anagrafica</legend>
          <CampoTesto
            etichetta="Titolo"
            valore={scheda.titolo}
            cambia={(v) => campo("titolo", v)}
            suggerimento="Trilocale via Roma"
          />
          <CampoTesto etichetta="Comune" valore={scheda.comune} cambia={(v) => campo("comune", v)} />
          <CampoTesto
            etichetta="Indirizzo"
            valore={scheda.indirizzo}
            cambia={(v) => campo("indirizzo", v)}
          />
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
          <CampoNumero
            etichetta="Prezzo richiesto"
            valore={scheda.prezzo}
            passo={1000}
            massimo={10_000_000}
            cambia={(v) => campo("prezzo", v)}
          />
          <CampoNumero
            etichetta="Superficie commerciale, mq"
            valore={scheda.superficie_mq}
            massimo={10_000}
            cambia={(v) => campo("superficie_mq", v)}
          />
          <CampoTesto
            etichetta="Categoria catastale"
            valore={scheda.categoria}
            cambia={(v) => campo("categoria", v)}
            suggerimento="A/2"
          />
          <CampoNumero
            etichetta="Rendita catastale"
            valore={scheda.rendita_catastale}
            massimo={100_000}
            cambia={(v) => campo("rendita_catastale", v)}
            nota="E' il dato che sblocca il prezzo-valore. Si chiede al venditore insieme alla superficie calpestabile, con una richiesta sola."
          />
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
            immobile: e' il modo in cui il limite dichiarato del foglio sparisce invece di essere
            aggirato.
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
            Sono le sole voci che questa area determina per intero. Provvigione, notaio e costi del
            mutuo stanno nell'area del costo dell'operazione, e non vengono stimate qui: un numero
            indicativo accanto a numeri esatti si ricorda come esatto.
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
          scritte nella proposta stessa. L'elenco e' lo stesso del foglio Checklist, e viene dalla
          stessa fonte.
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
                          stato.cambia((s) =>
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
                      onChange={(e) => stato.cambia((s) => conVerifica(s, v.id, { note: e.target.value }))}
                    />
                  </li>
                ))}
              </ul>
            </div>
          );
        })}
      </details>

      <Azioni
        puoScrivere={puoScrivere}
        salvataggio={stato.salvataggio}
        modificata={stato.modificata}
        nuovo={immobile === null}
        salva={stato.salva}
        extra={
          puoCancellare && (
            <button
              type="button"
              className="pericolo"
              onClick={() => void rimuovi?.()}
              disabled={stato.salvataggio}
            >
              Elimina
            </button>
          )
        }
      />
    </section>
  );
}
