// L'area del costo dell'operazione: quanta cassa serve davvero per comprare.
//
// E' la seconda delle sei aree, e nel workbook corrisponde al foglio Costo operazione. Mostra e
// basta, come la prima: ogni regola sta nel modello puro accanto, ogni numero viene dal motore.
//
// Una differenza di forma rispetto all'area immobile vale spiegata. Questa area non puo' lavorare
// su un immobile che non esiste ancora, perche' i suoi numeri partono dal prezzo, che appartiene
// all'altra schermata. Invece di riempirsi di controlli sul nulla, il componente si divide in
// due: quello esterno decide se c'e' qualcosa da mostrare, quello interno lavora su un immobile
// che a quel punto esiste per il compilatore e non solo per convinzione. E' la stessa ragione per
// cui il contratto di una sezione porta `rimuovi` a null invece di una funzione che non fa niente.

import { useMemo } from "react";

import type { Immobile } from "../../condiviso/immobile";
import { ruoloSufficiente } from "../../condiviso/ruoli";
import { useBozza } from "../../interfaccia/bozza";
import {
  Azioni,
  CampoNumero,
  CampoPercentuale,
  Conferma,
  Errori,
  Voce,
} from "../../interfaccia/controlli";
import { euro, percentuale } from "../../interfaccia/formato";
import type { ProprietaSezione } from "../../interfaccia/sezione";

import { conCosto, conFinanziamento, riepilogo, schedaDa, versoInvio } from "./modello";
import type { SchedaCosto } from "./tipi";

export function SezioneCosto({ immobile, ruolo, salva }: ProprietaSezione) {
  if (!immobile) {
    return (
      <section className="scheda">
        <h2>Costo dell'operazione</h2>
        <p className="avviso">
          Scegli un immobile dall'elenco, oppure creane uno nell'area Immobile. Il costo
          dell'operazione parte dal prezzo, e senza un immobile non c'e' niente su cui calcolarlo.
        </p>
      </section>
    );
  }
  return <CostoAperto immobile={immobile} ruolo={ruolo} salva={salva} />;
}

