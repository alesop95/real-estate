# Work-log

> Append-only, in ordine cronologico inverso. Ogni voce riporta data, file toccati, motivo.

## 2026-08-31, undici annunci a registro, le aste nel perimetro, recap operativo

File toccati: `src/immobiliare/annunci.py`, `src/immobiliare/excel_builder.py`, `tools/valuta.py`, `tests/test_workbook.py`, `docs/aste-immobiliari.md` nuovo, `docs/raccolta-annunci.md`, `docs/fonti.md`, `CLAUDE.md`, `README.md`, `.claude/context/roadmap.md`, `.claude/memory/decisions.md` con ADR-012.

Registro. Aggiunti otto link forniti dall'utente, portando il registro a undici immobili. Uno era gia' presente e il riconoscimento dei duplicati per link normalizzato lo ha rifiutato, che e' la prima volta che quella difesa serve davvero. Un link accorciato di Google e' stato risolto seguendo i reindirizzamenti e si e' rivelato un annuncio su casa.it. Due annunci sono marcati a priorita' dieci su indicazione dell'utente.

Il campo del punteggio esisteva senza semantica dichiarata: ora e' documentato come priorita' da zero a dieci assegnata a mano, e non come punteggio calcolato, perche' il modello ha gia' metriche proprie e sovrapporne una sintetica servirebbe solo a nascondere il ragionamento. Nuova azione `annunci modifica`, che mancava: marcare la priorita' o correggere un campo di un annuncio gia' a registro richiedeva di rifare la riga.

Le aste entrano nel perimetro, ed e' un cambio di decisione. La roadmap le dichiarava fuori, con la motivazione che seguono regole proprie e meriterebbero uno strumento separato: la motivazione era corretta sui fatti e sbagliata nella conclusione, perche' quelle regole proprie sono poche e circoscritte mentre imposte, mutuo, rendimento e confronto valgono identici. La voce di roadmap e' stata sostituita dichiarando il superamento invece di essere cancellata, e la decisione e' ADR-012.

Cosa e' stato costruito: cinque campi nel registro, il foglio Asta, sette voci nel Dossier tecnico che sale a settantatre' documenti in dieci famiglie, e la scheda `docs/aste-immobiliari.md`. Le norme sono state verificate sui testi primari del corpus, non su fonti divulgative: l'articolo 2922 del codice civile che esclude la garanzia per i vizi e l'impugnazione per lesione, il 2923 sull'opponibilita' delle locazioni con data certa anteriore al pignoramento e sull'eccezione del canone inferiore di un terzo al giusto prezzo, il 560 del codice di procedura sul possesso del debitore fino al decreto, il 585 sul finanziamento con versamento diretto alla procedura e ipoteca di primo grado, il 586 sulla cancellazione dei gravami e sulla facolta' del giudice di sospendere la vendita a prezzo notevolmente inferiore al giusto, il 587 sulla decadenza con perdita della cauzione a titolo di multa.

Il foglio non serve a calcolare meglio ma a impedire un errore preciso. Un'asta valutata con il modello ordinario mostra un'incidenza dei costi bassa, perche' manca la provvigione, e un prezzo apparentemente ottimo: sul caso di prova l'incidenza risulta del quattro e mezzo per cento contro il dieci del libero mercato. Il numero di sintesi non e' quindi il prezzo ma lo sconto sul valore di mercato, confrontato con una soglia impostabile che rappresenta il prezzo dei quattro rischi, e accanto c'e' il prezzo massimo a cui fermarsi in gara, che va scritto prima perche' in gara non si ragiona.

L'aggiunta dei cinque campi ha rotto il contratto posizionale fra la dataclass, l'ordine di esportazione e le colonne del foglio, e i due test scritti apposta lo hanno intercettato alla prima esecuzione. E' la conferma sul campo di cio' che `refactor-06` argomentava in astratto: un commento che dice di tenere allineato non e' un presidio.

Recap operativo. Aggiunta a `docs/raccolta-annunci.md` la sezione che descrive i tre percorsi dall'annuncio alla decisione, cioe' inserimento manuale, incolla del testo con strutturazione locale e prelievo diretto, con la sequenza dei comandi che li segue fino al workbook e le due varianti per l'asta e per il passaggio alla trattativa.

Sviluppi futuri. Annotata in roadmap la versione parallela per l'agente immobiliare: stesso motore di calcolo, caso d'uso rovesciato, con anagrafica dei clienti, accoppiamento fra immobili e interessati e promemoria sui contatti da riprendere. Va tenuta come progetto separato che condivide i moduli di dominio, perche' un'anagrafica di clienti e' un trattamento di dati personali di terzi con basi giuridiche e obblighi che un progetto personale non ha.

Verifica: cinquanta test verdi, workbook a ventun fogli rigenerato con undici annunci e riaperto con Excel senza celle in errore.

## 2026-08-31, prova della catena col modello locale, e due difetti che la rendevano inutile

File toccati: `src/immobiliare/annunci.py`, `tests/test_workbook.py`.

La catena provata per intero. I due annunci idealista forniti dall'utente rispondono 403 sia al prelievo del progetto sia a qualunque client che non sia un browser, quindi la catena e' stata provata sul percorso documentato, cioe' testo dell'annuncio in un file, strutturazione con il modello locale, inserimento a registro, arricchimento con le quotazioni OMI e riversamento nel workbook. Con qwen3:14b la strutturazione impiega venti secondi.

