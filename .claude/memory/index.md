# Indice di stato

> Da leggere per primo a inizio sessione. Da' lo stato di sincronizzazione delle schede e il punto di ripresa.

## Snapshot

```
Branch attivo:         web
Commit di riferimento: 570e988, fase tre con la prima area; la seconda area non e' ancora
                       committata
Ultimo aggiornamento:  2026-09-14
Revisione fiscale:     2026-08-28, legge di bilancio 2026 (legge 199/2025)
Verifica Euribor:      2026-09-01, serie BCE 1994-01 / 2026-08
Trattazione LaTeX:     32 pagine, compilata senza avvisi il 2026-09-02
Registro annunci:      14 immobili, non versionato
Pronti alla valutazione: 0 su 14, manca la rendita catastale su tutti
Test:                  107 in Python: 52 motore e moduli, 26 struttura, 29 rischio
Motore TypeScript:     211 vettori di riscontro dal motore Python, tutti passati
Simulazione rischio:   in Python e in TypeScript, 52 vettori su 64 estrazioni, accordo con
                       Excel entro 1,5e-13 sui trenta numeri del foglio
Applicazione web:      174 prove verdi in due ambienti, schema a due migrazioni, undici rotte,
                       interfaccia con due delle sei aree e l'amministrazione; niente di remoto
Messa in rete:         procedura in nove passi, flusso di distribuzione verde; eseguito il passo 1,
                       cioe' l'account senza metodo di pagamento
Vault Obsidian:        aperto sulla radice, 48 note e 186 collegamenti, nessun orfano
Parametri comunali:    imposta di soggiorno di Civitanova letta il 2026-09-04, IMU da leggere
Workbook:              21 fogli, ricalcolato con Excel, nessuna cella in errore
Fattore comune:        30% predefinito, riduzione a indipendenza verificata, per ADR-023
Direzione:             applicazione web autenticata su Cloudflare, per ADR-024
Scopo:                 uso proprio piu' vendita a un'agenzia immobiliare, per ADR-025
Interfaccia:           React con TypeScript costruito da Vite, servito dal Worker come
                       risorse statiche; aree immobile e costo scritte, quattro da scrivere.
                       Il contesto di lavoro sta nel guscio, per ADR-028
Regole condivise:      app/src/condiviso/, per ADR-027: forma dell'immobile e dell'organizzazione,
                       ruoli e livelli, forma del documento delle ipotesi, catalogo delle trenta
                       verifiche e predefiniti delle dataclass, questi ultimi due generati da Python
Livelli di accesso:    quattro, per ADR-029: lettore, membro e amministratore dentro
                       un'organizzazione, piu' supporto e superamministratore sulla piattaforma.
                       Il livello di piattaforma non legge i dati di alcuna organizzazione
Branch di lavoro:      web; fase uno e parte locale della fase due chiuse il 7 settembre,
                       fase tre cominciata il 14 settembre
```

Committato fino a `570e988`, che apre la fase tre con la catena di costruzione, il modulo condiviso e la prima area dell'interfaccia. La seconda parte della giornata, cioè l'area del costo dell'operazione e l'architettura delle aree, è sul disco e non ancora committata: i comandi sono stati consegnati all'utente, che li esegue a mano. I quattro commit che lo precedono portano in ordine lo scopo commerciale con la piattaforma Cloudflare e la voce didattica 13, la fase uno cioè il motore TypeScript con i duecentoundici vettori, la fase due in locale cioè schema, Worker e rotte autorizzate, e la procedura di messa in rete in nove passi con il flusso che distribuisce.

I frontmatter delle schede di contesto restano ancorati ad `a0b3420`, che è il commit del codice di calcolo che descrivono: nulla di quanto è seguito ha cambiato il modello.

## Stato delle schede