function CostoAperto({
  immobile,
  ruolo,
  salva,
}: {
  immobile: Immobile;
  ruolo: ProprietaSezione["ruolo"];
  salva: ProprietaSezione["salva"];
}) {
  const stato = useBozza<SchedaCosto>(
    immobile,
    () => schedaDa(immobile),
    (scheda, i) => versoInvio(scheda, (i ?? immobile) as Immobile),
    salva,
  );
  const scheda = stato.bozza;
  const puoScrivere = ruoloSufficiente(ruolo, "membro");
  const numeri = useMemo(() => riepilogo(scheda, immobile), [scheda, immobile]);

  return (
    <section className="scheda">
      <header>
        <h2>Costo dell'operazione</h2>
        <p className="fascia">
          Il prezzo non e' il costo. Qui si dichiarano le voci che non discendono da una norma ma
          da una trattativa, e il totale che ne esce e' il denominatore con cui si misurera' ogni
          rendimento: usare il prezzo al suo posto gonfia il rendimento di quanto valgono i costi,
          che su un'operazione ordinaria sono quasi il dieci per cento.
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
          <legend>Mediazione e atto</legend>
          <CampoPercentuale
            etichetta="Provvigione dell'agenzia, sul prezzo"
            frazione={scheda.costi.provvigione_aliquota}
            massimo={10}
            cambia={(v) => stato.cambia((s) => conCosto(s, "provvigione_aliquota", v))}
            nota="Si scrive al netto dell'IVA, che il calcolo aggiunge. La provvigione matura alla conclusione dell'affare: se la proposta ha una condizione sospensiva sul mutuo, va escluso per iscritto che sia dovuta quando la condizione non si avvera."
          />
          <CampoNumero
            etichetta="Onorario del notaio per la compravendita"
            valore={scheda.costi.notaio_compravendita}
            passo={100}
            massimo={20_000}
            cambia={(v) => stato.cambia((s) => conCosto(s, "notaio_compravendita", v))}
            nota="Con l'opzione prezzo-valore l'onorario si riduce del trenta per cento per legge: il preventivo va chiesto dichiarando che la si chiedera'."
          />
          <CampoNumero
            etichetta="Altri costi dell'operazione"
            valore={scheda.costi.altri_costi}
            passo={100}
            massimo={100_000}
            cambia={(v) => stato.cambia((s) => conCosto(s, "altri_costi", v))}
            nota="Visure, tecnico di parte, traslochi, allacci: tutto cio' che l'operazione richiede e che nessuna delle altre voci copre."
          />
        </fieldset>

        <fieldset disabled={!puoScrivere}>
          <legend>Mutuo e suoi oneri iniziali</legend>
          <CampoNumero
            etichetta="Importo richiesto alla banca"
            valore={scheda.finanziamento.importo}
            passo={1000}
            massimo={10_000_000}
            cambia={(v) => stato.cambia((s) => conFinanziamento(s, "importo", v))}
            nota="A zero l'operazione e' senza mutuo, e le tre voci qui sotto non entrano nel totale. Tasso e durata governano la rata e stanno nell'area del finanziamento."
          />
          <CampoNumero
            etichetta="Istruttoria"
            valore={scheda.finanziamento.istruttoria}
            passo={50}
            massimo={10_000}
            cambia={(v) => stato.cambia((s) => conFinanziamento(s, "istruttoria", v))}
          />
          <CampoNumero
            etichetta="Perizia"
            valore={scheda.finanziamento.perizia}
            passo={50}
            massimo={10_000}
            cambia={(v) => stato.cambia((s) => conFinanziamento(s, "perizia", v))}
          />
          <CampoNumero
            etichetta="Notaio per l'atto di mutuo"
            valore={scheda.finanziamento.notaio_atto_mutuo}
            passo={100}
            massimo={20_000}
            cambia={(v) => stato.cambia((s) => conFinanziamento(s, "notaio_atto_mutuo", v))}
            nota="E' un secondo atto, con un secondo onorario: chi confronta i preventivi dimenticandolo sottostima di circa mille euro."
          />
        </fieldset>

        <aside className="numeri">
          <h3>Dove vanno i soldi</h3>
          <dl>
            <Voce nome="Prezzo" valore={euro(numeri.prezzo)} />
            <Voce nome={`Imposte (${numeri.regimeImposte})`} valore={euro(numeri.imposteTotali)} />
            <Voce nome="Provvigione, IVA inclusa" valore={euro(numeri.provvigione)} />
            <Voce nome="Notaio, compravendita" valore={euro(numeri.notaioCompravendita)} />
            {numeri.mutuo > 0 && (
              <>
                <Voce nome="Notaio, atto di mutuo" valore={euro(numeri.notaioMutuo)} />
                <Voce nome="Imposta sostitutiva sul mutuo" valore={euro(numeri.sostitutivaMutuo)} />
                <Voce nome="Istruttoria" valore={euro(numeri.istruttoria)} />
                <Voce nome="Perizia" valore={euro(numeri.perizia)} />
              </>
            )}
            {numeri.altriCosti > 0 && <Voce nome="Altri costi" valore={euro(numeri.altriCosti)} />}
            <Voce nome="Costi accessori" valore={euro(numeri.costiAccessori)} />
            <Voce nome="Sul prezzo" valore={percentuale(numeri.incidenzaCosti)} />
            <Voce nome="Costo totale" valore={euro(numeri.costoTotale)} forte />
          </dl>

          <h3>Quanta cassa serve</h3>
          <dl>
            <Voce nome="Mutuo" valore={euro(numeri.mutuo)} />
            <Voce nome="Esborso iniziale" valore={euro(numeri.esborsoIniziale)} forte />
            <Voce
              nome="Mutuo sul prezzo"
              valore={percentuale(numeri.rapportoMutuoPrezzo)}
              segno={numeri.oltreRapportoOrdinario ? "negativo" : undefined}
            />
          </dl>

          {numeri.oltreRapportoOrdinario && (
            <p className="avviso">
              La richiesta supera il {percentuale(numeri.rapportoOrdinarioMassimo)} del prezzo, che
              e' il rapporto oltre il quale una banca di norma non va senza la garanzia del fondo
              pubblico. Non e' impossibile, ma e' un'assunzione: va verificata prima di costruirci
              sopra un piano.
            </p>
          )}

          <p className="nota">
            L'imposta sostitutiva e' trattenuta dalla banca sull'erogato, quindi non si paga: si
            riceve meno. Compare fra i costi perche' il conto non cambia, e chi la dimentica
            scopre in banca che l'accreditato e' inferiore al deliberato.
          </p>
          <p className="nota">
            Il regime delle imposte, cioe' prima casa, prezzo-valore e venditore impresa, si
            dichiara nell'area Immobile e qui si legge soltanto: cambiarlo da due schermate
            significherebbe non sapere piu' dove si cambia.
          </p>
        </aside>
      </div>

      <Azioni
        puoScrivere={puoScrivere}
        salvataggio={stato.salvataggio}
        modificata={stato.modificata}
        nuovo={false}
        salva={stato.salva}
      />
    </section>
  );
}
