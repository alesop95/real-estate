# Raccolta degli annunci e acquisizione dei dati

> Scheda operativa. Descrive come si tiene il registro degli immobili in valutazione, come si arricchisce e quali sono i limiti che l'acquisizione automatica deve rispettare. L'implementazione è in `src/immobiliare/annunci.py` e `src/immobiliare/omi.py`, l'interfaccia in `tools/valuta.py`.

## Che cosa tiene il registro

Il registro è un archivio CSV in `data/annunci.csv`, una riga per immobile, che sopravvive alla rigenerazione del workbook e non dipende da Excel. Ogni riga porta l'identificativo, lo stato di avanzamento, il link all'annuncio, i dati fisici ed economici dell'immobile, la quotazione OMI della zona e il canone atteso. Tre grandezze non si scrivono e si calcolano da sole nel foglio Annunci del workbook: il prezzo al metro quadro, lo scarto rispetto alla quotazione OMI della zona e il rendimento lordo.

Quattro campi meritano una nota perché rispondono a domande che si pongono presto e che i dati puramente economici non catturano. L'agenzia e il contatto sono il riferimento con cui si sta trattando, inseriti a mano: non provengono dal prelievo automatico, che per scelta non estrae recapiti, e la differenza fra annotare un recapito ricevuto e raccoglierne a strascico è esattamente la differenza fra un'agenda e una banca dati. La destinazione d'uso, cioè la classificazione ministeriale, dice se l'immobile è accatastato come abitazione oppure no: un monolocale accatastato a ufficio non è un'abitazione, cambia le imposte, la possibilità di prendervi la residenza e quella di locarlo a uso abitativo, e il cambio di destinazione ha un costo che va messo nel prezzo. La data di consegna serve alle nuove costruzioni, dove il tempo fra proposta e disponibilità è esso stesso un costo.

L'ordine delle colonne del foglio Annunci è un contratto fra due file, perché l'esportazione scrive per posizione e non per nome. Un test dedicato lo verifica, insieme al fatto che le tre colonne di formula non vengano mai sovrascritte: è proprio quel test ad aver scoperto che la scorciatoia con cui si assegnava il valore a una cella saltava l'assegnazione quando il valore era nullo, lasciando in cella il dato dell'annuncio che occupava prima quella riga.

Il registro alimenta poi il foglio Confronto immobili, che applica a ogni riga lo stesso modello del resto del workbook, dalle imposte di trasferimento al cash flow, e restituisce una tabella in cui gli annunci si leggono in fila con rendimento netto, cap rate, cash on cash e debt service coverage ratio affiancati. Serve a scegliere quale immobile approfondire, non a decidere.

Il regime di acquisto si dichiara per riga, ed è la ragione delle due colonne in coda al registro. `prima_casa` dice se quell'immobile è prima casa per chi compra, che non è una caratteristica dell'immobile ma della posizione dell'acquirente rispetto a esso, e cambia da riga a riga tipicamente fra un immobile nel Comune di residenza e uno fuori. `venditore_impresa` dice se la vendita è soggetta a IVA invece che a imposta di registro, e questo è il salto più grosso fra due righe della stessa lista: sullo stesso prezzo l'IVA si applica per intero, mentre il registro con il prezzo-valore si applica al valore catastale, che di norma è una frazione. Confrontare un usato da privato e un nuovo da costruttore senza questa distinzione produce una graduatoria sbagliata nel verso peggiore, perché fa sembrare più conveniente proprio l'immobile che porta l'imposta più alta.

Entrambi i campi hanno tre stati e non due. SI e NO dichiarano il regime della riga; il vuoto significa eredita dal foglio Immobile, quindi un registro compilato senza toccare quelle colonne si comporta esattamente come prima che esistessero. Nel foglio di confronto il regime effettivamente applicato è visibile nelle due colonne \"Prima casa\" e \"Da impresa\", che sono anche le celle che le formule delle imposte e dei costi accessori leggono: una graduatoria in cui una riga paga l'IVA e un'altra il registro va letta sapendolo, non scoprendolo. Restano invece globali, presi dal foglio Immobile, l'opzione prezzo-valore e la qualifica di immobile di lusso.

