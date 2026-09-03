# Guida per chi compra insieme

> Guida d'uso per una persona che non ha il progetto sulla macchina e deve capire il workbook e le sue conclusioni. Copre le tre domande a cui lo strumento risponde, il percorso in cinque passi, i cinque colori delle celle, i venti fogli con quali riguardano chi, e tutte e cinquantuno le celle di input spiegate una per una. Chiude con un giro completo su un immobile reale e con i limiti dichiarati.

Le voci di questa guida non sono scritte a memoria: sono estratte dal workbook generato, leggendo etichetta, colore di riempimento e nota di ogni cella di input. È completa per costruzione, e quando si aggiunge una cella al generatore va rigenerata dalla stessa fonte.

## A che domanda risponde lo strumento

A tre, e conviene sapere quali sono perché tutto il resto ne discende.

**Quanta cassa serve davvero per chiudere.** Non il prezzo: il prezzo più imposte di trasferimento, notaio, provvigione e oneri del mutuo. Su un immobile da centoventimila euro il costo reale sta attorno ai centotrentaduemila, e quei dodicimila non tornano alla rivendita.

**Quanto rende al netto di tutto,** e come si confronta con il non comprarlo. Fra il rendimento lordo che si legge negli annunci e il rendimento netto si perdono di norma due punti e mezzo. Chi promette un netto vicino al lordo sta contando male, o non sta contando le stesse cose.

**Quali verifiche vanno chiuse prima di firmare.** Una proposta accettata è già un contratto: le verifiche si chiudono prima, oppure diventano condizioni scritte nella proposta.

Quello che non fa: non è una consulenza fiscale, legale o finanziaria, e non sostituisce il notaio, il commercialista e il tecnico. Serve a sapere quali domande fare loro, e a non pagare per farsi dire un numero che si può calcolare da soli.

## Il percorso, in cinque passi

I primi tre si fanno da terminale, il quarto nel foglio Excel, il quinto in agenzia. L'ordine conta: saltare il primo significa valutare a fondo un immobile che una tabella avrebbe scartato in dieci secondi.

**Primo, registrare tutto quello che si guarda.** Ogni immobile entra in un registro, anche con il solo link. Serve a non rivalutare due volte la stessa casa e a non perdere quella vista tre settimane prima.

```
python tools/valuta.py annunci aggiungi --link "https://..." --comune "..." --mq 75 --prezzo 89000
```

**Secondo, agganciare la zona e guardare la graduatoria.** Le quotazioni dell'Osservatorio del mercato immobiliare dicono fra quali prezzi si muove quella zona per quella tipologia. La graduatoria ordina per scarto sulla zona e non per prezzo, perché fra immobili di taglia diversa il prezzo non dice niente.

```
python tools/valuta.py omi zone --comune "Civitanova Marche"
python tools/valuta.py annunci omi --id house_1
python tools/valuta.py annunci confronta
```

**Terzo, chiedere i dati che mancano.** Un comando dice, immobile per immobile, che cosa manca e che cosa quel dato blocca. Su quasi tutti gli annunci mancano le stesse tre cose, e si ottengono con una mail sola: rendita catastale e categoria dalla visura, superficie calpestabile oltre a quella commerciale, consuntivo condominiale degli ultimi due esercizi con il verbale dell'ultima assemblea.

```
python tools/valuta.py annunci mancanti
```

**Quarto, generare il foglio dell'immobile e compilarlo.** Il workbook nasce già compilato con i dati del registro. Restano da mettere a mano le tre cose che il registro non porta: aliquota IMU dalla delibera del Comune, importo e tasso dal preventivo della banca, e la verifica che le spese condominiali vengano dal consuntivo e non dalla stima dell'agenzia.

```
python tools/valuta.py excel --con-annunci --da-annuncio house_1
```

