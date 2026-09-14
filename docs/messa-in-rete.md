# Messa in rete, passo per passo

> Procedura operativa per portare l'applicazione dal disco al proprio indirizzo, e registro di ciò che è stato fatto. Ogni passo porta la ragione tecnologica per cui esiste, l'azione esatta da compiere, che cosa va riportato all'ambiente di sviluppo, e come si verifica che sia andato a buon fine. Si esegue una volta sola, dall'alto verso il basso, e non si salta un passo perché ciascuno presuppone il precedente. Lo stato di avanzamento è in fondo, e va aggiornato appena un passo si chiude.

## Come funziona questa procedura

Le azioni si dividono in due categorie e conviene tenerle distinte, perché la responsabilità è diversa. Le azioni sull'account sono dell'utente: creare l'account, autorizzare la riga di comando, configurare l'accesso, incollare un valore in un segreto del repository. Nessuna di queste può essere compiuta dall'ambiente di sviluppo, e non per una limitazione tecnica ma perché richiedono un'identità e una volontà che appartengono a una persona. Le azioni sul repository sono dell'ambiente di sviluppo: scrivere la configurazione, applicare le migrazioni, distribuire, verificare.

Per ogni passo, la forma è sempre la stessa: perché esiste, che cosa fare, che cosa riportare, come si verifica. E ogni passo chiuso lascia una riga nel registro in fondo a questo documento, con la data e l'esito, perché fra sei mesi la domanda non sarà come si fa ma che cosa era stato fatto.

Una regola attraversa tutta la procedura e non ha eccezioni: non si collega mai un metodo di pagamento all'account. È la sola cosa che rende la gratuità una proprietà del sistema invece di una promessa da sorvegliare, perché senza carta il superamento di un limite produce un errore e non una fattura. Chi arriva qui da [`architettura-web.md`](architettura-web.md) lo ha già letto; chi arriva da fuori lo legga due volte.

## Passo 1. L'account, e la verifica che non possa costare

Perché esiste. Tutto il resto vive dentro un account Cloudflare, e la scelta dell'account non è neutrale: un account che ha già un metodo di pagamento collegato, tipicamente perché vi è stato comprato un dominio, rende possibile per distrazione un abbonamento a pagamento. La verifica va fatta adesso, non dopo aver costruito sopra.

Che cosa fare. Se non esiste un account, registrarne uno su `dash.cloudflare.com/sign-up` con un indirizzo di posta che resterà raggiungibile: sarà l'indirizzo con cui si amministra il servizio e con cui arriveranno gli avvisi di superamento delle quote. La registrazione non chiede una carta, e non va aggiunta neppure quando l'interfaccia la propone. Se un account esiste già, entrare e guardare due cose: alla voce di fatturazione, se risulta un metodo di pagamento; e alla voce Workers, se il piano indicato è quello gratuito o quello a pagamento.

Che cosa riportare. Se l'account è nuovo, basta dirlo. Se è preesistente, riportare se ha un metodo di pagamento collegato e quale piano Workers risulta attivo, perché nel primo caso conviene valutare un account separato per questo progetto, e nel secondo la garanzia strutturale non c'è più e la scelta va rifatta con cognizione.

Come si verifica. Alla voce Workers del pannello il piano indicato è "Free". Nella sezione di fatturazione non compare alcun metodo di pagamento.

## Passo 2. Autorizzare la riga di comando

Perché esiste. Da qui in avanti si potrebbe fare tutto dal pannello a video, e sarebbe la strada sbagliata: ogni configurazione fatta cliccando esiste in un posto solo, non lascia traccia nel repository e non si può rifare su un altro account senza ricordarsela. Con la riga di comando, invece, la configurazione atterra in `app/wrangler.toml`, che è versionato, e la stessa applicazione si ricrea da zero altrove eseguendo gli stessi comandi. È lo stesso principio per cui in questo progetto il workbook si genera da codice invece di essere modificato a mano.

Che cosa fare. Dalla cartella `app/`, eseguire il comando di accesso. Si apre il browser, si conferma l'autorizzazione con l'account del passo uno, e la riga di comando conserva un token locale. Che cosa succeda esattamente in quei pochi secondi, dove finisca il token e che cosa significhi ciascuno dei quindici permessi che la pagina elenca, sta in [`wrangler.md`](wrangler.md), che è la scheda da leggere la prima volta che si esegue un comando di questo strumento.

```
npx wrangler login
```

Che cosa riportare. L'esito del comando di verifica seguente, che stampa l'account autorizzato.

```
npx wrangler whoami
```

Come si verifica. Il comando `whoami` mostra l'indirizzo di posta dell'account e l'identificativo dell'account stesso, che è la stringa esadecimale nella colonna "Account ID". Quell'identificativo serve al passo seguente.

