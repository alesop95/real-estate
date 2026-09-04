# Metodo di valutazione e metriche

> Scheda di metodo. Spiega che cosa il modello calcola, perché lo calcola così e dove sono i suoi limiti. Le formule vivono in `src/immobiliare/calcoli.py` e, in forma di formule Excel, nei fogli del workbook.

## La doppia implementazione, e perché esiste

Le stesse regole sono scritte due volte, una in Python e una in formule Excel. Non è una ridondanza accidentale: è il modo con cui il progetto si verifica. Il motore Python è quello leggibile e testabile, il workbook è quello con cui si lavora davvero perché permette di cambiare un input e vedere ricalcolare tutto senza rieseguire nulla. Fare girare i due sullo stesso caso e confrontare i risultati è un test di regressione che intercetta l'errore di trascrizione, che nei fogli di calcolo è l'errore più frequente e il più difficile da vedere.

Sul caso precaricato le due implementazioni concordano su tutte le grandezze di sintesi, dal costo totale al rendimento netto al cash flow. L'unica divergenza voluta è il tasso interno di rendimento, perché la riga di comando assume un flusso di cassa costante mentre il workbook indicizza i costi all'inflazione: per una decisione vale il secondo, il primo serve a scremare in fretta molti immobili.

La verifica formale del workbook, invece, è affidata a `tools/verifica-excel.ps1`, che lo apre con Excel, forza un ricalcolo completo e segnala ogni cella in errore. Serve perché la libreria che genera il file scrive le formule ma non le valuta: senza quel passaggio un riferimento sbagliato o un nome non risolto resterebbe invisibile fino all'apertura da parte di una persona.

## Il denominatore corretto

La scelta metodologica che più cambia i numeri è quale grandezza mettere al denominatore dei rendimenti. La convenzione degli annunci e delle conversazioni è il prezzo. La convenzione di questo modello è il costo totale dell'operazione, cioè il prezzo più le imposte di trasferimento, la provvigione, il notaio, gli oneri del mutuo e gli altri costi di ingresso.

La ragione è che quei costi sono capitale immobilizzato a tutti gli effetti: sono usciti dal conto corrente e non torneranno alla rivendita. Ignorarli gonfia il rendimento di quanto essi incidono, che nell'esempio precaricato è quasi il dieci per cento. È anche la ragione per cui il modello espone l'incidenza dei costi come indicatore a sé: sotto il sei per cento l'operazione è leggera, sopra il dieci vale la pena capire quale voce pesa, perché spesso è una sola, tipicamente la provvigione o l'imposta sostitutiva del due per cento sui mutui non prima casa.

L'esborso iniziale, cioè il costo totale meno la parte finanziata dalla banca, è invece il denominatore del cash on cash, perché è il capitale proprio davvero impiegato. Tenere separati i due denominatori è ciò che permette di leggere la leva finanziaria per quello che è: un moltiplicatore che amplifica il rendimento quando il reddito operativo supera il costo del debito e lo amplifica in negativo quando non lo supera.

## Perché l'accantonamento per la ristrutturazione sta nel conto economico

Un immobile che si tiene quarant'anni va rifatto almeno una volta, e un rifacimento completo costa un ordine di grandezza pari a un terzo del valore dell'immobile. Trattare quella spesa come un evento futuro da ignorare nel rendimento corrente è l'errore che rende ottimistica la maggior parte delle valutazioni immobiliari fatte a mente.

Il modello quindi la ripartisce: un trentesimo di un terzo del valore, ogni anno, come riga del conto economico accanto alla manutenzione ordinaria. È l'impostazione del foglio sulla rendita immobiliare di Paolo Coletti, ed è quella che spiega perché nell'esempio precaricato il rendimento netto scende dall'uno virgola tre allo zero virgola cinque per cento: la differenza è quasi tutta lì. Il numero più basso non è pessimismo, è il numero giusto.

La manutenzione ordinaria segue una regola empirica diversa e altrettanto consolidata, l'uno per cento del valore l'anno, che copre caldaia, infissi, elettrodomestici e le tinteggiature fra un inquilino e l'altro.

## L'ordine in cui si sottraggono le cose