**Quinto, leggere, decidere, e portare una pagina in agenzia.** Si legge il Cruscotto, poi lo scenario sfavorevole. Se l'operazione regge, un comando produce una pagina con i quattro numeri della trattativa e l'elenco delle cose da chiedere.

```
python tools/valuta.py scheda --id house_1 --mutuo 65600 --imu 0.0106
```

## I colori delle celle

È la cosa da imparare per prima, e l'unica indispensabile. La legenda, con i colori mostrati e non descritti, sta in testa al primo foglio del workbook.

| Colore | Che cosa significa |
|---|---|
| Gialla | Ci scrivi tu, un numero o un testo. Sono le uniche celle da compilare, e sono poche per foglio. |
| Azzurra | Ci scegli da un elenco: clicca la cella e a destra compare una freccia. Un valore scritto a mano fuori dall'elenco viene rifiutato, ed è voluto. |
| Grigia | La calcola il foglio. Non ci si scrive: sovrascriverla rompe il calcolo in silenzio, cioè senza nessun messaggio di errore. |
| Verde | Risultato di sintesi. È quello che sei venuto a leggere, e viene sempre da celle gialle e azzurre compilate altrove. |
| Rossa | Attenzione. Un valore ha superato una soglia oltre la quale è un problema, oppure un controllo di plausibilità non è superato. |

Ogni foglio, in riga tre, ha una fascia che dice in una frase se lì si scrive o si legge, quando conviene aprirlo e che cosa ne esce. Se la fascia è gialla si compila, se è grigia si legge e non si tocca niente. A sinistra, il collegamento che riporta all'indice.

## I venti fogli, e quali riguardano chi

Dieci accettano input, dieci si leggono. Ma dei dieci che accettano input solo tre servono sempre: gli altri dipendono da come si compra e da dove si è arrivati nella trattativa.

| Foglio | Che cosa si fa | Quando serve |
|---|---|---|
| Immobile | si compila | Sempre. È il foglio da cui parte tutto. |
| Mutuo | si compila | Sempre, anche solo per vedere il caso senza mutuo mettendo importo zero. |
| Locazione | si compila | Solo se l'immobile si mette a reddito. |
| Comproprietà | si compila | Solo se si compra in più di uno. |
| Scenari | si compila e si legge | Prima di decidere, mai dopo. Qui si mettono le tre ipotesi e si guarda quella cattiva. |
| Simulatore mutuo | si compila e si legge | Prima di firmare un mutuo, soprattutto se è a tasso variabile. |
| Asta | si compila e si legge | Solo per le vendite giudiziarie, dove le regole sono altre. |
| Checklist | si spunta | Dal momento in cui si passa dalla valutazione alla proposta. |
| Dossier tecnico | si spunta | Prima della proposta, non dopo. Sono le carte da farsi consegnare. |
| Annunci | si compila | Da subito. Di norma lo riempie il comando, non la mano. |
| Cruscotto | si legge | Sempre, per primo e per ultimo. I numeri che decidono, con le soglie accanto. |
| Metriche | si legge | Tutti gli indicatori, compreso il rendimento reale al netto dell'inflazione. |
| Ammortamento | si legge | Il piano rata per rata, fino a quarant'anni. |
| Cash flow | si legge | La proiezione anno per anno, con l'uscita finale. |
| Confronto affitto | si legge | Solo se è casa propria: comprare oppure affittare e investire la differenza. |
| Rischio | si legge | Mille scenari, e la probabilità che il cash flow sia negativo. |
| Confronto immobili | si legge | Tutti gli annunci in fila con lo stesso modello. Si popola da sé. |
| Parametri | si consulta | Ogni aliquota con la fonte accanto. Si tocca solo all'aggiornamento fiscale. |
| Fonti | si consulta | Da dove viene ogni dato, con il collegamento all'istituzione. |
| Guida | si legge | È l'indice: primo foglio, con un collegamento a tutti gli altri. |

## Foglio Immobile, diciotto celle

