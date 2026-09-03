# Fiscalità dell'acquisto

> Scheda di dominio, aggiornata al 28 agosto 2026 con i parametri della legge di bilancio 2026, legge 30 dicembre 2025 n. 199. I numeri operativi vivono in `src/immobiliare/parametri.py` e nel foglio Parametri del workbook: questa scheda spiega la logica, non duplica le cifre. Le fonti puntuali stanno in [`fonti.md`](fonti.md).

## Il bivio che determina tutto: chi vende

La prima domanda da farsi non riguarda l'immobile ma il venditore, perché da lì discende l'intero impianto impositivo. Se vende un privato, o un'impresa in regime di esenzione, l'operazione sconta l'imposta di registro in misura proporzionale e le imposte ipotecaria e catastale in misura fissa da cinquanta euro ciascuna. Se vende un'impresa costruttrice o ristrutturatrice con cessione soggetta a IVA, l'IVA sostituisce il registro proporzionale e le altre tre imposte diventano fisse da duecento euro ciascuna.

La cessione da impresa è soggetta a IVA quando avviene entro cinque anni dall'ultimazione dei lavori, oppure oltre i cinque anni se l'impresa esercita in atto l'opzione per l'imponibilità. Fuori da questi casi la cessione è esente e si ricade nel primo scenario, con il registro proporzionale. La distinzione non è una sottigliezza: su un immobile da centoventimila euro il passaggio dal registro all'IVA cambia il conto di diverse migliaia di euro, e cambia anche il momento in cui si paga, perché l'IVA si versa al venditore mentre il registro si versa al notaio che lo riversa all'erario.

## La regola prezzo-valore, che vale più dell'agevolazione stessa

Quando l'acquisto è fuori campo IVA, l'acquirente persona fisica che compra un immobile a uso abitativo può chiedere al notaio, espressamente in atto, che la base imponibile del registro sia il valore catastale invece del prezzo pattuito. Il valore catastale si ottiene rivalutando la rendita catastale del cinque per cento e moltiplicandola per centodieci se l'acquisto è agevolato prima casa, per centoventi negli altri casi.

L'effetto quantitativo è spesso maggiore di quello dell'agevolazione prima casa. Nell'esempio precaricato nel workbook, un immobile trattato a centoventimila euro con rendita catastale di quattrocentocinquanta euro ha un valore catastale di poco meno di cinquantaduemila euro: l'imposta di registro al due per cento si calcola su quest'ultimo, non sul prezzo, e scende da duemilaquattrocento euro a poco più di mille. Il prezzo-valore porta con sé altri due vantaggi che si dimenticano facilmente, la riduzione del trenta per cento dell'onorario notarile e la preclusione del potere di accertamento di valore dell'amministrazione finanziaria, che è una tutela sostanziale contro una rettifica futura.

Due avvertenze. La regola va chiesta, non si applica da sola, e va detto al notaio prima dell'atto. E nell'atto deve comunque comparire il prezzo realmente pattuito: dichiarare un prezzo inferiore a quello pagato fa decadere il beneficio, riapre l'accertamento e attiva le sanzioni, il che rende il pagamento in nero un modo particolarmente inefficiente di risparmiare, perché si rinuncia a una tutela certa in cambio di un risparmio incerto e sanzionabile.

## L'agevolazione prima casa

L'agevolazione porta il registro dal nove al due per cento, oppure l'IVA dal dieci al quattro, e riduce anche il moltiplicatore catastale da centoventi a centodieci. Non spetta sulle categorie A/1, A/8 e A/9, cioè abitazioni signorili, ville e castelli, che restano fuori in ogni caso e in regime IVA scontano l'aliquota ordinaria del ventidue per cento.

