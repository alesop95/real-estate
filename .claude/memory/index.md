# Indice di stato

> Da leggere per primo a inizio sessione. Da' lo stato di sincronizzazione delle schede e il punto di ripresa.

## Snapshot

```
Branch attivo:         web
Commit di riferimento: 8a6e50d, studio dello stack web
Ultimo aggiornamento:  2026-09-07
Revisione fiscale:     2026-08-28, legge di bilancio 2026 (legge 199/2025)
Verifica Euribor:      2026-09-01, serie BCE 1994-01 / 2026-08
Trattazione LaTeX:     32 pagine, compilata senza avvisi il 2026-09-02
Registro annunci:      14 immobili, non versionato
Pronti alla valutazione: 0 su 14, manca la rendita catastale su tutti
Test:                  78 in Python, 52 sul motore e sui moduli e 26 sulla struttura
Motore TypeScript:     211 vettori di riscontro dal motore Python, tutti passati
Applicazione web:      35 prove verdi in due ambienti, schema e cinque rotte, niente di remoto
Vault Obsidian:        aperto sulla radice, 48 note e 186 collegamenti, nessun orfano
Parametri comunali:    imposta di soggiorno di Civitanova letta il 2026-09-04, IMU da leggere
Workbook:              21 fogli, ricalcolato con Excel, nessuna cella in errore
Simulazione rischio:   fattore comune al 30%, riduzione a indipendenza verificata
Direzione:             applicazione web autenticata su Cloudflare, per ADR-024
Scopo:                 uso proprio piu' vendita a un'agenzia immobiliare, per ADR-025
Branch di lavoro:      web; fase uno del piano chiusa il 7 settembre
```

Committato fino a `5b77739`. I quattro commit del 3 e 4 settembre portano, in ordine: il vault Obsidian aperto sulla radice con la sua configurazione versionata in `docs/`, la conversione dei riferimenti in collegamenti veri con lo strumento che la mantiene, il comando `comune` con il registro delle verifiche comunali, e la pulizia della fornitura OMI dalle righe del Piemonte. Resta da committare il lavoro di tracciatura di questa sessione, cioè le due voci di work-log, le ADR 021 e 022, questa scheda, [`current-work.md`](../context/current-work.md) e il filtro `--regione` all'importazione con i suoi test e la sua documentazione. Non committato il riordino delle cartelle e l'ampliamento della trattazione: `output/` diventa una cartella per immobile sotto `output/immobili/<id>/`, il LaTeX passa sotto `docs/matematica/`, il workbook precompilato non sovrascrive più il file-modello, la trattazione sale a trentadue pagine con il capitolo sulla notazione e ventisette letture a parole, più due sezioni nuove nel manuale operativo e la voce di work-log.

I frontmatter delle schede di contesto restano ancorati ad `a0b3420`, che è il commit del codice di calcolo che descrivono: nulla di quanto è seguito ha cambiato il modello.

## Stato delle schede