È il foglio da cui parte tutto, e le sue quattro celle più importanti non stanno nell'annuncio: rendita catastale, categoria, e le due scelte sul regime di acquisto.

### Identificazione

Le prime cinque servono a ritrovare le cose, non al calcolo, con l'eccezione della superficie.

| Cella | Che cosa scrivere | Perché serve |
|---|---|---|
| Riferimento interno (gialla) | Lo stesso identificativo del registro, per esempio `house_1`. | Lega il foglio alla riga del registro. Se non combaciano, fra un mese non si sa più di quale casa si stia parlando. |
| Comune (gialla) | Il Comune dell'immobile. | Serve a ritrovare la delibera IMU e la zona OMI di riferimento. Sono i due dati che cambiano il conto e che dipendono dal Comune. |
| Indirizzo (gialla) | Via e numero civico. | Serve a scegliere la zona OMI giusta, che è descritta per vie e quartieri. |
| Link annuncio (gialla) | L'indirizzo della pagina. | Per rileggere l'annuncio quando i portali lo rimuovono. Capita prima di quanto si pensi. |
| Superficie commerciale (gialla) | Metri quadri commerciali, non calpestabili. | È la base del prezzo al metro quadro di mercato, e le quotazioni OMI sono espresse sulla stessa base. Confrontare la calpestabile con quotazioni commerciali sbaglia del quindici-venti per cento. |

### Dati catastali

Dalla visura, non dall'annuncio.

| Cella | Che cosa scrivere | Perché serve |
|---|---|---|
| Categoria catastale (azzurra) | Si sceglie dall'elenco: da A/1 a A/11. | A/1, A/8 e A/9 sono escluse dall'agevolazione prima casa e scontano IVA al ventidue per cento. Decide anche il moltiplicatore del valore catastale. |
| Rendita catastale (gialla) | L'importo in euro che si legge nella visura. | È la cella più importante del foglio. Serve al prezzo-valore, che è la leva fiscale più grossa dell'operazione, e all'IMU. Senza, le imposte si calcolano sul prezzo intero e si paga di più. |

### Il prezzo

| Cella | Che cosa scrivere | Perché serve |
|---|---|---|
| Prezzo richiesto (gialla) | Quello scritto nell'annuncio. | Resta come riferimento, per sapere di quanto si è scesi. |
| Prezzo trattato, da mettere in proposta (gialla) | Il prezzo su cui si vuole chiudere. | È il prezzo su cui si costruisce tutta l'analisi. Tutti i numeri del workbook si riferiscono a questo, non al richiesto. |

### Il regime di acquisto

Quattro scelte che valgono migliaia di euro.

| Cella | Che cosa scegliere | Perché serve |
|---|---|---|
| Venditore impresa con IVA (azzurra) | SI oppure NO. | SI se si compra da impresa costruttrice entro cinque anni dall'ultimazione, o con opzione per l'imponibilità. Cambia tutto: l'IVA colpisce il prezzo intero, l'imposta di registro con il prezzo-valore colpisce il valore catastale. |
| Nuova costruzione (azzurra) | SI oppure NO. | Attiva le verifiche del d.lgs. 122/2005 nella checklist: fideiussione sugli acconti e polizza decennale postuma. Sono tutele di legge che spesso non vengono offerte se non si chiedono. |
| Agevolazione prima casa (azzurra) | SI oppure NO. | Richiede residenza nel Comune entro diciotto mesi e assenza di altra prima casa agevolata, salvo rivendita entro due anni. Vale qualche migliaio di euro, e si consuma: non si può riusare su un acquisto futuro finché non si rivende. |
| Opzione prezzo-valore (azzurra) | SI oppure NO. | Da chiedere al notaio in atto: non è automatica. Fa calcolare l'imposta di registro sul valore catastale invece che sul prezzo. Non si applica comprando da impresa con IVA. |

### Chi compra, e per farne cosa

