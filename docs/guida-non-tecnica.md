# Guida d'uso, senza gergo

> Per chi vuole usare lo strumento senza sapere come è fatto. Si legge una volta, poi si tiene aperta accanto al file. Ogni voce spiega che cosa è, perché conta e da quale norma discende. La versione per chi mette le mani nel codice è in `guida-tecnica(catena-calcolo-e-normativa).md`.

## Che cosa è questo file e che cosa non è

È un foglio di calcolo che risponde a tre domande: quanti soldi servono davvero per comprare un immobile, quanto rende se lo si affitta, e se conviene comprarlo oppure no. Non è una consulenza e non decide al posto tuo: mette in fila i numeri che di solito si tengono a mente male, e ti fa vedere di quanto cambia il risultato quando cambia un'ipotesi.

Non risponde invece a due domande che spesso gli si vorrebbe fare. Non dice se un immobile è bello o se la zona è buona, perché quelle sono valutazioni che si fanno con gli occhi e con i piedi. E non dice se il prezzo è giusto in assoluto, ma solo se sta dentro o fuori il mercato della sua zona, confrontandolo con le quotazioni ufficiali dell'Agenzia delle Entrate.

## Come si apre

Il file si chiama `Valutazione-Immobile.xlsx` e sta nella cartella `output`. Se non c'è, o se qualcuno ha cambiato il modello, si rigenera facendo doppio clic su un terminale e scrivendo questa riga dentro la cartella del progetto.

```
python tools/valuta.py excel --con-annunci
```

Una cosa da sapere subito, perché evita un dispiacere. Ogni volta che si esegue quel comando il file viene **riscritto da zero**. Quello che hai digitato dentro va perso. Se ci hai lavorato e vuoi tenerlo, salvalo con un altro nome, per esempio `Valutazione-via-Roma-12.xlsx`, e lavora su quello.

## I colori dicono cosa toccare, e la riga in alto dice che cosa fare

Prima di tutto il resto, due cose che rendono il file navigabile senza sapere niente.

I colori delle celle sono cinque e significano cinque cose diverse. **Giallo**: ci scrivi tu, un numero o un testo, e sono le uniche celle da compilare. **Azzurro**: ci scegli da un elenco, clicchi la cella e compare una freccia a destra; un valore scritto a mano fuori dall'elenco viene rifiutato, ed è voluto. **Grigio**: la calcola il foglio, e se ci scrivi rompi il calcolo senza che nessun messaggio te lo dica. **Verde**: risultato di sintesi, è quello che sei venuto a leggere. **Rosso**: attenzione, un valore ha superato una soglia oppure un controllo non è superato. La legenda con i colori mostrati sta in testa al primo foglio.

Ogni foglio, in alto, ha una riga che dice in una frase se quello è un foglio dove si scrive o uno dove si legge, quando conviene aprirlo e che cosa ne esce. Se quella riga è gialla si compila, se è grigia si legge e non si tocca niente. Accanto, a sinistra, c'è il collegamento che riporta all'indice.

## I colori nel dettaglio

C'è una sola regola e vale in tutto il file. Le celle **gialle** sono le tue: quelle le compili tu. Le celle **grigie** sono calcolate: se ci scrivi dentro rompi la formula e il numero smette di aggiornarsi. Le celle **verdi** sono i risultati, quelli che devi guardare.

Quando un numero diventa rosso, o una cella si colora di rosa, è un avviso: qualcosa è sopra soglia, o negativo, e vale la pena capire perché.

## L'indice, e come si gira fra i fogli

Il primo foglio del file è un indice. Elenca tutti gli altri in ordine di lettura, raggruppati per fase, e per ognuno dice tre cose: se lì si scrive o si legge, quando lo si apre nel percorso, e che cosa ne esce. Ogni nome è un collegamento: ci si clicca e si va. Da ogni foglio si torna all'indice cliccando **<< Indice** in alto a sinistra, appena sotto il titolo.

