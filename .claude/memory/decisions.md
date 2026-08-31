# Registro delle decisioni

> Convenzione ADR-lite, append-only. Una decisione non si cancella e non si riscrive: quando viene superata, si aggiunge una voce nuova che dichiara di superarla e ne cita il numero.

## ADR-001, il workbook porta formule vive e non valori calcolati

Data: 2026-08-28. Stato: accettata.

Contesto. Il generatore poteva scrivere numeri gia' calcolati in Python, il che sarebbe stato molto piu' semplice, oppure formule Excel che si ricalcolano da sole.

Decisione. Scrive formule. Ogni grandezza derivata e' una formula, e i riferimenti fra fogli passano per nomi definiti anziche' per indirizzi di cella.

Motivazione. Uno strumento di valutazione serve a fare domande, non a dare una risposta: il valore sta nel poter cambiare il prezzo o il tasso e vedere subito l'effetto. Un file di numeri costringerebbe a rieseguire Python per ogni ipotesi, il che nella pratica significa che nessuno le proverebbe.

Conseguenze. Il generatore e' piu' complesso e gli errori nelle formule non emergono alla scrittura. Da qui discende ADR-003.

## ADR-002, i rendimenti si calcolano sul costo totale, non sul prezzo

Data: 2026-08-28. Stato: accettata.

Contesto. La convenzione degli annunci e delle conversazioni usa il prezzo come denominatore dei rendimenti.

Decisione. Il denominatore e' il costo totale dell'operazione, cioe' prezzo piu' imposte, provvigione, notaio, oneri del mutuo e altri costi di ingresso. Il cash on cash usa invece l'esborso iniziale, cioe' il capitale proprio.

Motivazione. Quei costi sono capitale immobilizzato che non torna alla rivendita. Ignorarli gonfia il rendimento di quanto essi incidono, che sul caso di riferimento e' quasi il dieci per cento.

Conseguenze. I numeri prodotti sono sistematicamente piu' bassi di quelli che l'utente trova altrove, e questo va spiegato invece che nascosto. Il modello espone l'incidenza dei costi come indicatore a se'.

## ADR-003, il workbook si verifica aprendolo con Excel

Data: 2026-08-28. Stato: accettata.

Contesto. La libreria di generazione scrive le formule senza valutarle, quindi un errore di sintassi, un nome non risolto o un blocco XML malformato non emergono in fase di scrittura. Durante la costruzione un elemento di validazione vuoto ha reso il file irricevibile per Excel senza che nulla lo segnalasse a monte.

Decisione. Esiste uno script che apre il workbook con Excel via automazione COM, forza il ricalcolo completo, elenca ogni cella in errore e stampa i valori chiave. Va eseguito dopo ogni modifica al generatore.

Motivazione. E' l'unico modo per sapere che il file non solo si scrive ma funziona. La sola alternativa disponibile su questa macchina sarebbe stata l'ispezione manuale.

Conseguenze. La verifica richiede Excel installato ed e' quindi legata alla piattaforma. Non e' un vincolo per usare lo strumento, solo per svilupparlo. L'automazione COM va invocata con la cultura en-US esplicita, perche' con una console italiana il late binding non risolve i metodi.

## ADR-004, l'acquisizione automatica degli annunci rispetta robots.txt senza eccezioni

Data: 2026-08-28. Stato: accettata.

Contesto. La raccolta degli annunci puo' avvenire manualmente, per incolla del testo, o per prelievo diretto delle pagine dai portali.

Decisione. Il prelievo diretto e' subordinato alla verifica del `robots.txt` per il singolo URL, con astensione in caso di file non leggibile, intervallo minimo di cinque secondi per dominio, user agent che si dichiara, e nessun meccanismo di aggiramento delle protezioni. Non si raccolgono dati di contatto di persone fisiche.

Motivazione. La materia tocca i termini di servizio dei portali, il diritto sui generis sulle banche dati e la protezione dei dati personali. Il fatto che un dato sia visibile non lo rende liberamente riutilizzabile. Il valore dello strumento non dipende dal prelievo automatico: le altre due vie restano sempre disponibili.

Conseguenze. Su alcuni portali il prelievo non sara' possibile, e il programma lo dice spiegando le alternative anziche' fallire.

## ADR-005, l'accantonamento per la ristrutturazione entra nel conto economico

Data: 2026-08-28. Stato: accettata.

Contesto. Un immobile tenuto quarant'anni richiede almeno un rifacimento completo, di ordine pari a un terzo del valore.

