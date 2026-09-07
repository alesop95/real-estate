# Studio dello stack: portare lo strumento in rete

> Studio tecnico, non una migrazione già fatta. Nasce dalla decisione del 4 settembre 2026 di spostare lo strumento da file locale ad applicazione web autenticata, con il dossier in rete e l'ipotesi che a usarlo possa essere anche un'agenzia immobiliare. Fissa che cosa cambia nel vincolo di riservatezza, misura le fasce gratuite delle piattaforme candidate invece di ricordarle, sceglie lo stack e ne dichiara le alternative escluse, affronta il nodo di dove viva il motore di calcolo, e dice che fine fanno i cinque limiti dichiarati. Si legge prima di scrivere la prima riga dell'applicazione, e si rilegge quando una scelta di questo elenco viene rimessa in discussione.

## La decisione che rende necessario questo studio

Il progetto nasce con un vincolo esplicito, scritto in [`CLAUDE.md`](../CLAUDE.md) alla voce dei vincoli di team: ogni prodotto resta un file su questa macchina, non si pubblica nulla su servizi esterni, nemmeno in forma privata e nemmeno come pagina di sola lettura. La ragione non era il tipo di contenuto ma il perimetro: il progetto tratta una trattativa reale, con prezzi obiettivo, recapiti di terzi e una strategia di acquisto, e la riservatezza era dichiarata proprietà del progetto e non del singolo file.

La decisione del 4 settembre 2026 è di superare quel vincolo con cognizione: l'applicazione va in rete, autenticata, con il dossier ospitato, perché il valore d'uso di uno strumento raggiungibile da qualunque dispositivo supera il rischio di tenere quei dati su un fornitore, a condizione che l'ambiente sia protetto. La seconda parte della decisione è che il web sostituisca il workbook Excel come modo di usare lo strumento, non che gli si affianchi.

La terza parte è emersa dopo, il 7 settembre, ed è quella che cambia più requisiti: lo scopo non è soltanto usare lo strumento meglio, è venderlo a un'agenzia immobiliare. Da qui tre conseguenze che nel resto di questo studio sono già applicate. La fascia gratuita della piattaforma deve ammettere l'uso commerciale, e non è una preferenza: è la ragione per cui il piano Hobby di Vercel esce dalla selezione, perché ne vieta l'uso commerciale con una definizione ampia. L'isolamento fra clienti diventa un requisito di prodotto e non un'accortezza, quindi l'organizzazione non è una struttura eventuale da aggiungere se un giorno servisse, ma la radice del modello dei dati dal primo giorno. E il costo di esercizio deve restare nullo per una ragione commerciale oltre che personale: un tool venduto a un'agenzia piccola non sopporta un costo fisso mensile che ne mangi il prezzo, e la scelta di una piattaforma che non può addebitare nulla è quindi anche una scelta di margine.

Una quarta conseguenza riguarda l'onestà verso chi comprerà. Uno strumento venduto e servito su una fascia gratuita ha un limite che il venditore conosce e il compratore no, e va detto invece di scoprirlo insieme: le quote sono ampie per l'uso di una o due agenzie, ma il giorno in cui l'adozione le superasse, il costo esiste e va messo nel prezzo. Il limite più vicino a essere raggiunto non è il traffico né il database, sono i cinquanta utenti dell'autenticazione perimetrale.

Le due decisioni non hanno lo stesso peso. La prima riguarda dove vivono i dati e si risolve con autenticazione, regole di accesso e una scelta di fornitore. La seconda tocca l'identità del progetto, e va guardata in faccia prima di procedere.

## Che cosa si perde lasciando Excel, detto prima di guadagnare il resto

La prima decisione architetturale di questo progetto, ADR-001, dice che il workbook non è un rapporto ma un modello: ogni numero è una formula viva, chi lo apre può cambiare un input e vedere l'intera catena ricalcolarsi, e il file resta manipolabile da chi lo riceve senza dipendere da noi. Sostituire il workbook con un'applicazione toglie tre cose concrete.

Toglie il file che si consegna. Il workbook si manda a un socio, si porta dal commercialista, si apre in banca: è un oggetto che vive senza il suo autore e senza rete. Un'applicazione autenticata è raggiungibile solo da chi ha le credenziali, e chi la guarda vede quello che l'applicazione decide di mostrare.