| Scheda | Copre | Stato |
|---|---|---|
| [`.claude/context/STACK.md`](../context/STACK.md) | `src/**`, `tools/**` | aggiornata al 1 settembre, da ancorare al commit |
| [`.claude/context/design-and-security.md`](../context/design-and-security.md) | `src/immobiliare/annunci.py`, `src/immobiliare/llm_locale.py` | scritta, da ancorare al commit |
| [`.claude/context/deployment.md`](../context/deployment.md) | `pyproject.toml`, `tools/**` | scritta, da ancorare al commit |
| [`.claude/context/dev-testing.md`](../context/dev-testing.md) | `tools/verifica-excel.ps1`, `tests/**` | aggiornata al 1 settembre, da ancorare al commit |
| [`.claude/context/current-work.md`](../context/current-work.md) | feature attiva | aggiornata al 1 settembre |
| [`.claude/context/roadmap.md`](../context/roadmap.md) | direzione | aggiornata al 1 settembre, sezione "Prossimo" chiusa |
| [`.claude/context/studio-didattico-master.md`](../context/studio-didattico-master.md) e i tredici `refactor-NN` | evoluzioni strutturali del progetto | tredici voci; la tredicesima è la prima che non nasce da una riga di codice, e riguarda il metodo con cui si misura una fascia gratuita |
| [`docs/manuale-operativo.md`](../../docs/manuale-operativo.md) | `tools/valuta.py`, registro, workbook | ogni comando, ogni campo, ogni foglio, diagnostica; include la catena dei tassi e la build LaTeX |
| `docs/matematica/matematica-finanziaria.tex` | tutte le formule del modello | 32 pagine: capitolo sulla notazione per chi parte da zero, 27 paragrafi In parole, derivazioni, tavola simbolo-cella-funzione, caso svolto |
| [`docs/da-zero.md`](../../docs/da-zero.md) | avvio, `tools/valuta.py` | allineata, include `tassi --risalita` e l'indice navigabile |
| [`docs/fiscalita-acquisto.md`](../../docs/fiscalita-acquisto.md) | `src/immobiliare/parametri.py` | allineata alla revisione 2026-08-28 |
| [`docs/fiscalita-locazione.md`](../../docs/fiscalita-locazione.md) | `src/immobiliare/parametri.py` | allineata alla revisione 2026-08-28 |
| [`docs/due-diligence.md`](../../docs/due-diligence.md) | foglio Checklist | allineata |
| [`docs/perizia-pre-acquisto.md`](../../docs/perizia-pre-acquisto.md) | foglio Dossier tecnico | allineata, norme lette sui testi primari |
| [`docs/aste-immobiliari.md`](../../docs/aste-immobiliari.md) | foglio Asta | allineata, norme lette sui testi primari |
| [`docs/metodo-e-metriche.md`](../../docs/metodo-e-metriche.md) | `src/immobiliare/calcoli.py` | allineata, due sezioni nuove sul prezzo massimo e sullo scenario di stress |
| [`docs/raccolta-annunci.md`](../../docs/raccolta-annunci.md) | `src/immobiliare/annunci.py`, `src/immobiliare/omi.py` | allineata, include blocco OMI e regime per riga |
| [`docs/comprare-in-piu-persone.md`](../../docs/comprare-in-piu-persone.md) | foglio Comproprietà | allineata |
| [`docs/guida-al-workbook.md`](../../docs/guida-al-workbook.md) | workbook, tutti i fogli | nata il 3 settembre dalla fusione delle due guide d'uso, in tre parti |
| [`docs/guida-tecnica(catena-calcolo-e-normativa).md`](<../../docs/guida-tecnica(catena-calcolo-e-normativa).md>) | workbook e `src/**` | allineata a ventun fogli |
| [`docs/README.md`](../../docs/README.md) | indice della documentazione | i quattro percorsi di lettura e i quindici documenti per tipo di domanda; dal 3 settembre ogni nome citato è un collegamento vero |
| [`docs/vault-obsidian.md`](../../docs/vault-obsidian.md) | il vault Obsidian aperto sulla radice | configurazione applicata, forma del grafo misurata invece che prevista, e la conversione dei riferimenti con i suoi limiti |
| [`docs/fonti.md`](../../docs/fonti.md) | tutte | allineata, include l'uso della serie storica Euribor |

## Che cosa esiste e funziona

Il motore di calcolo in `src/immobiliare/calcoli.py` copre imposte di trasferimento nei quattro casi, prezzo-valore, costo totale dell'operazione, ammortamento alla francese, detrazione degli interessi, conto economico della locazione nei quattro regimi, IMU, plusvalenza, metriche di rendimento, tasso interno di rendimento e confronto fra comprare e affittare.

