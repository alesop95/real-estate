# 13. Una fascia gratuita si misura, e la misura cambia l'architettura

> Deep-dive della voce 13 di [`studio-didattico-master.md`](studio-didattico-master.md). Riguarda [`docs/architettura-web.md`](../../docs/architettura-web.md), la sezione delle piattaforme di distribuzione in [`docs/fonti.md`](../../docs/fonti.md), e le decisioni ADR-024 e ADR-025. È l'unica voce di questo racconto che non parte da una riga di codice, e vale come le altre perché l'errore che previene costa una riscrittura invece di un numero sbagliato.

## Il difetto, che era una frase e non un calcolo

Il progetto ha deciso di diventare un'applicazione web, e la prima domanda è sembrata quella dell'hosting. La prima risposta è stata Firebase, con tre argomenti buoni: autenticazione gestita, nessuna sospensione per inattività, e un piano gratuito che non chiede un metodo di pagamento. Tutti veri, tutti verificati sulla pagina del fornitore, e la scelta sarebbe stata difendibile.

Il difetto stava in ciò che non era stato chiesto. "Gratuito" era stato trattato come una proprietà del prezzo, mentre è una proprietà dell'architettura: una fascia gratuita non si limita a non farti pagare, ti proibisce delle cose, e le cose che proibisce diventano vincoli di disegno permanenti. Su Firebase, scrivendo la sezione della garanzia di gratuità, è emerso che le funzioni lato server non si possono distribuire sul piano che non può costare. Da lì, a cascata: niente lavori pianificati, niente segreti verso servizi esterni, niente archiviazione di file, niente operazioni che agiscano al di sopra delle regole di sicurezza. Non era un dettaglio di configurazione, era il perimetro di ciò che l'applicazione potrà mai fare senza pagare.

La domanda giusta è arrivata dall'utente e suonava così: esiste un full-stack gratuito senza quei vincoli? È la domanda che avrebbe dovuto essere la prima.

## Com'era il ragionamento, e perché era fragile

La prima stesura dello studio confrontava le piattaforme su tre assi: costo, comportamento a riposo, ammissibilità dell'uso commerciale. Sono gli assi che stanno in tutti gli articoli comparativi, e sono insufficienti, perché descrivono il servizio e non il programma che ci gira sopra. Con quegli assi Firebase vinceva senza avversari.

Gli assi che mancavano erano quattro, e ciascuno corrisponde a una cosa che un'applicazione prima o poi chiede. Esiste codice lato server dentro la fascia gratuita, o l'applicazione deve essere interamente client? Esiste lavoro ricorrente, cioè qualcosa che parta da sé a un'ora stabilita? Esistono segreti, cioè la possibilità di custodire una chiave che il browser non deve vedere? Esiste archiviazione di file? La differenza fra i due elenchi è tutta qui, e ribalta il risultato.

La fragilità del ragionamento vecchio non era il suo esito ma la sua forma: un confronto fatto sugli assi che il mercato propone, invece che sugli assi che il progetto userà.

## Il salto senior e perché è meglio

Il metodo che ha sostituito il confronto generico ha tre regole, e sono trasferibili a qualunque scelta di piattaforma.

La prima è che gli assi si derivano dal programma, non dal listino. Prima di guardare un prezzo si scrive l'elenco delle capacità che l'applicazione userà nell'arco previsto, comprese quelle non immediate, e ogni capacità diventa una colonna. Qui sono diventate sei: codice lato server, lavoro pianificato, segreti, archiviazione file, autenticazione gestita, isolamento fra clienti. Le prime quattro sono esattamente quelle su cui Firebase perde.

La seconda è che i numeri si leggono sulla pagina del fornitore e si datano. Nessuna delle cifre di questo studio viene da un articolo comparativo, e la differenza non è pedanteria: tre delle esclusioni finali poggiano su frasi che soltanto la fonte primaria contiene. Il Postgres gratuito di Render che scade trenta giorni dopo la creazione, con quattordici giorni di tolleranza, sta nella documentazione di Render e in nessuna tabella riassuntiva. Il divieto di uso commerciale del piano Hobby di Vercel sta in una riga della pagina del piano, e la sua definizione è tanto ampia che comprende chi viene pagato per scrivere il codice. La politica con cui Oracle recupera le istanze inattive sta nella sua documentazione, e contiene la sola cosa che conta, cioè che le tre condizioni valgono insieme e non separatamente.

