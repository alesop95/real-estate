# Wrangler, spiegato da zero

> Scheda tecnico-didattica sullo strumento a riga di comando con cui questo progetto parla con Cloudflare. Si legge la prima volta che si esegue un comando `wrangler`, e si rilegge quando un comando fa qualcosa di inatteso. Non dà per scontato niente: spiega che cos'è, che cosa succede a ogni passaggio, dove finiscono i file che produce, e che cosa ciascun comando fa davvero. La procedura operativa, cioè l'ordine in cui i comandi si eseguono per portare l'applicazione in rete, sta in [`messa-in-rete.md`](messa-in-rete.md); qui c'è il perché di ciascuno.

## Che cos'è, e perché non si fa tutto dal pannello

Cloudflare ha un pannello a video, cioè un sito su cui si clicca per creare un database, caricare un programma, configurare chi può entrare. Tutto ciò che facciamo con wrangler si potrebbe fare cliccando, e sarebbe la strada sbagliata per una ragione che questo progetto applica anche altrove: una configurazione fatta cliccando esiste in un posto solo, non lascia traccia nel repository, e non si può rifare su un altro account senza ricordarsela a memoria.

Wrangler è l'interfaccia a riga di comando[^1] di Cloudflare: un programma che si esegue nel terminale e che parla con l'account al posto nostro. La differenza pratica non è la velocità, è che ogni scelta atterra in un file di testo, cioè `app/wrangler.toml`, che è versionato insieme al codice. Chi clona questo repository su un altro computer e su un altro account ottiene la stessa applicazione eseguendo gli stessi comandi, senza doverne intervistare l'autore. È lo stesso principio per cui in questo progetto il workbook Excel si genera da codice invece di essere modificato a mano.

Wrangler fa tre famiglie di cose, e conviene tenerle distinte fin da subito. Crea e interroga risorse sull'account, per esempio un database. Esegue l'applicazione sulla propria macchina, simulando l'ambiente vero. E distribuisce l'applicazione, cioè la carica sull'account perché risponda a un indirizzo pubblico. Le prime due non toccano nulla di remoto quando si passa l'opzione che lo dice, e la distinzione fra locale e remoto è la cosa che più facilmente si sbaglia: la sezione apposita più sotto la tratta per esteso.

## Come lo eseguiamo, e perché non è installato nel sistema

Nel terminale i comandi cominciano tutti per `npx wrangler`, mai per `wrangler` e basta. Non è una formalità.

`npx` è un programma che arriva insieme a Node.js e che esegue un comando prendendolo dalle dipendenze del progetto in cui ci si trova. Wrangler, in questo repository, è dichiarato in `app/package.json` fra le dipendenze di sviluppo, a una versione precisa. Scrivendo `npx wrangler` si esegue quella versione lì; scrivendo `wrangler` si eseguirebbe quella eventualmente installata nel sistema, che potrebbe essere un'altra e comportarsi diversamente. Su uno strumento che distribuisce codice in esercizio, la differenza fra due versioni non è accademica.

Ne segue la regola pratica: i comandi si lanciano sempre dalla cartella `app/`, perché è lì che vive `package.json`, ed è lì che vive `wrangler.toml`. Da un'altra cartella wrangler non troverebbe né la propria versione né la configurazione.

```
cd E:\real-estate\app
npx wrangler whoami
```

La prima volta che si esegue un comando, `npx` può impiegare qualche secondo in più perché prepara il pacchetto; dalla seconda è immediato.

## La versione, e l'avviso che compare a ogni corsa

A ogni comando wrangler stampa un avviso che dice che la versione in uso è superata e invita ad aggiornare alla 4. La versione qui è fissata alla 3.99.0, e la fissazione è deliberata: una dipendenza che sceglie da sé quale versione usare è una dipendenza che un giorno cambia comportamento senza che nessuno l'abbia deciso.

L'avviso non è un errore e non impedisce nulla. L'aggiornamento alla versione maggiore successiva è un intervento a sé, che va fatto leggendo che cosa cambia e rieseguendo le prove, e non va mescolato a un lavoro che sta facendo altro. Finché non lo si fa, l'avviso si legge e si ignora consapevolmente, che è cosa diversa dall'ignorarlo per abitudine.

## L'accesso: che cosa è successo davvero in quei trenta secondi

