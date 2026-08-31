# Indice di stato

> Da leggere per primo a inizio sessione. Da' lo stato di sincronizzazione delle schede e il punto di ripresa.

## Snapshot

```
Branch attivo:        main (repository da inizializzare al primo commit)
Commit di riferimento: nessuno, il repository non e' ancora stato committato
Ultimo aggiornamento:  2026-08-28
Revisione fiscale:     2026-08-28, legge di bilancio 2026 (legge 199/2025)
```

## Stato delle schede

| Scheda | Copre | Stato |
|---|---|---|
| `.claude/context/STACK.md` | `src/**`, `tools/**` | scritta, da ancorare al primo commit |
| `.claude/context/design-and-security.md` | `src/immobiliare/annunci.py`, `src/immobiliare/llm_locale.py` | scritta, da ancorare al primo commit |
| `.claude/context/deployment.md` | `pyproject.toml`, `tools/**` | scritta, da ancorare al primo commit |
| `.claude/context/dev-testing.md` | `tools/verifica-excel.ps1`, `tests/**` | scritta, da ancorare al primo commit |
| `.claude/context/current-work.md` | feature attiva | aggiornata |
| `.claude/context/roadmap.md` | direzione | aggiornata |
| `docs/fiscalita-acquisto.md` | `src/immobiliare/parametri.py` | allineata alla revisione 2026-08-28 |
| `docs/fiscalita-locazione.md` | `src/immobiliare/parametri.py` | allineata alla revisione 2026-08-28 |
| `docs/due-diligence.md` | foglio Checklist | allineata |
| `docs/metodo-e-metriche.md` | `src/immobiliare/calcoli.py` | allineata |
| `docs/raccolta-annunci.md` | `src/immobiliare/annunci.py`, `src/immobiliare/omi.py` | allineata |
| `docs/fonti.md` | tutte | allineata |

## Che cosa esiste e funziona

Il motore di calcolo in `src/immobiliare/calcoli.py` copre imposte di trasferimento nei quattro casi, prezzo-valore, costo totale dell'operazione, ammortamento alla francese, detrazione degli interessi, conto economico della locazione nei quattro regimi, IMU, plusvalenza, metriche di rendimento, tasso interno di rendimento e confronto fra comprare e affittare.

Il generatore in `src/immobiliare/excel_builder.py` produce un workbook di sedici fogli con formule vive e nomi definiti, incluso Confronto immobili, che applica il modello a ogni riga del registro e restituisce gli annunci in fila con rendimento netto, cap rate, cash on cash e debt service coverage ratio affiancati. Il file e' stato aperto con Excel, ricalcolato integralmente e verificato: nessuna cella in errore. I risultati di sintesi coincidono con quelli del motore Python sullo stesso caso.

Il registro annunci in `src/immobiliare/annunci.py` legge e scrive un CSV di ventotto campi, riconosce i duplicati per link normalizzato, riversa nel workbook preservando le colonne di formula, e verifica il `robots.txt` prima di ogni prelievo. Il modulo `omi.py` scarica e interroga le quotazioni dell'Osservatorio. Il modulo `llm_locale.py` parla con Ollama e risulta raggiungibile con `qwen3:14b` e `bge-m3`.

I test automatici sono trentanove, in due file: trentatre' sul motore di calcolo e sei sulla struttura del workbook. Passano tutti, e la verifica con Excel non trova celle in errore.

La cartella e' stata riordinata: in radice restano solo i file di progetto, mentre il dossier personale, i riferimenti di terzi e i segnalibri stanno sotto `_notes/`, ignorato da git, con la mappa in `_notes/INDICE-MATERIALE.md`.

## Punto di ripresa

Il repository e' inizializzato con identita' locale e branch `main`, l'albero e' pulito e nulla di personale e' tracciabile. Manca il primo commit, che spetta all'utente. Subito dopo vanno ancorati i frontmatter delle sei schede di contesto e il commit di riferimento di questo snapshot.

Poi, la prima cosa utile sul merito: sostituire i valori di esempio del foglio Immobile con quelli di un immobile reale, verificare l'aliquota IMU nella delibera del Comune e le spese nel consuntivo condominiale, e leggere il foglio Confronto immobili per decidere quale dei tre annunci a registro merita l'approfondimento.
