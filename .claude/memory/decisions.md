# Registro delle decisioni

> Convenzione ADR-lite, append-only. Una decisione non si cancella e non si riscrive: quando viene superata, si aggiunge una voce nuova che dichiara di superarla e ne cita il numero.

## ADR-001, il workbook porta formule vive e non valori calcolati

Data: 2026-08-28. Stato: accettata.

Contesto. Il generatore poteva scrivere numeri già calcolati in Python, il che sarebbe stato molto più semplice, oppure formule Excel che si ricalcolano da sole.

Decisione. Scrive formule. Ogni grandezza derivata è una formula, e i riferimenti fra fogli passano per nomi definiti anziché per indirizzi di cella.

Motivazione. Uno strumento di valutazione serve a fare domande, non a dare una risposta: il valore sta nel poter cambiare il prezzo o il tasso e vedere subito l'effetto. Un file di numeri costringerebbe a rieseguire Python per ogni ipotesi, il che nella pratica significa che nessuno le proverebbe.

Conseguenze. Il generatore è più complesso e gli errori nelle formule non emergono alla scrittura. Da qui discende ADR-003.

## ADR-002, i rendimenti si calcolano sul costo totale, non sul prezzo

Data: 2026-08-28. Stato: accettata.

Contesto. La convenzione degli annunci e delle conversazioni usa il prezzo come denominatore dei rendimenti.

Decisione. Il denominatore è il costo totale dell'operazione, cioè prezzo più imposte, provvigione, notaio, oneri del mutuo e altri costi di ingresso. Il cash on cash usa invece l'esborso iniziale, cioè il capitale proprio.

Motivazione. Quei costi sono capitale immobilizzato che non torna alla rivendita. Ignorarli gonfia il rendimento di quanto essi incidono, che sul caso di riferimento è quasi il dieci per cento.

Conseguenze. I numeri prodotti sono sistematicamente più bassi di quelli che l'utente trova altrove, e questo va spiegato invece che nascosto. Il modello espone l'incidenza dei costi come indicatore a sé.

## ADR-003, il workbook si verifica aprendolo con Excel

Data: 2026-08-28. Stato: accettata.

Contesto. La libreria di generazione scrive le formule senza valutarle, quindi un errore di sintassi, un nome non risolto o un blocco XML malformato non emergono in fase di scrittura. Durante la costruzione un elemento di validazione vuoto ha reso il file irricevibile per Excel senza che nulla lo segnalasse a monte.

Decisione. Esiste uno script che apre il workbook con Excel via automazione COM, forza il ricalcolo completo, elenca ogni cella in errore e stampa i valori chiave. Va eseguito dopo ogni modifica al generatore.

Motivazione. È l'unico modo per sapere che il file non solo si scrive ma funziona. La sola alternativa disponibile su questa macchina sarebbe stata l'ispezione manuale.

Conseguenze. La verifica richiede Excel installato ed è quindi legata alla piattaforma. Non è un vincolo per usare lo strumento, solo per svilupparlo. L'automazione COM va invocata con la cultura en-US esplicita, perché con una console italiana il late binding non risolve i metodi.

## ADR-004, l'acquisizione automatica degli annunci rispetta robots.txt senza eccezioni

Data: 2026-08-28. Stato: accettata.

Contesto. La raccolta degli annunci può avvenire manualmente, per incolla del testo, o per prelievo diretto delle pagine dai portali.

Decisione. Il prelievo diretto è subordinato alla verifica del `robots.txt` per il singolo URL, con astensione in caso di file non leggibile, intervallo minimo di cinque secondi per dominio, user agent che si dichiara, e nessun meccanismo di aggiramento delle protezioni. Non si raccolgono dati di contatto di persone fisiche.

Motivazione. La materia tocca i termini di servizio dei portali, il diritto sui generis sulle banche dati e la protezione dei dati personali. Il fatto che un dato sia visibile non lo rende liberamente riutilizzabile. Il valore dello strumento non dipende dal prelievo automatico: le altre due vie restano sempre disponibili.

Conseguenze. Su alcuni portali il prelievo non sarà possibile, e il programma lo dice spiegando le alternative anziché fallire.

## ADR-005, l'accantonamento per la ristrutturazione entra nel conto economico

Data: 2026-08-28. Stato: accettata.

Contesto. Un immobile tenuto quarant'anni richiede almeno un rifacimento completo, di ordine pari a un terzo del valore.

Decisione. La spesa è ripartita come costo annuo ricorrente nel conto economico della locazione, accanto alla manutenzione ordinaria, e non trattata come evento futuro fuori dal rendimento corrente.

Motivazione. È l'impostazione dei fogli di Paolo Coletti ed è quella corretta: ignorarla è il modo più comune di sopravvalutare un immobile. Sul caso di riferimento sposta il rendimento netto dall'uno virgola tre allo zero virgola cinque per cento.

Conseguenze. La voce compare una sola volta, dentro il reddito operativo netto, e la colonna separata che il foglio del flusso di cassa aveva inizialmente è stata rimossa perché la contava due volte.