Toglie l'ispezionabilità della catena. In Excel si clicca su una cella e si vede la formula, e chi non si fida può rifare il conto a mano cella per cella. In un'applicazione la formula sta nel codice, e la fiducia si sposta dal foglio al programma. Questa perdita è recuperabile solo in parte, mostrando accanto a ogni risultato la sua scomposizione, ed è la ragione per cui l'interfaccia va progettata per spiegare e non solo per calcolare.

Toglie il funzionamento senza rete e senza account, che è la condizione in cui lo strumento è stato usato finora.

In cambio si guadagnano l'accesso da qualunque dispositivo, il confronto fra più immobili senza rigenerare un file, la collaborazione fra più persone sulla stessa trattativa, la possibilità che un'agenzia lo usi sui propri immobili, e la fine della manutenzione di ventun fogli di formule scritte da un generatore, che è il pezzo di codice più delicato del progetto.

Il ponte che conviene tenere è l'esportazione: una funzione che genera il workbook a partire dai dati dell'applicazione, da usare quando serve consegnare un file. Costa poco, perché il generatore esiste già, e restituisce la sola cosa davvero irrinunciabile fra quelle perdute. Va detto che con l'esportazione il generatore resta da mantenere, quindi il guadagno di manutenzione si dimezza: è una scelta da fare consapevolmente, non un contentino.

## I requisiti che la scelta deve soddisfare

Sette requisiti, in ordine di durezza. Il primo è il costo: gratuito, e gratuito in modo stabile, non gratuito per novanta giorni. Il secondo è la raggiungibilità: lo strumento serve quando serve, e una piattaforma che sospende il servizio dopo un periodo di inattività introduce un'attesa proprio nel momento in cui si riapre il dossier dopo settimane. Il terzo è l'autenticazione gestita, perché scriversi un sistema di credenziali è il modo più rapido di introdurre un difetto di sicurezza vero. Il quarto è la separazione dei dati fra utenti diversi, perché l'ipotesi dell'agenzia implica che due account non debbano mai vedere gli immobili l'uno dell'altro. Il quinto è l'ammissibilità dell'uso commerciale, che segue dalla stessa ipotesi. Il sesto è la persistenza affidabile, cioè che i dati non evaporino con una scadenza. Il settimo è che il modello di calcolo resti uno solo, o che la sua duplicazione sia presidiata da un meccanismo automatico.

## Le fasce gratuite, misurate

I numeri seguenti sono stati letti sulle pagine dei fornitori il 4 settembre 2026 e vanno riletti prima di impegnarsi, perché è materia che cambia senza preavviso. La tabella confronta soltanto ciò che decide, cioè la spesa possibile, il comportamento a riposo e i vincoli che si portano dietro.

| Piattaforma | Che cosa offre gratis | Il vincolo che pesa |
|---|---|---|
| Firebase, piano Spark | Firestore con 1 GiB di dati, 50.000 letture e 20.000 scritture al giorno, 10 GiB di traffico al mese; Hosting con 10 GB di spazio e 360 MB di traffico al giorno; autenticazione gestita fino a 50.000 utenti attivi al mese. Nessuna informazione di pagamento richiesta | Nessun codice lato server: le Cloud Functions non si distribuiscono su Spark. Ne discendono niente lavori pianificati, niente segreti, niente archiviazione di file, niente operazioni al di sopra delle regole |
| Cloudflare | Workers con 100.000 richieste al giorno, 10 ms di CPU per richiesta, 128 MB di memoria, 5 attivazioni pianificate per account e 64 fra variabili e segreti per Worker; D1 con 5 GB, 5 milioni di righe lette e 100.000 scritte al giorno; R2 con 10 GB di archiviazione, un milione di operazioni di scrittura e dieci di lettura al mese, e traffico in uscita gratuito; Zero Trust gratuito fino a 50 utenti | Nessun database parlabile direttamente dal browser: ogni operazione passa da un Worker che va scritto. L'autenticazione gestita c'è solo nella forma perimetrale di Access, oltre i cinquanta utenti va costruita |
| Supabase | Postgres da 500 MB con autenticazione gestita, 1 GB di archiviazione file, 50.000 utenti attivi al mese, 5 GB di traffico, funzioni ai bordi e lavori pianificati dentro il database | Il progetto viene sospeso dopo una settimana di inattività e si risveglia in una trentina di secondi; due progetti attivi al massimo |
| Neon | Postgres con 0,5 GB per progetto e 100 ore di calcolo al mese, cento progetti, nessuna carta richiesta | Il calcolo si sospende dopo cinque minuti di inattività e riparte alla connessione. È solo un database: autenticazione, logica e distribuzione vanno prese altrove |
| Oracle Cloud, risorse sempre gratuite | Due macchine AMD minime, più 2 OCPU e 12 GB di memoria su architettura Arm, 200 GB di disco, 20 GB di archiviazione a oggetti, due database autonomi da 20 GB, e 10 TB di traffico in uscita al mese | Serve una carta alla registrazione, e le istanze inattive vengono reclamate: Oracle le considera tali se per sette giorni il novantacinquesimo percentile di CPU, la rete e, sulle Arm, la memoria stanno tutti sotto il venti per cento. Sei tu il sistemista |
| Render | 750 ore di servizio al mese, 512 MB di memoria | Il servizio si spegne dopo quindici minuti senza traffico e riparte in circa un minuto; il Postgres gratuito scade trenta giorni dopo la creazione, con quattordici giorni di tolleranza prima della cancellazione |
| Vercel, piano Hobby | Hosting e funzioni serverless generosi per un progetto personale | L'uso commerciale è vietato dai termini, e la definizione è ampia: basta che qualcuno sia pagato per costruirlo |