Primo difetto, di omissione. Alla prima passata il modello ha estratto correttamente sei campi su nove e ne ha mancati tre: rendita catastale, categoria catastale e canone, tutti e tre scritti in chiaro nel testo. Il modello non aveva sbagliato nulla: quei campi non erano nello schema `CAMPI_ESTRAIBILI` che il prompt gli passa, e cio' che non si chiede non si trova. Sono pero' i tre campi che valgono piu' di tutti gli altri messi insieme, perche' la rendita sblocca il prezzo-valore, la categoria decide moltiplicatore ed esclusione dall'agevolazione e il canone determina l'intero calcolo del rendimento. Aggiunti allo schema insieme a provincia, destinazione d'uso e data di consegna: alla seconda passata l'estrazione e' di undici campi su undici.

Secondo difetto, di conversione, e piu' pericoloso. Il modello a volte restituisce i numeri come stringhe, cosi' come li trova nel testo, e la funzione di conversione trattava il punto come separatore decimale: 175.000 diventava centosettantacinque. Nessuna eccezione, nessun errore, un immobile che nel confronto risulta regalato. La discriminante corretta e' quante cifre seguono il punto, tre per le migliaia e una o due per i decimali. Coperto da un test con undici casi, incluso quello che rompeva.

Un test di forma verifica anche che ogni campo dello schema esista davvero nella dataclass, perche' altrimenti il modello lo estrarrebbe e la costruzione dell'annuncio lo scarterebbe in silenzio.

L'annuncio sintetico usato per la prova e' stato rimosso dal registro a fine verifica: il registro contiene solo immobili reali.

Verifica: cinquanta test verdi, workbook rigenerato e riaperto con Excel senza celle in errore.

## 2026-08-31, il registro si aggancia alla fornitura, e i portali rispondono 403

File toccati: `src/immobiliare/omi.py`, `src/immobiliare/annunci.py`, `tools/valuta.py`, `tests/test_calcoli.py`.

Aggancio del registro alle quotazioni. Nuova funzione `omi.quotazione_di_riferimento` e nuova azione `annunci omi`, che riempiono le colonne della quotazione minima e massima di ogni annuncio leggendo la fornitura in cache. E' il passo che rende viva la colonna dello scarto nel workbook, che senza quotazioni restava vuota e faceva sembrare il confronto fra immobili piu' povero di quanto sia.

Due scelte dentro quella funzione meritano di essere dette. Il riferimento si prende sullo stato conservativo normale quando c'e', perche' nella fornitura ottimo descrive l'immobile ristrutturato di recente e assumerlo come termine di paragone farebbe sembrare a buon mercato qualunque cosa. E la funzione restituisce, oltre ai due numeri, la loro provenienza: con la zona indicata si usa quella zona ed e' il confronto giusto, senza si ripiega sull'intero Comune, che su un Comune di costa mette insieme lungomare e zone agricole e produce una forbice cosi' larga da non dire quasi nulla. Sui tre annunci a registro, senza zona, la forbice risulta da 900 a 3.300 euro al metro quadro: il dato e' corretto e quasi inutile, ed e' scritto nell'uscita del comando invece di essere lasciato intuire.

Prova sui portali reali. Due annunci idealista forniti dall'utente: il `robots.txt` consente entrambi i percorsi, e il server risponde comunque 403. E' il caso che ADR-004 prevedeva in astratto e che ora si e' presentato: il permesso dichiarato c'era, la protezione anti bot ha negato lo stesso. Non si insiste, perche' insistere significherebbe aggirarla.

Il difetto qui era nella forma dell'errore, non nella decisione. L'eccezione HTTP usciva grezza, e un 403 letto da chi usa lo strumento sembra un guasto da riprovare invece di un limite da accettare. Aggiunta l'eccezione `PrelievoBloccato`, distinta da `ProbitaRifiutata` perche' i due casi si risolvono diversamente, e il messaggio porta le due vie alternative: incollare il testo dell'annuncio in un file per `annunci importa --file`, che passa dal modello locale, oppure inserire i campi a mano. Coperti anche 401, 405, 406, 429 e 503, che sono le altre risposte con cui un portale dice la stessa cosa.

Verifica: quarantotto test verdi, workbook rigenerato con le quotazioni riversate e riaperto con Excel senza celle in errore.

## 2026-08-31, fornitura OMI 2025/2 acquisita, e tre difetti trovati dal giro reale

File toccati: `src/immobiliare/omi.py`, `src/immobiliare/annunci.py`, `tools/valuta.py`, `tests/test_calcoli.py`, `tests/test_workbook.py`, `docs/raccolta-annunci.md`, `.claude/context/deployment.md`, `.claude/context/design-and-security.md`, `.claude/memory/decisions.md` con ADR-011.

Acquisita la fornitura ufficiale. Richiesta dall'area riservata per la regione Marche, semestre 2025/2, e importata: 22.347 quotazioni su 1.405 Comuni. La cartella `data/omi` contiene ora sia il mirror 2018-2 sia la fornitura 2025/2, e il programma legge la seconda ignorando la prima, che e' esattamente il caso per cui la selezione per semestre e' stata scritta. Il salto di prezzo fra i due semestri e' considerevole: a Civitanova la zona B1 in stato normale passa da 1.300-1.900 a 1.650-3.000 euro al metro quadro, mentre il rendimento lordo implicito resta intorno al cinque per cento, cioe' i canoni hanno seguito i prezzi.

Tre difetti trovati facendo il giro per davvero, tutti della stessa famiglia, quella che produce un risultato plausibile invece di un errore.

Il primo. La lettura della cartella prendeva il solo ultimo file in ordine alfabetico. Chi scarica per provincia si ritrova un file per provincia, e cercare un Comune di un'altra provincia avrebbe risposto "nessuna quotazione", che si legge come "Comune non coperto". Ora vengono letti tutti i file del semestre piu' recente e i periodi superati restano fuori.