Il comando `npx wrangler login` sembra fare una cosa sola e ne fa sei. Vale scomporle, perché conoscerle è la differenza fra fidarsi di un pulsante e sapere che cosa si sta autorizzando.

Primo, wrangler apre un piccolo server in ascolto sulla propria macchina, sulla porta 8976. Serve a ricevere la risposta finale, e vive solo per la durata dell'operazione. È la ragione per cui nell'indirizzo che il comando stampa compare `redirect_uri=http%3A%2F%2Flocalhost%3A8976%2Foauth%2Fcallback`: la risposta torna al proprio computer e non a un sito di terzi.

Secondo, wrangler genera due valori casuali. Uno si chiama `state` e serve a riconoscere la propria richiesta quando la risposta torna, così che una risposta fabbricata da qualcun altro non venga accettata. L'altro è un segreto di cui viene spedito soltanto il riassunto crittografico, che nell'indirizzo compare come `code_challenge` con `code_challenge_method=S256`: è il meccanismo chiamato PKCE[^2], e serve a che chi intercettasse il codice di autorizzazione non possa comunque trasformarlo in un token, perché gli mancherebbe il segreto originale.

Terzo, si apre il browser sulla pagina di Cloudflare che chiede l'autorizzazione, elencando i permessi. Quella pagina non è di wrangler: è di Cloudflare, e lo dichiara con la riga che dice che l'applicazione è posseduta e gestita da Cloudflare. Il consenso lo dà una persona, in un browser, su un sito che sa riconoscere.

Quarto, premuto il pulsante, Cloudflare rimanda il browser all'indirizzo locale del primo passaggio, portando con sé un codice di autorizzazione a uso singolo e lo `state` di prima. Wrangler verifica che lo `state` sia il proprio.

Quinto, wrangler scambia quel codice, insieme al segreto di cui aveva mandato solo il riassunto, con un token di accesso vero e con un token di rinnovo. Questo scambio non passa dal browser: è una chiamata diretta da wrangler a Cloudflare.

Sesto, i token finiscono in un file sul disco, e da quel momento ogni comando successivo li usa senza chiedere più niente. È questo che rende possibile, dai passi successivi, eseguire i comandi senza ripetere l'accesso.

Il messaggio finale, `Successfully logged in.`, significa che i sei passaggi sono andati tutti a buon fine. La pagina del browser che dice che l'autorizzazione è stata concessa si può chiudere.

## Dove vive il token, e che cosa contiene

Il file è questo, e su Windows sta sotto il profilo dell'utente.

```
C:\Users\<utente>\AppData\Roaming\xdg.config\.wrangler\config\default.toml
```

Il percorso contiene `xdg.config` perché wrangler usa una convenzione nata su sistemi di tipo Unix per decidere dove mettere la configurazione, e su Windows quella convenzione atterra lì. Non è un errore e non va spostato.

Dentro ci sono quattro campi. Il token di accesso, che è ciò con cui wrangler si presenta a Cloudflare a ogni comando. La data di scadenza, perché quel token dura poco. Il token di rinnovo, con cui wrangler ne ottiene uno nuovo quando il primo scade, senza riaprire il browser. E l'elenco dei permessi concessi, che serve a wrangler per dire subito che un comando non è autorizzato invece di scoprirlo dalla risposta del server.

Quel file è una credenziale personale e va trattato come una password: non si copia, non si incolla, non si mette in un repository, non si manda in chat. Se si sospetta che sia uscito, la reazione giusta è revocare l'autorizzazione dal pannello di Cloudflare, alla voce del proprio profilo che elenca le applicazioni collegate, e non limitarsi a cancellare il file: cancellarlo toglie l'accesso a questa macchina e lascia valido il token altrove.

Per uscire in modo ordinato esiste il comando dedicato, che revoca e ripulisce.

```
npx wrangler logout
```

## I quindici permessi, uno per uno

L'elenco che `whoami` stampa non è decorativo, ed è bene leggerlo perché è più largo di quanto questo progetto usi. Wrangler chiede un insieme fisso di permessi, uguale per chiunque lo usi, e non un insieme ritagliato sul singolo progetto.