Due piattaforme escono qui per ragioni che non si negoziano. Render esce perché un database che scade dopo trenta giorni non è una base su cui mettere il dossier di una trattativa. Vercel esce perché l'ipotesi dell'agenzia rende l'uso commerciale, e il piano Hobby lo vieta.

## Esiste un full-stack gratuito senza i vincoli di Firebase

La domanda nasce dal fatto che Firebase, sul piano che non può costare, proibisce il codice lato server, e con esso i lavori pianificati, i segreti e l'archiviazione dei file. È un prezzo accettabile se quelle cose non servono mai, ma nessuno può prometterlo di un prodotto che vuole crescere. La risposta della ricerca è che sì, una piattaforma che toglie quei vincoli restando gratuita, sempre accesa e senza carta esiste, ed è Cloudflare; e che esiste anche un'opzione senza alcun vincolo di piattaforma, Oracle, il cui prezzo però non è tecnico.

Su Cloudflare il codice lato server c'è ed è la norma, non l'eccezione: un Worker è codice che gira ai bordi della rete, con i suoi segreti, e la fascia gratuita ne concede centomila invocazioni al giorno. Le attivazioni pianificate ci sono, cinque per account, quindi il lavoro ricorrente che su Firebase era impossibile qui si scrive. Il database relazionale c'è, D1, con cinque gigabyte e cinque milioni di righe lette al giorno, che per questo dominio è un margine di tre ordini di grandezza. L'archiviazione dei file c'è, R2, dieci gigabyte con il traffico in uscita gratuito, il che significa che le planimetrie e le perizie del dossier possono davvero starci dentro. Nessuna di queste voci richiede una carta, e come su Firebase il superamento di un limite produce un errore e non un addebito.

Il prezzo di Cloudflare è di due tipi e va detto per intero. Il primo è che non esiste un SDK con cui il browser parli direttamente al database: su Firestore il client legge e scrive e le regole decidono, su D1 ogni operazione passa da un Worker che qualcuno deve scrivere. Significa progettare e mantenere un'interfaccia di programmazione, cioè più codice del percorso Firebase, forse due o tre volte tanto sulla parte di dati. In cambio si ottiene un database relazionale vero, che per un dominio fatto di organizzazioni, immobili, valutazioni e appartenenze è una forma più naturale di una collezione di documenti, e si evita di legare le regole di autorizzazione a un linguaggio proprietario. Il secondo prezzo è l'autenticazione: Cloudflare non offre un servizio di identità per gli utenti finali paragonabile a Firebase Authentication. Offre Access, che è autenticazione perimetrale, gratuita fino a cinquanta utenti, con accesso via codice monouso spedito per posta o tramite un fornitore di identità esterno, e che consegna al Worker un token firmato con l'identità di chi entra. Per uno strumento interno o per un'agenzia con pochi collaboratori è più che sufficiente ed è la strada consigliata. Se un giorno servisse la registrazione aperta di utenti sconosciuti, quella è la soglia oltre la quale l'autenticazione va costruita con una libreria, che è il pezzo più delicato da scrivere e la sola parte di questo studio che sconsiglierei di affrontare senza necessità.