Serve perché venti fogli sono troppi da tenere a mente, e le linguette in basso non dicono in che ordine leggerli né quali riguardano il tuo caso. Diversi fogli, per esempio Asta o Comproprietà, servono solo in situazioni particolari, e l'indice lo dice riga per riga così non li apri per curiosità e poi ti chiedi se avresti dovuto compilarli.

## L'ordine in cui si lavora

Il file ha sedici schede in fondo alla finestra. Non servono tutte insieme e non si leggono da sinistra a destra. L'ordine giusto è questo.

### Primo, la scheda Annunci

Qui ci metti gli immobili che stai guardando, uno per riga. All'inizio bastano quattro cose: il link, il Comune, i metri quadri e il prezzo richiesto. Se sai anche quanto pensi di affittarlo, mettilo, perché è quello che fa funzionare il resto.

Tre colonne si compilano da sole e non vanno toccate. Il **prezzo al metro quadro** è il prezzo diviso i metri quadri, ed è l'unico modo per confrontare immobili di taglia diversa. Lo **scarto su OMI** confronta quel prezzo al metro quadro con le quotazioni ufficiali della zona: se è verde stai sotto il mercato di zona, se è rosso stai sopra. Il **rendimento lordo** è il canone di un anno diviso il prezzo, ed è il numero che si legge negli annunci: serve per scremare, non per decidere.

Le quotazioni OMI si ottengono gratis dal sito dell'Agenzia delle Entrate, cercando "quotazioni immobiliari OMI", e si inseriscono a mano nelle due colonne apposite. È un lavoro di cinque minuti per Comune che ripaga per tutte le valutazioni successive.

In fondo alla riga ci sono due colonne che vale la pena compilare quando la lista mescola immobili diversi fra loro. "Prima casa" dice se quell'immobile sarebbe prima casa per te, e la risposta può cambiare da riga a riga: nel Comune dove hai la residenza sì, in un altro dove hai già un'abitazione no. "Venditore impresa" dice se compri da un costruttore o da un'impresa, cioè con l'IVA, invece che da un privato. Se le lasci vuote la riga usa quello che hai impostato nella scheda Immobile, quindi non devi compilarle per forza; se però in lista hai un usato da privato accanto a un nuovo da costruttore e non le compili, le imposte sono calcolate uguali per tutti e la classifica ti indica come migliore proprio l'immobile che costa più di imposte.

### Secondo, la scheda Confronto immobili

Non si compila: si legge. Prende tutti gli annunci della scheda precedente e applica a ciascuno lo stesso calcolo completo, imposte comprese, mettendoli in fila.

Qui la cosa da guardare non è il rendimento lordo ma il **cash flow**, che è la cassa che l'immobile ti mette in tasca o ti toglie ogni anno dopo aver pagato tutto, rata del mutuo inclusa. È normale che sia negativo quando c'è un mutuo importante: significa che ogni mese ci metti dei soldi tuoi, e la domanda diventa se te lo puoi permettere, non se l'operazione è buona.

L'altro numero è il **DSCR**, che confronta quanto rende l'immobile con quanto costa la rata. Sotto 1 il reddito dell'immobile non copre la rata, e la differenza esce dalla tua tasca.

Accanto a questi numeri la scheda porta la zona OMI dell'immobile, le due quotazioni al metro quadro di quella zona e lo scarto del prezzo rispetto alla loro media. Uno scarto negativo dice che si sta trattando sotto la media della zona, uno positivo che si sta trattando sopra, e nessuno dei due è un giudizio: la quotazione è una media di zona per tipologia, quindi non vede lo stato di conservazione, il piano, l'affaccio, la classe energetica né i lavori deliberati in condominio. Serve a sapere quali righe vale la pena capire, non a ordinarle.

Una differenza da tenere presente fra le due schede. Lo scarto della scheda Annunci è calcolato sul prezzo richiesto dal venditore, quello della scheda Confronto immobili sul prezzo che il calcolo sta effettivamente usando, cioè l'obiettivo quando è compilato. La distanza fra i due numeri è, letta al contrario, lo sconto che si sta chiedendo.

