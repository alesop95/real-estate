---
generated-from-commit: a0b3420
generated-from-branch: main
generated-date: 2026-09-01
covers-paths:
  - src/immobiliare/**
  - tools/**
last-verified-commit: a0b3420
---

# Stack e architettura

## Scelte tecnologiche, e quelle deliberatamente escluse

Python della serie 3.13 con `openpyxl` come unica dipendenza obbligatoria. Tutto il resto è libreria standard: `csv`, `json`, `urllib`, `dataclasses`, `argparse`. La scelta è vincolata dall'obiettivo, che è uno strumento locale che deve funzionare fra due anni su una macchina qualsiasi senza dover ricostruire un ambiente.

Sono state escluse tre strade che sarebbero state naturali. Un'applicazione web con Streamlit, che avrebbe dato interattività ma avrebbe richiesto un processo in esecuzione e avrebbe perso la portabilità del file: il workbook con formule vive da' la stessa interattività senza dipendenze. Pandas, che per volumi di questa taglia aggiunge un peso di installazione senza dare nulla. Un database, che per un archivio di poche decine di righe destinato anche alla lettura umana è una complicazione: il CSV si apre in Excel, si modifica a mano e si versiona.

## Moduli

`parametri.py` non calcola nulla: espone i valori normativi in dataclass congelate, ciascuno con la fonte accanto, e una data di revisione in testa. È l'unico file da toccare all'aggiornamento annuale. Dal 1 settembre 2026 ospita anche `RISALITE_EURIBOR`, che non è un parametro normativo ma una misura empirica congelata: le peggiori risalite dell'Euribor a tre mesi su finestre di dodici, ventiquattro e trentasei mesi, con la propria data di verifica separata dalla revisione fiscale. Sta qui e non nel generatore perché il generatore non fa rete, e la riproducibilità del workbook vale più dell'aggiornamento automatico di un numero che si muove di rado.

`calcoli.py` contiene le funzioni di dominio pure, che prendono numeri e restituiscono numeri senza conoscere Excel né leggere file. Le strutture di ingresso sono `Immobile`, `Acquirente`, `Finanziamento`, `Gestione`; quelle di uscita sono `ImposteAcquisto`, `CostoOperazione`, `ContoEconomico`, `Metriche`. Il tasso interno di rendimento è risolto per bisezione anziché con Newton, perché sui flussi immobiliari, dove il primo termine è un esborso grande e i successivi sono piccoli e di segno costante, Newton diverge.

`stile.py` raccoglie palette, formati numerici e funzioni di composizione delle righe del workbook, così che il cambio di aspetto sia un intervento in un punto solo.

`excel_builder.py` è il generatore. La classe `Costruttore` tiene il registro dei nomi definiti e costruisce i venti fogli in sequenza, uno per metodo `foglio_*`, nell'ordine dichiarato in `costruisci()`. I riferimenti fra fogli passano sempre per nomi definiti, mai per indirizzi di cella, il che rende le formule leggibili e resistenti allo spostamento delle righe.

`annunci.py` tiene il registro CSV, verifica il `robots.txt`, limita la frequenza delle richieste, riduce l'HTML a testo e riversa nel workbook preservando le colonne di formula.

`omi.py` scarica e interroga le quotazioni dell'Osservatorio, riconoscendo da solo il formato del file fra quello del mirror open data e quello della fornitura ufficiale. Dal 4 settembre 2026 l'importazione accetta un filtro per regione e avviene in transito: i file si estraggono in una cartella temporanea, si filtrano lì e solo alla fine si spostano nella cache, così un filtro che non tiene nessuna riga fallisce senza aver toccato la fornitura precedente. La ragione è empirica: il file chiesto per le Marche conteneva anche il Piemonte, e `filtra_per_regione` rifiuta di scrivere un file vuoto elencando le regioni che ha trovato, perché il caso probabile è il nome di regione scritto in una forma diversa da quella della fornitura.

`comuni.py` risolve le due voci che non hanno un valore nazionale, l'aliquota IMU e l'imposta di soggiorno, senza inventarle. Costruisce il collegamento agli atti IMU di un Comune sul portale del Dipartimento delle finanze da due soli parametri, il codice catastale e la sigla della provincia, che legge dalla fornitura OMI già in cache, quindi non introduce una tabella di codici da mantenere; conserva invece nel registro `data/comuni-verifiche.csv` il collegamento all'atto dell'imposta di soggiorno, per cui un elenco nazionale non esiste, e il valore che una persona ha letto con la data in cui l'ha fatto. La funzione `stato_verifica` traduce quella data nei quattro esiti che discendono dal termine del 28 ottobre, oltre il quale l'atto dell'anno non cambia più. Non fa rete: costruisce indirizzi e legge file locali, quindi resta fuori dalla catena che produce il workbook.

`tassi.py` interroga il portale dati della Banca centrale europea per le statistiche armonizzate sui tassi bancari, serie MIR per le nuove erogazioni in Italia e serie FM per l'Euribor. Non ha chiave né registrazione, e traduce lo scarto fra il tasso di un preventivo e la media della sua tipologia in euro di interessi sull'intera durata, che è l'unica forma in cui un decimo di punto diventa una cifra su cui trattare. Le funzioni `risalite_storiche` ed `estremi_storici` usano la stessa serie per una domanda diversa, cioè di quanto un tasso variabile può salire: la prima scandisce tutte le finestre di durata fissata e restituisce la peggiore risalita che ciascuna contiene, che è una misura commensurabile con l'orizzonte di un mutuo, a differenza dell'escursione fra massimo e minimo assoluti della serie, che descrive un intervallo di ventisei anni. Alimentano l'opzione `--risalita` del comando `tassi` e, per confronto, la costante congelata in `parametri.py`.

`indicatori.py` legge le due grandezze di contesto che il modello usa come assunzione e che nessuno verifica: l'euro short-term rate, pubblicato dalla BCE ogni giorno lavorativo, e i prezzi al consumo NIC dal servizio SDMX di ISTAT, con l'indice armonizzato della BCE come riscontro incrociato. Ogni valore esce con il suo periodo, perché su queste serie la data è metà dell'informazione: l'euro short-term rate è di ieri, le serie mensili hanno settimane di ritardo, e il flusso NIC si ferma quando ISTAT ribasa l'indice.

`llm_locale.py` è un cliente minimale per Ollama, con le due sole chiamate che servono, generazione vincolata a JSON ed embedding. La dipendenza è opzionale in senso stretto: se l'host non risponde, tutto il resto funziona.

## Flusso di generazione del workbook

Il costruttore crea i fogli in un ordine che non è arbitrario. I nomi definiti sono di livello workbook, quindi la risoluzione non dipende dall'ordine, ma la leggibilità sì: si va dai parametri agli input, dagli input al calcolo, dal calcolo alla sintesi.

I fogli con tabelle lunghe, cioè il piano di ammortamento a quattrocentottanta righe, la tabella annuale del mutuo e le proiezioni a quaranta anni, sono generati per intero e le righe oltre l'orizzonte sono neutralizzate da una condizione nella formula anziché essere omesse. In questo modo l'utente può allungare la durata o l'orizzonte senza dover rigenerare il file.

Il foglio degli scenari non usa le tabelle di simulazione di Excel, che la libreria non sa creare, ma formule esplicite che ricostruiscono il calcolo per ciascuna combinazione. La tabella su tasso e canone è esatta; quella sul prezzo è un'approssimazione dichiarata, perché assume che l'incidenza percentuale dei costi accessori resti quella dello scenario base.

## Interfaccia a riga di comando

`tools/valuta.py` espone i sottocomandi `excel`, `riepilogo`, `annunci`, `omi`, `tassi`, `indicatori`, `llm`. Il sottocomando `annunci` ha a sua volta le azioni `elenca`, `confronta`, `aggiungi`, `modifica`, `importa`, `esporta`, `rimuovi` e `omi`. Il file non può chiamarsi come il pacchetto, perché altrimenti l'importazione ricadrebbe su se stesso.

Il sottocomando `riepilogo` riproduce a video il calcolo del workbook, e la coincidenza dei due risultati è il test di regressione principale del progetto. L'unica divergenza voluta riguarda il tasso interno di rendimento, perché la riga di comando assume un flusso costante mentre il workbook indicizza i costi all'inflazione.
