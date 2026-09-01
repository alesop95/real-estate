---
generated-from-commit: a0b3420
generated-from-branch: main
generated-date: 2026-09-01
covers-paths:
  - pyproject.toml
  - requirements.txt
  - tools/**
last-verified-commit: a0b3420
---

# Ambiente ed esecuzione

## Non c'e' un deployment, e questo e' il punto

Il progetto non ha un server, un servizio o un ambiente di produzione: produce un file che si apre due volte al mese sulla macchina di chi decide. La scelta e' deliberata e discende dall'obiettivo, perche' uno strumento di valutazione deve funzionare fra due anni senza che nessuno abbia mantenuto un'infrastruttura nel frattempo.

La conseguenza pratica e' che l'unico artefatto che conta e' `output/Valutazione-Immobile.xlsx`, che non e' versionato perche' si rigenera in un secondo dal codice. Chi clona la repository ottiene il generatore, non il risultato, ed e' corretto cosi': il risultato contiene i numeri di una trattativa reale.

## Ambiente minimo

Python 3.11 o superiore con `openpyxl`. Nient'altro e' obbligatorio.

```
pip install openpyxl
python tools/valuta.py excel --con-annunci
```

Chi preferisce un ambiente isolato usi `pyproject.toml`, che dichiara la stessa dipendenza piu' `pytest` fra gli extra di sviluppo. Il file `requirements.txt` esiste per chi non vuole toccare nient'altro che `pip`.

## Ambiente di verifica

La verifica del workbook richiede Excel installato, perche' usa l'automazione COM per aprire il file e forzare il ricalcolo. E' un requisito di sviluppo, non d'uso: il workbook si apre anche con LibreOffice o Google Sheets, dove pero' la validazione a tendina e la formattazione condizionale possono rendere in modo diverso e la verifica automatica non e' disponibile.

```
powershell -NoProfile -ExecutionPolicy Bypass -File tools\verifica-excel.ps1
python tests\test_calcoli.py
```

I test non richiedono pytest: il file di test si esegue anche direttamente e riporta quanti sono passati e quali no. Con pytest installato, `python -m pytest tests` funziona allo stesso modo grazie alla configurazione in `pyproject.toml`.

## Dipendenze di rete, tutte opzionali

Quattro funzioni escono dalla macchina e nessuna e' necessaria al funzionamento del modello.

Il prelievo degli annunci contatta il portale, e solo se il suo `robots.txt` lo consente. La strutturazione del testo di un annuncio contatta un'istanza Ollama, il cui indirizzo predefinito e' quello standard in locale e si sovrascrive con la variabile d'ambiente `OLLAMA_HOST` quando il modello e' servito da un'altra macchina della propria rete; si verifica con `python tools/valuta.py llm stato`. Lo scarico delle quotazioni OMI storiche contatta il mirror open data su GitHub. La lettura dei tassi correnti e delle serie storiche degli indici contatta il portale dati della Banca centrale europea, senza chiave ne' registrazione, e la lettura dei prezzi al consumo contatta il servizio SDMX di ISTAT.

Se nessuna risponde, il generatore, il motore di calcolo, il registro annunci e i test continuano a funzionare. E' una proprieta' voluta e va preservata: nessuna di queste dipendenze deve diventare obbligatoria.

Su questa proprieta' va detto come e' stata mantenuta nel caso piu' recente, perche' la tentazione era nell'altra direzione. Le note del foglio Simulatore mutuo citano le peggiori risalite storiche dell'Euribor, e la via breve sarebbe stata leggerle dalla BCE durante la generazione del workbook. Avrebbe reso il generatore dipendente dalla rete e la generazione non riproducibile: due file generati in due momenti avrebbero potuto differire senza che nulla lo dichiarasse. I valori sono quindi congelati in `parametri.RISALITE_EURIBOR` con la propria data di verifica, e la rete serve solo al comando che li riverifica. La regola generale che ne discende e' che una funzione di rete puo' informare una decisione ma non deve entrare nella catena che produce un artefatto.

I test, allo stesso modo, non toccano la rete. La scansione delle risalite si verifica sostituendo la funzione di download con una che restituisce una serie sintetica, e il modulo degli indicatori ha un test dedicato al proprio degradare quando la rete non c'e'.

## Aggiornamento annuale

L'unica manutenzione prevista e' fiscale, e ha una procedura fissa. Si aggiornano i valori in `src/immobiliare/parametri.py` verificandoli sulle fonti di `docs/fonti.md`, si sposta la costante `REVISIONE` in testa al file, si aggiornano le schede di dominio sotto `docs/` nelle parti impattate, si eseguono i test e la verifica del workbook, e si rigenera.

I test sono la rete di sicurezza di questo passaggio: congelano il caso di riferimento e verificano gli scaglioni IRPEF, il minimo di legge del registro e i moltiplicatori catastali, che sono le tre cose che cambiano piu' spesso e che passerebbero inosservate.

## Manutenzione ricorrente, il promemoria

Le scadenze di questo progetto sono tre. Le prime due non sono automatizzabili perche' passano da una fonte che richiede una persona; la terza lo sarebbe, ed e' tenuta manuale per la ragione detta sopra, cioe' che il generatore non deve dipendere dalla rete.

**Una volta l'anno, dopo la legge di bilancio: aggiornamento fiscale.** E' la procedura della sezione precedente. Va fatta a gennaio o febbraio, quando la legge di bilancio e' in vigore e le circolari dell'Agenzia sono uscite.

**Due volte l'anno, a semestre chiuso: quotazioni OMI.** Cinque minuti, e vanno messi in calendario perche' altrimenti non si fanno. Il mirror open data che il modulo scarica da solo si ferma al secondo semestre 2018 ed e' utile solo per la serie storica; il dato corrente sta nella fornitura ufficiale, che e' gratuita ma vive dietro un'autenticazione personale con SPID, CIE, Entratel o Fisconline, che uno script non puo' e non deve simulare.

**Quando la BCE pubblica un semestre nuovo, o dopo un ciclo di rialzi: risalite dell'Euribor.** Un comando e due minuti. `python tools/valuta.py tassi --risalita` ricalcola sulla serie corrente le peggiori risalite su dodici, ventiquattro e trentasei mesi, le confronta con i valori congelati in `parametri.RISALITE_EURIBOR` e dichiara se sono ancora quelli. Se una finestra peggiore e' comparsa, si aggiorna la costante, si sposta il suo campo `verificato_il`, che e' separato dalla `REVISIONE` fiscale perche' le due scadenze sono indipendenti, e si rigenera il workbook, perche' tre note del foglio Simulatore mutuo sono interpolate da quei campi. Non e' una scadenza di calendario: e' una verifica da fare quando i tassi si sono mossi, ed e' anche il momento in cui serve, perche' e' allora che qualcuno rimette in discussione un mutuo variabile.

La procedura e' questa, e vale identica ogni volta.

```
1. https://telematici.agenziaentrate.gov.it, accesso con SPID o CIE
2. area riservata, Servizi ipotecari e catastali e Osservatorio del mercato immobiliare
3. Forniture dati OMI, Quotazioni immobiliari
4. semestre, e come ambito territoriale la regione: un raggio di ricerca
   realistico attraversa piu' province, e la regione costa un giro solo
5. python tools/valuta.py omi importa --file "<percorso dello zip scaricato>"
6. python tools/valuta.py omi cerca --comune "<Comune>"    per verificare che sia entrato
```

Il passo cinque normalizza l'archivio nella cartella di cache e riconosce da solo formato e codifica, quindi da li' in avanti tutto si comporta come col mirror. La cartella `data/omi/` non e' versionata: i file scaricati restano locali.

Le date utili sono la primavera per il secondo semestre dell'anno precedente e l'autunno per il primo semestre dell'anno in corso, perche' la pubblicazione arriva qualche mese dopo la chiusura del semestre. Chi tiene un registro di annunci attivo ha una ragione in piu' per non saltare il giro: la colonna dello scarto su OMI del foglio Annunci resta vuota finche' le quotazioni non sono in cache, e senza quella colonna il confronto fra immobili perde il suo unico riferimento indipendente dal prezzo richiesto.