Da qui esce il candidato su cui vale la pena spendere tempo. Gli altri restano in lista.

### Terzo, la scheda Immobile

È il cuore. Qui metti i dati veri dell'immobile scelto, e ne escono le imposte e il costo reale.

Le voci da compilare, una per una.

**Superficie commerciale** sono i metri quadri commerciali, che comprendono i muri e una quota di balconi e pertinenze, non i metri calpestabili. È la misura con cui si fanno i prezzi.

**Categoria catastale** si legge nella visura catastale. La A/2 è l'abitazione di tipo civile, la A/3 economica, la A/4 popolare. Conta perché A/1, A/8 e A/9, cioè signorile, villa e castello, sono escluse per legge dall'agevolazione prima casa.

**Rendita catastale** è nella visura, ed è il numero più importante del foglio dopo il prezzo. Non è il valore dell'immobile: è un valore fiscale convenzionale, di solito molto più basso, e su di esso si calcolano quasi tutte le imposte.

**Prezzo richiesto** e **prezzo trattato**: il primo è quello dell'annuncio, il secondo è quello che pensi di mettere nella proposta. Tutta l'analisi gira sul secondo.

**Venditore impresa con IVA** è la domanda che cambia tutto. Se vendi un privato si paga l'imposta di registro; se vende un'impresa costruttrice entro cinque anni dalla fine dei lavori si paga l'IVA. Sono due mondi diversi e il conto cambia di migliaia di euro.

**Agevolazione prima casa** riduce l'imposta di registro dal 9 al 2 per cento, oppure l'IVA dal 10 al 4. Per averla devi avere la residenza nel Comune dell'immobile o impegnarti a trasferirla entro diciotto mesi, non possedere un'altra casa in quel Comune, e non avere altrove un'altra casa già comprata con la stessa agevolazione, salvo rivenderla entro due anni. Il riferimento è la nota II-bis all'articolo 1 della tariffa allegata al DPR 131/1986, e il termine di due anni viene dall'articolo 1 comma 116 della legge 207/2024.

C'è una cosa che il foglio ti mostra e che quasi nessuno considera: l'agevolazione **si consuma**. Usata oggi, non è più disponibile sul prossimo acquisto finché non hai rivenduto. Se stai comprando per investimento e in futuro vuoi comprare la casa in cui vivere, il foglio ti dice quanto vale il bonus oggi, così puoi decidere se spenderlo adesso o tenerlo.

**Opzione prezzo-valore** è la voce che fa risparmiare di più, e va chiesta espressamente al notaio prima dell'atto perché non si applica da sola. Serve a far calcolare l'imposta di registro sul valore catastale invece che sul prezzo pagato. Nell'esempio caricato nel file, su un immobile da centoventimila euro l'imposta scende da circa duemilaquattrocento a poco più di mille. Porta con sé altre due cose che valgono: il notaio deve ridurre l'onorario del trenta per cento, e l'Agenzia delle Entrate non può più contestarti il valore dichiarato. La norma è l'articolo 1 comma 497 della legge 266/2005. Vale solo quando non c'è IVA, quindi non si applica all'acquisto dal costruttore.

**Quota di acquisto** è la tua parte se comprate in due: metti 50 per cento. Serve perché il tetto della detrazione degli interessi del mutuo è riferito all'immobile e va diviso fra chi lo compra.

**Destinato ad abitazione principale** va messo su SI solo se ci vai a vivere. Se lo compri per affittarlo va su NO, e il foglio azzera da solo la detrazione degli interessi e mette l'IMU, che sull'abitazione principale non si paga.

**Provvigione di agenzia**, di solito il tre per cento più IVA. Attenzione al momento in cui è dovuta: matura quando l'affare si conclude, cioè quando il venditore accetta la tua proposta, non al rogito.

**Notaio** e **altri costi**: il notaio della compravendita, e poi visure, tecnico di parte, allacci, accatastamento, l'arredo minimo. Sono le voci che si dimenticano e che pesano.