Sul dieci per cento di margine che a prima vista preoccupa, cioè i dieci millisecondi di CPU per richiesta del piano gratuito, vale una precisazione: sono dieci millisecondi di calcolo effettivo, non di durata della richiesta, e l'attesa di una query non li consuma. Un'operazione di lettura o scrittura su D1 ne usa una frazione. Non ci starebbe invece la simulazione probabilistica su mille scenari, che però in questa architettura gira nel browser e non sul server, quindi il limite non tocca nulla di ciò che facciamo.

L'opzione senza vincoli di piattaforma è Oracle. Le risorse sempre gratuite sono di un altro ordine di grandezza rispetto a tutto il resto di questa tabella: due processori Arm con dodici gigabyte di memoria, duecento gigabyte di disco, due database autonomi, dieci terabyte di traffico al mese. Su una macchina così ci si mette qualunque cosa, Postgres, un server applicativo, un motore di ricerca, e nessun limite di piattaforma esiste perché non c'è piattaforma: c'è un computer. Il prezzo è in tre parti. La prima è la carta di credito richiesta alla registrazione, che non viene addebitata finché non si passa a pagamento ma che è comunque un dato che si consegna. La seconda è la politica di recupero delle istanze inattive: Oracle considera inattiva una macchina se per sette giorni il novantacinquesimo percentile di CPU e di rete, e sulle Arm anche la memoria, stanno sotto il venti per cento, e le tre condizioni valgono insieme. Uno strumento usato a raffiche durante una trattativa e poi lasciato in silenzio per settimane sta esattamente in quella zona, e tenerlo artificialmente occupato per non farselo togliere è il genere di espediente che dichiara la fragilità di una scelta. La terza, e la più seria, è che si diventa sistemisti: aggiornamenti di sicurezza, certificati, salvataggi, sorveglianza. Il tempo che si guadagna non pagando l'hosting si perde a fare l'operatore, e su un progetto la cui parte di valore è il modello di calcolo è un cattivo scambio.

Le altre due candidate risolvono una parte sola del problema. Supabase è la più completa come servizio, con Postgres, autenticazione gestita, archiviazione e lavori pianificati dentro il database, ma sospende i progetti gratuiti dopo una settimana di inattività, ed è la stessa obiezione di sempre: il profilo d'uso di questo strumento è fatto di silenzi lunghi. Neon è un ottimo Postgres gratuito che si sospende in cinque minuti e si risveglia in meno di un secondo, ma è solo un database: autenticazione, logica e distribuzione vanno prese altrove, quindi non è un'alternativa ma un pezzo.

## La scelta, e le alternative escluse deliberatamente

La raccomandazione cambia rispetto alla prima stesura di questo studio, e cambia per la ragione che la domanda era diversa: la prima volta il criterio era il minimo attrito per arrivare a un'applicazione funzionante, e Firebase vinceva; posto il vincolo che lo strumento non debba mai trovarsi murato dentro la fascia gratuita, vince Cloudflare, perché è la sola piattaforma che dà codice lato server, lavori pianificati, segreti e archiviazione di file senza chiedere una carta e senza spegnersi per inattività.

| Livello | Scelta | Ruolo |
|---|---|---|
| Interfaccia | React con TypeScript, costruito con Vite | applicazione a pagina singola, servita come file statici |
| Componenti e tema | Material-UI | tutti gli stili dal tema centrale, nessun valore scritto a mano nei componenti |
| Stato condiviso | Jotai | atomi, niente Redux e niente Context per lo stato di dominio |
| Dati remoti | TanStack Query | interrogazioni e mutazioni con cache e ritentativi, verso la nostra interfaccia di programmazione |
| Logica lato server | Cloudflare Workers, con Hono per le rotte | l'unico posto dove si scrive che cosa un utente può fare |
| Dati | Cloudflare D1, cioè SQLite gestito | relazionale, perché il dominio lo è: organizzazioni, membri, immobili, valutazioni |
| File | Cloudflare R2, quando serviranno | dieci gigabyte con traffico in uscita gratuito, non nella prima versione |
| Identità | Cloudflare Access, gratuito fino a cinquanta utenti | codice monouso per posta o fornitore esterno; il Worker riceve un token firmato e lo verifica |
| Distribuzione | Cloudflare Workers con risorse statiche, da GitHub | l'applicazione e la sua interfaccia di programmazione stanno nello stesso deploy |
| Motore di calcolo | TypeScript nel browser, con vettori di riscontro generati dal motore Python | vedi la sezione dedicata, resta il nodo vero |
| Esportazione | generazione del workbook su richiesta, dal generatore Python esistente | il ponte verso chi un file lo vuole ancora |