Il secondo. Il riconoscimento del semestre leggeva un token di cinque cifre dal nome del file, convenzione del mirror. Se la fornitura ufficiale avesse usato un nome diverso il semestre sarebbe risultato ignoto, si sarebbe ordinato sotto qualunque valore noto, e il programma avrebbe continuato a rispondere con i dati del 2018 senza dire nulla. Aggiunte due vie di ripiego, la riga di metadati e la data di modifica, e la seconda sbaglia al massimo attribuendo il file al semestre corrente, cioe' facendolo vincere invece che perdere. Nel caso concreto il token c'era, ma la difesa resta.

Il terzo. Nella fornitura i nomi dei Comuni non sono scritti come li scrive una persona: convivono SANT con accento grave ELPIDIO A MARE e S BENEDETTO DEL TRONTO abbreviato. Il confronto era letterale, quindi digitando il nome corretto si otteneva zero righe. Ora la normalizzazione collassa apostrofi e prefissi agiografici, e quando comunque non si trova nulla il comando suggerisce i nomi vicini.

Quarto difetto, scoperto interrogando il registro: `Registro.carica` accodava invece di sostituire, e poiche' il costruttore lo chiama gia', rileggere il file da disco raddoppiava l'elenco. Il confronto fra immobili mostrava ogni annuncio due volte. Corretto azzerando la lista in testa al metodo.

Conformita' dell'accesso ai servizi telematici. Verificate le condizioni generali di consultazione della banca dati catastale, decreto 4 maggio 2007 e successive integrazioni. Nessuna violazione: l'accesso e' manuale, il fine e' la valutazione di un acquisto in corso, i documenti restano locali. Era pero' scoperto un obbligo assunto e non assolto, cioe' la citazione della fonte imposta dalla fornitura OMI: aggiunta la costante `omi.ATTRIBUZIONE` con la stringa dovuta, stampata in coda a ogni interrogazione e dichiarata nel foglio Fonti. La decisione e' ADR-011.

Nota di riservatezza. L'archivio scaricato dall'area riservata porta nel nome il codice fiscale del richiedente. Sta in `data/omi`, che e' ignorato da git, e i CSV che ne escono hanno nomi propri privi di dati personali: verificato che nessun file tracciato lo nomini.

Verifica: quarantasette test verdi, workbook rigenerato e riaperto con Excel senza celle in errore.

## 2026-08-31, garanzie legali nel dossier, indicatori di contesto, promemoria OMI

File toccati: `src/immobiliare/excel_builder.py`, `src/immobiliare/indicatori.py` nuovo, `src/immobiliare/omi.py`, `tools/valuta.py`, `tests/test_calcoli.py`, `docs/perizia-pre-acquisto.md`, `docs/guida-tecnica.md`, `docs/guida-non-tecnica.md`, `docs/raccolta-annunci.md`, `docs/fonti.md`, `README.md`, `CLAUDE.md`, `.claude/context/STACK.md`, `.claude/context/deployment.md`, `.claude/memory/decisions.md` con ADR-010. Fuori progetto, preparato e non committato: `E:\legal-consultant\docs\dominio-compravendita-immobiliare.md`.

Audit legale del dossier. Il fascicolo pre-acquisto era stato costruito con l'occhio del tecnico e mancava di tutto cio' che un legale metterebbe per primo, cioe' le dichiarazioni con valore legale. Interrogato il corpus, sono state aggiunte dodici voci in una nona famiglia. Le due che reggono il resto sono l'articolo 1482 del codice civile, per cui il compratore puo' sospendere il prezzo e ottenere la risoluzione solo se i gravami non erano dichiarati dal venditore e da lui ignorati, mentre se li conosceva gli resta la sola garanzia per evizione, e l'articolo 1489, che copre oneri e diritti di terzi non apparenti, i quali non si trascrivono e non compaiono in nessuna visura. La conseguenza operativa e' che la dichiarazione di liberta' da gravami non e' una formalita' notarile ma la condizione che tiene in vita il rimedio, e va anticipata nella proposta.

Tre punti che il corpus ha chiarito e che non erano nel modello. L'articolo 40-bis del testo unico bancario distingue estinzione e cancellazione dell'ipoteca: la banca puo' comunicare entro trenta giorni che l'ipoteca permane per giustificato motivo ostativo, quindi si verifica la cancellazione nei registri e non la quietanza. L'articolo 732 da' ai coeredi il riscatto della quota contro l'acquirente e ogni successivo avente causa finche' dura la comunione ereditaria. L'articolo 166 comma 3 del codice della crisi esclude dalla revocatoria le vendite e i preliminari trascritti a giusto prezzo su immobili destinati ad abitazione principale: tre condizioni congiunte, e la trascrizione del preliminare, che altrove e' opzionale, li' e' decisiva.

Il dossier passa da cinquantaquattro a sessantasei documenti e da ventuno a ventisette bloccanti. Workbook a venti fogli, ricalcolato senza celle in errore.

Aggiornamento del progetto legale. Esteso `docs/dominio-compravendita-immobiliare.md` con un secondo passaggio di audit sul ramo delle garanzie: nessuna lacuna nuova, ma due trappole di recupero documentate. Il DPR 445/2000 e' spezzato fra Testo B e Testo C e l'articolo 47 ha i commi vuoti nel primo e il testo nel secondo, quindi una ricerca sul solo Testo B conclude che non abbia contenuto. L'articolo 35 comma 22 del DL 223/2006 non si legge nel decreto ma nella finanziaria 2007 che lo ha modificato. La lacuna sulla legge 448 del 1998 e' stata riverificata in due modi indipendenti e resta aperta: il recupero forzato non restituisce l'atto e l'URN compare nel corpus solo come citazione dentro altri atti.

Codifica della fornitura OMI. La lettura dei CSV dava per scontato l'UTF-8. La fornitura ufficiale arriva nella codifica ANSI di Windows, e decodificarla come UTF-8 non solleva errori: sostituisce ogni accento con il segnaposto di rimpiazzo, il file si carica, le quotazioni si calcolano, e un Comune accentato diventa irreperibile alla ricerca per nome. Aggiunta `_leggi_testo` con riconoscimento della codifica e un test che scrive un file in cp1252 e verifica che il nome resti intatto e cercabile.

