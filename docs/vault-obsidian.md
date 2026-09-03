# Come organizzare questa documentazione in un vault Obsidian

> Il vault è aperto sulla radice del progetto dal 3 settembre 2026, e la sua configurazione vive in `.obsidian/`, ignorata da git. Il documento descrive come i documenti di `docs/`, la memoria di progetto e il materiale personale si dispongono nel vault, che cosa ci si guadagna, che cosa si rompe, e quale parte della configurazione è già scritta su disco contro quale resta da fare nell'interfaccia. Si legge prima di aprire questo progetto in Obsidian, e in particolare su un'altra macchina, dove `.obsidian/` non c'è perché non è versionata.

## La domanda vera, prima della struttura

Un vault Obsidian dà tre cose che una cartella di file Markdown non dà: i collegamenti bidirezionali, cioè aprendo un documento si vede chi lo cita; il grafo, che rende visibile quali documenti sono centrali e quali isolati; e la ricerca con proprietà, cioè trovare tutti i documenti con un certo stato di verifica o una certa data di revisione.

Toglie però una cosa, e va detta prima di parlare di cartelle: **la sorgente di verità si sdoppia.** Questo progetto ha una proprietà che vale più della navigabilità, cioè che ogni documento è versionato accanto al codice che descrive, e che i riferimenti fra documenti sono percorsi relativi che funzionano su GitHub, nell'editor e in qualunque visualizzatore Markdown. Un vault che copia i file crea una seconda copia che divergerà; un vault che li linka con la sintassi propria di Obsidian, cioè le doppie parentesi quadre, produce documenti che su GitHub mostrano un link rotto.

La conclusione è netta e conviene metterla in testa: **il vault va aperto sulla cartella del progetto, non accanto.** Obsidian sa aprire come vault una cartella qualunque, e ci mette dentro solo `.obsidian/`, che si aggiunge al `.gitignore`. Tutto il resto resta esattamente dov'è, i percorsi relativi continuano a funzionare, e non esiste una seconda copia.

## La struttura che ne risulta

Aprendo la radice del progetto come vault, la struttura è già questa e non richiede di spostare niente.

```
real-estate/                     ← il vault
  README.md                      ← nota di ingresso: si imposta come "Home"
  CLAUDE.md                      ← indice dei satelliti e regole di team
  docs/
    README.md                    ← indice della documentazione, il secondo hub
    guida-al-workbook.md
    manuale-operativo.md
    da-zero.md
    fiscalita-acquisto.md
    fiscalita-locazione.md
    due-diligence.md
    perizia-pre-acquisto.md
    aste-immobiliari.md
    comprare-in-piu-persone.md
    raccolta-annunci.md
    metodo-e-metriche.md
    guida-tecnica(catena-calcolo-e-normativa).md
    fonti.md
    vault-obsidian.md            ← questo file
    matematica/
      matematica-finanziaria.tex ← Obsidian lo mostra come testo, non lo compila
  .claude/
    memory/index.md              ← stato corrente
    memory/progress.md           ← work-log
    memory/decisions.md          ← venti decisioni
    context/*.md                 ← schede tecniche e studio didattico
  _notes/                        ← materiale personale, già fuori da git
  .obsidian/                     ← configurazione del vault, da ignorare in git
```

Nella pratica quotidiana serve una cosa in più: dire a Obsidian di non indicizzare ciò che non è documentazione. Alla voce dei file esclusi si aggiungono `src`, `tools`, `tests`, `scripts`, `output`, `data`, e in questo vault ci sono già, scritti in `app.json`. Restano visibili nel filesystem ma spariscono dal grafo e dalla ricerca, che è quello che si vuole: un grafo che include duemila righe di Python non dice niente.

## I due hub, e perché sono due

Un vault si naviga bene quando ha pochi punti di ingresso dichiarati, e questo progetto ne ha già due che funzionano come tali senza modifiche.

`README.md` è l'ingresso per chi arriva da fuori: dice che cosa fa il progetto, come si installa, com'è fatto. È il documento su cui il vault si apre, per il meccanismo spiegato più sotto: non esiste un'impostazione di pagina iniziale nel nucleo di Obsidian, e al suo posto si usa lo spazio di lavoro salvato.