Le esclusioni restano dichiarate. Firebase esce non perché sia peggiore in assoluto, ma perché il suo piano gratuito impone un'architettura senza server che va bene finché non serve nulla di ciò che un server fa: la prima volta che servisse un promemoria per una scadenza, un aggancio a un servizio esterno con una chiave, o un pannello che agisce sui dati di un altro utente, si dovrebbe migrare tutto o pagare. Supabase esce per la sospensione settimanale. Oracle esce per la politica di recupero delle istanze inattive e per il costo di gestione. Render e Vercel restano escluse per le ragioni della tabella. Non si usa un framework con rendering lato server, perché su questa architettura non aggiunge nulla e complica la distribuzione.

Una cosa va detta con onestà, perché è il costo vero della scelta: questa strada richiede più lavoro di Firebase. Su Firebase l'interfaccia parla direttamente con il database e la sicurezza si scrive in regole dichiarative; qui va scritta un'interfaccia di programmazione, rotta per rotta, con la sua validazione e i suoi test. È il prezzo per non avere un soffitto sopra la testa, ed è una scelta ragionevole solo perché il progetto ha un orizzonte lungo e un'ipotesi di crescita. Se l'orizzonte fosse una valutazione sola e poi il silenzio, Firebase sarebbe la risposta giusta.

## La garanzia di gratuità, e come si presidia

Il requisito che lo strumento resti gratuito non si soddisfa con la disciplina di chi guarda i consumi: si soddisfa con una proprietà strutturale. Su Cloudflare quella proprietà è che il piano gratuito non richiede un metodo di pagamento e che il superamento di un limite produce un errore, non un addebito: la documentazione di D1 lo dice per esteso, cioè che al superamento del limite giornaliero le interrogazioni falliscono restituendo un errore al client fino al ripristino. Vale la stessa cosa che valeva su Firebase, con una differenza importante a favore: qui il limite si supera senza che l'architettura debba rinunciare al codice lato server.

Il presidio contro la deriva è di tre pezzi, da costruire insieme allo scheletro. Il primo è non collegare mai un metodo di pagamento all'account: finché non c'è, la spesa è impossibile e non solo improbabile. Il secondo è un controllo automatico che fallisce se la configurazione introduce un servizio a pagamento o supera i limiti dichiarati del piano gratuito, per esempio più di cinque attivazioni pianificate. Il terzo è una pagina di stato dell'applicazione che mostri i consumi rispetto ai limiti, perché un errore che arriva quando la quota è finita va riconosciuto per quello che è invece di sembrare un guasto.

Restano fuori dalla prima versione due cose, non per vincolo di piattaforma ma per disciplina di rilascio: l'archiviazione dei file, che si aggiunge quando il dossier documentale la richiederà davvero, e la registrazione aperta di utenti, perché finché gli utenti sono pochi si creano dalla console di Access e un modulo di iscrizione aperto è solo una superficie di attacco in più.

## Come funziona, e dove sta la sicurezza

Vale ricostruire il percorso di una richiesta, perché con questa architettura è diverso da quello di Firebase e la differenza è tutta a vantaggio della chiarezza.

Chi apre l'indirizzo dell'applicazione incontra prima di tutto Access, che non è codice nostro: se non ha una sessione valida gli chiede di identificarsi, con un codice monouso spedito alla sua posta oppure con il fornitore di identità configurato. Superato quel passaggio, il browser riceve i file statici dell'applicazione e Access aggiunge a ogni richiesta successiva un token firmato che dice chi è quella persona. Il Worker verifica la firma di quel token contro le chiavi pubbliche di Cloudflare, e da quel momento sa con certezza l'identità del chiamante senza aver scritto una riga di logica di autenticazione.

L'autorizzazione, cioè che cosa quella persona può fare, è invece codice nostro e sta in un posto solo: il Worker. Ogni rotta comincia risolvendo l'appartenenza del chiamante all'organizzazione richiesta e il suo ruolo, con una interrogazione al database, e da lì decide. La differenza rispetto alle regole di Firestore è che qui la decisione è codice ordinario, quindi si legge, si prova con i test e si corregge come qualunque altra funzione, invece di vivere in un linguaggio dichiarativo separato. Il rovescio della medaglia è che una rotta scritta male è una rotta che dimentica il controllo, mentre una regola dimenticata nega per definizione: per questo la disciplina da adottare è che ogni rotta passi da una funzione unica di autorizzazione, e che un test verifichi per ciascuna sia il caso permesso sia quello negato.

