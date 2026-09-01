# Raccolta degli annunci e acquisizione dei dati

> Scheda operativa. Descrive come si tiene il registro degli immobili in valutazione, come si arricchisce e quali sono i limiti che l'acquisizione automatica deve rispettare. L'implementazione e' in `src/immobiliare/annunci.py` e `src/immobiliare/omi.py`, l'interfaccia in `tools/valuta.py`.

## Che cosa tiene il registro

Il registro e' un archivio CSV in `data/annunci.csv`, una riga per immobile, che sopravvive alla rigenerazione del workbook e non dipende da Excel. Ogni riga porta l'identificativo, lo stato di avanzamento, il link all'annuncio, i dati fisici ed economici dell'immobile, la quotazione OMI della zona e il canone atteso. Tre grandezze non si scrivono e si calcolano da sole nel foglio Annunci del workbook: il prezzo al metro quadro, lo scarto rispetto alla quotazione OMI della zona e il rendimento lordo.

Quattro campi meritano una nota perche' rispondono a domande che si pongono presto e che i dati puramente economici non catturano. L'agenzia e il contatto sono il riferimento con cui si sta trattando, inseriti a mano: non provengono dal prelievo automatico, che per scelta non estrae recapiti, e la differenza fra annotare un recapito ricevuto e raccoglierne a strascico e' esattamente la differenza fra un'agenda e una banca dati. La destinazione d'uso, cioe' la classificazione ministeriale, dice se l'immobile e' accatastato come abitazione oppure no: un monolocale accatastato a ufficio non e' un'abitazione, cambia le imposte, la possibilita' di prendervi la residenza e quella di locarlo a uso abitativo, e il cambio di destinazione ha un costo che va messo nel prezzo. La data di consegna serve alle nuove costruzioni, dove il tempo fra proposta e disponibilita' e' esso stesso un costo.

L'ordine delle colonne del foglio Annunci e' un contratto fra due file, perche' l'esportazione scrive per posizione e non per nome. Un test dedicato lo verifica, insieme al fatto che le tre colonne di formula non vengano mai sovrascritte: e' proprio quel test ad aver scoperto che la scorciatoia con cui si assegnava il valore a una cella saltava l'assegnazione quando il valore era nullo, lasciando in cella il dato dell'annuncio che occupava prima quella riga.

Il registro alimenta poi il foglio Confronto immobili, che applica a ogni riga lo stesso modello del resto del workbook, dalle imposte di trasferimento al cash flow, e restituisce una tabella in cui gli annunci si leggono in fila con rendimento netto, cap rate, cash on cash e debt service coverage ratio affiancati. Serve a scegliere quale immobile approfondire, non a decidere: il regime di acquisto applicato e' quello impostato nel foglio Immobile ed e' lo stesso per tutti, quindi confrontare cosi' un usato da privato e un nuovo da costruttore falsa le imposte e i due vanno valutati separatamente.

Lo scarto rispetto alla quotazione OMI e' la colonna che fa il lavoro. Un prezzo al metro quadro va letto solo contro il mercato della sua zona, e la quotazione dell'Osservatorio e' l'unico riferimento pubblico, gratuito e verificabile disponibile: la formattazione a scala di colore rende immediato vedere quali annunci stanno sopra il mercato di zona e quali sotto. Il rendimento lordo, ordinato in modo decrescente dall'elenco a riga di comando, serve invece a scremare in fretta una lista lunga prima di dedicare tempo a una valutazione completa.

Il riversamento nel workbook e' idempotente: riscrive le colonne di dato lasciando intatte le tre colonne di formula, e ripulisce le righe residue di un'esportazione precedente piu' lunga. Si puo' quindi rigenerare quante volte si vuole senza accumulare sporcizia.

## Tre modi di popolarlo, in ordine di preferenza

Il primo e' l'inserimento manuale con il sottocomando che aggiunge una riga. Non tocca nessun sito, non ha dipendenze, e per un numero di immobili nell'ordine delle decine e' semplicemente il modo piu' rapido.

Il secondo e' l'incolla del testo. Si apre l'annuncio nel browser, si copia il testo in un file e lo si passa al programma, che lo struttura con un modello linguistico in esecuzione sulla rete locale. Il contenuto non lascia la macchina: la richiesta va all'istanza Ollama configurata, e questa e' la ragione principale per cui questa strada e' preferita a un servizio in cloud. Il modello estrae Comune, indirizzo, tipologia, superficie, prezzo, piano, classe energetica e spese condominiali, con l'istruzione esplicita di non inventare i dati mancanti e di non riportare nomi, numeri di telefono o indirizzi email.

Il terzo e' il prelievo diretto della pagina, ed e' quello su cui il progetto prende una posizione restrittiva, per le ragioni della sezione seguente.