Il generatore in `src/immobiliare/excel_builder.py` produce un workbook di ventun fogli, venti visibili più `_Estrazioni` nascosto, con formule vive e nomi definiti. Si apre sul foglio Guida, che dal 1 settembre è un indice navigabile: porta i venti fogli raggruppati in otto fasi del percorso, con un collegamento a ciascuno e, per ognuno, se si compila o si legge, quando si apre e cosa ne esce. Da ogni foglio si torna all'indice con un collegamento in colonna A, scritto dalla funzione del titolo che tutti i fogli chiamano, così che un foglio nuovo non possa nascere senza via di ritorno. La tupla `Costruttore.PERCORSO` è la sorgente unica dell'indice e un test la confronta con i fogli realmente presenti nelle due direzioni.

Il secondo foglio è il Cruscotto, che raccoglie i cinque numeri di decisione leggendo solo nomi già esistenti: dal 1 settembre nessuna sua formula cita più una coordinata di cella, dopo che una di quelle coordinate si è rivelata puntare alla riga sbagliata e far dire al Cruscotto il contrario del foglio di dettaglio.

Il foglio Rischio porta una simulazione su mille scenari con estrazioni fisse a seme dichiarato e calcolo vivo, più un blocco a tornado. Il foglio Asta modella l'acquisto in vendita giudiziaria. Il foglio Dossier tecnico elenca settantatre' documenti da farsi consegnare in trattativa e riporta sul Cruscotto quanti ne mancano. Il foglio Scenari calcola il prezzo massimo sostenibile in forma chiusa, con tre celle visibili per i coefficienti e una cella che ricalcola il rendimento al prezzo trovato e mostra lo scarto dalla soglia, che deve essere zero. Il foglio Simulatore mutuo porta un percorso del tasso a sei gradini, con le peggiori risalite storiche dell'Euribor citate nelle note, e due righe che dicono se il piano si chiude entro i quarant'anni modellati.

Il foglio Confronto immobili applica il modello a ogni riga del registro annunci, con il regime di acquisto dichiarato per riga e il blocco delle quotazioni OMI di zona in coda. Il file è stato aperto con Excel, ricalcolato integralmente e verificato: nessuna cella in errore. I risultati di sintesi coincidono con quelli del motore Python sullo stesso caso.

Il registro annunci in `src/immobiliare/annunci.py` legge e scrive un CSV di trentacinque campi, cinque dedicati alle vendite giudiziarie e due al regime di acquisto, ed espone con `annunci confronta` la graduatoria per scarto sulla quotazione di zona, riconosce i duplicati per link normalizzato, riversa nel workbook preservando le colonne di formula, e verifica il `robots.txt` prima di ogni prelievo. I quattro campi a tre stati si normalizzano in ingresso.

Il modulo `comuni.py` risolve le due voci che non hanno un valore nazionale, aliquota IMU e imposta di soggiorno: costruisce il collegamento agli atti IMU di un Comune dal codice catastale e dalla sigla di provincia letti dalla fornitura OMI, e conserva in `data/comuni-verifiche.csv` il valore che una persona ha letto con la data, traducendola nei quattro esiti che discendono dal termine del 28 ottobre. Non fa rete. Il comando è `valuta.py comune`, e per ADR-021 non esiste e non esisterà una tabella di aliquote congelate.

Il modulo `omi.py` scarica dal mirror open data, importa la fornitura ufficiale con un filtro per regione e in modo atomico, e interroga le quotazioni dell'Osservatorio. In cache c'è la fornitura ufficiale delle Marche 2025/2, 7.093 quotazioni su 225 Comuni, accanto al mirror 2018-2 nazionale che resta per la serie storica. Il file scaricato dall'area riservata portava con sé anche il Piemonte, cioè 15.254 quotazioni su 1.180 Comuni estranei alla valutazione, e per un periodo la scheda ha riportato il totale di 22.347 quotazioni su 1.405 Comuni come se fossero tutte marchigiane: il 4 settembre 2026 le righe del Piemonte sono state rimosse dai due CSV e dall'archivio, quindi i numeri qui sopra sono ora quelli della sola regione richiesta. Il modulo `tassi.py` legge i tassi correnti sulle nuove erogazioni e, con `risalite_storiche` ed `estremi_storici`, misura sulla serie mensile dell'Euribor dal 1994 le peggiori risalite su finestre di dodici, ventiquattro e trentasei mesi. Il modulo `indicatori.py` legge l'euro short-term rate dalla BCE e i prezzi al consumo NIC da ISTAT. Il modulo `llm_locale.py` parla con Ollama.