| Cella | Che cosa scrivere | Perché serve |
|---|---|---|
| Quota di acquisto (gialla) | 1 se si compra da soli, 0,5 se si compra in due. | Incide sul massimale della detrazione degli interessi, che è riferito all'immobile e si divide fra i cointestatari. Comprando in due, ciascuno detrae al massimo su duemila euro di interessi, non su quattromila. |
| Destinato ad abitazione principale (azzurra) | SI se ci si va a vivere, NO se si compra per affittarlo. | SI abilita la detrazione degli interessi e l'esenzione IMU. È la scelta che cambia più voci contemporaneamente in tutto il workbook. |

### I costi accessori

Le tre celle che nessun annuncio dichiara.

| Cella | Che cosa scrivere | Perché serve |
|---|---|---|
| Provvigione di agenzia (gialla) | Percentuale sul prezzo, al netto di IVA. Tipicamente 3 per cento. | Zero se si tratta direttamente col privato. Con l'IVA al ventidue diventa il 3,66 per cento effettivo, ed è la voce accessoria più grossa dopo le imposte. |
| Notaio, atto di compravendita (gialla) | L'onorario preventivato. | Con il prezzo-valore l'onorario scende del trenta per cento per legge. Chiedere sempre due o tre preventivi scritti: la differenza fra studi è reale. |
| Altri costi (gialla) | Tutto il resto che si paga al rogito o subito dopo. | Visure, relazione notarile preliminare, tecnico di parte, allacci, accatastamento, arredo minimo. È la cella che si lascia a zero e che poi costa duemila euro. |

## Foglio Mutuo, dieci celle

Tutte vengono dal preventivo della banca, e vale la pena farsi dare il PIES, il prospetto standard europeo: è gratuito per legge ed è l'unico modo di confrontare due offerte sulla stessa base.

| Cella | Che cosa scrivere | Perché serve |
|---|---|---|
| Importo del mutuo (gialla) | Il capitale erogato. | Sopra l'ottanta per cento del valore servono garanzie in più e le condizioni peggiorano. Mettere zero per vedere il caso senza mutuo. |
| Tasso annuo nominale (gialla) | Il TAN del preventivo, in forma decimale: 0,032 per il 3,2 per cento. | Per un variabile si mette Euribor più spread e si usa il foglio Simulatore. Un comando dice se il preventivo è in linea col mercato. |
| Durata in anni (gialla) | Gli anni del piano. | Allungare abbassa la rata e alza gli interessi totali. Il foglio mostra entrambi gli effetti, perché la scelta è fra due cose diverse. |
| Spese di istruttoria (gialla) | Quanto la banca chiede per l'istruttoria. | Spesso azzerate nelle offerte commerciali: verificare sul foglio informativo e non sulla pubblicità. |
| Perizia (gialla) | Il costo della perizia della banca. | Si paga anche se il mutuo non viene poi erogato, in diversi contratti. |
| Notaio, atto di mutuo (gialla) | L'onorario del secondo atto. | È una fattura distinta da quella della compravendita, e se è prima casa è detraibile fra gli oneri accessori del mutuo. In molti non la portano in detrazione. |
| Polizza incendio, forma del premio (azzurra) | `annuo` oppure `unico`. | Le banche propongono spesso il premio unico anticipato per tutta la durata, finanziandolo dentro il mutuo: così ci si pagano sopra anche gli interessi. Il foglio mostra la differenza. |
| Polizza incendio e scoppio, importo (gialla) | Il premio, annuo o totale secondo la scelta sopra. | È obbligatoria, ma si può portarne una propria equivalente presa altrove, e la banca deve accettarla. Ci sono sessanta giorni per disdire quella venduta con il mutuo. |
| Polizza vita o impiego, premio annuo (gialla) | Zero se non la si prende. | È facoltativa per legge: la banca non può subordinare la concessione del credito alla sua sottoscrizione. Se insiste, è una pratica scorretta e va contestata. |
| Reddito netto mensile del richiedente (gialla) | Il netto in busta. | Serve al rapporto rata-reddito, che diventa rosso sopra il trentacinque per cento perché è lì che le banche si fermano. |