Il calcolo resta nel browser, e la ragione non cambia con la piattaforma: un calcolo va protetto quando il suo risultato concede qualcosa, e qui il risultato è un consiglio a chi ha digitato gli input. Il modello è pubblico e documentato in questo repository, quindi non c'è niente da nascondere.

## Le quote, e quanto margine danno davvero

I numeri servono a sapere se il vincolo stringe o è teorico, e con questa scelta non stringe. Le centomila richieste al giorno del piano gratuito si consumano a una per operazione: una sessione di lavoro seria su un immobile ne fa qualche decina, quindi il tetto sta intorno alle migliaia di sessioni al giorno, che è un ordine di grandezza sopra qualunque uso previsto. I cinque milioni di righe lette al giorno su D1 sono fuori scala per un dominio che conta gli immobili a decine. Le centomila righe scritte al giorno lo sono altrettanto. I cinque gigabyte di database bastano per un archivio di immobili e valutazioni che non si esaurirà. I dieci gigabyte di R2, quando servirà, tengono qualche migliaio di documenti di trattativa, con il traffico in uscita gratuito, che è la voce su cui gli altri fornitori guadagnano.

Il limite che va sorvegliato non è nessuno di questi: sono i cinquanta utenti di Access, perché è l'unico che si avvicina a un valore realistico se lo strumento venisse adottato da più di un'agenzia. È la soglia che, se raggiunta, impone la scelta fra pagare le sedute oltre la cinquantesima o costruire l'autenticazione. Meglio saperlo adesso che scoprirlo allora.

## I passi da compiere, una volta sola

Sono sette e li compie chi possiede l'account, perché il progetto nasce da lì e non da un file di questo repository.

1. Registrare un account su Cloudflare, che non chiede un metodo di pagamento. Non aggiungerne uno neppure dopo: è la garanzia che la spesa resti impossibile.
2. Dalla sezione Workers e Pages, creare l'applicazione, che a quel punto è raggiungibile a un indirizzo del tipo `valutazione-immobili.<account>.workers.dev`, con certificato incluso. Un dominio proprio si aggiunge dopo e non cambia nulla.
3. Creare il database D1 e annotarne l'identificativo, che serve al file di configurazione del progetto.
4. Attivare Zero Trust sul piano gratuito, creare l'organizzazione, e scegliere come metodo di accesso il codice monouso per posta, che non richiede alcun fornitore esterno.
5. Definire in Access un'applicazione che protegge l'indirizzo, con una politica che elenca le poste elettroniche ammesse. Sono gli utenti dello strumento, e finché sono pochi si aggiungono da lì.
6. Creare un token di interfaccia per la distribuzione automatica da GitHub, con i soli permessi di modifica dei Workers, e conservarlo fra i segreti del repository.
7. Consegnare all'ambiente di sviluppo l'identificativo dell'account, quello del database e il nome dell'organizzazione Zero Trust. Nessuno dei tre è un segreto, e ciò che protegge i dati non sono quei nomi ma la politica di Access e i controlli scritti nel Worker.

## Il nodo vero: dove vive il motore di calcolo

Questo è il punto su cui lo studio esiste, perché è l'unico dove la scelta sbagliata produce un danno permanente invece di un fastidio.

Il progetto ha oggi due implementazioni dello stesso modello, il motore Python in `calcoli.py` e le formule vive del workbook, e la disciplina che le tiene allineate è un impianto di test che le confronta sullo stesso caso. Portare il calcolo nel browser significa introdurne una terza, e una terza implementazione non presidiata è il modo classico in cui un modello finanziario comincia a dire due cose diverse a seconda di dove lo si guarda.

La prima via è far girare il motore Python esistente dentro il browser, compilato in WebAssembly. Nessuna riscrittura, nessuna terza implementazione, e i dati non lascerebbero il browser di chi calcola. Il prezzo è il peso: l'ambiente Python nel browser costa alcuni megabyte da scaricare e qualche secondo di avvio la prima volta, che su uno strumento aperto da un professionista fra un appuntamento e l'altro è un costo pagato ogni volta e molto visibile.