`docs/README.md` è l'ingresso per chi cerca un documento: organizza i quattordici per tipo di domanda e non per argomento. È l'hub che si usa davvero durante il lavoro.

Chi conosce Obsidian riconoscerà qui il pattern delle *Map of Content*, cioè una nota che indicizza altre note invece di lasciare che il grafo si organizzi da solo. La differenza è che qui gli hub esistevano già prima del vault, perché servivano comunque: sono nati come indice di una cartella e funzionano come MOC per caso, non per progetto.

## Il frontmatter, e come sfruttare quello che c'è già

Obsidian legge il frontmatter YAML come proprietà interrogabili. Le schede sotto `.claude/context/` **ne hanno già uno**, nato per la riconciliazione con i commit.

```yaml
---
generated-from-commit: a0b3420
generated-from-branch: main
generated-date: 2026-09-01
covers-paths:
  - src/**
last-verified-commit: a0b3420
---
```

Quel frontmatter diventa, senza toccarlo, una tabella interrogabile: quali schede sono ancorate a un commit vecchio, quali coprono un percorso che è stato modificato, quale è la più datata. È esattamente la domanda che il motore di riconciliazione del progetto pone, e in Obsidian si risponde con una query invece che con uno script.

I documenti sotto `docs/` non hanno frontmatter. Aggiungerlo è la sola modifica ai file che questa proposta suggerisce, ed è additiva: tre righe in testa che nessun visualizzatore Markdown mostra come contenuto.

```yaml
---
tipo: scheda-di-dominio
risponde-a: perché quel numero è quel numero
verificato: 2026-08-28
---
```

I valori di `tipo` sarebbero quattro, gli stessi quattro dell'indice: `guida-uso`, `scheda-di-dominio`, `metodo`, `riferimento`. Il campo `verificato` è quello che conta di più su una documentazione fiscale, perché permette di chiedere quali schede non sono state riviste dopo l'ultima legge di bilancio.

## Che cosa il grafo mostra, e perché non è quello che questa scheda prevedeva

La previsione era due hub al centro, tre grappoli distinti e `fonti.md` come nodo più connesso dopo gli hub. Era un'inferenza dalla struttura logica della documentazione, non una misura, e la prima apertura del vault l'ha smentita. Vale conservare l'errore invece di riscriverlo: la forma di un grafo dipende da come i collegamenti sono scritti, non da come i documenti sono organizzati.

La misura, ottenuta contando i collegamenti Markdown fra le quarantanove note indicizzate, dice questo. Quarantanove nodi, quindici archi, un solo hub. L'hub è `README.md`, che collega tutti e quindici i documenti di `docs/`, compresi `docs/README.md` e questa scheda, e non è collegato da nessuno. I quindici documenti hanno ciascuno un collegamento in entrata e nessuno in uscita, quindi il grafo dei collegamenti reali è una stella e non tre grappoli. Le altre trentatré note sono isolate: le diciannove schede di `.claude/context/` fra cui i dodici approfondimenti dello studio didattico, i tre file di memoria, le cinque regole, la skill, `CLAUDE.md`, `CLAUDE.local.md` e le tre note sotto `_notes/`.

La ragione è una sola e riguarda un carattere. `docs/README.md` e `CLAUDE.md` indicizzano i documenti scrivendone il nome fra apici inversi, cioè `fiscalita-acquisto.md`, e non fra parentesi quadre e tonde. Per un lettore è un indice; per Obsidian, che conta solo i collegamenti veri, è testo, e infatti `docs/README.md` non contiene un solo collegamento Markdown. Ne segue che il secondo hub nel grafo non esiste, che i grappoli non esistono, e che `fonti.md`, il documento a cui tutto rimanda per la provenienza di un dato, ha grado uno.

Da qui le due strade. Lasciare così, e il grafo resta una stella di sedici nodi, corretta e povera. Oppure convertire i due indici in collegamenti veri, che è una modifica al contenuto e non alla vista, quindi fuori dal criterio dichiarato in questa scheda, ma che ha un valore indipendente dal vault, perché un indice con i nomi cliccabili è migliore anche su GitHub e nell'editor. È la strada presa il 3 settembre, e le righe che seguono dicono come e a che prezzo.