I valori dei campi a tre stati si normalizzano in ingresso: `si`, `s`, `yes`, `true`, `vero` e `1` diventano SI, i corrispondenti negativi diventano NO, il vuoto resta vuoto e quello che non è riconosciuto resta scritto com'è. Serve al percorso di importazione col modello locale, che a una domanda booleana risponde volentieri `true`: senza normalizzazione il foglio lo leggerebbe come diverso da SI, cioè come un NO, e non lo segnalerebbe.

Lo stesso foglio porta in coda un blocco di quattro colonne dedicate all'Osservatorio: la zona OMI dell'immobile, la quotazione minima e la massima di quella zona, e lo scarto del prezzo al metro quadro rispetto alla loro media. Le prime tre arrivano dal registro, dove le scrive `omi cerca`; la quarta è calcolata sul foglio di confronto e non letta dal registro, e la ragione è che i due scarti non rispondono alla stessa domanda. Quello del foglio Annunci confronta la quotazione di zona con il prezzo richiesto, cioè misura quanto è caro l'annuncio; quello del foglio Confronto immobili la confronta con il prezzo che il modello sta usando in quella riga, cioè l'obiettivo quando è compilato, e misura quanto sarebbe caro l'acquisto alle condizioni che si sta cercando di ottenere. Leggere il primo dentro il secondo foglio avrebbe messo in riga un unico numero riferito a un prezzo diverso da quello di tutte le altre colonne, ed è un'incoerenza che nessuna cella avrebbe segnalato.

Sulla lettura dello scarto vale un'avvertenza che il numero da solo non porta. La quotazione OMI è un intervallo medio per zona omogenea e tipologia, non una stima dell'immobile: ignora stato di conservazione, piano, affaccio, classe energetica e lavori deliberati in condominio, e quando nel registro la zona è vuota le due quotazioni sono quelle dell'intero Comune, quindi un intervallo largo su cui lo scarto dice molto poco. È un segnalatore di righe da capire, non un criterio di ordinamento.

Lo scarto rispetto alla quotazione OMI è la colonna che fa il lavoro. Un prezzo al metro quadro va letto solo contro il mercato della sua zona, e la quotazione dell'Osservatorio è l'unico riferimento pubblico, gratuito e verificabile disponibile: la formattazione a scala di colore rende immediato vedere quali annunci stanno sopra il mercato di zona e quali sotto. Il rendimento lordo, ordinato in modo decrescente dall'elenco a riga di comando, serve invece a scremare in fretta una lista lunga prima di dedicare tempo a una valutazione completa.

Il riversamento nel workbook è idempotente: riscrive le colonne di dato lasciando intatte le tre colonne di formula, e ripulisce le righe residue di un'esportazione precedente più lunga. Si può quindi rigenerare quante volte si vuole senza accumulare sporcizia.

## Tre modi di popolarlo, in ordine di preferenza

Il primo è l'inserimento manuale con il sottocomando che aggiunge una riga. Non tocca nessun sito, non ha dipendenze, e per un numero di immobili nell'ordine delle decine è semplicemente il modo più rapido.

Il secondo è l'incolla del testo. Si apre l'annuncio nel browser, si copia il testo in un file e lo si passa al programma, che lo struttura con un modello linguistico in esecuzione sulla rete locale. Il contenuto non lascia la macchina: la richiesta va all'istanza Ollama configurata, e questa è la ragione principale per cui questa strada è preferita a un servizio in cloud. Il modello estrae Comune, indirizzo, tipologia, superficie, prezzo, piano, classe energetica e spese condominiali, con l'istruzione esplicita di non inventare i dati mancanti e di non riportare nomi, numeri di telefono o indirizzi email.

Il terzo è il prelievo diretto della pagina, ed è quello su cui il progetto prende una posizione restrittiva, per le ragioni della sezione seguente.

## I limiti dell'acquisizione automatica, e perché sono scritti nel codice

Il prelievo automatico di pagine da portali di annunci tocca tre corpi normativi distinti, e il fatto che i dati siano visibili pubblicamente non risolve nessuno dei tre.

