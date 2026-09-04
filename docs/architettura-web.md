# Studio dello stack: portare lo strumento in rete

> Studio tecnico, non una migrazione già fatta. Nasce dalla decisione del 4 settembre 2026 di spostare lo strumento da file locale ad applicazione web autenticata, con il dossier in rete e l'ipotesi che a usarlo possa essere anche un'agenzia immobiliare. Fissa che cosa cambia nel vincolo di riservatezza, misura le fasce gratuite delle piattaforme candidate invece di ricordarle, sceglie lo stack e ne dichiara le alternative escluse, affronta il nodo di dove viva il motore di calcolo, e dice che fine fanno i cinque limiti dichiarati. Si legge prima di scrivere la prima riga dell'applicazione, e si rilegge quando una scelta di questo elenco viene rimessa in discussione.

## La decisione che rende necessario questo studio

Il progetto nasce con un vincolo esplicito, scritto in [`CLAUDE.md`](../CLAUDE.md) alla voce dei vincoli di team: ogni prodotto resta un file su questa macchina, non si pubblica nulla su servizi esterni, nemmeno in forma privata e nemmeno come pagina di sola lettura. La ragione non era il tipo di contenuto ma il perimetro: il progetto tratta una trattativa reale, con prezzi obiettivo, recapiti di terzi e una strategia di acquisto, e la riservatezza era dichiarata proprietà del progetto e non del singolo file.

La decisione del 4 settembre 2026 è di superare quel vincolo con cognizione: l'applicazione va in rete, autenticata, con il dossier ospitato, perché il valore d'uso di uno strumento raggiungibile da qualunque dispositivo supera il rischio di tenere quei dati su un fornitore, a condizione che l'ambiente sia protetto. La seconda parte della decisione è che il web sostituisca il workbook Excel come modo di usare lo strumento, non che gli si affianchi.

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

I numeri seguenti sono stati letti sulle pagine dei fornitori il 4 settembre 2026 e vanno riletti prima di impegnarsi, perché è materia che cambia senza preavviso: la voce di Firebase sull'archiviazione dei file è già oggi in contraddizione fra la pagina ufficiale e le ricostruzioni di terzi, e la contraddizione è segnalata sotto.

| Piattaforma | Che cosa offre gratis | Il vincolo che pesa |
|---|---|---|
| Firebase, piano Spark | Firestore con 1 GiB di dati, 50.000 letture e 20.000 scritture al giorno, 10 GiB di traffico al mese; Hosting con 10 GB di spazio e 360 MB di traffico al giorno; autenticazione fino a 50.000 utenti attivi al mese | Il traffico giornaliero dell'hosting è modesto per un'applicazione con molte immagini; sull'archiviazione dei file la situazione va verificata, vedi sotto |
| Supabase, piano gratuito | Postgres da 500 MB, 1 GB di archiviazione file, 50.000 utenti attivi al mese, 5 GB di traffico | Il progetto viene sospeso dopo una settimana di inattività e si risveglia in una trentina di secondi alla richiesta successiva; i dati restano |
| Cloudflare, piano gratuito | Pages con richieste statiche illimitate, Workers con 100.000 richieste al giorno e 10 ms di CPU per richiesta, D1 con 5 GB e limiti giornalieri di righe lette e scritte applicati dal 1 settembre 2026 | Nessuna autenticazione gestita: va costruita, ed è il requisito che qui pesa di più |
| Render, piano gratuito | 750 ore di servizio al mese, servizio web con 512 MB di memoria | Il servizio si spegne dopo quindici minuti di inattività e riparte in circa un minuto; il Postgres gratuito scade trenta giorni dopo la creazione, con quattordici giorni di tolleranza prima della cancellazione |
| Vercel, piano Hobby | Hosting e funzioni serverless generosi per un progetto personale | L'uso commerciale è vietato dai termini, e la definizione di commerciale è ampia: basta che qualcuno sia pagato per costruirlo |

Due piattaforme escono qui, e per motivi che non si negoziano. Render esce perché un database che scade dopo trenta giorni non è una base su cui mettere il dossier di una trattativa: il requisito della persistenza è violato alla radice, e la sospensione per inattività violerebbe comunque il secondo. Vercel esce perché l'ipotesi dell'agenzia rende l'uso commerciale, e il piano Hobby lo vieta: si potrebbe restare su Vercel finché lo strumento è solo personale, ma costruire su una piattaforma che va abbandonata nel momento in cui il progetto riesce è una scelta che si paga due volte.

