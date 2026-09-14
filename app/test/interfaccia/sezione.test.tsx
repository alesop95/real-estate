// @vitest-environment jsdom
//
// Le prove della sezione e del suo hook, cioe' di cio' che le funzioni pure non coprono.
//
// La regola seguita nel ritagliarle e' che qui si prova solo cio' che ha bisogno di un
// documento: il collegamento fra un gesto e una chiamata, il ruolo che disabilita, e la corsa
// fra due caricamenti. Tutto il resto e' gia' provato in modello.test.ts senza browser, e
// riprovarlo attraverso un clic costerebbe di piu' e verificherebbe di meno.
//
// Il cliente e' finto ma il componente e' vero, compreso il suo uso della validazione
// condivisa: e' il punto della fase tre che vale la pena presidiare, perche' se la sezione
// smettesse di applicarla nessuna prova del Worker se ne accorgerebbe.

import { cleanup, fireEvent, render, renderHook, screen, waitFor } from "@testing-library/react";
import { act } from "react";
import { afterEach, describe, expect, it, vi } from "vitest";

import type { Immobile, ImmobileInviato } from "../../src/condiviso/immobile";
import type { Cliente } from "../../src/interfaccia/cliente";
import { useImmobili } from "../../src/sezioni/immobile/hook";
import { SezioneImmobile } from "../../src/sezioni/immobile/sezione";

afterEach(cleanup);