Il primo è contrattuale: i termini di servizio dei portali disciplinano l'uso automatizzato, e il file `robots.txt` esprime in forma leggibile da una macchina quali percorsi il gestore intende escludere. Il modulo lo legge e lo rispetta senza eccezioni, per ogni singolo URL e non una volta per dominio, perché un portale può consentire le pagine di dettaglio ed escludere le pagine di ricerca. Se il `robots.txt` non è raggiungibile la risposta è negativa: in assenza di un permesso esplicito il comportamento prudente è astenersi, non presumere.

Il secondo è il diritto sui generis del costitutore di banca dati, che tutela l'investimento nella raccolta e organizzazione dei dati e che colpisce l'estrazione o il reimpiego di una parte sostanziale del contenuto. È la ragione per cui la raccolta qui è puntuale e finalizzata a una decisione di acquisto personale, e non un'estrazione sistematica di interi cataloghi.

Il terzo è la protezione dei dati personali. I recapiti dei venditori privati e degli agenti sono dati personali, e la loro raccolta massiva richiederebbe una base giuridica che qui non esiste. Il modulo quindi non li raccoglie e istruisce esplicitamente il modello locale a non estrarli.

Ne discendono i vincoli tecnici che il codice impone da sé: una richiesta ogni cinque secondi per dominio, uno user agent che dichiara chi è e a che scopo, nessuna rotazione di identità, nessun aggiramento di protezioni anti bot. Su quest'ultimo punto la posizione è netta: se un sito risponde con un blocco, la risposta corretta è fermarsi, non travestirsi. Quando il prelievo non è consentito il programma non fallisce silenziosamente ma spiega le due vie alternative, l'incolla del testo e l'inserimento manuale, che restano sempre praticabili e sempre lecite.

## Le quotazioni OMI

Le quotazioni dell'Osservatorio del mercato immobiliare danno, per ogni zona omogenea di ogni Comune e per ogni tipologia edilizia, l'intervallo di prezzo al metro quadro di compravendita e di locazione, aggiornato semestralmente. Sono la base con cui il registro ancora i prezzi a un riferimento indipendente.

Sulle vie di accesso occorre essere precisi, perché cambiano il modo di usare il modulo. La fornitura ufficiale e aggiornata passa dall'area riservata di Fisconline o Entratel: è gratuita ma richiede un'autenticazione personale che uno script non può e non deve simulare, quindi il file va scaricato a mano una volta a semestre e passato al programma. Il mirror open data mantenuto da ondata, che il modulo sa scaricare da solo, ripubblica la stessa fonte ma si ferma al secondo semestre 2018: serve per ricostruire l'andamento storico di una zona, non per il prezzo di oggi, e il programma lo ricorda a ogni interrogazione. La consultazione puntuale a video sul servizio geopoi dell'Agenzia, infine, resta sempre disponibile senza registrazione ed è la via più rapida per una singola zona.

Il modulo riconosce da solo il formato del file, perché il mirror usa la virgola come separatore con l'intestazione sulla prima riga mentre la fornitura ufficiale usa il punto e virgola e antepone una riga di metadati, e i numeri hanno la virgola decimale in entrambi i casi. Riconosce anche la codifica, che è l'insidia meno visibile: il mirror pubblica già in UTF-8, la fornitura ufficiale arriva nella codifica ANSI di Windows, e leggerla come UTF-8 non solleva errori ma sostituisce ogni accento con un segnaposto, rendendo irreperibile alla ricerca per nome proprio il Comune che si sta cercando.

### Il giro semestrale, cinque minuti

