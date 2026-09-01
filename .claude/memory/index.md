# Indice di stato

> Da leggere per primo a inizio sessione. Da' lo stato di sincronizzazione delle schede e il punto di ripresa.

## Snapshot

```
Branch attivo:         main
Commit di riferimento: ff86e78, regime di acquisto per riga
Ultimo aggiornamento:  2026-09-01
Revisione fiscale:     2026-08-28, legge di bilancio 2026 (legge 199/2025)
Verifica Euribor:      2026-09-01, serie BCE 1994-01 / 2026-08
Test:                  61 verdi, 42 sul motore e 19 sulla struttura
Workbook:              21 fogli, ricalcolato con Excel, nessuna cella in errore
```

Gia' committato il 1 settembre, in quattro commit: il blocco delle quotazioni OMI di zona nel foglio Confronto immobili con lo scarto calcolato sul prezzo che il foglio usa, il regime di acquisto per riga con il terzo stato, la normalizzazione dei campi a tre stati, l'avvertenza sul confronto senza mutuo, la sostituzione delle coordinate fisse con nomi definiti nel Cruscotto, e i quattro test relativi.

Non committato, dalla seconda parte della stessa giornata: la cattura delle righe nel conto economico del foglio Locazione e nella tabella dei tre scenari, con la rimozione delle due variabili di ancoraggio rimaste senza usi; il prezzo massimo sostenibile in forma chiusa, con le tre celle dei coefficienti e la cella di verifica accanto; il percorso del tasso a sei gradini nel Simulatore mutuo; `RISALITE_EURIBOR` in `parametri.py`; `risalite_storiche` ed `estremi_storici` in `tassi.py` con l'opzione `--risalita` del comando `tassi`; il nome definito `sim_debito` e le due righe che dicono se il piano si chiude; cinque test nuovi; l'allineamento di `docs/guida-tecnica.md`, `docs/guida-non-tecnica.md`, `docs/metodo-e-metriche.md`, `docs/fonti.md`, `docs/da-zero.md`, `CLAUDE.md` e `README.md`; l'allineamento di memoria e schede di contesto, richiesto esplicitamente dall'utente; le ADR da 013 a 016; le voci da 8 a 11 dello studio didattico con i quattro approfondimenti nuovi. Il commit spetta all'utente.

## Stato delle schede

| Scheda | Copre | Stato |
|---|---|---|
| `.claude/context/STACK.md` | `src/**`, `tools/**` | aggiornata al 1 settembre, da ancorare al commit |
| `.claude/context/design-and-security.md` | `src/immobiliare/annunci.py`, `src/immobiliare/llm_locale.py` | scritta, da ancorare al commit |
| `.claude/context/deployment.md` | `pyproject.toml`, `tools/**` | scritta, da ancorare al commit |
| `.claude/context/dev-testing.md` | `tools/verifica-excel.ps1`, `tests/**` | aggiornata al 1 settembre, da ancorare al commit |
| `.claude/context/current-work.md` | feature attiva | aggiornata al 1 settembre |
| `.claude/context/roadmap.md` | direzione | aggiornata al 1 settembre, sezione "Prossimo" chiusa |
| `.claude/context/studio-didattico-master.md` e gli undici `refactor-NN` | evoluzioni strutturali del progetto | undici voci, allineate al codice corrente |
| `docs/da-zero.md` | avvio, `tools/valuta.py` | allineata, include `tassi --risalita` |
| `docs/fiscalita-acquisto.md` | `src/immobiliare/parametri.py` | allineata alla revisione 2026-08-28 |
| `docs/fiscalita-locazione.md` | `src/immobiliare/parametri.py` | allineata alla revisione 2026-08-28 |
| `docs/due-diligence.md` | foglio Checklist | allineata |
| `docs/perizia-pre-acquisto.md` | foglio Dossier tecnico | allineata, norme lette sui testi primari |
| `docs/aste-immobiliari.md` | foglio Asta | allineata, norme lette sui testi primari |
| `docs/metodo-e-metriche.md` | `src/immobiliare/calcoli.py` | allineata, due sezioni nuove sul prezzo massimo e sullo scenario di stress |
| `docs/raccolta-annunci.md` | `src/immobiliare/annunci.py`, `src/immobiliare/omi.py` | allineata, include blocco OMI e regime per riga |
| `docs/comprare-in-piu-persone.md` | foglio Comproprieta' | allineata |
| `docs/guida-non-tecnica.md` | workbook, tutti i fogli | allineata a ventun fogli |
| `docs/guida-tecnica.md` | workbook e `src/**` | allineata a ventun fogli |
| `docs/fonti.md` | tutte | allineata, include l'uso della serie storica Euribor |

## Che cosa esiste e funziona

Il motore di calcolo in `src/immobiliare/calcoli.py` copre imposte di trasferimento nei quattro casi, prezzo-valore, costo totale dell'operazione, ammortamento alla francese, detrazione degli interessi, conto economico della locazione nei quattro regimi, IMU, plusvalenza, metriche di rendimento, tasso interno di rendimento e confronto fra comprare e affittare.

