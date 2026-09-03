# Guida al workbook

> Guida d'uso completa del foglio di calcolo, per chi lo usa e per chi deve capirne le conclusioni senza toccare il codice. Nasce dalla fusione di due guide che avevano lo stesso destinatario, `guida-non-tecnica.md` e `guida-per-il-socio.md`, e ne conserva interamente il contenuto: la prima parte è il giro guidato che si legge una volta, la seconda è il riferimento cella per cella che si consulta quando serve.

Si legge da sola e si può mandare a un'altra persona: non richiede di avere il progetto sulla macchina, e i comandi che cita servono a chi lo genera, non a chi lo legge. La versione per chi mette le mani nel codice è in `guida-tecnica(catena-calcolo-e-normativa).md`, e la matematica dietro ogni formula in `matematica/matematica-finanziaria.tex`.

## Che cosa è questo file e che cosa non è

È un foglio di calcolo che risponde a tre domande: quanti soldi servono davvero per comprare un immobile, quanto rende se lo si affitta, e se conviene comprarlo oppure no. Non è una consulenza e non decide al posto tuo: mette in fila i numeri che di solito si tengono a mente male, e ti fa vedere di quanto cambia il risultato quando cambia un'ipotesi.

Non risponde invece a due domande che spesso gli si vorrebbe fare. Non dice se un immobile è bello o se la zona è buona, perché quelle sono valutazioni che si fanno con gli occhi e con i piedi. E non dice se il prezzo è giusto in assoluto, ma solo se sta dentro o fuori il mercato della sua zona, confrontandolo con le quotazioni ufficiali dell'Agenzia delle Entrate.

## Come si apre

Il file si chiama `Valutazione-Immobile.xlsx` e sta nella cartella `output`. Se non c'è, o se qualcuno ha cambiato il modello, si rigenera facendo doppio clic su un terminale e scrivendo questa riga dentro la cartella del progetto.

```
python tools/valuta.py excel --con-annunci
```

Una cosa da sapere subito, perché evita un dispiacere. Ogni volta che si esegue quel comando il file viene **riscritto da zero**. Quello che hai digitato dentro va perso. Se ci hai lavorato e vuoi tenerlo, salvalo con un altro nome, per esempio `Valutazione-via-Roma-12.xlsx`, e lavora su quello.

## A che domanda risponde lo strumento

A tre, e conviene sapere quali sono perché tutto il resto ne discende.

**Quanta cassa serve davvero per chiudere.** Non il prezzo: il prezzo più imposte di trasferimento, notaio, provvigione e oneri del mutuo. Su un immobile da centoventimila euro il costo reale sta attorno ai centotrentaduemila, e quei dodicimila non tornano alla rivendita.

**Quanto rende al netto di tutto,** e come si confronta con il non comprarlo. Fra il rendimento lordo che si legge negli annunci e il rendimento netto si perdono di norma due punti e mezzo. Chi promette un netto vicino al lordo sta contando male, o non sta contando le stesse cose.

**Quali verifiche vanno chiuse prima di firmare.** Una proposta accettata è già un contratto: le verifiche si chiudono prima, oppure diventano condizioni scritte nella proposta.

Quello che non fa: non è una consulenza fiscale, legale o finanziaria, e non sostituisce il notaio, il commercialista e il tecnico. Serve a sapere quali domande fare loro, e a non pagare per farsi dire un numero che si può calcolare da soli.

## I colori dicono cosa toccare, e la riga in alto dice che cosa fare

Prima di tutto il resto, due cose che rendono il file navigabile senza sapere niente.

I colori delle celle sono cinque e significano cinque cose diverse. **Giallo**: ci scrivi tu, un numero o un testo, e sono le uniche celle da compilare. **Azzurro**: ci scegli da un elenco, clicchi la cella e compare una freccia a destra; un valore scritto a mano fuori dall'elenco viene rifiutato, ed è voluto. **Grigio**: la calcola il foglio, e se ci scrivi rompi il calcolo senza che nessun messaggio te lo dica. **Verde**: risultato di sintesi, è quello che sei venuto a leggere. **Rosso**: attenzione, un valore ha superato una soglia oppure un controllo non è superato. La legenda con i colori mostrati sta in testa al primo foglio.