Sfitto e morosità vanno sottratti dal canone potenziale prima del calcolo dell'imposta, non dopo, perché l'imposta si paga sul canone percepito. Il modello espone quindi tre grandezze distinte: il canone potenziale, cioè quello contrattuale annualizzato; il canone effettivo, al netto dei mesi di vuoto e dell'accantonamento per insoluti; e l'utile netto, dopo costi operativi e imposta.

Va segnalata un'asimmetria del regime IRPEF ordinario che il modello non simula per intero ma che va conosciuta: i canoni non percepiti restano imponibili fino alla convalida di sfratto, il che significa che in caso di morosità si pagano imposte su denaro mai incassato. È un argomento a favore della cedolare secca che non compare nel confronto fra aliquote.

## Le metriche, e che cosa ciascuna dice

Il rendimento lordo, canone annuo su prezzo, è il numero che si legge negli annunci ed è il meno informativo, perché ignora imposte, costi e vuoti. Serve solo a scremare rapidamente una lista lunga.

Il rendimento netto, utile netto su costo totale, è il numero da usare per decidere. Fra il lordo e il netto si perdono di norma due punti e mezzo, e chi sente promettere un netto vicino al lordo sta ascoltando una stima costruita male.

Il cap rate, reddito operativo netto su costo totale, esclude imposte sul reddito e mutuo, e serve a confrontare immobili fra loro a prescindere da come sono finanziati e da chi li possiede. È la metrica giusta per rispondere alla domanda su quale immobile sia migliore, mentre il rendimento netto risponde alla domanda su quanto renda a me.

Il cash on cash, cassa netta del primo anno su capitale proprio, è quello che dice se l'immobile mette denaro in tasca o lo toglie. Con la leva può essere negativo anche in un'operazione sana, e in quel caso la domanda diventa se si è in grado di sostenere la differenza ogni mese, che è una domanda di sostenibilità e non di redditività.

Il debt service coverage ratio, reddito operativo netto su rata annua, è la soglia che le banche guardano: sotto uno il reddito dell'immobile non copre la rata e la differenza esce dalla tasca del proprietario. È l'indicatore che smaschera più in fretta le operazioni troppo tirate.

Il tasso interno di rendimento e il valore attuale netto lavorano sull'intero orizzonte e incorporano l'uscita, cioè il valore dell'immobile rivalutato meno il debito residuo, meno i costi di vendita, meno l'eventuale imposta sulla plusvalenza se si esce dentro il quinquennio. Il tasso interno è il numero da confrontare con il rendimento atteso di un portafoglio alternativo, ed è l'unico che rende commensurabili le due alternative.

## Il prezzo massimo si risolve, non si stima per proporzione

La domanda della trattativa è quale prezzo, al massimo, giustifichi l'operazione al rendimento netto che si è dichiarato accettabile. La forma spontanea della risposta è una proporzione: si divide il costo totale sostenibile per uno più l'incidenza percentuale dei costi accessori misurata sullo scenario base. È sbagliata, e vale capire perché, perché l'errore è istruttivo.

Sbaglia per due ragioni indipendenti che si sommano nella stessa direzione. La prima è che l'incidenza percentuale dei costi accessori non è una costante del modello ma una funzione del prezzo: notaio, altri costi, oneri del mutuo, imposte ipotecaria e catastale sono importi fissi, e con l'opzione prezzo-valore lo diventa anche l'intera imposta di registro, che resta ancorata al valore catastale e non segue il prezzo. Quando il prezzo scende, quegli importi restano e la loro incidenza percentuale cresce. La seconda è che l'utile netto annuo non è indipendente dal prezzo: manutenzione ordinaria e accantonamento per la ristrutturazione di fine ciclo sono quote del valore, quindi abbassare il prezzo alza l'utile. La proporzione tiene ferme entrambe le cose, e produce un prezzo massimo sistematicamente troppo basso.

La forma corretta è risolvere l'equazione invece di stimarla. Il costo totale in funzione del prezzo è lineare a tratti, cioè il prezzo per uno più una quota marginale, più una parte fissa; l'utile è lineare decrescente nel prezzo. Imporre che il loro rapporto sia pari all'obiettivo da' un'equazione di primo grado, con soluzione chiusa. Sul caso di riferimento del progetto le due strade danno 15.609 euro contro 43.445, cioè un fattore prossimo a tre, e la direzione dell'errore è quella che fa apparire impossibile qualunque trattativa.