La fornitura si scarica due volte l'anno e la procedura è sempre la stessa. Si accede ai servizi telematici dell'Agenzia con SPID o CIE, si entra nell'area riservata alla voce dei servizi ipotecari e catastali e dell'Osservatorio del mercato immobiliare, si sceglie Forniture dati OMI e poi Quotazioni immobiliari, si indicano semestre e ambito territoriale e si scarica il prodotto. L'archivio ottenuto si passa al programma senza estrarlo. Sull'ambito conviene ragionare una volta sola: la fornitura si chiede per Comune, provincia, area metropolitana, regione o intero territorio nazionale, e un raggio di ricerca realistico attraversa quasi sempre più province, perché quaranta chilometri da un capoluogo di costa ne toccano tre o quattro. Scaricare l'intera regione costa un solo giro e un solo file, e il programma filtra per Comune a costo nullo: il file nazionale del mirror porta centosessantunomila quotazioni su quasi ottomila Comuni e si interroga in un istante.

```
python tools/valuta.py omi importa --file "<percorso dello zip scaricato>" --regione "<Regione>"
python tools/valuta.py omi cerca --comune "<Comune>"
```

Il primo comando normalizza i CSV nella cartella di cache, che non è versionata; il secondo serve a verificare che siano entrati davvero, ed è il controllo da fare subito perché un ambito territoriale sbagliato produce un archivio valido che però non contiene il Comune di interesse. Se in cache finiscono più file, per esempio una provincia per volta, vengono letti tutti quelli del semestre più recente e i periodi superati restano fuori: mescolarli falserebbe il confronto, e leggerne uno solo, come faceva la prima versione, faceva concludere che un Comune non fosse coperto quando semplicemente stava nell'altro file. Le finestre utili sono la primavera per il secondo semestre dell'anno precedente e l'autunno per il primo semestre dell'anno in corso.

Oltre agli intervalli di prezzo, il modulo espone per ogni zona il rendimento lordo implicito, cioè il canone annuo di zona rapportato al prezzo di zona. È il metro di paragone più onesto per un singolo annuncio: se un immobile promette molto più della sua zona, o è un affare o c'è qualcosa che non si è capito, e la seconda ipotesi va esclusa prima di credere alla prima.

## Il riconoscimento dei duplicati

Lo stesso immobile ricompare spesso su portali diversi, con testo riscritto, foto diverse e prezzo leggermente diverso. Il confronto sul link non lo intercetta, perché i link sono per costruzione diversi. Il registro fa due cose: normalizza il link togliendo i parametri di tracciamento, così che lo stesso annuncio ripescato da una condivisione non entri due volte, e mette a disposizione il calcolo di un vettore semantico tramite il modello di embedding locale, con cui confrontare le descrizioni e far emergere le riproposizioni della stessa unità sotto altra veste.

## Dall'annuncio alla decisione, i tre percorsi

Ci sono tre modi di far entrare un immobile nel modello, e si scelgono in base a quanto si sa e a quanto il portale collabora. Portano tutti allo stesso punto, cioè una riga del registro completa abbastanza da reggere il confronto.

### Primo percorso: inserimento manuale

È il più veloce quando i dati si hanno già sotto gli occhi, ed è l'unico che funziona sempre, perché non dipende da nessuno.

```
python tools/valuta.py annunci aggiungi --link "<url>" --comune "Civitanova Marche" --provincia MC --mq 75 --prezzo 89000 --canone 550 --punteggio 8
```

Nessuna opzione è obbligatoria oltre a quelle che si vogliono valorizzare, e un annuncio può entrare anche con il solo link, da completare dopo. I campi che contano davvero, in ordine, sono il prezzo, i metri quadri, il Comune, la rendita catastale e il canone: i primi tre bastano per il confronto fra immobili, la rendita sblocca il prezzo-valore e il canone accende il calcolo del rendimento.

Per correggere o completare in seguito, senza rifare la riga:

```
python tools/valuta.py annunci modifica --id house_4 --prezzo 87000 --zona C3 --stato "in trattativa" --punteggio 10
```

### Secondo percorso: incolla del testo, strutturato dal modello locale

È quello da usare quando l'annuncio è lungo e i dati sono sparsi nella descrizione. Si apre la pagina nel browser, si seleziona il contenuto dell'annuncio compresa la tabella delle caratteristiche, lo si incolla in un file di testo, e si lascia fare al modello.

```
$env:OLLAMA_HOST = "http://<host del modello>:<porta>"
python tools/valuta.py annunci importa --file "C:\percorso\annuncio.txt" --link "<url>"
```

