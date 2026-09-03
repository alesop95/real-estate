---
generated-from-commit: a0b3420
generated-from-branch: main
generated-date: 2026-09-01
covers-paths:
  - src/immobiliare/annunci.py
  - src/immobiliare/llm_locale.py
  - .gitignore
last-verified-commit: a0b3420
---

# Design e limiti legali

## Il principio che governa l'acquisizione dei dati

Il progetto tratta l'acquisizione automatica come una facoltà subordinata, non come la modalità principale. L'ordine di preferenza è inserimento manuale, incolla del testo con strutturazione locale, prelievo diretto della pagina, ed è un ordine di preferenza anche giuridica oltre che tecnica.

Il prelievo diretto è vincolato in tre modi che il codice impone da sé. Il `robots.txt` viene letto e rispettato per ogni singolo URL e non una volta per dominio, perché un portale può consentire le pagine di dettaglio ed escludere quelle di ricerca. In caso di file non leggibile la risposta è negativa: in assenza di permesso esplicito ci si astiene, non si presume. La frequenza è limitata a una richiesta ogni cinque secondi per dominio, e lo user agent dichiara chi è e a quale scopo.

Non esiste, e non va aggiunto, alcun meccanismo di aggiramento delle protezioni anti bot: nessuna rotazione di identità, nessun browser headless per superare un blocco, nessun servizio di risoluzione di sfide. Se un sito risponde con un blocco, la risposta corretta è fermarsi. Il valore dello strumento non dipende dal prelievo automatico, e le due vie alternative restano sempre praticabili.

## I servizi autenticati dell'area riservata, e i loro vincoli

Il progetto usa quattro servizi dell'area riservata dell'Agenzia delle Entrate, sempre a mano e mai da programma: le forniture dei dati OMI, le visure e le ispezioni ipotecarie, la consultazione dei valori immobiliari dichiarati e la consultazione dei fogli di mappa. Accedendovi si accettano le condizioni generali per l'accesso diretto ai servizi telematici di consultazione della banca dati catastale, emanate con decreto del direttore dell'Agenzia del Territorio del 4 maggio 2007 e da ultimo integrate con provvedimento del 28 giugno 2017. Da quelle condizioni discendono tre vincoli operativi che vale enunciare, perché due riguardano il codice e uno riguarda l'uso.

Il primo è che l'accesso avviene previa autenticazione personale nell'area riservata, e questo chiude la questione dell'automazione: simulare quell'autenticazione significherebbe usare le credenziali di una persona per far interrogare la banca dati a un programma, che è esattamente il contrario di ciò che l'articolo 2 prevede. È la stessa conclusione di ADR-004, raggiunta per una via diversa: lì era il `robots.txt` a mancare, qui è l'autenticazione a esserci.

Il secondo è l'articolo 5, per cui l'Agenzia si riserva di introdurre limiti al numero di interrogazioni giornaliere per singolo utente. Anche prescindendo dall'autenticazione, un uso automatizzato e ripetuto ricadrebbe nell'uso eccessivo di cui l'articolo 3 rende responsabile l'utente, e l'articolo 4 sanziona la violazione con l'inibizione del servizio. Il rischio, quindi, non è teorico: è la perdita dell'accesso.

Il terzo riguarda cosa si fa dei dati una volta ottenuti. L'articolo 3 impegna a usare informazioni e documenti esclusivamente per i fini consentiti dalla legge e nel rispetto della normativa sulla protezione dei dati personali. Valutare l'acquisto di un immobile su cui si sta trattando è un fine consentito e proporzionato; costruire un archivio, ridistribuire i documenti o consultare immobili estranei alla trattativa non lo sono. Le visure e le ispezioni sul venditore contengono dati personali di terzi, e restano quindi sotto `_notes/`, che non è versionato, insieme a tutto il materiale della trattativa.

A queste si aggiunge un obbligo specifico della fornitura OMI, che è gratuita ma richiede di citare la fonte quando i dati vengono usati. La stringa dovuta è `Agenzia Entrate - OMI`, sta nella costante `omi.ATTRIBUZIONE`, ed è stampata in coda a ogni interrogazione e dichiarata nel foglio Fonti del workbook accanto alle colonne che ne derivano.

## I dati che non si raccolgono

Recapiti telefonici, indirizzi email e nomi di venditori privati e di agenti sono dati personali. Non vengono estratti dal prelievo, e il prompt del modello locale contiene l'istruzione esplicita di non riportarli. Il registro raccoglie i soli attributi economici e tecnici dell'immobile, più il link alla fonte, che è il modo corretto di riferirsi al contenuto altrui senza appropriarsene.

Sul diritto sui generis del costitutore di banca dati la posizione è che la raccolta qui è puntuale e finalizzata a una decisione di acquisto personale, non un'estrazione sistematica di cataloghi. Il limite pratico è la scala: decine di annunci seguiti nel tempo, non migliaia raccolti in massa.

## Perché il modello linguistico è locale

