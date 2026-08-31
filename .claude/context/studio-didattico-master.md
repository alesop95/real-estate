---
generated-from-commit: da assegnare al prossimo commit
generated-from-branch: main
generated-date: 2026-08-31
covers-paths:
  - src/immobiliare/**
  - tests/**
last-verified-commit: da assegnare al prossimo commit
---

# Studio didattico, racconto evolutivo

> Livello documentale distinto dalle schede di stato. `STACK.md` e le altre schede dicono *cosa* è vero oggi; `memory/decisions.md` dice *quale* decisione è stata presa e con quali conseguenze. Questo file dice *perché una forma ingenua era fragile e perché quella nuova è un salto*, e cresce per voci numerate in ordine cronologico: ogni intervento aggiunge una voce in fondo, nessuna voce si riscrive. Il dettaglio nel codice reale sta nei deep-dive `refactor-NN-*.md` accanto a questo file.

La pratica è stata adottata il 31 agosto 2026, su richiesta esplicita, con le voci che ricostruiscono i salti già compiuti in questo progetto perché tutti documentati e verificabili nel work-log e nel codice.

## 1. Il workbook porta formule, non risultati

Contesto. Il progetto deve produrre uno strumento che risponda a domande su un acquisto immobiliare. La prima scelta di architettura riguarda cosa esce dal generatore Python: numeri o formule.

Com'era e perché era fragile. La forma naturale, e quella che quasi tutti i generatori di report adottano, è calcolare in Python e scrivere il risultato nella cella. È semplice, si testa con un `assert`, e produce un file leggero. È però fragile per una ragione che non riguarda il codice ma l'uso: un file di numeri risponde a una domanda sola, quella con cui è stato generato. Cambiare il prezzo di cinquemila euro richiede di tornare al terminale, ricordare i parametri, rigenerare. Nella pratica significa che nessuno prova le ipotesi, e uno strumento di valutazione che non permette di provare le ipotesi non serve a valutare: serve a confermare la prima che si è avuta in testa.

Il salto senior e perché è meglio. Il generatore scrive formule Excel, e i riferimenti fra fogli passano per *nomi definiti* invece che per indirizzi di cella. La conseguenza è che il file non è un rapporto ma il modello stesso: chi lo apre cambia una cella gialla e vede ricalcolare l'intero workbook. Il costo è reale e va dichiarato: le formule non si valutano alla scrittura, quindi il generatore può produrre file sintatticamente validi e funzionalmente rotti, il che ha generato la voce 3 di questo racconto. Il principio generale è che quando l'artefatto prodotto è anche l'interfaccia con cui si lavora, conviene spostare il calcolo dentro l'artefatto e tenere nel codice la sua costruzione.

Dove leggere il dettaglio: `refactor-01-formule-vive.md`.

## 2. Il denominatore dei rendimenti è il costo totale, non il prezzo

Contesto. Ogni indicatore di rendimento è una frazione, e la scelta del denominatore è una scelta di modello che nessuno dichiara mai.

Com'era e perché era fragile. La convenzione degli annunci, delle conversazioni e della maggior parte dei fogli di calcolo che circolano è dividere per il prezzo. È fragile perché il prezzo non è il denaro che l'operazione ha assorbito: imposte di trasferimento, provvigione, notaio e oneri del mutuo sono capitale uscito dal conto corrente che non tornerà alla rivendita. Ignorarli non produce un errore visibile, produce un rendimento sistematicamente gonfiato, e la distorsione è tanto maggiore quanto più piccolo è l'immobile, cioè proprio dove i costi fissi pesano di più. Un modello che sbaglia sempre nella stessa direzione è peggio di uno rumoroso, perché sembra affidabile.

Il salto senior e perché è meglio. Il denominatore diventa il costo totale dell'operazione, e il capitale proprio effettivamente immobilizzato diventa il denominatore separato del *cash on cash*. Tenere due denominatori distinti, invece di uno solo di compromesso, è ciò che rende leggibile la leva finanziaria: il rendimento sul costo totale misura l'immobile, quello sull'esborso misura l'operazione finanziata. Sul caso di riferimento la differenza fra le due convenzioni è quasi un decimo, e il modello espone l'incidenza dei costi come indicatore autonomo proprio per rendere visibile quanto si sta correggendo.

Dove leggere il dettaglio: `refactor-02-denominatore.md`.

## 3. Il workbook si verifica aprendolo, non scrivendolo

Contesto. Conseguenza diretta della voce 1: la libreria che genera il file scrive le formule senza valutarle.

Com'era e perché era fragile. La verifica implicita era che il generatore terminasse senza eccezioni e il file si salvasse. È una verifica che non verifica nulla di ciò che conta: un riferimento a un nome inesistente, una parentesi sbagliata, un blocco XML vuoto passano tutti quel controllo. Il caso concreto che ha reso evidente il problema è stato un elemento di validazione dichiarato e mai associato ad alcuna cella, che ha prodotto un `<dataValidations count="0"/>` e ha reso il file irricevibile per Excel, senza che nulla in Python protestasse.

Il salto senior e perché è meglio. Esiste uno script che apre il workbook con Excel via automazione, forza un ricalcolo completo, raccoglie tutte le celle che valutano a errore e termina con codice diverso da zero. Accanto, una tecnica di diagnosi: quando il file non si apre affatto, si generano workbook progressivi con un foglio in più alla volta e si prova ad aprirli tutti, isolando il foglio responsabile per bisezione. Il principio generale è che quando un artefatto viene interpretato da un motore esterno, l'unica verifica che vale è farlo interpretare da quel motore.

Dove leggere il dettaglio: `refactor-03-verifica-con-excel.md`.

## 4. L'agevolazione applicabile è una sola fonte di verità

Contesto. L'agevolazione prima casa governa due grandezze diverse, l'aliquota dell'imposta di registro e il moltiplicatore catastale, e le governa insieme.

Com'era e perché era fragile. Le due grandezze erano calcolate in due punti distinti, ciascuno che si chiedeva da sé se l'agevolazione spettasse. Il calcolo del moltiplicatore guardava all'agevolazione *richiesta* dall'acquirente, quello dell'aliquota alla condizione completa che include l'esclusione delle categorie di lusso. Su un immobile ordinario i due coincidevano e il difetto restava invisibile; su una categoria A/1, A/8 o A/9 divergevano, e l'imposta risultava sottostimata di circa un dodicesimo. Il difetto era presente in modo identico nel motore Python e nelle formule Excel, il che dice qualcosa di utile: la doppia implementazione protegge dagli errori di trascrizione, non da un errore di ragionamento commesso una volta e replicato fedelmente.

Il salto senior e perché è meglio. La condizione diventa una funzione sola, `agevolazione_applicabile`, e nel workbook una cella sola con un nome, `agevolata`, calcolata prima di tutto ciò che ne dipende. L'ordine di costruzione delle celle smette di essere cosmetico e diventa parte della correttezza. Il principio è che quando due valori derivano dalla stessa condizione, la condizione va calcolata una volta e riferita, mai ricalcolata in parallelo: due copie della stessa logica divergono sempre, e divergono nel caso raro, cioè quello che nessuno prova.

Dove leggere il dettaglio: `refactor-04-agevolazione-unica.md`.

## 5. Un costo ricorrente sta in un posto solo

Contesto. L'accantonamento per la ristrutturazione di fine ciclo è un costo annuo che deve comparire nel conto economico della locazione e nella proiezione del flusso di cassa.

Com'era e perché era fragile. Compariva in entrambi, ed erano due cose diverse: nel foglio della locazione come voce del conto economico, nel foglio del flusso di cassa come colonna autonoma. Poiché la colonna dei costi operativi del flusso di cassa era derivata dal reddito operativo netto della locazione, l'accantonamento veniva sottratto due volte. Il flusso di cassa risultava peggiore del vero di un importo pari all'accantonamento, ogni anno, per tutto l'orizzonte, e nessun controllo lo segnalava perché entrambe le formule erano corrette prese da sole.

Il salto senior e perché è meglio. La voce entra una volta sola nel conto economico, e il foglio del flusso di cassa perde la colonna autonoma. La regola che ne discende, e che è stata applicata poi a ogni voce nuova, è che un costo ha un unico luogo di dichiarazione e tutti gli altri fogli lo ereditano attraverso una grandezza aggregata. Quando si è aggiunto il costo figurativo del tempo, mesi dopo, la domanda giusta è stata immediata: in quale conto economico entra, non in quali fogli va aggiunto.

Dove leggere il dettaglio: `refactor-05-doppio-conteggio.md`.

## 6. Il contratto posizionale fra due file va protetto da un test

Contesto. Il registro degli annunci è una dataclass Python, il foglio Annunci è una tabella Excel, e l'esportazione scrive per posizione di colonna.

Com'era e perché era fragile. L'allineamento fra l'ordine dei campi della dataclass, l'ordine della lista usata dall'esportazione e l'ordine delle intestazioni del foglio era garantito soltanto dall'attenzione di chi scriveva. Sono tre elenchi in due file diversi che devono restare paralleli, e nessun tipo li lega. Un campo inserito in mezzo alla dataclass avrebbe fatto scrivere i prezzi nella colonna delle note, in silenzio, con il file che si apre regolarmente e i numeri che sembrano numeri.

Il salto senior e perché è meglio. Un test esporta un annuncio con valori noti e rilegge le celle una per una, verificando anche che le tre colonne di formula non siano state sovrascritte. Ha ripagato il costo alla prima esecuzione, scoprendo un difetto che nessuno stava cercando: la libreria ignora l'assegnazione quando si passa un valore nullo al costruttore della cella, quindi un campo azzerato non ripuliva la cella e l'annuncio esportato ereditava in silenzio il dato di quello che occupava prima quella riga. Il principio è che un contratto posizionale non documentato è un difetto in attesa, e che il modo di renderlo sicuro non è commentarlo ma eseguirlo.

Dove leggere il dettaglio: `refactor-06-contratto-posizionale.md`.

## 7. La simulazione separa l'estrazione dal calcolo

Contesto. Passare da tre scenari scelti a mano a una distribuzione di esiti, restando dentro un foglio di calcolo e senza macro.

Com'era e perché era fragile. La forma ovvia è usare la funzione casuale nativa del foglio. È fragile per una proprietà di quella funzione che si scopre usandola: è volatile, quindi ogni ricalcolo rigenera tutti i numeri. Due letture consecutive dello stesso file danno risultati diversi, un percentile cambia mentre lo si guarda, e nulla è riproducibile né verificabile. Uno strumento che deve sostenere una decisione da centomila euro non può cambiare risposta a ogni pressione di un tasto.

Il salto senior e perché è meglio. Le due cose vengono separate. Le estrazioni sono mille righe di numeri fissi, generate una volta sola alla costruzione del file da un generatore con seme dichiarato, quindi identiche a ogni riapertura e riproducibili da chiunque rigeneri il workbook. Il calcolo che sta sopra è invece formula viva, e legge gli input dell'utente: cambiando il prezzo o il tasso, tutti i mille scenari si ricalcolano sulla stessa estrazione. Si ottiene una simulazione insieme stabile e interattiva, che è esattamente ciò che serviva e che nessuna delle due forme pure dava. Il foglio delle estrazioni è nascosto, perché non c'è nulla da leggerci.

Nella stessa voce rientra una correzione di modello che vale più della tecnica. La prima versione trattava l'estrazione sulla rivalutazione come se fosse un regime permanente per tutto l'orizzonte, e la coda alta produceva patrimoni finali fuori scala. La rivalutazione si compone, quindi l'estrazione non è la variazione di un anno ma la media del periodo, e la sua dispersione scende con la radice del numero di anni: senza quella correzione la simulazione era matematicamente coerente e finanziariamente assurda.

Dove leggere il dettaglio: `refactor-07-simulazione-riproducibile.md`.