## Passo 3. Creare il database

Perché esiste. D1 è il database dell'applicazione, e va creato prima di poterlo migrare. La creazione restituisce un identificativo che deve finire in `wrangler.toml`, dove oggi c'è un segnaposto: finché quel segnaposto è lì, ogni comando remoto fallisce, ed è voluto, perché un comando che fallisce è meglio di un comando che scrive nel database sbagliato.

Che cosa fare. Dalla cartella `app/`:

```
npx wrangler d1 create valutazione-immobili
```

Che cosa riportare. Il blocco che il comando stampa a video, che contiene il nome e l'identificativo del database. Non è un segreto: identifica un database che senza le credenziali dell'account nessuno può aprire.

Come si verifica. Il comando `npx wrangler d1 list` mostra il database appena creato.

## Passo 4. Applicare lo schema al database vero

Perché esiste. Lo schema esiste come migrazione versionata in `app/migrazioni/`, e le migrazioni si applicano, non si eseguono a mano: l'ordine e lo stato di applicazione li tiene il sistema, così che lo stesso schema si possa ricreare identico in locale, in esercizio e su un account nuovo. Applicare uno schema incollando comandi a video è il modo di ottenere due database che divergono senza sapere quando.

Che cosa fare. Prima in locale, che non tocca niente di remoto, poi in remoto.

```
npx wrangler d1 migrations apply valutazione-immobili --local
npx wrangler d1 migrations apply valutazione-immobili --remote
```

Che cosa riportare. L'elenco delle migrazioni applicate che il comando stampa.

Come si verifica. Il comando seguente elenca le tabelle del database remoto, e devono essere tre più quella di servizio delle migrazioni.

```
npx wrangler d1 execute valutazione-immobili --remote --command "SELECT name FROM sqlite_master WHERE type='table'"
```

## Passo 5. La prima distribuzione, che deve rispondere di no a tutti

Perché esiste. Distribuire prima di configurare l'accesso sembra pericoloso e non lo è, e la ragione è una proprietà del codice che vale verificare invece di assumere: la funzione che stabilisce l'identità restituisce "nessuno" quando la configurazione di Access è vuota, e ogni rotta protetta risponde quattrocentouno a chi non ha un'identità. Una distribuzione fatta adesso è quindi un'applicazione raggiungibile che non concede niente a nessuno, ed è il modo migliore di provare che il rifiuto predefinito funziona davvero, cosa che in locale si prova con un test e in esercizio si prova soltanto così.

Che cosa fare. Dalla cartella `app/`:

```
npx wrangler deploy
```

Che cosa riportare. L'indirizzo che il comando stampa alla fine, nella forma `valutazione-immobili.<sottodominio>.workers.dev`.

Come si verifica. Aprendo quell'indirizzo seguito da `/api/io` si ottiene una risposta di rifiuto, con codice quattrocentouno e il messaggio "non autenticato". Se si ottiene qualunque altra cosa, e in particolare se si ottengono dati, la procedura si ferma qui e il codice va guardato prima di andare avanti.

## Passo 6. Zero Trust, cioè chi può entrare

Perché esiste. È il pezzo che sostituisce un sistema di credenziali scritto da noi, e la ragione per cui non lo scriviamo è che l'autenticazione è la parte in cui un errore non si vede e costa tutto. Access identifica la persona con un codice monouso spedito alla sua posta, oppure con un fornitore di identità esterno, e consegna all'applicazione un token firmato che dice chi è. Fino a cinquanta persone è gratuito, e cinquanta persone sono più di quante ne avrà questo strumento prima di essere un prodotto vero.

Che cosa fare. Nel pannello, alla sezione Zero Trust, completare la creazione dell'organizzazione scegliendo un nome di squadra: diventerà parte dell'indirizzo di accesso, quindi conviene un nome breve e stabile. Come metodo di accesso lasciare o attivare il codice monouso via posta, che non richiede alcun fornitore esterno. Poi, alla voce delle applicazioni di Access, aggiungere un'applicazione autoospitata che protegge l'indirizzo del passo cinque, e darle una politica che consente l'ingresso a un elenco di indirizzi di posta: per ora il proprio.

Che cosa riportare. Tre cose: il nome della squadra scelto, l'etichetta del destinatario dell'applicazione, che il pannello chiama Application Audience e che è una stringa esadecimale lunga, e l'elenco degli indirizzi ammessi.

Come si verifica. Aprendo l'indirizzo dell'applicazione in una finestra anonima si viene fermati da una pagina di accesso, non dall'applicazione.

## Passo 7. Dire all'applicazione chi è la sua guardia