| Scheda | Copre | Stato |
|---|---|---|
| [`.claude/context/STACK.md`](../context/STACK.md) | `src/**`, `tools/**` | aggiornata al 1 settembre, da ancorare al commit |
| [`.claude/context/design-and-security.md`](../context/design-and-security.md) | `src/immobiliare/annunci.py`, `src/immobiliare/llm_locale.py` | scritta, da ancorare al commit |
| [`.claude/context/deployment.md`](../context/deployment.md) | `pyproject.toml`, `tools/**` | scritta, da ancorare al commit |
| [`.claude/context/dev-testing.md`](../context/dev-testing.md) | `tools/verifica-excel.ps1`, `tests/**` | aggiornata al 1 settembre, da ancorare al commit |
| [`.claude/context/current-work.md`](../context/current-work.md) | feature attiva | aggiornata al 14 settembre con la fase tre e la prima area |
| [`.claude/context/roadmap.md`](../context/roadmap.md) | direzione | aggiornata al 1 settembre, sezione "Prossimo" chiusa |
| [`.claude/context/studio-didattico-master.md`](../context/studio-didattico-master.md) e i diciannove `refactor-NN` | evoluzioni strutturali del progetto | diciannove voci; la tredicesima è la prima che non nasce da una riga di codice e riguarda il metodo con cui si misura una fascia gratuita, la quattordicesima è il presidio fra le due implementazioni del motore, la quindicesima è l'autorizzazione dichiarata in un posto solo, la sedicesima è la casualità passata invece che contenuta, la diciassettesima è la regola che vale da due lati e si scrive una volta, la diciottesima è il contesto di lavoro che passa al guscio quando arriva la seconda area, la diciannovesima è il livello di piattaforma con il perimetro definito per sottrazione |
| [`docs/manuale-operativo.md`](../../docs/manuale-operativo.md) | `tools/valuta.py`, registro, workbook | ogni comando, ogni campo, ogni foglio, diagnostica; include la catena dei tassi e la build LaTeX |
| `docs/matematica/matematica-finanziaria.tex` | tutte le formule del modello | 32 pagine: capitolo sulla notazione per chi parte da zero, 27 paragrafi In parole, derivazioni, tavola simbolo-cella-funzione, caso svolto |
| [`docs/da-zero.md`](../../docs/da-zero.md) | avvio, `tools/valuta.py` | allineata, include `tassi --risalita` e l'indice navigabile |
| [`docs/fiscalita-acquisto.md`](../../docs/fiscalita-acquisto.md) | `src/immobiliare/parametri.py` | allineata alla revisione 2026-08-28 |
| [`docs/fiscalita-locazione.md`](../../docs/fiscalita-locazione.md) | `src/immobiliare/parametri.py` | allineata alla revisione 2026-08-28 |
| [`docs/due-diligence.md`](../../docs/due-diligence.md) | foglio Checklist, `src/immobiliare/verifiche.py` | allineata; dal 14 settembre il catalogo delle trenta verifiche è un modulo proprio che alimenta anche l'applicazione |
| [`docs/perizia-pre-acquisto.md`](../../docs/perizia-pre-acquisto.md) | foglio Dossier tecnico | allineata, norme lette sui testi primari |
| [`docs/aste-immobiliari.md`](../../docs/aste-immobiliari.md) | foglio Asta | allineata, norme lette sui testi primari |
| [`docs/metodo-e-metriche.md`](../../docs/metodo-e-metriche.md) | `src/immobiliare/calcoli.py`, `src/immobiliare/rischio.py` | allineata; dal 9 settembre porta la sezione sulle tre implementazioni della simulazione e sui due difetti che il porto ha fatto emergere |
| [`docs/raccolta-annunci.md`](../../docs/raccolta-annunci.md) | `src/immobiliare/annunci.py`, `src/immobiliare/omi.py` | allineata, include blocco OMI e regime per riga |
| [`docs/comprare-in-piu-persone.md`](../../docs/comprare-in-piu-persone.md) | foglio Comproprietà | allineata |
| [`docs/guida-al-workbook.md`](../../docs/guida-al-workbook.md) | workbook, tutti i fogli | nata il 3 settembre dalla fusione delle due guide d'uso, in tre parti |
| [`docs/guida-tecnica(catena-calcolo-e-normativa).md`](<../../docs/guida-tecnica(catena-calcolo-e-normativa).md>) | workbook e `src/**` | allineata a ventun fogli |
| [`docs/README.md`](../../docs/README.md) | indice della documentazione | i quattro percorsi di lettura e i diciotto documenti per tipo di domanda; dal 3 settembre ogni nome citato è un collegamento vero |
| [`docs/vault-obsidian.md`](../../docs/vault-obsidian.md) | il vault Obsidian aperto sulla radice | configurazione applicata, forma del grafo misurata invece che prevista, e la conversione dei riferimenti con i suoi limiti |
| [`docs/architettura-web.md`](../../docs/architettura-web.md) | la scelta della piattaforma | lo studio con le fasce gratuite misurate e le alternative escluse; dall'8 settembre non tiene più la propria lista di passi e rimanda alla procedura |
| [`docs/struttura-del-progetto.md`](../../docs/struttura-del-progetto.md) | `app/**`, la mappa del repository | scritta il 7 settembre, aggiornata l'8 con la cartella dei flussi di lavoro e il 14 con l'interfaccia, le sezioni e il modulo condiviso |
| [`docs/messa-in-rete.md`](../../docs/messa-in-rete.md) | la procedura verso l'esercizio | nove passi, ciascuno con ragione, azione, che cosa riportare e verifica; il registro in fondo dice che il passo 1 è chiuso, e il passo 8 dal 14 settembre si riduce a una sola scrittura a mano |
| [`docs/fonti.md`](../../docs/fonti.md) | tutte | allineata, include l'uso della serie storica Euribor |