I risultati, in verde, sono tre. Il **totale delle imposte**, il **costo totale dell'operazione**, che è il numero da tenere in testa quando fai la proposta, e l'**esborso iniziale**, che è la cassa che ti serve davvero avendo tolto la parte che mette la banca. Se l'incidenza dei costi sul prezzo supera il dieci per cento la cella diventa rossa: vuol dire che una voce sta pesando troppo e vale la pena guardare quale.

### Quarto, la scheda Mutuo

Importo, tasso e durata. Il resto lo calcola il foglio, compreso il piano di ammortamento rata per rata nella scheda accanto.

Sul **tasso** c'è un comando che ti dice se il tuo preventivo è buono. Confronta il tasso che ti hanno offerto con la media di quello che le banche italiane hanno davvero applicato, presa dai dati ufficiali della Banca centrale europea, e ti traduce la differenza in euro.

```
python tools/valuta.py tassi --tasso 0.032 --mutuo 90000 --durata 25
```

Il **loan to value** è quanto ti presta la banca rispetto al valore dell'immobile. Sopra l'ottanta per cento serve una garanzia in più, di solito il fondo di garanzia Consap, e le condizioni peggiorano.

L'**imposta sostitutiva** è la tassa sul mutuo, che la banca trattiene direttamente da quello che ti eroga, quindi non la vedi uscire ma non ti arriva. È lo 0,25 per cento se il mutuo è per la prima casa e il 2 per cento in tutti gli altri casi: otto volte tanto, ed è una delle ragioni per cui comprare per investimento costa più di quanto si preventivi. Il riferimento sono gli articoli da 15 a 20 del DPR 601/1973.

La **detrazione degli interessi** vale il 19 per cento degli interessi pagati, su un tetto di quattromila euro l'anno, quindi al massimo settecentosessanta euro. Spetta solo sull'abitazione principale e richiede di trasferire la residenza entro **dodici** mesi, che è un termine diverso dai diciotto mesi dell'agevolazione prima casa: sono due benefici diversi con due scadenze diverse, e confonderli è l'errore più comune. La norma è l'articolo 15 comma 1 lettera b del TUIR.

Il **rapporto rata reddito** diventa rosso sopra il trentacinque per cento, perché è lì che le banche si fermano.

Se stai valutando un tasso **variabile**, la scheda Simulatore mutuo accanto serve esattamente a questo e va usata prima di firmare. Si compila il percorso del tasso a gradini: ogni riga dice da quale mese in poi il tasso è salito di quanto, e valgono i gradini man mano che si raggiunge il loro mese. Poi si guarda una riga sola, la rata massima raggiunta, e si risponde a una domanda sola: quella cifra la puoi pagare?

Sulla misura del rialzo da provare non affidarti all'intuizione, perché l'intuizione sbaglia in modo prevedibile. La cifra che viene in mente è un punto percentuale, che sembra prudente. Fra giugno 2022 e giugno 2023 l'Euribor a tre mesi, cioè l'indice a cui i mutui variabili sono agganciati, è salito di **3,78 punti in dodici mesi**: chi aveva provato un punto aveva provato un quinto di quello che poi è successo. La scheda riporta questo numero e quelli su due e tre anni, presi dalla serie ufficiale della Banca centrale europea che parte dal 1994, e suggerisce come distribuirlo in tre gradini. Sul caso di esempio del foglio quel rialzo porta la rata da 436 a 626 euro, cioè il quarantatré per cento in più.

Un avvertimento su una riga che sembra innocua. Se metti l'effetto "riduci durata", che è quello preimpostato, un rialzo forte non alza la rata ma allunga il piano, e il piano modellato si ferma a quarant'anni: può arrivare in fondo con del debito ancora da pagare. In quel caso la riga **Il piano si chiude** diventa colorata e dice NO, e le righe della durata e degli interessi totali vanno ignorate, perché stanno raccontando solo il pezzo di piano che ci stava nella tabella. Per il variabile italiano l'effetto corretto è "riduci rata", perché la banca tiene ferma la scadenza e alza la rata.

