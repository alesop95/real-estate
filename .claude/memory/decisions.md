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

## ADR-009, il fascicolo dei documenti sta in un foglio separato dalla checklist

Data: 2026-08-31. Stato: accettata.

Contesto. Serviva l'elenco della documentazione tecnica da farsi consegnare in fase di trattativa, al livello di dettaglio con cui la chiederebbe un tecnico incaricato. La Checklist esisteva gia' e conteneva alcune di quelle voci in forma di verifica.

Decisione. Due fogli distinti. La Checklist elenca verifiche e clausole, con il loro perche' e chi le fa. Il Dossier tecnico elenca documenti, con chi li rilascia, la norma che li rende dovuti, il costo indicativo e lo stato della raccolta, e ha una tassonomia propria a tre valori: bloccante, importante, se ricorre.

Motivazione. Le due cose rispondono a domande diverse in due momenti diversi. Le verifiche si chiudono prima di firmare; i documenti si chiedono prima ancora, quando si ha potere negoziale, e senza di essi le verifiche non si possono fare. Unirle avrebbe prodotto una tabella con meta' delle colonne vuote su meta' delle righe, e avrebbe nascosto il contatore che serve davvero, cioe' quanti documenti bloccanti mancano ancora.

Conseguenze. Il Cruscotto porta due contatori invece di uno, le verifiche aperte e i documenti bloccanti mancanti. La tassonomia del peso e' una stringa confrontata da `COUNTIFS`, quindi fragile per costruzione: un test verifica che ogni riga usi uno dei tre valori esatti, perche' un valore scritto diversamente sparirebbe dal conteggio senza errore e il cruscotto direbbe che non manca nulla.

## ADR-010, dai progetti senza licenza si prende l'informazione, non il codice

Data: 2026-08-31. Stato: accettata.

Contesto. Il bot Telegram open source `finanza-che-conta` pubblica l'euro short-term rate ogni lunedi' e l'inflazione ISTAT a ogni comunicato, ed e' la fonte da cui e' stato individuato l'identificativo del flusso SDMX dei prezzi al consumo, che la documentazione di ISTAT non rende facile trovare. Il repository, pero', non dichiara alcuna licenza.

Decisione. Nessun codice ripreso. Il modulo `indicatori.py` e' scritto da zero sullo stesso endpoint pubblico, e il credito e' dato nella docstring e nel registro delle fonti per la scoperta della fonte, non per il codice.

Motivazione. L'assenza di licenza non significa dominio pubblico ma il contrario: ogni diritto e' riservato all'autore, e la pubblicazione su una piattaforma non concede alcun permesso di riuso. Un endpoint pubblico, invece, e' un fatto: sapere che ISTAT espone i prezzi al consumo al flusso `167_744_DF_DCSP_NIC1B2015_1` non e' materiale protetto, e' un'informazione.

Conseguenze. La regola vale in generale per questo progetto: prima di riprendere codice da una fonte esterna si guarda la licenza, e in sua assenza si riscrive. Vale anche il contrario, cioe' che i progetti da cui si e' preso solo il perimetro funzionale restano citati come tali nel registro delle fonti, senza attribuire loro un contributo che non hanno dato.

## ADR-011, i servizi autenticati dell'area riservata restano manuali, e la fonte OMI si cita

Data: 2026-08-31. Stato: accettata. Estende ADR-004.

Contesto. Il progetto usa quattro servizi dell'area riservata dell'Agenzia delle Entrate: forniture OMI, visure e ispezioni ipotecarie, valori immobiliari dichiarati, fogli di mappa catastale. Accedendovi si accettano le condizioni generali di consultazione della banca dati catastale, decreto 4 maggio 2007 e successive integrazioni.

Decisione. Nessuno dei quattro viene automatizzato. Il file lo scarica la persona, il programma lo ingerisce da disco. Inoltre la stringa `Agenzia Entrate - OMI`, obbligatoria per la fornitura, e' esposta come `omi.ATTRIBUZIONE`, stampata in coda a ogni interrogazione e dichiarata nel foglio Fonti.

Motivazione. L'articolo 2 impone l'autenticazione personale, e simularla significherebbe far interrogare la banca dati a un programma con le credenziali di una persona. L'articolo 5 riserva all'Agenzia la facolta' di limitare le interrogazioni giornaliere, l'articolo 3 rende l'utente responsabile dell'uso improprio o eccessivo, e l'articolo 4 sanziona la violazione con l'inibizione del servizio: il costo di sbagliare non e' una discussione, e' la perdita dell'accesso. Sulla citazione della fonte, l'obbligo era assunto e non assolto: e' stato un difetto di conformita' reale, non un dettaglio.

