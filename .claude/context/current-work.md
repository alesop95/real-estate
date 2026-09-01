---
generated-from-commit: da assegnare al prossimo commit
generated-from-branch: main
generated-date: 2026-09-01
covers-paths:
  - src/**
  - tools/**
  - docs/**
last-verified-commit: da assegnare al prossimo commit
stato: strumento completo e verificato; nessuna feature attiva, resta il commit del lavoro del 1 settembre
---

# Lavoro in corso

## Feature: strumento di valutazione completo

Cosa fa. Genera un workbook Excel interattivo di ventun fogli che valuta l'acquisto di un immobile residenziale in Italia nelle tre destinazioni possibili, con i parametri fiscali 2026, la simulazione probabilistica del rischio e la ripartizione fra comproprietari, e tiene un registro degli immobili in valutazione con acquisizione dei dati rispettosa delle regole dei portali.

Stato al 1 settembre 2026: non c'e' una feature aperta. Tutte le voci della definizione di completamento sono chiuse, le tre voci di "Prossimo" della roadmap sono chiuse, e i quattro limiti dichiarati che avevano una correzione delimitata sono stati corretti. Resta il commit, che spetta all'utente.

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
- [x] Foglio Comproprieta' e documento sull'acquisto in piu' persone
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
- [ ] Commit del lavoro del 1 settembre, che spetta all'utente

## Da fare dopo il commit

Ancorare i campi `generated-from-commit` e `last-verified-commit` nelle schede di `.claude/context/` che li portano ancora come da assegnare, e il commit di riferimento nello snapshot di `.claude/memory/index.md`. Le schede interessate sono `STACK.md`, `design-and-security.md`, `deployment.md`, `dev-testing.md`, `current-work.md`, `roadmap.md` e `studio-didattico-master.md`.

## Domande aperte

Restano aperte le questioni che non hanno una correzione delimitata, e per ciascuna e' scritto perche'.

La fornitura OMI aggiornata richiede autenticazione personale ai servizi telematici e non e' automatizzabile, per ADR-011. La scelta e' accettare il download manuale semestrale, normalizzato da `omi.importa_fornitura`.

La tabella sul prezzo del foglio Scenari, cioe' quella che fa variare il prezzo in sette scaglioni, calcola le imposte in modo esatto in colonna ma propaga al resto della riga l'assunzione che l'incidenza degli altri costi accessori resti quella dello scenario base. E' l'ultimo residuo dell'approssimazione corretta il 1 settembre nel prezzo massimo sostenibile, e la correzione sarebbe la stessa: scomporre in parte proporzionale e parte fissa. Non e' stata fatta perche' quella tabella si legge come sensibilita' e non come numero di decisione, ma e' la prima cosa da prendere se qualcuno la usa per trattare.

La simulazione del foglio Rischio assume le variabili indipendenti, mentre nella realta' tassi, prezzi, sfitto e morosita' si muovono insieme. Introdurre una struttura di correlazione richiederebbe di stimare una matrice che nessuno ha, e sostituirebbe un'assunzione dichiarata con una nascosta: si e' scelto di restare indipendenti e dirlo nel foglio.

Il piano del Simulatore mutuo si ferma a quarant'anni di rate, e sotto la modalita' che riduce la durata un rialzo forte puo' non chiudere il piano entro la tabella. Dal 1 settembre il foglio lo dichiara con due righe di esito, ma non lo risolve: risolverlo richiederebbe una tabella piu' lunga di quanto abbia senso per un mutuo residenziale.

Nel foglio Confronto immobili restano globali l'opzione prezzo-valore e la qualifica di immobile di lusso, prese dal foglio Immobile. Portarle nel registro sarebbe meccanicamente identico a quanto fatto per prima casa e venditore impresa, e non e' stato fatto perche' la prima e' una scelta che conviene quasi sempre e la seconda riguarda un caso raro: se in lista compare un immobile in categoria A/1, A/8 o A/9, va valutato a parte.

## Prossima azione concreta

Committare. Sul merito, il lavoro utile non e' piu' sullo strumento ma con lo strumento: riempire il foglio Immobile con l'immobile reale scelto fra i dodici a registro, verificare l'aliquota IMU nella delibera del Comune e le spese nel consuntivo condominiale, chiedere la rendita catastale che nessuno dei dodici annunci indica, e leggere Cruscotto, coda bassa del foglio Rischio e prezzo massimo sostenibile con il suo scarto sul prezzo trattato. Se il mutuo in valutazione e' a tasso variabile, prima di firmare va compilato il percorso del tasso con il rialzo storico e letta la rata massima raggiunta.
