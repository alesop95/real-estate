// @vitest-environment jsdom
//
// Le prove della schermata di amministrazione, cioe' di cio' che decide chi vede che cosa.
//
// Qui la coppia permesso e negato conta piu' che altrove, e non perche' il browser sia una difesa:
// non lo e', e il Worker riapplica ogni controllo. Conta perche' un pannello dei permessi che
// mostra un gesto impossibile insegna a chi lo usa che i rifiuti sono normali, e da quel momento
// in poi nessun rifiuto viene piu' letto. La difesa sta nel server, la chiarezza sta qui, e la
// seconda si rompe in silenzio.

import { cleanup, fireEvent, render, screen, waitFor } from "@testing-library/react";
import { afterEach, describe, expect, it, vi } from "vitest";

import type { Membro, OrganizzazioneConMembri } from "../../src/condiviso/organizzazione";
import type { Cliente } from "../../src/interfaccia/cliente";
import { SezioneAmministrazione } from "../../src/sezioni/amministrazione/sezione";

afterEach(cleanup);

const MEMBRI: Membro[] = [
  { email: "capo@a.invalid", ruolo: "amministratore", aggiunto_il: "2026-09-07T08:00:00.000Z" },
  { email: "socio@a.invalid", ruolo: "membro", aggiunto_il: "2026-09-07T08:00:00.000Z" },
  { email: "ospite@a.invalid", ruolo: "lettore", aggiunto_il: "2026-09-07T08:00:00.000Z" },
];

const ORGANIZZAZIONI: OrganizzazioneConMembri[] = [
  { id: "agenzia-a", nome: "Agenzia A", creata_il: "2026-09-07T08:00:00.000Z", membri: 3, amministratori: 1 },
  { id: "agenzia-b", nome: "Agenzia B", creata_il: "2026-09-07T08:00:00.000Z", membri: 1, amministratori: 0 },
];

function clienteFinto(sovrascrivi: Partial<Record<string, unknown>> = {}) {
  const spie = {
    elencaMembri: vi.fn(async () => MEMBRI),
    scriviMembro: vi.fn(async () => MEMBRI),
    rimuoviMembro: vi.fn(async () => MEMBRI.slice(0, 2)),
    elencaOrganizzazioni: vi.fn(async () => ORGANIZZAZIONI),
    creaOrganizzazione: vi.fn(async () => ORGANIZZAZIONI),
    rimuoviOrganizzazione: vi.fn(async () => ORGANIZZAZIONI.slice(0, 1)),
    ...sovrascrivi,
  };
  return { cliente: spie as unknown as Cliente, spie };
}

describe("chi fa parte dell'organizzazione", () => {
  it("un membro vede l'elenco e non i comandi per cambiarlo", async () => {
    const { cliente } = clienteFinto();
    render(
      <SezioneAmministrazione cliente={cliente} organizzazione="agenzia-a" ruolo="membro" livello={null} />,
    );
    expect(await screen.findByText("capo@a.invalid")).toBeTruthy();
    expect(screen.getByText(/Per invitare o revocare serve il ruolo di amministratore/)).toBeTruthy();
    expect(screen.queryByLabelText(/^Ruolo di /)).toBeNull();
    expect(screen.queryByRole("button", { name: /^Revoca / })).toBeNull();
  });

  it("un amministratore cambia il ruolo di un collega", async () => {
    const { cliente, spie } = clienteFinto();
    render(
      <SezioneAmministrazione
        cliente={cliente}
        organizzazione="agenzia-a"
        ruolo="amministratore"
        livello={null}
      />,
    );
    const scelta = await screen.findByLabelText("Ruolo di socio@a.invalid");
    fireEvent.change(scelta, { target: { value: "amministratore" } });
    await waitFor(() => expect(spie.scriviMembro).toHaveBeenCalled());
    expect(spie.scriviMembro).toHaveBeenCalledWith("agenzia-a", {
      email: "socio@a.invalid",
      ruolo: "amministratore",
    });
  });

  it("la revoca chiede conferma in due tempi invece di una finestra di sistema", async () => {
    // Una finestra di sistema si chiude per riflesso, e il gesto che si conferma qui toglie a una
    // persona l'accesso all'archivio dell'agenzia.
    const { cliente, spie } = clienteFinto();
    render(
      <SezioneAmministrazione
        cliente={cliente}
        organizzazione="agenzia-a"
        ruolo="amministratore"
        livello={null}
      />,
    );
    fireEvent.click(await screen.findByLabelText("Revoca ospite@a.invalid"));
    expect(spie.rimuoviMembro).not.toHaveBeenCalled();
    fireEvent.click(screen.getByRole("button", { name: "Confermi la revoca?" }));
    await waitFor(() => expect(spie.rimuoviMembro).toHaveBeenCalledWith("agenzia-a", "ospite@a.invalid"));
  });

  it("si puo' cambiare idea prima di confermare", async () => {
    const { cliente, spie } = clienteFinto();
    render(
      <SezioneAmministrazione
        cliente={cliente}
        organizzazione="agenzia-a"
        ruolo="amministratore"
        livello={null}
      />,
    );
    fireEvent.click(await screen.findByLabelText("Revoca ospite@a.invalid"));
    fireEvent.click(screen.getByRole("button", { name: "Annulla" }));
    expect(screen.queryByRole("button", { name: "Confermi la revoca?" })).toBeNull();
    expect(spie.rimuoviMembro).not.toHaveBeenCalled();
  });

  it("il rifiuto sull'ultimo amministratore arriva a video con la ragione", async () => {
    const messaggio =
      "e' l'ultimo amministratore dell'organizzazione: nominane un altro prima di revocare questo";
    const { cliente } = clienteFinto({
      rimuoviMembro: vi.fn(async () => {
        throw new Error(messaggio);
      }),
    });
    render(
      <SezioneAmministrazione
        cliente={cliente}
        organizzazione="agenzia-a"
        ruolo="amministratore"
        livello={null}
      />,
    );
    fireEvent.click(await screen.findByLabelText("Revoca capo@a.invalid"));
    fireEvent.click(screen.getByRole("button", { name: "Confermi la revoca?" }));
    expect(await screen.findByText(messaggio)).toBeTruthy();
  });

  it("invita una persona con l'indirizzo e il ruolo scelti", async () => {
    const { cliente, spie } = clienteFinto();
    render(
      <SezioneAmministrazione
        cliente={cliente}
        organizzazione="agenzia-a"
        ruolo="amministratore"
        livello={null}
      />,
    );
    fireEvent.change(await screen.findByLabelText("Indirizzo di posta"), {
      target: { value: "nuovo@a.invalid" },
    });
    fireEvent.change(screen.getByLabelText("Ruolo"), { target: { value: "lettore" } });
    fireEvent.click(screen.getByRole("button", { name: "Aggiungi" }));
    await waitFor(() =>
      expect(spie.scriviMembro).toHaveBeenCalledWith("agenzia-a", {
        email: "nuovo@a.invalid",
        ruolo: "lettore",
      }),
    );
  });

  it("chi non appartiene a nessuna organizzazione lo legge invece di vedere una tabella vuota", () => {
    const { cliente, spie } = clienteFinto();
    render(<SezioneAmministrazione cliente={cliente} organizzazione={null} ruolo={null} livello={null} />);
    expect(screen.getByText(/Non appartieni ad alcuna organizzazione/)).toBeTruthy();
    expect(spie.elencaMembri).not.toHaveBeenCalled();
  });
});