Di lettura ce ne sono quattro. `user:read` serve a sapere chi sei, ed è ciò che alimenta `whoami`. `account:read` serve a sapere su quale account e su quale piano stai operando, ed è la ragione per cui wrangler può rifiutare un comando che il piano gratuito non consente prima ancora di provarci. `workers_tail:read` serve a leggere i registri di esecuzione di un'applicazione distribuita. `zone:read` riguarda i domini, e a noi non serve, perché usiamo l'indirizzo che Cloudflare assegna e non un dominio proprio.

Di scrittura ce ne sono undici, e quelle che questo progetto usa davvero sono tre. `workers:write` e `workers_scripts:write` servono a caricare l'applicazione. `d1:write` serve a creare il database, applicarvi le migrazioni ed eseguirvi interrogazioni.

Le altre otto sono nell'ambito e non vengono esercitate: `workers_kv:write` per un archivio chiave-valore che non usiamo, `workers_routes:write` per associare l'applicazione a un dominio proprio, `pages:write` per il prodotto gemello dedicato ai siti statici, `ssl_certs:write` per i certificati, e soprattutto `ai:write`, `queues:write` e `pipelines:write`, che riguardano tre prodotti fuori dal piano gratuito. C'è infine `offline_access`, che non è un permesso su una risorsa ma la facoltà di rinnovare il token senza riaprire il browser.

Su questi ultimi tre vale una precisazione che è il cuore della disciplina di questo progetto. Il fatto che il token possa creare una coda o un modello non significa che qualcosa si crei: significa che un comando dato per sbaglio non verrebbe fermato dai permessi. Ciò che ci protegge davvero sono due cose diverse e indipendenti. La prima è che sull'account non c'è un metodo di pagamento, quindi il superamento di un limite produce un rifiuto e non una fattura. La seconda è il presidio automatico in `app/test/limiti.test.ts`, che legge `wrangler.toml` e fallisce se vi compare la dichiarazione di un prodotto fuori dal piano gratuito. Un permesso ampio non è un pericolo se ciò che lo userebbe non esiste nella configurazione e non potrebbe entrarvi senza far fallire le prove.

## Le tre identità che non vanno confuse

In questo progetto circolano tre credenziali diverse. Confonderle è l'errore che costa di più, quindi conviene fissarle una volta.

Il token OAuth[^3] di wrangler è quello appena ottenuto. È personale, vive sulla macchina di chi sviluppa, ha un ambito largo, e serve a lavorare. Non entra mai nel repository e non si condivide.

Il token di interfaccia di programmazione, che arriverà più avanti nella procedura, è un'altra cosa: si crea a mano dal pannello, gli si assegnano i pochi permessi che servono e nessun altro, e vive fra i segreti del repository su GitHub perché lo usa il flusso automatico che distribuisce. È l'unico segreto vero dell'intera catena, ed è anche l'unico punto in cui i permessi li scegliamo noi uno per uno invece di accettare un insieme fisso.

Il token di Access è la terza cosa e non riguarda wrangler affatto: è quello che Cloudflare aggiunge a ogni richiesta di una persona che ha superato l'accesso all'applicazione, e che il Worker verifica in `app/src/server/identita.ts` per sapere chi sta chiamando. Non si crea, non si conserva, e dura quanto una richiesta.

## Locale contro remoto: due mondi con gli stessi comandi

Questa è la parte che più facilmente si sbaglia, perché i comandi si assomigliano e la differenza sta in una parola.

Con l'opzione `--local`, wrangler esegue tutto sulla propria macchina. Il database non è quello di Cloudflare ma un file SQLite[^4] dentro la cartella nascosta del progetto, e il programma non gira sui server di Cloudflare ma in un runtime chiamato workerd, che è lo stesso che Cloudflare esegue davvero, scaricato e avviato in locale. Non esce niente in rete, non si tocca niente dell'account, e si può sbagliare quanto si vuole.

```
app/.wrangler/state/v3/d1/miniflare-D1DatabaseObject/   il database locale
app/.wrangler/tmp/                                       i file temporanei di una corsa
```

Quella cartella è ignorata da git, e cancellarla non perde niente di importante: si ricrea applicando di nuovo le migrazioni. È anzi il modo più rapido di ripartire da un database pulito quando si è fatto disordine provando.

Con l'opzione `--remote`, lo stesso comando agisce sull'account vero. Un comando remoto che cancella una tabella cancella la tabella di un cliente, e non c'è un annulla. La regola che questo progetto si dà è di provare sempre prima in locale e di leggere due volte una riga di comando che contiene `--remote`.