## Che cosa esiste e funziona

Il motore di calcolo in `src/immobiliare/calcoli.py` copre imposte di trasferimento nei quattro casi, prezzo-valore, costo totale dell'operazione, ammortamento alla francese, detrazione degli interessi, conto economico della locazione nei quattro regimi, IMU, plusvalenza, metriche di rendimento, tasso interno di rendimento e confronto fra comprare e affittare.

Il generatore in `src/immobiliare/excel_builder.py` produce un workbook di ventun fogli, venti visibili più `_Estrazioni` nascosto, con formule vive e nomi definiti. Si apre sul foglio Guida, che dal 1 settembre è un indice navigabile: porta i venti fogli raggruppati in otto fasi del percorso, con un collegamento a ciascuno e, per ognuno, se si compila o si legge, quando si apre e cosa ne esce. Da ogni foglio si torna all'indice con un collegamento in colonna A, scritto dalla funzione del titolo che tutti i fogli chiamano, così che un foglio nuovo non possa nascere senza via di ritorno. La tupla `Costruttore.PERCORSO` è la sorgente unica dell'indice e un test la confronta con i fogli realmente presenti nelle due direzioni.

Il secondo foglio è il Cruscotto, che raccoglie i cinque numeri di decisione leggendo solo nomi già esistenti: dal 1 settembre nessuna sua formula cita più una coordinata di cella, dopo che una di quelle coordinate si è rivelata puntare alla riga sbagliata e far dire al Cruscotto il contrario del foglio di dettaglio.