Conseguenze. `omi.importa_fornitura` resta la sola via per i dati correnti e accetta l'archivio cosi' come arriva. Visure e ispezioni sul venditore contengono dati personali di terzi e restano sotto `_notes/`, non versionato. La regola generale che ne discende: quando una fonte richiede autenticazione personale, il confine fra automatizzabile e no non lo decide la comodita' ma il testo che si e' accettato.

## ADR-012, le aste giudiziarie entrano nel perimetro

Data: 2026-08-31. Stato: accettata. Supera la voce di `roadmap.md` che le dichiarava fuori perimetro.

Contesto. La roadmap teneva le aste giudiziarie fuori dal perimetro, con la motivazione che seguono regole proprie su perizia, custode, decreto di trasferimento e liberazione dell'immobile e che meriterebbero uno strumento separato. La motivazione era corretta sui fatti e sbagliata nella conclusione: quelle regole proprie sono poche e circoscritte, e il resto del modello, cioe' imposte, mutuo, rendimento e confronto con l'alternativa, vale identico.

Decisione. Le aste entrano, con un foglio dedicato che modella cio' che differisce e riusa tutto il resto: cinque campi nel registro, il foglio Asta, sette voci nel Dossier tecnico e la scheda `docs/aste-immobiliari.md`. Restano fuori le vendite nella liquidazione giudiziale, le aste con incanto e i beni non abitativi.

Motivazione. Il foglio non serve a calcolare meglio: serve a impedire un errore preciso. Un'asta valutata con il modello ordinario mostra un'incidenza dei costi bassa, perche' manca la provvigione, e un prezzo apparentemente ottimo, e fa sembrare conveniente un'operazione che porta con se' l'assenza di garanzia per i vizi ex art. 2922 c.c., il possesso del debitore fino al decreto ex art. 560 c.p.c., la locazione opponibile ex art. 2923 c.c. e la decadenza con perdita della cauzione ex art. 587 c.p.c. Il numero di sintesi non e' quindi il prezzo ma lo sconto sul valore di mercato, confrontato con una soglia che rappresenta il prezzo di quei rischi.

Conseguenze. Il registro cresce di cinque campi e il foglio Annunci di cinque colonne, con il contratto posizionale riallineato e i test aggiornati: il difetto era gia' stato intercettato da quei test alla prima esecuzione, che e' la conferma che servissero. Il prezzo-valore si applica anche qui, dopo la sentenza 6 del 2014 della Corte costituzionale, e resta la singola ottimizzazione piu' redditizia dell'operazione.

## ADR-013, nessun riferimento per coordinata: fra fogli si usa un nome, dentro una tabella si usa la riga restituita

Data: 2026-09-01. Stato: accettata.

Contesto. Il generatore scrive formule, e una formula deve citare altre celle. Tre forme convivevano nel codice. La prima, i nomi definiti, usata per la gran parte dei riferimenti fra fogli. La seconda, la coordinata scritta a mano, usata in due punti del Cruscotto. La terza, l'indice calcolato come riga di ancoraggio piu' una costante, usata nel conto economico del foglio Locazione e nella tabella a tre scenari del foglio Scenari.

Le ultime due hanno prodotto difetti reali, e sono stati trovati per caso. La formula del Cruscotto che da' il verdetto fra comprare e affittare citava `'Confronto affitto'!$B$52`, che era diventata la riga del patrimonio comprando invece di quella della differenza fra i due patrimoni: poiche' il patrimonio comprando e' positivo per qualunque immobile di valore, il verdetto diceva "conviene comprare" quasi sempre, e con il rendimento del portafoglio alternativo al nove per cento diceva di comprare mentre il foglio concludeva l'opposto per centoquattordicimila euro. Gli indici per offset non avevano ancora prodotto un difetto visibile soltanto perche' nessuno aveva inserito una voce in mezzo, ma erano dichiarati come il punto piu' fragile del generatore, e con ragione.

Va notato che il difetto del Cruscotto era una recidiva: il work-log del 28 agosto registra la correzione di un difetto identico nello stesso foglio, dove la differenza puntava alla riga del capitale versato. Lo stesso errore due volte nello stesso posto non e' sfortuna, e' la firma di una forma di codice sbagliata.

Decisione. Un riferimento da un foglio a un altro si scrive sempre per nome definito. Un riferimento a una riga di una tabella costruita da un helper si scrive sempre usando la riga che l'helper restituisce, mai calcolandola. Dove la tabella e' costruita da un ciclo, le righe si registrano in un dizionario sotto una chiave e le formule citano le chiavi. Nessuna coordinata di cella e nessun offset numerico compare piu' in una formula che attraversi un foglio o una tabella.

