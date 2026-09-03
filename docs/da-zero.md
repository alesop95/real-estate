# Da zero alla prima valutazione

> Percorso di avvio per chi non ha mai aperto questo progetto e non ha nulla installato. Si arriva a una valutazione completa di un immobile reale in un'ora, comprese le pause per cercare i documenti. Chi ha già l'ambiente pronto può saltare al passo 4.

## Cosa serve, e cosa non serve

Serve **Python**, versione 3.11 o successiva, e una sola libreria. Serve **Excel** se si vuole eseguire la verifica automatica del workbook, ma non per usarlo: il file si apre anche con LibreOffice o Google Sheets, dove però la validazione a tendina e la formattazione condizionale possono rendere in modo diverso.

Non servono connessione permanente, account, chiavi, database, né alcun servizio in esecuzione. Tre funzioni escono dalla macchina, e sono tutte facoltative: la lettura dei tassi correnti dalla Banca centrale europea, lo scarico delle quotazioni storiche dell'Osservatorio immobiliare, e la strutturazione automatica del testo di un annuncio tramite un modello linguistico locale. Se nessuna delle tre risponde, il modello, i test e il workbook funzionano ugualmente.

## Passo 1: Python

Su Windows conviene installarlo dal Microsoft Store cercando Python, oppure da `python.org` spuntando la casella che aggiunge Python al PATH. Per verificare che ci sia:

```
python --version
```

Se risponde con un numero di versione uguale o superiore a 3.11, il passo è fatto.

## Passo 2: la libreria

Una sola, e si installa in pochi secondi.

```
pip install openpyxl
```

Chi vuole anche eseguire i test aggiunga `pytest`, che però non è necessario: i due file di test si eseguono anche direttamente.

## Passo 3: il progetto

Si clona la repository, oppure si scarica lo ZIP dalla pagina GitHub e si estrae. Poi ci si porta dentro la cartella e si genera il workbook.

```
python tools/valuta.py excel
```

Compaiono tre righe di conferma con il percorso del file prodotto e la data della revisione fiscale. Il file sta in `output/Valutazione-Immobile.xlsx`.

Una cosa da sapere adesso, perché evita un dispiacere più avanti: **quel comando riscrive il file da zero ogni volta**. Quello che si è digitato dentro va perso. Chi ci lavora sul serio lo salva con un altro nome, per esempio `Valutazione-via-Roma-12.xlsx`, e lavora su quello.

## Passo 4: i documenti da procurarsi

Prima di aprire il foglio conviene avere sottomano cinque cose. Senza, si compila con valori inventati e si ottiene una risposta inventata.

La **visura catastale** dell'immobile, da cui si leggono la categoria e soprattutto la rendita catastale, che è il numero più importante del foglio dopo il prezzo perché su di essa si calcolano quasi tutte le imposte. La chiede l'agenzia o il venditore, e si ottiene anche dall'Agenzia delle Entrate.

Il **consuntivo condominiale** degli ultimi due esercizi, non la stima a voce dell'agenzia, e i **verbali delle ultime assemblee**, perché i lavori già deliberati e non ancora eseguiti sono un costo certo che arriva dopo il rogito.

La **delibera comunale sull'aliquota IMU** dell'anno in corso. La legge fissa una base dello 0,86 per cento ma i Comuni possono arrivare all'1,06, e su vent'anni la differenza non è piccola. Si trova sul sito del Comune o sul portale del federalismo fiscale.

Le **quotazioni OMI** della zona, che sono l'unico riferimento pubblico e gratuito per capire se un prezzo al metro quadro sta dentro o fuori il mercato di zona. Si consultano gratis sul servizio a video dell'Agenzia delle Entrate.

Il **preventivo del mutuo**, se c'è. Serve il TAN, la durata, e le voci di costo: istruttoria, perizia, notaio dell'atto di mutuo, e la forma del premio della polizza incendio, che può essere annuo oppure unico anticipato per tutta la durata.

## Passo 5: la prima passata, quindici minuti

Si apre il file e si va al foglio **Cruscotto**. È tutto calcolato e all'inizio dice cose senza senso, perché legge i valori di esempio: serve a sapere dove si arriverà.

Poi si va al foglio **Immobile** e si compilano solo le celle gialle, nell'ordine in cui compaiono. Prezzo trattato, rendita catastale, categoria, chi vende, se si chiede la prima casa, se si opta per il prezzo-valore. In fondo compaiono le imposte reali e il costo totale dell'operazione, che è il numero da avere in testa quando si fa la proposta: non il prezzo.

Poi il foglio **Mutuo**: importo, tasso, durata, e le voci di costo del preventivo. Se il preventivo non c'è ancora, si può sapere che tasso è ragionevole con un comando:

```
python tools/valuta.py tassi
```

che stampa la media di quello che le banche italiane hanno davvero applicato negli ultimi mesi, presa dai dati ufficiali della Banca centrale europea. Se il preventivo c'è, si confronta:

```
python tools/valuta.py tassi --tasso 0.032 --mutuo 90000 --durata 25
```

e la differenza rispetto al mercato viene tradotta in euro di interessi sull'intera durata, che è l'unica forma in cui un decimo di punto diventa una cifra su cui trattare.

Se il tasso che si sta valutando è variabile, prima di andare avanti serve una prova in più, e c'è un comando anche per quella:

```
python tools/valuta.py tassi --risalita
```