describe("il registro delle organizzazioni", () => {
  it("senza livello di piattaforma il pannello non esiste", async () => {
    const { cliente, spie } = clienteFinto();
    render(
      <SezioneAmministrazione cliente={cliente} organizzazione="agenzia-a" ruolo="amministratore" livello={null} />,
    );
    await screen.findByText("capo@a.invalid");
    expect(screen.queryByText("Organizzazioni")).toBeNull();
    expect(spie.elencaOrganizzazioni).not.toHaveBeenCalled();
  });

  it("il supporto legge il registro e non trova il modulo per creare", async () => {
    const { cliente } = clienteFinto();
    render(
      <SezioneAmministrazione cliente={cliente} organizzazione={null} ruolo={null} livello="supporto" />,
    );
    expect(await screen.findByText("Agenzia A")).toBeTruthy();
    expect(screen.queryByText("Nuova organizzazione")).toBeNull();
    expect(screen.queryByRole("button", { name: /^Rimuovi / })).toBeNull();
  });

  it("il superamministratore crea un'organizzazione con il suo primo amministratore", async () => {
    const { cliente, spie } = clienteFinto();
    render(
      <SezioneAmministrazione
        cliente={cliente}
        organizzazione={null}
        ruolo={null}
        livello="superamministratore"
      />,
    );
    fireEvent.change(await screen.findByLabelText("Nome"), { target: { value: "Agenzia Rossi" } });
    fireEvent.change(screen.getByLabelText("Identificativo"), { target: { value: "agenzia-rossi" } });
    fireEvent.change(screen.getByLabelText("Primo amministratore"), {
      target: { value: "titolare@rossi.invalid" },
    });
    fireEvent.click(screen.getByRole("button", { name: "Crea" }));
    await waitFor(() =>
      expect(spie.creaOrganizzazione).toHaveBeenCalledWith({
        nome: "Agenzia Rossi",
        id: "agenzia-rossi",
        amministratore: "titolare@rossi.invalid",
      }),
    );
  });

  it("segnala un'organizzazione rimasta senza amministratori", async () => {
    // L'invariante difeso in membri.ts rende questo stato irraggiungibile dall'applicazione: se
    // compare, viene da una scrittura fatta fuori di qui, e va visto perche' nessuno la puo' piu'
    // amministrare dal pannello.
    const { cliente } = clienteFinto();
    render(
      <SezioneAmministrazione
        cliente={cliente}
        organizzazione={null}
        ruolo={null}
        livello="superamministratore"
      />,
    );
    expect(await screen.findByText(/senza amministratore/)).toBeTruthy();
  });

  it("la rimozione di un'organizzazione chiede conferma, e dice che porta via tutto", async () => {
    const { cliente, spie } = clienteFinto();
    render(
      <SezioneAmministrazione
        cliente={cliente}
        organizzazione={null}
        ruolo={null}
        livello="superamministratore"
      />,
    );
    fireEvent.click(await screen.findByLabelText("Rimuovi Agenzia B"));
    expect(spie.rimuoviOrganizzazione).not.toHaveBeenCalled();
    fireEvent.click(screen.getByRole("button", { name: "Confermi? Porta via tutto" }));
    await waitFor(() => expect(spie.rimuoviOrganizzazione).toHaveBeenCalledWith("agenzia-b"));
  });
});
