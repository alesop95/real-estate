# Indice di stato

> Da leggere per primo a inizio sessione. Da' lo stato di sincronizzazione delle schede e il punto di ripresa.

## Snapshot

```
Branch attivo:         main
Commit di riferimento: a0b3420, righe catturate e prezzo massimo esatto
Ultimo aggiornamento:  2026-09-01
Revisione fiscale:     2026-08-28, legge di bilancio 2026 (legge 199/2025)
Verifica Euribor:      2026-09-01, serie BCE 1994-01 / 2026-08
Trattazione LaTeX:     23 pagine, compilata senza avvisi il 2026-09-02
Registro annunci:      14 immobili, non versionato
Test:                  65 verdi, 44 sul motore e 21 sulla struttura
Workbook:              21 fogli, ricalcolato con Excel, nessuna cella in errore
```

Committato fino a `7fe9747`. Del 2 settembre non e' committato nulla: la catena dei tassi in `tassi.py` con l'opzione del comando, l'analisi dell'effetto inflazione nel motore e nel foglio Metriche, il pacchetto LaTeX istanziato con la trattazione `docs/matematica-finanziaria.tex`, i due annunci nuovi a registro, due test, l'allineamento della documentazione, ADR-018 e la voce di work-log. Resta inoltre non committato il lavoro del 1 settembre sull'indice navigabile e sul manuale operativo, elencato sotto. Non committato: l'indice navigabile del workbook, cioe' il foglio Guida ricostruito con i collegamenti a tutti i fogli, il ritorno all'indice su ogni foglio, l'helper dei collegamenti interni in `stile.py`, l'unificazione degli stati ammessi per un annuncio, due test nuovi, il manuale operativo `docs/manuale-operativo.md`, i rimandi ad esso nelle guide e nel README, ADR-017 e la voce 12 dello studio didattico con l'approfondimento `refactor-12`. I frontmatter delle schede restano ancorati ad `a0b3420`, che e' il commit del codice che descrivono.

Resta fuori dal versionamento, per scelta, il solo `data/annunci.csv` con i dodici immobili a registro, perche' porta i link alle trattative e la colonna del prezzo obiettivo.

## Stato delle schede

| Scheda | Copre | Stato |
|---|---|---|
| `.claude/context/STACK.md` | `src/**`, `tools/**` | aggiornata al 1 settembre, da ancorare al commit |
| `.claude/context/design-and-security.md` | `src/immobiliare/annunci.py`, `src/immobiliare/llm_locale.py` | scritta, da ancorare al commit |
| `.claude/context/deployment.md` | `pyproject.toml`, `tools/**` | scritta, da ancorare al commit |
| `.claude/context/dev-testing.md` | `tools/verifica-excel.ps1`, `tests/**` | aggiornata al 1 settembre, da ancorare al commit |
| `.claude/context/current-work.md` | feature attiva | aggiornata al 1 settembre |
| `.claude/context/roadmap.md` | direzione | aggiornata al 1 settembre, sezione "Prossimo" chiusa |
| `.claude/context/studio-didattico-master.md` e i dodici `refactor-NN` | evoluzioni strutturali del progetto | dodici voci, allineate al codice corrente |
| `docs/manuale-operativo.md` | `tools/valuta.py`, registro, workbook | ogni comando, ogni campo, ogni foglio, diagnostica; include la catena dei tassi e la build LaTeX |
| `docs/matematica-finanziaria.tex` | tutte le formule del modello | nuova il 2 settembre: 23 pagine, derivazioni, tavola simbolo-cella-funzione, caso svolto |
| `docs/da-zero.md` | avvio, `tools/valuta.py` | allineata, include `tassi --risalita` e l'indice navigabile |
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

Il generatore in `src/immobiliare/excel_builder.py` produce un workbook di ventun fogli, venti visibili piu' `_Estrazioni` nascosto, con formule vive e nomi definiti. Si apre sul foglio Guida, che dal 1 settembre e' un indice navigabile: porta i venti fogli raggruppati in otto fasi del percorso, con un collegamento a ciascuno e, per ognuno, se si compila o si legge, quando si apre e cosa ne esce. Da ogni foglio si torna all'indice con un collegamento in colonna A, scritto dalla funzione del titolo che tutti i fogli chiamano, cosi' che un foglio nuovo non possa nascere senza via di ritorno. La tupla `Costruttore.PERCORSO` e' la sorgente unica dell'indice e un test la confronta con i fogli realmente presenti nelle due direzioni.