## ADR-006, la revisione fiscale è datata e vive in un solo file

Data: 2026-08-28. Stato: accettata.

Contesto. Le aliquote cambiano con ogni legge di bilancio e sono sparse per natura fra imposte di trasferimento, mutuo, locazione, IMU e plusvalenza.

Decisione. Tutti i parametri normativi stanno in `src/immobiliare/parametri.py`, con la fonte accanto a ciascuno e una data di revisione dichiarata in testa, e sono replicati nel foglio Parametri del workbook dove restano modificabili.

Motivazione. L'aggiornamento annuale deve essere un intervento in un punto solo, e chi legge un numero deve poter risalire alla fonte senza cercare.

Conseguenze. Il foglio Parametri è modificabile dall'utente: se una aliquota cambia in corso d'anno si aggiorna lì senza rigenerare, e il codice si allinea alla revisione successiva.

## ADR-007, la simulazione probabilistica separa le estrazioni fisse dal calcolo vivo

Data: 2026-08-31. Stato: accettata.

Contesto. Passare dai tre scenari scelti a mano a una distribuzione di esiti richiede molte estrazioni casuali dentro un foglio di calcolo senza macro. La funzione casuale nativa è volatile e cambierebbe tutti i mille scenari a ogni tocco di cella; pre-calcolare tutto in Python e scrivere valori tradirebbe ADR-001.

Decisione. I due strati vivono separati nel foglio nascosto `_Estrazioni`. Le estrazioni sono numeri fissi generati in Python con seme dichiarato nel modulo, `SEME_SIMULAZIONE`. Il calcolo che le trasforma in esiti sono formule vive che leggono gli input dell'utente.

Motivazione. Riproducibilità e interattività sembravano in conflitto e non lo erano: sono due strati diversi. Due persone che discutono lo stesso file devono guardare gli stessi numeri, e il file deve comunque reagire a un cambio di prezzo.

Conseguenze. Il ricalcolo dell'intero workbook costa sei decimi di secondo. Le variabili sono assunte indipendenti, e il limite è dichiarato dentro il foglio: la distribuzione va letta come misura della dispersione, non come probabilità oggettiva. Chi aggiunge una variabile aleatoria deve decidere esplicitamente se la sua incertezza è di livello, e allora non si scala, oppure di variazione annua di una grandezza che si compone, e allora si divide per la radice dell'orizzonte.

## ADR-008, il progetto adotta il pacchetto studio-didattico del template

Data: 2026-08-31. Stato: accettata.

Contesto. Le decisioni erano registrate qui in forma sintetica, ma il perché di sette scelte strutturali, e soprattutto com'era il codice prima e perché quella forma era fragile, non era scritto da nessuna parte. Chi riprende il progetto vede lo stato finale e non i vincoli che lo hanno prodotto.

Decisione. Adottato il pacchetto `studio-didattico` del template: `.claude/context/studio-didattico-master.md` con voci numerate in ordine cronologico nella struttura in quattro parti, e un approfondimento `refactor-NN-<slug>.md` per ciascuna, con il codice reale prima e dopo e la sezione su come estendere il pattern.

Motivazione. Un registro ADR dice cosa si è deciso; non insegna a riconoscere la classe di difetto. Il caso del moltiplicatore catastale lo dimostra: era identico in Python e in Excel, quindi la doppia implementazione non l'ha intercettato, e il valore sta nel capire perché un presidio che funziona sugli errori di trascrizione non funziona su un errore concettuale replicato fedelmente.

Conseguenze. Ogni evoluzione strutturale futura aggiunge una voce al master e il suo approfondimento. Il pacchetto è indicizzato in `CLAUDE.md` e va letto prima di rifare diversamente una scelta che ha già un numero.

## ADR-009, il fascicolo dei documenti sta in un foglio separato dalla checklist

Data: 2026-08-31. Stato: accettata.

Contesto. Serviva l'elenco della documentazione tecnica da farsi consegnare in fase di trattativa, al livello di dettaglio con cui la chiederebbe un tecnico incaricato. La Checklist esisteva già e conteneva alcune di quelle voci in forma di verifica.

Decisione. Due fogli distinti. La Checklist elenca verifiche e clausole, con il loro perché e chi le fa. Il Dossier tecnico elenca documenti, con chi li rilascia, la norma che li rende dovuti, il costo indicativo e lo stato della raccolta, e ha una tassonomia propria a tre valori: bloccante, importante, se ricorre.

Motivazione. Le due cose rispondono a domande diverse in due momenti diversi. Le verifiche si chiudono prima di firmare; i documenti si chiedono prima ancora, quando si ha potere negoziale, e senza di essi le verifiche non si possono fare. Unirle avrebbe prodotto una tabella con metà delle colonne vuote su metà delle righe, e avrebbe nascosto il contatore che serve davvero, cioè quanti documenti bloccanti mancano ancora.