Cinque cose che la legge ti riconosce e che quasi nessuno usa, prese dalla guida ufficiale della Banca d'Italia sul mutuo ipotecario. La banca deve consegnarti gratuitamente il **PIES**, un prospetto standard europeo con le tue condizioni personalizzate, ed è l'unico modo per confrontare due offerte sulla stessa base. Quando ricevi l'offerta vincolante hai **sette giorni** di riflessione durante i quali l'offerta resta ferma. La **polizza incendio** è obbligatoria ma puoi portarne una tua presa altrove, purché equivalente, e la banca deve accettarla; hai sessanta giorni per disdire quella che ti hanno venduto. Attenzione alla forma del premio: esiste sia annuo sia unico anticipato per tutta la durata, e le banche propongono spesso il secondo finanziandolo dentro il mutuo, il che significa pagarci sopra anche gli interessi. Il foglio ti fa scegliere quale delle due, e nel caso del premio unico lo mette fra i costi che escono al rogito. Il tasso non può superare la **soglia d'usura**, che la Banca d'Italia pubblica ogni trimestre. E puoi consultare gratis la tua posizione in **Centrale dei Rischi**, cosa utile prima di chiedere, perché una pratica dimenticata aperta presso un mediatore pesa sulla delibera e si chiude revocando l'incarico per iscritto.

### Quinto, la scheda Locazione

Solo se l'immobile lo affitti. Metti il canone che pensi di ottenere, le spese condominiali e l'aliquota IMU, e il foglio mette a confronto quattro modi di tassare lo stesso affitto.

Sui due numeri che contano di più va detto qualcosa. Le **spese condominiali** vanno prese dal consuntivo degli ultimi due esercizi, non dalla stima dell'agenzia, e insieme al consuntivo vanno letti i verbali delle assemblee, perché i lavori già deliberati e non ancora fatti sono un costo tuo che arriva dopo il rogito. L'**aliquota IMU** va letta nella delibera del tuo Comune per l'anno in corso: la legge fissa una base dello 0,86 per cento ma i Comuni possono arrivare all'1,06, e la differenza su vent'anni non è piccola.

Due voci nuove che vale la pena non lasciare a zero. Il **costo figurativo del tuo tempo**: gestire un affitto costa ore, e se le conti a zero stai confrontando l'immobile con un investimento finanziario che di ore non ne chiede. Metti quante ore all'anno ci dedichi e quanto vale un'ora tua; per la locazione breve il foglio moltiplica quelle ore, perche' e' un'altra cosa. E il **moltiplicatore**: la locazione breve non e' un investimento passivo, e' piu' vicina a un mestiere.

I quattro regimi, in breve.

La **cedolare secca al 21 per cento** su contratto a canone libero, di solito quattro anni più quattro. È la scelta semplice: un'imposta fissa che sostituisce IRPEF, addizionali, imposta di registro e bollo. In cambio rinunci ad aggiornare il canone all'inflazione per tutta la durata.

Il **canone concordato con cedolare al 10 per cento**, contratto di tre anni più due. Il canone non lo decidi tu ma l'accordo territoriale del Comune, e serve l'attestazione di un'associazione firmataria. In cambio l'imposta è dimezzata e nella maggior parte dei Comuni l'IMU scende del venticinque per cento. Conviene o no a seconda di quanto è più basso il canone concordato rispetto al libero nella tua zona, e il foglio ti mette le due colonne affiancate proprio per farti vedere il confronto.

L'**IRPEF ordinaria**, in cui l'affitto si somma al tuo reddito. Conviene solo se hai un reddito basso. Per tutti gli altri è la scelta peggiore, e nell'esempio caricato nel file l'utile netto è addirittura negativo.