Motivazione. E' una scelta sul modo in cui un errore si manifesta, non sull'eleganza. Un nome definito inesistente produce `#NOME?` in ogni cella che lo usa, che e' impossibile non vedere e che la verifica con Excel intercetta. Una chiave assente nel dizionario solleva un KeyError alla generazione, quindi il file non viene nemmeno prodotto. Una coordinata sbagliata, invece, e' un riferimento perfettamente valido a una cella diversa: produce un numero dell'ordine di grandezza giusto, in una cella che non e' in errore, su un foglio che si apre regolarmente. Fra tre forme che sbagliano, si scelgono quelle che sbagliano rumorosamente.

Conseguenze. Il vincolo operativo che ne discende e' che una formula puo' citare solo righe gia' scritte, il che ordina la costruzione di una tabella dall'alto verso il basso. Non e' un costo: era gia' vero di fatto in entrambe le tabelle, e adesso e' verificato dal linguaggio invece che dall'attenzione. Tre test presidiano la regola: uno verifica che il nome `conf_differenza` punti alla riga la cui etichetta e' "Differenza a favore dell'acquisto", uno che il reddito operativo netto sommi esattamente le righe fra il ricavo effettivo e se stesso su tutte e quattro le colonne dei regimi, uno che ogni formula della tabella degli scenari citi solo righe interne alla tabella e precedenti alla propria.

## ADR-014, il regime di acquisto e' un dato della riga, e il vuoto e' un terzo stato

Data: 2026-09-01. Stato: accettata.

Contesto. Il foglio Confronto immobili applicava a ogni riga il regime di acquisto impostato nel foglio Immobile, cioe' prima casa oppure no e venditore privato oppure impresa con IVA. Il limite era dichiarato nel foglio e registrato come il piu' rilevante fra quelli noti. La sua conseguenza non e' un'imprecisione ma un'inversione: sullo stesso prezzo l'IVA si applica per intero mentre l'imposta di registro con il prezzo-valore si applica al valore catastale, che di norma e' una frazione, quindi un usato da privato e un nuovo da costruttore confrontati con lo stesso regime producono una graduatoria che indica come migliore proprio l'immobile che porta l'imposta piu' alta.

Decisione. Il regime si dichiara per riga nel registro, con i campi `prima_casa` e `venditore_impresa`, e il foglio di confronto lo espone in due colonne che sono anche quelle lette dalle formule delle imposte e dei costi accessori. I due campi hanno tre stati e non due: SI e NO dichiarano il regime della riga, il vuoto significa eredita dal foglio Immobile. Restano globali l'opzione prezzo-valore e la qualifica di immobile di lusso.

Motivazione. Sul perche' per riga e non globale, la ragione e' che nessuno dei due dati e' una proprieta' del modello: `venditore_impresa` e' una caratteristica dell'immobile, e `prima_casa` non e' nemmeno quello, e' una caratteristica della posizione di chi compra rispetto a quell'immobile, che cambia tipicamente fra un immobile nel Comune di residenza e uno fuori. Un dato che varia per riga va nella riga.

Sul perche' tre stati e non due, la ragione e' la compatibilita' con cio' che esiste. Trattare il vuoto come NO avrebbe cambiato in silenzio i numeri di ogni registro gia' compilato, e nel verso peggiore, cioe' togliendo l'agevolazione prima casa a dodici annunci che la avevano. Il terzo stato rende l'aggiunta esattamente neutra: chi non tocca quelle colonne vede gli stessi numeri di prima. Sui due campi restati globali, l'opzione prezzo-valore e' una scelta che si esercita in atto e conviene quasi sempre, la qualifica di lusso riguarda un caso raro, e per entrambi il costo di portarli nel registro non era giustificato dalla frequenza.

Conseguenze. Il registro passa a trentacinque campi e il foglio Annunci a trentotto colonne, con il contratto posizionale riallineato. `venditore_impresa` entra nello schema di estrazione del modello locale e `prima_casa` no, perche' il primo sta scritto negli annunci e il secondo dipende da chi compra. Da questo discende ADR-015 sulla normalizzazione. Il foglio dichiara che l'agevolazione prima casa si usa una volta sola mentre piu' righe possono dichiararla: e' corretto, perche' ogni riga e' un'alternativa alle altre e non un acquisto che si somma, ma la lettura giusta della graduatoria e' che il bonus andra' a una sola di quelle righe.

## ADR-015, i campi a tre stati si normalizzano in ingresso, e cio' che non si riconosce non si indovina

Data: 2026-09-01. Stato: accettata.