La conversione non è stata fatta a mano ma con `tools/collega-riferimenti.py`, che è nato per questo e resta nel progetto, perché la convenzione va mantenuta quando arriva un documento nuovo e non ricostruita a memoria. Lo strumento trasforma il nome fra apici inversi in un collegamento che tiene il nome fra apici inversi dentro il proprio testo, cioè `[` più il nome in monospazio più `](percorso)`: un code span dentro il testo di un collegamento è Markdown standard, reso da GitHub come da Obsidian, quindi la convenzione tipografica del progetto, che vuole i nomi di file in monospazio, non è stata sacrificata alla navigabilità. Il percorso è relativo alla nota, e passa alla forma con le parentesi angolari quando contiene tonde.

Quattro limiti dello strumento sono deliberati e vanno conosciuti prima di rilanciarlo. Non tocca il frontmatter né le righe dentro i blocchi recintati, quindi l'indice di `CLAUDE.md`, che vive in blocchi preformattati, resta testo, e i collegamenti di quel file sono soltanto quelli della sua prosa. Non indovina un nome nudo che nel vault esiste in più di un posto, ed è la regola che ha evitato l'errore vero della prima corsa: `README.md` citato dentro `docs/` veniva risolto sul README della cartella mentre la frase intendeva quello di radice. Collega la prima citazione per bersaglio in ogni file e non tutte, perché l'arco nel grafo è lo stesso e la prosa non si riempie di collegamenti ripetuti, e fa eccezione solo per i file il cui mestiere è indicizzare, cioè l'indice della documentazione, quello di stato e il master dello studio didattico, dove ogni citazione diventa un collegamento perché una riga di tabella che non collega è inutile a chi la sta guardando; per essere idempotente conta come prima citazione anche un collegamento che il file già porta, altrimenti ogni corsa ne aggiungerebbe uno nuovo fino a esaurire le citazioni. Questa scheda, infine, è esclusa dalla conversione, perché cita i nomi come oggetto di discussione e non come navigazione: collegarli le darebbe il grado di un hub e distorcerebbe il grafo che descrive.

La misura dopo la conversione, con lo stesso conteggio di prima: quarantanove nodi, centottantasei archi contro i quindici di partenza, un solo nodo isolato. I gradi più alti sono `studio-didattico-master.md` con trenta, perché indicizza i dodici approfondimenti e ognuno di essi rimanda a lui, poi i due registri di memoria, poi `fonti.md` con ventuno, che è esattamente la posizione che la previsione gli assegnava e che ora ha per misura invece che per inferenza. I grappoli esistono: le guide d'uso, le schede di dominio attorno a `fonti.md`, lo studio didattico come stella a sé, la memoria che lega tutto. Il solo nodo isolato era la trascrizione di una conversazione ChatGPT sotto `_notes/dossier/conversazioni/`, e il grafo ha fatto qui il suo lavoro migliore: quel punto sospeso, isolato per costruzione perché nessun documento del progetto lo citava, è stato notato proprio perché era il solo, riletto per intero e cancellato, dopo aver portato nel progetto l'unica cosa che conteneva e che mancava. Il conto è ora quarantotto nodi e centottantanove archi, con nessun orfano: i tre archi in più rispetto alla misura precedente sono i collegamenti scritti mentre si assorbiva quella conversazione. I nodi orfani restano comunque visibili nella configurazione, perché la prossima nota che nascesse scollegata è esattamente quella che si vuole vedere.

Due modifiche accompagnano la conversione, perché senza di esse il grafo resterebbe incompleto in due punti. `CLAUDE.md` non indicizzava le cinque regole modulari pur dichiarando di indicizzare i satelliti tracciati, e ora le nomina una per una: `security-permissions.md` era il secondo nodo isolato e non lo è più. `docs/manuale-operativo.md` citava la skill `latex-build` senza puntare al suo file, che nessuno collegava.

## Che cosa si rompe, e come si evita

Tre cose, in ordine di gravità.

**La sintassi dei collegamenti.** Obsidian propone per default le doppie parentesi quadre, che non sono Markdown standard e su GitHub restano testo. Va cambiata nelle impostazioni, e in questo vault lo è già in `app.json`: si disattiva il collegamento con le doppie quadre e si imposta il percorso relativo alla nota. Così i collegamenti che Obsidian crea sono gli stessi che funzionano già in tutto il resto del progetto.