Il secondo foglio e' il Cruscotto, che raccoglie i cinque numeri di decisione leggendo solo nomi gia' esistenti: dal 1 settembre nessuna sua formula cita piu' una coordinata di cella, dopo che una di quelle coordinate si e' rivelata puntare alla riga sbagliata e far dire al Cruscotto il contrario del foglio di dettaglio.

Il foglio Rischio porta una simulazione su mille scenari con estrazioni fisse a seme dichiarato e calcolo vivo, piu' un blocco a tornado. Il foglio Asta modella l'acquisto in vendita giudiziaria. Il foglio Dossier tecnico elenca settantatre' documenti da farsi consegnare in trattativa e riporta sul Cruscotto quanti ne mancano. Il foglio Scenari calcola il prezzo massimo sostenibile in forma chiusa, con tre celle visibili per i coefficienti e una cella che ricalcola il rendimento al prezzo trovato e mostra lo scarto dalla soglia, che deve essere zero. Il foglio Simulatore mutuo porta un percorso del tasso a sei gradini, con le peggiori risalite storiche dell'Euribor citate nelle note, e due righe che dicono se il piano si chiude entro i quarant'anni modellati.

Il foglio Confronto immobili applica il modello a ogni riga del registro annunci, con il regime di acquisto dichiarato per riga e il blocco delle quotazioni OMI di zona in coda. Il file e' stato aperto con Excel, ricalcolato integralmente e verificato: nessuna cella in errore. I risultati di sintesi coincidono con quelli del motore Python sullo stesso caso.

Il registro annunci in `src/immobiliare/annunci.py` legge e scrive un CSV di trentacinque campi, cinque dedicati alle vendite giudiziarie e due al regime di acquisto, ed espone con `annunci confronta` la graduatoria per scarto sulla quotazione di zona, riconosce i duplicati per link normalizzato, riversa nel workbook preservando le colonne di formula, e verifica il `robots.txt` prima di ogni prelievo. I quattro campi a tre stati si normalizzano in ingresso.

Il modulo `omi.py` scarica dal mirror open data, importa la fornitura ufficiale e interroga le quotazioni dell'Osservatorio. In cache c'e' la fornitura ufficiale delle Marche 2025/2, 22.347 quotazioni su 1.405 Comuni, accanto al mirror 2018-2 che resta per la serie storica. Il modulo `tassi.py` legge i tassi correnti sulle nuove erogazioni e, con `risalite_storiche` ed `estremi_storici`, misura sulla serie mensile dell'Euribor dal 1994 le peggiori risalite su finestre di dodici, ventiquattro e trentasei mesi. Il modulo `indicatori.py` legge l'euro short-term rate dalla BCE e i prezzi al consumo NIC da ISTAT. Il modulo `llm_locale.py` parla con Ollama.

I test automatici sono sessantatre, in due file: quarantadue sul motore e sui moduli di dominio e ventuno sulla struttura del workbook, sull'acquisizione e sulla graduatoria. Passano tutti, e la verifica con Excel non trova celle in errore.

Il materiale personale sta sotto `_notes/`, ignorato da git, con la mappa in `_notes/INDICE-MATERIALE.md`. Nulla di personale e' tracciato.

## Punto di ripresa

Sul processo resta da committare il lavoro sull'indice navigabile e sul manuale operativo, elencato nello snapshot; le schede restano ancorate ad `a0b3420`, che e' il commit del codice di calcolo che descrivono, e non vanno riancorate per una modifica che riguarda navigazione e documentazione.

Sul merito, lo strumento non ha piu' voci di sviluppo aperte con una correzione delimitata, e le tre voci di "Prossimo" della roadmap sono chiuse. Il lavoro utile e' passato dallo strumento all'uso dello strumento: scegliere fra i dodici annunci a registro quello da approfondire, riempire il foglio Immobile con i suoi dati reali, verificare l'aliquota IMU nella delibera del Comune e le spese nel consuntivo condominiale, e chiedere la rendita catastale, che nessuno dei dodici annunci indica ed e' il dato che sblocca il prezzo-valore. Poi si leggono il Cruscotto, la coda bassa del foglio Rischio e il prezzo massimo sostenibile con il suo scarto sul prezzo trattato. Se il mutuo in valutazione e' variabile, il percorso del tasso va compilato con il rialzo storico prima di firmare.

Le direzioni ancora aperte, tutte facoltative, stanno in `roadmap.md` sotto "Piu' avanti": la piu' vicina a essere utile e' l'ammortamento della surroga, perche' un rialzo simulato con il percorso a gradini rende immediata la domanda su quanto convenga surrogare a quel punto del piano. I limiti noti che restano, con la ragione per cui restano, sono elencati fra le domande aperte di `current-work.md`.