## Foglio Locazione, diciassette celle

Solo se l'immobile si mette a reddito. Confronta quattro modi di tassare lo stesso affitto, e il risultato dipende anche dalla posizione fiscale personale di chi compra: per due persone diverse il regime migliore può non essere lo stesso.

### Quanto entra

| Cella | Che cosa scrivere | Perché serve |
|---|---|---|
| Canone mensile atteso, canone libero (gialla) | Quello che si pensa di ottenere. | Da verificare sulle quotazioni OMI di locazione della zona e sugli annunci di affitto comparabili, non a sentimento. |
| Canone mensile a canone concordato (gialla) | Quello dell'accordo territoriale. | Deriva dall'accordo del Comune, con attestazione di un'associazione firmataria. Di norma inferiore del dieci-venti per cento al libero, in cambio di un'aliquota più bassa. |
| Ricavi lordi annui da locazione breve (gialla) | Tariffa media per notte per le notti occupate attese. | Va stimata sui dati reali della zona su tutto l'anno, non sul picco di agosto. È l'errore più comune di chi valuta il breve. |
| Mesi di sfitto attesi all'anno (gialla) | Un mese è l'assunzione prudenziale standard. | Non è pessimismo: fra un contratto e l'altro il vuoto reale è di norma più lungo. Metterlo a zero è la prima cosa che falsa un rendimento. |
| Accantonamento per morosità (gialla) | Tre per cento è un riferimento. | Uno sfratto per morosità richiede circa un anno e mezzo, durante il quale il canone non entra ma le imposte si pagano lo stesso. |

### Quanto esce

Le prime due sono le celle da non lasciare mai al valore predefinito.

| Cella | Che cosa scrivere | Perché serve |
|---|---|---|
| Spese condominiali annue totali (gialla) | Dal consuntivo, non dalla stima dell'agenzia. | Chiedere anche il verbale dell'ultima assemblea: i lavori già deliberati e non ancora fatti sono un costo tuo che arriva dopo il rogito, e non compare in nessun annuncio. |
| Aliquota IMU deliberata dal Comune (gialla) | Dalla delibera comunale dell'anno in corso. | Non dal valore base di legge. I Comuni possono azzerarla o portarla all'1,06 per cento: sul valore base l'IMU stimata può sbagliare di un quarto, ogni anno per tutta la durata del possesso. |
| Quota a carico del proprietario (gialla) | Quaranta per cento è un riferimento. | La ripartizione fra proprietario e inquilino segue la tabella degli oneri accessori: la straordinaria al proprietario, l'ordinaria all'inquilino. |
| Manutenzione ordinaria, quota del valore (gialla) | Un per cento del valore l'anno. | È la regola empirica, e copre caldaia, infissi, elettrodomestici e tinteggiature fra un inquilino e l'altro. |
| Assicurazione fabbricato (gialla) | Il premio annuo. | Esiste anche senza mutuo, e a zero il conto economico è ottimistico. |
| Gestione affidata a terzi, quota del canone (gialla) | Zero se si gestisce da soli. | Un property manager costa il dieci per cento sul lungo periodo, il venti sul breve. |
| Costi variabili della locazione breve (gialla) | Quindici per cento è un riferimento. | Pulizie, biancheria, utenze, commissioni dei portali, consumabili. Sono calcolati sui ricavi e non sull'utile. |

### Il proprio tempo, e la propria posizione fiscale

