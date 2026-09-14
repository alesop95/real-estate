---
generated-from-commit: a0b3420
generated-from-branch: main
generated-date: 2026-09-01
covers-paths:
  - src/immobiliare/**
  - tests/**
last-verified-commit: a0b3420
---

# Studio didattico, racconto evolutivo

> Livello documentale distinto dalle schede di stato. [`STACK.md`](STACK.md) e le altre schede dicono *cosa* è vero oggi; `memory/decisions.md` dice *quale* decisione è stata presa e con quali conseguenze. Questo file dice *perché una forma ingenua era fragile e perché quella nuova è un salto*, e cresce per voci numerate in ordine cronologico: ogni intervento aggiunge una voce in fondo, nessuna voce si riscrive. Il dettaglio nel codice reale sta nei deep-dive `refactor-NN-*.md` accanto a questo file.

La pratica è stata adottata il 31 agosto 2026, su richiesta esplicita, con le voci che ricostruiscono i salti già compiuti in questo progetto perché tutti documentati e verificabili nel work-log e nel codice.

## 1. Il workbook porta formule, non risultati

Contesto. Il progetto deve produrre uno strumento che risponda a domande su un acquisto immobiliare. La prima scelta di architettura riguarda cosa esce dal generatore Python: numeri o formule.

Com'era e perché era fragile. La forma naturale, e quella che quasi tutti i generatori di report adottano, è calcolare in Python e scrivere il risultato nella cella. È semplice, si testa con un `assert`, e produce un file leggero. È però fragile per una ragione che non riguarda il codice ma l'uso: un file di numeri risponde a una domanda sola, quella con cui è stato generato. Cambiare il prezzo di cinquemila euro richiede di tornare al terminale, ricordare i parametri, rigenerare. Nella pratica significa che nessuno prova le ipotesi, e uno strumento di valutazione che non permette di provare le ipotesi non serve a valutare: serve a confermare la prima che si è avuta in testa.

Il salto senior e perché è meglio. Il generatore scrive formule Excel, e i riferimenti fra fogli passano per *nomi definiti* invece che per indirizzi di cella. La conseguenza è che il file non è un rapporto ma il modello stesso: chi lo apre cambia una cella gialla e vede ricalcolare l'intero workbook. Il costo è reale e va dichiarato: le formule non si valutano alla scrittura, quindi il generatore può produrre file sintatticamente validi e funzionalmente rotti, il che ha generato la voce 3 di questo racconto. Il principio generale è che quando l'artefatto prodotto è anche l'interfaccia con cui si lavora, conviene spostare il calcolo dentro l'artefatto e tenere nel codice la sua costruzione.

Dove leggere il dettaglio: [`refactor-01-formule-vive.md`](refactor-01-formule-vive.md).

## 2. Il denominatore dei rendimenti è il costo totale, non il prezzo

Contesto. Ogni indicatore di rendimento è una frazione, e la scelta del denominatore è una scelta di modello che nessuno dichiara mai.

Com'era e perché era fragile. La convenzione degli annunci, delle conversazioni e della maggior parte dei fogli di calcolo che circolano è dividere per il prezzo. È fragile perché il prezzo non è il denaro che l'operazione ha assorbito: imposte di trasferimento, provvigione, notaio e oneri del mutuo sono capitale uscito dal conto corrente che non tornerà alla rivendita. Ignorarli non produce un errore visibile, produce un rendimento sistematicamente gonfiato, e la distorsione è tanto maggiore quanto più piccolo è l'immobile, cioè proprio dove i costi fissi pesano di più. Un modello che sbaglia sempre nella stessa direzione è peggio di uno rumoroso, perché sembra affidabile.

Il salto senior e perché è meglio. Il denominatore diventa il costo totale dell'operazione, e il capitale proprio effettivamente immobilizzato diventa il denominatore separato del *cash on cash*. Tenere due denominatori distinti, invece di uno solo di compromesso, è ciò che rende leggibile la leva finanziaria: il rendimento sul costo totale misura l'immobile, quello sull'esborso misura l'operazione finanziata. Sul caso di riferimento la differenza fra le due convenzioni è quasi un decimo, e il modello espone l'incidenza dei costi come indicatore autonomo proprio per rendere visibile quanto si sta correggendo.

Dove leggere il dettaglio: [`refactor-02-denominatore.md`](refactor-02-denominatore.md).

## 3. Il workbook si verifica aprendolo, non scrivendolo

Contesto. Conseguenza diretta della voce 1: la libreria che genera il file scrive le formule senza valutarle.

Com'era e perché era fragile. La verifica implicita era che il generatore terminasse senza eccezioni e il file si salvasse. È una verifica che non verifica nulla di ciò che conta: un riferimento a un nome inesistente, una parentesi sbagliata, un blocco XML vuoto passano tutti quel controllo. Il caso concreto che ha reso evidente il problema è stato un elemento di validazione dichiarato e mai associato ad alcuna cella, che ha prodotto un `<dataValidations count="0"/>` e ha reso il file irricevibile per Excel, senza che nulla in Python protestasse.

Il salto senior e perché è meglio. Esiste uno script che apre il workbook con Excel via automazione, forza un ricalcolo completo, raccoglie tutte le celle che valutano a errore e termina con codice diverso da zero. Accanto, una tecnica di diagnosi: quando il file non si apre affatto, si generano workbook progressivi con un foglio in più alla volta e si prova ad aprirli tutti, isolando il foglio responsabile per bisezione. Il principio generale è che quando un artefatto viene interpretato da un motore esterno, l'unica verifica che vale è farlo interpretare da quel motore.

Dove leggere il dettaglio: [`refactor-03-verifica-con-excel.md`](refactor-03-verifica-con-excel.md).

## 4. L'agevolazione applicabile è una sola fonte di verità

Contesto. L'agevolazione prima casa governa due grandezze diverse, l'aliquota dell'imposta di registro e il moltiplicatore catastale, e le governa insieme.

Com'era e perché era fragile. Le due grandezze erano calcolate in due punti distinti, ciascuno che si chiedeva da sé se l'agevolazione spettasse. Il calcolo del moltiplicatore guardava all'agevolazione *richiesta* dall'acquirente, quello dell'aliquota alla condizione completa che include l'esclusione delle categorie di lusso. Su un immobile ordinario i due coincidevano e il difetto restava invisibile; su una categoria A/1, A/8 o A/9 divergevano, e l'imposta risultava sottostimata di circa un dodicesimo. Il difetto era presente in modo identico nel motore Python e nelle formule Excel, il che dice qualcosa di utile: la doppia implementazione protegge dagli errori di trascrizione, non da un errore di ragionamento commesso una volta e replicato fedelmente.

Il salto senior e perché è meglio. La condizione diventa una funzione sola, `agevolazione_applicabile`, e nel workbook una cella sola con un nome, `agevolata`, calcolata prima di tutto ciò che ne dipende. L'ordine di costruzione delle celle smette di essere cosmetico e diventa parte della correttezza. Il principio è che quando due valori derivano dalla stessa condizione, la condizione va calcolata una volta e riferita, mai ricalcolata in parallelo: due copie della stessa logica divergono sempre, e divergono nel caso raro, cioè quello che nessuno prova.

Dove leggere il dettaglio: [`refactor-04-agevolazione-unica.md`](refactor-04-agevolazione-unica.md).

## 5. Un costo ricorrente sta in un posto solo

Contesto. L'accantonamento per la ristrutturazione di fine ciclo è un costo annuo che deve comparire nel conto economico della locazione e nella proiezione del flusso di cassa.

Com'era e perché era fragile. Compariva in entrambi, ed erano due cose diverse: nel foglio della locazione come voce del conto economico, nel foglio del flusso di cassa come colonna autonoma. Poiché la colonna dei costi operativi del flusso di cassa era derivata dal reddito operativo netto della locazione, l'accantonamento veniva sottratto due volte. Il flusso di cassa risultava peggiore del vero di un importo pari all'accantonamento, ogni anno, per tutto l'orizzonte, e nessun controllo lo segnalava perché entrambe le formule erano corrette prese da sole.

Il salto senior e perché è meglio. La voce entra una volta sola nel conto economico, e il foglio del flusso di cassa perde la colonna autonoma. La regola che ne discende, e che è stata applicata poi a ogni voce nuova, è che un costo ha un unico luogo di dichiarazione e tutti gli altri fogli lo ereditano attraverso una grandezza aggregata. Quando si è aggiunto il costo figurativo del tempo, mesi dopo, la domanda giusta è stata immediata: in quale conto economico entra, non in quali fogli va aggiunto.

Dove leggere il dettaglio: [`refactor-05-doppio-conteggio.md`](refactor-05-doppio-conteggio.md).

## 6. Il contratto posizionale fra due file va protetto da un test

Contesto. Il registro degli annunci è una dataclass Python, il foglio Annunci è una tabella Excel, e l'esportazione scrive per posizione di colonna.

Com'era e perché era fragile. L'allineamento fra l'ordine dei campi della dataclass, l'ordine della lista usata dall'esportazione e l'ordine delle intestazioni del foglio era garantito soltanto dall'attenzione di chi scriveva. Sono tre elenchi in due file diversi che devono restare paralleli, e nessun tipo li lega. Un campo inserito in mezzo alla dataclass avrebbe fatto scrivere i prezzi nella colonna delle note, in silenzio, con il file che si apre regolarmente e i numeri che sembrano numeri.

Il salto senior e perché è meglio. Un test esporta un annuncio con valori noti e rilegge le celle una per una, verificando anche che le tre colonne di formula non siano state sovrascritte. Ha ripagato il costo alla prima esecuzione, scoprendo un difetto che nessuno stava cercando: la libreria ignora l'assegnazione quando si passa un valore nullo al costruttore della cella, quindi un campo azzerato non ripuliva la cella e l'annuncio esportato ereditava in silenzio il dato di quello che occupava prima quella riga. Il principio è che un contratto posizionale non documentato è un difetto in attesa, e che il modo di renderlo sicuro non è commentarlo ma eseguirlo.

Dove leggere il dettaglio: [`refactor-06-contratto-posizionale.md`](refactor-06-contratto-posizionale.md).

## 7. La simulazione separa l'estrazione dal calcolo

Contesto. Passare da tre scenari scelti a mano a una distribuzione di esiti, restando dentro un foglio di calcolo e senza macro.

Com'era e perché era fragile. La forma ovvia è usare la funzione casuale nativa del foglio. È fragile per una proprietà di quella funzione che si scopre usandola: è volatile, quindi ogni ricalcolo rigenera tutti i numeri. Due letture consecutive dello stesso file danno risultati diversi, un percentile cambia mentre lo si guarda, e nulla è riproducibile né verificabile. Uno strumento che deve sostenere una decisione da centomila euro non può cambiare risposta a ogni pressione di un tasto.

Il salto senior e perché è meglio. Le due cose vengono separate. Le estrazioni sono mille righe di numeri fissi, generate una volta sola alla costruzione del file da un generatore con seme dichiarato, quindi identiche a ogni riapertura e riproducibili da chiunque rigeneri il workbook. Il calcolo che sta sopra è invece formula viva, e legge gli input dell'utente: cambiando il prezzo o il tasso, tutti i mille scenari si ricalcolano sulla stessa estrazione. Si ottiene una simulazione insieme stabile e interattiva, che è esattamente ciò che serviva e che nessuna delle due forme pure dava. Il foglio delle estrazioni è nascosto, perché non c'è nulla da leggerci.

Nella stessa voce rientra una correzione di modello che vale più della tecnica. La prima versione trattava l'estrazione sulla rivalutazione come se fosse un regime permanente per tutto l'orizzonte, e la coda alta produceva patrimoni finali fuori scala. La rivalutazione si compone, quindi l'estrazione non è la variazione di un anno ma la media del periodo, e la sua dispersione scende con la radice del numero di anni: senza quella correzione la simulazione era matematicamente coerente e finanziariamente assurda.

Dove leggere il dettaglio: [`refactor-07-simulazione-riproducibile.md`](refactor-07-simulazione-riproducibile.md).

## 8. Un riferimento per coordinata è un difetto in attesa

Contesto. Il generatore scrive formule, e una formula cita altre celle. Le forme disponibili sono tre: il nome definito, la coordinata scritta a mano, l'indice calcolato come ancoraggio più una costante.

Com'era e perché era fragile. Tutte tre convivevano, e le ultime due hanno prodotto difetti veri. La formula del Cruscotto che dà il verdetto fra comprare e affittare citava `'Confronto affitto'!$B$52`, che nel frattempo era diventata la riga del patrimonio comprando invece di quella della differenza fra i due patrimoni. Il patrimonio comprando è positivo per qualunque immobile di valore, quindi il verdetto rispondeva "conviene comprare" quasi sempre, indipendentemente dal confronto che diceva di riportare: portando il rendimento del portafoglio alternativo al nove per cento, la differenza vale meno centoquattordicimila euro e il foglio conclude che conviene restare in affitto, mentre la formula precedente diceva di comprare. Il difetto era una recidiva, perché lo stesso foglio ne aveva già avuto uno identico quattro giorni prima. Gli indici per offset, nel conto economico della locazione e nella tabella a tre scenari, non avevano ancora prodotto nulla di visibile soltanto perché nessuno aveva inserito una voce in mezzo.

Il salto senior e perché è meglio. La scelta non riguarda l'eleganza ma il modo in cui l'errore si manifesta, e questa è la parte generalizzabile. Un nome definito inesistente produce `#NOME?` in ogni cella che lo usa, e la verifica con Excel lo intercetta. Una chiave assente in un dizionario di righe solleva un `KeyError` alla generazione, e il file non viene nemmeno prodotto. Una coordinata sbagliata è invece un riferimento perfettamente valido a una cella diversa: nessun errore, un numero dell'ordine di grandezza giusto, un foglio che si apre. Fra tre forme che possono sbagliare si scelgono quelle che sbagliano rumorosamente. Il presidio non è un commento ma un test che verifica l'invariante in termini di etichette e non di numeri di riga, così che continui a valere dopo un riordino del foglio.

Dove leggere il dettaglio: [`refactor-08-riferimenti-per-nome.md`](refactor-08-riferimenti-per-nome.md).

## 9. Un'assunzione uguale per tutte le righe non è un dato

Contesto. Il foglio Confronto immobili valuta una lista di annunci con lo stesso modello del resto del workbook, imposte di trasferimento comprese.

Com'era e perché era fragile. Il regime di acquisto, cioè prima casa oppure no e venditore privato oppure impresa con IVA, era quello impostato nel foglio Immobile e valeva per tutte le righe. Il limite era dichiarato nel foglio, il che lo rendeva onesto ma non innocuo, perché la sua conseguenza non è un'imprecisione ma un'inversione dell'ordine: sullo stesso prezzo l'IVA si applica per intero mentre l'imposta di registro con il prezzo-valore si applica al valore catastale, che di norma è una frazione. Un usato da privato e un nuovo da costruttore, confrontati con lo stesso regime, producono una graduatoria che segnala come migliore proprio l'immobile che porta l'imposta più alta. Una dichiarazione in nota non protegge da un ordinamento sbagliato, perché chi legge una tabella ordinata legge l'ordine.

Il salto senior e perché è meglio. Il dato torna dove varia, cioè nella riga, e il foglio espone il regime applicato accanto alle imposte, perché una graduatoria in cui una riga paga l'IVA e un'altra il registro va letta sapendolo. La parte non ovvia è il terzo stato: il vuoto non significa NO, significa eredita da dove stava prima. Serve a rendere l'aggiunta esattamente neutra su tutto ciò che esiste già, e la neutralità qui non è cortesia verso il passato ma una proprietà verificabile, perché permette di affermare che un registro non toccato produce gli stessi numeri. Trattare il vuoto come NO avrebbe cambiato in silenzio le imposte di dodici annunci, togliendo loro l'agevolazione prima casa.

Dove leggere il dettaglio: [`refactor-09-regime-per-riga.md`](refactor-09-regime-per-riga.md).

## 10. Un'incidenza percentuale non è un parametro del modello

Contesto. Il prezzo massimo sostenibile risponde alla domanda della trattativa: quale prezzo, al massimo, giustifica l'operazione al rendimento netto dichiarato accettabile.

Com'era e perché era fragile. Era calcolato dividendo il costo totale sostenibile per uno più l'incidenza percentuale dei costi accessori misurata sullo scenario base, con l'approssimazione dichiarata in nota. Sbagliava per due ragioni indipendenti che si sommavano nella stessa direzione. L'incidenza dei costi accessori non è una costante ma una funzione del prezzo, perché notaio, altri costi, oneri del mutuo, imposte fisse e, con il prezzo-valore, l'intera imposta di registro sono importi fissi, e la loro incidenza percentuale cresce quando il prezzo scende. E l'utile netto non è indipendente dal prezzo, perché manutenzione ordinaria e accantonamento per la ristrutturazione sono quote del valore. Sul caso di riferimento le due strade danno 15.609 euro contro 43.445, un fattore prossimo a tre, e l'errore va nella direzione che fa sembrare impossibile qualunque trattativa.

Il salto senior e perché è meglio. L'equazione si risolve invece di stimarla, e la soluzione è algebra di primo grado, non un metodo numerico: il costo totale è lineare a tratti nel prezzo, l'utile è lineare decrescente, imporre il loro rapporto pari all'obiettivo dà una formula chiusa. Le tre grandezze che la compongono stanno in tre celle visibili con la loro nota, perché una formula che nasconde tre coefficienti non è ispezionabile. La seconda metà del salto è il controllo di chiusura: una cella ricalcola il rendimento al prezzo trovato con le formule esatte delle imposte, minimo di legge compreso, e mostra lo scarto dalla soglia. Sta nel foglio e non in un test per una ragione precisa, cioè che la soluzione è esatta solo sul tratto lineare e il caso che la rompe, il minimo di legge dell'imposta di registro, si presenta quando l'utente cambia gli input a video, non nel caso precaricato che un test coprirebbe. Il principio generale è che un rapporto fra due grandezze che dipendono entrambe dalla variabile che si sta muovendo non è un parametro, e usarlo come tale è il modo più comune di introdurre un errore che resta dell'ordine di grandezza giusto.

Dove leggere il dettaglio: [`refactor-10-prezzo-massimo-esatto.md`](refactor-10-prezzo-massimo-esatto.md).

## 11. Uno scenario di stress si misura sui dati, non si sceglie a sentimento

Contesto. Chi valuta un mutuo a tasso variabile deve decidere di quanto farlo salire nella simulazione.

Com'era e perché era fragile. Il foglio offriva un gradino singolo, una variazione e un mese di entrata in vigore, e lasciava il valore all'utente con la nota che un punto percentuale è uno scenario ordinario e non estremo. È il punto in cui un modello per il resto rigoroso veniva consegnato all'intuizione, e l'intuizione sbaglia in modo prevedibile: la cifra che viene in mente è un punto, perché suona prudente. Fra giugno 2022 e giugno 2023 l'Euribor a tre mesi è salito di 3,78 punti in dodici mesi. Chi aveva simulato un punto aveva simulato un quinto dello scenario che si è verificato, e la rata che aveva dichiarato sostenibile non era quella che ha pagato.

Il salto senior e perché è meglio. Il numero si misura sulla serie storica, che era già scaricabile dal modulo dei tassi e non veniva usata per questo. La misura scelta è la peggiore risalita su una finestra di durata fissata, e la scelta va motivata perché un'alternativa apparentemente equivalente dà un numero doppio e privo di senso: massimo assoluto meno minimo assoluto darebbe più di otto punti, ma i due estremi distano ventisei anni e nessun piano di ammortamento li attraversa nella stessa finestra. Il percorso del tasso diventa a gradini, così che una risalita possa essere descritta come è avvenuta e non come un salto istantaneo, e i valori misurati vengono congelati nel codice con la data di verifica, perché il generatore non deve dipendere dalla rete, con un comando che li riverifica e dichiara se sono ancora quelli.

Nella stessa voce rientra un difetto trovato usando ciò che si era appena costruito, che è il modo in cui questi difetti si trovano. Provando il rialzo reale in tre gradini, il piano arrivava a 480 mesi con 206.464 euro di interessi: due numeri veri che rispondevano a una domanda diversa, perché 480 è il fondo della tabella e non la durata del piano, e restavano 87.082 euro di debito non estinto. Sotto la modalità che riduce la durata un rialzo forte allunga il piano invece di alzare la rata. Ora due righe di esito dicono se il piano si chiude, e lo stesso scenario sotto la modalità che riduce la rata, cioè il funzionamento del variabile italiano, chiude regolarmente con la rata che passa da 436 a 626 euro: è quello il numero da confrontare con il reddito.

Dove leggere il dettaglio: [`refactor-11-scenario-misurato.md`](refactor-11-scenario-misurato.md).

## 12. Uno strumento corretto che non si sa percorrere non è finito

Contesto. Il workbook è arrivato a venti fogli visibili, tutti dentro il perimetro e tutti verificati. La segnalazione è arrivata dall'uso, non da un test: i fogli sono tanti, sono probabilmente tutti necessari, ma si perde il flusso.

Com'era e perché era fragile. La navigazione dipendeva dalle linguette in basso, più un foglio di presentazione che portava un elenco descrittivo di undici voci su venti e nessun collegamento. È una fragilità di natura diversa da tutte le altre voci di questo racconto, perché non produce un numero sbagliato: produce un file in cui il numero giusto non si trova. Le undici voci mancanti non erano una dimenticanza, erano il segnale che quell'elenco veniva aggiornato a mano e quindi non lo era.

Il salto senior e perché è meglio. L'indice non elenca i fogli, che le linguette elencano già: risponde alle tre domande che le linguette non rispondono, cioè se in quel foglio si scrive o si legge, quando lo si apre nel percorso, e se riguarda il proprio caso, perché diversi fogli servono solo in situazioni particolari e chi apre il file non sa se stia dimenticando di compilarli. Ed è costruito da una sorgente unica che un test confronta con i fogli realmente presenti, nelle due direzioni, perché un elenco di navigazione mantenuto a mano diverge sempre, e la sua divergenza è invisibile: un collegamento verso un foglio rinominato è sintatticamente valido e Excel lo apre senza errore, semplicemente non andando da nessuna parte.

Due dettagli tecnici della stessa voce meritano attenzione perché sono errori che si fanno una volta. Il primo è la posizione del ritorno all'indice: metterlo accanto al titolo sembra naturale e non funziona, perché il titolo occupa da quattro a ventisei colonne a seconda del foglio, quindi su un foglio largo il ritorno finisce fuori dalla vista; la posizione giusta è la riga che la funzione del titolo lasciava vuota, in colonna A, identica su tutti i fogli. E la funzione del titolo è anche il posto giusto in cui scriverlo, perché ogni foglio la chiama per primo e così un foglio nuovo non può nascere senza via di ritorno. Il secondo è la forma del collegamento: assegnare una stringa alla proprietà del collegamento lo registra come destinazione esterna, e nel file finisce fra le relazioni verso l'esterno; un collegamento interno non ha una destinazione esterna, ha una posizione dentro il file.

Nella stessa voce rientra un difetto trovato scrivendo la documentazione, che è il modo in cui la documentazione ripaga il suo costo. L'aiuto della riga di comando offriva per lo stato di un annuncio tre valori che il menu a tendina del foglio non contiene: due copie dello stesso elenco di valori ammessi, già divergenti. Ora l'elenco ha una sorgente sola. È ADR-013 applicato a un elenco invece che a un riferimento, e il principio è lo stesso: fra due forme si sceglie quella in cui la divergenza è impossibile, non quella in cui è silenziosa.

Dove leggere il dettaglio: [`refactor-12-indice-navigabile.md`](refactor-12-indice-navigabile.md).

## 13. Una fascia gratuita si misura, e la misura cambia l'architettura

Contesto. Il progetto ha deciso di diventare un'applicazione web autenticata, da usare dal browser e da vendere a un'agenzia, e la prima domanda è sembrata quella dell'hosting.

Com'era e perché era fragile. Il primo confronto fra piattaforme usava gli assi che il mercato propone, cioè costo, comportamento a riposo e ammissibilità dell'uso commerciale, e su quegli assi Firebase vinceva senza avversari. Gli assi mancanti erano quattro, e ciascuno corrisponde a una cosa che un'applicazione prima o poi chiede: codice lato server, lavoro ricorrente, segreti verso servizi esterni, archiviazione di file. Sul piano gratuito di Firebase nessuna delle quattro è disponibile, perché le funzioni non si distribuiscono su quel piano, e questo non era un dettaglio di configurazione ma il perimetro permanente di ciò che l'applicazione potrà fare senza pagare. Il confronto era stato fatto sugli assi del listino invece che su quelli del programma.

Il salto senior e perché è meglio. Il metodo che ha sostituito il confronto generico ha tre regole. Gli assi si derivano dall'elenco delle capacità che il programma userà nell'arco previsto, non dal listino. I numeri si leggono sulla pagina del fornitore e si datano, perché tre delle esclusioni finali poggiano su frasi che soltanto la fonte primaria contiene, come il database gratuito di Render che scade dopo trenta giorni o la clausola non commerciale del piano Hobby di Vercel. E si distingue fra un limite che ferma e un limite che addebita, preferendo il primo: dove il limite ferma, "gratuito" è una proprietà del sistema e non una condizione da sorvegliare, che per un prodotto da vendere è la differenza fra nessun rischio e un rischio di margine. Applicato, il metodo ha ribaltato l'esito e ha scelto Cloudflare.

Il prezzo del salto è dichiarato invece di nascosto, e sta nel modo in cui si sbaglia. Con regole dichiarative una regola dimenticata nega l'accesso, quindi sbaglia rumorosamente; con un'interfaccia di programmazione una rotta che dimentica il controllo concede l'accesso, quindi sbaglia in silenzio, ed è il dato di un cliente visto da un altro. È lo stesso genere di difetto delle voci 6 e 8, e la contromisura è la stessa: rendere impossibile la forma sbagliata invece di raccomandare quella giusta.

Dove leggere il dettaglio: [`refactor-13-fasce-gratuite-misurate.md`](refactor-13-fasce-gratuite-misurate.md).

## 14. Due implementazioni dello stesso modello, e il presidio che le tiene insieme

Contesto. L'applicazione web calcola nel browser, quindi il motore deve esistere anche in TypeScript, mentre in Python esiste già ed è il riferimento verificato del progetto.

Com'era e perché era fragile. Il rischio non è la traduzione, che è meccanica: è il terzo mese, quando la legge di bilancio cambia un'aliquota e la si aggiorna in un posto solo, oppure quando un difetto si corregge su un lato e non sull'altro. Due implementazioni dello stesso modello finanziario non divergono con un errore, divergono con due numeri plausibili, e chi guarda uno dei due non ha modo di sapere che l'altro dice diversamente. Il progetto conosceva già questa forma di rischio fra motore Python e formule del workbook, e la teneva con test scritti a mano su un caso solo.

Il salto senior e perché è meglio. Il presidio ha tre pezzi. I parametri non si traducono: il generatore li legge per introspezione dalle dataclass di `parametri.py` e li riemette in TypeScript, così l'aggiornamento fiscale resta un file solo. I casi non sono casuali: sono il prodotto cartesiano delle sei decisioni che nel codice cambiano ramo, più sedici limiti aggiunti uno per uno con il nome di ciò che rompono, per duecentoundici casi che coprono i rami invece di coprire il volume. La tolleranza si dichiara prima di guardare gli scarti, ed è severa, 1e-9 relativo: le due implementazioni fanno le stesse operazioni nello stesso ordine, quindi devono coincidere quasi all'ultimo bit. Perché quella severità regga, la traduzione conserva l'ordine dei termini nelle somme e lo dichiara con un commento dove lo fa per questa ragione, perché la somma in virgola mobile non è associativa.

Il presidio ha ripagato prima di essere finito. Alla prima corsa il generatore è morto con una divisione per zero dentro il tasso interno di rendimento: un difetto del motore Python, presente da sempre e mai visto, perché `taeg_approssimato` non era chiamato da nessuno e nessun test lo copriva. Sui flussi mensili di un mutuo il fattore di sconto esce dai numeri rappresentabili ai due capi dell'intervallo di bisezione, e la divisione fallisce. Corretto trattando i due estremi per quello che sono, cioè un infinito col segno del flusso da una parte e un contributo nullo dall'altra, con l'aritmetica ordinaria invariata e un test di regressione sulle tre durate che attraversano le soglie.

La suite contiene infine un caso che deve fallire, cioè un vettore alterato di poco più della tolleranza, perché duecentoundici casi verdi alla prima esecuzione vanno sospettati prima di essere creduti: se il confronto scivolasse in un ramo sbagliato, il verde sarebbe indistinguibile da quello vero.

Dove leggere il dettaglio: [`refactor-14-vettori-di-riscontro.md`](refactor-14-vettori-di-riscontro.md).

## 15. L'autorizzazione in un posto solo, e la forma sbagliata resa impossibile

Contesto. Con la fase due dell'applicazione web nascono le prime rotte che leggono e scrivono dati di un'organizzazione, quindi il primo codice del progetto in cui un errore non produce un numero sbagliato ma il dato di un cliente visto da un altro.

Com'era e perché era fragile. La forma naturale, quella di ogni esempio, mette in ogni rotta le cinque righe che risolvono identità, appartenenza e ruolo. Non sono righe sbagliate: sono righe da ricopiare, e la ventesima rotta sarà scritta di fretta partendo da un copia e incolla in cui il controllo del ruolo si perde perché quella "tanto è solo una lettura". C'è anche un difetto più sottile, cioè che il gestore riceve il contesto grezzo e può leggersi da solo l'organizzazione chiesta dal chiamante: verifica e uso restano separati, e ogni volta che lo sono qualcuno prima o poi userà senza verificare. La differenza rispetto a un database con regole dichiarative è il verso dell'errore: là una regola dimenticata nega e rompe visibilmente, qui una rotta dimenticata concede e non rompe niente.

Il salto senior e perché è meglio. Una rotta non si registra chiamando il router, si dichiara passando da una funzione che pretende il ruolo minimo come parametro obbligatorio e consegna al gestore un contesto già autorizzato. Il ruolo non può mancare perché TypeScript non compila senza; il gestore non ha un percorso alternativo per ottenere l'organizzazione non verificata; e scrivere una rotta fuori dal registro richiede un gesto visibile in revisione, non una dimenticanza. È lo stesso principio delle voci 6 e 8, cioè rendere impossibile la forma sbagliata invece di raccomandare quella giusta, applicato per la prima volta a codice di rete. Il file che monta l'applicazione diventa una mappa di dieci righe dove il ruolo minimo di ogni rotta si legge senza aprire nient'altro.

Due dettagli della stessa voce meritano di essere ricordati. La gerarchia dei ruoli sta in una tabella sola, perché la forma sbagliata più comune è confrontare per uguaglianza e negare all'amministratore ciò che si concede al membro. E il codice di rifiuto è una decisione di sicurezza travestita da dettaglio: a chi non è membro si risponde non trovato e non vietato, perché un divieto esplicito confermerebbe l'esistenza di quell'organizzazione, e su un prodotto venduto a più agenzie l'esistenza di un cliente è già un'informazione che non ci appartiene.

Resta infine la difesa che non sta nel codice. Chiavi esterne, controllo sui valori ammessi del ruolo e cancellazione a cascata vivono nello schema, dove nessuna rotta distratta può aggirarli, e tre prove li verificano scrivendo direttamente sul database e pretendendo un rifiuto.

Dove leggere il dettaglio: [`refactor-15-autorizzazione-in-un-posto-solo.md`](refactor-15-autorizzazione-in-un-posto-solo.md).

## 16. Le estrazioni diventano un ingresso, e la simulazione diventa verificabile

Contesto. Il 9 settembre 2026 la simulazione probabilistica del foglio Rischio era l'ultima parte del modello con una sola implementazione: mille scenari di formule, controllati con cura ma dimostrati guardandoli. L'applicazione web ne ha bisogno nel browser, quindi una seconda implementazione andava scritta comunque, e la domanda era se scriverla con un presidio o senza.

Com'era e perché era fragile. Il presidio dei vettori della voce 14 funziona perché il motore è una funzione deterministica dei suoi input. Una simulazione non lo è: dipende anche dalle estrazioni, e Python e JavaScript non possono estrarre gli stessi numeri, perché il generatore pseudocasuale è diverso e in JavaScript non è nemmeno specificato dallo standard. La forma naturale, cioè una funzione che riceve un seme e un numero di scenari e estrae per conto proprio, è comoda da chiamare e impossibile da confrontare: due implementazioni entrambe giuste danno risultati diversi, e per distinguerle da una sbagliata servirebbero tolleranze statistiche larghe, cioè una suite che passa anche quando una delle due sbaglia.

Il salto senior e perché è meglio. La casualità si passa invece di contenerla: `simula` riceve le estrazioni ed è una funzione pura. Da questo discendono quattro cose che prima non erano possibili. I vettori portano con sé il campione di estrazioni, quindi il confronto fra Python e TypeScript resta bit per bit, con la stessa tolleranza di un miliardesimo usata per il resto del motore. Le proprietà si provano con estrazioni scelte a mano, e la prova si legge come l'enunciato invece di cercare fra mille scenari quello utile. Il confronto con il workbook diventa possibile, perché la funzione che rigenera le estrazioni riproduce seme e ordine di chiamata del foglio: sui trenta numeri che il foglio mostra lo scarto massimo è 1,5 su dieci alla tredicesima, e quei numeri sono ora congelati in un test, cioè un test del progetto contiene la misura fatta con un altro programma. E l'uso interattivo resta servito da una funzione di estrazione dichiaratamente fuori dal confronto, di cui si prova il solo requisito che ha, cioè la riproducibilità dallo stesso seme.

Due difetti trovati, entrambi dal confronto e non dalla lettura. Il primo è l'arrotondamento del mezzo: `ROUND` di Excel lo allontana da zero, `round` di Python lo porta al pari, `Math.round` di JavaScript lo alza. Su venticinque anni ridotti del dieci per cento la differenza è un anno di durata del mutuo, cioè centosettanta euro di rata annua, e si presentava su un lato solo del tornado, che è il modo in cui una differenza di convenzione somiglia a un difetto del modello. Il secondo è che la formula chiusa del debito residuo, a tasso nullo, divide per zero: nel foglio quel caso diventerebbe un errore che si propaga a due delle cinque distribuzioni, mentre nei due moduli è trattato come il limite in cui il capitale si rimborsa in parti uguali. È emersa anche un'approssimazione mai scritta, cioè che la simulazione tassa il ricavo con la cedolare sul canone libero qualunque sia il regime scelto: portata come parametro con lo stesso valore predefinito, così che il confronto resti esatto e l'applicazione possa passare l'aliquota giusta.

La regola generale che questa voce aggiunge: sospettare le funzioni omonime. Percentile, mediana e arrotondamento esistono in tutti e tre gli ambienti con lo stesso nome e convenzioni diverse, e la convenzione non sta nella firma. Uno scarto piccolo e sistematico è il modo peggiore di sbagliare, perché somiglia a un errore di arrotondamento e non lo è.

Dove leggere il dettaglio: [`refactor-16-estrazioni-come-ingresso.md`](refactor-16-estrazioni-come-ingresso.md).

## 17. La stessa regola dalle due parti, scritta una volta

Contesto. Il 14 settembre 2026 comincia la fase tre, cioè la prima delle sei aree dell'interfaccia. Fino al giorno prima l'applicazione aveva un lato solo, il Worker, e la forma di un immobile viveva dentro il file delle sue rotte: era la scelta giusta, perché l'unico chiamante era una prova automatica. Nasce ora un secondo lato che quella forma la produce, e la premessa cambia senza che il codice sia cambiato.

Com'era e perché era fragile. La forma naturale è che il browser si scriva la propria copia della validazione, perché gli serve per dire subito che cosa non va. Le due copie divergono, e i due versi della divergenza non sono simmetrici: un'interfaccia più severa del server produce un fastidio che si segnala, una più permissiva produce un modulo che dice tutto bene e un rifiuto che arriva dopo, in una forma pensata per un programma, su un campo che il modulo non sapeva evidenziare. Lo stesso vale per i valori predefiniti, che non sono un dettaglio dell'interfaccia ma parte della forma: se li scrivono in due, un immobile creato dal modulo e uno creato da una chiamata diretta nascono diversi e nessuno dei due è sbagliato. E vale per la gerarchia dei ruoli, che l'interfaccia deve conoscere per non mostrare un pulsante destinato a un rifiuto: scritta due volte, riproduce dal lato del browser esattamente il difetto che la voce 15 aveva chiuso dal lato del server.

Il salto senior e perché è meglio. Nasce `app/src/condiviso/`, e le regole che due lati applicano si scrivono lì. Il punto da capire, e che si dimentica, è che le due applicazioni non hanno lo stesso statuto: quella del Worker è la difesa, perché chiunque può parlare all'interfaccia di programmazione senza passare dalla pagina, mentre quella della sezione è cortesia. Condividere la regola non toglie la difesa, toglie la seconda scrittura della stessa regola. La ripartizione delle prove segue: il contenuto si prova una volta sola su una funzione pura, l'applicazione si prova dove ha una conseguenza, cioè dentro il runtime di Cloudflare contro un D1 vero.

Quando i due lati non condividono il linguaggio, il modulo condiviso non esiste e la risposta era già nel progetto. Le trenta verifiche pre-acquisto vivevano come lista letterale dentro il generatore del foglio Checklist; ricopiarle in TypeScript sarebbe costato dieci minuti e avrebbe garantito che al primo aggiornamento normativo il foglio e l'applicazione mostrassero due elenchi di verifiche legali diversi. Il catalogo esce dal metodo, diventa `src/immobiliare/verifiche.py`, e il presidio che dal 7 settembre emette i parametri fiscali per introspezione guadagna una quarta uscita che lo emette in TypeScript. Non servono vettori di riscontro, perché non c'è un calcolo da verificare: serve che il testo sia lo stesso, e lo si ottiene generandolo. Scrivendo quel modulo avevo elencato a mano le fasi del percorso e ne mancava una, il che era già la seconda fonte di verità che il modulo esisteva per evitare: sostituita da una funzione che le ricava, con due prove che la presidiano nelle due direzioni.

La terza regola di questa voce riguarda una struttura dati con più autori. Le ipotesi di valutazione stanno in un documento JSON che sei aree scriveranno, e ciascuna ne conosce solo la propria parte: un'area che salvasse soltanto ciò che sa cancellerebbe il lavoro delle altre senza produrre nessun errore, e chi apre l'area del finanziamento il giorno dopo troverebbe i predefiniti al posto delle proprie assunzioni. La regola è che ciò che non si conosce si conserva, e la sua simmetrica sulla lettura è che ciò che non si riconosce non rompe. La prova che conta è quella del giro completo, perché è l'unica che fallisce quando qualcuno, mesi dopo, aggiunge una chiave e dimentica la copia.

Un difetto trovato, e dalla prova e non dalla lettura. L'anteprima delle imposte leggeva la base imponibile chiamando `baseImponibileRegistro`, che risponde correttamente alla domanda del registro e non sa dell'IVA: con venditore impresa mostrava il valore catastale accanto a un'IVA calcolata sul prezzo, cioè due numeri entrambi giusti nel proprio contesto e incoerenti fra loro. Il motore aveva già deciso quella base e la restituiva nel proprio esito; l'anteprima l'ha ricalcolata invece di leggerla. È la stessa regola con cui questo progetto tratta le formule del workbook, cioè non ricalcolare ciò che un'altra parte ha già stabilito, portata dentro l'interfaccia: le funzioni che rispondono a domande vicine hanno nomi vicini, e la prova che le distingue è la sola cosa che separa un'anteprima esatta da una plausibile.

Dove leggere il dettaglio: [`refactor-17-una-regola-due-lati.md`](refactor-17-una-regola-due-lati.md).

## 18. Il contesto nel guscio, e la conservazione che smette di essere una raccomandazione

Contesto. Il 14 settembre 2026, nella stessa giornata in cui nasce la prima area, ne nasce la seconda: il costo dell'operazione. L'area immobile possedeva tutto, cioè l'elenco, la selezione, il ciclo di salvataggio e la propria lettura del documento delle ipotesi, e nessuna di quelle scelte era sbagliata per una schermata che non ne aveva accanto altre.

Com'era e perché era fragile. La regola generale che questa voce isola è che una soluzione e un pattern non sono la stessa cosa: finché esiste un'istanza, il codice che risolve un problema è la soluzione di quel problema; dalla seconda in poi diventa qualcosa che qualcuno dovrà ricopiare correttamente. La domanda giusta, quando arriva la seconda istanza, non è se il codice della prima sia buono, ma quale sua parte, ricopiata male, fallirebbe in silenzio. Qui le parti erano quattro, in ordine crescente di danno: due caricamenti dell'elenco invece di uno, che è spreco e si vede; la selezione persa cambiando area, che è un fastidio e si vede; la conservazione di ciò che un'area non conosce ridotta a raccomandazione, che la quarta area dimenticherebbe cancellando il lavoro delle altre; e l'azzeramento della bozza quando cambia l'immobile aperto, che dimenticato mostra i dati del primo sotto il nome del secondo e fa sovrascrivere il secondo con il primo, senza errore e senza rifiuto.

Il salto senior e perché è meglio. Tre spostamenti, ciascuno con lo stesso carattere. La forma dell'intero documento delle ipotesi si dichiara in `app/src/condiviso/ipotesi.ts`, e la conservazione smette di essere una raccomandazione perché `conSezione` è l'unica funzione che produce un documento nuovo e sparge sempre due volte: il primo spargimento tiene le sezioni delle altre aree, il secondo tiene i campi che un'altra versione aveva scritto dentro questa sezione, che è la stessa perdita un piano più in basso. I predefiniti con cui si riempie un campo assente non si trascrivono dal motore Python: il presidio guadagna una quinta uscita che li emette per introspezione dalle dataclass di `calcoli.py`, e i tre che non può vedere, perché sono predefiniti di funzione e non campi, si derivano da dove il progetto li dichiara comunque e la derivazione si presidia con una prova che chiama il motore con e senza e pretende lo stesso esito. E il contesto di lavoro, cioè l'elenco, l'immobile aperto e il ciclo di salvataggio, passa al guscio: un'area riceve l'immobile, il ruolo e una funzione che salva, e non riceve il cliente, perché con il cliente in mano potrebbe fare per conto proprio tutto ciò che si è appena tolto.

Due dettagli del ciclo di bozza valgono scritti perché sono il genere di cosa che si riscopre a caro prezzo. Il primo è che cosa si osserva per decidere quando ripartire: non l'oggetto, che cambia identità a ogni ricarica dell'elenco e butterebbe via ciò che si sta scrivendo, e non il solo identificativo, perché dopo un salvataggio l'immobile è lo stesso ma il contenuto no; si osserva identificativo e data di ultima modifica insieme. Il secondo l'ho trovato scrivendo la prova e non leggendo il codice: il salvataggio fa arrivare un immobile nuovo, quindi l'effetto che riazzera la bozza spegneva il messaggio di conferma appena mostrato, e l'utente avrebbe visto un lampo e nessuna conferma.

Due forme minori, con la stessa idea dietro. Uno stato che non può esistere non si rappresenta con un valore neutro ma con un tipo che lo esclude: l'area del costo si divide in un componente esterno che decide se c'è un immobile e uno interno che ne riceve uno esistente per il compilatore e non solo per convinzione, e `rimuovi` vale null quando non c'è nulla di aperto invece di essere una funzione che non fa niente. E un confine fra aree si dichiara invece di essere difeso: il regime di acquisto cambia il numero più grande della tabella del costo e pure appartiene all'area immobile, quindi lì si mostra con scritto dove si cambia, perché un valore modificabile da due schermate è un valore di cui nessuno sa più dove si cambia.

Dove leggere il dettaglio: [`refactor-18-contesto-nel-guscio.md`](refactor-18-contesto-nel-guscio.md).