Il foglio Rischio porta una simulazione su mille scenari con estrazioni fisse a seme dichiarato e calcolo vivo, più un blocco a tornado. Dal 9 settembre 2026 la stessa simulazione esiste anche in `src/immobiliare/rischio.py` e in `app/src/motore/rischio.ts`, per ADR-026: le estrazioni sono un parametro e non una parte interna, i cinquantadue vettori portano con sé il campione con cui sono stati prodotti, e sui trenta numeri che il foglio mostra le due implementazioni concordano entro 1,5 su dieci alla tredicesima, con i valori misurati in Excel congelati in `tests/test_rischio.py`. Il foglio Asta modella l'acquisto in vendita giudiziaria. Il foglio Dossier tecnico elenca settantatre' documenti da farsi consegnare in trattativa e riporta sul Cruscotto quanti ne mancano. Il foglio Scenari calcola il prezzo massimo sostenibile in forma chiusa, con tre celle visibili per i coefficienti e una cella che ricalcola il rendimento al prezzo trovato e mostra lo scarto dalla soglia, che deve essere zero. Il foglio Simulatore mutuo porta un percorso del tasso a sei gradini, con le peggiori risalite storiche dell'Euribor citate nelle note, e due righe che dicono se il piano si chiude entro i quarant'anni modellati.

Il foglio Confronto immobili applica il modello a ogni riga del registro annunci, con il regime di acquisto dichiarato per riga e il blocco delle quotazioni OMI di zona in coda. Il file è stato aperto con Excel, ricalcolato integralmente e verificato: nessuna cella in errore. I risultati di sintesi coincidono con quelli del motore Python sullo stesso caso.

Il registro annunci in `src/immobiliare/annunci.py` legge e scrive un CSV di trentacinque campi, cinque dedicati alle vendite giudiziarie e due al regime di acquisto, ed espone con `annunci confronta` la graduatoria per scarto sulla quotazione di zona, riconosce i duplicati per link normalizzato, riversa nel workbook preservando le colonne di formula, e verifica il `robots.txt` prima di ogni prelievo. I quattro campi a tre stati si normalizzano in ingresso.

Il modulo `comuni.py` risolve le due voci che non hanno un valore nazionale, aliquota IMU e imposta di soggiorno: costruisce il collegamento agli atti IMU di un Comune dal codice catastale e dalla sigla di provincia letti dalla fornitura OMI, e conserva in `data/comuni-verifiche.csv` il valore che una persona ha letto con la data, traducendola nei quattro esiti che discendono dal termine del 28 ottobre. Non fa rete. Il comando è `valuta.py comune`, e per ADR-021 non esiste e non esisterà una tabella di aliquote congelate.

Il modulo `omi.py` scarica dal mirror open data, importa la fornitura ufficiale con un filtro per regione e in modo atomico, e interroga le quotazioni dell'Osservatorio. In cache c'è la fornitura ufficiale delle Marche 2025/2, 7.093 quotazioni su 225 Comuni, accanto al mirror 2018-2 nazionale che resta per la serie storica. Il file scaricato dall'area riservata portava con sé anche il Piemonte, cioè 15.254 quotazioni su 1.180 Comuni estranei alla valutazione, e per un periodo la scheda ha riportato il totale di 22.347 quotazioni su 1.405 Comuni come se fossero tutte marchigiane: il 4 settembre 2026 le righe del Piemonte sono state rimosse dai due CSV e dall'archivio, quindi i numeri qui sopra sono ora quelli della sola regione richiesta. Il modulo `tassi.py` legge i tassi correnti sulle nuove erogazioni e, con `risalite_storiche` ed `estremi_storici`, misura sulla serie mensile dell'Euribor dal 1994 le peggiori risalite su finestre di dodici, ventiquattro e trentasei mesi. Il modulo `indicatori.py` legge l'euro short-term rate dalla BCE e i prezzi al consumo NIC da ISTAT. Il modulo `llm_locale.py` parla con Ollama.

I test automatici sono centosette, in tre file: cinquantadue sul motore e sui moduli di dominio, ventisei sulla struttura del workbook, sull'acquisizione e sulla graduatoria, ventinove sulla simulazione del rischio. Passano tutti, e la verifica con Excel non trova celle in errore.

Il materiale personale sta sotto `_notes/`, ignorato da git, con la mappa in [`_notes/INDICE-MATERIALE.md`](../../_notes/INDICE-MATERIALE.md). Nulla di personale è tracciato.