I requisiti sono tre e vanno tutti verificati prima dell'atto, perché è in atto che si rendono le dichiarazioni. L'immobile deve trovarsi nel Comune in cui l'acquirente ha la residenza, o in cui si impegna a trasferirla entro diciotto mesi dal rogito. L'acquirente non deve essere titolare esclusivo o in comunione col coniuge di un'altra abitazione nello stesso Comune. L'acquirente non deve possedere, su tutto il territorio nazionale, un'altra abitazione acquistata con la stessa agevolazione, salva la facoltà di rivenderla entro due anni dal nuovo acquisto agevolato.

Su quest'ultimo punto c'è la novità che vale la pena isolare, perché è recente e viene spesso riportata male. Il termine per rivendere la precedente abitazione agevolata è passato da uno a due anni con l'articolo 1 comma 116 della legge 207/2024, e vale per gli atti stipulati dal primo gennaio 2025 e per quelli del 2024 il cui termine annuale non era ancora scaduto al 31 dicembre 2024. Resta invece fermo a un anno il termine diverso e spesso confuso con questo, quello entro cui riacquistare un'altra prima casa dopo aver venduto infra quinquennio, per non decadere dai benefici goduti sul primo acquisto.

Una precisazione sull'acquisto congiunto, perché è il caso che genera più errori. In comunione legale dei beni entrambi i coniugi devono intervenire in atto e rendere le dichiarazioni di legge: il beneficio non si estende automaticamente al coniuge che diventa comproprietario per effetto della comunione ma non ha partecipato all'atto. In separazione dei beni ciascuno risponde per sé, e il concetto di residenza della famiglia non opera, per cui il mancato trasferimento della residenza da parte di uno dei due comporta la decadenza per la sua quota.

Va infine sgombrato il campo da un equivoco diffuso: l'esenzione da registro, ipotecaria e catastale per gli under 36, introdotta dall'articolo 64 del decreto legge 73/2021, non è più in vigore, essendo scaduta il 31 dicembre 2023 salvo la coda sui preliminari registrati entro quella data. Quello che resta per i giovani è il fondo di garanzia Consap, che è cosa diversa: non riduce le imposte, garantisce la banca e permette di ottenere un finanziamento oltre l'ottanta per cento del valore.

## Il fatto che l'agevolazione si consuma

L'agevolazione prima casa è una risorsa a consumo, non un diritto ricorrente: usarla oggi significa non poterla usare sul prossimo acquisto finché non si è rivenduto. La conseguenza pratica riguarda chi compra un immobile per metterlo a reddito pur avendo in mente, fra qualche anno, l'acquisto dell'abitazione in cui vivere. In quel caso il calcolo corretto non è quanto si risparmia oggi, ma quanto si rinuncia domani, ed è un confronto che il workbook rende esplicito con la riga sul valore del bonus nel foglio Immobile.

C'è poi il vincolo quinquennale. Se si rivende entro cinque anni dall'acquisto agevolato senza riacquistare un'altra prima casa entro un anno, si decade: si versano le imposte risparmiate, gli interessi e una sanzione del trenta per cento. Il vincolo non riguarda l'uso dell'immobile ma la sua rivendita: affittare l'immobile acquistato con l'agevolazione, mantenendo la residenza nel Comune, non comporta decadenza, perché la legge chiede la residenza nel Comune e non l'occupazione materiale dell'alloggio.

## Il costo del finanziamento

Sul contratto di mutuo ipotecario si paga l'imposta sostitutiva, che assorbe registro, bollo, ipotecarie e catastali relative al finanziamento: è lo zero virgola venticinque per cento se il mutuo è destinato all'acquisto della prima casa, il due per cento negli altri casi. La banca la trattiene direttamente dall'erogato, quindi non è un esborso che si vede ma un importo che non si riceve. L'ottuplicarsi dell'aliquota sulla seconda casa è una delle voci che rende l'acquisto per investimento sensibilmente più caro di quanto si preventivi a mente.

