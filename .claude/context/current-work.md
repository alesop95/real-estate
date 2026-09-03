---
generated-from-commit: a0b3420
generated-from-branch: main
generated-date: 2026-09-01
covers-paths:
  - src/**
  - tools/**
  - docs/**
last-verified-commit: a0b3420
stato: strumento completo e verificato; nessuna feature attiva, nessun lavoro pendente
---

# Lavoro in corso

## Feature: strumento di valutazione completo

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
- [x] Fusione delle due guide d'uso in `guida-al-workbook.md`, senza perdita di contenuto
- [x] README pubblico completo, con architettura, modello, fonti e collegamenti verificati
- [x] Indice della documentazione, e prova di organizzazione in un vault Obsidian
- [ ] Commit del lavoro dal 1 al 3 settembre, che spetta all'utente

## Riconciliazione

Fatta il 1 settembre 2026. Le sette schede di questa cartella, cioè `STACK.md`, `design-and-security.md`, `deployment.md`, `dev-testing.md`, `current-work.md`, `roadmap.md` e `studio-didattico-master.md`, portano `generated-from-commit` e `last-verified-commit` ancorati a `a0b3420`, e nessuna porta più un segnaposto. Prima di ancorarle, `design-and-security.md` e `deployment.md` sono state allineate al lavoro della giornata, perché erano le due schede che non avevo toccato ma che il lavoro aveva reso in parte non più vere: la prima sul criterio con cui si sceglie cosa chiedere al modello locale e sul limite di copertura della doppia implementazione, la seconda sulla terza scadenza ricorrente e sul principio che una funzione di rete non entra nella catena che produce un artefatto.

Alla riconciliazione successiva la cosa da verificare per prima è se `parametri.py` sia stato toccato, perché governa due date indipendenti: la `REVISIONE` fiscale e il `verificato_il` delle risalite dell'Euribor.

## Domande aperte

Restano aperte le questioni che non hanno una correzione delimitata, e per ciascuna è scritto perché.

La fornitura OMI aggiornata richiede autenticazione personale ai servizi telematici e non è automatizzabile, per ADR-011. La scelta è accettare il download manuale semestrale, normalizzato da `omi.importa_fornitura`.

La tabella sul prezzo del foglio Scenari, cioè quella che fa variare il prezzo in sette scaglioni, calcola le imposte in modo esatto in colonna ma propaga al resto della riga l'assunzione che l'incidenza degli altri costi accessori resti quella dello scenario base. È l'ultimo residuo dell'approssimazione corretta il 1 settembre nel prezzo massimo sostenibile, e la correzione sarebbe la stessa: scomporre in parte proporzionale e parte fissa. Non è stata fatta perché quella tabella si legge come sensibilità e non come numero di decisione, ma è la prima cosa da prendere se qualcuno la usa per trattare.

La simulazione del foglio Rischio assume le variabili indipendenti, mentre nella realtà tassi, prezzi, sfitto e morosità si muovono insieme. Introdurre una struttura di correlazione richiederebbe di stimare una matrice che nessuno ha, e sostituirebbe un'assunzione dichiarata con una nascosta: si è scelto di restare indipendenti e dirlo nel foglio.

Il piano del Simulatore mutuo si ferma a quarant'anni di rate, e sotto la modalità che riduce la durata un rialzo forte può non chiudere il piano entro la tabella. Dal 1 settembre il foglio lo dichiara con due righe di esito, ma non lo risolve: risolverlo richiederebbe una tabella più lunga di quanto abbia senso per un mutuo residenziale.

Nel foglio Confronto immobili restano globali l'opzione prezzo-valore e la qualifica di immobile di lusso, prese dal foglio Immobile. Portarle nel registro sarebbe meccanicamente identico a quanto fatto per prima casa e venditore impresa, e non è stato fatto perché la prima è una scelta che conviene quasi sempre e la seconda riguarda un caso raro: se in lista compare un immobile in categoria A/1, A/8 o A/9, va valutato a parte.

## Prossima azione concreta

Sullo strumento non c'è una prossima azione: il lavoro utile è passato all'uso dello strumento. Riempire il foglio Immobile con l'immobile reale scelto fra i dodici a registro, verificare l'aliquota IMU nella delibera del Comune e le spese nel consuntivo condominiale, chiedere la rendita catastale che nessuno dei dodici annunci indica, e leggere Cruscotto, coda bassa del foglio Rischio e prezzo massimo sostenibile con il suo scarto sul prezzo trattato. Se il mutuo in valutazione è a tasso variabile, prima di firmare va compilato il percorso del tasso con il rialzo storico e letta la rata massima raggiunta.
