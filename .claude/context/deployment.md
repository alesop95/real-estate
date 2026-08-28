---
generated-from-commit: da assegnare al primo commit
generated-from-branch: main
generated-date: 2026-08-28
covers-paths:
  - pyproject.toml
  - requirements.txt
  - tools/**
last-verified-commit: da assegnare al primo commit
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

Il prelievo degli annunci contatta il portale, e solo se il suo `robots.txt` lo consente. La strutturazione del testo di un annuncio contatta un'istanza Ollama, il cui indirizzo predefinito e' quello standard in locale e si sovrascrive con la variabile d'ambiente `OLLAMA_HOST` quando il modello e' servito da un'altra macchina della propria rete; si verifica con `python tools/valuta.py llm stato`. Lo scarico delle quotazioni OMI storiche contatta il mirror open data su GitHub. La lettura dei tassi correnti contatta il portale dati della Banca centrale europea, senza chiave ne' registrazione.

Se nessuna delle tre risponde, il generatore, il motore di calcolo, il registro annunci e i test continuano a funzionare. E' una proprieta' voluta e va preservata: nessuna di queste dipendenze deve diventare obbligatoria.

## Aggiornamento annuale

L'unica manutenzione prevista e' fiscale, e ha una procedura fissa. Si aggiornano i valori in `src/immobiliare/parametri.py` verificandoli sulle fonti di `docs/fonti.md`, si sposta la costante `REVISIONE` in testa al file, si aggiornano le schede di dominio sotto `docs/` nelle parti impattate, si eseguono i test e la verifica del workbook, e si rigenera.

I test sono la rete di sicurezza di questo passaggio: congelano il caso di riferimento e verificano gli scaglioni IRPEF, il minimo di legge del registro e i moltiplicatori catastali, che sono le tre cose che cambiano piu' spesso e che passerebbero inosservate.