Gli altri oneri sono l'istruttoria, spesso azzerata nelle offerte commerciali, la perizia, la polizza incendio e scoppio che è obbligatoria per legge, e l'onorario del notaio per l'atto di mutuo, che è una fattura distinta da quella della compravendita. La polizza vita o sulla perdita dell'impiego, invece, è facoltativa: la banca non può subordinare la concessione del credito alla sua sottoscrizione, e chi se la sente proporre come condizione ha titolo per contestarlo.

## La detrazione degli interessi passivi

Gli interessi passivi e gli oneri accessori del mutuo ipotecario per l'acquisto dell'abitazione principale danno diritto a una detrazione IRPEF del diciannove per cento, su un massimale di quattromila euro l'anno di interessi, quindi al massimo settecentosessanta euro l'anno. Il requisito è che l'immobile sia adibito ad abitazione principale, con residenza trasferita entro dodici mesi dall'acquisto, e non entro diciotto come per l'agevolazione prima casa: sono due termini diversi per due benefici diversi, e confonderli è l'errore più comune in questa materia.

Il massimale è riferito all'immobile e non alla persona, quindi va ripartito fra i cointestatari del mutuo: con due intestatari al cinquanta per cento ciascuno detrae il diciannove per cento su duemila euro, non su quattromila. Il workbook lo gestisce con il campo della quota di acquisto.

Fra gli oneri accessori detraibili rientrano l'onorario del notaio per l'atto di mutuo, la perizia, l'istruttoria, la commissione di intermediazione bancaria, la penale per estinzione anticipata e l'imposta sostitutiva. Non rientrano invece l'assicurazione dell'immobile neppure quando la richiede la banca, la provvigione di mediazione immobiliare, l'onorario del notaio per l'atto di compravendita e le imposte di registro, IVA, ipotecaria e catastale.

Sull'immobile comprato per affittare la detrazione non spetta, perché manca il requisito dell'abitazione principale. È una differenza che pesa: nella colonna della locazione il workbook la azzera automaticamente in funzione del campo che dichiara la destinazione.

## La plusvalenza in uscita

La rivendita genera plusvalenza imponibile se fra acquisto e cessione passano meno di cinque anni, ai sensi dell'articolo 67 comma 1 lettera b del TUIR. Non è imponibile, anche dentro il quinquennio, se l'immobile è stato adibito ad abitazione principale del cedente o dei suoi familiari per la maggior parte del periodo di possesso, né se è pervenuto per successione. In atto si può chiedere al notaio l'applicazione dell'imposta sostitutiva del ventisei per cento in luogo della tassazione IRPEF ordinaria, il che conviene a chiunque abbia un'aliquota marginale superiore.

Dal 2024 esiste una finestra più lunga per gli immobili oggetto di interventi agevolati con superbonus: la plusvalenza è imponibile se la cessione avviene entro dieci anni dalla conclusione dei lavori, con le stesse esclusioni per successione e per abitazione principale. È un elemento da verificare sempre in fase di acquisto, non solo di vendita, perché condiziona la liquidità futura dell'immobile e quindi la strategia di uscita.

## Il possesso: IMU

L'abitazione principale non di lusso è esente da IMU. Restano imponibili le categorie A/1, A/8 e A/9 anche se abitazione principale, con aliquota ridotta e detrazione di duecento euro. Ogni altro immobile paga, con base imponibile pari alla rendita catastale rivalutata del cinque per cento e moltiplicata per centosessanta per i fabbricati del gruppo A esclusa la A/10.

L'aliquota base di legge è lo zero virgola ottantasei per cento, ma i Comuni possono azzerarla o portarla fino all'uno virgola zero sei: il valore da mettere nel modello è quello della delibera comunale dell'anno in corso, non quello di legge. È la voce che, insieme alle spese condominiali, varia di più da un immobile all'altro e che più spesso viene sottostimata nelle valutazioni fatte a mente. Per i contratti a canone concordato l'imposta è ridotta del venticinque per cento, cioè si versa il settantacinque per cento del dovuto.
