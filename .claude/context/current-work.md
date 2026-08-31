---
generated-from-commit: ba9397c
generated-from-branch: main
generated-date: 2026-08-31
covers-paths:
  - src/**
  - tools/**
  - docs/**
last-verified-commit: ba9397c
stato: strumento completo e verificato; lavoro dell'ultima sessione su disco, non committato
---

# Lavoro in corso

## Feature: strumento di valutazione completo

Cosa fa. Genera un workbook Excel interattivo di diciannove fogli che valuta l'acquisto di un immobile residenziale in Italia nelle tre destinazioni possibili, con i parametri fiscali 2026, la simulazione probabilistica del rischio e la ripartizione fra comproprietari, e tiene un registro degli immobili in valutazione con acquisizione dei dati rispettosa delle regole dei portali.

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
- [x] Strato didattico: master a sette voci e sette approfondimenti
- [ ] Commit del lavoro dell'ultima sessione, che spetta all'utente

## Da fare dopo il commit

Aggiornare nelle quattro schede di `.claude/context/` che lo dichiarano i campi `generated-from-commit` e `last-verified-commit`, e il commit di riferimento nello snapshot di `.claude/memory/index.md`.

## Domande aperte

La fornitura OMI aggiornata richiede autenticazione personale ai servizi telematici e non e' automatizzabile. La scelta attuale e' accettare il download manuale semestrale, normalizzato da `omi.importa_fornitura`. L'alternativa, una consultazione puntuale sul servizio a video, non darebbe un file riutilizzabile e ricadrebbe sotto ADR-004.

Il foglio degli scenari calcola la tabella sul prezzo con un'approssimazione, perche' assume che l'incidenza percentuale dei costi accessori resti quella dello scenario base. E' dichiarato nel foglio. Renderla esatta richiederebbe di replicare l'intero calcolo delle imposte in ogni cella, cosa gia' fatta per la colonna delle imposte ma non propagata al resto.

Il confronto fra comprare e affittare non modella il caso in cui chi compra non ha un mutuo. Funziona, perche' la rata risulta nulla, ma il confronto perde di significato: andrebbe aggiunta un'avvertenza nel foglio.

Il foglio Confronto immobili applica a tutti gli immobili il regime di acquisto impostato nel foglio Immobile. E' dichiarato nel foglio, ma rende non confrontabile un usato accanto a un nuovo da costruttore. Renderlo per riga richiederebbe due colonne di input nel registro e formule piu' pesanti.

La simulazione del foglio Rischio assume le variabili indipendenti, mentre nella realta' tassi, prezzi, sfitto e morosita' si muovono insieme. Introdurre una struttura di correlazione richiederebbe di stimare una matrice che nessuno ha, e sostituirebbe un'assunzione dichiarata con una nascosta: si e' scelto di restare indipendenti e dirlo nel foglio.

Gli indici di riga del conto economico nel foglio Locazione sono calcolati per offset da una base. Chi inserisce una riga in mezzo deve aggiornare i quattro offset, e il segnale che non l'ha fatto e' un valore di sintesi plausibile e falso. E' il punto piu' fragile del generatore, documentato in `refactor-05`.

## Prossima azione concreta

Committare, poi ancorare i frontmatter. Sul merito, riempire il foglio Immobile con un immobile reale e leggere Cruscotto e coda bassa del foglio Rischio.
