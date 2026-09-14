// Le impalcature comuni alle prove dell'interfaccia.
//
// Stanno in un file proprio e non dentro una delle prove perche' le usano piu' aree, e una
// impalcatura copiata in due file diverge come qualsiasi altra cosa copiata: due prove che
// credono di partire dallo stesso immobile e non lo fanno sono il modo piu' sicuro di passare
// entrambe mentre una delle due non verifica quello che dice di verificare.

import { vi } from "vitest";

import type { Immobile, ImmobileInviato } from "../../src/condiviso/immobile";

/** Un immobile plausibile, con i numeri del caso di riferimento del progetto. */
export function immobileFinto(parziale: Partial<Immobile> = {}): Immobile {
  return {
    id: "i1",
    organizzazione: "o1",
    titolo: "Trilocale via Roma",
    comune: "Civitanova Marche",
    indirizzo: "via Roma 1",
    prezzo: 180_000,
    superficie_mq: 85,
    categoria: "A/2",
    rendita_catastale: 620,
    stato: "da valutare",
    ipotesi: {},
    creato_il: "2026-09-14T10:00:00.000Z",
    aggiornato_il: "2026-09-14T10:00:00.000Z",
    ...parziale,
  };
}

/**
 * Un salvataggio finto che registra il corpo ricevuto e restituisce l'immobile aggiornato.
 *
 * Restituire il corpo salvato e non un oggetto qualunque non e' un dettaglio: il ciclo di bozza
 * riparte da cio' che il server ha accettato, quindi una finzione che restituisse altro
 * proverebbe un comportamento che in esercizio non esiste.
 */
export function salvataggioFinto(base: Immobile | null = null) {
  const inviati: ImmobileInviato[] = [];
  const salva = vi.fn(async (corpo: ImmobileInviato) => {
    inviati.push(corpo);
    return immobileFinto({
      ...corpo,
      id: base?.id ?? "nuovo",
      aggiornato_il: "2026-09-14T12:00:00.000Z",
    });
  });
  return { inviati, salva };
}