## I limiti dell'acquisizione automatica, e perche' sono scritti nel codice

Il prelievo automatico di pagine da portali di annunci tocca tre corpi normativi distinti, e il fatto che i dati siano visibili pubblicamente non risolve nessuno dei tre.

Il primo e' contrattuale: i termini di servizio dei portali disciplinano l'uso automatizzato, e il file `robots.txt` esprime in forma leggibile da una macchina quali percorsi il gestore intende escludere. Il modulo lo legge e lo rispetta senza eccezioni, per ogni singolo URL e non una volta per dominio, perche' un portale puo' consentire le pagine di dettaglio ed escludere le pagine di ricerca. Se il `robots.txt` non e' raggiungibile la risposta e' negativa: in assenza di un permesso esplicito il comportamento prudente e' astenersi, non presumere.

Il secondo e' il diritto sui generis del costitutore di banca dati, che tutela l'investimento nella raccolta e organizzazione dei dati e che colpisce l'estrazione o il reimpiego di una parte sostanziale del contenuto. E' la ragione per cui la raccolta qui e' puntuale e finalizzata a una decisione di acquisto personale, e non un'estrazione sistematica di interi cataloghi.

Il terzo e' la protezione dei dati personali. I recapiti dei venditori privati e degli agenti sono dati personali, e la loro raccolta massiva richiederebbe una base giuridica che qui non esiste. Il modulo quindi non li raccoglie e istruisce esplicitamente il modello locale a non estrarli.

Ne discendono i vincoli tecnici che il codice impone da se': una richiesta ogni cinque secondi per dominio, uno user agent che dichiara chi e' e a che scopo, nessuna rotazione di identita', nessun aggiramento di protezioni anti bot. Su quest'ultimo punto la posizione e' netta: se un sito risponde con un blocco, la risposta corretta e' fermarsi, non travestirsi. Quando il prelievo non e' consentito il programma non fallisce silenziosamente ma spiega le due vie alternative, l'incolla del testo e l'inserimento manuale, che restano sempre praticabili e sempre lecite.

## Le quotazioni OMI

Le quotazioni dell'Osservatorio del mercato immobiliare danno, per ogni zona omogenea di ogni Comune e per ogni tipologia edilizia, l'intervallo di prezzo al metro quadro di compravendita e di locazione, aggiornato semestralmente. Sono la base con cui il registro ancora i prezzi a un riferimento indipendente.

Sulle vie di accesso occorre essere precisi, perche' cambiano il modo di usare il modulo. La fornitura ufficiale e aggiornata passa dall'area riservata di Fisconline o Entratel: e' gratuita ma richiede un'autenticazione personale che uno script non puo' e non deve simulare, quindi il file va scaricato a mano una volta a semestre e passato al programma. Il mirror open data mantenuto da ondata, che il modulo sa scaricare da solo, ripubblica la stessa fonte ma si ferma al secondo semestre 2018: serve per ricostruire l'andamento storico di una zona, non per il prezzo di oggi, e il programma lo ricorda a ogni interrogazione. La consultazione puntuale a video sul servizio geopoi dell'Agenzia, infine, resta sempre disponibile senza registrazione ed e' la via piu' rapida per una singola zona.

Il modulo riconosce da solo il formato del file, perche' il mirror usa la virgola come separatore con l'intestazione sulla prima riga mentre la fornitura ufficiale usa il punto e virgola e antepone una riga di metadati, e i numeri hanno la virgola decimale in entrambi i casi. Riconosce anche la codifica, che e' l'insidia meno visibile: il mirror pubblica gia' in UTF-8, la fornitura ufficiale arriva nella codifica ANSI di Windows, e leggerla come UTF-8 non solleva errori ma sostituisce ogni accento con un segnaposto, rendendo irreperibile alla ricerca per nome proprio il Comune che si sta cercando.

### Il giro semestrale, cinque minuti

La fornitura si scarica due volte l'anno e la procedura e' sempre la stessa. Si accede ai servizi telematici dell'Agenzia con SPID o CIE, si entra nell'area riservata alla voce dei servizi ipotecari e catastali e dell'Osservatorio del mercato immobiliare, si sceglie Forniture dati OMI e poi Quotazioni immobiliari, si indicano semestre e ambito territoriale e si scarica il prodotto. L'archivio ottenuto si passa al programma senza estrarlo. Sull'ambito conviene ragionare una volta sola: la fornitura si chiede per Comune, provincia, area metropolitana, regione o intero territorio nazionale, e un raggio di ricerca realistico attraversa quasi sempre piu' province, perche' quaranta chilometri da un capoluogo di costa ne toccano tre o quattro. Scaricare l'intera regione costa un solo giro e un solo file, e il programma filtra per Comune a costo nullo: il file nazionale del mirror porta centosessantunomila quotazioni su quasi ottomila Comuni e si interroga in un istante.