function immobileFinto(parziale: Partial<Immobile> = {}): Immobile {
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

/** Un cliente che risponde da un elenco in memoria e registra cio' che gli si chiede. */
function clienteFinto(iniziali: Immobile[] = []) {
  const inviati: { id: string | null; corpo: ImmobileInviato }[] = [];
  const cliente = {
    io: vi.fn(),
    elencaImmobili: vi.fn(async () => iniziali),
    leggiImmobile: vi.fn(async (_org: string, id: string) => immobileFinto({ id })),
    creaImmobile: vi.fn(async (_org: string, corpo: ImmobileInviato) => {
      inviati.push({ id: null, corpo });
      return immobileFinto({ ...corpo, id: "nuovo", aggiornato_il: "2026-09-14T12:00:00.000Z" });
    }),
    aggiornaImmobile: vi.fn(async (_org: string, id: string, corpo: ImmobileInviato) => {
      inviati.push({ id, corpo });
      return immobileFinto({ ...corpo, id, aggiornato_il: "2026-09-14T12:00:00.000Z" });
    }),
    rimuoviImmobile: vi.fn(async () => undefined),
  };
  return { cliente: cliente as unknown as Cliente, inviati, spie: cliente };
}

describe("la sezione immobile", () => {
  it("mostra gli immobili dell'organizzazione", async () => {
    const { cliente } = clienteFinto([immobileFinto(), immobileFinto({ id: "i2", titolo: "Bilocale" })]);
    render(<SezioneImmobile cliente={cliente} organizzazione="o1" ruolo="membro" />);
    expect(await screen.findByText("Trilocale via Roma")).toBeTruthy();
    expect(screen.getByText("Bilocale")).toBeTruthy();
  });

  it("dice che l'elenco e' vuoto invece di mostrare il nulla", async () => {
    const { cliente } = clienteFinto([]);
    render(<SezioneImmobile cliente={cliente} organizzazione="o1" ruolo="membro" />);
    expect(await screen.findByText(/Nessun immobile in questa organizzazione/)).toBeTruthy();
  });

  it("a un lettore non offre il salvataggio", async () => {
    const { cliente, spie } = clienteFinto([immobileFinto()]);
    render(<SezioneImmobile cliente={cliente} organizzazione="o1" ruolo="lettore" />);
    await screen.findByText("Trilocale via Roma");
    expect(screen.getByText(/sola lettura/)).toBeTruthy();
    expect(screen.getByRole("button", { name: /Crea immobile/ }).hasAttribute("disabled")).toBe(true);
    expect(spie.creaImmobile).not.toHaveBeenCalled();
  });

  it("applica la regola condivisa prima di chiamare il server", async () => {
    const { cliente, spie } = clienteFinto([]);
    render(<SezioneImmobile cliente={cliente} organizzazione="o1" ruolo="membro" />);
    await screen.findByText(/Nessun immobile/);
    fireEvent.click(screen.getByRole("button", { name: /Crea immobile/ }));
    // Il titolo manca: l'errore arriva dal modulo condiviso, senza un giro di rete.
    expect(await screen.findByText("titolo: non puo' essere vuoto")).toBeTruthy();
    expect(spie.creaImmobile).not.toHaveBeenCalled();
  });

  it("salvando non cancella le ipotesi scritte dalle altre aree", async () => {
    const altrui = { finanziamento: { importo: 120_000 } };
    const { cliente, inviati } = clienteFinto([immobileFinto({ ipotesi: altrui })]);
    render(<SezioneImmobile cliente={cliente} organizzazione="o1" ruolo="membro" />);
    fireEvent.click(await screen.findByText("Trilocale via Roma"));
    fireEvent.click(screen.getByRole("button", { name: "Salva" }));
    await waitFor(() => expect(inviati.length).toBe(1));
    expect(inviati[0].corpo.ipotesi.finanziamento).toEqual(altrui.finanziamento);
    expect(inviati[0].corpo.ipotesi.regime_acquisto).toBeTruthy();
  });

  it("lo stato di una verifica finisce nelle ipotesi salvate", async () => {
    const { cliente, inviati } = clienteFinto([immobileFinto()]);
    render(<SezioneImmobile cliente={cliente} organizzazione="o1" ruolo="membro" />);
    fireEvent.click(await screen.findByText("Trilocale via Roma"));
    const scelta = screen.getByLabelText(/^Stato: Visura catastale/);
    fireEvent.change(scelta, { target: { value: "fatto" } });
    fireEvent.click(screen.getByRole("button", { name: "Salva" }));
    await waitFor(() => expect(inviati.length).toBe(1));
    const verifiche = inviati[0].corpo.ipotesi.verifiche as Record<string, { stato: string }>;
    expect(verifiche.v01.stato).toBe("fatto");
  });

  it("ricalcola le imposte mentre si digita il prezzo", async () => {
    const { cliente } = clienteFinto([]);
    render(<SezioneImmobile cliente={cliente} organizzazione="o1" ruolo="membro" />);
    await screen.findByText(/Nessun immobile/);
    const prezzo = screen.getByLabelText("Prezzo richiesto");
    fireEvent.change(prezzo, { target: { value: "200000" } });
    // Duecentomila per il due per cento della prima casa, piu' i due fissi da cinquanta:
    // il numero viene dal motore, qui si verifica soltanto che arrivi a video. Si scrive 4100
    // e non 4.100 perche' l'italiano non raggruppa le migliaia sotto le cinque cifre, e lo
    // spazio prima dell'euro e' unificatore: il confronto passa dalla forma normalizzata.
    const cella = await screen.findByText((t) => t.replace(/\s+/g, " ") === "4100 €");
    expect(cella).toBeTruthy();
  });

  it("riporta il rifiuto del server invece di far credere che sia andata", async () => {
    const { cliente, spie } = clienteFinto([immobileFinto()]);
    spie.aggiornaImmobile.mockRejectedValueOnce(new Error("serve il ruolo membro, hai lettore"));
    render(<SezioneImmobile cliente={cliente} organizzazione="o1" ruolo="membro" />);
    fireEvent.click(await screen.findByText("Trilocale via Roma"));
    fireEvent.click(screen.getByRole("button", { name: "Salva" }));
    expect(await screen.findByText("serve il ruolo membro, hai lettore")).toBeTruthy();
  });
});

describe("l'hook dell'elenco", () => {
  it("butta la risposta di un caricamento superato da uno piu' recente", async () => {
    // La corsa che conta: si cambia organizzazione mentre la prima risposta e' in volo, e la
    // prima arriva per ultima. Senza il contrassegno, l'elenco mostrato sarebbe quello di
    // un'altra organizzazione sotto il nome di questa.
    const lente = new Map<string, (v: Immobile[]) => void>();
    const cliente = {
      elencaImmobili: vi.fn(
        (org: string) => new Promise<Immobile[]>((risolvi) => lente.set(org, risolvi)),
      ),
    } as unknown as Cliente;

    const { result, rerender } = renderHook(
      ({ org }: { org: string }) => useImmobili(cliente, org),
      { initialProps: { org: "o1" } },
    );
    rerender({ org: "o2" });

    await act(async () => {
      lente.get("o2")?.([immobileFinto({ id: "della-seconda", organizzazione: "o2" })]);
      lente.get("o1")?.([immobileFinto({ id: "della-prima", organizzazione: "o1" })]);
    });

    expect(result.current.immobili.map((i) => i.id)).toEqual(["della-seconda"]);
  });

  it("svuota l'elenco quando non c'e' organizzazione", async () => {
    const cliente = { elencaImmobili: vi.fn(async () => [immobileFinto()]) } as unknown as Cliente;
    const { result, rerender } = renderHook(
      ({ org }: { org: string | null }) => useImmobili(cliente, org),
      { initialProps: { org: "o1" as string | null } },
    );
    await waitFor(() => expect(result.current.immobili.length).toBe(1));
    rerender({ org: null });
    await waitFor(() => expect(result.current.immobili.length).toBe(0));
  });

  it("porta fuori l'errore invece di restare in caricamento per sempre", async () => {
    const cliente = {
      elencaImmobili: vi.fn(async () => {
        throw new Error("organizzazione non trovata");
      }),
    } as unknown as Cliente;
    const { result } = renderHook(() => useImmobili(cliente, "o1"));
    await waitFor(() => expect(result.current.errore).toBe("organizzazione non trovata"));
    expect(result.current.caricamento).toBe(false);
  });
});
