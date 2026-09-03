# real-estate

> Istruzioni di team, versionate. Questo file e' l'indice del progetto: indicizza i soli file satellite tracciati e descrive la procedura di ripresa. Le preferenze personali vivono in `CLAUDE.local.md`, ignorato da git, non qui.

## Cos'e' questo progetto

Strumento locale per valutare l'acquisto di un immobile residenziale in Italia, in tutte e tre le destinazioni possibili: abitazione propria, messa a reddito, investimento puro. Produce un workbook Excel di ventun fogli con formule vive, quindi interattivo, che copre il cruscotto di sintesi, il costo reale dell'operazione, il mutuo con simulatore e piano di ammortamento, i regimi fiscali della locazione a confronto, la proiezione del flusso di cassa, gli indicatori di rendimento, il confronto con l'alternativa di non comprare, le tabelle di sensibilita', la simulazione probabilistica su mille scenari con analisi a tornado, la ripartizione fra comproprietari, la checklist delle verifiche legali e tecniche, il dossier dei documenti da farsi consegnare in trattativa, il costo reale di un'aggiudicazione all'asta, il registro degli immobili in valutazione e il registro delle fonti.

Il perimetro e' deliberatamente definito. Sono coperti l'acquisto da privato e da impresa con IVA, la prima casa e le altre, l'acquisto in quota da parte di piu' soggetti, la nuova costruzione con le tutele del d.lgs. 122/2005. Non e' coperta la ristrutturazione come progetto a se', per scelta esplicita; resta invece modellata la ristrutturazione periodica di fine ciclo, perche' e' un costo ricorrente e ignorarlo falsa il rendimento.

Il progetto adotta il sistema di progetto portabile del template `E:\template-claude-developing`: memoria e schede di contesto versionate, regole modulari, e il pacchetto `studio-didattico`, cioe' il registro delle evoluzioni di progetto con i relativi approfondimenti nel codice reale.

Due invarianti del generatore, imparate correggendo difetti reali e non scelte a priori, vanno conosciute prima di toccare `excel_builder.py`. Un riferimento da un foglio a un altro si scrive per nome definito e mai per coordinata di cella; la riga di una tabella costruita da un helper si prende dal valore che l'helper restituisce e mai calcolandola come ancoraggio piu' una costante. La ragione, distesa in ADR-013 e nella voce 8 dello studio didattico, e' che le due forme vietate non sbagliano rumorosamente: producono un riferimento valido a una cella diversa, quindi un numero plausibile su un foglio che si apre senza errori.

## Contesto operativo

```
OS sviluppo:    Windows
Python:         3.13, dipendenza unica openpyxl
Verifica Excel: automazione COM tramite PowerShell, richiede Excel installato
LLM locale:     Ollama, opzionale; host in OLLAMA_HOST, default http://localhost:11434
LaTeX:          TinyTeX user-local, engine pdflatex; manifesto in tex-packages.txt,
                script in scripts/, skill latex-build. Serve solo alla trattazione
                matematica: il resto del progetto non dipende da esso
Identita' git:  da impostare locale al repository, vedi CLAUDE.local.md
```

L'identita' git, l'indirizzo dell'istanza Ollama e il remoto sono specifici della macchina e vivono in `CLAUDE.local.md`, che non e' versionato. Questo file, che finisce in una repository pubblica, non porta indirizzi di posta, recapiti, indirizzi di rete interni ne' percorsi personali.

## Procedura di ripresa in una sessione nuova

Lo stato del progetto e' interamente recuperabile su disco. Si legge per primo `.claude/memory/index.md`, che da' branch, stato di verifica di ogni scheda e punto di ripresa. Si legge poi `.claude/context/current-work.md` se c'e' una feature attiva. Le schede di dominio sotto `docs/` si aprono solo quando il task tocca la materia che descrivono, mai tutte insieme. Il registro `.claude/memory/progress.md` e quello delle decisioni `.claude/memory/decisions.md` forniscono storia e motivazioni quando servono.

Prima di toccare un parametro fiscale si legge `docs/fonti.md` e si verifica la fonte: nessun numero entra nel modello senza una fonte citata e una data di verifica.

## Comandi