**Le parentesi nel nome di un file.** `guida-tecnica(catena-calcolo-e-normativa).md` è un caso reale in questo progetto, e in Markdown un percorso con parentesi tonde richiede la forma con parentesi angolari, cioè `[testo](<percorso(con).md>)`, altrimenti la prima tonda di chiusura interrompe il collegamento. Obsidian gestisce entrambe le forme, GitHub anche, ma ogni collegamento a quel file va scritto nella forma angolare e chi lo scrive deve ricordarsene. Rinominare con i trattini, cioè `guida-tecnica-catena-di-calcolo-e-norme.md`, direbbe la stessa cosa senza il vincolo: è una raccomandazione e non un problema aperto, perché i collegamenti attuali sono scritti nella forma giusta e funzionano.

**La convenzione della riga unica per paragrafo.** Questo progetto scrive ogni paragrafo su una riga sorgente sola, per quanto lunga, e ha uno strumento che lo verifica. L'editor di Obsidian rispetta la convenzione perché non riformatta il testo esistente, ma alcuni plugin di formattazione automatica la violano riavvolgendo le righe a una larghezza fissa. Se si installa qualcosa del genere, `python tools/md-unwrap.py --check .` lo rileva al primo controllo.

Una quarta cosa non si rompe ma va saputa: `.obsidian/` contiene la configurazione del vault, comprese le dimensioni delle finestre e i file aperti di recente. Va nel `.gitignore`, e se si vuole condividere la configurazione fra macchine si versiona selettivamente solo `.obsidian/app.json` e `.obsidian/appearance.json`, lasciando fuori `workspace.json`.

## La configurazione, che ora esiste su disco

I sei passi previsti sono cinque scritti in `.obsidian/`, quindi su questa macchina non resta nulla da cliccare per averli, e uno che un file di configurazione del nucleo di Obsidian non può esprimere e che ha la sostituzione descritta più sotto.

Il file `app.json` porta le tre impostazioni che rendono il vault compatibile con il resto del progetto invece che ostile: i collegamenti si scrivono in Markdown standard e non con le doppie parentesi quadre, il percorso è relativo alla nota, e i sei percorsi di codice e di artefatti indicati sopra sono esclusi da ricerca, grafo e menzioni non collegate, con l'aggiunta di `.pytest_cache/`, che contiene un README generato da pytest e non da noi. Due impostazioni non erano nella proposta e vale dire perché ci sono. La visualizzazione dei file non supportati è attiva, altrimenti la trattazione `.tex` non comparirebbe nemmeno nell'albero dei file, e l'aggiornamento automatico dei collegamenti al rinomino è disattivo, perché su una documentazione dove ogni collegamento è scritto a mano nella forma che GitHub accetta, compreso il caso con le parentesi tonde, la riscrittura automatica è un rischio e non una comodità.

Il file `core-plugins.json` accende ciò che serve a navigare, cioè grafo, collegamenti entranti e uscenti, ricerca globale, struttura del documento, proprietà e note a piè di pagina, e spegne il resto. Due spegnimenti sono deliberati e non estetici. La sincronizzazione di Obsidian è spenta perché caricherebbe il contenuto del vault sui server del produttore, e questo progetto non pubblica niente fuori da questa macchina; il visualizzatore web interno è spento perché aprirebbe pagine di rete dentro l'applicazione che tiene aperto il dossier di una trattativa reale. Il file `community-plugins.json` allinea questo vault agli altri due della macchina con gli stessi tre plugin di terze parti, copiati dalla loro cartella e non riscaricati, quindi alle stesse versioni: BRAT, che installa e aggiorna plugin presi direttamente da GitHub, New 3D Graph, che è il motivo dell'allineamento perché disegna il grafo in tre dimensioni con filtri propri, ed Embed HTML, che mostra un file HTML dentro una nota. Nessuno dei tre riformatta il testo, che era il rischio da cui guardarsi, e la convenzione del paragrafo su riga unica resta comunque presidiata da `python tools/md-unwrap.py --check .`, da lanciare se un plugin nuovo entra. Una cosa va saputa e non nascosta: BRAT interroga GitHub all'avvio per cercare aggiornamenti, quindi il vault non è più a traffico di rete nullo. È una richiesta al produttore dei plugin e non contenuto che esce, il che lo tiene dentro il vincolo di team, ma se si vuole il silenzio completo l'aggiornamento all'avvio si spegne nelle impostazioni di BRAT.

