# Valutazione di un investimento immobiliare

Strumento locale per decidere se comprare un immobile residenziale in Italia, e a quali condizioni. Genera un workbook Excel con formule vive: si cambia il prezzo o il tasso e tutto si ricalcola, senza rieseguire nulla.

Copre le tre destinazioni possibili dello stesso acquisto, cioe' abitarci, metterlo a reddito, tenerlo come investimento, e le combinazioni che cambiano il conto: prima casa oppure no, acquisto da privato oppure da impresa con IVA, acquisto singolo oppure in quota, nuova costruzione oppure usato. La ristrutturazione come progetto e' fuori perimetro per scelta; la ristrutturazione periodica di fine ciclo resta invece dentro, come costo ricorrente, perche' ignorarla e' il modo piu' comune di sopravvalutare un immobile.

I parametri fiscali sono quelli in vigore al 28 agosto 2026, con le novita' della legge di bilancio 2026.

## Che cosa produce

Il workbook ha venti fogli e si apre sul Cruscotto, che raccoglie i cinque numeri su cui si decide. Quelli in cui si lavora sono Immobile, Mutuo, Locazione, Cash flow e Annunci, dove le celle gialle sono gli input. Quelli che si leggono sono Confronto immobili, Metriche, Confronto affitto, Scenari e Rischio. Il Simulatore mutuo sta a se': serve a provare rimborsi volontari e rialzi di tasso senza toccare l'analisi principale. Quelli che si consultano sono Guida, Parametri, Checklist, Dossier tecnico e Fonti, piu' il piano di ammortamento rata per rata.

Il foglio Immobile calcola le imposte di trasferimento nei quattro casi rilevanti, applica la regola prezzo-valore quando spetta, quantifica il valore economico del bonus prima casa mostrando quanto si pagherebbe senza, e arriva al costo totale dell'operazione e alla cassa che serve davvero.

Il foglio Locazione mette a confronto sullo stesso immobile la cedolare secca a canone libero, il canone concordato, l'IRPEF ordinaria e la locazione breve, riga per riga dal ricavo lordo all'utile netto, passando per sfitto, morosita', condominio, manutenzione, accantonamento per la ristrutturazione, IMU e imposta.

Il foglio Comproprieta' risponde alla domanda su cosa cambia comprando in due, in tre o in N: ripartisce l'operazione per quote, calcola l'imposta di ciascuno secondo il regime che ciascuno sceglie, e riporta le regole di governo della comunione, a partire dal fatto che non serve costituire una societa'.

Il foglio Confronto immobili applica lo stesso modello a ogni annuncio del registro, una riga per immobile, e risponde alla domanda che viene prima di ogni altra, cioe' quale dei candidati meriti una valutazione approfondita.

Il foglio Rischio non chiede quanto rende l'immobile ma quanto puo' andare storto: mille scenari con canone, sfitto, tasso e rivalutazione che variano insieme, piu' l'evento raro di una morosita' grave, e in uscita la distribuzione del cash flow e del patrimonio finale. Il numero che conta e' la coda bassa, cioe' quanto si mette di tasca propria ogni mese nello scenario peggiore su venti. Accanto, un'analisi a tornado dice quale ipotesi muove di piu' il risultato, quindi dove convenga spendere tempo a stimare meglio.

Il foglio Metriche da' rendimento lordo e netto, cap rate, cash on cash, debt service coverage ratio, tasso interno di rendimento e valore attuale netto, tutti calcolati sul costo totale e non sul prezzo. Il foglio Confronto affitto risponde alla domanda su quanto valga comprare rispetto a restare in affitto investendo la differenza. Il foglio Scenari mostra quanto l'esito dipenda dalle assunzioni, che e' la cosa piu' utile che un modello del genere possa fare.

Il foglio Dossier tecnico elenca i cinquantaquattro documenti che un tecnico incaricato chiede all'agenzia o al venditore prima della proposta, divisi in otto famiglie e ciascuno con chi lo rilascia, la norma che lo rende dovuto, che cosa prova, che cosa si rischia se manca e un costo indicativo. Ventuno sono marcati bloccanti, nel senso preciso che senza di essi l'atto e' nullo, il mutuo non si delibera o il costo di regolarizzazione resta ignoto. Il foglio tiene lo stato della raccolta e riporta sul Cruscotto quanti bloccanti mancano ancora.

## Come si usa

```
python tools/valuta.py excel                 genera output/Valutazione-Immobile.xlsx
python tools/valuta.py excel --con-annunci   e vi riversa il registro degli annunci
```

Per uno sguardo rapido senza aprire Excel, ad esempio per scremare una lista di annunci:

```
python tools/valuta.py riepilogo --prezzo 120000 --rendita 450 --mq 55 --mutuo 90000 --tasso 0.032 --durata 25 --canone 500 --canone-concordato 420
```

Il registro degli immobili in valutazione vive in un CSV e sopravvive alla rigenerazione del workbook:

```
python tools/valuta.py annunci aggiungi --link ... --comune "..." --provincia XX --agenzia "..." --mq 75 --prezzo 89000 --obiettivo 82000 --canone 550
python tools/valuta.py annunci elenca
python tools/valuta.py annunci esporta
```