La strutturazione del testo di un annuncio è un compito che un modello linguistico svolge bene ed è l'unico punto del progetto in cui ne serve uno. La scelta di usare un'istanza sulla rete di casa invece di un servizio in cloud è una scelta di riservatezza: il testo dell'annuncio, e con esso l'informazione su quali immobili si sta valutando e a che prezzo, è informazione sensibile su una trattativa in corso, e non c'è ragione perché lasci la rete locale.

La dipendenza è opzionale in senso forte. Il cliente solleva un'eccezione dedicata quando l'host non risponde, la riga di comando la intercetta e suggerisce la verifica, e tutto il resto continua a funzionare.

Ciò che si chiede al modello, però, va scelto con un criterio, e il criterio non è quanto il modello sia capace di rispondere. Lo schema di estrazione contiene solo dati che stanno scritti nell'annuncio. Quando il 1 settembre 2026 il registro ha guadagnato i due campi del regime di acquisto, `venditore_impresa` è entrato nello schema perché la vendita diretta dal costruttore, o il prezzo dichiarato soggetto a IVA, sono informazioni che il testo porta; `prima_casa` non è entrato, perché non è una caratteristica dell'immobile ma della posizione di chi compra rispetto a esso, e il testo non la conosce. Chiederla comunque avrebbe prodotto una risposta, perché un modello linguistico risponde: sarebbe stata un'ipotesi presentata come dato estratto, che è il modo peggiore di riempire un campo che decide le imposte.

Dallo stesso passaggio viene un presidio sull'output. Un modello, a una domanda che somiglia a un booleano, risponde volentieri `true`, ed Excel confronta il testo senza distinguere le maiuscole ma `true` resta diverso da `SI`: il foglio lo avrebbe letto come un NO senza segnalare nulla. I quattro campi a tre stati si normalizzano quindi in `__post_init__` della dataclass, cioè su ogni annuncio da qualunque origine e non solo su quelli che passano dal modello, e la normalizzazione si ferma dove finisce la certezza, lasciando intatto ciò che non riconosce. Il principio generale, che vale per qualunque output di un modello linguistico che entri in un calcolo, è che va normalizzato al confine e non nel punto d'uso, e che ciò che non si riconosce non si traduce per ipotesi.

## Che cosa non entra nel repository

Il `.gitignore` esclude tre categorie distinte. Il materiale personale dell'utente in radice, cioè le cartelle di documentazione dei singoli immobili, le visure, le planimetrie e i fogli di calcolo storici, perché contiene dati di trattative reali. Il materiale di terzi scaricato come riferimento sotto `_notes/`, perché non è nostro da ridistribuire. Gli artefatti rigenerabili, cioè il workbook prodotto e i file OMI scaricati, perché si ricostruiscono dal codice e peserebbero inutilmente sulla storia.

Anche l'archivio degli annunci in `data/annunci.csv` resta fuori, e la scelta merita una riga di spiegazione perché non è ovvia. Il file è piccolo ed è il lavoro di ricerca di chi usa lo strumento, quindi versionarlo sarebbe naturale; contiene però i link agli immobili in trattativa e la colonna del prezzo obiettivo, che è la propria strategia di acquisto. In una repository destinata a diventare pubblica quella colonna è esattamente ciò che non si vuole pubblicare, e il valore di avere lo storico non compensa. Chi lavora in un repository privato tolga la riga dal `.gitignore`.

## Robustezza del generatore

Il generatore ha un modo di fallire che va conosciuto: scrive le formule senza valutarle, quindi produce file sintatticamente validi ma funzionalmente rotti senza segnalare nulla. Durante la costruzione un elemento di validazione dichiarato e mai associato ad alcuna cella ha generato un blocco XML vuoto che ha reso il file irricevibile per Excel. La difesa è lo script di verifica, non l'attenzione.

Il secondo modo di fallire è più insidioso perché non produce errori: una formula che punta alla riga sbagliata calcola un numero plausibile. La difesa qui è la doppia implementazione, cioè il confronto fra il risultato del workbook e quello del motore Python sullo stesso caso, ed è esattamente così che è stato trovato l'errore nella differenza fra i due patrimoni del foglio di confronto.

Quella difesa, però, ha un limite di copertura che il 1 settembre 2026 si è manifestato: vale sui valori che il motore Python calcola, e non su tutto ciò che il workbook contiene. Il verdetto fra comprare e affittare sul Cruscotto leggeva una coordinata fissa di un altro foglio, quella coordinata era diventata la riga sbagliata, e nessun confronto fra le due implementazioni lo copriva perché il motore Python non produce quel verdetto. Ne è seguita ADR-013, che vieta i riferimenti per coordinata e li sostituisce con nomi definiti fra fogli e con righe restituite dagli helper dentro le tabelle. La ragione è che quelle due forme falliscono in modo visibile, con un `#NOME?` in cella o un'eccezione alla generazione, mentre una coordinata sbagliata resta un riferimento valido a una cella diversa. È la stessa logica del presidio contro il primo modo di fallire: non si difende l'attenzione, si sceglie la forma che rende l'errore rumoroso.