Conseguenze. Il Cruscotto porta due contatori invece di uno, le verifiche aperte e i documenti bloccanti mancanti. La tassonomia del peso è una stringa confrontata da `COUNTIFS`, quindi fragile per costruzione: un test verifica che ogni riga usi uno dei tre valori esatti, perché un valore scritto diversamente sparirebbe dal conteggio senza errore e il cruscotto direbbe che non manca nulla.

## ADR-010, dai progetti senza licenza si prende l'informazione, non il codice

Data: 2026-08-31. Stato: accettata.

Contesto. Il bot Telegram open source `finanza-che-conta` pubblica l'euro short-term rate ogni lunedì e l'inflazione ISTAT a ogni comunicato, ed è la fonte da cui è stato individuato l'identificativo del flusso SDMX dei prezzi al consumo, che la documentazione di ISTAT non rende facile trovare. Il repository, però, non dichiara alcuna licenza.

Decisione. Nessun codice ripreso. Il modulo `indicatori.py` è scritto da zero sullo stesso endpoint pubblico, e il credito è dato nella docstring e nel registro delle fonti per la scoperta della fonte, non per il codice.

Motivazione. L'assenza di licenza non significa dominio pubblico ma il contrario: ogni diritto è riservato all'autore, e la pubblicazione su una piattaforma non concede alcun permesso di riuso. Un endpoint pubblico, invece, è un fatto: sapere che ISTAT espone i prezzi al consumo al flusso `167_744_DF_DCSP_NIC1B2015_1` non è materiale protetto, è un'informazione.

Conseguenze. La regola vale in generale per questo progetto: prima di riprendere codice da una fonte esterna si guarda la licenza, e in sua assenza si riscrive. Vale anche il contrario, cioè che i progetti da cui si è preso solo il perimetro funzionale restano citati come tali nel registro delle fonti, senza attribuire loro un contributo che non hanno dato.

## ADR-011, i servizi autenticati dell'area riservata restano manuali, e la fonte OMI si cita

Data: 2026-08-31. Stato: accettata. Estende ADR-004.

Contesto. Il progetto usa quattro servizi dell'area riservata dell'Agenzia delle Entrate: forniture OMI, visure e ispezioni ipotecarie, valori immobiliari dichiarati, fogli di mappa catastale. Accedendovi si accettano le condizioni generali di consultazione della banca dati catastale, decreto 4 maggio 2007 e successive integrazioni.

Decisione. Nessuno dei quattro viene automatizzato. Il file lo scarica la persona, il programma lo ingerisce da disco. Inoltre la stringa `Agenzia Entrate - OMI`, obbligatoria per la fornitura, è esposta come `omi.ATTRIBUZIONE`, stampata in coda a ogni interrogazione e dichiarata nel foglio Fonti.

Motivazione. L'articolo 2 impone l'autenticazione personale, e simularla significherebbe far interrogare la banca dati a un programma con le credenziali di una persona. L'articolo 5 riserva all'Agenzia la facoltà di limitare le interrogazioni giornaliere, l'articolo 3 rende l'utente responsabile dell'uso improprio o eccessivo, e l'articolo 4 sanziona la violazione con l'inibizione del servizio: il costo di sbagliare non è una discussione, è la perdita dell'accesso. Sulla citazione della fonte, l'obbligo era assunto e non assolto: è stato un difetto di conformità reale, non un dettaglio.

Conseguenze. `omi.importa_fornitura` resta la sola via per i dati correnti e accetta l'archivio così come arriva. Visure e ispezioni sul venditore contengono dati personali di terzi e restano sotto `_notes/`, non versionato. La regola generale che ne discende: quando una fonte richiede autenticazione personale, il confine fra automatizzabile e no non lo decide la comodità ma il testo che si è accettato.

## ADR-012, le aste giudiziarie entrano nel perimetro

Data: 2026-08-31. Stato: accettata. Supera la voce di `roadmap.md` che le dichiarava fuori perimetro.

Contesto. La roadmap teneva le aste giudiziarie fuori dal perimetro, con la motivazione che seguono regole proprie su perizia, custode, decreto di trasferimento e liberazione dell'immobile e che meriterebbero uno strumento separato. La motivazione era corretta sui fatti e sbagliata nella conclusione: quelle regole proprie sono poche e circoscritte, e il resto del modello, cioè imposte, mutuo, rendimento e confronto con l'alternativa, vale identico.

Decisione. Le aste entrano, con un foglio dedicato che modella ciò che differisce e riusa tutto il resto: cinque campi nel registro, il foglio Asta, sette voci nel Dossier tecnico e la scheda `docs/aste-immobiliari.md`. Restano fuori le vendite nella liquidazione giudiziale, le aste con incanto e i beni non abitativi.

Motivazione. Il foglio non serve a calcolare meglio: serve a impedire un errore preciso. Un'asta valutata con il modello ordinario mostra un'incidenza dei costi bassa, perché manca la provvigione, e un prezzo apparentemente ottimo, e fa sembrare conveniente un'operazione che porta con sé l'assenza di garanzia per i vizi ex art. 2922 c.c., il possesso del debitore fino al decreto ex art. 560 c.p.c., la locazione opponibile ex art. 2923 c.c. e la decadenza con perdita della cauzione ex art. 587 c.p.c. Il numero di sintesi non è quindi il prezzo ma lo sconto sul valore di mercato, confrontato con una soglia che rappresenta il prezzo di quei rischi.