Nuovo modulo `indicatori.py` e comando `valuta.py indicatori`. Legge l'euro short-term rate dalla BCE, che e' l'unica serie davvero giornaliera e libera perche' l'Euribor giornaliero non e' ridistribuito dalla BCE, e i prezzi al consumo NIC dal servizio SDMX di ISTAT, con l'indice armonizzato della BCE come riscontro incrociato. Il vecchio endpoint `sdmx.istat.it` oggi rimanda alla home: l'indirizzo vivo e' `esploradati.istat.it`, l'ordine delle dimensioni e' stato verificato sul data structure definition, e la corrispondenza dei codici della dimensione MEASURE e' stata verificata sui valori, perche' la misura 7 a dicembre 2025 vale 1,2 per cento e coincide con l'indice armonizzato Italia dello stesso mese. Alla data odierna l'euro short-term rate e' del 28 agosto 2026 mentre entrambe le serie di inflazione si fermano a dicembre 2025: il comando stampa sempre il periodo accanto al valore, perche' su queste serie la data e' meta' dell'informazione.

Promemoria di manutenzione. Le scadenze del progetto sono ora due e stanno in `deployment.md`: l'aggiornamento fiscale annuale dopo la legge di bilancio, e le quotazioni OMI due volte l'anno, cinque minuti, con la procedura passo per passo dall'area riservata fino a `omi importa`. La stessa procedura e' registrata come flusso in `docs/raccolta-annunci.md`.

Verifica: quarantatre' test verdi, workbook rigenerato e riaperto con Excel senza celle in errore, md-unwrap pulito, scansione dei dati personali pulita.

## 2026-08-31, giro di prova sullo strumento e canone concordato realistico

File toccati: `src/immobiliare/parametri.py`, `tools/valuta.py`, e l'allineamento di `.claude/memory/index.md`, `.claude/memory/progress.md`, `.claude/memory/decisions.md` con ADR-009, `.claude/context/current-work.md`, `.claude/context/STACK.md`, `.claude/context/dev-testing.md`, `.claude/context/studio-didattico-master.md`, `docs/da-zero.md`, `docs/guida-tecnica.md`.

Allineamento. Le schede di memoria e contesto sono state riportate al commit `7307fdc` e ai conteggi correnti: venti fogli, quaranta test. Le voci storiche del work-log non sono state toccate, perche' descrivono lo stato al momento in cui furono scritte ed e' proprio il loro valore.

Difetto trovato provando lo strumento. Il comando `riepilogo`, quando non riceve `--canone-concordato`, confrontava il regime concordato usando lo stesso canone del libero: il concordato incassava cosi' l'aliquota ridotta al dieci per cento senza il minor canone che la giustifica, e vinceva sempre. Sul caso di prova dava un reddito operativo netto di 2.504 euro contro i 2.290 del libero, cioe' un ordinamento invertito rispetto al vero. Ora il default e' il canone libero ridotto dello sconto tipico, dichiarato in `parametri.Locazione.sconto_canone_concordato` al quindici per cento con la forbice osservata annotata accanto, e la riga di comando stampa quale canone ha usato e come sovrascriverlo. Con la correzione i due regimi si avvicinano, 0,87 contro 0,82 per cento, che e' il margine vero e dipende dallo sconto reale dell'accordo territoriale del Comune.

Giro di prova completo. Tassi correnti letti dal portale della Banca centrale europea, media 3,49 per cento e fisso oltre dieci anni 3,60 a giugno 2026; confronto di un preventivo al 3,50 che risulta sotto mercato di un decimo di punto, pari a 1.452 euro di interessi risparmiati su venticinque anni. Quotazioni OMI scaricate dal mirror per il semestre 2018-2 e interrogate per Comune, ventidue zone con rendimento lordo implicito fra il 3,3 e il 5,1 per cento. Modello linguistico locale raggiungibile. Workbook rigenerato e ricalcolato con Excel senza celle in errore, cruscotto e foglio di confronto letti via automazione COM: dei tre annunci a registro solo il primo ha un reddito che copre la rata, con DSCR 1,16 contro 0,87 e 0,48.

Osservazione emersa dal giro. Il foglio di confronto mostra rendita catastale e spese condominiali a zero per tutti e tre gli annunci, perche' quei campi del registro non sono compilati. Sono esattamente i due dati che il nuovo foglio Dossier tecnico dice di andare a prendere, e la loro assenza si propaga: senza rendita non si puo' applicare il prezzo-valore e le imposte vengono calcolate sul prezzo, quindi sovrastimate rispetto a quanto si pagherebbe davvero.

## 2026-08-31, dossier dei documenti tecnici pre-acquisto

File toccati: `src/immobiliare/excel_builder.py` (metodo `foglio_dossier` e due contatori sul Cruscotto), `tests/test_workbook.py`, `docs/perizia-pre-acquisto.md` nuovo, `docs/guida-tecnica.md`, `docs/guida-non-tecnica.md`, `docs/due-diligence.md`, `docs/fonti.md`, `CLAUDE.md`, `README.md`.

Il foglio. Nuovo foglio Dossier tecnico, ventesimo del workbook, con cinquantaquattro documenti in otto famiglie: identificazione e titolarita', legittimita' urbanistica, struttura e sismica, vincoli, impianti ed energia, condominio, nuova costruzione, occupazione e tributi. Ogni riga porta chi rilascia il documento, la norma che lo rende dovuto, che cosa prova e che cosa si rischia se manca, un costo indicativo, e le colonne di stato, data della richiesta e data di ricezione. Ventuno voci sono marcate bloccanti nel senso preciso che senza di esse l'atto e' nullo, la banca non delibera oppure il costo di regolarizzazione resta ignoto.

