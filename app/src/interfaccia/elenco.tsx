// L'elenco degli immobili dell'organizzazione, che sta nel guscio e non in un'area.
//
// La ragione e' la selezione, non l'estetica. Se ogni area tenesse il proprio elenco e la propria
// scelta, passando dall'area immobile a quella del costo ci si troverebbe davanti a un'altra
// scheda, o a nessuna: l'immobile aperto e' una proprieta' della sessione di lavoro, non di una
// schermata, esattamente come nel workbook il foglio Immobile alimenta tutti gli altri. Il
// secondo motivo e' che sei aree con sei elenchi sono sei richieste al server per mostrare la
// stessa lista.

import type { Immobile } from "../condiviso/immobile";

import { euro } from "./formato";

interface Proprieta {
  immobili: readonly Immobile[];
  sceltoId: string | null;
  caricamento: boolean;
  errore: string | null;
  puoCreare: boolean;
  scegli: (id: string | null) => void;
  ricarica: () => void;
}

export function Elenco({
  immobili,
  sceltoId,
  caricamento,
  errore,
  puoCreare,
  scegli,
  ricarica,
}: Proprieta) {
  return (
    <aside className="elenco">
      <div className="elenco-testa">
        <h2>Immobili</h2>
        <button type="button" onClick={() => scegli(null)} disabled={!puoCreare}>
          Nuovo
        </button>
      </div>

      {caricamento && <p className="attesa">Caricamento...</p>}

      {errore && (
        <p className="errore" role="alert">
          {errore}{" "}
          <button type="button" onClick={ricarica}>
            riprova
          </button>
        </p>
      )}

      {!caricamento && !errore && immobili.length === 0 && (
        <p className="vuoto">
          Nessun immobile in questa organizzazione. Il primo si crea qui: bastano un titolo e un
          prezzo, il resto si aggiunge quando lo si conosce.
        </p>
      )}

      <ul>
        {immobili.map((i) => (
          <li key={i.id}>
            <button
              type="button"
              className={i.id === sceltoId ? "voce scelta" : "voce"}
              onClick={() => scegli(i.id)}
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
  );
}
