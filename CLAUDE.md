# real-estate

> Istruzioni di team, versionate. Questo file e' l'indice del progetto: indicizza i soli file satellite tracciati e descrive la procedura di ripresa. Le preferenze personali vivono in `CLAUDE.local.md`, ignorato da git, non qui.

## Cos'e' questo progetto

Strumento locale per valutare l'acquisto di un immobile residenziale in Italia, in tutte e tre le destinazioni possibili: abitazione propria, messa a reddito, investimento puro. Produce un workbook Excel di ventun fogli con formule vive, quindi interattivo, che copre il cruscotto di sintesi, il costo reale dell'operazione, il mutuo con simulatore e piano di ammortamento, i regimi fiscali della locazione a confronto, la proiezione del flusso di cassa, gli indicatori di rendimento, il confronto con l'alternativa di non comprare, le tabelle di sensibilita', la simulazione probabilistica su mille scenari con analisi a tornado, la ripartizione fra comproprietari, la checklist delle verifiche legali e tecniche, il dossier dei documenti da farsi consegnare in trattativa, il costo reale di un'aggiudicazione all'asta, il registro degli immobili in valutazione e il registro delle fonti.

Il perimetro e' deliberatamente definito. Sono coperti l'acquisto da privato e da impresa con IVA, la prima casa e le altre, l'acquisto in quota da parte di piu' soggetti, la nuova costruzione con le tutele del d.lgs. 122/2005. Non e' coperta la ristrutturazione come progetto a se', per scelta esplicita; resta invece modellata la ristrutturazione periodica di fine ciclo, perche' e' un costo ricorrente e ignorarlo falsa il rendimento.

Il progetto adotta il sistema di progetto portabile del template `E:\template-claude-developing`: memoria e schede di contesto versionate, regole modulari, e il pacchetto `studio-didattico`, cioe' il registro delle evoluzioni di progetto con i relativi approfondimenti nel codice reale.

## Contesto operativo

```
OS sviluppo:    Windows
Python:         3.13, dipendenza unica openpyxl
Verifica Excel: automazione COM tramite PowerShell, richiede Excel installato
LLM locale:     Ollama, opzionale; host in OLLAMA_HOST, default http://localhost:11434
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
python tools/valuta.py annunci importa --file ...  struttura un annuncio col modello locale
python tools/valuta.py tassi --tasso 0.032        tassi correnti di mercato e confronto
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

Schede di dominio, sotto `docs/`. Sono la parte di conoscenza del progetto: spiegano la materia, non il codice.

```
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
docs/guida-non-tecnica.md    guida d'uso senza gergo, foglio per foglio, con il significato
                              di ogni voce spiegato in linguaggio comune
docs/guida-tecnica.md        architettura, catena di calcolo, riferimento di ogni voce con
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
studio-didattico-master.md                  indice narrativo, sette voci numerate
refactor-01-formule-vive.md                 workbook come modello, non come rapporto
refactor-02-denominatore.md                 il denominatore dei rendimenti
refactor-03-verifica-con-excel.md           automazione COM e locale italiano
refactor-04-agevolazione-unica.md           una sola fonte di verita' per l'agevolazione
refactor-05-doppio-conteggio.md             un costo ricorrente sta in un posto solo
refactor-06-contratto-posizionale.md        il contratto fra registro annunci e foglio
refactor-07-simulazione-riproducibile.md    simulazione riproducibile e interattiva
```

Regole modulari sotto `.claude/rules/`. Lo standard di sistema completo resta in `E:\template-claude-developing\.claude\PROJECT-SYSTEM.md`.

## Vincoli di team

Le operazioni di `git add`, commit e push restano manuali dell'utente: l'agente prepara i file, non committa. L'identita' git va impostata a livello locale del repository secondo `.claude/rules/git-identity-and-repo.md`. Lo stile di documentazione e di interazione e' quello di `.claude/rules/interaction-style.md`, e vale per ogni file scritto qui dentro. Claude non scrive autonomamente nei file di memoria e di contesto: li aggiorna solo su richiesta esplicita.

Il materiale personale, raccolto sotto `_notes/` dopo il riordino del 28 agosto 2026, non e' versionato e non va pubblicato: contiene documentazione di trattative reali, fogli di calcolo di terzi e conversazioni. Nemmeno `data/annunci.csv` entra in git, perche' porta i link agli immobili in trattativa e la colonna del prezzo obiettivo, che e' la propria strategia di acquisto e non ha ragione di stare in una repository pubblica.

## Avvertenza sul contenuto

Il progetto produce uno strumento di analisi personale, non una consulenza fiscale, legale o finanziaria. Le aliquote implementate sono quelle vigenti alla data di revisione dichiarata in `src/immobiliare/parametri.py` e cambiano con ogni legge di bilancio. Prima di qualunque firma le posizioni soggettive vanno confermate da un notaio e da un commercialista, e la conformita' urbanistica da un tecnico abilitato.
