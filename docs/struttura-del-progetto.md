# La struttura del progetto, e perché è fatta così

> Mappa di dove vive ogni cosa e della ragione per cui vive lì. Da settembre 2026 il repository contiene due basi di codice che condividono un modello: lo strumento locale in Python, che produce il workbook Excel, e l'applicazione web in TypeScript, che nascerà su Cloudflare. Questo documento serve a orientarsi fra le due senza doverle leggere, e a sapere quale toccare quando si cambia qualcosa. Si legge prima di aprire un file la prima volta, e quando si aggiunge una cartella.

## Le due basi di codice, e cosa le tiene insieme

La prima domanda che un lettore si fa è perché ci siano due implementazioni dello stesso calcolo. La risposta breve è che una serve a produrre un file e l'altra a servire una pagina, e nessuna delle due può fare il mestiere dell'altra: `openpyxl` non gira in un browser, e TypeScript non genera un foglio Excel con formule vive senza portarsi dietro mezza applicazione.

La risposta lunga è che le due non sono paritarie. Il motore Python è l'implementazione di riferimento: è quello verificato dai test di dominio, quello che il generatore del workbook usa, e quello che decide chi ha ragione quando i numeri divergono. Il motore TypeScript è un porto, e vive solo finché un presidio automatico dimostra che dice le stesse cose. Il presidio è `tools/genera-motore.py`, che dal motore Python emette i parametri fiscali in TypeScript e duecentoundici casi di riscontro con il loro esito completo; la suite in `app/test/motore.test.ts` li ricalcola e confronta ogni valore entro un miliardesimo relativo. Il racconto della scelta, con il difetto che ha fatto emergere, sta nella voce 14 dello studio didattico.

Dal 9 settembre 2026 il presidio ha una seconda famiglia di vettori, quella della simulazione del rischio, e sta in un file a parte per una ragione di sostanza: la simulazione non dipende dai soli input ma anche dalle estrazioni, che due linguaggi non possono generare uguali. I vettori portano percio' anche il campione di estrazioni con cui sono stati prodotti, la suite lo passa come ingresso, e le estrazioni per l'uso interattivo restano una funzione separata e dichiaratamente fuori dal confronto. La voce 16 dello studio didattico racconta il pattern e i due difetti che ha fatto emergere.

Ne segue una regola operativa che vale sempre: dopo aver toccato `src/immobiliare/calcoli.py` o `src/immobiliare/parametri.py`, i vettori sul disco sono scaduti. Il comando `python tools/genera-motore.py --check` lo dice senza scrivere niente, e la suite TypeScript si rifiuta di partire se la revisione dei parametri non coincide con quella dei vettori.

## La mappa

```
real-estate/
  src/immobiliare/      il motore Python e il generatore del workbook
    parametri.py        aliquote, soglie e moltiplicatori, con fonte e data
    calcoli.py          il modello: imposte, mutuo, locazione, metriche, inflazione
    excel_builder.py    i ventun fogli con le formule vive
    rischio.py          la simulazione probabilistica e il tornado, riferimento del porto
    annunci.py omi.py tassi.py indicatori.py comuni.py llm_locale.py
  tools/                gli eseguibili, che si lanciano a mano
    valuta.py           la riga di comando dello strumento locale
    genera-motore.py    parametri TypeScript e vettori di riscontro
    verifica-excel.ps1  apre il workbook con Excel e cerca le celle in errore
    md-unwrap.py collega-riferimenti.py fix-*.py   convenzioni della documentazione
  tests/                le prove dello strumento locale, in Python
  app/                  l'applicazione web
    src/motore/         il porto TypeScript del modello, piu' esitoCompleto e il rischio
    src/condiviso/      le regole che il Worker e il browser applicano entrambi
    src/server/         il Worker: identita', autorizzazione, rotte di dati e di piattaforma
    src/interfaccia/    il guscio: cliente, elenco, ciclo di bozza, controlli, stile
    src/sezioni/        una cartella per area, con sezione, modello e tipi
    migrazioni/         lo schema del database, un file per passo
    test/               le prove: motore e interfaccia in Node, rotte e identita' in workerd
    statico/            l'interfaccia costruita da Vite, non versionata
    index.html vite.config.ts   la pagina d'ingresso e la costruzione
    wrangler.toml       la configurazione del Worker
  docs/                 la conoscenza del dominio e le decisioni tecniche
  .claude/              memoria di progetto, schede di contesto, regole, studio didattico
  .github/workflows/    prove a ogni spinta, e distribuzione da main dopo che sono passate
  data/                 registro annunci e cache OMI, non versionati
  output/               il workbook generato, non versionato
  _notes/               materiale personale, non versionato
```

Una cartella non c'è e vale dire perché. Non c'è una cartella condivisa fra Python e TypeScript, perché ciò che i due condividono, cioè i parametri fiscali, i casi di prova e dal 14 settembre 2026 il catalogo delle verifiche pre-acquisto, passa dal generatore invece che da un formato comune: un formato comune andrebbe mantenuto, il generatore no.