La lezione generale, che vale oltre questa cella, è che un'incidenza percentuale misurata su uno scenario non è un parametro del modello: è un rapporto fra due grandezze che dipendono entrambe dalla variabile che si sta muovendo. Usarla come costante è il modo più comune di introdurre un errore che non si vede, perché il numero che ne esce resta dell'ordine di grandezza giusto. Il presidio adottato è una cella di controllo accanto al risultato: ricalcola il rendimento al prezzo trovato con le formule esatte, minimo di legge dell'imposta di registro compreso, e mostra lo scarto dalla soglia, che deve essere zero. Quando non lo è, dichiara che si è fuori dal tratto lineare, e non lascia dedurlo.

## Lo scenario di risalita del tasso si misura, non si sceglie

Chi valuta un mutuo a tasso variabile deve decidere di quanto farlo salire nella simulazione, ed è il punto in cui un modello per il resto rigoroso viene di solito abbandonato all'intuizione. L'intuizione risponde un punto percentuale, perché è l'ordine di grandezza che suona prudente. La serie mensile dell'Euribor a tre mesi pubblicata dalla Banca centrale europea, che parte dal gennaio 1994, dice che la peggiore finestra di dodici mesi che contiene vale 3,78 punti, fra giugno 2022 e giugno 2023: chi aveva simulato un punto aveva simulato un quinto dello scenario che si è poi verificato, e la rata che aveva dichiarato sostenibile non era quella che ha pagato.

La misura scelta è la peggiore risalita su una finestra di durata fissata, e la scelta va motivata perché un'alternativa apparentemente equivalente da' un numero doppio e privo di senso. Prendere il massimo assoluto della serie e sottrarne il minimo assoluto darebbe più di otto punti, ma il massimo è del marzo 1995 e il minimo del dicembre 2021: nessun piano di ammortamento attraversa ventisei anni nella stessa finestra, quindi quel numero non descrive nessuno scenario che qualcuno possa incontrare. La finestra di dodici, ventiquattro o trentasei mesi, invece, è esattamente ciò che un mutuo attraversa.

Su come va letto il numero, due avvertenze che il valore da solo non porta. Non è una previsione e non è un limite superiore: è il peggio contenuto nei dati disponibili, che in assenza di una previsione è il solo riferimento non arbitrario, e serve come prova di sostenibilità e non come misura di probabilità. E lo stesso scarto produce tassi molto diversi a seconda del livello di partenza: la risalita del 2022-2023 partiva da un Euribor negativo e arrivava al 3,54 per cento, mentre applicata al livello attuale porterebbe a un tasso che nella serie compare soltanto negli anni Novanta. Non è una ragione per escluderla, è una ragione per sapere che si sta guardando la coda della distribuzione.

## Le variabili di scenario si muovono insieme, e il modo di dirlo

Fino al 4 settembre 2026 la simulazione del foglio Rischio estraeva le sue variabili indipendentemente l'una dall'altra, e lo dichiarava. L'assunzione era comoda e sbagliata nella direzione peggiore: sottostimava le code. Nella realtà quando i tassi salgono i prezzi tendono a scendere, e quando il mercato del lavoro peggiora crescono insieme sfitto e morosità, quindi gli scenari cattivi arrivano in gruppo e non uno per volta, ed è esattamente la coda bassa che una decisione di acquisto a leva deve guardare.

La correzione non è una matrice di correlazione completa, e la ragione per cui non lo è va detta: una matrice richiede di stimare una dozzina di parametri che su questi dati nessuno possiede, e sostituirebbe un'assunzione dichiarata e falsa con una nascosta e arbitraria. La forma scelta è un fattore comune: una sola variabile di scenario, estratta insieme alle altre, che entra in ciascuna con il segno del verso in cui quella variabile reagisce a uno scenario favorevole. Canone e rivalutazione salgono, sfitto e tasso scendono, la morosità diventa meno probabile.

L'intensità è un solo numero, impostato nel foglio, e la parametrizzazione è pensata perché quel numero si legga come una correlazione e non come un coefficiente astratto: fra due variabili che reagiscono nello stesso verso la correlazione risultante è esattamente il valore impostato, e fra due di verso opposto è lo stesso valore col segno cambiato. I pesi con cui il fattore comune e la componente propria si mescolano sono la radice della correlazione e la radice del suo complemento, e la scelta non è estetica: la somma dei loro quadrati fa uno, quindi ogni estrazione resta distribuita come prima e le incertezze dichiarate in cima al foglio continuano a valere esattamente quelle. Introdurre la correlazione non gonfia di nascosto le volatilità, che è il difetto in cui questa modifica poteva cadere.