Perché esiste. L'applicazione verifica il token di Access solo se sa da quale organizzazione aspettarselo e per quale destinatario è stato emesso. Senza quei due valori la verifica non si tenta e l'identità resta nessuno, che è il comportamento prudente del passo cinque ma non è quello utile. Il controllo sul destinatario, in particolare, è la difesa contro un token valido emesso per un'altra applicazione della stessa organizzazione.

Che cosa fare. Riportare in `app/wrangler.toml` il nome della squadra e l'etichetta del destinatario, che non sono segreti, e distribuire di nuovo. Questa è un'azione dell'ambiente di sviluppo, non dell'utente.

Come si verifica. Dopo l'accesso da Access, l'indirizzo seguito da `/api/io` risponde con il proprio indirizzo di posta e un elenco vuoto di organizzazioni. L'elenco vuoto è corretto: l'identità esiste, l'appartenenza no.

## Passo 8. Il primo superamministratore, e tutto il resto dal pannello

Perché esiste. Un utente autenticato che non appartiene a nessuna organizzazione entra e non vede niente, per costruzione. Qualcuno deve quindi creare la prima organizzazione, e quel qualcuno non può essere una rotta aperta a chiunque entri, perché sarebbe una scrittura che il primo arrivato userebbe per fabbricarsi un'organizzazione. Fino al 14 settembre 2026 la risposta era inserire a mano nel database l'organizzazione e la sua prima appartenenza; dal 14 settembre esistono il livello di piattaforma e il pannello che lo usa, quindi la scrittura a mano si riduce a una sola riga, una volta sola nella vita del sistema: quella che dice chi amministra la piattaforma.

Il perimetro di quel livello va conosciuto prima di attribuirlo, ed è ADR-029: un superamministratore crea e rimuove organizzazioni e ne nomina il primo amministratore, e non vede gli immobili di nessuna organizzazione di cui non sia membro. Se vuole vederli deve aggiungersi fra i suoi membri, e quell'aggiunta lascia una riga. Non è impossibilità, è tracciabilità, e la differenza va detta al cliente per intero.

Che cosa fare. È un'azione dell'ambiente di sviluppo, ed è un inserimento solo. L'indirizzo di posta è quello ammesso nella politica del passo sei, e deve coincidere carattere per carattere con quello che Access consegna, perché il livello è per posta elettronica e non per identificativo utente; l'applicazione normalizza in minuscolo ciò che scrive lei, quindi anche qui si scrive in minuscolo.

```
npx wrangler d1 execute valutazione-immobili --remote --command "INSERT INTO gestori (email, livello, aggiunto_il) VALUES ('la-propria-posta@esempio.it', 'superamministratore', datetime('now'))"
```

Da qui in avanti non si scrive più nel database a mano. Si apre l'indirizzo dell'applicazione, si va alla voce Amministrazione, e nel pannello delle organizzazioni si crea la prima: identificativo, nome e primo amministratore, che è obbligatorio. Le due scritture, cioè l'organizzazione e la sua prima appartenenza, partono insieme in un lotto, perché un'organizzazione creata senza amministratore sarebbe un'organizzazione che nessuno può amministrare, e ripararla richiederebbe di nuovo una scrittura a mano.

Il ruolo del primo amministratore è amministratore e non membro, ed è una scelta e non una comodità: dei tre ruoli è il solo che può eliminare un immobile e cambiare chi fa parte dell'organizzazione, quindi la prima persona che entra deve averlo, altrimenti non esisterebbe nessuno in grado di disfare un proprio errore. Un'organizzazione non può nemmeno restare senza amministratori dopo: revocare o retrocedere l'ultimo viene rifiutato con un messaggio che dice di nominarne un altro prima.

Come si verifica. L'indirizzo seguito da `/api/io` risponde con il proprio indirizzo di posta e il livello `superamministratore`, e con un elenco di organizzazioni vuoto finché non ce se ne aggiunge a una: l'elenco vuoto accanto al livello pieno è la prova che le due cose sono separate davvero. Creata la prima organizzazione dal pannello, la rotta dei suoi immobili risponde con un elenco vuoto invece che con un rifiuto a chi ne è stato nominato amministratore.

## Passo 9. La distribuzione automatica dal repository

Perché esiste. Distribuire a mano funziona finché lo fa la stessa persona dalla stessa macchina, e smette di funzionare esattamente quando serve. Con un token di interfaccia conservato fra i segreti del repository, la distribuzione diventa una conseguenza di una spinta sul branch, ed è anche una difesa: la versione in esercizio corrisponde sempre a un commit, e non a quello che c'era sul disco di qualcuno.

