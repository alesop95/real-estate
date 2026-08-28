---
generated-from-commit: da assegnare al primo commit
generated-from-branch: main
generated-date: 2026-08-28
covers-paths:
  - src/**
  - tools/**
  - docs/**
last-verified-commit: da assegnare al primo commit
stato: costruzione iniziale completata, in attesa del primo commit
---

# Lavoro in corso

## Feature: strumento di valutazione completo

Cosa fa. Genera un workbook Excel interattivo che valuta l'acquisto di un immobile residenziale in Italia nelle tre destinazioni possibili, con i parametri fiscali 2026, e tiene un registro degli immobili in valutazione con acquisizione dei dati rispettosa delle regole dei portali.

## Definizione di completamento

- [x] Parametri fiscali 2026 verificati sulle fonti e datati
- [x] Motore di calcolo in Python con imposte, mutuo, locazione, metriche, confronto
- [x] Generatore del workbook con formule vive e nomi definiti
- [x] Verifica del workbook con Excel, nessuna cella in errore
- [x] Coincidenza fra motore Python e workbook sul caso di riferimento
- [x] Registro degli annunci con verifica del robots.txt e riversamento nel workbook
- [x] Modulo delle quotazioni OMI
- [x] Cliente del modello linguistico locale, opzionale
- [x] Schede di dominio e registro delle fonti
- [x] Adozione del sistema di progetto del template
- [x] Suite di test automatici: motore di calcolo e struttura del workbook
- [x] Riordino della cartella, con il materiale personale sotto `_notes/` e la sua mappa
- [x] Foglio Confronto immobili, alimentato dal registro annunci
- [x] Colonne del registro allineate al foglio di lavoro precedente
- [ ] Primo commit, con ancoraggio dei frontmatter di riconciliazione

## Da fare subito dopo il primo commit

Sostituire in tutte e sei le schede di `.claude/context/` i segnaposto `da assegnare al primo commit` nei campi `generated-from-commit` e `last-verified-commit` con l'hash del commit iniziale, e aggiornare il commit di riferimento nello snapshot di `.claude/memory/index.md`. Da quel momento il drift si misura normalmente rispetto a HEAD.

## Domande aperte

La fornitura OMI aggiornata richiede autenticazione personale ai servizi telematici e non e' automatizzabile. Resta da decidere se accettare il download manuale semestrale come procedura, che e' la scelta attuale, oppure se costruire un percorso di consultazione puntuale sul servizio a video, che pero' non da' un file riutilizzabile.

Il foglio degli scenari calcola la tabella sul prezzo con un'approssimazione, perche' assume che l'incidenza percentuale dei costi accessori resti quella dello scenario base. E' dichiarato nel foglio. Renderla esatta richiederebbe di replicare l'intero calcolo delle imposte in ogni cella, cosa gia' fatta per la colonna delle imposte ma non propagata al resto: da valutare se ne valga la complessita'.

Il confronto fra comprare e affittare non modella il caso in cui chi compra non ha un mutuo. Funziona, perche' la rata risulta nulla, ma il confronto perde di significato: andrebbe aggiunta un'avvertenza nel foglio.

Il foglio Confronto immobili applica a tutti gli immobili il regime di acquisto impostato nel foglio Immobile, cioe' prima casa oppure no, privato oppure impresa con IVA. E' dichiarato nel foglio, ma resta una semplificazione che rende non confrontabile un usato accanto a un nuovo da costruttore. Renderlo per riga richiederebbe due colonne di input nel registro e formule piu' pesanti: da valutare quando capitera' di confrontare davvero i due casi insieme.

## Prossima azione concreta

Il repository e' inizializzato, l'identita' git e' impostata in locale e l'albero e' pulito: restano solo i file di progetto, perche' il materiale personale e' sotto `_notes/` e l'archivio annunci e' escluso. Manca il primo commit, che spetta all'utente, e subito dopo l'ancoraggio dei frontmatter.