```
python tools/valuta.py excel --con-annunci        genera il workbook e vi riversa gli annunci
python tools/valuta.py riepilogo --prezzo ...      calcolo rapido a video, senza Excel
python tools/valuta.py annunci elenca              registro degli immobili in valutazione
python tools/valuta.py annunci confronta            graduatoria per scarto sulla zona OMI
python tools/valuta.py annunci mancanti             che cosa manca su ogni immobile, e cosa blocca
python tools/valuta.py excel --da-annuncio ID      workbook precompilato coi dati di un immobile
python tools/valuta.py scheda --id ID              scheda LaTeX di una pagina per la trattativa
python tools/valuta.py annunci importa --file ...  struttura un annuncio col modello locale
python tools/valuta.py tassi --tasso 0.032        tassi correnti di mercato e confronto
python tools/valuta.py tassi --risalita             peggiori risalite storiche dell'Euribor
python tools/valuta.py indicatori                  euro short-term rate e inflazione ISTAT
python tools/valuta.py omi cerca --comune ...      quotazioni OMI della zona
python tools/valuta.py llm stato                   raggiungibilita' del modello locale
powershell -NoProfile -ExecutionPolicy Bypass -File tools\verifica-excel.ps1
```

L'ultimo comando e' la verifica del workbook: apre il file con Excel, forza il ricalcolo completo e segnala ogni cella in errore. Va eseguito dopo ogni modifica a `excel_builder.py`, perche' la libreria che genera il file scrive le formule ma non le valuta. I test automatici si eseguono con `python -m pytest tests`, oppure lanciando direttamente i due file se pytest non e' installato.

Il materiale personale, cioe' il dossier delle trattative, i riferimenti di terzi e i segnalibri, vive sotto `_notes/` ed e' interamente ignorato da git. La mappa di cosa contiene, con trascritta l'informazione dei file che sono vuoti e la portano nel nome, sta in `_notes/INDICE-MATERIALE.md`.

## Indice dei file satellite tracciati

Documenti pubblici, in radice.

```
README.md    descrizione del progetto per chi lo incontra la prima volta
LICENSE      licenza MIT, con la nota che delimita cosa la licenza non garantisce
```

Schede di dominio, sotto `docs/`. Sono la parte di conoscenza del progetto: spiegano la materia, non il codice. L'indice di questa cartella, con che cos'e' ciascun file, per chi e' scritto e quando si apre, sta in `docs/README.md`: e' il file da aprire quando non si sa dove cercare.

```
docs/README.md               indice della documentazione: i quattro percorsi di lettura,
                              i quindici documenti per tipo di domanda, le sovrapposizioni note
docs/da-zero.md              avvio da zero: cosa installare, quali documenti procurarsi,
                              la prima valutazione completa in sette passi
docs/fiscalita-acquisto.md   imposte di trasferimento, prezzo-valore, prima casa, mutuo,
                              detrazione degli interessi, plusvalenza, IMU
docs/fiscalita-locazione.md  i quattro regimi a confronto, novita' 2026 sulle locazioni
                              brevi, oneri della registrazione, rischi non catturati
docs/due-diligence.md        verifiche per fase, conformita' catastale e urbanistica,
                              Salva Casa, clausole della proposta, condominio, costruttore
docs/perizia-pre-acquisto.md documentazione tecnica da farsi consegnare in trattativa:
                              otto famiglie, chi rilascia, norma, costo, come si chiede
docs/aste-immobiliari.md     vendita giudiziaria: i quattro rischi che il prezzo deve
                              pagare, come si legge un avviso, quanto sconto serve
docs/metodo-e-metriche.md    scelte metodologiche, denominatore dei rendimenti, metriche
                              e loro lettura, limiti dichiarati del modello
docs/raccolta-annunci.md     registro degli annunci, vincoli dell'acquisizione automatica,
                              quotazioni OMI, riconoscimento dei duplicati
docs/comprare-in-piu-persone.md
                              acquisto in comproprieta': comunione o societa', maggioranze,
                              scioglimento, fisco pro quota, quando serve una societa'
docs/guida-per-il-socio.md   guida per chi compra insieme e non ha il progetto sulla
                              macchina: il percorso, i cinque colori, le cinquantuno celle
                              di input una per una, un giro completo su un immobile reale
docs/guida-non-tecnica.md    guida d'uso senza gergo, foglio per foglio, con il significato
                              di ogni voce spiegato in linguaggio comune
docs/matematica/matematica-finanziaria.tex
                              trattazione LaTeX: ogni formula del modello derivata da zero,
                              dalla capitalizzazione alla graduatoria, con la tavola che lega
                              simbolo, cella del workbook e funzione Python. Si compila con
                              scripts/build.ps1 -Main docs\matematica\matematica-finanziaria.tex
docs/manuale-operativo.md    guida d'uso completa: installazione, ogni comando con ogni
                              opzione, ogni campo del registro, ogni foglio, manutenzione
                              ricorrente, diagnostica degli errori
docs/guida-tecnica(catena-calcolo-e-normativa).md
                              architettura, catena di calcolo, riferimento di ogni voce con
                              formula e norma, punti di intervento, verifica
docs/fonti.md                registro completo delle fonti: cosa fornisce ciascuna, dove
                              atterra nel codice o nel workbook, stato di verifica, lacune
```

