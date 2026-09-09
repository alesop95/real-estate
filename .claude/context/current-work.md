---
generated-from-commit: a0b3420
generated-from-branch: main
generated-date: 2026-09-01
covers-paths:
  - src/**
  - tools/**
  - docs/**
last-verified-commit: a0b3420
stato: lo strumento locale è completo e verificato; dal 4 settembre è attiva una feature nuova, cioè il passaggio ad applicazione web autenticata su Cloudflare, con il doppio scopo di uso proprio e vendita a un'agenzia. Vive sul branch web
---

# Lavoro in corso

## Feature attiva: l'applicazione web da vendere

Cosa fa. Sposta lo strumento da workbook Excel generato in locale ad applicazione web autenticata, con i dati per organizzazione, in modo che si usi dal browser e si possa vendere a un'agenzia immobiliare. Il motore di calcolo resta lo stesso modello, riscritto in TypeScript per girare nel browser, con il motore Python come implementazione di riferimento da cui si generano i vettori di riscontro.

Dove vive. Branch `web`, allineato a `main`. La direzione, le piattaforme misurate, le alternative scartate, il funzionamento senza codice lato server e il piano in fasi stanno in [`docs/architettura-web.md`](../../docs/architettura-web.md). Le decisioni sono ADR-024 per la piattaforma e ADR-025 per la scelta di prodotto. La voce didattica è la 13 dello studio didattico.

Stato all'8 settembre 2026. È scritto e provato tutto ciò che non richiede un account. La fase uno è chiusa, cioè il motore in TypeScript con i duecentoundici vettori generati dal motore Python. La parte locale della fase due è chiusa, cioè lo schema del database, il Worker con le cinque rotte autorizzate e le trentacinque prove che girano dentro il runtime di Cloudflare con un D1 vero, senza account e senza rete. L'8 settembre si è aggiunto ciò che il passaggio successivo richiede: la procedura in nove passi di [`messa-in-rete.md`](../../docs/messa-in-rete.md), con il registro che ne segue l'avanzamento, e il flusso `.github/workflows/distribuzione.yml`, che prova a ogni spinta e distribuisce da `main` soltanto dopo che le prove sono passate. Da qui in avanti la parte remota è dell'utente, perché richiede di aprire l'account. Il 9 settembre, in attesa, è stata portata nel motore la simulazione del rischio, in Python come riferimento e in TypeScript per il browser: era l'ultima parte del modello a esistere soltanto come formule, l'interfaccia ne avrà bisogno nella sua area della decisione, e la conversione ha fatto emergere due difetti reali del foglio. Le prove dell'applicazione salgono a cinquantadue e i test Python a centosette.

### Definizione di completamento della feature web

- [x] Studio dello stack, con gli assi derivati dalle capacità del programma e non dal listino
- [x] Limiti delle fasce gratuite letti sulle pagine dei fornitori, datati e registrati fra le fonti
- [x] Scelta della piattaforma con il prezzo dichiarato, e alternative scartate con la ragione
- [x] Vincolo di riservatezza riscritto: che cosa può stare in rete e che cosa no
- [x] Voce didattica sul metodo di misura di una fascia gratuita
- [x] Fase uno: motore in TypeScript, generatore di vettori dal motore Python, suite che li verifica. Duecentoundici casi, tolleranza 1e-9 relativo dichiarata prima, tutti passati, piu' un caso che deve fallire
- [x] Fase uno, ricaduta: corretto il difetto del motore Python che il generatore ha fatto emergere, cioe' la divisione per zero nel tasso interno sui flussi mensili
- [x] Fase due, parte locale: schema del database, verifica del token di Access, autorizzazione dichiarata, cinque rotte, trentacinque prove contro un D1 vero dentro il runtime di Cloudflare
- [x] Fase due, presidio: il test che fallisce se la configurazione esce dal piano gratuito
- [x] Fase due, struttura: [`docs/struttura-del-progetto.md`](../../docs/struttura-del-progetto.md) e la voce didattica 15 sull'autorizzazione
- [x] Fase due, procedura: [`messa-in-rete.md`](../../docs/messa-in-rete.md) in nove passi, ciascuno con la ragione, l'azione esatta, che cosa riportare e come si verifica, piu' il registro dell'avanzamento con le date
- [x] Fase due, distribuzione automatica: `.github/workflows/distribuzione.yml`, con le prove su ogni spinta, la distribuzione dal solo `main` dopo che sono passate, le migrazioni applicate prima del codice e il controllo che i vettori di riscontro non siano scaduti
- [ ] Fase due, parte remota: account aperto, D1 creato, Access configurato, prima distribuzione. Chiusa quando l'applicazione risponde all'indirizzo e le prove girano anche contro il database vero. È l'unica voce che l'ambiente di sviluppo non può chiudere da solo
- [x] Simulazione del rischio nel motore, in Python come riferimento e in TypeScript per il browser, con le estrazioni come parametro per ADR-026, cinquantadue vettori, l'accordo con il foglio congelato in un test e la voce didattica 16
- [ ] Fase tre: le sei aree dell'interfaccia, una per volta
- [ ] Fase quattro: migrazione del registro immobili e delle verifiche comunali, ed esportazione del workbook come ponte
- [ ] Fase cinque: una voce didattica per ogni passo che introduce un pattern, con il codice reale prima e dopo
- [ ] Licenza rivista, perché MIT permette a chiunque di rivendere lo stesso codice

## Feature chiusa: strumento di valutazione completo

Cosa fa. Genera un workbook Excel interattivo di ventun fogli che valuta l'acquisto di un immobile residenziale in Italia nelle tre destinazioni possibili, con i parametri fiscali 2026, la simulazione probabilistica del rischio e la ripartizione fra comproprietari, e tiene un registro degli immobili in valutazione con acquisizione dei dati rispettosa delle regole dei portali.

Stato al 1 settembre 2026, seconda parte della giornata: non c'è una feature aperta sul modello. L'ultima aggiunta non riguarda il calcolo ma l'uso, cioè l'indice navigabile del workbook e il manuale operativo, nati da una segnalazione d'uso e non da un difetto di numeri. Tutte le voci della definizione di completamento sono chiuse, le tre voci di "Prossimo" della roadmap sono chiuse, i quattro limiti dichiarati che avevano una correzione delimitata sono stati corretti, e il lavoro è committato con l'albero pulito. Le schede di questa cartella sono ancorate al commit `a0b3420`.

## Definizione di completamento

- [x] Parametri fiscali 2026 verificati sulle fonti e datati
- [x] Motore di calcolo in Python con imposte, mutuo, locazione, metriche, confronto
- [x] Generatore del workbook con formule vive e nomi definiti
- [x] Verifica del workbook con Excel, nessuna cella in errore
- [x] Coincidenza fra motore Python e workbook sul caso di riferimento
- [x] Registro degli annunci con verifica del robots.txt e riversamento nel workbook
- [x] Modulo delle quotazioni OMI, con mirror open data e import della fornitura ufficiale
- [x] Modulo dei tassi correnti dal portale dati della Banca centrale europea
- [x] Cliente del modello linguistico locale, opzionale
- [x] Schede di dominio e registro delle fonti
- [x] Adozione del sistema di progetto del template
- [x] Suite di test automatici: motore di calcolo e struttura del workbook
- [x] Riordino della cartella, con il materiale personale sotto `_notes/` e la sua mappa
- [x] Foglio Confronto immobili, alimentato dal registro annunci
- [x] Simulatore mutuo con rimborsi volontari e percorso del tasso
- [x] Guide d'uso, tecnica e non tecnica, foglio per foglio
- [x] Foglio Comproprietà e documento sull'acquisto in più persone
- [x] Cruscotto di sintesi come primo foglio
- [x] Foglio Rischio: mille scenari con estrazioni fisse, analisi a tornado
- [x] Guida di avvio da zero
- [x] Registro delle fonti con l'uso tecnico di ciascuna e le lacune dichiarate
- [x] Strato didattico: master a undici voci e undici approfondimenti
- [x] Foglio Dossier tecnico: settantatre' documenti pre-acquisto con norma, peso e costo
- [x] Modulo `indicatori.py`: euro short-term rate e prezzi al consumo ISTAT
- [x] Blocco delle quotazioni OMI di zona nel foglio Confronto immobili, con lo scarto calcolato sul prezzo che il foglio usa
- [x] Regime di acquisto per riga, con il vuoto come terzo stato che eredita dal foglio Immobile
- [x] Normalizzazione dei campi a tre stati in ingresso
- [x] Riferimenti fra fogli per nome definito, e righe delle tabelle catturate invece che calcolate per offset
- [x] Prezzo massimo sostenibile in forma chiusa, con la cella di verifica accanto
- [x] Avvertenza nel foglio Confronto affitto per il caso senza mutuo
- [x] Percorso del tasso a sei gradini, con la misura del rialzo dalla serie storica dell'Euribor
- [x] Segnale di chiusura del piano nel Simulatore mutuo
- [x] Commit del lavoro del 1 settembre e ancoraggio dei frontmatter
- [x] Indice navigabile come primo foglio, con collegamento a ogni foglio e ritorno da ogni foglio
- [x] Manuale operativo: ogni comando con ogni opzione, ogni campo del registro, ogni foglio, diagnostica
- [x] Catena dei tassi: dall'overnight della BCE al preventivo, con gli scarti che la scompongono
- [x] Effetto dell'inflazione: Fisher esatto, scomposizione per componente, costo dell'indicizzazione rinunciata
- [x] Trattazione LaTeX della matematica del modello, con la tavola simbolo-cella-funzione
- [x] Workbook precompilato da una riga del registro, con l'azzeramento dei campi assenti
- [x] Comando che dice che cosa manca su ogni immobile e che cosa quel dato blocca
- [x] Controlli di plausibilità sugli input, nel Cruscotto, con il contatore in testa
- [x] Scheda di trattativa di una pagina in LaTeX, con il rifiuto di stampare ciò che non è calcolabile
- [x] Cinque colori con la legenda che li mostra, e colore proprio per le celle da scegliere
- [x] Fascia in testa a ogni foglio: qui si scrive oppure qui si legge
- [x] Opzioni della riga di comando per i campi che il comando mancanti chiede
- [x] Il percorso operativo e la mappa delle fonti in due diagrammi
- [x] Riordino di output in una cartella per immobile, e del LaTeX sotto docs/matematica
- [x] Il workbook precompilato non sovrascrive più il file-modello
- [x] Trattazione leggibile da zero: capitolo sulla notazione e 27 letture a parole
- [x] Tipografia italiana su tutto il progetto: accenti, trattini, con gli strumenti istanziati
- [x] Fusione delle due guide d'uso in [`guida-al-workbook.md`](../../docs/guida-al-workbook.md), senza perdita di contenuto
- [x] README pubblico completo, con architettura, modello, fonti e collegamenti verificati
- [x] Indice della documentazione, e prova di organizzazione in un vault Obsidian
- [x] Vault Obsidian aperto sulla radice, con la configurazione scritta nei file e non cliccata
- [x] Plugin allineati agli altri vault della macchina, alle stesse versioni
- [x] Forma del grafo misurata invece che prevista, e la previsione sbagliata conservata come lezione
- [x] Riferimenti fra documenti convertiti in collegamenti veri, da 15 a 186 archi, con lo strumento che mantiene la convenzione
- [x] Convenzione dei collegamenti dichiarata in [`interaction-style.md`](../rules/interaction-style.md), perché uno strumento senza regola è conoscenza che si perde
- [x] Trascrizione ChatGPT assorbita e cancellata, con l'imposta di soggiorno portata in [`fiscalita-locazione.md`](../../docs/fiscalita-locazione.md)
- [x] Comando `comune`: collegamento calcolato agli atti IMU, registro delle verifiche con la data, quattro esiti di scadenza
- [x] Tariffa dell'imposta di soggiorno di Civitanova letta e registrata, con la distinzione fra fonte operativa e atto
- [x] Cinque fonti nuove registrate in [`fonti.md`](../../docs/fonti.md), tutte aperte e verificate, nessuna citata di seconda mano
- [x] Fornitura OMI ripulita dalle righe del Piemonte, e il filtro trasformato in opzione `omi importa --regione`
- [x] Importazione resa atomica, con il rifiuto di un filtro che non tiene nessuna riga
- [x] Fattore comune nella simulazione del rischio, con la riduzione esatta al caso indipendente verificata in Excel
- [x] Studio dello stack per portare lo strumento in rete, con le fasce gratuite misurate e le piattaforme escluse
- [ ] Commit della tracciatura del 4 settembre, che spetta all'utente

## Riconciliazione

Fatta il 1 settembre 2026. Le sette schede di questa cartella, cioè [`STACK.md`](STACK.md), [`design-and-security.md`](design-and-security.md), [`deployment.md`](deployment.md), [`dev-testing.md`](dev-testing.md), `current-work.md`, [`roadmap.md`](roadmap.md) e [`studio-didattico-master.md`](studio-didattico-master.md), portano `generated-from-commit` e `last-verified-commit` ancorati a `a0b3420`, e nessuna porta più un segnaposto. Prima di ancorarle, `design-and-security.md` e `deployment.md` sono state allineate al lavoro della giornata, perché erano le due schede che non avevo toccato ma che il lavoro aveva reso in parte non più vere: la prima sul criterio con cui si sceglie cosa chiedere al modello locale e sul limite di copertura della doppia implementazione, la seconda sulla terza scadenza ricorrente e sul principio che una funzione di rete non entra nella catena che produce un artefatto.

Alla riconciliazione successiva la cosa da verificare per prima è se `parametri.py` sia stato toccato, perché governa due date indipendenti: la `REVISIONE` fiscale e il `verificato_il` delle risalite dell'Euribor.

## Domande aperte

Restano aperte le questioni che non hanno una correzione delimitata, e per ciascuna è scritto perché.

La fornitura OMI aggiornata richiede autenticazione personale ai servizi telematici e non è automatizzabile, per ADR-011. La scelta è accettare il download manuale semestrale, normalizzato da `omi.importa_fornitura`.

La tabella sul prezzo del foglio Scenari, cioè quella che fa variare il prezzo in sette scaglioni, calcola le imposte in modo esatto in colonna ma propaga al resto della riga l'assunzione che l'incidenza degli altri costi accessori resti quella dello scenario base. È l'ultimo residuo dell'approssimazione corretta il 1 settembre nel prezzo massimo sostenibile, e la correzione sarebbe la stessa: scomporre in parte proporzionale e parte fissa. Non è stata fatta perché quella tabella si legge come sensibilità e non come numero di decisione, ma è la prima cosa da prendere se qualcuno la usa per trattare.

Il piano del Simulatore mutuo si ferma a quarant'anni di rate, e sotto la modalità che riduce la durata un rialzo forte può non chiudere il piano entro la tabella. Dal 1 settembre il foglio lo dichiara con due righe di esito, ma non lo risolve: risolverlo richiederebbe una tabella più lunga di quanto abbia senso per un mutuo residenziale.

Nel foglio Confronto immobili restano globali l'opzione prezzo-valore e la qualifica di immobile di lusso, prese dal foglio Immobile. Portarle nel registro sarebbe meccanicamente identico a quanto fatto per prima casa e venditore impresa, e non è stato fatto perché la prima è una scelta che conviene quasi sempre e la seconda riguarda un caso raro: se in lista compare un immobile in categoria A/1, A/8 o A/9, va valutato a parte.

## Prossima azione concreta

Aprire l'account Cloudflare ed eseguire i primi passi della procedura, perché tutto ciò che si poteva scrivere senza account è scritto e provato. Le fasi uno e due-in-locale sono chiuse, la procedura e il flusso di distribuzione esistono, e nessuno dei nove passi è stato eseguito: il registro in fondo a [`messa-in-rete.md`](../../docs/messa-in-rete.md) lo dice riga per riga e va aggiornato appena uno si chiude. All'ambiente di sviluppo servono poi tre valori, nessuno segreto, cioè l'identificativo del database, il nome dell'organizzazione Zero Trust e l'etichetta del destinatario di Access; il solo segreto della catena è il token di interfaccia, che sta fra i segreti del repository con il nome `CLOUDFLARE_API_TOKEN`.

In parallelo, quando l'utente apre l'account: i nove passi di [`docs/messa-in-rete.md`](../../docs/messa-in-rete.md), di cui il primo, cioè verificare che l'account non abbia e non prenda un metodo di pagamento, è quello che protegge la gratuità. Sette li compie chi possiede l'account, due sono dell'ambiente di sviluppo, e il registro in fondo a quel documento è la fonte dello stato di avanzamento.

Sull'uso dello strumento di oggi, che resta il banco di prova, non è cambiato niente: manca la rendita catastale su tutti i quattordici immobili a registro, e l'aliquota IMU di Civitanova si legge dal collegamento che `valuta.py comune` costruisce e si annota con la data.