Restano Firebase, Supabase e Cloudflare, e fra queste la differenza decisiva non è il prezzo ma il comportamento a riposo e l'autenticazione. Cloudflare non offre autenticazione gestita, quindi imporrebbe di costruire il pezzo più delicato. Supabase sospende dopo una settimana di inattività, e il modo in cui questo strumento viene usato, cioè a raffiche durante una trattativa e poi silenzio per settimane, è esattamente il profilo che la sospensione colpisce. Firebase non sospende, offre autenticazione gestita fino a cinquantamila utenti attivi al mese, e ha un modello di regole di sicurezza che si scrive accanto ai dati e si verifica con dei test.

## La scelta, e le alternative escluse deliberatamente

| Livello | Scelta | Ruolo |
|---|---|---|
| Interfaccia | React con TypeScript, costruito con Vite | applicazione a pagina singola, nessun rendering lato server |
| Componenti e tema | Material-UI | tutti gli stili dal tema centrale, nessun valore scritto a mano nei componenti |
| Stato condiviso | Jotai | atomi, niente Redux e niente Context per lo stato di dominio |
| Dati remoti | TanStack Query | interrogazioni e mutazioni con cache e ritentativi |
| Autenticazione e dati | Firebase Authentication e Firestore, piano Spark | nessun server proprio da mantenere |
| Distribuzione | Firebase Hosting | dominio fornito, certificato incluso, nessuna sospensione |
| Motore di calcolo | TypeScript nel browser, con vettori di riscontro generati dal motore Python | vedi la sezione dedicata, è il nodo vero |
| Esportazione | generazione del workbook su richiesta, dal generatore Python esistente | il ponte verso chi un file lo vuole ancora |

Lo stack coincide con quello di un altro progetto di questa macchina, `my-wedding-day`, e la coincidenza è un argomento a favore e non un caso: le convenzioni, le regole di sicurezza verificate con l'emulatore, la separazione fra sezioni, hook e tipi, e perfino gli errori già commessi e corretti là, sono conoscenza che si trasferisce invece di doversi ricomprare. La sola differenza consigliata è lo strumento di costruzione: là c'è Create React App, che non è più mantenuto, e qui conviene partire da Vite.

Due esclusioni vanno dichiarate perché sono le tentazioni naturali. Non si usa un framework con rendering lato server, perché introdurrebbe un server da tenere sveglio e riporterebbe dentro il problema che la scelta di Firebase elimina. Non si usa una libreria di componenti diversa da quella già conosciuta, perché il tempo che si guadagna scegliendo lo strumento migliore in astratto si perde tutto nel primo mese di apprendimento.

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

Ogni area segue lo stesso schema, mutuato dal progetto gemello: una sezione nell'interfaccia, un hook che parla con i dati, un tipo che ne descrive la forma. Il calcolo non vive nelle sezioni: vive nel modulo del motore, che riceve una descrizione dell'immobile e restituisce i risultati, esattamente come fa oggi la funzione Python.

## Dati e sicurezza

I dati vivono in Firestore, in collezioni separate per organizzazione, con le regole di sicurezza che leggono dai claim della sessione l'appartenenza e il ruolo. La verifica delle regole non si fa a occhio: si scrive una suite che gira contro l'emulatore e prova, per ciascun ruolo, sia ciò che deve essere permesso sia ciò che deve essere negato. È il pezzo che nel progetto gemello ha già pagato il proprio costo, e va replicato qui prima che ci siano dati veri dentro.

Tre cose non entrano nell'applicazione, e vanno decise ora e non dopo. Le fonti e i parametri normativi restano nel codice, versionati, perché sono conoscenza del progetto e non dato dell'utente. Le quotazioni OMI restano un'importazione manuale semestrale per la ragione di ADR-011, cioè l'autenticazione personale ai servizi telematici, e nell'applicazione diventano dati di riferimento caricati dal manutentore, non da ciascun utente. I documenti veri della trattativa, cioè visure, planimetrie e perizie, sono file: l'archiviazione di file su Firebase è la voce che va verificata prima di prometterla, perché la pagina ufficiale la dà disponibile sul piano gratuito mentre ricostruzioni di terzi affermano che dal 3 febbraio 2026 richieda il piano a consumo. Finché il punto non è chiarito, la prima versione dell'applicazione tratta i documenti come voci di una lista con il loro stato, senza custodirne il contenuto, che è peraltro ciò che il workbook fa oggi.

