// @vitest-environment jsdom
//
// Le prove dell'area immobile, del ciclo di bozza che tutte le aree condividono, e dell'hook
// dell'elenco: cioe' di cio' che le funzioni pure non coprono.
//
// La regola seguita nel ritagliarle e' che qui si prova solo cio' che ha bisogno di un documento:
// il collegamento fra un gesto e una chiamata, il ruolo che disabilita, l'azzeramento della bozza
// quando cambia l'immobile aperto, e la corsa fra due caricamenti. Tutto il resto e' gia' provato
// senza browser, e riprovarlo attraverso un clic costerebbe di piu' e verificherebbe di meno.

import { cleanup, fireEvent, render, renderHook, screen, waitFor } from "@testing-library/react";
import { act } from "react";
import { afterEach, describe, expect, it, vi } from "vitest";

import type { Immobile } from "../../src/condiviso/immobile";
import type { Cliente } from "../../src/interfaccia/cliente";
import { useImmobili } from "../../src/sezioni/immobile/hook";
import { SezioneImmobile } from "../../src/sezioni/immobile/sezione";

import { immobileFinto, salvataggioFinto } from "./finti";
afterEach(cleanup);

describe("l'area immobile", () => {
  it("mostra i dati dell'immobile aperto", () => {
    const { salva } = salvataggioFinto();
    render(
      <SezioneImmobile immobile={immobileFinto()} ruolo="membro" salva={salva} rimuovi={null} />,
    );
    expect((screen.getByLabelText("Titolo") as HTMLInputElement).value).toBe("Trilocale via Roma");
    expect((screen.getByLabelText("Prezzo richiesto") as HTMLInputElement).value).toBe("180000");
  });

  it("a un lettore non offre il salvataggio", () => {
    const { salva } = salvataggioFinto();
    render(
      <SezioneImmobile immobile={immobileFinto()} ruolo="lettore" salva={salva} rimuovi={null} />,
    );
    expect(screen.getByText(/sola lettura/)).toBeTruthy();
    expect(screen.getByRole("button", { name: "Salva" }).hasAttribute("disabled")).toBe(true);
    expect(salva).not.toHaveBeenCalled();
  });

  it("a un membro non offre la cancellazione, che e' dell'amministratore", () => {
    const { salva } = salvataggioFinto();
    const { rerender } = render(
      <SezioneImmobile
        immobile={immobileFinto()}
        ruolo="membro"
        salva={salva}
        rimuovi={async () => undefined}
      />,
    );
    expect(screen.queryByRole("button", { name: "Elimina" })).toBeNull();
    rerender(
      <SezioneImmobile
        immobile={immobileFinto()}
        ruolo="amministratore"
        salva={salva}
        rimuovi={async () => undefined}
      />,
    );
    expect(screen.getByRole("button", { name: "Elimina" })).toBeTruthy();
  });

  it("applica la regola condivisa prima di chiamare il server", async () => {
    const { salva } = salvataggioFinto();
    render(<SezioneImmobile immobile={null} ruolo="membro" salva={salva} rimuovi={null} />);
    fireEvent.click(screen.getByRole("button", { name: /Crea immobile/ }));
    // Il titolo manca: l'errore arriva dal modulo condiviso, senza un giro di rete.
    expect(await screen.findByText("titolo: non puo' essere vuoto")).toBeTruthy();
    expect(salva).not.toHaveBeenCalled();
  });

  it("salvando non cancella le ipotesi scritte dalle altre aree", async () => {
    const altrui = { finanziamento: { importo: 120_000 }, gestione: { canone_mensile: 650 } };
    const base = immobileFinto({ ipotesi: altrui });
    const { inviati, salva } = salvataggioFinto(base);
    render(<SezioneImmobile immobile={base} ruolo="membro" salva={salva} rimuovi={null} />);
    fireEvent.click(screen.getByRole("button", { name: "Salva" }));
    await waitFor(() => expect(inviati.length).toBe(1));
    expect(inviati[0].ipotesi.finanziamento).toEqual(altrui.finanziamento);
    expect(inviati[0].ipotesi.gestione).toEqual(altrui.gestione);
    expect(inviati[0].ipotesi.regime_acquisto).toBeTruthy();
  });

  it("lo stato di una verifica finisce nelle ipotesi salvate", async () => {
    const base = immobileFinto();
    const { inviati, salva } = salvataggioFinto(base);
    render(<SezioneImmobile immobile={base} ruolo="membro" salva={salva} rimuovi={null} />);
    fireEvent.change(screen.getByLabelText(/^Stato: Visura catastale/), {
      target: { value: "fatto" },
    });
    fireEvent.click(screen.getByRole("button", { name: "Salva" }));
    await waitFor(() => expect(inviati.length).toBe(1));
    const verifiche = inviati[0].ipotesi.verifiche as Record<string, { stato: string }>;
    expect(verifiche.v01.stato).toBe("fatto");
  });

  it("ricalcola le imposte mentre si digita il prezzo", async () => {
    const { salva } = salvataggioFinto();
    render(<SezioneImmobile immobile={null} ruolo="membro" salva={salva} rimuovi={null} />);
    fireEvent.change(screen.getByLabelText("Prezzo richiesto"), { target: { value: "200000" } });
    // Duecentomila per il due per cento della prima casa, piu' i due fissi da cinquanta: il numero
    // viene dal motore, qui si verifica soltanto che arrivi a video. Si scrive 4100 e non 4.100
    // perche' l'italiano non raggruppa le migliaia sotto le cinque cifre, e lo spazio prima
    // dell'euro e' unificatore: il confronto passa dalla forma normalizzata.
    expect(await screen.findByText((t) => t.replace(/\s+/g, " ") === "4100 €")).toBeTruthy();
  });

  it("riporta il rifiuto del server invece di far credere che sia andata", async () => {
    const salva = vi.fn(async () => {
      throw new Error("serve il ruolo membro, hai lettore");
    });
    render(<SezioneImmobile immobile={immobileFinto()} ruolo="membro" salva={salva} rimuovi={null} />);
    fireEvent.click(screen.getByRole("button", { name: "Salva" }));
    expect(await screen.findByText("serve il ruolo membro, hai lettore")).toBeTruthy();
  });
});