Conseguenze. Il registro cresce di cinque campi e il foglio Annunci di cinque colonne, con il contratto posizionale riallineato e i test aggiornati: il difetto era già stato intercettato da quei test alla prima esecuzione, che è la conferma che servissero. Il prezzo-valore si applica anche qui, dopo la sentenza 6 del 2014 della Corte costituzionale, e resta la singola ottimizzazione più redditizia dell'operazione.

## ADR-013, nessun riferimento per coordinata: fra fogli si usa un nome, dentro una tabella si usa la riga restituita

Data: 2026-09-01. Stato: accettata.

Contesto. Il generatore scrive formule, e una formula deve citare altre celle. Tre forme convivevano nel codice. La prima, i nomi definiti, usata per la gran parte dei riferimenti fra fogli. La seconda, la coordinata scritta a mano, usata in due punti del Cruscotto. La terza, l'indice calcolato come riga di ancoraggio più una costante, usata nel conto economico del foglio Locazione e nella tabella a tre scenari del foglio Scenari.

Le ultime due hanno prodotto difetti reali, e sono stati trovati per caso. La formula del Cruscotto che da' il verdetto fra comprare e affittare citava `'Confronto affitto'!$B$52`, che era diventata la riga del patrimonio comprando invece di quella della differenza fra i due patrimoni: poiché il patrimonio comprando è positivo per qualunque immobile di valore, il verdetto diceva "conviene comprare" quasi sempre, e con il rendimento del portafoglio alternativo al nove per cento diceva di comprare mentre il foglio concludeva l'opposto per centoquattordicimila euro. Gli indici per offset non avevano ancora prodotto un difetto visibile soltanto perché nessuno aveva inserito una voce in mezzo, ma erano dichiarati come il punto più fragile del generatore, e con ragione.

Va notato che il difetto del Cruscotto era una recidiva: il work-log del 28 agosto registra la correzione di un difetto identico nello stesso foglio, dove la differenza puntava alla riga del capitale versato. Lo stesso errore due volte nello stesso posto non è sfortuna, è la firma di una forma di codice sbagliata.

Decisione. Un riferimento da un foglio a un altro si scrive sempre per nome definito. Un riferimento a una riga di una tabella costruita da un helper si scrive sempre usando la riga che l'helper restituisce, mai calcolandola. Dove la tabella è costruita da un ciclo, le righe si registrano in un dizionario sotto una chiave e le formule citano le chiavi. Nessuna coordinata di cella e nessun offset numerico compare più in una formula che attraversi un foglio o una tabella.

Motivazione. È una scelta sul modo in cui un errore si manifesta, non sull'eleganza. Un nome definito inesistente produce `#NOME?` in ogni cella che lo usa, che è impossibile non vedere e che la verifica con Excel intercetta. Una chiave assente nel dizionario solleva un KeyError alla generazione, quindi il file non viene nemmeno prodotto. Una coordinata sbagliata, invece, è un riferimento perfettamente valido a una cella diversa: produce un numero dell'ordine di grandezza giusto, in una cella che non è in errore, su un foglio che si apre regolarmente. Fra tre forme che sbagliano, si scelgono quelle che sbagliano rumorosamente.

Conseguenze. Il vincolo operativo che ne discende è che una formula può citare solo righe già scritte, il che ordina la costruzione di una tabella dall'alto verso il basso. Non è un costo: era già vero di fatto in entrambe le tabelle, e adesso è verificato dal linguaggio invece che dall'attenzione. Tre test presidiano la regola: uno verifica che il nome `conf_differenza` punti alla riga la cui etichetta è "Differenza a favore dell'acquisto", uno che il reddito operativo netto sommi esattamente le righe fra il ricavo effettivo e se stesso su tutte e quattro le colonne dei regimi, uno che ogni formula della tabella degli scenari citi solo righe interne alla tabella e precedenti alla propria.

## ADR-014, il regime di acquisto è un dato della riga, e il vuoto è un terzo stato

Data: 2026-09-01. Stato: accettata.

Contesto. Il foglio Confronto immobili applicava a ogni riga il regime di acquisto impostato nel foglio Immobile, cioè prima casa oppure no e venditore privato oppure impresa con IVA. Il limite era dichiarato nel foglio e registrato come il più rilevante fra quelli noti. La sua conseguenza non è un'imprecisione ma un'inversione: sullo stesso prezzo l'IVA si applica per intero mentre l'imposta di registro con il prezzo-valore si applica al valore catastale, che di norma è una frazione, quindi un usato da privato e un nuovo da costruttore confrontati con lo stesso regime producono una graduatoria che indica come migliore proprio l'immobile che porta l'imposta più alta.

