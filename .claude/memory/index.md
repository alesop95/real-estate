# Indice di stato

> Da leggere per primo a inizio sessione. Da' lo stato di sincronizzazione delle schede e il punto di ripresa.

## Snapshot

```
Branch attivo:         main
Commit di riferimento: 7307fdc, foglio Dossier tecnico
Ultimo aggiornamento:  2026-08-31
Revisione fiscale:     2026-08-28, legge di bilancio 2026 (legge 199/2025)
```

Non committato: la famiglia delle garanzie legali nel Dossier tecnico, il modulo `indicatori.py` con il comando omonimo, il riconoscimento della codifica nella lettura OMI, il promemoria di manutenzione semestrale, l'allineamento di memoria e schede, ADR-009 e ADR-010. In `E:\legal-consultant` e' pronto e non committato il secondo passaggio di audit sul dominio della compravendita. Il commit spetta all'utente, in entrambi i repository.

## Stato delle schede

| Scheda | Copre | Stato |
|---|---|---|
| `.claude/context/STACK.md` | `src/**`, `tools/**` | scritta, da ancorare al commit corrente |
| `.claude/context/design-and-security.md` | `src/immobiliare/annunci.py`, `src/immobiliare/llm_locale.py` | scritta, da ancorare al commit corrente |
| `.claude/context/deployment.md` | `pyproject.toml`, `tools/**` | scritta, da ancorare al commit corrente |
| `.claude/context/dev-testing.md` | `tools/verifica-excel.ps1`, `tests/**` | scritta, da ancorare al commit corrente |
| `.claude/context/current-work.md` | feature attiva | aggiornata |
| `.claude/context/roadmap.md` | direzione | aggiornata |
| `.claude/context/studio-didattico-master.md` e i sette `refactor-NN` | evoluzioni strutturali del progetto | sette voci, allineate al codice corrente |
| `docs/da-zero.md` | avvio, `tools/valuta.py` | allineata |
| `docs/fiscalita-acquisto.md` | `src/immobiliare/parametri.py` | allineata alla revisione 2026-08-28 |
| `docs/fiscalita-locazione.md` | `src/immobiliare/parametri.py` | allineata alla revisione 2026-08-28 |
| `docs/due-diligence.md` | foglio Checklist | allineata |
| `docs/perizia-pre-acquisto.md` | foglio Dossier tecnico | allineata, norme lette sui testi primari |
| `docs/aste-immobiliari.md` | foglio Asta | allineata, norme lette sui testi primari |
| `docs/metodo-e-metriche.md` | `src/immobiliare/calcoli.py` | allineata |
| `docs/raccolta-annunci.md` | `src/immobiliare/annunci.py`, `src/immobiliare/omi.py` | allineata |
| `docs/comprare-in-piu-persone.md` | foglio Comproprieta' | allineata |
| `docs/guida-non-tecnica.md` | workbook, tutti i fogli | allineata a venti fogli |
| `docs/guida-tecnica.md` | workbook e `src/**` | allineata a venti fogli |
| `docs/fonti.md` | tutte | riscritta con l'uso tecnico di ogni fonte |

## Che cosa esiste e funziona

Il motore di calcolo in `src/immobiliare/calcoli.py` copre imposte di trasferimento nei quattro casi, prezzo-valore, costo totale dell'operazione, ammortamento alla francese, detrazione degli interessi, conto economico della locazione nei quattro regimi, IMU, plusvalenza, metriche di rendimento, tasso interno di rendimento e confronto fra comprare e affittare.

Il generatore in `src/immobiliare/excel_builder.py` produce un workbook di ventun fogli, venti visibili piu' `_Estrazioni` nascosto, con formule vive e nomi definiti. Si apre sul Cruscotto, che raccoglie i cinque numeri di decisione leggendo solo nomi gia' esistenti e non puo' quindi divergere dal dettaglio. Il foglio Rischio porta una simulazione su mille scenari con estrazioni fisse a seme dichiarato e calcolo vivo, piu' un blocco a tornado. Il foglio Asta modella l'acquisto in vendita giudiziaria, che differisce dal libero mercato in quattro punti che il modello ordinario non vede. Il foglio Dossier tecnico elenca settantatre' documenti da farsi consegnare in trattativa, e riporta sul Cruscotto quanti ne mancano. Il foglio Confronto immobili applica il modello a ogni riga del registro annunci. Il file e' stato aperto con Excel, ricalcolato integralmente e verificato: nessuna cella in errore, ricalcolo in sei decimi di secondo. I risultati di sintesi coincidono con quelli del motore Python sullo stesso caso.

Il registro annunci in `src/immobiliare/annunci.py` legge e scrive un CSV di ventotto campi, riconosce i duplicati per link normalizzato, riversa nel workbook preservando le colonne di formula, e verifica il `robots.txt` prima di ogni prelievo. Il modulo `omi.py` scarica dal mirror open data, importa la fornitura ufficiale e interroga le quotazioni dell'Osservatorio: legge tutti i file del semestre piu' recente presente in cache ignorando i periodi superati, riconosce il semestre dal nome, dai metadati o in ultimo dalla data del file, e confronta i nomi dei Comuni in forma normalizzata, perche' nella fornitura gli apostrofi e i prefissi agiografici sono scritti in modi diversi. In cache c'e' la fornitura ufficiale delle Marche 2025/2, 22.347 quotazioni su 1.405 Comuni, accanto al mirror 2018-2 che resta per la serie storica. Il modulo `tassi.py` legge dal portale dati della Banca centrale europea i tassi correnti sulle nuove erogazioni e confronta un preventivo con il mercato. Il modulo `indicatori.py` legge l'euro short-term rate dalla BCE e i prezzi al consumo NIC dal servizio SDMX di ISTAT, per tarare l'inflazione assunta dal modello. Il modulo `llm_locale.py` parla con Ollama.

I test automatici sono cinquanta, in due file: quaranta sul motore e sui moduli di dominio e dieci sulla struttura del workbook e sull'acquisizione. Passano tutti, e la verifica con Excel non trova celle in errore.

Il materiale personale sta sotto `_notes/`, ignorato da git, con la mappa in `_notes/INDICE-MATERIALE.md`. Nulla di personale e' tracciato.

## Punto di ripresa

Sul processo: c'e' lavoro non committato, elencato nello snapshot. Il commit spetta all'utente; dopo il commit vanno ancorati i frontmatter delle quattro schede di contesto che lo dichiarano.

Sul merito, la prima cosa utile e' sostituire i valori di esempio del foglio Immobile con quelli di un immobile reale, verificare l'aliquota IMU nella delibera del Comune e le spese nel consuntivo condominiale, poi leggere il Cruscotto e la coda bassa del foglio Rischio: e' il cash flow che si dovra' sostenere ogni mese se le cose vanno male, ed e' il numero che decide se l'operazione e' sostenibile.

Le direzioni aperte restano quelle di `roadmap.md`. Il limite noto piu' rilevante e' che il foglio Confronto immobili applica a tutti gli annunci il regime di acquisto del foglio Immobile.