describe("il ciclo di bozza, comune a tutte le aree", () => {
  it("cambiando immobile aperto riparte dai dati del nuovo", () => {
    // E' il difetto che il ciclo condiviso esiste per rendere impossibile: senza l'azzeramento,
    // la scheda mostrerebbe i dati del primo immobile sotto il nome del secondo, e chi salvasse
    // sovrascriverebbe il secondo con il primo senza che nulla fallisca.
    const { salva } = salvataggioFinto();
    const primo = immobileFinto();
    const secondo = immobileFinto({ id: "i2", titolo: "Bilocale", prezzo: 95_000 });
    const { rerender } = render(
      <SezioneImmobile immobile={primo} ruolo="membro" salva={salva} rimuovi={null} />,
    );
    fireEvent.change(screen.getByLabelText("Titolo"), { target: { value: "modificato a mano" } });
    rerender(<SezioneImmobile immobile={secondo} ruolo="membro" salva={salva} rimuovi={null} />);
    expect((screen.getByLabelText("Titolo") as HTMLInputElement).value).toBe("Bilocale");
    expect((screen.getByLabelText("Prezzo richiesto") as HTMLInputElement).value).toBe("95000");
  });

  it("segnala le modifiche non salvate, e smette dopo il salvataggio", async () => {
    const base = immobileFinto();
    const { salva } = salvataggioFinto(base);
    const { rerender } = render(
      <SezioneImmobile immobile={base} ruolo="membro" salva={salva} rimuovi={null} />,
    );
    expect(screen.queryByText("modifiche non salvate")).toBeNull();
    fireEvent.change(screen.getByLabelText("Comune"), { target: { value: "Macerata" } });
    expect(screen.getByText("modifiche non salvate")).toBeTruthy();

    fireEvent.click(screen.getByRole("button", { name: "Salva" }));
    await waitFor(() => expect(salva).toHaveBeenCalled());
    const salvato = immobileFinto({ comune: "Macerata", aggiornato_il: "2026-09-14T12:00:00.000Z" });
    rerender(<SezioneImmobile immobile={salvato} ruolo="membro" salva={salva} rimuovi={null} />);
    expect(screen.queryByText("modifiche non salvate")).toBeNull();
  });

  it("conserva la conferma del salvataggio anche se l'immobile torna aggiornato", async () => {
    // Il salvataggio fa arrivare un immobile nuovo, quindi il ciclo riazzera la bozza: senza il
    // confronto con l'ultimo salvataggio riuscito, l'azzeramento spegnerebbe il messaggio che
    // dice che e' andata, e l'utente vedrebbe un lampo e nessuna conferma.
    const base = immobileFinto();
    const { salva } = salvataggioFinto(base);
    const { rerender } = render(
      <SezioneImmobile immobile={base} ruolo="membro" salva={salva} rimuovi={null} />,
    );
    fireEvent.click(screen.getByRole("button", { name: "Salva" }));
    await waitFor(() => expect(salva).toHaveBeenCalled());
    const salvato = immobileFinto({ aggiornato_il: "2026-09-14T12:00:00.000Z" });
    rerender(<SezioneImmobile immobile={salvato} ruolo="membro" salva={salva} rimuovi={null} />);
    expect(await screen.findByText(/^Salvato alle/)).toBeTruthy();
  });
});

describe("l'hook dell'elenco", () => {
  it("butta la risposta di un caricamento superato da uno piu' recente", async () => {
    // La corsa che conta: si cambia organizzazione mentre la prima risposta e' in volo, e la prima
    // arriva per ultima. Senza il contrassegno, l'elenco mostrato sarebbe quello di un'altra
    // organizzazione sotto il nome di questa.
    const lente = new Map<string, (v: Immobile[]) => void>();
    const cliente = {
      elencaImmobili: vi.fn(
        (org: string) => new Promise<Immobile[]>((risolvi) => lente.set(org, risolvi)),
      ),
    } as unknown as Cliente;

    const { result, rerender } = renderHook(({ org }: { org: string }) => useImmobili(cliente, org), {
      initialProps: { org: "o1" },
    });
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