| Cella | Che cosa scrivere | Perché serve |
|---|---|---|
| Aliquota marginale IRPEF del contribuente (gialla) | Lo scaglione in cui cade l'ultimo euro di reddito. | Ventitré per cento fino a ventottomila euro, trentatré fino a cinquantamila, quarantatré oltre. Serve solo al confronto con il regime ordinario, ma è la cella che rende il confronto personale e non generico. |
| Ore all'anno dedicate alla gestione (gialla) | Trenta è l'ordine di grandezza di una locazione lunga che va liscia. | Una locazione breve gestita in proprio sta su un altro ordine di grandezza, dalle duecento ore in su. |
| Valore di un'ora del proprio tempo (gialla) | Zero per escludere la voce dal conto. | Un riferimento onesto è il proprio costo orario netto, oppure quanto si pagherebbe qualcuno per farlo al posto proprio. |
| Moltiplicatore del tempo per la locazione breve (gialla) | Sei volte il tempo della locazione lunga. | La locazione breve non è un investimento passivo: è più vicina a un mestiere, e va confrontata con gli altri regimi tenendone conto. |
| Regime scelto per la proiezione (azzurra) | Uno fra `cedolare_libero`, `cedolare_concordato`, `irpef_ordinario`, `breve`. | Alimenta il foglio Cash flow e quindi tutte le metriche. Si compila dopo aver guardato il confronto fra i quattro, non prima. |

### Una cosa che l'aliquota non dice

La cedolare secca conviene quasi sempre guardando l'aliquota. In cambio, chi la opta rinuncia all'aggiornamento ISTAT del canone per la durata dell'opzione. Su un orizzonte lungo il canone perde in termini reali tutta l'inflazione, e il foglio Metriche calcola quanto vale quella rinuncia: sul caso di esempio, venticinquemila euro di valore attuale contro dodicimilasettecento di risparmio d'imposta. Non è un verdetto, perché l'opzione si riconsidera a ogni rinnovo, ma è un confronto che quasi nessuno fa, perché il risparmio si vede in dichiarazione e il canone non chiesto non si vede mai.

## Foglio Comproprietà

È il foglio che riguarda direttamente un acquisto in due. Non è un elenco di celle ma una tabella: una riga per acquirente, fino a otto.

| Colonna | Che cosa scrivere | Perché serve |
|---|---|---|
| Quota (gialla) | La quota di ciascuno, come frazione: 0,5 e 0,5. | Il foglio controlla che la somma faccia esattamente uno e lo dice se non torna. Le quote vanno in atto e determinano tutto il resto. |
| Aliquota IRPEF (gialla) | Lo scaglione marginale di ciascuno. | Sul fisco ciascuno fa storia a sé: il canone si dichiara pro quota e ognuno può scegliere il proprio regime. Con due aliquote diverse, il regime migliore può essere diverso per i due. |
| Regime fiscale (azzurra) | Il regime scelto da quell'acquirente. | Sono scelte indipendenti, e il foglio le tiene separate invece di assumere che coincidano. |
| Prima casa (azzurra) | SI oppure NO, per ciascuno. | L'agevolazione è personale: uno può averla e l'altro no, e in quel caso si applica pro quota. È una delle cose che sorprende di più al rogito. |

### Le tre cose da mettere per iscritto prima, non dopo

Il foglio le elenca, e valgono più di qualunque calcolo.

Chi paga cosa e in che proporzione, perché la quota in atto e i versamenti effettivi possono divergere e allora nasce un credito fra i due. Che cosa succede se uno vuole uscire: senza un patto, ciascuno può disporre della propria quota e cedere a chiunque, e chi resta si trova un estraneo in comproprietà. Come si decide sui lavori, perché le maggioranze si contano per valore delle quote e con due al cinquanta per cento non esiste maggioranza: ogni disaccordo si risolve solo davanti a un giudice, o non si risolve.

Non serve costituire una società. Serve un accordo scritto, e il momento per farlo è prima della proposta. La materia è distesa in `comprare-in-piu-persone.md`.

## I numeri da leggere, e le loro soglie

Sono cinque sul Cruscotto, e ognuno porta accanto la soglia oltre la quale è un problema. Un indicatore senza soglia si guarda e non si usa.