Ogni foglio, in alto, ha una riga che dice in una frase se quello è un foglio dove si scrive o uno dove si legge, quando conviene aprirlo e che cosa ne esce. Se quella riga è gialla si compila, se è grigia si legge e non si tocca niente. Accanto, a sinistra, c'è il collegamento che riporta all'indice.

## I cinque colori in tabella

La stessa cosa in forma di tabella, per averla sotto gli occhi mentre si compila. La legenda con i colori mostrati, e non descritti, sta in testa al primo foglio del workbook.

| Colore | Che cosa significa |
|---|---|
| Gialla | Ci scrivi tu, un numero o un testo. Sono le uniche celle da compilare, e sono poche per foglio. |
| Azzurra | Ci scegli da un elenco: clicca la cella e a destra compare una freccia. Un valore scritto a mano fuori dall'elenco viene rifiutato, ed è voluto. |
| Grigia | La calcola il foglio. Non ci si scrive: sovrascriverla rompe il calcolo in silenzio, cioè senza nessun messaggio di errore. |
| Verde | Risultato di sintesi. È quello che sei venuto a leggere, e viene sempre da celle gialle e azzurre compilate altrove. |
| Rossa | Attenzione. Un valore ha superato una soglia oltre la quale è un problema, oppure un controllo di plausibilità non è superato. |

## I colori nel dettaglio

C'è una sola regola e vale in tutto il file. Le celle **gialle** sono le tue: quelle le compili tu. Le celle **grigie** sono calcolate: se ci scrivi dentro rompi la formula e il numero smette di aggiornarsi. Le celle **verdi** sono i risultati, quelli che devi guardare.

Quando un numero diventa rosso, o una cella si colora di rosa, è un avviso: qualcosa è sopra soglia, o negativo, e vale la pena capire perché.

## L'indice, e come si gira fra i fogli

Il primo foglio del file è un indice. Elenca tutti gli altri in ordine di lettura, raggruppati per fase, e per ognuno dice tre cose: se lì si scrive o si legge, quando lo si apre nel percorso, e che cosa ne esce. Ogni nome è un collegamento: ci si clicca e si va. Da ogni foglio si torna all'indice cliccando **<< Indice** in alto a sinistra, appena sotto il titolo.

Serve perché venti fogli sono troppi da tenere a mente, e le linguette in basso non dicono in che ordine leggerli né quali riguardano il tuo caso. Diversi fogli, per esempio Asta o Comproprietà, servono solo in situazioni particolari, e l'indice lo dice riga per riga così non li apri per curiosità e poi ti chiedi se avresti dovuto compilarli.

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

# Parte prima: il giro guidato, scheda per scheda

Questa parte si legge una volta, nell'ordine, mentre si compila il file la prima volta. Racconta le schede nell'ordine in cui si aprono e spiega non solo che cosa scrivere ma perché, con le norme di riferimento dove servono. Chi cerca il significato di una singola cella può saltare alla seconda parte.

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

Due voci nuove che vale la pena non lasciare a zero. Il **costo figurativo del tuo tempo**: gestire un affitto costa ore, e se le conti a zero stai confrontando l'immobile con un investimento finanziario che di ore non ne chiede. Metti quante ore all'anno ci dedichi e quanto vale un'ora tua; per la locazione breve il foglio moltiplica quelle ore, perché è un'altra cosa. E il **moltiplicatore**: la locazione breve non è un investimento passivo, è più vicina a un mestiere.

I quattro regimi, in breve.

La **cedolare secca al 21 per cento** su contratto a canone libero, di solito quattro anni più quattro. È la scelta semplice: un'imposta fissa che sostituisce IRPEF, addizionali, imposta di registro e bollo. In cambio rinunci ad aggiornare il canone all'inflazione per tutta la durata.

Il **canone concordato con cedolare al 10 per cento**, contratto di tre anni più due. Il canone non lo decidi tu ma l'accordo territoriale del Comune, e serve l'attestazione di un'associazione firmataria. In cambio l'imposta è dimezzata e nella maggior parte dei Comuni l'IMU scende del venticinque per cento. Conviene o no a seconda di quanto è più basso il canone concordato rispetto al libero nella tua zona, e il foglio ti mette le due colonne affiancate proprio per farti vedere il confronto.

L'**IRPEF ordinaria**, in cui l'affitto si somma al tuo reddito. Conviene solo se hai un reddito basso. Per tutti gli altri è la scelta peggiore, e nell'esempio caricato nel file l'utile netto è addirittura negativo.