Il flusso di lavoro esiste già e sta in `.github/workflows/distribuzione.yml`, quindi questo passo non scrive codice: consegna al flusso la sola cosa che gli manca, cioè il permesso di parlare all'account. È in due lavori con un vincolo fra loro, e il vincolo è la parte che conta: le prove girano su ogni spinta e su ogni richiesta di modifica, senza alcun segreto, perché motore, rotte e identità si provano dentro il runtime di Cloudflare con un D1 locale; la distribuzione parte solo dopo che le prove sono passate, solo dal branch `main` o da un avvio manuale, e mai da una richiesta di modifica. Applica le migrazioni prima di distribuire, e non dopo, perché uno schema vecchio sotto codice nuovo rompe alla prima richiesta mentre uno schema nuovo sotto codice vecchio di norma non rompe niente. Include anche il controllo che i vettori di riscontro non siano scaduti, che è il presidio della doppia implementazione: se fallisce, le prove hanno confrontato il motore TypeScript con un modello Python che nel frattempo è cambiato.

Che cosa fare. Nel pannello, alla voce dei token di interfaccia del proprio profilo, creare un token con il solo permesso di modificare gli script dei Workers e di leggere il proprio account, aggiungendo il permesso di scrittura su D1 perché il flusso applica anche le migrazioni. Conservarlo poi fra i segreti del repository su GitHub, alla voce delle azioni, con il nome esatto `CLOUDFLARE_API_TOKEN`, che è quello che il flusso legge. Il token è l'unico segreto vero di tutta la procedura: non finisce in nessun file del repository, non si incolla in chat, e se si sospetta che sia uscito si revoca dal pannello invece di cambiargli i permessi.

Come si verifica. Un avvio manuale del flusso, dalla scheda delle azioni del repository, arriva in fondo a entrambi i lavori, e l'indirizzo del passo cinque risponde con la versione nuova. Da lì in avanti ogni spinta su `main` fa lo stesso da sé.

## Registro delle azioni

Una riga per passo, con la data e l'esito. Si aggiorna appena un passo si chiude, e resta come storia: quando fra sei mesi qualcosa non tornerà, la domanda sarà che cosa era stato fatto, non come si fa.

| Passo | Stato | Data | Esito e valori |
|---|---|---|---|
| 1. Account senza metodo di pagamento | fatto | 2026-09-14 | Account nuovo, creato con una registrazione ordinaria. Nessun metodo di pagamento collegato, e nessuno da scollegare: la gratuità è quindi una proprietà dell'account e non una promessa da sorvegliare. |
| 2. Riga di comando autorizzata | fatto | 2026-09-14 | Accesso OAuth concesso dal browser e token salvato nel profilo utente della macchina di sviluppo. `whoami` conferma l'account della registrazione del passo 1, con i quindici permessi predefiniti di Wrangler. L'identificativo dell'account non è trascritto qui perché il repository è pubblico e perché non serve: con l'accesso interattivo wrangler lo ricava da sé, e la riga che lo dichiarerebbe in `app/wrangler.toml` resta commentata. |
| 3. Database creato | da fare | | |
| 4. Schema applicato in locale e in remoto | da fare | | |
| 5. Prima distribuzione, rifiuto predefinito verificato | da fare | | |
| 6. Zero Trust e politica di accesso | da fare | | |
| 7. Applicazione configurata con squadra e destinatario | da fare | | |
| 8. Primo superamministratore, e prima organizzazione dal pannello | da fare | | |
| 9. Distribuzione automatica dal repository | da fare | | |

## Dove finiscono i valori

I valori che questa procedura produce si dividono in tre destinazioni, e la divisione non è formale.

Vanno in `app/wrangler.toml`, che è versionato, l'identificativo del database, il nome della squadra e l'etichetta del destinatario di Access: non sono segreti, sono configurazione, e stanno nel repository perché servono a chiunque debba ricostruire l'applicazione.

Vanno in `app/.dev.vars`, che non è versionato, le variabili dello sviluppo locale, prima di tutto la modalità: è il file che dice all'applicazione in esecuzione sulla propria macchina di accettare l'identità dall'intestazione di comodo invece che da un token. Il modello si chiama `app/.dev.vars.example` ed è versionato.

Vanno fra i segreti del repository su GitHub, e in nessun altro posto, il token di interfaccia della distribuzione. Non in un file, non in una nota, non in chat.

Non va da nessuna parte, e vale dirlo perché è la domanda che si fa, l'identificativo dell'account: con l'accesso interattivo del passo due, o con un token che raggiunge un solo account, wrangler lo ricava da sé. La riga che lo dichiarerebbe esiste in `app/wrangler.toml` commentata, e si scompone soltanto se un comando si lamenta di non sapere quale account usare.