Il tasso del preventivo si confronta con la media di mercato delle nuove erogazioni in Italia, presa dal portale dati della Banca centrale europea, e lo scarto viene tradotto in euro di interessi sull'intera durata:

```
python tools/valuta.py tassi
python tools/valuta.py tassi --tasso 0.032 --mutuo 90000 --durata 25
```

Le quotazioni dell'Osservatorio del mercato immobiliare ancorano i prezzi a un riferimento pubblico:

```
python tools/valuta.py omi scarica --semestre 2018-2
python tools/valuta.py omi cerca --comune "NOME DEL COMUNE"
```

## Le due guide

Sull'acquisto in piu' persone c'e' una scheda dedicata, `docs/comprare-in-piu-persone.md`, che spiega perche' la comunione basta e quando invece una societa' serve.

Chi parte da zero, senza Python installato e senza sapere quali documenti servano, legge `docs/da-zero.md`: sette passi dall'ambiente vuoto alla prima valutazione completa. Chi vuole solo usare il file legge `docs/guida-non-tecnica.md`, che accompagna foglio per foglio spiegando ogni voce in linguaggio comune. Chi interviene sul modello legge `docs/guida-tecnica.md`, che riporta architettura, catena di calcolo e il riferimento di ogni voce con formula, nome definito e norma di riferimento.

## Requisiti

Python 3.11 o superiore con `openpyxl`, che e' l'unica dipendenza obbligatoria. Excel installato serve solo per la verifica automatica del workbook, non per usarlo: il file si apre anche con LibreOffice o Google Sheets, dove pero' la validazione a tendina e la formattazione condizionale possono rendere in modo diverso.

L'importazione automatica degli annunci usa un modello linguistico servito da Ollama sulla rete locale, ed e' facoltativa: senza, l'inserimento resta manuale e tutto il resto funziona.

```
pip install openpyxl
```

## Verifica

```
powershell -NoProfile -ExecutionPolicy Bypass -File tools\verifica-excel.ps1
```

Apre il workbook con Excel, forza il ricalcolo completo e segnala ogni cella in errore, poi stampa i valori chiave. E' il controllo che va eseguito dopo ogni modifica al generatore, perche' la libreria scrive le formule ma non le valuta: senza questo passaggio un riferimento sbagliato resterebbe invisibile.

```
python -m pytest tests
```

I test coprono due livelli. Quelli sul motore di calcolo congelano un caso di riferimento e le regole che cambiano piu' spesso, come gli scaglioni IRPEF e i moltiplicatori catastali. Quelli sul generatore verificano la struttura del workbook e in particolare il contratto piu' fragile del progetto, cioe' la corrispondenza posizionale fra le colonne del foglio Annunci e l'ordine con cui il registro le scrive: sono due elenchi in due file diversi, e se divergono l'esportazione mette i prezzi nella colonna delle note senza che nulla protesti.

Le stesse regole sono poi implementate due volte, in Python e in formule Excel. Confrontare le due uscite sullo stesso caso e' il controllo che intercetta l'errore di trascrizione, che nei fogli di calcolo e' il piu' frequente e il piu' difficile da vedere.

## Sull'attendibilita' dei numeri

Ogni parametro fiscale porta la fonte accanto, nel foglio Parametri del workbook e in `src/immobiliare/parametri.py`. Il registro completo e' in `docs/fonti.md`, e per ogni fonte dichiara tre cose: cosa fornisce, dove atterra nel progetto fra campo di parametro, funzione, cella del workbook e voce di checklist, e con quale grado di verifica. Le fonti lette direttamente sono distinte da quelle solo segnalate, nessun parametro del modello poggia su una fonte non verificata, e le lacune note sono elencate in fondo invece di essere taciute.

Due voci vanno sempre sostituite con il dato reale prima di prendere sul serio un risultato: l'aliquota IMU, che va letta nella delibera del Comune dell'anno in corso e non nel valore base di legge, e le spese condominiali, che vanno lette nel consuntivo degli ultimi due esercizi e non nella stima dell'agenzia.

Questo e' uno strumento di analisi personale, non una consulenza fiscale, legale o finanziaria. Le aliquote cambiano con ogni legge di bilancio, e le posizioni soggettive vanno confermate da un notaio e da un commercialista.

## Impostazione metodologica

Il debito principale e' verso i fogli di calcolo pubblicati da Paolo Coletti, da cui viene l'impostazione dell'orizzonte lungo con lo sfitto fra un contratto e l'altro, la ristrutturazione periodica trattata come costo ricorrente e il confronto finale con un portafoglio alternativo. Quei fogli sono del 2022 per la parte immobiliare: il metodo regge, le aliquote no, ed e' la ragione per cui qui la parte fiscale e' stata ricostruita da capo sulle fonti del 2026.

Sulla parte legale e urbanistica il riferimento e' il lavoro di divulgazione di Carlo Pagliai, in particolare sulla distinzione fra conformita' catastale e conformita' urbanistica e sugli effetti del decreto Salva Casa sullo stato legittimo e sulle tolleranze costruttive.
