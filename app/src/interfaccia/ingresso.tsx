// Il punto in cui l'applicazione entra nella pagina, e nient'altro.
//
// Resta di dieci righe di proposito: e' l'unico file che tocca il documento HTML, quindi e'
// anche l'unico che non si puo' provare senza un browser, e cio' che non si prova conviene che
// sia poco e che non decida niente.

import { StrictMode } from "react";
import { createRoot } from "react-dom/client";

import { Applicazione } from "./applicazione";
import "./stile.css";

const radice = document.getElementById("radice");
if (!radice) throw new Error("manca l'elemento radice nella pagina");

createRoot(radice).render(
  <StrictMode>
    <Applicazione />
  </StrictMode>,
);