Circa venti secondi per annuncio. Va inclusa la sezione delle caratteristiche, quella tabellare, e non solo il testo descrittivo: è lì che stanno spese condominiali, classe energetica e, quando ci sono, rendita e categoria catastale. Il testo non lascia la rete locale.

Va poi riletto quello che il modello ha estratto, con `annunci elenca`, prima di fidarsene. Non perché sbagli spesso, ma perché quando sbaglia lo fa in silenzio.

### Terzo percorso: prelievo diretto della pagina

Esiste, è subordinato al `robots.txt` e nella pratica funziona di rado, perché i portali maggiori consentono il percorso e poi rispondono comunque con un blocco a chi non è un browser. Quando succede, il programma lo dice e indica le due vie sopra invece di insistere.

```
python tools/valuta.py annunci importa --link "<url>"
```

## Una volta che gli immobili sono a registro

L'ordine è questo, e ogni passo serve al successivo.

```
python tools/valuta.py annunci omi          aggancia le quotazioni della zona a ogni annuncio
python tools/valuta.py annunci confronta    graduatoria per scarto sulla zona, con le segnalazioni
python tools/valuta.py annunci elenca       controlla che i dati siano quelli giusti
python tools/valuta.py excel --con-annunci  genera il workbook con il registro dentro
```

Il comando `annunci confronta` da' la stessa graduatoria a video, ordinata per scarto sulla quotazione di zona e non per prezzo, perché fra immobili di taglia diversa il prezzo non dice nulla. Accanto a ogni riga espone il canone che la zona paga per quella superficie, ricavato dalle quotazioni OMI di locazione e non dall'annuncio, e una colonna di segnalazioni ricavata dalle note: immobile già locato, da ristrutturare, zona assegnata per ipotesi, dati incoerenti nell'annuncio, rendita catastale mancante. È un'euristica su testo libero e va letta per quello che è, cioè un promemoria per non perdere di vista un vincolo mentre si guarda una tabella di numeri.

Nel workbook si apre il foglio Confronto immobili, che applica il modello completo a ogni riga e mette in fila rendimento netto, cap rate, cash on cash e debt service coverage ratio. Da lì esce il candidato su cui vale la pena spendere un'ora, e per quello si compila il foglio Immobile con i dati reali.

Sull'aggancio delle quotazioni vale un'avvertenza. Senza la zona OMI indicata nel registro, il riferimento è l'intero Comune, e su un Comune di costa la forbice mette insieme il lungomare e le zone agricole: il numero è corretto e quasi inutile. La zona si trova con `omi zone --comune "..."` incrociando l'indirizzo, si scrive nel registro con `annunci modifica --zona`, e da quel momento lo scarto diventa un numero su cui trattare.

## Se l'immobile viene da un'asta

Il percorso cambia in due punti. Nel registro si marcano i campi dedicati:

```
python tools/valuta.py annunci modifica --id house_4 --note "asta, tribunale di Macerata"
```

e si compilano a mano nel foglio Annunci le colonne dell'asta, cioè base d'asta, data, tribunale e procedura, e soprattutto lo stato di occupazione. Poi si lavora nel foglio Asta, non nel foglio Immobile: le imposte si calcolano allo stesso modo, ma il costo dell'operazione comprende il compenso del delegato, la cancellazione dei gravami e la liberazione, e non comprende la provvigione.

Il numero da guardare non è il prezzo ma lo sconto effettivo sul valore di mercato, e quello da scriversi su un foglio prima della gara è il prezzo massimo a cui fermarsi. La materia sta in [`aste-immobiliari.md`](aste-immobiliari.md).

## Che cosa fare quando si passa alla trattativa

A quel punto il registro ha esaurito il suo compito e cominciano gli altri due fogli. Il Dossier tecnico elenca i documenti da farsi consegnare, con la norma che li rende dovuti, e va usato prima della proposta, quando si ha ancora potere negoziale. La Checklist elenca le verifiche e le clausole, e il suo contatore va a zero prima di firmare, oppure le verifiche aperte diventano condizioni scritte dentro la proposta.