Perche' un foglio separato dalla Checklist. Le due cose rispondono a domande diverse: la Checklist elenca verifiche da fare, il dossier elenca carte da avere per poterle fare, e le carte si chiedono in trattativa, quando si ha ancora potere negoziale. Tenerle insieme avrebbe prodotto una tabella con due colonne inutili per meta' delle righe. La decisione e' ADR-009.

Verifica delle norme sui testi primari. Le voci urbanistiche non poggiano su fonti divulgative: dal corpus legale locale sono stati letti l'articolo 9-bis commi 1-bis e 1-ter del DPR 380/2001, con la regola introdotta dal Salva Casa per cui le difformita' sulle parti comuni non rilevano per lo stato legittimo della singola unita' e viceversa, l'articolo 34-bis con le soglie di tolleranza graduate per superficie, cinque per cento sotto i cento metri quadrati e a scendere fino al due oltre i cinquecento, e l'obbligo di dichiarazione asseverata da allegare al trasferimento, gli articoli 24, 30 e 93-94, e l'articolo 40 comma 3 della legge 47/1985 sulla dichiarazione sostitutiva per le opere iniziate prima del 1 settembre 1967.

Il punto di metodo che il foglio incorpora. I titoli edilizi si ottengono con l'accesso agli atti, che richiede la delega del proprietario o una proposta gia' sottoscritta: da qui la contraddizione apparente fra il dover verificare prima e il poter accedere solo dopo. La via che il progetto indica e' la proposta condizionata all'esito della verifica tecnica, con termine breve e provvigione dovuta solo ad avveramento, ed e' scritta sia nel foglio sia nella scheda.

Test. Nuovo test sulla struttura del foglio: verifica che ogni riga porti uno dei tre pesi ammessi, perche' la formula del contatore fa `COUNTIFS` sulla stringa esatta e un valore scritto anche solo con l'iniziale maiuscola sparirebbe dal conteggio in silenzio, facendo dire al Cruscotto che non manca nulla.

Verifica: quaranta test verdi, workbook a venti fogli riaperto con Excel senza celle in errore, contatori letti via COM che danno cinquantaquattro documenti in elenco, cinquantaquattro applicabili e ventuno bloccanti aperti alla generazione.

## 2026-08-31, cruscotto, simulazione probabilistica e strato didattico

File toccati: `src/immobiliare/excel_builder.py` (fogli Cruscotto, Rischio, `_Estrazioni`), `tests/test_workbook.py`, `docs/da-zero.md` nuovo, `docs/fonti.md` riscritto, `.claude/context/studio-didattico-master.md` nuovo e i sette approfondimenti `refactor-01` .. `refactor-07`, `CLAUDE.md`, `.claude/memory/index.md`, `.claude/memory/decisions.md`.

Cruscotto. Il workbook aveva quindici fogli e nessun punto di ingresso: chi lo apriva doveva sapere gia' dove guardare. Il nuovo primo foglio raccoglie i cinque numeri di decisione, costo totale, cassa al rogito, rendimento netto, cash flow mensile e debt service coverage ratio, con accanto la coda bassa della simulazione e il contatore delle verifiche ancora aperte. Nessun calcolo nuovo: tutte le celle leggono nomi definiti gia' esistenti, quindi il cruscotto non puo' divergere dai fogli di dettaglio.

Simulazione probabilistica. Nuovo foglio Rischio su mille scenari, con quattro variabili aleatorie, canone, sfitto, tasso e rivalutazione, piu' un evento discreto di morosita' grave. Il conflitto fra riproducibilita' e interattivita' e' risolto separando i due strati: le estrazioni sono numeri fissi generati con seme dichiarato e scritti nel foglio nascosto `_Estrazioni`, il calcolo che le trasforma in esiti sono formule vive che leggono gli input dell'utente. La funzione casuale nativa e' stata scartata perche' volatile: renderebbe i percentili diversi a ogni tocco di cella. Accanto, un blocco a tornado che muove una variabile per volta del dieci per cento e ordina per ampiezza, che risponde alla domanda operativa di dove convenga spendere tempo a stimare meglio.

Correzione di modello sulla rivalutazione. La prima versione applicava la volatilita' annua come se l'estrazione fosse un regime permanente per tutto l'orizzonte, e la coda alta produceva un patrimonio finale di novecentodiciottomila euro su un immobile da centoventimila. L'estrazione e' invece la media di N realizzazioni annue, quindi la sua dispersione va divisa per la radice dell'orizzonte. La correzione non si applica alle altre variabili, dove l'incertezza e' di livello e non si media via. Corretto anche il montante finale, che sommava i flussi a valore nominale e rendeva asimmetrico il confronto con l'alternativa: ora li capitalizza al rendimento del portafoglio.

Documentazione da zero. Nuovo `docs/da-zero.md`: dall'ambiente vuoto alla prima valutazione in sette passi, con l'elenco dei cinque documenti da procurarsi prima di aprire il foglio, perche' senza visura, consuntivo condominiale, delibera IMU, quotazioni OMI e preventivo del mutuo si compila con valori inventati.

Registro delle fonti riscritto. Ogni riga porta ora una colonna in piu' che dichiara dove quella fonte atterra: il campo della dataclass, la funzione, la cella con nome definito, la voce di checklist. Aggiunta una sezione sulle interfacce dati automatizzate con endpoint, protocollo e comportamento in caso di indisponibilita', e una sezione finale che elenca le lacune note, a partire dal testo primario dell'articolo 7 della legge 448/1998 che non e' stato recuperato.