Memoria e meta-stato, sotto `.claude/memory/`, letti sempre a inizio sessione.

```
.claude/memory/index.md       snapshot e tabella di sincronizzazione, da leggere per primo
.claude/memory/progress.md    work-log append-only di passi e riconciliazioni
.claude/memory/decisions.md   registro ADR-lite delle decisioni
```

Schede tecniche, sotto `.claude/context/`, con frontmatter di riconciliazione.

```
.claude/context/STACK.md                stack, moduli, flussi di codice
.claude/context/design-and-security.md  paradigmi di design e limiti legali dell'acquisizione
.claude/context/deployment.md           ambiente, esecuzione, e le due scadenze ricorrenti:
                                        fiscale annuale, quotazioni OMI semestrali
.claude/context/dev-testing.md          come si verifica il modello, doppia implementazione
.claude/context/current-work.md         feature attiva, definition of done, domande aperte
.claude/context/roadmap.md              direzione e priorita'
```

Pacchetto `studio-didattico`, sotto `.claude/context/`. E' il registro delle evoluzioni di progetto: il file master porta le voci numerate in ordine cronologico, ciascuna con contesto, com'era e perche' era fragile, il salto compiuto e il rimando all'approfondimento. Gli approfondimenti mostrano il codice reale, prima e dopo, e chiudono con il modo di estendere il pattern. Si legge quando si deve capire perche' una scelta e' fatta cosi', prima di rifarla diversamente.

```
studio-didattico-master.md                  indice narrativo, dodici voci numerate
refactor-01-formule-vive.md                 workbook come modello, non come rapporto
refactor-02-denominatore.md                 il denominatore dei rendimenti
refactor-03-verifica-con-excel.md           automazione COM e locale italiano
refactor-04-agevolazione-unica.md           una sola fonte di verita' per l'agevolazione
refactor-05-doppio-conteggio.md             un costo ricorrente sta in un posto solo
refactor-06-contratto-posizionale.md        il contratto fra registro annunci e foglio
refactor-07-simulazione-riproducibile.md    simulazione riproducibile e interattiva
refactor-08-riferimenti-per-nome.md         nomi definiti invece di coordinate fisse
refactor-09-regime-per-riga.md              il regime di acquisto e il terzo stato
refactor-10-prezzo-massimo-esatto.md        soluzione chiusa invece di proporzione
refactor-11-scenario-misurato.md            il rialzo del tasso preso dalla serie storica
refactor-12-indice-navigabile.md            l'indice del workbook e i collegamenti interni
```

Regole modulari sotto `.claude/rules/`. Lo standard di sistema completo resta in `E:\template-claude-developing\.claude\PROJECT-SYSTEM.md`.

## Vincoli di team

Ogni prodotto di questo progetto resta un file su questa macchina. Non si pubblica nulla su servizi esterni, nemmeno in forma privata e nemmeno come pagina di sola lettura: non pagine web ospitate, non documenti su piattaforme di terzi, non caricamenti di alcun genere. Vale per la documentazione come per i dati, e vale anche quando il contenuto sembra innocuo, perche' il perimetro non lo decide il singolo contenuto: questo progetto tratta una trattativa reale, con prezzi obiettivo, recapiti di terzi e una strategia di acquisto, e la riservatezza di quel materiale e' una proprieta' del progetto e non di ciascun file. Quando serve un documento condivisibile, si scrive un file sotto `docs/` e lo condivide l'utente con i mezzi che sceglie.

Le operazioni di `git add`, commit e push restano manuali dell'utente: l'agente prepara i file, non committa. L'identita' git va impostata a livello locale del repository secondo `.claude/rules/git-identity-and-repo.md`. Lo stile di documentazione e di interazione e' quello di `.claude/rules/interaction-style.md`, e vale per ogni file scritto qui dentro. Claude non scrive autonomamente nei file di memoria e di contesto: li aggiorna solo su richiesta esplicita.

Il materiale personale, raccolto sotto `_notes/` dopo il riordino del 28 agosto 2026, non e' versionato e non va pubblicato: contiene documentazione di trattative reali, fogli di calcolo di terzi e conversazioni. Nemmeno `data/annunci.csv` entra in git, perche' porta i link agli immobili in trattativa e la colonna del prezzo obiettivo, che e' la propria strategia di acquisto e non ha ragione di stare in una repository pubblica.

## Avvertenza sul contenuto

Il progetto produce uno strumento di analisi personale, non una consulenza fiscale, legale o finanziaria. Le aliquote implementate sono quelle vigenti alla data di revisione dichiarata in `src/immobiliare/parametri.py` e cambiano con ogni legge di bilancio. Prima di qualunque firma le posizioni soggettive vanno confermate da un notaio e da un commercialista, e la conformita' urbanistica da un tecnico abilitato.