Due cartelle ci sono dal 14 settembre 2026, con l'apertura della fase tre, e vale dire che cosa distingue l'una dall'altra. In `app/src/condiviso/` stanno le regole che il Worker e il browser applicano entrambi, per ADR-027: la forma di un immobile con la sua validazione e i suoi valori predefiniti, la gerarchia dei ruoli, la forma del documento delle ipotesi con la funzione che lo scrive conservando ciò che non si conosce, e i due file che il generatore emette, cioè il catalogo delle verifiche e i predefiniti delle dataclass di ingresso del motore. Le due applicazioni non hanno lo stesso statuto, e confonderle sarebbe grave: quella del Worker è la difesa, perché chiunque può parlare all'interfaccia di programmazione senza passare dalla pagina, mentre quella del browser evita all'utente un giro di rete per sapere una cosa che si poteva sapere prima.

In `app/src/sezioni/` sta una cartella per area, con la forma del progetto gemello di questa macchina: una sezione che mostra, un tipo per la forma, e un modello di funzioni pure dove sta ogni regola di dominio dell'area. La ripartizione non è estetica ed è la ragione per cui le prove sono sostenibili: una funzione pura si prova con un'asserzione, mentre la stessa regola scritta dentro un componente si prova solo simulando un clic, il che costa dieci volte tanto e verifica meno. La regola pratica che ne discende è che in un file di sezione non compaia un solo ramo che riguardi il dominio. Il guscio sta in `app/src/interfaccia/`, e dal 14 settembre 2026 possiede più della navigazione: per ADR-028 tiene l'identità, la scelta dell'organizzazione, l'elenco degli immobili, l'immobile aperto e il ciclo di salvataggio, e a un'area consegna soltanto l'immobile, il ruolo e le funzioni che salvano e rimuovono. Un'area non riceve il cliente, che resta l'unico punto dell'applicazione che parla con il server, e la ragione è che ciò che un'area ha in mano finirà per usarlo: con il cliente potrebbe caricarsi l'elenco e scegliersi l'immobile per conto proprio, che è esattamente ciò che produrrebbe sei elenchi caricati sei volte e sei selezioni che si perdono cambiando schermata. Il ciclo di modifica e salvataggio vive in `bozza.ts`, perché le cinque cose che lo compongono, e in particolare l'azzeramento della bozza quando cambia l'immobile aperto, sono le prime che una sesta copia dimenticherebbe.

Una riorganizzazione più radicale, per esempio spostare il codice Python sotto `python/` per simmetria con `app/`, è stata considerata e scartata: rinominare `src/` significherebbe toccare ogni importazione, ogni test, ogni comando documentato e centinaia di riferimenti nella documentazione, in cambio di una simmetria che non risolve nessun problema reale. La leggibilità di una struttura si ottiene spiegandola, non pareggiandola.

## Come è fatta l'applicazione, dall'esterno verso l'interno

Il percorso di una richiesta è la cosa da capire per prima, perché su questa piattaforma è diverso da quello di un'applicazione con un server proprio.

Chi apre l'indirizzo incontra Cloudflare Access, che non è codice nostro. Se non ha una sessione valida gli viene chiesto di identificarsi, con un codice monouso spedito alla sua posta o con un fornitore di identità esterno. Superato quel passaggio, ogni richiesta che arriva al Worker porta un token firmato che dice chi è quella persona.

Il Worker fa tre cose, in quest'ordine, e sono in tre file diversi apposta. Verifica il token e ne ricava un indirizzo di posta, in `identita.ts`. Risolve l'appartenenza di quell'indirizzo all'organizzazione richiesta e il suo ruolo, in `autorizzazione.ts`. Solo allora esegue il gestore della rotta, in `immobili.ts` o in `membri.ts`, che riceve un contesto già autorizzato e non ha modo di vedere la richiesta grezza.

Dal 14 settembre 2026 le famiglie di rotte sono due, per ADR-029, e la differenza va conosciuta perché è una difesa e non una classificazione. Le rotte sotto un'organizzazione toccano i dati e chiedono un ruolo; quelle di piattaforma, in `piattaforma.ts`, toccano il registro delle organizzazioni e chiedono un livello. Le due non si sommano e non si implicano: un superamministratore crea l'organizzazione di un cliente e ne nomina l'amministratore, e non ne legge gli immobili. Se vuole leggerli deve aggiungersi fra i membri, e l'aggiunta lascia una riga; la protezione è quindi tracciabilità e non impossibilità, e vale dirlo per intero perché le due promesse si confondono con facilità.

Il calcolo non passa da qui. Gira nel browser, con il motore TypeScript, sui dati che l'utente ha inserito. Il server conserva gli input e non conserva nessun risultato, ed è una scelta di cui parla la sezione seguente.

Dal 14 settembre 2026 il Worker fa una quarta cosa, e va detta perché è una trappola evitata. Tutto ciò che non comincia per `/api` e non corrisponde a un file statico riceve la pagina dell'applicazione, servita attraverso il legame `ASSETS`. Quel ripiego lo farebbe anche l'impostazione `single-page-application` delle risorse statiche, che però scatta prima del Worker e risponderebbe la pagina anche a `/api/qualcosa`: una chiamata sbagliata all'interfaccia di programmazione riceverebbe venti kilobyte di HTML invece di un rifiuto in JSON. La configurazione lascia quindi passare al Worker tutto ciò che non trova, e il ripiego è scritto dopo le rotte, dove si legge e si prova.