Strato didattico. Adottato il pacchetto `studio-didattico` del template: un master con sette voci numerate, ciascuna con contesto, com'era e perche' era fragile, il salto compiuto e il rimando, e sette approfondimenti che mostrano il codice reale prima e dopo e chiudono spiegando come estendere il pattern. Le voci non sono ricostruzioni a posteriori: sono i sette punti in cui il progetto ha cambiato impostazione, incluso il moltiplicatore catastale sbagliato che era identico in Python e in Excel e che la doppia implementazione non aveva intercettato.

Verifica: trentanove test verdi, workbook a diciannove fogli riaperto con Excel, nessuna cella in errore, ricalcolo completo in sei decimi di secondo, scansione dei dati personali sui file tracciati pulita.

## 2026-08-31, articoli civilistici del corpus, acquisto in piu' persone e scenari settabili

File toccati: `src/immobiliare/excel_builder.py` (foglio Comproprieta' e blocco dei tre scenari), `tests/test_workbook.py`, `docs/comprare-in-piu-persone.md` nuovo, `docs/guida-tecnica.md`, `docs/guida-non-tecnica.md`, `docs/fonti.md`, `CLAUDE.md`, `README.md`.

Articoli civilistici. L'utente aveva enumerato a mano nel suo foglio precedente dieci articoli del codice civile, dei quali il modello ne citava due. Recuperati dal corpus locale quarantatre' articoli con testo e rubrica, tutti trovati: le fasi contrattuali dal 1326 al 1403 con il 2645-bis, il 2775-bis, il 2825-bis e il 2932, la garanzia per vizi, e l'intero titolo sulla comunione dal 1100 al 1116 piu' il 2247 e il 2248 sul confine con la societa'. Sono ora il riferimento normativo della guida tecnica.

Acquisto in piu' persone. Nuovo foglio Comproprieta', fino a otto acquirenti. La risposta di merito viene dall'articolo 2248: la comunione costituita o mantenuta al solo scopo del godimento non e' un contratto di societa', quindi comprare insieme e affittare non richiede di costituire nulla. Il foglio ripartisce per quote e calcola l'imposta di ciascuno separatamente, perche' l'opzione per la cedolare secca si esercita disgiuntamente e vale solo per chi l'ha esercitata, e l'aliquota marginale e' personale: verificato che con due acquirenti in regimi diversi le imposte divergono correttamente. Una riga di controllo segnala se le quote non sommano a cento, perche' con quote incoerenti il foglio mentirebbe in silenzio, e i totali di colonna riconciliano con il resto del workbook.

Scenari settabili. Aggiunto al foglio Scenari un blocco a tre colonne, pessimistico, base e ottimistico, con canone, sfitto, morosita', tasso e rivalutazione impostabili per ciascuna, e in uscita ricavo effettivo, reddito operativo netto, utile, cash flow, rendimento netto, debt service coverage ratio e patrimonio netto a fine orizzonte. Il debito residuo usa la formula chiusa dell'ammortamento alla francese, quindi resta esatto anche cambiando il tasso di scenario. La colonna base riconcilia con il resto del modello.

Legge 448/1998. Provata anche la raccolta di Bosetti e Gatti indicata dall'utente: riporta l'articolo 7 in omissis. Con Normattiva che rende gli articoli via JavaScript e il corpus locale che non ha l'atto, il testo primario resta non recuperabile e la lacuna e' dichiarata in `docs/fonti.md`; le regole del credito d'imposta sono ricostruite da fonti professionali.

Verifica: trentanove test verdi, workbook a sedici fogli riaperto con Excel senza celle in errore.

## 2026-08-29, fonti residue chiuse: trascrizioni, canale Telegram, legge regionale, e tre correzioni al modello

File toccati: `src/immobiliare/excel_builder.py`, `src/immobiliare/omi.py`, `src/immobiliare/parametri.py`, `tools/valuta.py`, `docs/fonti.md`, le due guide, `_notes/INDICE-MATERIALE.md`.

Trascrizioni dei video. I quattro video segnalati sono stati trascritti senza ricorrere al riconoscimento vocale: YouTube espone i sottotitoli automatici italiani e `yt-dlp` li scarica direttamente. Circa 68.000 parole ripulite dalla sovrapposizione tipica delle didascalie automatiche. Da qui vengono due voci nuove del modello.

Canale Telegram. L'utente ha esportato a mano il sottocanale "Tassazione, spese, mutui", che dall'esterno non era leggibile perche' il gruppo sta dietro un passaggio anti bot. Quasi sedicimila messaggi su due anni e mezzo, filtrati a 2.385 pertinenti e 932 sostanziosi. Da qui viene la terza correzione.

Legge regionale delle Marche sul turismo. Il PDF non era estraibile perche' privo di mappa Unicode; la conversione in JSON fornita dall'utente ha permesso di ricostruire il testo. Ne esce la soglia che mancava: l'articolo 33 consente l'uso occasionale di immobili a fini ricettivi per non piu' di novanta giorni l'anno, e l'articolo 27 comma 3 qualifica come attivita' ricettiva la gestione non occasionale e organizzata.

Tre correzioni al modello, tutte da fonte. Il costo figurativo del tempo dedicato alla gestione, che nella diretta con Fineco viene indicato come voce da calcolare e non solo da citare, entra nel conto economico con un moltiplicatore dedicato per la locazione breve, che non e' un investimento passivo; resta a zero per impostazione predefinita, quindi il modello e' retrocompatibile. Il controllo di concentrazione del patrimonio, con la soglia di un terzo e l'avvertenza che l'immobiliare non decorrela dall'azionario nelle recessioni. E la forma del premio della polizza incendio, che il canale Telegram ha mostrato esistere anche come premio unico anticipato per l'intera durata, spesso finanziato dentro il mutuo: il modello ora lo tratta come onere iniziale e lo ripartisce sulla durata per il confronto.

Quotazioni OMI. Verificato che il servizio di consultazione a video non espone una API documentata ne' un `robots.txt`, e la fornitura ufficiale richiede un'autenticazione personale: l'automazione non e' quindi una strada percorribile e ci si astiene, coerentemente con ADR-004. Aggiunti invece `omi importa`, che ingerisce la fornitura scaricata a mano accettando lo zip o i CSV, e `omi zone`, che elenca le zone omogenee di un Comune.

Resta aperta la legge 448/1998: Normattiva rende gli articoli via JavaScript e la pagina statica non li contiene, mentre il corpus locale non restituisce l'atto al suo URN.

Verifica: trentanove test verdi, workbook a quindici fogli riaperto con Excel senza celle in errore, scansione dei dati personali pulita.

## 2026-08-28, chiusura delle fonti arretrate, simulatore del mutuo e guide d'uso

File toccati: `src/immobiliare/excel_builder.py` (foglio Simulatore mutuo, sei voci di checklist, fonte Banca d'Italia), `src/immobiliare/parametri.py`, `tests/test_workbook.py`, `docs/guida-non-tecnica.md` e `docs/guida-tecnica.md` nuovi, `CLAUDE.md`, `README.md`, `_notes/INDICE-MATERIALE.md`.

Materiale locale rimasto indietro, ora letto. Quattordici schermate di thread di r/ItaliaPersonalFinance, che erano l'unica copia di discussioni non piu' raggiungibili dal web perche' il dominio non e' prelevabile; le sottocartelle tematiche si sono rivelate duplicati esatti, verificato per impronta. La guida ufficiale della Banca d'Italia sul mutuo ipotecario, trentasei pagine, da cui sono uscite sei voci di checklist su diritti che quasi nessuno esercita: consegna del PIES, sette giorni di riflessione sull'offerta vincolante, gratuita' di legge della portabilita', verifica della soglia d'usura, liberta' di scelta della polizza, accesso gratuito alla Centrale dei Rischi. Il documento sul rimborso anticipato, con la correzione dell'equivoco per cui converrebbe estinguere presto perche' all'inizio si pagano soprattutto interessi. Il dossier tecnico di un immobile reale e il documento di rinuncia all'incarico di mediazione creditizia, entrambi segnalati nell'indice perche' contengono dati personali di terzi.

Il testo unico regionale del turismo delle Marche non e' stato estratto: il PDF non ha mappa Unicode e il testo esce illeggibile senza riconoscimento ottico. Il quadro sul confine fra locazione turistica non imprenditoriale e attivita' ricettiva e' stato ricostruito dalle fonti in rete.

Coletti, completato. Analizzati anche i fogli che mancavano del calcolatore mutuo, in particolare il Simulatore, che ricalcola la rata mese per mese sul debito residuo e ammette versamenti volontari. Restano fuori `leva.xlsx` e `leva.ipynb`, che riguardano la leva su attivi volatili e non l'immobiliare, e i quattro video segnalati dall'utente, per i quali non esiste trascrizione recuperabile.

Corpus normativo, usato e non solo verificato. Estratti da `E:\legal-consultant` quindici articoli con testo e URN, che sono ora le citazioni della guida tecnica. Due conferme dal testo primario valgono piu' di qualunque sintesi: l'art. 4 del DL 50/2017 prevede il 26 per cento ridotto al 21 per una sola unita' individuata in dichiarazione, e non contempla alcuna aliquota del 30 per cento; l'art. 18 del DPR 601/1973 conferma lo 0,25 per cento sul mutuo prima casa e il 2 per cento negli altri casi.

Nuovo foglio Simulatore mutuo, quindicesimo del workbook. Ricorsione mese per mese con versamenti volontari ricorrenti e una tantum, percorso del tasso con variazione a partire da un mese scelto, e le due modalita' di imputazione del rimborso, riduzione della durata oppure della rata, che vanno dichiarate alla banca e producono risultati molto diversi: sullo stesso versamento di cento euro al mese il risparmio e' di 11.373 euro riducendo la durata contro 6.543 riducendo la rata. Espone anche la scelta della convenzione di conversione del tasso mensile, divisione per dodici come nei contratti italiani oppure tasso equivalente composto. Si autovalida: a versamenti nulli e tasso invariato riproduce esattamente il piano base, con tasso interno pari al nominale.

Scritte le due guide d'uso richieste, una per l'utente non tecnico che accompagna foglio per foglio in linguaggio comune, e una tecnica con architettura, catena di calcolo e riferimento di ogni voce con formula, nome definito e norma.

Verifica: trentanove test verdi, workbook a quindici fogli riaperto con Excel senza celle in errore, scansione dei dati personali sui file tracciati pulita.

## 2026-08-28, riordino della cartella, colonne del registro e confronto fra immobili

File toccati: `.gitignore`, il riordino di `_notes/`, `_notes/INDICE-MATERIALE.md` e `_notes/RESUME-PROMPT.md` nuovi e ignorati, `src/immobiliare/annunci.py`, `src/immobiliare/excel_builder.py`, `tools/valuta.py`, `tests/test_workbook.py` nuovo, `.claude/context/deployment.md` nuovo, `LICENSE`, `CLAUDE.local.md` e `.claude/settings.local.json` nuovi e ignorati, `CLAUDE.md`, `README.md`, `docs/raccolta-annunci.md`, `.claude/context/dev-testing.md`, `.claude/context/current-work.md`.

Riordino della cartella. In radice il codice stava mischiato a quattordici elementi personali. Tutto il materiale e' stato spostato sotto `_notes/`, in tre rami con criteri distinti: `dossier/` per il materiale personale, `riferimenti/` per quello di terzi, `segnalibri/` per i collegamenti senza file associato. Settantuno file spostati, nessuno perso, nessuno rinominato. La scelta di non rinominare non e' pigrizia: quattro file hanno dimensione zero e portano l'informazione nel nome, fra cui il numero del centralino di una palazzina, e un rinomino l'avrebbe cancellata. Il loro contenuto e' trascritto in `_notes/INDICE-MATERIALE.md`, che mappa l'intera struttura. Il `.gitignore` si e' di conseguenza semplificato, perche' una sola riga per `_notes/` sostituisce le dieci regole per nome che c'erano prima.

Colonne del registro. Il confronto con il foglio di lavoro precedente dell'utente ha mostrato cinque campi persi nel passaggio: agenzia, contatto, provincia, data di consegna e destinazione d'uso. Sono stati rimessi, portando il registro a ventotto campi e il foglio Annunci a trentuno colonne. Sull'agenzia e sul contatto va detto perche' non contraddicono ADR-004: quella decisione vieta di raccogliere recapiti con il prelievo automatico, non di annotare a mano il riferimento con cui si sta trattando, e la differenza fra un'agenda e una banca dati e' esattamente questa.

Foglio Confronto immobili. Applica il modello completo a ogni riga del registro, dalle imposte di trasferimento al cash flow, e restituisce gli annunci in fila con rendimento netto, cap rate, cash on cash e debt service coverage ratio affiancati, con l'esito rispetto alla soglia di rendimento del foglio Scenari. Le colonne intermedie sono deliberate: ogni formula legge la precedente invece di ricalcolare da capo, il che rende ogni cella ispezionabile quando un numero sorprende. Il regime di acquisto e' quello del foglio Immobile e vale per tutti, limite dichiarato nel foglio e fra le domande aperte.

Test sul generatore. Nuovo file `tests/test_workbook.py`, sei test sulla struttura: elenco dei fogli, presenza dei nomi definiti essenziali, corrispondenza posizionale fra le colonne del foglio Annunci e l'ordine di esportazione, riga di aggancio del foglio di confronto, estensione del piano di ammortamento. Il test sull'esportazione ha trovato subito un difetto reale: `openpyxl` salta l'assegnazione quando si passa `value=None` a `cell()`, quindi un campo azzerato non ripuliva la cella e l'annuncio esportato ereditava in silenzio il dato di quello che occupava prima quella riga. Corretto assegnando sull'attributo invece che tramite il parametro.

Verifica: trentanove test verdi in due file, workbook rigenerato e riaperto con Excel senza celle in errore, foglio di confronto che ordina correttamente i tre annunci a registro.

## 2026-08-28, costruzione iniziale del progetto

Adozione del sistema di progetto del template nella forma minima: `CLAUDE.md` come indice, regole modulari sotto `.claude/rules/` limitate alle cinque pertinenti, memoria e schede di contesto versionate, nessun pacchetto opzionale. La regola sugli screenshot manuali e' stata esclusa perche' non pertinente a un progetto senza interfaccia.

Ricerca fiscale e normativa aggiornata al 28 agosto 2026. Verificate sulle fonti le imposte di trasferimento, la regola prezzo-valore, i termini dell'agevolazione prima casa incluso il passaggio da uno a due anni per la rivendita della precedente, l'imposta sostitutiva sui mutui, la detrazione degli interessi passivi, gli scaglioni IRPEF con la seconda aliquota ridotta al trentatre' per cento, l'IMU, i regimi di tassazione dei canoni e la plusvalenza.

Risolta una contraddizione fra le fonti sulle locazioni brevi 2026. Diverse ricostruzioni riportavano aliquote progressive con un trenta per cento sulla terza e quarta unita', incompatibile con la contestuale riduzione della soglia a due unita'. La verifica incrociata su piu' fonti, inclusa la guida dell'Agenzia delle Entrate aggiornata ad aprile 2026, ha confermato che le aliquote restano ventuno per cento sulla prima unita' e ventisei sulle altre, e che cio' che e' cambiato e' solo la soglia, da quattro a due unita'.

Scritti `src/immobiliare/parametri.py` con i parametri e le fonti, `calcoli.py` con le funzioni di dominio, `stile.py` con gli stili del workbook, `excel_builder.py` con il generatore a tredici fogli, `annunci.py` con il registro e l'acquisizione, `omi.py` con le quotazioni dell'Osservatorio, `llm_locale.py` con il cliente Ollama.

Scaricati come riferimento, sotto `_notes/riferimenti/coletti/` non versionato, i fogli di calcolo immobiliari di Paolo Coletti. Registrate le date di ultima modifica dichiarate dal server, perche' determinano quali parti siano ancora utilizzabili: i due fogli immobiliari sono del 17 febbraio 2022, quello su mutuo e investimento del 29 settembre 2025. Da essi proviene l'impostazione dell'orizzonte lungo, dello sfitto fra un contratto e l'altro, della ristrutturazione periodica e del confronto con il portafoglio alternativo.

Verifica del workbook con Excel. Il primo file generato non si apriva: la bisezione sui fogli ha isolato la causa in un elemento `dataValidations` vuoto sul foglio Mutuo, prodotto da una validazione dichiarata e mai associata ad alcuna cella. Rimossa la dichiarazione inutile, il file si apre e ricalcola senza errori.

Corretti due difetti sostanziali emersi dal ricalcolo. La differenza fra i due patrimoni nel foglio di confronto puntava alla riga del capitale versato invece che a quella del patrimonio comprando. L'accantonamento per la ristrutturazione compariva sia nel foglio del flusso di cassa sia, indirettamente, nei costi operativi: spostato una sola volta dentro il conto economico della locazione e rimossa la colonna che lo duplicava.

Reso parametrico il tasso marginale IRPEF usato nel confronto con il regime ordinario, che era cablato sulla seconda aliquota.

Scritte le schede di dominio sotto `docs/` e il registro completo delle fonti, con distinzione esplicita fra fonti lette direttamente e fonti solo segnalate.