Decisione. Il regime si dichiara per riga nel registro, con i campi `prima_casa` e `venditore_impresa`, e il foglio di confronto lo espone in due colonne che sono anche quelle lette dalle formule delle imposte e dei costi accessori. I due campi hanno tre stati e non due: SI e NO dichiarano il regime della riga, il vuoto significa eredita dal foglio Immobile. Restano globali l'opzione prezzo-valore e la qualifica di immobile di lusso.

Motivazione. Sul perché per riga e non globale, la ragione è che nessuno dei due dati è una proprietà del modello: `venditore_impresa` è una caratteristica dell'immobile, e `prima_casa` non è nemmeno quello, è una caratteristica della posizione di chi compra rispetto a quell'immobile, che cambia tipicamente fra un immobile nel Comune di residenza e uno fuori. Un dato che varia per riga va nella riga.

Sul perché tre stati e non due, la ragione è la compatibilità con ciò che esiste. Trattare il vuoto come NO avrebbe cambiato in silenzio i numeri di ogni registro già compilato, e nel verso peggiore, cioè togliendo l'agevolazione prima casa a dodici annunci che la avevano. Il terzo stato rende l'aggiunta esattamente neutra: chi non tocca quelle colonne vede gli stessi numeri di prima. Sui due campi restati globali, l'opzione prezzo-valore è una scelta che si esercita in atto e conviene quasi sempre, la qualifica di lusso riguarda un caso raro, e per entrambi il costo di portarli nel registro non era giustificato dalla frequenza.

Conseguenze. Il registro passa a trentacinque campi e il foglio Annunci a trentotto colonne, con il contratto posizionale riallineato. `venditore_impresa` entra nello schema di estrazione del modello locale e `prima_casa` no, perché il primo sta scritto negli annunci e il secondo dipende da chi compra. Da questo discende ADR-015 sulla normalizzazione. Il foglio dichiara che l'agevolazione prima casa si usa una volta sola mentre più righe possono dichiararla: è corretto, perché ogni riga è un'alternativa alle altre e non un acquisto che si somma, ma la lettura giusta della graduatoria è che il bonus andrà a una sola di quelle righe.

## ADR-015, i campi a tre stati si normalizzano in ingresso, e ciò che non si riconosce non si indovina

Data: 2026-09-01. Stato: accettata.

Contesto. Quattro campi del registro sono confrontati dal workbook con la stringa SI: `asta`, `nuova_costruzione`, `prima_casa`, `venditore_impresa`. Due di essi sono nello schema di estrazione passato al modello linguistico locale, che a una domanda booleana risponde volentieri `true` oppure `yes`. Excel confronta il testo senza distinguere le maiuscole, quindi `si` minuscolo funziona, mentre `true` risulta diverso da SI e viene letto come un NO.

Decisione. La normalizzazione avviene in `__post_init__` della dataclass, quindi su ogni annuncio da qualunque origine, CSV compreso: gli affermativi riconosciuti diventano SI, i negativi NO, la stringa vuota resta vuota, e ciò che non è riconosciuto resta scritto com'è.

Motivazione. Il caso `true` non produce un errore ma un valore di default silenzioso, ed è peggio di un errore perché cambia le imposte di una riga senza lasciare traccia. Sulla scelta di non indovinare, la ragione è simmetrica: se qualcuno scrive "da chiarire col notaio", tradurlo in NO significherebbe fingere una risposta che nessuno ha dato, mentre lasciarlo visibile lo fa comportare come un vuoto nel confronto con SI e resta leggibile a chi apre il foglio. Un valore strano che si vede è preferibile a un valore strano tradotto per ipotesi.

Conseguenze. La validazione a elenco nel foglio Annunci ammette il vuoto, così che le colonne restino a tre stati anche a video. Il test copre esplicitamente `true`, che è il motivo per cui la normalizzazione esiste, e il caso non riconosciuto, che è il motivo per cui non è più aggressiva.

## ADR-016, il prezzo massimo si risolve in forma chiusa, e porta con sé la propria verifica

Data: 2026-09-01. Stato: accettata.

Contesto. Il prezzo massimo sostenibile al rendimento obiettivo era calcolato dividendo il costo totale sostenibile per uno più l'incidenza percentuale dei costi accessori misurata sullo scenario base, con l'approssimazione dichiarata in nota. La nota rendeva l'approssimazione onesta ma non la rendeva innocua: sul caso di riferimento la formula dava 15.609 euro contro i 43.445 esatti, cioè un fattore prossimo a tre, e l'errore andava nella direzione che fa sembrare impossibile qualunque trattativa. È il numero che serve a decidere quanto offrire.

Decisione. Il prezzo massimo si ottiene risolvendo l'equazione. Il costo totale in funzione del prezzo è `P*(1+k)+c`, l'utile è `utile_base-(P-prezzo)*m`, e imporre il rapporto pari all'obiettivo da' `(utile_base+prezzo*m-obiettivo*c)/(obiettivo*(1+k)+m)`. Le tre grandezze stanno in tre celle visibili con la loro nota, non dentro la formula. Accanto, una cella ricalcola il rendimento a quel prezzo con le formule esatte delle imposte, minimo di legge compreso, e una mostra lo scarto dalla soglia, che deve essere zero.

