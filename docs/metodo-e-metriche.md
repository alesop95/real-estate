# Metodo di valutazione e metriche

> Scheda di metodo. Spiega che cosa il modello calcola, perche' lo calcola cosi' e dove sono i suoi limiti. Le formule vivono in `src/immobiliare/calcoli.py` e, in forma di formule Excel, nei fogli del workbook.

## La doppia implementazione, e perche' esiste

Le stesse regole sono scritte due volte, una in Python e una in formule Excel. Non e' una ridondanza accidentale: e' il modo con cui il progetto si verifica. Il motore Python e' quello leggibile e testabile, il workbook e' quello con cui si lavora davvero perche' permette di cambiare un input e vedere ricalcolare tutto senza rieseguire nulla. Fare girare i due sullo stesso caso e confrontare i risultati e' un test di regressione che intercetta l'errore di trascrizione, che nei fogli di calcolo e' l'errore piu' frequente e il piu' difficile da vedere.

Sul caso precaricato le due implementazioni concordano su tutte le grandezze di sintesi, dal costo totale al rendimento netto al cash flow. L'unica divergenza voluta e' il tasso interno di rendimento, perche' la riga di comando assume un flusso di cassa costante mentre il workbook indicizza i costi all'inflazione: per una decisione vale il secondo, il primo serve a scremare in fretta molti immobili.

La verifica formale del workbook, invece, e' affidata a `tools/verifica-excel.ps1`, che lo apre con Excel, forza un ricalcolo completo e segnala ogni cella in errore. Serve perche' la libreria che genera il file scrive le formule ma non le valuta: senza quel passaggio un riferimento sbagliato o un nome non risolto resterebbe invisibile fino all'apertura da parte di una persona.

## Il denominatore corretto

La scelta metodologica che piu' cambia i numeri e' quale grandezza mettere al denominatore dei rendimenti. La convenzione degli annunci e delle conversazioni e' il prezzo. La convenzione di questo modello e' il costo totale dell'operazione, cioe' il prezzo piu' le imposte di trasferimento, la provvigione, il notaio, gli oneri del mutuo e gli altri costi di ingresso.

La ragione e' che quei costi sono capitale immobilizzato a tutti gli effetti: sono usciti dal conto corrente e non torneranno alla rivendita. Ignorarli gonfia il rendimento di quanto essi incidono, che nell'esempio precaricato e' quasi il dieci per cento. E' anche la ragione per cui il modello espone l'incidenza dei costi come indicatore a se': sotto il sei per cento l'operazione e' leggera, sopra il dieci vale la pena capire quale voce pesa, perche' spesso e' una sola, tipicamente la provvigione o l'imposta sostitutiva del due per cento sui mutui non prima casa.

L'esborso iniziale, cioe' il costo totale meno la parte finanziata dalla banca, e' invece il denominatore del cash on cash, perche' e' il capitale proprio davvero impiegato. Tenere separati i due denominatori e' cio' che permette di leggere la leva finanziaria per quello che e': un moltiplicatore che amplifica il rendimento quando il reddito operativo supera il costo del debito e lo amplifica in negativo quando non lo supera.

## Perche' l'accantonamento per la ristrutturazione sta nel conto economico

Un immobile che si tiene quarant'anni va rifatto almeno una volta, e un rifacimento completo costa un ordine di grandezza pari a un terzo del valore dell'immobile. Trattare quella spesa come un evento futuro da ignorare nel rendimento corrente e' l'errore che rende ottimistica la maggior parte delle valutazioni immobiliari fatte a mente.

Il modello quindi la ripartisce: un trentesimo di un terzo del valore, ogni anno, come riga del conto economico accanto alla manutenzione ordinaria. E' l'impostazione del foglio sulla rendita immobiliare di Paolo Coletti, ed e' quella che spiega perche' nell'esempio precaricato il rendimento netto scende dall'uno virgola tre allo zero virgola cinque per cento: la differenza e' quasi tutta li'. Il numero piu' basso non e' pessimismo, e' il numero giusto.

La manutenzione ordinaria segue una regola empirica diversa e altrettanto consolidata, l'uno per cento del valore l'anno, che copre caldaia, infissi, elettrodomestici e le tinteggiature fra un inquilino e l'altro.

## L'ordine in cui si sottraggono le cose

Sfitto e morosita' vanno sottratti dal canone potenziale prima del calcolo dell'imposta, non dopo, perche' l'imposta si paga sul canone percepito. Il modello espone quindi tre grandezze distinte: il canone potenziale, cioe' quello contrattuale annualizzato; il canone effettivo, al netto dei mesi di vuoto e dell'accantonamento per insoluti; e l'utile netto, dopo costi operativi e imposta.

Va segnalata un'asimmetria del regime IRPEF ordinario che il modello non simula per intero ma che va conosciuta: i canoni non percepiti restano imponibili fino alla convalida di sfratto, il che significa che in caso di morosita' si pagano imposte su denaro mai incassato. E' un argomento a favore della cedolare secca che non compare nel confronto fra aliquote.