La **locazione breve**, cioè contratti sotto i trenta giorni. Ha il rendimento lordo più alto e i costi più alti, e dal 2026 ha regole nuove che vanno conosciute prima di costruirci sopra un piano. L'aliquota è il 21 per cento sulla prima unità e il 26 dalla seconda. Il regime copre al massimo **due** unità: dalla terza scatta la presunzione di attività d'impresa con obbligo di partita IVA. Serve il codice identificativo nazionale in ogni annuncio, la comunicazione degli ospiti alla questura, e i dispositivi di sicurezza obbligatori. Va infine letto il regolamento condominiale, perché se è di tipo contrattuale può vietare l'uso turistico e cancellare il piano in una riga.

Su questo punto c'è un avvertimento che viene da un parere raccolto sul campo e che il file non può darti da solo: destinare a locazione turistica un immobile comprato con l'agevolazione prima casa, comunicandolo come attività, può far perdere l'agevolazione e aggiungere la sanzione. La scelta sul regime di affitto e quella sull'agevolazione vanno fatte insieme, non una dopo l'altra.

### Sesto, le schede che si leggono

Nel foglio **Metriche** c'e' anche un controllo che non riguarda questo immobile ma tutto il tuo patrimonio: quanta parte e' gia' in mattone. Se superi i due terzi non hai un portafoglio, hai una scommessa sul mercato immobiliare della tua zona. E non consolarti pensando che l'immobiliare ti protegga quando le borse scendono: nelle recessioni i due si muovono insieme, perche' e' la stessa contrazione del credito a colpirli.

**Metriche** dà gli indicatori. Il **rendimento netto** è il numero da usare per decidere: è l'utile dopo tutti i costi e le imposte, diviso il costo totale. Fra il lordo che leggi negli annunci e questo netto si perdono di solito due punti e mezzo, e chi ti promette un netto vicino al lordo sta contando male. Il **cash on cash** dice quanto rende il denaro tuo che hai messo. Il **tasso interno di rendimento** è l'unico numero che puoi confrontare con il rendimento di un investimento finanziario, perché tiene conto anche di quanto vale l'immobile alla fine.

**Confronto affitto** risponde alla domanda se convenga comprare o restare in affitto investendo la differenza. Va letto sapendo che dipende quasi solo da tre ipotesi: quanto rende il portafoglio alternativo, quanto si rivaluta l'immobile e quanto pagheresti di affitto. Cambiando la prima di un punto l'esito spesso si rovescia, e questo dice che va usato come mappa, non come sentenza.

Se compri senza mutuo, in quella scheda compare da sola una riga di avvertenza, e conviene darle peso. Il confronto è costruito mettendo a paragone chi compra a debito e chi affitta investendo la differenza: senza mutuo la differenza non c'è più, perché tutto il capitale è già nell'immobile dal primo giorno, e il conto che esce risponde a un'altra domanda. In quel caso il numero da guardare è il tasso interno di rendimento nella scheda Metriche, confrontato con quanto renderebbe lo stesso capitale investito altrove.

Nella scheda **Scenari** trovi anche tre colonne affiancate, pessimistico, base e ottimistico, con canone, sfitto, morosità, tasso e rivalutazione impostabili uno per uno. È lì che si risponde alla domanda vera: non quanto rende se tutto va bene, ma **quanto ci rimetto ogni mese se va male**. Guarda la riga del cash flow annuo, dividila per dodici, e chiediti se quella cifra te la puoi permettere per anni.

**Scenari** è forse la scheda più utile di tutte, perché non ti dà un numero ma ti dice di quanto quel numero cambia se le cose vanno diversamente. C'è anche una riga che calcola il canone minimo sotto il quale l'immobile ti toglie cassa invece di dartene.

Nella stessa scheda, in fondo, c'è il numero che serve in trattativa: il **prezzo massimo** che l'immobile giustifica al rendimento che hai dichiarato accettabile, e lo scarto rispetto al prezzo di cui si sta parlando. Se lo scarto è negativo, quella è la cifra di sconto da ottenere perché l'operazione stia in piedi ai tuoi criteri. Sotto trovi una riga di verifica che ricalcola il rendimento a quel prezzo e mostra lo scarto dalla soglia: deve essere zero, e se non lo è significa che sei finito in un caso particolare, tipicamente un prezzo così basso che l'imposta di registro scatta al minimo di legge invece di essere proporzionale.

