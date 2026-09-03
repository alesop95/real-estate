---
generated-from-commit: a0b3420
generated-from-branch: main
generated-date: 2026-09-01
covers-paths:
  - tools/verifica-excel.ps1
  - tests/**
last-verified-commit: a0b3420
---

# Verifica

## I quattro livelli

Il primo livello è la verifica formale del workbook. Lo script `tools/verifica-excel.ps1` lo apre con Excel via automazione COM, forza un ricalcolo completo con `CalculateFullRebuild`, raccoglie con `SpecialCells` tutte le celle che valutano a errore e le elenca con la formula che le ha prodotte, poi stampa i valori chiave e le sezioni di sintesi. Termina con codice diverso da zero se trova errori, quindi è usabile come cancello prima di un commit.

Due dettagli di ambiente che vanno ricordati perché fanno perdere tempo. L'automazione COM di Excel espone i metodi nella lingua di installazione, e con una console italiana il late binding di PowerShell non risolve `Open`: la chiamata va fatta con `InvokeMember` passando esplicitamente la cultura `en-US`. E il messaggio di errore che dice che il metodo non esiste è lo stesso che si ottiene quando il metodo esiste ma il file è malformato, per cui va isolata la causa provando ad aprire un file banale.

Il secondo livello è la bisezione sui fogli, quando il workbook non si apre. Si generano workbook progressivi con un foglio in più alla volta e si prova ad aprirli tutti: il primo che fallisce identifica il foglio responsabile. È così che è stato trovato l'elemento di validazione vuoto sul foglio Mutuo.

Il terzo livello sono i test automatici, in due file. `tests/test_calcoli.py` copre il motore di dominio e congela il caso di riferimento. `tests/test_workbook.py` copre la struttura del workbook generato: l'elenco dei fogli, la presenza dei nomi definiti essenziali, e soprattutto la corrispondenza posizionale fra le colonne del foglio Annunci e l'ordine con cui `annunci.esporta_in_excel` le scrive, che è il contratto più fragile del progetto perché vive in due file diversi e nessun tipo lo protegge. Quel test esporta un annuncio noto e rilegge le celle una per una, e ha già ripagato il costo trovando un difetto reale: `openpyxl` ignora l'assegnazione quando si passa `value=None` a `cell()`, quindi un campo azzerato non ripuliva la cella e l'annuncio esportato ereditava in silenzio il dato di quello che occupava prima quella riga.

Al 1 settembre 2026 i test sono sessantuno, quarantadue sul motore di calcolo e sui moduli di dominio e diciannove sulla struttura del workbook, sull'acquisizione e sulla graduatoria.

Una famiglia di test aggiunta il 1 settembre 2026 merita una nota di metodo, perché presidia una classe di difetto e non un calcolo. Sono i test che verificano come una formula cita altre celle, e sono scritti in termini di etichette e non di numeri di riga, così che continuino a valere dopo un riordino del foglio. Il test sul verdetto del Cruscotto verifica che il nome definito `conf_differenza` punti alla riga la cui etichetta è "Differenza a favore dell'acquisto", che è l'asserzione che avrebbe intercettato il difetto reale trovato quel giorno, cioè una coordinata fissa che era diventata la riga del patrimonio comprando e faceva dire al primo foglio del workbook il contrario di quello che il foglio di dettaglio concludeva. Il test sul conto economico della locazione verifica che il reddito operativo netto sommi esattamente le righe comprese fra il ricavo effettivo e se stesso, su tutte e quattro le colonne dei regimi e non solo sulla prima. Il test sulla tabella dei tre scenari è generico e non enumera le formule: estrae con un'espressione regolare tutti i riferimenti di colonna e verifica che ciascuno cada dentro la tabella e prima della riga che lo cita.

Un secondo criterio ricorrente in questi test è l'asserzione negativa, che spesso è quella che conta. Verificare che le due colonne del regime di acquisto esistano non protegge da nulla: se la formula delle imposte tornasse a citare i nomi globali, le colonne resterebbero al loro posto mostrando il regime della riga mentre il foglio calcola con quello globale. L'asserzione utile è che nella formula delle imposte i nomi `agevolata` e `da_impresa` non compaiano. Allo stesso modo, sul prezzo massimo sostenibile l'asserzione utile è che la formula non citi `incidenza_costi`, cioè che non sia tornata all'approssimazione per proporzione.

Un test che tocca la rete non è un test. La scansione delle risalite storiche dell'Euribor si verifica sostituendo la funzione di download con una lambda che restituisce una serie sintetica, costruita perché la peggiore finestra e l'escursione fra massimo e minimo divergano: è l'unico modo di verificare che la funzione stia misurando la finestra e non l'escursione. Accanto, un test di coerenza interna sui valori congelati in `parametri.RISALITE_EURIBOR` controlla che la finestra lunga non sia inferiore alla corta, che nessuna finestra superi l'escursione totale, e che i valori siano scritti in punti percentuali e non in frazione, perché un 3,78 riscritto come 0,0378 supererebbe ogni altro controllo e produrrebbe note del workbook che parlano di zero punti di rialzo.

Allo stesso genere appartiene il test sul foglio Dossier tecnico, che verifica che ogni riga porti uno dei tre soli valori ammessi nella colonna del peso. La ragione è che il contatore dei documenti bloccanti è un `COUNTIFS` su stringa esatta: un valore scritto anche solo con l'iniziale maiuscola non solleverebbe alcun errore, sparirebbe dal conteggio, e il Cruscotto direbbe che non manca nessun documento bloccante. È il modello di difetto contro cui vale la pena scrivere un test, cioè quello che produce un numero plausibile invece di un errore.

Il quarto livello, e il più importante per la correttezza sostanziale, è il confronto fra le due implementazioni. Lo stesso caso passa per il motore Python con `python tools/valuta.py riepilogo` e per il workbook, e i risultati devono coincidere. Sul caso di riferimento coincidono su costo totale, esborso, imposte, rata, reddito operativo netto, utile netto, rendimento netto, cap rate, cash on cash, debt service coverage ratio e cash flow.

## Il caso di riferimento

Immobile di categoria A/3, cinquantacinque metri quadri, rendita catastale di quattrocentocinquanta euro, prezzo trattato centoventimila, acquisto da privato con agevolazione prima casa e opzione prezzo-valore, mutuo di novantamila a tasso fisso del tre virgola due per cento su venticinque anni, canone atteso di cinquecento euro al mese in cedolare secca.

I valori attesi sono un valore catastale di 51.975 euro, imposte di trasferimento per 1.140, costi accessori per 11.557 pari al 9,63 per cento del prezzo, costo totale di 131.557, esborso iniziale di 41.557, rata mensile di 436,21, reddito operativo netto di 1.805, utile netto di 684, rendimento netto dello 0,52 per cento, cap rate dell'1,37, cash on cash del meno 10,95, debt service coverage ratio di 0,34 e cash flow annuo di meno 4.550 euro.

Se un cambiamento al generatore sposta uno di questi numeri senza che sia stata cambiata la regola corrispondente, è una regressione.

## Verifiche di dominio da tenere presenti

L'IRPEF lorda su trentamila euro di imponibile deve dare 7.100 euro con gli scaglioni 2026, cioè ventotto mila al ventitré per cento più duemila al trentatré. È il controllo più rapido per accorgersi che gli scaglioni sono rimasti a un'annualità precedente.

L'imposta di registro non può mai scendere sotto il minimo di legge, il che diventa vincolante su immobili con rendita catastale bassa: la formula usa un massimo e non una semplice moltiplicazione.

La detrazione degli interessi deve azzerarsi quando l'immobile non è abitazione principale, e il massimale deve scalare con la quota di acquisto.

Il prezzo-valore non si applica quando si compra da impresa con IVA, perché è una regola dell'imposta di registro: se il calcolo lo applicasse comunque, l'imposta risulterebbe sistematicamente sottostimata sugli acquisti da costruttore.

Il moltiplicatore catastale deve seguire l'agevolazione effettivamente applicabile e non quella richiesta. Sulle categorie A/1, A/8 e A/9 l'agevolazione non spetta mai, quindi il moltiplicatore torna a centoventi insieme all'aliquota del nove per cento: usare centodieci perché l'acquirente ha chiesto la prima casa sottostima l'imposta di circa un dodicesimo. Era un difetto reale, presente sia in Python sia nelle formule, trovato dal test sulla categoria di lusso.

## Prove di comportamento con Excel, oltre alla verifica formale

La verifica formale dice che nessuna cella è in errore, che è necessario e non sufficiente: una formula corretta che legge la cella sbagliata passa quel controllo. Per le funzionalità che dipendono da un input dell'utente serve una prova di comportamento, cioè aprire il workbook via automazione COM, scrivere gli input in memoria, forzare il ricalcolo e leggere l'esito, senza salvare.

Il pattern è quello dello script di verifica: `InvokeMember` con cultura `en-US` per aprire, `CalculateFullRebuild` dopo ogni scrittura, `$wb.Names.Item("nome").RefersToRange` per raggiungere una cella per nome definito invece che per coordinata, e chiusura con `Close(false)` perché il file su disco non va toccato. Le celle di un altro foglio non si raggiungono con `$ws.Range("nome")`, che è relativo al foglio e solleva un errore COM: va usata la collezione dei nomi del workbook.

Le prove eseguite il 1 settembre 2026, che vale ripetere dopo una modifica alle formule interessate: il regime di acquisto per riga, scrivendo NO nella colonna della prima casa di un annuncio e verificando che le sue imposte passino da 1.740 a 7.480 euro; l'avvertenza del confronto affitto, portando a zero l'importo del mutuo e verificando che il testo compaia; il verdetto del Cruscotto, marcando l'immobile come abitazione principale e portando il rendimento del portafoglio al nove per cento, dove la differenza vale meno 114.579 euro e il verdetto deve dire di restare in affitto; il prezzo massimo con la sua cella di verifica, che deve chiudere a zero; il percorso del tasso a gradini, leggendo il tasso applicato ai mesi di confine, che sul rialzo 2022-2023 in tre gradini deve dare 3,20 fino al dodicesimo mese, poi 4,46, poi 5,72, poi 6,98; e la chiusura del piano nelle due modalità di rimborso, dove quella che riduce la durata non chiude e lascia 87.082 euro di debito, mentre quella che riduce la rata chiude in 300 mesi con la rata a 625,52 euro.

Se Excel resta appeso dopo una prova, cosa che accade quando lo script termina senza rilasciare l'oggetto, la rigenerazione successiva del workbook falla con un errore di permesso sul file. Il processo va chiuso prima di rigenerare.

## Quando rigenerare e riverificare

Dopo ogni modifica a `excel_builder.py` va rigenerato il workbook e rieseguita la verifica. Dopo ogni modifica a `parametri.py` vanno rieseguiti sia il riepilogo sia la verifica, e va aggiornata la data di revisione in testa al file insieme alla riga corrispondente in `docs/fonti.md`.