Il file `graph.json` è la parte che la prima apertura ha costretto a correggere, e la correzione vale più della configurazione. Nella prima versione gli allegati erano dentro, per far comparire la trattazione `.tex` come nodo terminale, e il grafo ne è uscito illeggibile. La ragione, contata: fuori dalle cartelle escluse il vault contiene novantasette file non Markdown, cioè trentatré fotografie, ventiquattro file di testo, dieci PDF, sei fogli di calcolo, tre documenti Word e gli ausiliari di LaTeX, quasi tutti sotto `_notes/`, e nessuno di essi è collegato a niente. Novantasette nodi sospesi contro quarantanove note sono coriandoli, non un grafo. Ora gli allegati sono fuori, e con essi la trattazione `.tex`: quel nodo terminale costava novantasei nodi di rumore e non valeva il prezzo. Restano fuori anche i collegamenti irrisolti, perché i riferimenti al codice escluso non devono sporcare la vista, mentre i nodi orfani sono dentro: dopo la conversione dei riferimenti descritta più sotto ne resta uno solo, e nasconderlo sarebbe nascondere l'unica informazione che quella categoria porta. Cinque gruppi di colore separano invece gli hub, i documenti di `docs/`, la memoria, le schede di contesto e il materiale personale, con la stessa logica della legenda a cinque colori del workbook.

Il file `workspace.json` apre il vault su `README.md` in modalità lettura, con `docs/README.md` nella seconda linguetta, l'albero dei file e la ricerca a sinistra, i collegamenti entranti e uscenti e la struttura del documento a destra. È la sostituzione della nota iniziale: Obsidian non ha nel nucleo l'impostazione di una pagina di apertura, che richiede il plugin Homepage della comunità, e al suo posto ripristina l'ultimo spazio di lavoro. Alla prima apertura il risultato è lo stesso, con una differenza da sapere: quel file è stato di sessione, quindi Obsidian lo riscrive alla chiusura e dalla volta successiva riapre i documenti dove li si è lasciati, non più i due hub.

Il vault è anche registrato nell'elenco dei vault dell'applicazione, che vive in `%APPDATA%\obsidian\obsidian.json`, quindi compare nella lista accanto agli altri di questa macchina e si riapre da lì senza indicare di nuovo la cartella. Del file precedente resta una copia `obsidian.json.bak` nella stessa cartella, da cancellare quando la lista risulta corretta.

Restano fuori dalla configurazione due cose. La lingua dell'interfaccia e il tema sono impostazioni dell'applicazione e non del vault, quindi seguono quelle degli altri vault di questa macchina e non sono state toccate. La forma del grafo, invece, va verificata alla prima apertura: due hub al centro, tre grappoli, la trattazione come nodo terminale. Se la forma non è quella, la causa più probabile è un'esclusione che ha tolto più del previsto, e si legge in `app.json` prima che nell'interfaccia.

Nessuno dei passi tocca un file di contenuto, ed è il criterio con cui la configurazione è costruita: se aprire il vault avesse richiesto di modificare i documenti, sarebbe stata una migrazione e non una vista.

## La raccomandazione

Aprire il vault sulla radice, con la configurazione qui sopra, e non aggiungere frontmatter finché non serve una query che lo richieda. Il guadagno immediato è la ricerca e il grafo, che su quattordici documenti più venti decisioni più dodici voci di studio didattico è già abbastanza da valere la configurazione. Il frontmatter su `docs/` diventa utile quando arriva la prima revisione fiscale con il vault già in uso, perché allora la domanda «quali schede non ho ancora riverificato» ha una risposta interrogabile invece che a memoria.

Quello che non conviene fare, e che è la tentazione naturale di chi conosce Obsidian, è ristrutturare le cartelle per assomigliare a un vault, per esempio separando note atomiche e MOC in cartelle dedicate. Questa documentazione non è un sistema di note personali: è la documentazione di un progetto, dove ogni file sta accanto al codice che descrive e i percorsi relativi sono un contratto con GitHub e con l'editor. Un vault che la rispetta la rende navigabile; un vault che la riorganizza la rompe in due.