```
python tools/valuta.py omi importa --file "<percorso dello zip scaricato>"
python tools/valuta.py omi cerca --comune "<Comune>"
```

Il primo comando normalizza i CSV nella cartella di cache, che non e' versionata; il secondo serve a verificare che siano entrati davvero, ed e' il controllo da fare subito perche' un ambito territoriale sbagliato produce un archivio valido che pero' non contiene il Comune di interesse. Se in cache finiscono piu' file, per esempio una provincia per volta, vengono letti tutti quelli del semestre piu' recente e i periodi superati restano fuori: mescolarli falserebbe il confronto, e leggerne uno solo, come faceva la prima versione, faceva concludere che un Comune non fosse coperto quando semplicemente stava nell'altro file. Le finestre utili sono la primavera per il secondo semestre dell'anno precedente e l'autunno per il primo semestre dell'anno in corso.

Oltre agli intervalli di prezzo, il modulo espone per ogni zona il rendimento lordo implicito, cioe' il canone annuo di zona rapportato al prezzo di zona. E' il metro di paragone piu' onesto per un singolo annuncio: se un immobile promette molto piu' della sua zona, o e' un affare o c'e' qualcosa che non si e' capito, e la seconda ipotesi va esclusa prima di credere alla prima.

## Il riconoscimento dei duplicati

Lo stesso immobile ricompare spesso su portali diversi, con testo riscritto, foto diverse e prezzo leggermente diverso. Il confronto sul link non lo intercetta, perche' i link sono per costruzione diversi. Il registro fa due cose: normalizza il link togliendo i parametri di tracciamento, cosi' che lo stesso annuncio ripescato da una condivisione non entri due volte, e mette a disposizione il calcolo di un vettore semantico tramite il modello di embedding locale, con cui confrontare le descrizioni e far emergere le riproposizioni della stessa unita' sotto altra veste.

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

Il comando `annunci confronta` da' la stessa graduatoria a video, ordinata per scarto sulla quotazione di zona e non per prezzo, perche' fra immobili di taglia diversa il prezzo non dice nulla. Accanto a ogni riga espone il canone che la zona paga per quella superficie, ricavato dalle quotazioni OMI di locazione e non dall'annuncio, e una colonna di segnalazioni ricavata dalle note: immobile gia' locato, da ristrutturare, zona assegnata per ipotesi, dati incoerenti nell'annuncio, rendita catastale mancante. E' un'euristica su testo libero e va letta per quello che e', cioe' un promemoria per non perdere di vista un vincolo mentre si guarda una tabella di numeri.

Nel workbook si apre il foglio Confronto immobili, che applica il modello completo a ogni riga e mette in fila rendimento netto, cap rate, cash on cash e debt service coverage ratio. Da lì esce il candidato su cui vale la pena spendere un'ora, e per quello si compila il foglio Immobile con i dati reali.

Sull'aggancio delle quotazioni vale un'avvertenza. Senza la zona OMI indicata nel registro, il riferimento è l'intero Comune, e su un Comune di costa la forbice mette insieme il lungomare e le zone agricole: il numero è corretto e quasi inutile. La zona si trova con `omi zone --comune "..."` incrociando l'indirizzo, si scrive nel registro con `annunci modifica --zona`, e da quel momento lo scarto diventa un numero su cui trattare.

## Se l'immobile viene da un'asta

Il percorso cambia in due punti. Nel registro si marcano i campi dedicati:

```
python tools/valuta.py annunci modifica --id house_4 --note "asta, tribunale di Macerata"
```

e si compilano a mano nel foglio Annunci le colonne dell'asta, cioè base d'asta, data, tribunale e procedura, e soprattutto lo stato di occupazione. Poi si lavora nel foglio Asta, non nel foglio Immobile: le imposte si calcolano allo stesso modo, ma il costo dell'operazione comprende il compenso del delegato, la cancellazione dei gravami e la liberazione, e non comprende la provvigione.

Il numero da guardare non è il prezzo ma lo sconto effettivo sul valore di mercato, e quello da scriversi su un foglio prima della gara è il prezzo massimo a cui fermarsi. La materia sta in `aste-immobiliari.md`.

## Che cosa fare quando si passa alla trattativa

A quel punto il registro ha esaurito il suo compito e cominciano gli altri due fogli. Il Dossier tecnico elenca i documenti da farsi consegnare, con la norma che li rende dovuti, e va usato prima della proposta, quando si ha ancora potere negoziale. La Checklist elenca le verifiche e le clausole, e il suo contatore va a zero prima di firmare, oppure le verifiche aperte diventano condizioni scritte dentro la proposta.
