---
generated-from-commit: da assegnare al primo commit
generated-from-branch: main
generated-date: 2026-08-28
covers-paths:
  - tools/verifica-excel.ps1
  - tests/**
last-verified-commit: da assegnare al primo commit
---

# Verifica

## I quattro livelli

Il primo livello e' la verifica formale del workbook. Lo script `tools/verifica-excel.ps1` lo apre con Excel via automazione COM, forza un ricalcolo completo con `CalculateFullRebuild`, raccoglie con `SpecialCells` tutte le celle che valutano a errore e le elenca con la formula che le ha prodotte, poi stampa i valori chiave e le sezioni di sintesi. Termina con codice diverso da zero se trova errori, quindi e' usabile come cancello prima di un commit.

Due dettagli di ambiente che vanno ricordati perche' fanno perdere tempo. L'automazione COM di Excel espone i metodi nella lingua di installazione, e con una console italiana il late binding di PowerShell non risolve `Open`: la chiamata va fatta con `InvokeMember` passando esplicitamente la cultura `en-US`. E il messaggio di errore che dice che il metodo non esiste e' lo stesso che si ottiene quando il metodo esiste ma il file e' malformato, per cui va isolata la causa provando ad aprire un file banale.

Il secondo livello e' la bisezione sui fogli, quando il workbook non si apre. Si generano workbook progressivi con un foglio in piu' alla volta e si prova ad aprirli tutti: il primo che fallisce identifica il foglio responsabile. E' cosi' che e' stato trovato l'elemento di validazione vuoto sul foglio Mutuo.

Il terzo livello sono i test automatici, in due file. `tests/test_calcoli.py` copre il motore di dominio e congela il caso di riferimento. `tests/test_workbook.py` copre la struttura del workbook generato: l'elenco dei fogli, la presenza dei nomi definiti essenziali, e soprattutto la corrispondenza posizionale fra le colonne del foglio Annunci e l'ordine con cui `annunci.esporta_in_excel` le scrive, che e' il contratto piu' fragile del progetto perche' vive in due file diversi e nessun tipo lo protegge. Quel test esporta un annuncio noto e rilegge le celle una per una, e ha gia' ripagato il costo trovando un difetto reale: `openpyxl` ignora l'assegnazione quando si passa `value=None` a `cell()`, quindi un campo azzerato non ripuliva la cella e l'annuncio esportato ereditava in silenzio il dato di quello che occupava prima quella riga.

Allo stesso genere appartiene il test sul foglio Dossier tecnico, che verifica che ogni riga porti uno dei tre soli valori ammessi nella colonna del peso. La ragione e' che il contatore dei documenti bloccanti e' un `COUNTIFS` su stringa esatta: un valore scritto anche solo con l'iniziale maiuscola non solleverebbe alcun errore, sparirebbe dal conteggio, e il Cruscotto direbbe che non manca nessun documento bloccante. E' il modello di difetto contro cui vale la pena scrivere un test, cioe' quello che produce un numero plausibile invece di un errore.

Il quarto livello, e il piu' importante per la correttezza sostanziale, e' il confronto fra le due implementazioni. Lo stesso caso passa per il motore Python con `python tools/valuta.py riepilogo` e per il workbook, e i risultati devono coincidere. Sul caso di riferimento coincidono su costo totale, esborso, imposte, rata, reddito operativo netto, utile netto, rendimento netto, cap rate, cash on cash, debt service coverage ratio e cash flow.

## Il caso di riferimento

Immobile di categoria A/3, cinquantacinque metri quadri, rendita catastale di quattrocentocinquanta euro, prezzo trattato centoventimila, acquisto da privato con agevolazione prima casa e opzione prezzo-valore, mutuo di novantamila a tasso fisso del tre virgola due per cento su venticinque anni, canone atteso di cinquecento euro al mese in cedolare secca.

I valori attesi sono un valore catastale di 51.975 euro, imposte di trasferimento per 1.140, costi accessori per 11.557 pari al 9,63 per cento del prezzo, costo totale di 131.557, esborso iniziale di 41.557, rata mensile di 436,21, reddito operativo netto di 1.805, utile netto di 684, rendimento netto dello 0,52 per cento, cap rate dell'1,37, cash on cash del meno 10,95, debt service coverage ratio di 0,34 e cash flow annuo di meno 4.550 euro.

Se un cambiamento al generatore sposta uno di questi numeri senza che sia stata cambiata la regola corrispondente, e' una regressione.

## Verifiche di dominio da tenere presenti

L'IRPEF lorda su trentamila euro di imponibile deve dare 7.100 euro con gli scaglioni 2026, cioe' ventotto mila al ventitre' per cento piu' duemila al trentatre'. E' il controllo piu' rapido per accorgersi che gli scaglioni sono rimasti a un'annualita' precedente.

L'imposta di registro non puo' mai scendere sotto il minimo di legge, il che diventa vincolante su immobili con rendita catastale bassa: la formula usa un massimo e non una semplice moltiplicazione.

La detrazione degli interessi deve azzerarsi quando l'immobile non e' abitazione principale, e il massimale deve scalare con la quota di acquisto.

Il prezzo-valore non si applica quando si compra da impresa con IVA, perche' e' una regola dell'imposta di registro: se il calcolo lo applicasse comunque, l'imposta risulterebbe sistematicamente sottostimata sugli acquisti da costruttore.

Il moltiplicatore catastale deve seguire l'agevolazione effettivamente applicabile e non quella richiesta. Sulle categorie A/1, A/8 e A/9 l'agevolazione non spetta mai, quindi il moltiplicatore torna a centoventi insieme all'aliquota del nove per cento: usare centodieci perche' l'acquirente ha chiesto la prima casa sottostima l'imposta di circa un dodicesimo. Era un difetto reale, presente sia in Python sia nelle formule, trovato dal test sulla categoria di lusso.

## Quando rigenerare e riverificare

Dopo ogni modifica a `excel_builder.py` va rigenerato il workbook e rieseguita la verifica. Dopo ogni modifica a `parametri.py` vanno rieseguiti sia il riepilogo sia la verifica, e va aggiornata la data di revisione in testa al file insieme alla riga corrispondente in `docs/fonti.md`.