Stampa di quanto l'Euribor a tre mesi è salito nelle peggiori finestre della sua storia dal 1994, che è la misura da mettere nel percorso del tasso della scheda **Simulatore mutuo**. Il numero da aspettarsi non è quello che viene in mente: fra giugno 2022 e giugno 2023 sono stati 3,78 punti in dodici mesi. Si compila il percorso a gradini con quel rialzo, si legge la rata massima raggiunta e si decide se è sostenibile, perché è quella la domanda che il variabile pone e che il tasso di partenza non fa vedere.

Infine il foglio **Locazione**, se l'immobile si affitta: canone atteso, spese condominiali dal consuntivo, aliquota IMU dalla delibera. Il foglio mette a confronto quattro regimi fiscali sullo stesso immobile e si sceglie quello che alimenterà la proiezione.

A questo punto si torna al **Cruscotto** e i numeri sono veri.

## Passo 6: leggere il risultato

Cinque numeri, in quest'ordine.

Il **costo totale** e la **cassa necessaria al rogito** dicono se l'operazione è alla portata. La cassa necessaria è quasi sempre più alta di quanto si pensa, perché il prezzo non comprende imposte, notaio e provvigione.

Il **rendimento netto** è il numero per decidere. Fra il rendimento lordo che si legge negli annunci e questo si perdono di norma due punti e mezzo: chi promette un netto vicino al lordo sta contando male.

Il **cash flow mensile** dice se l'immobile mette soldi in tasca o li toglie. Con un mutuo importante è normale che sia negativo, e la domanda giusta non è se è bello ma se è sostenibile per anni.

Il **debt service coverage ratio** sotto 1 dice che il reddito dell'immobile non copre la rata.

E il numero che quasi nessuno guarda: nel foglio **Rischio**, il *cash flow annuo nello scenario peggiore su venti*. Diviso dodici è quanto si mette di tasca propria ogni mese se le cose vanno male. Prima di firmare, quella cifra va potuta sostenere.

## Passo 7: prima di firmare

Si va al foglio **Checklist** e si filtra per fase. Il principio da capire, e da cui dipende tutto il resto, è che **una proposta di acquisto accettata dal venditore è già un contratto vincolante**: da quel momento l'obbligo di comprare esiste e la provvigione dell'agenzia è dovuta.

Quindi o si chiudono le verifiche prima di firmare, oppure si trasformano in condizioni scritte dentro la proposta. Le due che non devono mancare mai sono la condizione legata all'ottenimento del mutuo, e la clausola che esclude la provvigione se quella condizione non si avvera.

Il contatore in fondo al foglio dice quante verifiche restano aperte, e compare anche sul Cruscotto.

## Se si sta valutando più di un immobile

Si parte dall'altra estremità. Nel foglio **Annunci** si mettono tutti gli immobili che si stanno guardando, anche solo con link, Comune, metri quadri e prezzo. Il foglio **Confronto immobili** si popola da solo e applica a ciascuno il calcolo completo, imposte comprese.

Per orientarsi fra i venti fogli non serve ricordarli: il primo foglio del workbook è un indice con un collegamento a ciascuno, e per ognuno dice se si compila o si legge, quando lo si apre e che cosa ne esce. Da ogni foglio si torna all'indice col collegamento in alto a sinistra. Questo documento resta il percorso rapido; la guida completa a ogni comando e a ogni campo è `manuale-operativo.md`.

Da lì esce il candidato su cui vale la pena spendere l'ora del passo 5. Gli altri restano in lista.

Il registro si può popolare anche dalla riga di comando, che è più rapido:

```
python tools/valuta.py annunci aggiungi --link ... --comune "..." --mq 75 --prezzo 89000 --canone 550
python tools/valuta.py annunci elenca
python tools/valuta.py excel --con-annunci
```

## Se si compra in più persone

C'è il foglio **Comproprietà**, una riga per acquirente. La cosa da sapere subito è che **non serve costituire una società**: tenere insieme un immobile e affittarlo è comunione, non impresa. Le regole di governo e i casi in cui invece una società serve stanno in `comprare-in-piu-persone.md`.

## Verificare che tutto funzioni

Due comandi, utili dopo aver modificato qualcosa o se qualcosa sembra strano.

```
python -m pytest tests
powershell -NoProfile -ExecutionPolicy Bypass -File tools\verifica-excel.ps1
```

Il primo esegue quaranta test sul motore di calcolo e sulla struttura del workbook. Il secondo apre il file con Excel, forza il ricalcolo e segnala ogni cella in errore: serve perché la libreria che genera il file scrive le formule ma non le valuta.

Se la rigenerazione fallisce con un errore di permesso, è Excel rimasto aperto da una verifica precedente: va chiuso il processo.

## Dove andare a leggere

`guida-non-tecnica.md` accompagna foglio per foglio in linguaggio comune. `guida-tecnica(catena-calcolo-e-normativa).md` riporta architettura e riferimento di ogni voce con formula e norma. `fiscalita-acquisto.md` e `fiscalita-locazione.md` spiegano la materia. `due-diligence.md` spiega perché ogni verifica della checklist esiste. `comprare-in-piu-persone.md` copre l'acquisto in comproprietà. `fonti.md` dice da dove viene ogni numero.

Chi vuole capire perché il modello è fatto così, e non solo come si usa, trovi in `.claude/context/studio-didattico-master.md` il racconto delle scelte di progetto, con i deep-dive nel codice reale.

## Una cosa da ricordare

Le aliquote implementate sono quelle in vigore alla data di revisione dichiarata in cima al foglio Parametri, e cambiano con ogni legge di bilancio. Questo è uno strumento per arrivare preparati a tre conversazioni, quella con il commercialista, quella con il notaio e quella con il tecnico: non per sostituirle.
