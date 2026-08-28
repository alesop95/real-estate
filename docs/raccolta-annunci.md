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

Il modulo riconosce da solo il formato del file, perche' il mirror usa la virgola come separatore con l'intestazione sulla prima riga mentre la fornitura ufficiale usa il punto e virgola e antepone una riga di metadati, e i numeri hanno la virgola decimale in entrambi i casi.

Oltre agli intervalli di prezzo, il modulo espone per ogni zona il rendimento lordo implicito, cioe' il canone annuo di zona rapportato al prezzo di zona. E' il metro di paragone piu' onesto per un singolo annuncio: se un immobile promette molto piu' della sua zona, o e' un affare o c'e' qualcosa che non si e' capito, e la seconda ipotesi va esclusa prima di credere alla prima.

## Il riconoscimento dei duplicati

Lo stesso immobile ricompare spesso su portali diversi, con testo riscritto, foto diverse e prezzo leggermente diverso. Il confronto sul link non lo intercetta, perche' i link sono per costruzione diversi. Il registro fa due cose: normalizza il link togliendo i parametri di tracciamento, cosi' che lo stesso annuncio ripescato da una condivisione non entri due volte, e mette a disposizione il calcolo di un vettore semantico tramite il modello di embedding locale, con cui confrontare le descrizioni e far emergere le riproposizioni della stessa unita' sotto altra veste.
