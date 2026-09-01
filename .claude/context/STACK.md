---
generated-from-commit: da assegnare al primo commit
generated-from-branch: main
generated-date: 2026-08-28
covers-paths:
  - src/immobiliare/**
  - tools/**
last-verified-commit: da assegnare al primo commit
---

# Stack e architettura

## Scelte tecnologiche, e quelle deliberatamente escluse

Python della serie 3.13 con `openpyxl` come unica dipendenza obbligatoria. Tutto il resto e' libreria standard: `csv`, `json`, `urllib`, `dataclasses`, `argparse`. La scelta e' vincolata dall'obiettivo, che e' uno strumento locale che deve funzionare fra due anni su una macchina qualsiasi senza dover ricostruire un ambiente.

Sono state escluse tre strade che sarebbero state naturali. Un'applicazione web con Streamlit, che avrebbe dato interattivita' ma avrebbe richiesto un processo in esecuzione e avrebbe perso la portabilita' del file: il workbook con formule vive da' la stessa interattivita' senza dipendenze. Pandas, che per volumi di questa taglia aggiunge un peso di installazione senza dare nulla. Un database, che per un archivio di poche decine di righe destinato anche alla lettura umana e' una complicazione: il CSV si apre in Excel, si modifica a mano e si versiona.

## Moduli

`parametri.py` non calcola nulla: espone i valori normativi in dataclass congelate, ciascuno con la fonte accanto, e una data di revisione in testa. E' l'unico file da toccare all'aggiornamento annuale.

`calcoli.py` contiene le funzioni di dominio pure, che prendono numeri e restituiscono numeri senza conoscere Excel ne' leggere file. Le strutture di ingresso sono `Immobile`, `Acquirente`, `Finanziamento`, `Gestione`; quelle di uscita sono `ImposteAcquisto`, `CostoOperazione`, `ContoEconomico`, `Metriche`. Il tasso interno di rendimento e' risolto per bisezione anziche' con Newton, perche' sui flussi immobiliari, dove il primo termine e' un esborso grande e i successivi sono piccoli e di segno costante, Newton diverge.

`stile.py` raccoglie palette, formati numerici e funzioni di composizione delle righe del workbook, cosi' che il cambio di aspetto sia un intervento in un punto solo.

`excel_builder.py` e' il generatore. La classe `Costruttore` tiene il registro dei nomi definiti e costruisce i venti fogli in sequenza, uno per metodo `foglio_*`, nell'ordine dichiarato in `costruisci()`. I riferimenti fra fogli passano sempre per nomi definiti, mai per indirizzi di cella, il che rende le formule leggibili e resistenti allo spostamento delle righe.

`annunci.py` tiene il registro CSV, verifica il `robots.txt`, limita la frequenza delle richieste, riduce l'HTML a testo e riversa nel workbook preservando le colonne di formula.

`omi.py` scarica e interroga le quotazioni dell'Osservatorio, riconoscendo da solo il formato del file fra quello del mirror open data e quello della fornitura ufficiale.

`tassi.py` interroga il portale dati della Banca centrale europea per le statistiche armonizzate sui tassi bancari, serie MIR per le nuove erogazioni in Italia e serie FM per l'Euribor. Non ha chiave ne' registrazione, e traduce lo scarto fra il tasso di un preventivo e la media della sua tipologia in euro di interessi sull'intera durata, che e' l'unica forma in cui un decimo di punto diventa una cifra su cui trattare.

`indicatori.py` legge le due grandezze di contesto che il modello usa come assunzione e che nessuno verifica: l'euro short-term rate, pubblicato dalla BCE ogni giorno lavorativo, e i prezzi al consumo NIC dal servizio SDMX di ISTAT, con l'indice armonizzato della BCE come riscontro incrociato. Ogni valore esce con il suo periodo, perche' su queste serie la data e' meta' dell'informazione: l'euro short-term rate e' di ieri, le serie mensili hanno settimane di ritardo, e il flusso NIC si ferma quando ISTAT ribasa l'indice.

`llm_locale.py` e' un cliente minimale per Ollama, con le due sole chiamate che servono, generazione vincolata a JSON ed embedding. La dipendenza e' opzionale in senso stretto: se l'host non risponde, tutto il resto funziona.

## Flusso di generazione del workbook

Il costruttore crea i fogli in un ordine che non e' arbitrario. I nomi definiti sono di livello workbook, quindi la risoluzione non dipende dall'ordine, ma la leggibilita' si': si va dai parametri agli input, dagli input al calcolo, dal calcolo alla sintesi.

I fogli con tabelle lunghe, cioe' il piano di ammortamento a quattrocentottanta righe, la tabella annuale del mutuo e le proiezioni a quaranta anni, sono generati per intero e le righe oltre l'orizzonte sono neutralizzate da una condizione nella formula anziche' essere omesse. In questo modo l'utente puo' allungare la durata o l'orizzonte senza dover rigenerare il file.

Il foglio degli scenari non usa le tabelle di simulazione di Excel, che la libreria non sa creare, ma formule esplicite che ricostruiscono il calcolo per ciascuna combinazione. La tabella su tasso e canone e' esatta; quella sul prezzo e' un'approssimazione dichiarata, perche' assume che l'incidenza percentuale dei costi accessori resti quella dello scenario base.

## Interfaccia a riga di comando

`tools/valuta.py` espone i sottocomandi `excel`, `riepilogo`, `annunci`, `omi`, `tassi`, `indicatori`, `llm`. Il sottocomando `annunci` ha a sua volta le azioni `elenca`, `confronta`, `aggiungi`, `modifica`, `importa`, `esporta`, `rimuovi` e `omi`. Il file non puo' chiamarsi come il pacchetto, perche' altrimenti l'importazione ricadrebbe su se stesso.

Il sottocomando `riepilogo` riproduce a video il calcolo del workbook, e la coincidenza dei due risultati e' il test di regressione principale del progetto. L'unica divergenza voluta riguarda il tasso interno di rendimento, perche' la riga di comando assume un flusso costante mentre il workbook indicizza i costi all'inflazione.