La seconda via è portare il motore in TypeScript e tenere quello Python come implementazione di riferimento. L'interfaccia diventa immediata, il ricalcolo è istantaneo mentre si digita, e l'applicazione pesa quanto una pagina normale. Il prezzo è la terza implementazione, che va presidiata: il presidio proposto è un generatore che, dal motore Python, produce alcune centinaia di casi con i loro risultati attesi, e una suite in TypeScript che li verifica tutti a ogni build. È lo stesso principio con cui oggi il workbook viene confrontato con il motore, portato da un caso a un campione sistematico.

La terza via è tenere il motore Python su un servizio e chiamarlo dall'applicazione. Una sola implementazione, ma un server da tenere sveglio, un requisito di raggiungibilità violato dalle fasce gratuite disponibili, e gli input che viaggiano in rete a ogni ricalcolo.

La raccomandazione è la seconda, con il presidio dichiarato sopra come parte non negoziabile della definizione di completamento. La prima resta la scelta corretta se il presidio non venisse costruito: meglio un'applicazione lenta ad avviarsi che due modelli che divergono in silenzio.

## Architettura proposta

L'applicazione è una pagina singola con tre livelli di accesso. Un utente vede solo i propri immobili e le proprie valutazioni. Un'organizzazione, che è la forma con cui si modella un'agenzia, raccoglie più utenti che condividono un insieme di immobili, con un ruolo di amministrazione che può invitare e revocare. Un livello di sola lettura serve al caso in cui una valutazione va mostrata a un terzo, il socio o il consulente, senza dargli la possibilità di modificarla: è il sostituto più vicino al file che oggi si consegna.

I ventun fogli del workbook non diventano ventun pagine. La traduzione naturale raggruppa in sei aree: l'immobile con i suoi dati e le verifiche, il costo dell'operazione con imposte e accessori, il finanziamento con simulatore e piano, la messa a reddito con i quattro regimi a confronto, la decisione con cruscotto, scenari, rischio e confronto con l'affitto, e il portafoglio con il registro degli immobili e la graduatoria. Le checklist e il dossier documentale diventano liste con stato, che è la forma in cui erano nate e che il foglio di calcolo rendeva goffe.

Ogni area segue lo stesso schema, mutuato dal progetto gemello: una sezione nell'interfaccia, un hook che parla con i dati attraverso l'interfaccia di programmazione, un tipo che ne descrive la forma e che è lo stesso da una parte e dall'altra, perché il Worker e l'applicazione stanno nello stesso repository e nello stesso linguaggio. Il calcolo non vive nelle sezioni: vive nel modulo del motore, che riceve una descrizione dell'immobile e restituisce i risultati, esattamente come fa oggi la funzione Python.

## Dati e sicurezza

I dati vivono in D1, cioè in uno SQLite gestito, con uno schema relazionale che riflette il dominio: organizzazioni, membri con il loro ruolo, immobili, valutazioni. L'isolamento fra organizzazioni non è una proprietà dello schema ma del codice che lo interroga, e questa è la differenza da tenere a mente rispetto a un database con regole dichiarative: là una regola dimenticata nega, qui una rotta che dimentica il controllo concede. La disciplina che ne discende è che nessuna rotta interroghi il database direttamente: ogni rotta passa da una funzione unica che risolve chiamante, organizzazione e ruolo e restituisce un contesto già autorizzato, e ogni interrogazione filtra per l'organizzazione di quel contesto. La verifica non si fa a occhio: per ciascuna rotta si scrive la coppia di test che prova il caso permesso e quello negato, e la suite gira contro il database locale dell'ambiente di sviluppo, non contro quello vero.

Tre cose non entrano nell'applicazione, e vanno decise ora e non dopo. Le fonti e i parametri normativi restano nel codice, versionati, perché sono conoscenza del progetto e non dato dell'utente. Le quotazioni OMI restano un'importazione manuale semestrale per la ragione di ADR-011, cioè l'autenticazione personale ai servizi telematici, e nell'applicazione diventano dati di riferimento caricati dal manutentore, non da ciascun utente. I documenti veri della trattativa, cioè visure, planimetrie e perizie, sono file, e su questa architettura hanno una casa: R2, con dieci gigabyte gratuiti e il traffico in uscita non fatturato, che è la voce su cui gli altri fornitori guadagnano. Non entrano comunque nella prima versione, e la ragione non è tecnica ma di rilascio: finché il dossier documentale è una lista di voci con il loro stato, come nel workbook di oggi, l'applicazione non deve custodire nulla di pesante e nulla di riservato oltre ai numeri. Si aggiunge quando servirà davvero, sapendo che il posto dove metterli esiste già.