## Le metriche, e che cosa ciascuna dice

Il rendimento lordo, canone annuo su prezzo, e' il numero che si legge negli annunci ed e' il meno informativo, perche' ignora imposte, costi e vuoti. Serve solo a scremare rapidamente una lista lunga.

Il rendimento netto, utile netto su costo totale, e' il numero da usare per decidere. Fra il lordo e il netto si perdono di norma due punti e mezzo, e chi sente promettere un netto vicino al lordo sta ascoltando una stima costruita male.

Il cap rate, reddito operativo netto su costo totale, esclude imposte sul reddito e mutuo, e serve a confrontare immobili fra loro a prescindere da come sono finanziati e da chi li possiede. E' la metrica giusta per rispondere alla domanda su quale immobile sia migliore, mentre il rendimento netto risponde alla domanda su quanto renda a me.

Il cash on cash, cassa netta del primo anno su capitale proprio, e' quello che dice se l'immobile mette denaro in tasca o lo toglie. Con la leva puo' essere negativo anche in un'operazione sana, e in quel caso la domanda diventa se si e' in grado di sostenere la differenza ogni mese, che e' una domanda di sostenibilita' e non di redditivita'.

Il debt service coverage ratio, reddito operativo netto su rata annua, e' la soglia che le banche guardano: sotto uno il reddito dell'immobile non copre la rata e la differenza esce dalla tasca del proprietario. E' l'indicatore che smaschera piu' in fretta le operazioni troppo tirate.

Il tasso interno di rendimento e il valore attuale netto lavorano sull'intero orizzonte e incorporano l'uscita, cioe' il valore dell'immobile rivalutato meno il debito residuo, meno i costi di vendita, meno l'eventuale imposta sulla plusvalenza se si esce dentro il quinquennio. Il tasso interno e' il numero da confrontare con il rendimento atteso di un portafoglio alternativo, ed e' l'unico che rende commensurabili le due alternative.

## Il prezzo massimo si risolve, non si stima per proporzione

La domanda della trattativa e' quale prezzo, al massimo, giustifichi l'operazione al rendimento netto che si e' dichiarato accettabile. La forma spontanea della risposta e' una proporzione: si divide il costo totale sostenibile per uno piu' l'incidenza percentuale dei costi accessori misurata sullo scenario base. E' sbagliata, e vale capire perche', perche' l'errore e' istruttivo.

Sbaglia per due ragioni indipendenti che si sommano nella stessa direzione. La prima e' che l'incidenza percentuale dei costi accessori non e' una costante del modello ma una funzione del prezzo: notaio, altri costi, oneri del mutuo, imposte ipotecaria e catastale sono importi fissi, e con l'opzione prezzo-valore lo diventa anche l'intera imposta di registro, che resta ancorata al valore catastale e non segue il prezzo. Quando il prezzo scende, quegli importi restano e la loro incidenza percentuale cresce. La seconda e' che l'utile netto annuo non e' indipendente dal prezzo: manutenzione ordinaria e accantonamento per la ristrutturazione di fine ciclo sono quote del valore, quindi abbassare il prezzo alza l'utile. La proporzione tiene ferme entrambe le cose, e produce un prezzo massimo sistematicamente troppo basso.

La forma corretta e' risolvere l'equazione invece di stimarla. Il costo totale in funzione del prezzo e' lineare a tratti, cioe' il prezzo per uno piu' una quota marginale, piu' una parte fissa; l'utile e' lineare decrescente nel prezzo. Imporre che il loro rapporto sia pari all'obiettivo da' un'equazione di primo grado, con soluzione chiusa. Sul caso di riferimento del progetto le due strade danno 15.609 euro contro 43.445, cioe' un fattore prossimo a tre, e la direzione dell'errore e' quella che fa apparire impossibile qualunque trattativa.

La lezione generale, che vale oltre questa cella, e' che un'incidenza percentuale misurata su uno scenario non e' un parametro del modello: e' un rapporto fra due grandezze che dipendono entrambe dalla variabile che si sta muovendo. Usarla come costante e' il modo piu' comune di introdurre un errore che non si vede, perche' il numero che ne esce resta dell'ordine di grandezza giusto. Il presidio adottato e' una cella di controllo accanto al risultato: ricalcola il rendimento al prezzo trovato con le formule esatte, minimo di legge dell'imposta di registro compreso, e mostra lo scarto dalla soglia, che deve essere zero. Quando non lo e', dichiara che si e' fuori dal tratto lineare, e non lascia dedurlo.

## Lo scenario di risalita del tasso si misura, non si sceglie