### Settimo, la scheda Comproprietà, se comprate in più di uno

Serve solo se l'immobile lo comprate in due o più. Una riga per persona: nome, quota, aliquota IRPEF e regime fiscale scelto.

La cosa da sapere prima di tutto: **non serve aprire una società**. Il codice civile dice che tenere insieme una cosa per goderne è comunione, non impresa. La società serve se fate impresa davvero, cioè comprate per ristrutturare e rivendere, o gestite affitti turistici in modo organizzato: in quel caso, se non la costituite, ne nasce comunque una di fatto in cui tutti rispondono con tutto.

Il foglio calcola la parte di ciascuno perché **sul fisco ciascuno fa storia a sé**: la cedolare secca si sceglie individualmente, quindi in due uno può stare in cedolare e l'altro in IRPEF, e la scelta giusta dipende dall'aliquota di ciascuno.

Tre regole che conviene conoscere prima di firmare. Le decisioni si contano **per quote, non per teste**: con il 51% governi la gestione, con i due terzi fai i lavori, per vendere servono tutti. Ciascuno può **vendere la sua quota a chi vuole**, e senza un patto di prelazione ti ritrovi in società con uno sconosciuto. E soprattutto: **chiunque può in ogni momento chiedere di sciogliere la comunione**, cioè costringere a vendere. L'unico antidoto è un patto di indivisione, che vale al massimo dieci anni e va rinnovato.

C'è una scheda dedicata che spiega tutto questo per esteso: `docs/comprare-in-piu-persone.md`.

### Ottavo, la scheda Checklist

È quella che si usa davvero quando si passa dalla valutazione all'offerta. Trenta verifiche divise per fase, con lo stato da spuntare e un contatore delle verifiche ancora aperte.

Il principio da capire, e da cui dipende tutto il resto: **una proposta di acquisto accettata dal venditore è già un contratto vincolante**. Da quel momento sei obbligato a comprare e la provvigione dell'agenzia è dovuta. Quindi o chiudi le verifiche prima di firmare, oppure le trasformi in condizioni scritte dentro la proposta stessa.

Le due condizioni che non devono mancare mai sono quella legata al mutuo, perché senza di essa se la banca non delibera perdi la caparra e paghi comunque l'agenzia, e quella che esclude la provvigione se la condizione non si avvera, che va scritta perché altrimenti l'agenzia può pretenderla lo stesso.

Le due verifiche tecniche che vanno fatte da un professionista e che sono spesso confuse fra loro sono la **conformità catastale**, cioè che la planimetria depositata corrisponda a com'è fatta la casa, e la **conformità urbanistica**, cioè che la casa corrisponda ai titoli edilizi rilasciati nel tempo. La seconda è quella che conta di più: è la difformità urbanistica che blocca la vendita e il mutuo, e il costo per sistemarla lo paga chi compra se non se ne accorge prima.

### Nono, la scheda Dossier tecnico

La Checklist dice che cosa verificare. Questa dice **quali carte ti servono per poterlo verificare**, ed è la lista che un ingegnere e un avvocato incaricati manderebbero all'agenzia. Sono sessantasei documenti divisi in nove famiglie: identificazione e titolarità, legittimità urbanistica, struttura e sismica, vincoli, impianti ed energia, condominio, nuova costruzione, occupazione e tributi, e garanzie legali e dichiarazioni in atto.

Per ciascuno trovi chi lo rilascia, la norma che lo rende dovuto, che cosa prova e che cosa rischi se manca, un costo indicativo, e le colonne gialle per segnare stato, data della richiesta e data di ricezione.

