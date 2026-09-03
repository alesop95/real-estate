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

## Non c'è un deployment, e questo è il punto

Il progetto non ha un server, un servizio o un ambiente di produzione: produce un file che si apre due volte al mese sulla macchina di chi decide. La scelta è deliberata e discende dall'obiettivo, perché uno strumento di valutazione deve funzionare fra due anni senza che nessuno abbia mantenuto un'infrastruttura nel frattempo.

La conseguenza pratica è che l'unico artefatto che conta è `output/Valutazione-Immobile.xlsx`, che non è versionato perché si rigenera in un secondo dal codice. Chi clona la repository ottiene il generatore, non il risultato, ed è corretto così: il risultato contiene i numeri di una trattativa reale.

## Ambiente minimo

Python 3.11 o superiore con `openpyxl`. Nient'altro è obbligatorio.

```
pip install openpyxl
python tools/valuta.py excel --con-annunci
```

Chi preferisce un ambiente isolato usi `pyproject.toml`, che dichiara la stessa dipendenza più `pytest` fra gli extra di sviluppo. Il file `requirements.txt` esiste per chi non vuole toccare nient'altro che `pip`.

## Ambiente di verifica

La verifica del workbook richiede Excel installato, perché usa l'automazione COM per aprire il file e forzare il ricalcolo. È un requisito di sviluppo, non d'uso: il workbook si apre anche con LibreOffice o Google Sheets, dove però la validazione a tendina e la formattazione condizionale possono rendere in modo diverso e la verifica automatica non è disponibile.

```
powershell -NoProfile -ExecutionPolicy Bypass -File tools\verifica-excel.ps1
python tests\test_calcoli.py
```

I test non richiedono pytest: il file di test si esegue anche direttamente e riporta quanti sono passati e quali no. Con pytest installato, `python -m pytest tests` funziona allo stesso modo grazie alla configurazione in `pyproject.toml`.

## Dipendenze di rete, tutte opzionali

Quattro funzioni escono dalla macchina e nessuna è necessaria al funzionamento del modello.

Il prelievo degli annunci contatta il portale, e solo se il suo `robots.txt` lo consente. La strutturazione del testo di un annuncio contatta un'istanza Ollama, il cui indirizzo predefinito è quello standard in locale e si sovrascrive con la variabile d'ambiente `OLLAMA_HOST` quando il modello è servito da un'altra macchina della propria rete; si verifica con `python tools/valuta.py llm stato`. Lo scarico delle quotazioni OMI storiche contatta il mirror open data su GitHub. La lettura dei tassi correnti e delle serie storiche degli indici contatta il portale dati della Banca centrale europea, senza chiave né registrazione, e la lettura dei prezzi al consumo contatta il servizio SDMX di ISTAT.

Se nessuna risponde, il generatore, il motore di calcolo, il registro annunci e i test continuano a funzionare. È una proprietà voluta e va preservata: nessuna di queste dipendenze deve diventare obbligatoria.

Su questa proprietà va detto come è stata mantenuta nel caso più recente, perché la tentazione era nell'altra direzione. Le note del foglio Simulatore mutuo citano le peggiori risalite storiche dell'Euribor, e la via breve sarebbe stata leggerle dalla BCE durante la generazione del workbook. Avrebbe reso il generatore dipendente dalla rete e la generazione non riproducibile: due file generati in due momenti avrebbero potuto differire senza che nulla lo dichiarasse. I valori sono quindi congelati in `parametri.RISALITE_EURIBOR` con la propria data di verifica, e la rete serve solo al comando che li riverifica. La regola generale che ne discende è che una funzione di rete può informare una decisione ma non deve entrare nella catena che produce un artefatto.

I test, allo stesso modo, non toccano la rete. La scansione delle risalite si verifica sostituendo la funzione di download con una che restituisce una serie sintetica, e il modulo degli indicatori ha un test dedicato al proprio degradare quando la rete non c'è.

## Aggiornamento annuale