La terza è che si distingue fra un limite che ferma e un limite che addebita, e si preferisce il primo. È il criterio che ha deciso fra le due finaliste e che chiamiamo gratuità strutturale: su Cloudflare, come su Firebase, il piano gratuito non richiede un metodo di pagamento, e il superamento di un limite fa fallire le richieste con un errore invece di generare una fattura. Su una piattaforma dove il limite addebita, "gratuito" è una condizione da sorvegliare per sempre; dove il limite ferma, è una proprietà del sistema. Per uno strumento che verrà venduto, la differenza è fra un rischio di margine e nessun rischio.

Applicato, il metodo ha prodotto un esito diverso dal primo: Cloudflare, che dà Workers per il codice lato server con centomila invocazioni al giorno, cinque attivazioni pianificate per account, sessantaquattro fra variabili e segreti per Worker, un database relazionale con cinque milioni di righe lette al giorno, e dieci gigabyte di archiviazione file con il traffico in uscita non fatturato. Nessuna carta, e il limite che ferma invece di addebitare.

## Il prezzo del salto, che va detto

Il metodo non ha prodotto una scelta migliore sotto ogni aspetto, e presentarla così sarebbe disonesto. Cloudflare costa più lavoro: non esiste un SDK con cui il browser parli direttamente al database, quindi ogni operazione passa da un Worker che va scritto, con la sua validazione e i suoi test. Sulla parte dati è forse due o tre volte il codice del percorso Firebase.

E sposta il modo in cui si sbaglia, che è la parte da tenere a mente. Con regole dichiarative su un database, una regola dimenticata nega l'accesso: l'errore si manifesta come un rifiuto, cioè rumorosamente. Con un'interfaccia di programmazione, una rotta che dimentica il controllo concede l'accesso: l'errore si manifesta come un silenzio, cioè come un dato di un cliente visibile a un altro. È lo stesso genere di difetto che questo progetto ha già incontrato due volte, nella voce 8 con i riferimenti per coordinata e nella voce 6 con il contratto posizionale, e la contromisura è la stessa: rendere impossibile la forma sbagliata invece di raccomandare quella giusta. Qui prende la forma di una regola vincolante, cioè che nessuna rotta interroghi il database da sola e che tutte passino da una funzione unica che risolve chiamante, organizzazione e ruolo, più la coppia di test per ciascuna rotta sul caso permesso e su quello negato.

## Come si estende il pattern

Quando si valuta una piattaforma, per questo progetto o per un altro, l'ordine è questo. Si scrive l'elenco delle capacità che il programma userà nell'arco previsto e si trasformano in colonne. Si leggono i numeri sulla pagina del fornitore, si citano con la data, e si registrano in [`docs/fonti.md`](../../docs/fonti.md) come qualunque altra fonte, perché una fascia gratuita è un fatto con una scadenza breve. Si separano i limiti che fermano da quelli che addebitano. Si scelgono i primi. E si scrive, accanto alla scelta, il prezzo che si è accettato, perché una decisione senza il suo prezzo dichiarato è una decisione che qualcuno rimetterà in discussione fra sei mesi senza sapere che era già stata pesata.

Una cosa in più, specifica di questo caso e utile altrove. Il numero che decide non è sempre quello grande: qui le quote di traffico e di database hanno due o tre ordini di grandezza di margine e non contano, mentre il limite che l'adozione può davvero incontrare sono i cinquanta utenti dell'autenticazione perimetrale. È anche l'unico numero dello studio che non viene dalla pagina del fornitore ma da ricostruzioni di terzi concordanti, e per questo è registrato fra le fonti come da riverificare prima di impegnarsi. Il limite più vicino e la fonte più debole erano lo stesso numero, e accorgersene è metà del lavoro.