Motivazione. L'errore aveva due cause indipendenti che si sommavano nella stessa direzione, ed è la ragione per cui l'approssimazione era più grave di quanto la nota suggerisse. L'incidenza percentuale dei costi accessori non è un parametro del modello ma un rapporto fra due grandezze che dipendono entrambe dal prezzo: notaio, altri costi, oneri del mutuo, imposte fisse e, con il prezzo-valore, l'intera imposta di registro sono importi fissi, quindi la loro incidenza cresce al calare del prezzo. E l'utile netto non è indipendente dal prezzo, perché manutenzione e accantonamento per la ristrutturazione sono quote del valore. Tenere ferme entrambe le cose è il modo più comune di introdurre un errore che non si vede, perché il risultato resta dell'ordine di grandezza giusto.

Sul perché la verifica sta nel foglio e non in un test. La soluzione chiusa è esatta solo sul tratto in cui il costo totale è lineare nel prezzo, e c'è un caso in cui non lo è: il minimo di legge dell'imposta di registro, che su prezzi molto bassi diventa vincolante. Un test coprirebbe il caso precaricato, non il caso che l'utente produce cambiando gli input a video, ed è proprio quello il momento in cui serve saperlo. La cella dello scarto è il presidio giusto perché è presente esattamente quando il problema si presenta.

Conseguenze. La riga dello scarto sul prezzo trattato deriva ora dal prezzo massimo invece di ricalcolarlo, quindi le due non possono divergere. Il nome `incidenza_costi` resta e resta utile come indicatore autonomo, ma non è più usato per invertire nulla. La lezione è registrata anche in `docs/metodo-e-metriche.md`, perché vale oltre questa cella: un'incidenza percentuale misurata su uno scenario non è un parametro, e usarla come tale produce errori silenziosi.

## ADR-017, il workbook si naviga da un indice, e ogni elenco di valori ammessi ha una sorgente sola

Data: 2026-09-01. Stato: accettata.

Contesto. Il workbook ha venti fogli visibili, tutti necessari al perimetro, e la navigazione dipendeva dalle linguette in basso più un elenco descrittivo parziale sul primo foglio. La segnalazione è arrivata dall'uso, in termini esatti: i fogli sono tanti, sono probabilmente tutti necessari, ma si perde il flusso. È un difetto di natura diversa da quelli affrontati finora, perché non riguarda la correttezza di un numero ma la possibilità di trovare il numero giusto, e un modello che nessuno riesce a percorrere produce numeri che nessuno usa.

Decisione. Il primo foglio è un indice navigabile, costruito da una tupla che è sorgente unica e verificata da un test contro i fogli realmente presenti. Ogni foglio porta il ritorno all'indice in una posizione identica, scritta dalla funzione che tutti i fogli chiamano per prima. I collegamenti interni si costruiscono con un helper dedicato che usa `location`, e non assegnando una stringa a `cell.hyperlink`. Nella stessa decisione rientra l'unificazione degli stati ammessi per un annuncio in `annunci.STATI_ANNUNCIO`, condivisa fra il menu a tendina del foglio e l'aiuto della riga di comando.

Motivazione. Sull'indice, la ragione è che l'informazione che serve per navigare non è l'elenco dei fogli, che le linguette danno già, ma tre cose che le linguette non danno: se in quel foglio si scrive o si legge, quando lo si apre nel percorso, e se riguarda il proprio caso. Diversi fogli, per esempio Asta e Comproprieta, servono solo in situazioni particolari, e senza quell'informazione chi apre il file non sa se stia dimenticando di compilarli.

Sulla sorgente unica e sul test, la ragione è la solita di questo progetto: il difetto da presidiare è quello che non si vede. Un foglio rinominato lascia un collegamento sintatticamente valido verso una destinazione che non esiste più, e Excel lo apre senza segnalare nulla.

Sulla forma del collegamento, la ragione è tecnica e va scritta perché la scorciatoia è quella che si trova per prima: openpyxl registra come destinazione esterna un collegamento assegnato come stringa, e nel file finisce fra le relazioni verso l'esterno. Un collegamento interno non ha una destinazione esterna, ha una posizione dentro il file.

Sugli stati ammessi, la ragione è che erano due elenchi e divergevano già. Il valore scritto dalla riga di comando non passa per la validazione del foglio, quindi resta in cella senza errore, ma il menu a tendina non lo contiene e un filtro per stato non lo trova dove chi lo ha scritto lo cerca. È lo stesso principio di ADR-013 applicato a un elenco invece che a un riferimento: fra due forme, si sceglie quella in cui la divergenza è impossibile invece di quella in cui è silenziosa.

Conseguenze. Il vincolo che ne discende per il futuro è che un foglio nuovo va aggiunto in due posti, il metodo che lo costruisce e la tupla dell'indice, e che il test lo impone invece di lasciarlo alla memoria. Il ritorno all'indice, invece, non richiede nulla, perché lo scrive la funzione del titolo. Il manuale operativo `docs/manuale-operativo.md` nasce nella stessa sessione e con la stessa motivazione, cioè rendere usabile ciò che era stato reso corretto.