L'unica manutenzione prevista è fiscale, e ha una procedura fissa. Si aggiornano i valori in `src/immobiliare/parametri.py` verificandoli sulle fonti di [`docs/fonti.md`](../../docs/fonti.md), si sposta la costante `REVISIONE` in testa al file, si aggiornano le schede di dominio sotto `docs/` nelle parti impattate, si eseguono i test e la verifica del workbook, e si rigenera.

I test sono la rete di sicurezza di questo passaggio: congelano il caso di riferimento e verificano gli scaglioni IRPEF, il minimo di legge del registro e i moltiplicatori catastali, che sono le tre cose che cambiano più spesso e che passerebbero inosservate.

## Manutenzione ricorrente, il promemoria

Le scadenze di questo progetto sono tre. Le prime due non sono automatizzabili perché passano da una fonte che richiede una persona; la terza lo sarebbe, ed è tenuta manuale per la ragione detta sopra, cioè che il generatore non deve dipendere dalla rete.

**Una volta l'anno, dopo la legge di bilancio: aggiornamento fiscale.** È la procedura della sezione precedente. Va fatta a gennaio o febbraio, quando la legge di bilancio è in vigore e le circolari dell'Agenzia sono uscite.

**Due volte l'anno, a semestre chiuso: quotazioni OMI.** Cinque minuti, e vanno messi in calendario perché altrimenti non si fanno. Il mirror open data che il modulo scarica da solo si ferma al secondo semestre 2018 ed è utile solo per la serie storica; il dato corrente sta nella fornitura ufficiale, che è gratuita ma vive dietro un'autenticazione personale con SPID, CIE, Entratel o Fisconline, che uno script non può e non deve simulare.

**Quando la BCE pubblica un semestre nuovo, o dopo un ciclo di rialzi: risalite dell'Euribor.** Un comando e due minuti. `python tools/valuta.py tassi --risalita` ricalcola sulla serie corrente le peggiori risalite su dodici, ventiquattro e trentasei mesi, le confronta con i valori congelati in `parametri.RISALITE_EURIBOR` e dichiara se sono ancora quelli. Se una finestra peggiore è comparsa, si aggiorna la costante, si sposta il suo campo `verificato_il`, che è separato dalla `REVISIONE` fiscale perché le due scadenze sono indipendenti, e si rigenera il workbook, perché tre note del foglio Simulatore mutuo sono interpolate da quei campi. Non è una scadenza di calendario: è una verifica da fare quando i tassi si sono mossi, ed è anche il momento in cui serve, perché è allora che qualcuno rimette in discussione un mutuo variabile.

La procedura è questa, e vale identica ogni volta.

```
1. https://telematici.agenziaentrate.gov.it, accesso con SPID o CIE
2. area riservata, Servizi ipotecari e catastali e Osservatorio del mercato immobiliare
3. Forniture dati OMI, Quotazioni immobiliari
4. semestre, e come ambito territoriale la regione: un raggio di ricerca
   realistico attraversa piu' province, e la regione costa un giro solo
5. python tools/valuta.py omi importa --file "<percorso dello zip scaricato>"
6. python tools/valuta.py omi cerca --comune "<Comune>"    per verificare che sia entrato
```

Il passo cinque normalizza l'archivio nella cartella di cache e riconosce da solo formato e codifica, quindi da lì in avanti tutto si comporta come col mirror. La cartella `data/omi/` non è versionata: i file scaricati restano locali.

Le date utili sono la primavera per il secondo semestre dell'anno precedente e l'autunno per il primo semestre dell'anno in corso, perché la pubblicazione arriva qualche mese dopo la chiusura del semestre. Chi tiene un registro di annunci attivo ha una ragione in più per non saltare il giro: la colonna dello scarto su OMI del foglio Annunci resta vuota finché le quotazioni non sono in cache, e senza quella colonna il confronto fra immobili perde il suo unico riferimento indipendente dal prezzo richiesto.
