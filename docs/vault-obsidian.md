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

## Che cosa il grafo mostrerebbe

Vale la pena anticiparlo, perché è la ragione principale per aprire il vault e perché la forma attesa è verificabile.

Al centro `docs/README.md` e `README.md`, con il grado più alto. Attorno, tre grappoli distinti. Il grappolo delle **guide d'uso**, tre documenti che si citano a vicenda e citano i comandi. Il grappolo delle **schede di dominio**, sette documenti che citano `fonti.md` e sono citati dalla guida al workbook: `fonti.md` risulterebbe il nodo più connesso dopo gli hub, e sarebbe corretto, perché è il documento a cui tutto rimanda per la provenienza di un dato. Il grappolo **metodo e costruzione**, quattro documenti che si citano fra loro e citano il codice.

Un nodo isolato ci sarebbe, e va previsto invece di scoprirlo: `matematica-finanziaria.tex`. Obsidian non indicizza i collegamenti dentro un file `.tex`, quindi la trattazione comparirebbe come nodo terminale, citata ma senza citazioni in uscita. È accettabile, perché quel documento è per costruzione un punto di arrivo, e la sua tavola simbolo-cella-funzione svolge il ruolo dei collegamenti in forma tabellare.

## Che cosa si rompe, e come si evita

Tre cose, in ordine di gravità.

**La sintassi dei collegamenti.** Obsidian propone per default le doppie parentesi quadre, che non sono Markdown standard e su GitHub restano testo. Va cambiata nelle impostazioni, e in questo vault lo è già in `app.json`: si disattiva il collegamento con le doppie quadre e si imposta il percorso relativo alla nota. Così i collegamenti che Obsidian crea sono gli stessi che funzionano già in tutto il resto del progetto.

**Le parentesi nel nome di un file.** `guida-tecnica(catena-calcolo-e-normativa).md` è un caso reale in questo progetto, e in Markdown un percorso con parentesi tonde richiede la forma con parentesi angolari, cioè `[testo](<percorso(con).md>)`, altrimenti la prima tonda di chiusura interrompe il collegamento. Obsidian gestisce entrambe le forme, GitHub anche, ma ogni collegamento a quel file va scritto nella forma angolare e chi lo scrive deve ricordarsene. Rinominare con i trattini, cioè `guida-tecnica-catena-di-calcolo-e-norme.md`, direbbe la stessa cosa senza il vincolo: è una raccomandazione e non un problema aperto, perché i collegamenti attuali sono scritti nella forma giusta e funzionano.

**La convenzione della riga unica per paragrafo.** Questo progetto scrive ogni paragrafo su una riga sorgente sola, per quanto lunga, e ha uno strumento che lo verifica. L'editor di Obsidian rispetta la convenzione perché non riformatta il testo esistente, ma alcuni plugin di formattazione automatica la violano riavvolgendo le righe a una larghezza fissa. Se si installa qualcosa del genere, `python tools/md-unwrap.py --check .` lo rileva al primo controllo.

Una quarta cosa non si rompe ma va saputa: `.obsidian/` contiene la configurazione del vault, comprese le dimensioni delle finestre e i file aperti di recente. Va nel `.gitignore`, e se si vuole condividere la configurazione fra macchine si versiona selettivamente solo `.obsidian/app.json` e `.obsidian/appearance.json`, lasciando fuori `workspace.json`.

## La configurazione, che ora esiste su disco

I sei passi previsti sono cinque scritti in `.obsidian/`, quindi su questa macchina non resta nulla da cliccare per averli, e uno che un file di configurazione del nucleo di Obsidian non può esprimere e che ha la sostituzione descritta più sotto.

Il file `app.json` porta le tre impostazioni che rendono il vault compatibile con il resto del progetto invece che ostile: i collegamenti si scrivono in Markdown standard e non con le doppie parentesi quadre, il percorso è relativo alla nota, e i sei percorsi di codice e di artefatti indicati sopra sono esclusi da ricerca, grafo e menzioni non collegate, con l'aggiunta di `.pytest_cache/`, che contiene un README generato da pytest e non da noi. Due impostazioni non erano nella proposta e vale dire perché ci sono. La visualizzazione dei file non supportati è attiva, altrimenti la trattazione `.tex` non comparirebbe nemmeno nell'albero dei file, e l'aggiornamento automatico dei collegamenti al rinomino è disattivo, perché su una documentazione dove ogni collegamento è scritto a mano nella forma che GitHub accetta, compreso il caso con le parentesi tonde, la riscrittura automatica è un rischio e non una comodità.