## Che fine fanno i cinque limiti dichiarati

Il passaggio non è un modo per aggirare i limiti: tre dei cinque si risolvono per costruzione, uno si risolve nel motore e va fatto comunque, uno resta.

La tabella di sensibilità sul prezzo, che oggi propaga l'incidenza dei costi accessori dello scenario base invece di ricalcolarla, è un limite del foglio: in un'applicazione ogni riga della tabella è una chiamata al motore, e l'approssimazione sparisce senza che nessuno debba scomporre nulla.

L'opzione prezzo-valore e la qualifica di lusso, che nel confronto fra immobili restano globali perché il foglio le prende da una cella sola, diventano attributi di ciascun immobile, che è la forma corretta e che il registro degli annunci già prevede per la prima casa e per il venditore impresa.

Il piano di ammortamento che si ferma a quarant'anni è un limite della lunghezza di una tabella di Excel. Nel motore l'ammortamento si calcola fino a chiusura, e il caso in cui un rialzo impedisce la chiusura si segnala come tale invece di essere troncato.

L'indipendenza delle variabili nella simulazione del rischio non era un limite di Excel ed era l'unico dei cinque che andava affrontato nel modello: è stato risolto il 4 settembre 2026, prima di aprire questo cantiere, con il fattore comune descritto in [`metodo-e-metriche.md`](metodo-e-metriche.md). La simulazione vive per intero nel workbook, perché il motore Python non ha una parte probabilistica, quindi la correzione è nelle formule del foglio e nelle estrazioni congelate. Quando il motore verrà portato in TypeScript la simulazione andrà scritta là per la prima volta, e il fattore comune è la specifica da riportare: un solo parametro leggibile come correlazione, pesi pari alla radice della correlazione e del suo complemento, e la riduzione esatta al caso indipendente quando il parametro è zero, che è la proprietà da mettere fra i vettori di riscontro.

La fornitura OMI che richiede un'autenticazione personale resta esattamente com'è, perché non dipende da noi.

## Il piano, in fasi con un criterio di chiusura ciascuna

La prima fase è il motore in TypeScript con il suo presidio: il generatore di vettori dal motore Python, la traduzione, e la suite che li verifica. È chiusa quando tutti i vettori passano e la differenza massima rispetto al riferimento sta sotto la soglia dichiarata. Non produce interfaccia, e va fatta per prima perché è la sola parte che, se sbagliata, invalida tutto il resto.

La seconda fase è lo scheletro autenticato: progetto Firebase, accesso, regole di sicurezza con la loro suite contro l'emulatore, e una sola pagina che mostra un immobile e i suoi numeri. È chiusa quando due account diversi non vedono i dati l'uno dell'altro e i test delle regole lo dimostrano.

La terza fase sono le sei aree, una per volta, ciascuna con la propria sezione, il proprio hook e i propri tipi.

La quarta fase è la migrazione dei dati esistenti, cioè il registro degli immobili e le verifiche comunali, e l'esportazione del workbook come ponte.

La quinta fase è la documentazione tecnico-didattica, che in questo progetto non è un adempimento finale ma il modo in cui le decisioni restano leggibili: ogni fase che introduce un pattern nuovo produce la propria voce nello studio didattico, con il codice reale prima e dopo e la ragione del salto.

## Che cosa va deciso o verificato prima di cominciare

Tre cose. Il vincolo di team in `CLAUDE.md` va riscritto, perché oggi vieta esattamente ciò che si sta per fare, e va riscritto dicendo che cosa può stare in rete e che cosa no, non cancellato. L'archiviazione dei file su piano gratuito va verificata sulla pagina ufficiale al momento in cui serve, e fino ad allora il piano non deve dipenderne. E va deciso se il workbook resta generabile: la risposta cambia se il generatore va mantenuto o se può essere archiviato, ed è la differenza fra dimezzare la manutenzione e non ridurla affatto.