## Punto di ripresa

Il progetto ha due stati e conviene tenerli distinti. Lo strumento locale è completo, verificato e non ha voci di sviluppo aperte: workbook a ventun fogli che si ricalcola in Excel senza celle in errore, centosette test verdi, e il quarto dei cinque limiti dichiarati chiuso il 4 settembre con il fattore comune nella simulazione del rischio. Su di esso il lavoro utile è uso e non sviluppo: manca la rendita catastale su tutti i quattordici immobili a registro, ed è il dato che sblocca il prezzo-valore, e l'aliquota IMU di Civitanova si legge aprendo il collegamento che `valuta.py comune --nome "Civitanova Marche"` costruisce, annotandola in `data/comuni-verifiche.csv` con la data.

Lo stato nuovo è la feature attiva, cioè il passaggio ad applicazione web autenticata su Cloudflare, con il doppio scopo di uso proprio e vendita a un'agenzia immobiliare. Vive sul branch `web`, allineato a `main`. È fatto tutto il lavoro che precede il codice: lo studio con le piattaforme misurate sulle fonti primarie, la scelta con il suo prezzo dichiarato in ADR-024, la scelta di prodotto in ADR-025, la riscrittura del vincolo di riservatezza, e la voce 13 dello studio didattico sul metodo di misura di una fascia gratuita. Nessuna riga dell'applicazione esiste ancora.

La prossima azione per la fase due è aprire l'account, e resta in attesa dell'utente. Nel frattempo, il 9 settembre, è stato fatto il lavoro che non lo richiede e che serviva comunque: la simulazione del rischio portata nel motore in Python e in TypeScript, con i cinquantadue vettori che portano le proprie estrazioni e l'accordo con il foglio congelato in un test. È l'ultima parte del modello che aveva una sola implementazione, e la sua conversione ha fatto emergere due difetti reali, l'arrotondamento del mezzo e la divisione per zero del debito residuo a tasso nullo, per cui il racconto sta nella voce 16 dello studio didattico. Il 14 settembre è cominciata la fase tre, che pure non richiede l'account, ed è scritta e provata la prima delle sei aree. Esistono ora tre cose che il giorno prima non c'erano. La catena di costruzione, cioè l'interfaccia React con TypeScript costruita da Vite verso `app/statico/` e servita dallo stesso rilascio del Worker, con il ripiego della pagina singola scritto nel Worker invece che nella configurazione delle risorse statiche, perché quella impostazione scatta prima e risponderebbe HTML anche a una chiamata all'interfaccia di programmazione. La cartella `app/src/condiviso/`, dove per ADR-027 vivono le regole che il Worker e il browser applicano entrambi, cioè la forma di un immobile con la sua validazione e i suoi predefiniti e la gerarchia dei ruoli; dove i due lati non condividono il linguaggio la regola resta presso la fonte e si genera, ed è il caso del catalogo delle trenta verifiche pre-acquisto, uscito dal generatore del foglio Checklist ed emesso in TypeScript come quarta uscita di `tools/genera-motore.py`. E l'area immobile, con anagrafica, regime di acquisto dichiarato per singolo immobile, le verifiche con stato e note, e l'anteprima delle imposte di trasferimento ricalcolata dal motore a ogni battitura: è esatta e non indicativa, perché legge soltanto valori che quell'area determina per intero. Nella stessa giornata è nata anche la seconda area, cioè il costo dell'operazione, e con essa l'architettura che tutte e sei seguiranno: per ADR-028 il contesto di lavoro, cioè l'elenco, l'immobile aperto e il ciclo di salvataggio, appartiene al guscio, e una sezione riceve l'immobile, il ruolo e una funzione che salva, senza il cliente. La forma del documento delle ipotesi è dichiarata una volta in `app/src/condiviso/ipotesi.ts`, dove la conservazione di ciò che un'area non conosce smette di essere una raccomandazione e diventa l'unico modo di scrivere, ai due livelli in cui una perdita è possibile. I valori predefiniti delle dataclass di ingresso sono la quinta uscita del presidio, e i tre che l'introspezione non vede si derivano da dove il progetto li dichiara già, con una prova che chiama il motore con e senza e pretende lo stesso esito. Le prove dell'applicazione salgono da cinquantadue a centotrentadue, la costruzione produce ottantatre kilobyte compressi, e l'applicazione è stata provata in esecuzione con wrangler e un D1 locale, non solo in prova: rifiuto senza identità, non trovato a un estraneo, divieto a un lettore, pagina servita sulla radice, collegamento profondo che ricade sulla pagina e chiamata inesistente che continua a rispondere JSON. La fase uno è chiusa, cioè il motore TypeScript con i duecentoundici vettori generati dal motore Python, e la parte locale della fase due è chiusa, cioè lo schema, il Worker con le cinque rotte autorizzate e le trentacinque prove che girano dentro il runtime di Cloudflare con un D1 vero, senza account e senza rete. L'8 settembre si è aggiunto ciò che serve al passaggio successivo: la procedura in nove passi di [`docs/messa-in-rete.md`](../../docs/messa-in-rete.md), che porta per ogni passo la ragione, l'azione, che cosa riportare e come si verifica, e il flusso `.github/workflows/distribuzione.yml`, che prova a ogni spinta e distribuisce da `main` soltanto dopo che le prove sono passate. Il registro in fondo alla procedura dice che nessuno dei nove passi è stato eseguito, e quel registro è la fonte dello stato di avanzamento.

