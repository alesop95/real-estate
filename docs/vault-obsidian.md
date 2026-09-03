# Come organizzare questa documentazione in un vault Obsidian

> Prova di organizzazione, non una migrazione già fatta. Descrive come i quattordici documenti di `docs/`, la memoria di progetto e il materiale personale si disporrebbero in un vault Obsidian, che cosa ci si guadagna, che cosa si rompe, e la sola forma che regge senza duplicare la sorgente. Si legge se si sta valutando di aprire questo progetto in Obsidian.

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

Nella pratica quotidiana serve una cosa in più: dire a Obsidian di non indicizzare ciò che non è documentazione. Nelle impostazioni, alla voce dei file esclusi, si aggiungono `src`, `tools`, `tests`, `scripts`, `output`, `data`. Restano visibili nel filesystem ma spariscono dal grafo e dalla ricerca, che è quello che si vuole: un grafo che include duemila righe di Python non dice niente.

## I due hub, e perché sono due

Un vault si naviga bene quando ha pochi punti di ingresso dichiarati, e questo progetto ne ha già due che funzionano come tali senza modifiche.

`README.md` è l'ingresso per chi arriva da fuori: dice che cosa fa il progetto, come si installa, com'è fatto. Si imposta come pagina iniziale del vault nelle impostazioni.

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

**La sintassi dei collegamenti.** Obsidian propone per default le doppie parentesi quadre, che non sono Markdown standard e su GitHub restano testo. Va cambiata nelle impostazioni: si disattiva il collegamento con le doppie quadre e si imposta il percorso relativo alla nota. Così i collegamenti che Obsidian crea sono gli stessi che funzionano già in tutto il resto del progetto.

**Le parentesi nel nome di un file.** `guida-tecnica(catena-calcolo-e-normativa).md` è un caso reale in questo progetto, e in Markdown un percorso con parentesi tonde richiede la forma con parentesi angolari, cioè `[testo](<percorso(con).md>)`, altrimenti la prima tonda di chiusura interrompe il collegamento. Obsidian gestisce entrambe le forme, GitHub anche, ma ogni collegamento a quel file va scritto nella forma angolare e chi lo scrive deve ricordarsene. Rinominare con i trattini, cioè `guida-tecnica-catena-di-calcolo-e-norme.md`, direbbe la stessa cosa senza il vincolo: è una raccomandazione e non un problema aperto, perché i collegamenti attuali sono scritti nella forma giusta e funzionano.

**La convenzione della riga unica per paragrafo.** Questo progetto scrive ogni paragrafo su una riga sorgente sola, per quanto lunga, e ha uno strumento che lo verifica. L'editor di Obsidian rispetta la convenzione perché non riformatta il testo esistente, ma alcuni plugin di formattazione automatica la violano riavvolgendo le righe a una larghezza fissa. Se si installa qualcosa del genere, `python tools/md-unwrap.py --check .` lo rileva al primo controllo.

Una quarta cosa non si rompe ma va saputa: `.obsidian/` contiene la configurazione del vault, comprese le dimensioni delle finestre e i file aperti di recente. Va nel `.gitignore`, e se si vuole condividere la configurazione fra macchine si versiona selettivamente solo `.obsidian/app.json` e `.obsidian/appearance.json`, lasciando fuori `workspace.json`.

## La configurazione minima, in pratica

Sei passi, una volta sola.

Si apre Obsidian e si sceglie di aprire una cartella come vault, indicando la radice del progetto. Nelle impostazioni dei file e collegamenti si disattiva l'uso delle doppie parentesi quadre e si imposta il formato del collegamento su percorso relativo alla nota. Nelle stesse impostazioni si aggiungono ai file esclusi `src`, `tools`, `tests`, `scripts`, `output`, `data`. Si imposta `README.md` come nota iniziale. Si aggiunge `.obsidian/` al `.gitignore`. Si apre il grafo e si verifica che la forma sia quella attesa: due hub al centro, tre grappoli, la trattazione come nodo terminale.

Nessuno dei sei passi tocca un file di contenuto, ed è il criterio con cui la proposta è costruita: se aprire il vault richiedesse di modificare i documenti, sarebbe una migrazione e non una vista.

## La raccomandazione

Aprire il vault sulla radice, con la configurazione qui sopra, e non aggiungere frontmatter finché non serve una query che lo richieda. Il guadagno immediato è la ricerca e il grafo, che su quattordici documenti più venti decisioni più dodici voci di studio didattico è già abbastanza da valere la configurazione. Il frontmatter su `docs/` diventa utile quando arriva la prima revisione fiscale con il vault già in uso, perché allora la domanda «quali schede non ho ancora riverificato» ha una risposta interrogabile invece che a memoria.

Quello che non conviene fare, e che è la tentazione naturale di chi conosce Obsidian, è ristrutturare le cartelle per assomigliare a un vault, per esempio separando note atomiche e MOC in cartelle dedicate. Questa documentazione non è un sistema di note personali: è la documentazione di un progetto, dove ogni file sta accanto al codice che descrive e i percorsi relativi sono un contratto con GitHub e con l'editor. Un vault che la rispetta la rende navigabile; un vault che la riorganizza la rompe in due.