Il file `core-plugins.json` accende ciò che serve a navigare, cioè grafo, collegamenti entranti e uscenti, ricerca globale, struttura del documento, proprietà e note a piè di pagina, e spegne il resto. Due spegnimenti sono deliberati e non estetici. La sincronizzazione di Obsidian è spenta perché caricherebbe il contenuto del vault sui server del produttore, e questo progetto non pubblica niente fuori da questa macchina; il visualizzatore web interno è spento perché aprirebbe pagine di rete dentro l'applicazione che tiene aperto il dossier di una trattativa reale. Il file `community-plugins.json` è una lista vuota, ed è la dichiarazione esplicita che nessun plugin di terze parti tocca questi file: il rischio concreto, già previsto sopra, è un formattatore automatico che riavvolge le righe e viola la convenzione del paragrafo su riga unica.

Il file `graph.json` imposta il grafo sulla forma attesa. Le etichette restano fuori, gli allegati dentro, perché è come allegato che compare la trattazione `.tex`; i collegamenti irrisolti sono nascosti, perché i riferimenti al codice escluso non devono sporcare la vista; i nodi orfani restano visibili, perché un documento che nessuno cita è un'informazione e non un difetto da mascherare.

Il file `workspace.json` apre il vault su `README.md` in modalità lettura, con `docs/README.md` nella seconda linguetta, l'albero dei file e la ricerca a sinistra, i collegamenti entranti e uscenti e la struttura del documento a destra. È la sostituzione della nota iniziale: Obsidian non ha nel nucleo l'impostazione di una pagina di apertura, che richiede il plugin Homepage della comunità, e al suo posto ripristina l'ultimo spazio di lavoro. Alla prima apertura il risultato è lo stesso, con una differenza da sapere: quel file è stato di sessione, quindi Obsidian lo riscrive alla chiusura e dalla volta successiva riapre i documenti dove li si è lasciati, non più i due hub.

Il vault è anche registrato nell'elenco dei vault dell'applicazione, che vive in `%APPDATA%\obsidian\obsidian.json`, quindi compare nella lista accanto agli altri di questa macchina e si riapre da lì senza indicare di nuovo la cartella. Del file precedente resta una copia `obsidian.json.bak` nella stessa cartella, da cancellare quando la lista risulta corretta.

Restano fuori dalla configurazione due cose. La lingua dell'interfaccia e il tema sono impostazioni dell'applicazione e non del vault, quindi seguono quelle degli altri vault di questa macchina e non sono state toccate. La forma del grafo, invece, va verificata alla prima apertura: due hub al centro, tre grappoli, la trattazione come nodo terminale. Se la forma non è quella, la causa più probabile è un'esclusione che ha tolto più del previsto, e si legge in `app.json` prima che nell'interfaccia.

Nessuno dei passi tocca un file di contenuto, ed è il criterio con cui la configurazione è costruita: se aprire il vault avesse richiesto di modificare i documenti, sarebbe stata una migrazione e non una vista.

## La raccomandazione

Aprire il vault sulla radice, con la configurazione qui sopra, e non aggiungere frontmatter finché non serve una query che lo richieda. Il guadagno immediato è la ricerca e il grafo, che su quattordici documenti più venti decisioni più dodici voci di studio didattico è già abbastanza da valere la configurazione. Il frontmatter su `docs/` diventa utile quando arriva la prima revisione fiscale con il vault già in uso, perché allora la domanda «quali schede non ho ancora riverificato» ha una risposta interrogabile invece che a memoria.

Quello che non conviene fare, e che è la tentazione naturale di chi conosce Obsidian, è ristrutturare le cartelle per assomigliare a un vault, per esempio separando note atomiche e MOC in cartelle dedicate. Questa documentazione non è un sistema di note personali: è la documentazione di un progetto, dove ogni file sta accanto al codice che descrive e i percorsi relativi sono un contratto con GitHub e con l'editor. Un vault che la rispetta la rende navigabile; un vault che la riorganizza la rompe in due.