Dei nove passi, sette li compie chi possiede l'account e due sono dell'ambiente di sviluppo, cioè la configurazione dell'applicazione con i valori di Access e la creazione della prima organizzazione. Il passo che protegge tutto è il primo, ed è verificare che l'account non abbia e non prenda un metodo di pagamento, perché è ciò che rende la gratuità una proprietà del sistema invece di una promessa da sorvegliare. Dopo il passo tre e il passo sei servono all'ambiente di sviluppo tre valori, nessuno dei quali è un segreto: l'identificativo del database, il nome dell'organizzazione Zero Trust e l'etichetta del destinatario di Access. Il solo segreto è il token di interfaccia del passo nove, che sta fra i segreti del repository con il nome `CLOUDFLARE_API_TOKEN` e in nessun altro posto.

Le schede di `context/` restano ancorate ad `a0b3420`, che è il commit del codice di calcolo che descrivono. [`STACK.md`](../context/STACK.md) e [`deployment.md`](../context/deployment.md) sono state aggiornate il 4 settembre per il modulo `comuni.py` e per il filtro all'importazione; [`current-work.md`](../context/current-work.md) è stata riscritta il 7 settembre attorno alla feature web. Il modello di calcolo non è stato toccato da nulla di quanto è seguito, quindi non vanno riancorate.

Restano aperte tre cose delimitate, e sono le uniche. La delibera di giunta 7/2023 di Civitanova, che fissa le tariffe dell'imposta di soggiorno lette per ora sulla pagina del concessionario, è un PDF da aprire perché il valore poggi sull'atto. Il limite dei cinquanta utenti dell'autenticazione perimetrale di Cloudflare è l'unico numero dello studio preso da fonti di terzi concordanti e non dalla pagina del fornitore, e va riverificato prima di impegnarsi. E la licenza va rivista, perché MIT permette a chiunque di rivendere lo stesso codice.

I limiti noti che restano sul modello, con la ragione per cui restano, sono elencati fra le domande aperte di [`current-work.md`](../context/current-work.md); tre dei cinque si sciolgono con il passaggio al web, e il quinto, cioè la fornitura OMI che richiede un'autenticazione personale, non dipende da noi.