Due proprietà rendono la modifica verificabile invece che opinabile. A correlazione zero la simulazione torna identica a quella indipendente, estrazione per estrazione, e la verifica con Excel misura uno scarto dell'ordine di due su dieci alla sedicesima, cioè la precisione della macchina. Al trenta per cento predefinito la mediana del flusso di cassa resta praticamente ferma mentre la coda bassa peggiora di circa milleseicento euro l'anno sul caso precaricato: la correlazione muove le code e non il centro, che è il comportamento atteso e la ragione per cui serve.

Il valore predefinito resta una convenzione dichiarata, non una stima. Il modo onesto di usarlo è muoverlo fra zero e un valore alto e guardare se la decisione cambia: se cambia, la decisione non era solida.

## Che cosa il modello non sa

Il tasso interno di rendimento non pesa il rischio. Un immobile porta rischio di sfitto, di morosità, di deterioramento, di illiquidità e soprattutto di concentrazione, perché è un singolo bene in una singola via di un singolo Comune. Un portafoglio diversificato con lo stesso rendimento atteso non è la stessa cosa, e la differenza va aggiunta a mano nel giudizio.

Il modello non prezza il lavoro. Gestire un immobile costa tempo, e quel tempo ha un valore che nessuna cella cattura. Nella locazione breve la componente di lavoro è tale che l'operazione somiglia più a un'attività d'impresa che a un investimento, ed è la ragione per cui confrontarne il rendimento con quello di un indice azionario è un confronto fra oggetti diversi.

Il confronto fra comprare e restare in affitto, nel foglio dedicato, assume disciplina perfetta di chi affitta: che investa davvero ogni euro di differenza, ogni anno, senza toccarlo. Nella realtà quasi nessuno lo fa, e il mutuo funziona come piano di accumulo forzato. È un vantaggio comportamentale reale che il foglio non sa misurare e che va tenuto presente quando l'esito è vicino al pareggio.

Il piano di ammortamento simulato si ferma a quarant'anni di rate, e questo introduce un limite che va dichiarato perché non è visibile nel risultato. Sotto la modalità di rimborso che tiene ferma la rata e accorcia il piano, un rialzo forte del tasso produce l'effetto opposto, cioè allunga il piano: con una risalita delle dimensioni di quella del 2022-2023 il piano può arrivare al fondo della tabella con il debito non estinto, e in quel caso la durata effettiva e gli interessi totali descrivono soltanto la porzione di piano che stava in tabella. Sono numeri veri che rispondono a una domanda diversa da quella posta. Il modello lo dichiara con una riga di esito dedicata, che dice se il piano si chiude, ma non lo risolve: risolverlo richiederebbe una tabella più lunga di quanto abbia senso per un mutuo residenziale.

Restano infine fuori la sicurezza abitativa, la libertà di intervenire sull'immobile, il rischio di sfratto e il vincolo di mobilità lavorativa. Sono decisivi nella scelta di dove vivere e irrilevanti nella scelta di dove investire, ed è la ragione per cui le due domande vanno tenute separate anche quando riguardano lo stesso immobile.

## Le tre assunzioni che ribaltano l'esito

Nel confronto fra comprare e affittare tre soli numeri determinano il risultato: il rendimento atteso del portafoglio alternativo, la rivalutazione dell'immobile e il canone che si pagherebbe restando in affitto. Cambiando il primo di un punto percentuale l'esito spesso si rovescia.

Questo dice quanto poco il verdetto vada preso come responso e quanto vada preso come mappa. L'uso corretto del foglio non è leggere l'ultima riga, è capire quanto è distante il pareggio dalle assunzioni in cui si crede. Sulla rivalutazione, in particolare, va detto che in termini reali il mercato residenziale italiano è rimasto sostanzialmente fermo per un ventennio: mettere l'inflazione come rivalutazione nominale è già un'ipotesi benevola, e ogni valore superiore va giustificato con qualcosa di più solido di una sensazione sulla zona.