## Che fine fanno i cinque limiti dichiarati

Il passaggio non è un modo per aggirare i limiti: tre dei cinque si risolvono per costruzione, uno si risolve nel motore e va fatto comunque, uno resta.

La tabella di sensibilità sul prezzo, che oggi propaga l'incidenza dei costi accessori dello scenario base invece di ricalcolarla, è un limite del foglio: in un'applicazione ogni riga della tabella è una chiamata al motore, e l'approssimazione sparisce senza che nessuno debba scomporre nulla.

L'opzione prezzo-valore e la qualifica di lusso, che nel confronto fra immobili restano globali perché il foglio le prende da una cella sola, diventano attributi di ciascun immobile, che è la forma corretta e che il registro degli annunci già prevede per la prima casa e per il venditore impresa.

Il piano di ammortamento che si ferma a quarant'anni è un limite della lunghezza di una tabella di Excel. Nel motore l'ammortamento si calcola fino a chiusura, e il caso in cui un rialzo impedisce la chiusura si segnala come tale invece di essere troncato.

L'indipendenza delle variabili nella simulazione del rischio non era un limite di Excel ed era l'unico dei cinque che andava affrontato nel modello: è stato risolto il 4 settembre 2026, prima di aprire questo cantiere, con il fattore comune descritto in [`metodo-e-metriche.md`](metodo-e-metriche.md). La simulazione vive per intero nel workbook, perché il motore Python non ha una parte probabilistica, quindi la correzione è nelle formule del foglio e nelle estrazioni congelate. Quando il motore verrà portato in TypeScript la simulazione andrà scritta là per la prima volta, e il fattore comune è la specifica da riportare: un solo parametro leggibile come correlazione, pesi pari alla radice della correlazione e del suo complemento, e la riduzione esatta al caso indipendente quando il parametro è zero, che è la proprietà da mettere fra i vettori di riscontro.

La fornitura OMI che richiede un'autenticazione personale resta esattamente com'è, perché non dipende da noi.

## Il piano, in fasi con un criterio di chiusura ciascuna

La prima fase è il motore in TypeScript con il suo presidio: il generatore di vettori dal motore Python, la traduzione, e la suite che li verifica. È chiusa quando tutti i vettori passano e la differenza massima rispetto al riferimento sta sotto la soglia dichiarata. Non produce interfaccia, e va fatta per prima perché è la sola parte che, se sbagliata, invalida tutto il resto.

La seconda fase è lo scheletro autenticato: account Cloudflare senza metodo di pagamento, applicazione servita con le sue risorse statiche, database D1 con lo schema iniziale, Access davanti all'indirizzo con due poste ammesse, e un Worker con tre rotte, cioè elenco degli immobili, lettura di uno e scrittura di uno. È chiusa quando due utenti di organizzazioni diverse non vedono i dati l'uno dell'altro e i test lo dimostrano rotta per rotta, e quando il controllo automatico sui limiti del piano gratuito è in funzione.

La terza fase sono le sei aree, una per volta, ciascuna con la propria sezione, il proprio hook e i propri tipi.

La quarta fase è la migrazione dei dati esistenti, cioè il registro degli immobili e le verifiche comunali, e l'esportazione del workbook come ponte.

La quinta fase è la documentazione tecnico-didattica, che in questo progetto non è un adempimento finale ma il modo in cui le decisioni restano leggibili: ogni fase che introduce un pattern nuovo produce la propria voce nello studio didattico, con il codice reale prima e dopo e la ragione del salto.

## Che cosa va deciso o verificato prima di cominciare

Tre cose. Il vincolo di team in `CLAUDE.md` va riscritto, perché oggi vieta esattamente ciò che si sta per fare, e va riscritto dicendo che cosa può stare in rete e che cosa no, non cancellato. Va deciso se il workbook resta generabile: la risposta cambia se il generatore va mantenuto o se può essere archiviato, ed è la differenza fra dimezzare la manutenzione e non ridurla affatto. E va confermata la soglia dei cinquanta utenti di Access come sufficiente per l'orizzonte previsto, perché è l'unico limite di questa architettura che un'adozione riuscita può davvero incontrare, e la risposta cambia il disegno dell'autenticazione, che non è un dettaglio.