Il comando `npx wrangler dev` è un caso a parte perché in questa versione è locale in modo predefinito: avvia l'applicazione sulla propria macchina, in ascolto su un indirizzo locale, con il database locale e le risorse statiche costruite. È il modo in cui si prova l'applicazione intera prima di distribuirla.

## Che cosa wrangler legge in `wrangler.toml`

Il file di configurazione è versionato e si legge dall'alto verso il basso come una dichiarazione di che cosa l'applicazione è.

Il campo `name` è il nome dell'applicazione sull'account, e diventa parte dell'indirizzo pubblico. Il campo `main` indica il file da cui parte il programma, cioè l'ingresso del Worker. Il campo `compatibility_date` fissa la data delle regole del runtime: è il modo in cui Cloudflare fa convivere programmi scritti in momenti diversi senza cambiare comportamento sotto ai piedi di nessuno, e in questo progetto è tenuta alla data che il runtime installato supporta davvero, perché chiederne una più avanti farebbe girare le prove su un runtime diverso da quello dichiarato. Il campo `compatibility_flags` accende singole funzionalità, e qui accende le interfacce di Node richieste dalla catena di prova.

La sezione `[vars]` porta le variabili non segrete, e la più importante è `MODALITA`: vale `esercizio` di predefinito, e in quella modalità l'applicazione non legge nemmeno l'intestazione di comodo con cui in sviluppo si dichiara la propria identità. Dimenticare quel valore rende l'applicazione prudente, non aperta.

La sezione `[[d1_databases]]` lega il database al nome con cui il codice lo raggiunge, che è `DB`. Il campo `database_id` oggi porta un segnaposto, e finché lo porta ogni comando remoto fallisce: è voluto, perché un comando che fallisce è meglio di un comando che scrive nel database sbagliato. Il flusso di distribuzione rifiuta di distribuire finché quel segnaposto è al suo posto.

La sezione `[assets]` dichiara la cartella delle risorse statiche dell'interfaccia, che Vite costruisce e che non si versiona. Porta anche la scelta di far arrivare al Worker tutto ciò che non corrisponde a un file, invece di far rispondere la pagina dell'applicazione: la ragione è scritta per esteso nel file stesso, e in breve è che l'impostazione comoda risponderebbe HTML anche a una chiamata all'interfaccia di programmazione.

## I comandi di questo progetto, uno per uno

Ciascuno di questi compare nella procedura di messa in rete, dove è collocato nel passo giusto. Qui c'è che cosa fa e che cosa si vede.

```
npx wrangler login
```

Autorizza la riga di comando con l'account, nel modo descritto sopra. Si esegue una volta per macchina. Non crea niente sull'account e non spende.

```
npx wrangler whoami
```

Dice con quale account si sta lavorando e con quali permessi. Stampa l'indirizzo di posta, una tabella con il nome dell'account e il suo identificativo, e l'elenco dei permessi. Non cambia niente: è il comando da eseguire quando si ha il dubbio di essere sull'account sbagliato, ed è un dubbio che conviene togliersi prima di un comando remoto e non dopo.

L'identificativo dell'account non è un segreto e non va conservato da nessuna parte: con l'accesso interattivo wrangler lo ricava da sé. La riga che lo dichiarerebbe esiste in `wrangler.toml` ed è commentata di proposito; si scommenta soltanto se un comando si lamenta di non sapere quale account usare, il che accade quando lo stesso accesso raggiunge più account.

```
npx wrangler d1 create valutazione-immobili
```

Crea il database sull'account e stampa un blocco di configurazione che contiene il suo identificativo. Quell'identificativo va riportato in `wrangler.toml` al posto del segnaposto. Il comando si esegue una volta sola: eseguirlo di nuovo creerebbe un secondo database con lo stesso nome e un identificativo diverso, che è il modo più semplice di ritrovarsi a scrivere in un database e a leggere dall'altro.

```
npx wrangler d1 migrations apply valutazione-immobili --local
npx wrangler d1 migrations apply valutazione-immobili --remote
```

Applica al database le migrazioni che stanno in `app/migrazioni/`, in ordine di nome, saltando quelle già applicate. Wrangler tiene il conto in una tabella di servizio dentro il database stesso, quindi il comando si può rieseguire senza danno: non riapplica ciò che c'è già. È la ragione per cui lo schema non si crea incollando comandi a mano, e per cui lo stesso schema si ricrea identico in locale, in esercizio e su un account nuovo.