La **locazione breve**, cioè contratti sotto i trenta giorni. Ha il rendimento lordo più alto e i costi più alti, e dal 2026 ha regole nuove che vanno conosciute prima di costruirci sopra un piano. L'aliquota è il 21 per cento sulla prima unità e il 26 dalla seconda. Il regime copre al massimo **due** unità: dalla terza scatta la presunzione di attività d'impresa con obbligo di partita IVA. Serve il codice identificativo nazionale in ogni annuncio, la comunicazione degli ospiti alla questura, e i dispositivi di sicurezza obbligatori. Va infine letto il regolamento condominiale, perché se è di tipo contrattuale può vietare l'uso turistico e cancellare il piano in una riga.

Su questo punto c'è un avvertimento che viene da un parere raccolto sul campo e che il file non può darti da solo: destinare a locazione turistica un immobile comprato con l'agevolazione prima casa, comunicandolo come attività, può far perdere l'agevolazione e aggiungere la sanzione. La scelta sul regime di affitto e quella sull'agevolazione vanno fatte insieme, non una dopo l'altra.

### Sesto, le schede che si leggono

Nel foglio **Metriche** c'è anche un controllo che non riguarda questo immobile ma tutto il tuo patrimonio: quanta parte è già in mattone. Se superi i due terzi non hai un portafoglio, hai una scommessa sul mercato immobiliare della tua zona. E non consolarti pensando che l'immobiliare ti protegga quando le borse scendono: nelle recessioni i due si muovono insieme, perché è la stessa contrazione del credito a colpirli.

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

# Parte seconda: riferimento, cella per cella

Questa parte non si legge, si consulta. Sono le cinquantuno celle che accettano un valore, divise per foglio, con che cosa scrivere e perché serve. Le voci non sono scritte a memoria: sono estratte dal workbook generato, leggendo etichetta, colore di riempimento e nota di ogni cella di input, quindi l'elenco è completo per costruzione. Quando si aggiunge una cella al generatore, questa parte va rigenerata dalla stessa fonte.

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

# Parte terza: leggere il risultato, e decidere

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

## Le due voci da non lasciare al valore predefinito

Il file arriva con valori d'esempio ovunque, e vanno tutti sostituiti. Due però meritano di essere ripetute perché sono quelle che più spesso si lasciano come sono e falsano il risultato: l'**aliquota IMU**, che va presa dalla delibera del tuo Comune, e le **spese condominiali**, che vanno prese dal consuntivo.

## Un immobile vero, dall'inizio alla fine

Trilocale di settantacinque metri quadri a Civitanova Marche, in via Martiri di Belfiore. Richiesta ottantanovemila euro, già locato e arredato, primo e ultimo piano. È l'immobile `house_1` del registro, e lo si usa qui perché è l'unico dei quattordici a registro che ha un canone: il canone è il dato che sblocca il rendimento.

Ipotesi dichiarate: prezzo trattato ottantaduemila euro, mutuo di sessantacinquemilaseicento all'ottanta per cento del prezzo, tasso 3,2 per cento su venticinque anni, canone cinquecentocinquanta euro al mese, cedolare secca. L'aliquota IMU è quella base di legge perché la delibera del Comune non è ancora stata letta: è uno dei quattro controlli che il foglio segnala come non superati.

| Grandezza | Valore | Lettura |
|---|---|---|
| Costo reale | 90.705 € | contro 82.000 di prezzo: 10,6 per cento di costi accessori |
| Cassa al rogito | 25.105 € | da avere sul conto il giorno dell'atto |
| Rendimento netto | 3,23 % | nominale; 1,21 per cento reale, al netto del due di inflazione |
| Cap rate | 4,59 % | il rendimento dell'immobile, prima del debito e delle imposte |
| Cash on cash | -3,52 % | sul capitale proprio: la cassa del primo anno è negativa |
| Cash flow annuo | -883 € | cioè settantaquattro euro al mese di tasca propria |
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

## Tre cose che il foglio non sa e che devi mettere tu

Le prime due ripetono in altre parole i limiti qui sopra, e la terza non compare da nessun'altra parte.

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

## Avvertenza

Questa guida accompagna uno strumento di analisi personale e non costituisce consulenza fiscale, legale o finanziaria. I numeri dell'immobile riportati sopra sono ipotesi di lavoro su una trattativa in corso: il prezzo trattato è una strategia di acquisto e non un valore di mercato.