La colonna **Peso** dice quanto pesa l'assenza. *Bloccante* significa che senza quel documento l'atto è nullo, la banca non delibera oppure non si può sapere quanto costa sistemare le cose: ce ne sono ventisette. *Importante* significa che incide sul prezzo o sul rischio. *Se ricorre* significa che dipende dal caso, per esempio la fideiussione del costruttore, che su un usato non c'entra: quelle voci si marcano come non applicabili e spariscono dal conteggio.

Come si usa in pratica. Prima si marcano non applicabili le voci che non c'entrano con l'immobile in questione, poi si manda **una sola mail** con l'elenco di quello che resta, poi si segnano le date man mano che arrivano. In fondo al foglio c'è il completamento del fascicolo e il numero di documenti bloccanti ancora da avere, che compare anche sul Cruscotto.

Due cose da sapere prima di iniziare. La prima è che quello che l'agenzia non ha, quasi sempre esiste lo stesso: visure e planimetrie le prende un tecnico in giornata per poche decine di euro, i documenti del condominio li ha gratis l'amministratore, i titoli edilizi stanno in Comune. La seconda è che i titoli edilizi in Comune si ottengono con l'accesso agli atti, che però vuole la delega del proprietario o una proposta già firmata: è il motivo per cui la proposta si fa **condizionata** all'esito della verifica, invece di aspettare documenti che non arriveranno mai prima.

Il costo di tutta la verifica sta fra le seicento e le millecinquecento euro. Sembra molto finché non lo confronti con quello che costa scoprire dopo il rogito una difformità da sanare. La spiegazione distesa di ogni documento sta in `docs/perizia-pre-acquisto.md`.

## Le due voci da non lasciare al valore predefinito

Il file arriva con valori d'esempio ovunque, e vanno tutti sostituiti. Due però meritano di essere ripetute perché sono quelle che più spesso si lasciano come sono e falsano il risultato: l'**aliquota IMU**, che va presa dalla delibera del tuo Comune, e le **spese condominiali**, che vanno prese dal consuntivo.

## Che cosa il foglio non sa, e devi mettercelo tu

Non sa il rischio. Un immobile è un singolo bene, in una singola via, di un singolo Comune, e non si vende in tre giorni. Un investimento finanziario con lo stesso rendimento atteso non è la stessa cosa, e la differenza va aggiunta a mano nel giudizio.

Non sa il lavoro. Gestire un affitto significa registrare contratti, seguire assemblee, rincorrere manutenzioni e, nel caso brutto, gestire un inquilino che non paga con tempi che si misurano in anni. Quel tempo ha un valore che nessuna cella misura, e sulla locazione breve la componente di lavoro è tale che somiglia più a un mestiere che a un investimento.

Non sa perché stai comprando. La sicurezza di avere una casa tua, la libertà di cambiarla, il non dover traslocare quando decide qualcun altro sono cose che contano quando scegli dove vivere e non contano nulla quando scegli dove investire. Il foglio tratta solo la seconda domanda: se stai facendo la prima, guarda i numeri per sapere se te lo puoi permettere, non per sapere se conviene.

## Se qualcosa non torna

Se un numero sembra sbagliato, la prima cosa da controllare è se hai scritto dentro una cella grigia, perché in quel caso hai cancellato una formula: si rigenera il file e si ricomincia. Se il file non si rigenera e dice che non ha i permessi, è Excel rimasto aperto: chiudilo e riprova.

Se vuoi verificare che il modello nel suo insieme sia sano, c'è un comando che apre il file, ricalcola tutto e ti dice se c'è anche una sola cella in errore.

```
powershell -NoProfile -ExecutionPolicy Bypass -File tools\verifica-excel.ps1
```

## Da ricordare in una riga

Le aliquote di questo file sono quelle in vigore al 28 agosto 2026 e cambiano con ogni legge di bilancio. Prima di firmare qualunque cosa, le posizioni fiscali vanno confermate da un commercialista, quelle sull'atto da un notaio, e la conformità urbanistica da un tecnico. Questo è uno strumento per arrivare preparato a quelle tre conversazioni, non per sostituirle.