Chi valuta un mutuo a tasso variabile deve decidere di quanto farlo salire nella simulazione, ed e' il punto in cui un modello per il resto rigoroso viene di solito abbandonato all'intuizione. L'intuizione risponde un punto percentuale, perche' e' l'ordine di grandezza che suona prudente. La serie mensile dell'Euribor a tre mesi pubblicata dalla Banca centrale europea, che parte dal gennaio 1994, dice che la peggiore finestra di dodici mesi che contiene vale 3,78 punti, fra giugno 2022 e giugno 2023: chi aveva simulato un punto aveva simulato un quinto dello scenario che si e' poi verificato, e la rata che aveva dichiarato sostenibile non era quella che ha pagato.

La misura scelta e' la peggiore risalita su una finestra di durata fissata, e la scelta va motivata perche' un'alternativa apparentemente equivalente da' un numero doppio e privo di senso. Prendere il massimo assoluto della serie e sottrarne il minimo assoluto darebbe piu' di otto punti, ma il massimo e' del marzo 1995 e il minimo del dicembre 2021: nessun piano di ammortamento attraversa ventisei anni nella stessa finestra, quindi quel numero non descrive nessuno scenario che qualcuno possa incontrare. La finestra di dodici, ventiquattro o trentasei mesi, invece, e' esattamente cio' che un mutuo attraversa.

Su come va letto il numero, due avvertenze che il valore da solo non porta. Non e' una previsione e non e' un limite superiore: e' il peggio contenuto nei dati disponibili, che in assenza di una previsione e' il solo riferimento non arbitrario, e serve come prova di sostenibilita' e non come misura di probabilita'. E lo stesso scarto produce tassi molto diversi a seconda del livello di partenza: la risalita del 2022-2023 partiva da un Euribor negativo e arrivava al 3,54 per cento, mentre applicata al livello attuale porterebbe a un tasso che nella serie compare soltanto negli anni Novanta. Non e' una ragione per escluderla, e' una ragione per sapere che si sta guardando la coda della distribuzione.

## Che cosa il modello non sa

Il tasso interno di rendimento non pesa il rischio. Un immobile porta rischio di sfitto, di morosita', di deterioramento, di illiquidita' e soprattutto di concentrazione, perche' e' un singolo bene in una singola via di un singolo Comune. Un portafoglio diversificato con lo stesso rendimento atteso non e' la stessa cosa, e la differenza va aggiunta a mano nel giudizio.

Il modello non prezza il lavoro. Gestire un immobile costa tempo, e quel tempo ha un valore che nessuna cella cattura. Nella locazione breve la componente di lavoro e' tale che l'operazione somiglia piu' a un'attivita' d'impresa che a un investimento, ed e' la ragione per cui confrontarne il rendimento con quello di un indice azionario e' un confronto fra oggetti diversi.

Il confronto fra comprare e restare in affitto, nel foglio dedicato, assume disciplina perfetta di chi affitta: che investa davvero ogni euro di differenza, ogni anno, senza toccarlo. Nella realta' quasi nessuno lo fa, e il mutuo funziona come piano di accumulo forzato. E' un vantaggio comportamentale reale che il foglio non sa misurare e che va tenuto presente quando l'esito e' vicino al pareggio.

Il piano di ammortamento simulato si ferma a quarant'anni di rate, e questo introduce un limite che va dichiarato perche' non e' visibile nel risultato. Sotto la modalita' di rimborso che tiene ferma la rata e accorcia il piano, un rialzo forte del tasso produce l'effetto opposto, cioe' allunga il piano: con una risalita delle dimensioni di quella del 2022-2023 il piano puo' arrivare al fondo della tabella con il debito non estinto, e in quel caso la durata effettiva e gli interessi totali descrivono soltanto la porzione di piano che stava in tabella. Sono numeri veri che rispondono a una domanda diversa da quella posta. Il modello lo dichiara con una riga di esito dedicata, che dice se il piano si chiude, ma non lo risolve: risolverlo richiederebbe una tabella piu' lunga di quanto abbia senso per un mutuo residenziale.

Restano infine fuori la sicurezza abitativa, la liberta' di intervenire sull'immobile, il rischio di sfratto e il vincolo di mobilita' lavorativa. Sono decisivi nella scelta di dove vivere e irrilevanti nella scelta di dove investire, ed e' la ragione per cui le due domande vanno tenute separate anche quando riguardano lo stesso immobile.

## Le tre assunzioni che ribaltano l'esito

Nel confronto fra comprare e affittare tre soli numeri determinano il risultato: il rendimento atteso del portafoglio alternativo, la rivalutazione dell'immobile e il canone che si pagherebbe restando in affitto. Cambiando il primo di un punto percentuale l'esito spesso si rovescia.

Questo dice quanto poco il verdetto vada preso come responso e quanto vada preso come mappa. L'uso corretto del foglio non e' leggere l'ultima riga, e' capire quanto e' distante il pareggio dalle assunzioni in cui si crede. Sulla rivalutazione, in particolare, va detto che in termini reali il mercato residenziale italiano e' rimasto sostanzialmente fermo per un ventennio: mettere l'inflazione come rivalutazione nominale e' gia' un'ipotesi benevola, e ogni valore superiore va giustificato con qualcosa di piu' solido di una sensazione sulla zona.