## ADR-018, la matematica del modello si formalizza in un documento a parte, e il nominale non basta

Data: 2026-09-02. Stato: accettata.

Contesto. Il modello calcola una trentina di grandezze, ciascuna con la sua formula, e le formule vivevano in tre posti: le celle del workbook, le funzioni del motore, e le note di dominio che le descrivevano in prosa. Nessuno dei tre le derivava. La conseguenza non era un errore ma un limite di verificabilità: chi voleva controllare un numero poteva leggere la formula della cella, non ricostruire perché quella formula fosse quella giusta. Sulla stessa linea, tutti i rendimenti erano nominali, e un rendimento nominale non risponde alla domanda per cui esiste un investimento, che è se il potere d'acquisto cresca.

Decisione. Due cose insieme, perché la seconda è il primo cliente della prima. Si adotta il pacchetto `latex` del template e si scrive `docs/matematica-finanziaria.tex`, che formalizza ogni calcolo del modello partendo dalle definizioni, con le derivazioni, le ipotesi, i metodi numerici e i limiti, e chiude con la tavola che lega simbolo, cella e funzione. E si aggiunge al modello l'analisi dell'effetto dell'inflazione, con l'equazione di Fisher in forma esatta, la scomposizione dell'effetto per componente e la quantificazione dell'indicizzazione rinunciata dalla cedolare secca.

Motivazione. Sulla trattazione, la ragione è che un modello di cui non si può ricostruire la derivazione è verificabile solo per confronto, cioè rifacendo lo stesso conto con lo stesso metodo, che è il modo peggiore di verificare perché replica anche l'errore di ragionamento. Un documento che parte dalle definizioni permette la verifica indipendente, e ha prodotto due risultati che le celle non mostravano: la formula della leva, che rende esplicita la condizione perché il debito aiuti, e la scomposizione della derivata del rendimento rispetto al prezzo, che dice quanta parte dell'effetto passa dal numeratore.

Sul documento a parte e non dentro le schede di dominio, la ragione è di destinatario: le schede spiegano la materia a chi decide, la trattazione spiega la matematica a chi verifica, e i due registri non convivono nello stesso file senza che uno dei due si degradi. Sulla scelta di LaTeX invece di Markdown, la ragione è che il documento contiene sessanta formule numerate con riferimenti incrociati e quattro dimostrazioni: Markdown le renderebbe come immagini o come testo, e in entrambi i casi non sarebbero citabili.

Sul reale invece del nominale, la ragione è che la conversione non è un ornamento ma cambia il segno della conclusione. Sul caso di riferimento il rendimento netto passa da più 0,52 per cento a meno 1,45, e il tasso interno da più 0,40 a meno 1,56: l'operazione mostra un utile in euro e perde potere d'acquisto. Un modello che riporta solo il nominale non è impreciso, risponde a una domanda diversa da quella che gli si pone.

Conseguenze. L'ambiente LaTeX è una dipendenza nuova del progetto, e va confinata: serve soltanto alla trattazione, il resto non ne dipende, e chi non la compila non perde nulla dello strumento. Il PDF è un artefatto derivato e resta fuori da git. La forma esatta di Fisher diventa la regola: nessuna cella del modello usa la sottrazione, e la cella che mostra l'errore dell'approssimazione esiste perché la sottrazione resta utile per il conto a mente e va saputa per quello che è. Dall'analisi dell'inflazione discende un risultato che vale registrare come tale: sul caso di riferimento la cedolare secca ha un saldo negativo di circa settemiladuecento euro di valore attuale, perché l'indicizzazione rinunciata vale più del risparmio d'imposta. Non è un verdetto generale, ed è esposto con le sue tre cautele, ma è un confronto che il modello prima non permetteva di fare.

## ADR-019, un dato che manca si azzera e si dichiara, non si eredita dall'esempio

Data: 2026-09-02. Stato: accettata.

Contesto. Il workbook generato porta valori di esempio in tutte le celle di input: servono a mostrare il formato atteso e a far funzionare il modello a vuoto, e su un file-modello sono corretti. Con la precompilazione da registro nasce un file dedicato a un immobile reale, e in quel contesto gli stessi valori cambiano natura. Il caso osservato: il registro non ha la rendita catastale di house_6, la cella conservava i 450 euro dell'esempio, il modello applicava il prezzo-valore su quella base, e il controllo di plausibilità che riguarda la rendita risultava superato. Il risultato era un costo dell'operazione plausibile calcolato su un dato inventato, con tutti i presidi del progetto che dichiaravano tutto in ordine.

Decisione. Nel file dedicato a un immobile, i campi che il registro non ha vengono azzerati e non lasciati al valore di esempio. L'azzeramento riguarda soltanto i campi la cui assenza è una lacuna; quelli la cui assenza significa qualcosa, cioè i due del regime di acquisto dove il vuoto è il terzo stato di ADR-014 e la base d'asta dove il vuoto significa che non è un'asta, restano intatti. La stessa logica governa la scheda di trattativa, che non stampa i numeri dipendenti da un dato assente invece di stamparli calcolati su ciò che c'è.

