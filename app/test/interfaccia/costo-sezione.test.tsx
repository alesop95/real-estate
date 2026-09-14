// @vitest-environment jsdom
//
// Le prove della schermata del costo dell'operazione, cioe' delle sole cose che hanno bisogno di
// un documento: che non pretenda un immobile che non c'e', che un campo percentuale mostri e
// conservi due numeri diversi, e che un salvataggio da qui non tocchi le altre aree.

import { cleanup, fireEvent, render, screen, waitFor } from "@testing-library/react";
import { afterEach, describe, expect, it } from "vitest";

import { SEZIONE } from "../../src/condiviso/ipotesi";
import { SezioneCosto } from "../../src/sezioni/costo/sezione";

import { immobileFinto, salvataggioFinto } from "./finti";

afterEach(cleanup);

describe("l'area del costo dell'operazione", () => {
  it("senza un immobile aperto dice cosa fare invece di mostrare campi vuoti", () => {
    const { salva } = salvataggioFinto();
    render(<SezioneCosto immobile={null} ruolo="membro" salva={salva} rimuovi={null} />);
    expect(screen.getByText(/Scegli un immobile dall'elenco/)).toBeTruthy();
    expect(screen.queryByLabelText(/Provvigione/)).toBeNull();
  });

  it("mostra il costo totale e l'esborso calcolati dal motore", () => {
    const base = immobileFinto();
    const { salva } = salvataggioFinto(base);
    render(<SezioneCosto immobile={base} ruolo="membro" salva={salva} rimuovi={null} />);
    expect(screen.getByText("Costo totale")).toBeTruthy();
    expect(screen.getByText("Esborso iniziale")).toBeTruthy();
  });

  it("il campo percentuale mostra tre e conserva zero virgola zero tre", async () => {
    // E' la conversione che, ripetuta area per area, prima o poi si dimentica in un punto solo:
    // un'aliquota che valesse tre invece di zero virgola zero tre produrrebbe una provvigione
    // cento volte tanto, senza che nulla fallisca.
    const base = immobileFinto();
    const { inviati, salva } = salvataggioFinto(base);
    render(<SezioneCosto immobile={base} ruolo="membro" salva={salva} rimuovi={null} />);
    const campo = screen.getByLabelText(/^Provvigione dell'agenzia/) as HTMLInputElement;
    expect(campo.value).toBe("3");

    fireEvent.change(campo, { target: { value: "2.5" } });
    fireEvent.click(screen.getByRole("button", { name: "Salva" }));
    await waitFor(() => expect(inviati.length).toBe(1));
    const sezione = inviati[0].ipotesi[SEZIONE.costo] as Record<string, number>;
    expect(sezione.provvigione_aliquota).toBeCloseTo(0.025, 12);
  });

  it("salvando da qui non tocca le verifiche dell'area immobile", async () => {
    const altrui = { v01: { stato: "fatto", note: "visura del 2 settembre" } };
    const base = immobileFinto({ ipotesi: { [SEZIONE.verifiche]: altrui } });
    const { inviati, salva } = salvataggioFinto(base);
    render(<SezioneCosto immobile={base} ruolo="membro" salva={salva} rimuovi={null} />);
    fireEvent.change(screen.getByLabelText(/^Altri costi/), { target: { value: "1500" } });
    fireEvent.click(screen.getByRole("button", { name: "Salva" }));
    await waitFor(() => expect(inviati.length).toBe(1));
    expect(inviati[0].ipotesi[SEZIONE.verifiche]).toEqual(altrui);
    expect((inviati[0].ipotesi[SEZIONE.costo] as Record<string, number>).altri_costi).toBe(1500);
  });

  it("avverte quando la richiesta alla banca supera il rapporto ordinario", () => {
    const base = immobileFinto();
    const { salva } = salvataggioFinto(base);
    render(<SezioneCosto immobile={base} ruolo="membro" salva={salva} rimuovi={null} />);
    expect(screen.queryByText(/supera il/)).toBeNull();
    fireEvent.change(screen.getByLabelText(/^Importo richiesto alla banca/), {
      target: { value: "170000" },
    });
    expect(screen.getByText(/supera il/)).toBeTruthy();
  });

  it("a un lettore non offre il salvataggio", () => {
    const base = immobileFinto();
    const { salva } = salvataggioFinto(base);
    render(<SezioneCosto immobile={base} ruolo="lettore" salva={salva} rimuovi={null} />);
    expect(screen.getByRole("button", { name: "Salva" }).hasAttribute("disabled")).toBe(true);
  });
});