I test automatici sono sessantatre, in due file: quarantadue sul motore e sui moduli di dominio e ventuno sulla struttura del workbook, sull'acquisizione e sulla graduatoria. Passano tutti, e la verifica con Excel non trova celle in errore.

Il materiale personale sta sotto `_notes/`, ignorato da git, con la mappa in [`_notes/INDICE-MATERIALE.md`](../../_notes/INDICE-MATERIALE.md). Nulla di personale è tracciato.

## Punto di ripresa

Il progetto ha due stati e conviene tenerli distinti. Lo strumento locale è completo, verificato e non ha voci di sviluppo aperte: workbook a ventun fogli che si ricalcola in Excel senza celle in errore, settantasette test verdi, e il quarto dei cinque limiti dichiarati chiuso il 4 settembre con il fattore comune nella simulazione del rischio. Su di esso il lavoro utile è uso e non sviluppo: manca la rendita catastale su tutti i quattordici immobili a registro, ed è il dato che sblocca il prezzo-valore, e l'aliquota IMU di Civitanova si legge aprendo il collegamento che `valuta.py comune --nome "Civitanova Marche"` costruisce, annotandola in `data/comuni-verifiche.csv` con la data.

Lo stato nuovo è la feature attiva, cioè il passaggio ad applicazione web autenticata su Cloudflare, con il doppio scopo di uso proprio e vendita a un'agenzia immobiliare. Vive sul branch `web`, allineato a `main`. È fatto tutto il lavoro che precede il codice: lo studio con le piattaforme misurate sulle fonti primarie, la scelta con il suo prezzo dichiarato in ADR-024, la scelta di prodotto in ADR-025, la riscrittura del vincolo di riservatezza, e la voce 13 dello studio didattico sul metodo di misura di una fascia gratuita. Nessuna riga dell'applicazione esiste ancora.

La prossima azione è la fase uno del piano, che è indipendente dalla piattaforma e non richiede alcun account aperto: il motore di calcolo in TypeScript, il generatore che dal motore Python produce i casi di riscontro, e la suite che li verifica a ogni build. Va per prima perché se sbagliata invalida tutto il resto. In parallelo, quando l'utente apre l'account Cloudflare, valgono i sette passi elencati in [`docs/architettura-web.md`](../../docs/architettura-web.md), di cui il secondo, cioè non collegare mai un metodo di pagamento, è quello che protegge la gratuità.

Le schede di `context/` restano ancorate ad `a0b3420`, che è il commit del codice di calcolo che descrivono. [`STACK.md`](../context/STACK.md) e [`deployment.md`](../context/deployment.md) sono state aggiornate il 4 settembre per il modulo `comuni.py` e per il filtro all'importazione; [`current-work.md`](../context/current-work.md) è stata riscritta il 7 settembre attorno alla feature web. Il modello di calcolo non è stato toccato da nulla di quanto è seguito, quindi non vanno riancorate.

Restano aperte tre cose delimitate, e sono le uniche. La delibera di giunta 7/2023 di Civitanova, che fissa le tariffe dell'imposta di soggiorno lette per ora sulla pagina del concessionario, è un PDF da aprire perché il valore poggi sull'atto. Il limite dei cinquanta utenti dell'autenticazione perimetrale di Cloudflare è l'unico numero dello studio preso da fonti di terzi concordanti e non dalla pagina del fornitore, e va riverificato prima di impegnarsi. E la licenza va rivista, perché MIT permette a chiunque di rivendere lo stesso codice.

I limiti noti che restano sul modello, con la ragione per cui restano, sono elencati fra le domande aperte di [`current-work.md`](../context/current-work.md); tre dei cinque si sciolgono con il passaggio al web, e il quinto, cioè la fornitura OMI che richiede un'autenticazione personale, non dipende da noi.
