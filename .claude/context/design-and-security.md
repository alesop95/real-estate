---
generated-from-commit: da assegnare al primo commit
generated-from-branch: main
generated-date: 2026-08-28
covers-paths:
  - src/immobiliare/annunci.py
  - src/immobiliare/llm_locale.py
  - .gitignore
last-verified-commit: da assegnare al primo commit
---

# Design e limiti legali

## Il principio che governa l'acquisizione dei dati

Il progetto tratta l'acquisizione automatica come una facolta' subordinata, non come la modalita' principale. L'ordine di preferenza e' inserimento manuale, incolla del testo con strutturazione locale, prelievo diretto della pagina, ed e' un ordine di preferenza anche giuridica oltre che tecnica.

Il prelievo diretto e' vincolato in tre modi che il codice impone da se'. Il `robots.txt` viene letto e rispettato per ogni singolo URL e non una volta per dominio, perche' un portale puo' consentire le pagine di dettaglio ed escludere quelle di ricerca. In caso di file non leggibile la risposta e' negativa: in assenza di permesso esplicito ci si astiene, non si presume. La frequenza e' limitata a una richiesta ogni cinque secondi per dominio, e lo user agent dichiara chi e' e a quale scopo.

Non esiste, e non va aggiunto, alcun meccanismo di aggiramento delle protezioni anti bot: nessuna rotazione di identita', nessun browser headless per superare un blocco, nessun servizio di risoluzione di sfide. Se un sito risponde con un blocco, la risposta corretta e' fermarsi. Il valore dello strumento non dipende dal prelievo automatico, e le due vie alternative restano sempre praticabili.

## I dati che non si raccolgono

Recapiti telefonici, indirizzi email e nomi di venditori privati e di agenti sono dati personali. Non vengono estratti dal prelievo, e il prompt del modello locale contiene l'istruzione esplicita di non riportarli. Il registro raccoglie i soli attributi economici e tecnici dell'immobile, piu' il link alla fonte, che e' il modo corretto di riferirsi al contenuto altrui senza appropriarsene.

Sul diritto sui generis del costitutore di banca dati la posizione e' che la raccolta qui e' puntuale e finalizzata a una decisione di acquisto personale, non un'estrazione sistematica di cataloghi. Il limite pratico e' la scala: decine di annunci seguiti nel tempo, non migliaia raccolti in massa.

## Perche' il modello linguistico e' locale

La strutturazione del testo di un annuncio e' un compito che un modello linguistico svolge bene ed e' l'unico punto del progetto in cui ne serve uno. La scelta di usare un'istanza sulla rete di casa invece di un servizio in cloud e' una scelta di riservatezza: il testo dell'annuncio, e con esso l'informazione su quali immobili si sta valutando e a che prezzo, e' informazione sensibile su una trattativa in corso, e non c'e' ragione perche' lasci la rete locale.

La dipendenza e' opzionale in senso forte. Il cliente solleva un'eccezione dedicata quando l'host non risponde, la riga di comando la intercetta e suggerisce la verifica, e tutto il resto continua a funzionare.

## Che cosa non entra nel repository

Il `.gitignore` esclude tre categorie distinte. Il materiale personale dell'utente in radice, cioe' le cartelle di documentazione dei singoli immobili, le visure, le planimetrie e i fogli di calcolo storici, perche' contiene dati di trattative reali. Il materiale di terzi scaricato come riferimento sotto `_notes/`, perche' non e' nostro da ridistribuire. Gli artefatti rigenerabili, cioe' il workbook prodotto e i file OMI scaricati, perche' si ricostruiscono dal codice e peserebbero inutilmente sulla storia.

Anche l'archivio degli annunci in `data/annunci.csv` resta fuori, e la scelta merita una riga di spiegazione perche' non e' ovvia. Il file e' piccolo ed e' il lavoro di ricerca di chi usa lo strumento, quindi versionarlo sarebbe naturale; contiene pero' i link agli immobili in trattativa e la colonna del prezzo obiettivo, che e' la propria strategia di acquisto. In una repository destinata a diventare pubblica quella colonna e' esattamente cio' che non si vuole pubblicare, e il valore di avere lo storico non compensa. Chi lavora in un repository privato tolga la riga dal `.gitignore`.

## Robustezza del generatore

Il generatore ha un modo di fallire che va conosciuto: scrive le formule senza valutarle, quindi produce file sintatticamente validi ma funzionalmente rotti senza segnalare nulla. Durante la costruzione un elemento di validazione dichiarato e mai associato ad alcuna cella ha generato un blocco XML vuoto che ha reso il file irricevibile per Excel. La difesa e' lo script di verifica, non l'attenzione.

Il secondo modo di fallire e' piu' insidioso perche' non produce errori: una formula che punta alla riga sbagliata calcola un numero plausibile. La difesa qui e' la doppia implementazione, cioe' il confronto fra il risultato del workbook e quello del motore Python sullo stesso caso, ed e' esattamente cosi' che e' stato trovato l'errore nella differenza fra i due patrimoni del foglio di confronto.