Contesto. Quattro campi del registro sono confrontati dal workbook con la stringa SI: `asta`, `nuova_costruzione`, `prima_casa`, `venditore_impresa`. Due di essi sono nello schema di estrazione passato al modello linguistico locale, che a una domanda booleana risponde volentieri `true` oppure `yes`. Excel confronta il testo senza distinguere le maiuscole, quindi `si` minuscolo funziona, mentre `true` risulta diverso da SI e viene letto come un NO.

Decisione. La normalizzazione avviene in `__post_init__` della dataclass, quindi su ogni annuncio da qualunque origine, CSV compreso: gli affermativi riconosciuti diventano SI, i negativi NO, la stringa vuota resta vuota, e cio' che non e' riconosciuto resta scritto com'e'.

Motivazione. Il caso `true` non produce un errore ma un valore di default silenzioso, ed e' peggio di un errore perche' cambia le imposte di una riga senza lasciare traccia. Sulla scelta di non indovinare, la ragione e' simmetrica: se qualcuno scrive "da chiarire col notaio", tradurlo in NO significherebbe fingere una risposta che nessuno ha dato, mentre lasciarlo visibile lo fa comportare come un vuoto nel confronto con SI e resta leggibile a chi apre il foglio. Un valore strano che si vede e' preferibile a un valore strano tradotto per ipotesi.

Conseguenze. La validazione a elenco nel foglio Annunci ammette il vuoto, cosi' che le colonne restino a tre stati anche a video. Il test copre esplicitamente `true`, che e' il motivo per cui la normalizzazione esiste, e il caso non riconosciuto, che e' il motivo per cui non e' piu' aggressiva.

## ADR-016, il prezzo massimo si risolve in forma chiusa, e porta con se' la propria verifica

Data: 2026-09-01. Stato: accettata.

Contesto. Il prezzo massimo sostenibile al rendimento obiettivo era calcolato dividendo il costo totale sostenibile per uno piu' l'incidenza percentuale dei costi accessori misurata sullo scenario base, con l'approssimazione dichiarata in nota. La nota rendeva l'approssimazione onesta ma non la rendeva innocua: sul caso di riferimento la formula dava 15.609 euro contro i 43.445 esatti, cioe' un fattore prossimo a tre, e l'errore andava nella direzione che fa sembrare impossibile qualunque trattativa. E' il numero che serve a decidere quanto offrire.

Decisione. Il prezzo massimo si ottiene risolvendo l'equazione. Il costo totale in funzione del prezzo e' `P*(1+k)+c`, l'utile e' `utile_base-(P-prezzo)*m`, e imporre il rapporto pari all'obiettivo da' `(utile_base+prezzo*m-obiettivo*c)/(obiettivo*(1+k)+m)`. Le tre grandezze stanno in tre celle visibili con la loro nota, non dentro la formula. Accanto, una cella ricalcola il rendimento a quel prezzo con le formule esatte delle imposte, minimo di legge compreso, e una mostra lo scarto dalla soglia, che deve essere zero.

Motivazione. L'errore aveva due cause indipendenti che si sommavano nella stessa direzione, ed e' la ragione per cui l'approssimazione era piu' grave di quanto la nota suggerisse. L'incidenza percentuale dei costi accessori non e' un parametro del modello ma un rapporto fra due grandezze che dipendono entrambe dal prezzo: notaio, altri costi, oneri del mutuo, imposte fisse e, con il prezzo-valore, l'intera imposta di registro sono importi fissi, quindi la loro incidenza cresce al calare del prezzo. E l'utile netto non e' indipendente dal prezzo, perche' manutenzione e accantonamento per la ristrutturazione sono quote del valore. Tenere ferme entrambe le cose e' il modo piu' comune di introdurre un errore che non si vede, perche' il risultato resta dell'ordine di grandezza giusto.

Sul perche' la verifica sta nel foglio e non in un test. La soluzione chiusa e' esatta solo sul tratto in cui il costo totale e' lineare nel prezzo, e c'e' un caso in cui non lo e': il minimo di legge dell'imposta di registro, che su prezzi molto bassi diventa vincolante. Un test coprirebbe il caso precaricato, non il caso che l'utente produce cambiando gli input a video, ed e' proprio quello il momento in cui serve saperlo. La cella dello scarto e' il presidio giusto perche' e' presente esattamente quando il problema si presenta.

Conseguenze. La riga dello scarto sul prezzo trattato deriva ora dal prezzo massimo invece di ricalcolarlo, quindi le due non possono divergere. Il nome `incidenza_costi` resta e resta utile come indicatore autonomo, ma non e' piu' usato per invertire nulla. La lezione e' registrata anche in `docs/metodo-e-metriche.md`, perche' vale oltre questa cella: un'incidenza percentuale misurata su uno scenario non e' un parametro, e usarla come tale produce errori silenziosi.