Decisione. La spesa e' ripartita come costo annuo ricorrente nel conto economico della locazione, accanto alla manutenzione ordinaria, e non trattata come evento futuro fuori dal rendimento corrente.

Motivazione. E' l'impostazione dei fogli di Paolo Coletti ed e' quella corretta: ignorarla e' il modo piu' comune di sopravvalutare un immobile. Sul caso di riferimento sposta il rendimento netto dall'uno virgola tre allo zero virgola cinque per cento.

Conseguenze. La voce compare una sola volta, dentro il reddito operativo netto, e la colonna separata che il foglio del flusso di cassa aveva inizialmente e' stata rimossa perche' la contava due volte.

## ADR-006, la revisione fiscale e' datata e vive in un solo file

Data: 2026-08-28. Stato: accettata.

Contesto. Le aliquote cambiano con ogni legge di bilancio e sono sparse per natura fra imposte di trasferimento, mutuo, locazione, IMU e plusvalenza.

Decisione. Tutti i parametri normativi stanno in `src/immobiliare/parametri.py`, con la fonte accanto a ciascuno e una data di revisione dichiarata in testa, e sono replicati nel foglio Parametri del workbook dove restano modificabili.

Motivazione. L'aggiornamento annuale deve essere un intervento in un punto solo, e chi legge un numero deve poter risalire alla fonte senza cercare.

Conseguenze. Il foglio Parametri e' modificabile dall'utente: se una aliquota cambia in corso d'anno si aggiorna li' senza rigenerare, e il codice si allinea alla revisione successiva.

## ADR-007, la simulazione probabilistica separa le estrazioni fisse dal calcolo vivo

Data: 2026-08-31. Stato: accettata.

Contesto. Passare dai tre scenari scelti a mano a una distribuzione di esiti richiede molte estrazioni casuali dentro un foglio di calcolo senza macro. La funzione casuale nativa e' volatile e cambierebbe tutti i mille scenari a ogni tocco di cella; pre-calcolare tutto in Python e scrivere valori tradirebbe ADR-001.

Decisione. I due strati vivono separati nel foglio nascosto `_Estrazioni`. Le estrazioni sono numeri fissi generati in Python con seme dichiarato nel modulo, `SEME_SIMULAZIONE`. Il calcolo che le trasforma in esiti sono formule vive che leggono gli input dell'utente.

Motivazione. Riproducibilita' e interattivita' sembravano in conflitto e non lo erano: sono due strati diversi. Due persone che discutono lo stesso file devono guardare gli stessi numeri, e il file deve comunque reagire a un cambio di prezzo.

Conseguenze. Il ricalcolo dell'intero workbook costa sei decimi di secondo. Le variabili sono assunte indipendenti, e il limite e' dichiarato dentro il foglio: la distribuzione va letta come misura della dispersione, non come probabilita' oggettiva. Chi aggiunge una variabile aleatoria deve decidere esplicitamente se la sua incertezza e' di livello, e allora non si scala, oppure di variazione annua di una grandezza che si compone, e allora si divide per la radice dell'orizzonte.

## ADR-008, il progetto adotta il pacchetto studio-didattico del template

Data: 2026-08-31. Stato: accettata.

Contesto. Le decisioni erano registrate qui in forma sintetica, ma il perche' di sette scelte strutturali, e soprattutto com'era il codice prima e perche' quella forma era fragile, non era scritto da nessuna parte. Chi riprende il progetto vede lo stato finale e non i vincoli che lo hanno prodotto.

Decisione. Adottato il pacchetto `studio-didattico` del template: `.claude/context/studio-didattico-master.md` con voci numerate in ordine cronologico nella struttura in quattro parti, e un approfondimento `refactor-NN-<slug>.md` per ciascuna, con il codice reale prima e dopo e la sezione su come estendere il pattern.

Motivazione. Un registro ADR dice cosa si e' deciso; non insegna a riconoscere la classe di difetto. Il caso del moltiplicatore catastale lo dimostra: era identico in Python e in Excel, quindi la doppia implementazione non l'ha intercettato, e il valore sta nel capire perche' un presidio che funziona sugli errori di trascrizione non funziona su un errore concettuale replicato fedelmente.

Conseguenze. Ogni evoluzione strutturale futura aggiunge una voce al master e il suo approfondimento. Il pacchetto e' indicizzato in `CLAUDE.md` e va letto prima di rifare diversamente una scelta che ha gia' un numero.