| Numero | Che cosa misura | Soglia |
|---|---|---|
| Rendimento netto | L'utile dopo tutti i costi e tutte le imposte, diviso il costo totale dell'operazione. È il numero per decidere. | Sotto il costo opportunità del proprio capitale, l'operazione non ha senso rispetto alle alternative. |
| Cash flow mensile | Quanto entra o esce dalla tasca ogni mese, rata compresa. | Se è negativo va sostenuto ogni mese per anni. La domanda non è se l'operazione è buona, è se te lo puoi permettere. |
| DSCR | Quante volte il reddito dell'immobile copre la rata. | Sotto 1 il reddito non copre la rata e la differenza esce di tasca propria. |
| Incidenza dei costi | Quanto pesano imposte, notaio, provvigione e oneri sul prezzo. | Sopra il dieci per cento diventa rossa. Sui piccoli tagli i costi fissi pesano di più. |
| Controlli non superati | Quanti input il modello considera non ancora attendibili. | Deve andare a zero. Un controllo non superato non è un errore del modello: è un input che non è ancora un dato. |

E poi, prima di firmare, due contatori che non sono numeri di rendimento ma di lavoro: verifiche ancora aperte, dal foglio Checklist, e documenti bloccanti ancora da avere, dal Dossier tecnico. Sono le carte la cui assenza rende nullo l'atto, blocca il mutuo, o lascia ignoto il costo di una regolarizzazione. Vanno a zero prima della proposta, non prima del rogito.

## Un immobile vero, dall'inizio alla fine

Trilocale di settantacinque metri quadri a Civitanova Marche, in via Martiri di Belfiore. Richiesta ottantanovemila euro, già locato e arredato, primo e ultimo piano. È l'immobile `house_1` del registro, e lo si usa qui perché è l'unico dei quattordici a registro che ha un canone: il canone è il dato che sblocca il rendimento.

Ipotesi dichiarate: prezzo trattato ottantaduemila euro, mutuo di sessantacinquemilaseicento all'ottanta per cento del prezzo, tasso 3,2 per cento su venticinque anni, canone cinquecentocinquanta euro al mese, cedolare secca. L'aliquota IMU è quella base di legge perché la delibera del Comune non è ancora stata letta: è uno dei quattro controlli che il foglio segnala come non superati.

| Grandezza | Valore | Lettura |
|---|---|---|
| Costo reale | 90.705 € | contro 82.000 di prezzo: 10,6 per cento di costi accessori |
| Cassa al rogito | 25.105 € | da avere sul conto il giorno dell'atto |
| Rendimento netto | 3,23 % | nominale; 1,21 per cento reale, al netto del due di inflazione |
| Cap rate | 4,59 % | il rendimento dell'immobile, prima del debito e delle imposte |
| Cash on cash | −3,52 % | sul capitale proprio: la cassa del primo anno è negativa |
| Cash flow annuo | −883 € | cioè settantaquattro euro al mese di tasca propria |
| DSCR | 1,09 | sopra uno: il reddito operativo copre la rata |
| Prezzo massimo | 70.524 € | per rendere il quattro per cento netto: sconto da ottenere 11.476 |

### Come si legge questa tabella

C'è una cosa che sembra una contraddizione e non lo è, e capirla è capire come funziona la leva. Il cap rate è 4,59 per cento e il denaro costa 3,2: l'immobile rende più del mutuo, quindi il debito dovrebbe aiutare. E invece il cash on cash è negativo e ogni mese escono settantaquattro euro.

Le due cose convivono perché misurano periodi diversi. Il cap rate confronta il reddito con il costo del denaro, cioè i soli interessi. La rata, invece, contiene anche la quota capitale: quei settantaquattro euro al mese non sono una perdita, sono risparmio forzato che va a ridurre il debito e che alla rivendita si ritrova. Il DSCR a 1,09 dice la stessa cosa dall'altro lato: il reddito operativo copre la rata, e il cash flow diventa negativo solo dopo aver pagato l'imposta sul canone.