## Le tre decisioni di architettura che spiegano il resto

### L'organizzazione è la radice, dal primo giorno

Ogni tabella che contiene dati di qualcuno ha una colonna `organizzazione_id`, ogni interrogazione filtra su quella colonna, e ogni rotta riceve l'organizzazione dal percorso. Non è una previsione ottimistica sul successo del prodotto: è la constatazione che aggiungere la multiproprietà dopo obbligherebbe a migrare ogni tabella e riscrivere ogni interrogazione, e che nel frattempo esisterebbero righe senza proprietario che nessun filtro può recuperare. La decisione è ADR-025, e discende dal fatto che lo strumento sarà venduto a un'agenzia.

### Colonna se si filtra, documento se lo legge solo il motore

L'immobile ha una decina di colonne vere, cioè titolo, comune, prezzo, superficie, categoria, rendita, stato; tutte le altre ipotesi di valutazione, che sono una quarantina di campi fra acquirente, finanziamento e gestione, viaggiano in una colonna sola come documento JSON.

Il criterio è quello che sta nel titolo di questa sezione, e serve a evitare due errori simmetrici. Una tabella con cinquanta colonne va migrata ogni volta che il modello cresce di un'ipotesi, e le migrazioni su un database di produzione sono il posto dove si rompono le cose. Un documento unico, all'opposto, rende impossibile una graduatoria: non si ordina per prezzo se il prezzo è dentro una stringa JSON. Tenere fuori i campi su cui si filtra e dentro quelli che solo il motore legge dà la parte utile di entrambe le forme.

### Nessun valore calcolato viene salvato

Rendimenti, rata, prezzo massimo sostenibile, flussi di cassa: niente di tutto questo sta nel database. Si ricava dagli input a ogni lettura, nel browser.

La ragione è che un numero derivato conservato diventa falso in silenzio il giorno in cui cambia un'aliquota o si corregge una formula, e questo progetto ha già pagato quel prezzo altrove. Il costo dell'alternativa è nullo o quasi: il motore calcola una valutazione completa in una frazione di millisecondo, quindi ricalcolare un elenco di cento immobili costa meno di trenta millisecondi, mentre mantenere coerente una cache di risultati costerebbe una colonna con la revisione dei parametri, un controllo a ogni lettura e un lavoro di ricalcolo dopo ogni aggiornamento fiscale.

Il giorno in cui l'elenco diventasse abbastanza grande da rendere il ricalcolo percettibile, la risposta corretta non sarà salvare i risultati ma calcolarli una volta sola per sessione, che è una cache in memoria e non un dato.

## Come si prova, e perché in due modi

Le prove sono cinquantadue e girano in due ambienti diversi, ed è deliberato.

Il motore, la simulazione del rischio e i controlli sulla configurazione girano in Node, perché sono aritmetica e lettura di file. Le rotte e l'identità girano dentro workerd, cioè il runtime che Cloudflare esegue davvero, con un database D1 locale creato per l'occasione. Provare le rotte contro un finto database darebbe una suite verde che non dice niente sul comportamento reale, e in particolare non direbbe nulla sui vincoli di integrità, che sono metà della difesa: nella suite ci sono tre prove che verificano che il database rifiuti un'appartenenza a un'organizzazione inesistente, un ruolo inventato, e che cancellando un'organizzazione spariscano i suoi immobili.

Niente di tutto questo richiede un account o una connessione. Il comando è `npm test` dentro `app/`.

## I comandi che servono

```
python -m pytest tests                          le prove dello strumento locale
python tools/genera-motore.py                   rigenera parametri e vettori di riscontro
python tools/genera-motore.py --check           dice se i vettori sono scaduti
cd app && npm test                              motore, rotte, identita', limiti
cd app && npm run tipi                          il controllo dei tipi, senza emettere niente
cd app && npm run migra:locale                  applica le migrazioni al D1 locale
```

## Dove guardare quando si cambia qualcosa

Se cambia un'aliquota si tocca `parametri.py`, si rigenerano i vettori e si esegue tutto. Se cambia una formula si tocca `calcoli.py`, si aggiorna il porto in `app/src/motore/motore.ts`, si rigenerano i vettori: la suite dirà se il porto è rimasto indietro. Se si tocca la simulazione del rischio si toccano due file, `src/immobiliare/rischio.py` e `app/src/motore/rischio.ts`, si rigenerano i vettori e si guarda che i valori congelati in `tests/test_rischio.py`, che sono quelli letti da Excel, non si siano mossi: se si muovono, si è cambiato il modello e non il codice, e il foglio va cambiato con esso. Se cambia la forma dei dati si aggiunge una migrazione in `app/migrazioni/`, mai modificando quelle già applicate. Se si aggiunge una rotta si passa da `rotta()` in `autorizzazione.ts`, che pretende il ruolo minimo, e si scrivono le due prove, quella del permesso e quella del rifiuto.