```
npx wrangler d1 execute valutazione-immobili --local --command "SELECT ..."
```

Esegue un'interrogazione sul database. Con `--local` sul file di prova, con `--remote` su quello vero. È lo strumento con cui, nella procedura, si inserisce la prima riga che dichiara chi amministra la piattaforma: è l'unica scrittura a mano nella vita del sistema, e tutto il resto si fa dal pannello dell'applicazione.

```
npx wrangler dev
```

Avvia l'applicazione in locale. Stampa i legami che ha trovato, cioè il database e le variabili, e poi l'indirizzo su cui risponde. Resta in esecuzione finché non lo si ferma con Control più C. È il modo in cui si vede l'applicazione vera, con il Worker vero e le rotte vere, prima che esista qualunque cosa in rete.

```
npx wrangler deploy
```

Carica l'applicazione sull'account e la rende raggiungibile a un indirizzo pubblico. È l'unico comando di questo elenco che produce qualcosa di visibile da fuori. Nella procedura si esegue prima di configurare l'accesso, e non è un'imprudenza: serve a verificare in esercizio che senza configurazione di Access l'applicazione rifiuti tutti, che è una proprietà che in locale si prova con un test e in esercizio si prova soltanto così.

```
npx wrangler logout
```

Revoca l'autorizzazione e cancella i token dal disco. Si usa quando si smette di lavorare su quella macchina, o quando si vuole rientrare con un altro account.

## Diagnostica: gli errori che si incontrano

Se un comando dice che non sei autenticato, il token è scaduto e il rinnovo non è andato a buon fine: si riesegue `login`.

Se un comando remoto si lamenta dell'identificativo del database, il segnaposto in `wrangler.toml` non è ancora stato sostituito. È il comportamento voluto.

Se un comando si lamenta di non sapere quale account usare, l'accesso raggiunge più account: si esegue `whoami`, si prende l'identificativo giusto e si scommenta la riga `account_id` in `wrangler.toml`.

Se `dev` non parte lamentando che una porta è occupata, c'è un'altra corsa rimasta viva: si chiude quella, oppure si passa una porta diversa.

Se la pagina non compare e il Worker risponde che l'interfaccia non è costruita, manca la costruzione: si esegue prima `npm run costruisci` dentro `app/`.

Se le prove delle rotte non partono affatto, può mancare la cartella delle risorse statiche, che `wrangler.toml` dichiara: la ricrea lo script che gira prima delle prove, quindi in pratica succede solo eseguendo la suite in modi non previsti.

## Che cosa non facciamo con wrangler, e perché

Non creiamo code, archivi chiave-valore, bucket, modelli o pipeline, pur avendone il permesso. Non è prudenza generica: sono i prodotti che porterebbero fuori dal piano gratuito, e il presidio automatico che legge `wrangler.toml` fallirebbe se comparissero nella configurazione.

Non usiamo `wrangler secret` per conservare segreti dell'applicazione, perché oggi l'applicazione non ne ha: l'identità arriva da Access e il database è legato per configurazione, non per credenziale. Il giorno in cui servisse, quello è lo strumento giusto, e il segreto non andrebbe comunque in `wrangler.toml`.

Non distribuiamo a mano dal proprio computer se non la prima volta. Dal passo che accende il flusso automatico in poi, la distribuzione è una conseguenza di una spinta sul branch principale, e la ragione è che la versione in esercizio deve corrispondere sempre a un commit e non a quello che c'era sul disco di qualcuno.

[^1]: *CLI*, Command Line Interface - interfaccia a riga di comando, cioè un programma che si usa scrivendo comandi in un terminale invece di cliccare in una finestra.

[^2]: *PKCE*, Proof Key for Code Exchange - meccanismo che lega il codice di autorizzazione a un segreto generato da chi lo ha chiesto, così che intercettarlo non basti a ottenere un token.

[^3]: *OAuth* - protocollo con cui un programma ottiene il permesso di agire su un account senza conoscerne la password, e con cui quel permesso si può revocare in qualunque momento.

[^4]: *SQLite* - motore di database che conserva l'intero archivio in un solo file, senza un processo server separato. D1 è SQLite gestito da Cloudflare.