La lettura pratica è quindi che l'operazione è sana ma assorbe cassa nei primi anni, e la domanda non è se conviene ma se quei settantaquattro euro al mese si possono sostenere per anni anche in un anno in cui l'immobile resta vuoto tre mesi invece di uno. A quella domanda risponde il foglio Scenari, e va guardata prima di fare la proposta.

### Perché lo scarto sulla zona qui non dice niente

La scheda riporta uno scarto di meno 43,5 per cento sulla quotazione di zona, e sembra un affare enorme. Non lo è: la zona OMI di questo immobile non è ancora stata assegnata, e in sua assenza il modello usa la forbice dell'intero Comune, che va da novecento a tremilatrecento euro il metro quadro. Su un intervallo così largo lo scarto è quasi privo di significato. Assegnare la zona richiede di guardare dove cade l'indirizzo sulla mappa delle zone omogenee, e via Martiri di Belfiore non compare in nessuna delle tredici descrizioni: va determinata, non indovinata.

### Che cosa manca, e che cosa cambierebbe

La rendita catastale: senza, il prezzo-valore non si applica e le imposte sono calcolate sul prezzo intero, cioè millesettecentoquaranta euro invece dei circa millecento che si pagherebbero con l'opzione. È la voce che, arrivando, abbassa di più il costo.

La zona OMI, che rende leggibile lo scarto, oggi illeggibile. Le spese condominiali, oggi a zero, quindi il reddito operativo netto di quattromilacentosessantacinque euro è sovrastimato di tutto il loro importo: su un trilocale in condominio parliamo di sette-novecento euro l'anno, che si mangiano un quinto del reddito operativo. La categoria catastale, che decide il moltiplicatore del valore catastale e l'eventuale esclusione dall'agevolazione.

Sono quattro dati, si ottengono con una mail e una visura, e finché mancano ogni numero qui sopra va letto come provvisorio. La scheda di trattativa lo dichiara in testa, in giallo, invece di far finta di essere completa.

## Che cosa il modello non sa

Sono limiti dichiarati, non difetti scoperti: ognuno è scritto anche nella cella del foglio che lo produce.

Non pesa il rischio. Un immobile è un singolo bene, in una singola via, di un singolo Comune, comprato in un singolo momento del ciclo. Porta insieme rischio di tempistica, di ciclo economico, di tasso e di localizzazione, e non si vende in tre giorni. Un portafoglio diversificato con lo stesso rendimento atteso non è la stessa cosa, e la differenza va aggiunta a mano nel giudizio.

Non prezza il lavoro, oltre alla voce del tempo che si può compilare a mano. Nella locazione breve la componente di lavoro è tale che l'operazione somiglia più a un mestiere che a un investimento.

Assume le variabili indipendenti nella simulazione, mentre nella realtà tassi, prezzi, sfitto e morosità si muovono insieme. Introdurre una correlazione richiederebbe di stimare una matrice che nessuno ha, e sostituirebbe un'assunzione dichiarata con una nascosta.

Non modella la ristrutturazione come progetto, per scelta di perimetro. Resta dentro il solo accantonamento per il rifacimento di fine ciclo, perché un immobile che si tiene quarant'anni va rifatto almeno una volta e ignorarlo falsa il rendimento.

E soprattutto, le aliquote implementate sono quelle vigenti alla data di revisione dichiarata nel foglio Parametri e cambiano con ogni legge di bilancio. Prima di firmare, le posizioni soggettive vanno confermate da un notaio e da un commercialista, e la conformità urbanistica e catastale da un tecnico abilitato.

## Avvertenza

Questa guida accompagna uno strumento di analisi personale e non costituisce consulenza fiscale, legale o finanziaria. I numeri dell'immobile riportati sopra sono ipotesi di lavoro su una trattativa in corso: il prezzo trattato è una strategia di acquisto e non un valore di mercato.