Motivazione. La scelta è fra due modi di essere incompleti, e non fra completo e incompleto. Un modello che mostra rendimenti a zero e cinque controlli non superati è visibilmente incompleto; un modello che mostra un costo totale di 172.000 euro calcolato su una rendita di esempio è apparentemente sano. La prima forma costa un file che sembra rotto, la seconda costa una decisione presa su un numero falso, e fra le due non c'è paragone. Vale la stessa logica di ADR-013 spostata dai riferimenti ai dati: fra due modi di sbagliare si sceglie quello che sbaglia rumorosamente.

Sulla scheda, la ragione è la stessa portata all'estremo. Il prezzo massimo sostenibile senza canone atteso risultava negativo, e la casella annunciava uno sconto da ottenere del centoquattro per cento del prezzo: un numero aritmeticamente corretto, in una casella intitolata "il numero da portare in trattativa". Un documento che si porta in agenzia non può contenere una cifra del genere accanto a un'etichetta del genere, e la soluzione non è un avviso in fondo ma il rifiuto di stampare la cifra.

Conseguenze. Chi genera un file precompilato deve aspettarsi di vederlo incompleto, ed è il comportamento corretto: i campi azzerati sono elencati dal comando con il valore di esempio che avevano, così che si veda cosa è stato tolto. I controlli di plausibilità del Cruscotto diventano il presidio naturale di questa decisione, perché è su di loro che l'azzeramento si manifesta: sul file di house_6 passano da tre a cinque non superati. Resta un limite dichiarato: i controlli rilevano lo zero e non la falsità, quindi un dato sbagliato ma plausibile scritto a mano nel registro non viene intercettato da nulla, e nessun presidio automatico può farlo.

## ADR-020, la leggibilità di un artefatto è un requisito, e i suoi presidi stanno nel generatore

Data: 2026-09-02. Stato: accettata.

Contesto. Il workbook è arrivato a ventun fogli, tutti verificati, con formule vive e nessuna cella in errore. La segnalazione d'uso, arrivata da chi ha seguito il progetto dall'inizio, è stata che non si capiscono i dati di input, quelli da selezionare e quelli di output, e che ci si perde. È un difetto reale di una classe che nessun test di correttezza cattura, perché non riguarda ciò che il file calcola ma ciò che chi lo apre riesce a fare.

Decisione. Tre presidi, tutti dentro il generatore e non affidati alla disciplina di chi scriverà un foglio nuovo. Le celle con una validazione a elenco hanno un colore proprio, l'azzurro, assegnato dall'unico helper previsto per applicare una tendina. Ogni foglio porta in testa una fascia che dichiara se lì si scrive o si legge, scritta dalla funzione del titolo che ogni foglio chiama per prima, leggendo un registro riempito dalla stessa tupla da cui nasce l'indice. L'indice porta cinque righe di primi passi in linguaggio elementare e una legenda che mostra i colori invece di descriverli.

Motivazione. Sul colore delle tendine, la ragione è che l'assenza di distinzione produceva un errore d'uso silenzioso: si scrive in una cella che voleva una scelta, Excel rifiuta, e il messaggio non spiega. Sul fatto che il presidio stia nell'helper e non nella convenzione, vale la logica di ADR-013: una convenzione dichiarata si dimentica, un helper unico rende l'errore impossibile. Il test che ne verifica l'effetto ha trovato immediatamente un caso che avevo mancato, cioè un riempimento generico che girava dopo e sovrascriveva.

Sulla fascia, la ragione è che l'informazione esisteva ma solo nell'indice, e chi arriva su un foglio dalle linguette in basso non passa dall'indice. Ripeterla dove serve è duplicazione soltanto se le due copie si mantengono a mano: venendo dalla stessa tupla non possono divergere, e un test verifica anche la coerenza fra le due.

Sulla legenda che mostra invece di descrivere, la ragione sta nella segnalazione stessa: l'associazione fra un nome di colore e il suo significato non era chiara nemmeno a chi conosceva il progetto, quindi ripeterla a parole non l'avrebbe resa chiara. Una cella gialla accanto alla parola gialla non chiede di ricordare niente.

Conseguenze. Un foglio nuovo eredita la fascia se e solo se è dichiarato nella tupla dell'indice, e il test lo impone; eredita il ritorno all'indice sempre, perché lo scrive la funzione del titolo; e non può avere una tendina del colore sbagliato, perché l'unico modo di applicarla la colora. La regola generale che ne discende, e che vale oltre questo progetto: quando l'artefatto prodotto è anche l'interfaccia con cui qualcuno lavora, la sua leggibilità è un requisito funzionale, va raccolta chiedendo a chi lo apre senza averlo costruito, e i suoi presidi vanno messi nel codice che genera e non nelle istruzioni per chi genera.