Il generatore in `src/immobiliare/excel_builder.py` produce un workbook di ventun fogli, venti visibili piu' `_Estrazioni` nascosto, con formule vive e nomi definiti. Si apre sul Cruscotto, che raccoglie i cinque numeri di decisione leggendo solo nomi gia' esistenti: dal 1 settembre nessuna sua formula cita piu' una coordinata di cella, dopo che una di quelle coordinate si e' rivelata puntare alla riga sbagliata e far dire al Cruscotto il contrario del foglio di dettaglio.

Il foglio Rischio porta una simulazione su mille scenari con estrazioni fisse a seme dichiarato e calcolo vivo, piu' un blocco a tornado. Il foglio Asta modella l'acquisto in vendita giudiziaria. Il foglio Dossier tecnico elenca settantatre' documenti da farsi consegnare in trattativa e riporta sul Cruscotto quanti ne mancano. Il foglio Scenari calcola il prezzo massimo sostenibile in forma chiusa, con tre celle visibili per i coefficienti e una cella che ricalcola il rendimento al prezzo trovato e mostra lo scarto dalla soglia, che deve essere zero. Il foglio Simulatore mutuo porta un percorso del tasso a sei gradini, con le peggiori risalite storiche dell'Euribor citate nelle note, e due righe che dicono se il piano si chiude entro i quarant'anni modellati.

Il foglio Confronto immobili applica il modello a ogni riga del registro annunci, con il regime di acquisto dichiarato per riga e il blocco delle quotazioni OMI di zona in coda. Il file e' stato aperto con Excel, ricalcolato integralmente e verificato: nessuna cella in errore. I risultati di sintesi coincidono con quelli del motore Python sullo stesso caso.

Il registro annunci in `src/immobiliare/annunci.py` legge e scrive un CSV di trentacinque campi, cinque dedicati alle vendite giudiziarie e due al regime di acquisto, ed espone con `annunci confronta` la graduatoria per scarto sulla quotazione di zona, riconosce i duplicati per link normalizzato, riversa nel workbook preservando le colonne di formula, e verifica il `robots.txt` prima di ogni prelievo. I quattro campi a tre stati si normalizzano in ingresso.

Il modulo `omi.py` scarica dal mirror open data, importa la fornitura ufficiale e interroga le quotazioni dell'Osservatorio. In cache c'e' la fornitura ufficiale delle Marche 2025/2, 22.347 quotazioni su 1.405 Comuni, accanto al mirror 2018-2 che resta per la serie storica. Il modulo `tassi.py` legge i tassi correnti sulle nuove erogazioni e, con `risalite_storiche` ed `estremi_storici`, misura sulla serie mensile dell'Euribor dal 1994 le peggiori risalite su finestre di dodici, ventiquattro e trentasei mesi. Il modulo `indicatori.py` legge l'euro short-term rate dalla BCE e i prezzi al consumo NIC da ISTAT. Il modulo `llm_locale.py` parla con Ollama.

I test automatici sono sessantuno, in due file: quarantadue sul motore e sui moduli di dominio e diciannove sulla struttura del workbook, sull'acquisizione e sulla graduatoria. Passano tutti, e la verifica con Excel non trova celle in errore.

Il materiale personale sta sotto `_notes/`, ignorato da git, con la mappa in `_notes/INDICE-MATERIALE.md`. Nulla di personale e' tracciato.

## Punto di ripresa

Sul processo: c'e' lavoro non committato, elencato nello snapshot. Il commit spetta all'utente; dopo il commit vanno ancorati i frontmatter delle sette schede di contesto che lo dichiarano.

Sul merito, lo strumento non ha piu' voci di sviluppo aperte con una correzione delimitata, e le tre voci di "Prossimo" della roadmap sono chiuse. Il lavoro utile e' passato dallo strumento all'uso dello strumento: scegliere fra i dodici annunci a registro quello da approfondire, riempire il foglio Immobile con i suoi dati reali, verificare l'aliquota IMU nella delibera del Comune e le spese nel consuntivo condominiale, e chiedere la rendita catastale, che nessuno dei dodici annunci indica ed e' il dato che sblocca il prezzo-valore. Poi si leggono il Cruscotto, la coda bassa del foglio Rischio e il prezzo massimo sostenibile con il suo scarto sul prezzo trattato. Se il mutuo in valutazione e' variabile, il percorso del tasso va compilato con il rialzo storico prima di firmare.

Le direzioni ancora aperte, tutte facoltative, stanno in `roadmap.md` sotto "Piu' avanti": la piu' vicina a essere utile e' l'ammortamento della surroga, perche' un rialzo simulato con il percorso a gradini rende immediata la domanda su quanto convenga surrogare a quel punto del piano. I limiti noti che restano, con la ragione per cui restano, sono elencati fra le domande aperte di `current-work.md`.
