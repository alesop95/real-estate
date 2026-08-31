# Work-log

> Append-only, in ordine cronologico inverso. Ogni voce riporta data, file toccati, motivo.

## 2026-08-31, articoli civilistici del corpus, acquisto in piu' persone e scenari settabili

File toccati: `src/immobiliare/excel_builder.py` (foglio Comproprieta' e blocco dei tre scenari), `tests/test_workbook.py`, `docs/comprare-in-piu-persone.md` nuovo, `docs/guida-tecnica.md`, `docs/guida-non-tecnica.md`, `docs/fonti.md`, `CLAUDE.md`, `README.md`.

Articoli civilistici. L'utente aveva enumerato a mano nel suo foglio precedente dieci articoli del codice civile, dei quali il modello ne citava due. Recuperati dal corpus locale quarantatre' articoli con testo e rubrica, tutti trovati: le fasi contrattuali dal 1326 al 1403 con il 2645-bis, il 2775-bis, il 2825-bis e il 2932, la garanzia per vizi, e l'intero titolo sulla comunione dal 1100 al 1116 piu' il 2247 e il 2248 sul confine con la societa'. Sono ora il riferimento normativo della guida tecnica.

Acquisto in piu' persone. Nuovo foglio Comproprieta', fino a otto acquirenti. La risposta di merito viene dall'articolo 2248: la comunione costituita o mantenuta al solo scopo del godimento non e' un contratto di societa', quindi comprare insieme e affittare non richiede di costituire nulla. Il foglio ripartisce per quote e calcola l'imposta di ciascuno separatamente, perche' l'opzione per la cedolare secca si esercita disgiuntamente e vale solo per chi l'ha esercitata, e l'aliquota marginale e' personale: verificato che con due acquirenti in regimi diversi le imposte divergono correttamente. Una riga di controllo segnala se le quote non sommano a cento, perche' con quote incoerenti il foglio mentirebbe in silenzio, e i totali di colonna riconciliano con il resto del workbook.

Scenari settabili. Aggiunto al foglio Scenari un blocco a tre colonne, pessimistico, base e ottimistico, con canone, sfitto, morosita', tasso e rivalutazione impostabili per ciascuna, e in uscita ricavo effettivo, reddito operativo netto, utile, cash flow, rendimento netto, debt service coverage ratio e patrimonio netto a fine orizzonte. Il debito residuo usa la formula chiusa dell'ammortamento alla francese, quindi resta esatto anche cambiando il tasso di scenario. La colonna base riconcilia con il resto del modello.

Legge 448/1998. Provata anche la raccolta di Bosetti e Gatti indicata dall'utente: riporta l'articolo 7 in omissis. Con Normattiva che rende gli articoli via JavaScript e il corpus locale che non ha l'atto, il testo primario resta non recuperabile e la lacuna e' dichiarata in `docs/fonti.md`; le regole del credito d'imposta sono ricostruite da fonti professionali.

Verifica: trentanove test verdi, workbook a sedici fogli riaperto con Excel senza celle in errore.

## 2026-08-29, fonti residue chiuse: trascrizioni, canale Telegram, legge regionale, e tre correzioni al modello

File toccati: `src/immobiliare/excel_builder.py`, `src/immobiliare/omi.py`, `src/immobiliare/parametri.py`, `tools/valuta.py`, `docs/fonti.md`, le due guide, `_notes/INDICE-MATERIALE.md`.

Trascrizioni dei video. I quattro video segnalati sono stati trascritti senza ricorrere al riconoscimento vocale: YouTube espone i sottotitoli automatici italiani e `yt-dlp` li scarica direttamente. Circa 68.000 parole ripulite dalla sovrapposizione tipica delle didascalie automatiche. Da qui vengono due voci nuove del modello.

Canale Telegram. L'utente ha esportato a mano il sottocanale "Tassazione, spese, mutui", che dall'esterno non era leggibile perche' il gruppo sta dietro un passaggio anti bot. Quasi sedicimila messaggi su due anni e mezzo, filtrati a 2.385 pertinenti e 932 sostanziosi. Da qui viene la terza correzione.

Legge regionale delle Marche sul turismo. Il PDF non era estraibile perche' privo di mappa Unicode; la conversione in JSON fornita dall'utente ha permesso di ricostruire il testo. Ne esce la soglia che mancava: l'articolo 33 consente l'uso occasionale di immobili a fini ricettivi per non piu' di novanta giorni l'anno, e l'articolo 27 comma 3 qualifica come attivita' ricettiva la gestione non occasionale e organizzata.

Tre correzioni al modello, tutte da fonte. Il costo figurativo del tempo dedicato alla gestione, che nella diretta con Fineco viene indicato come voce da calcolare e non solo da citare, entra nel conto economico con un moltiplicatore dedicato per la locazione breve, che non e' un investimento passivo; resta a zero per impostazione predefinita, quindi il modello e' retrocompatibile. Il controllo di concentrazione del patrimonio, con la soglia di un terzo e l'avvertenza che l'immobiliare non decorrela dall'azionario nelle recessioni. E la forma del premio della polizza incendio, che il canale Telegram ha mostrato esistere anche come premio unico anticipato per l'intera durata, spesso finanziato dentro il mutuo: il modello ora lo tratta come onere iniziale e lo ripartisce sulla durata per il confronto.

Quotazioni OMI. Verificato che il servizio di consultazione a video non espone una API documentata ne' un `robots.txt`, e la fornitura ufficiale richiede un'autenticazione personale: l'automazione non e' quindi una strada percorribile e ci si astiene, coerentemente con ADR-004. Aggiunti invece `omi importa`, che ingerisce la fornitura scaricata a mano accettando lo zip o i CSV, e `omi zone`, che elenca le zone omogenee di un Comune.

Resta aperta la legge 448/1998: Normattiva rende gli articoli via JavaScript e la pagina statica non li contiene, mentre il corpus locale non restituisce l'atto al suo URN.

Verifica: trentanove test verdi, workbook a quindici fogli riaperto con Excel senza celle in errore, scansione dei dati personali pulita.

## 2026-08-28, chiusura delle fonti arretrate, simulatore del mutuo e guide d'uso

File toccati: `src/immobiliare/excel_builder.py` (foglio Simulatore mutuo, sei voci di checklist, fonte Banca d'Italia), `src/immobiliare/parametri.py`, `tests/test_workbook.py`, `docs/guida-non-tecnica.md` e `docs/guida-tecnica.md` nuovi, `CLAUDE.md`, `README.md`, `_notes/INDICE-MATERIALE.md`.

Materiale locale rimasto indietro, ora letto. Quattordici schermate di thread di r/ItaliaPersonalFinance, che erano l'unica copia di discussioni non piu' raggiungibili dal web perche' il dominio non e' prelevabile; le sottocartelle tematiche si sono rivelate duplicati esatti, verificato per impronta. La guida ufficiale della Banca d'Italia sul mutuo ipotecario, trentasei pagine, da cui sono uscite sei voci di checklist su diritti che quasi nessuno esercita: consegna del PIES, sette giorni di riflessione sull'offerta vincolante, gratuita' di legge della portabilita', verifica della soglia d'usura, liberta' di scelta della polizza, accesso gratuito alla Centrale dei Rischi. Il documento sul rimborso anticipato, con la correzione dell'equivoco per cui converrebbe estinguere presto perche' all'inizio si pagano soprattutto interessi. Il dossier tecnico di un immobile reale e il documento di rinuncia all'incarico di mediazione creditizia, entrambi segnalati nell'indice perche' contengono dati personali di terzi.

Il testo unico regionale del turismo delle Marche non e' stato estratto: il PDF non ha mappa Unicode e il testo esce illeggibile senza riconoscimento ottico. Il quadro sul confine fra locazione turistica non imprenditoriale e attivita' ricettiva e' stato ricostruito dalle fonti in rete.

Coletti, completato. Analizzati anche i fogli che mancavano del calcolatore mutuo, in particolare il Simulatore, che ricalcola la rata mese per mese sul debito residuo e ammette versamenti volontari. Restano fuori `leva.xlsx` e `leva.ipynb`, che riguardano la leva su attivi volatili e non l'immobiliare, e i quattro video segnalati dall'utente, per i quali non esiste trascrizione recuperabile.

Corpus normativo, usato e non solo verificato. Estratti da `E:\legal-consultant` quindici articoli con testo e URN, che sono ora le citazioni della guida tecnica. Due conferme dal testo primario valgono piu' di qualunque sintesi: l'art. 4 del DL 50/2017 prevede il 26 per cento ridotto al 21 per una sola unita' individuata in dichiarazione, e non contempla alcuna aliquota del 30 per cento; l'art. 18 del DPR 601/1973 conferma lo 0,25 per cento sul mutuo prima casa e il 2 per cento negli altri casi.

Nuovo foglio Simulatore mutuo, quindicesimo del workbook. Ricorsione mese per mese con versamenti volontari ricorrenti e una tantum, percorso del tasso con variazione a partire da un mese scelto, e le due modalita' di imputazione del rimborso, riduzione della durata oppure della rata, che vanno dichiarate alla banca e producono risultati molto diversi: sullo stesso versamento di cento euro al mese il risparmio e' di 11.373 euro riducendo la durata contro 6.543 riducendo la rata. Espone anche la scelta della convenzione di conversione del tasso mensile, divisione per dodici come nei contratti italiani oppure tasso equivalente composto. Si autovalida: a versamenti nulli e tasso invariato riproduce esattamente il piano base, con tasso interno pari al nominale.

Scritte le due guide d'uso richieste, una per l'utente non tecnico che accompagna foglio per foglio in linguaggio comune, e una tecnica con architettura, catena di calcolo e riferimento di ogni voce con formula, nome definito e norma.

Verifica: trentanove test verdi, workbook a quindici fogli riaperto con Excel senza celle in errore, scansione dei dati personali sui file tracciati pulita.

## 2026-08-28, riordino della cartella, colonne del registro e confronto fra immobili

File toccati: `.gitignore`, il riordino di `_notes/`, `_notes/INDICE-MATERIALE.md` e `_notes/RESUME-PROMPT.md` nuovi e ignorati, `src/immobiliare/annunci.py`, `src/immobiliare/excel_builder.py`, `tools/valuta.py`, `tests/test_workbook.py` nuovo, `.claude/context/deployment.md` nuovo, `LICENSE`, `CLAUDE.local.md` e `.claude/settings.local.json` nuovi e ignorati, `CLAUDE.md`, `README.md`, `docs/raccolta-annunci.md`, `.claude/context/dev-testing.md`, `.claude/context/current-work.md`.

Riordino della cartella. In radice il codice stava mischiato a quattordici elementi personali. Tutto il materiale e' stato spostato sotto `_notes/`, in tre rami con criteri distinti: `dossier/` per il materiale personale, `riferimenti/` per quello di terzi, `segnalibri/` per i collegamenti senza file associato. Settantuno file spostati, nessuno perso, nessuno rinominato. La scelta di non rinominare non e' pigrizia: quattro file hanno dimensione zero e portano l'informazione nel nome, fra cui il numero del centralino di una palazzina, e un rinomino l'avrebbe cancellata. Il loro contenuto e' trascritto in `_notes/INDICE-MATERIALE.md`, che mappa l'intera struttura. Il `.gitignore` si e' di conseguenza semplificato, perche' una sola riga per `_notes/` sostituisce le dieci regole per nome che c'erano prima.

Colonne del registro. Il confronto con il foglio di lavoro precedente dell'utente ha mostrato cinque campi persi nel passaggio: agenzia, contatto, provincia, data di consegna e destinazione d'uso. Sono stati rimessi, portando il registro a ventotto campi e il foglio Annunci a trentuno colonne. Sull'agenzia e sul contatto va detto perche' non contraddicono ADR-004: quella decisione vieta di raccogliere recapiti con il prelievo automatico, non di annotare a mano il riferimento con cui si sta trattando, e la differenza fra un'agenda e una banca dati e' esattamente questa.

Foglio Confronto immobili. Applica il modello completo a ogni riga del registro, dalle imposte di trasferimento al cash flow, e restituisce gli annunci in fila con rendimento netto, cap rate, cash on cash e debt service coverage ratio affiancati, con l'esito rispetto alla soglia di rendimento del foglio Scenari. Le colonne intermedie sono deliberate: ogni formula legge la precedente invece di ricalcolare da capo, il che rende ogni cella ispezionabile quando un numero sorprende. Il regime di acquisto e' quello del foglio Immobile e vale per tutti, limite dichiarato nel foglio e fra le domande aperte.

Test sul generatore. Nuovo file `tests/test_workbook.py`, sei test sulla struttura: elenco dei fogli, presenza dei nomi definiti essenziali, corrispondenza posizionale fra le colonne del foglio Annunci e l'ordine di esportazione, riga di aggancio del foglio di confronto, estensione del piano di ammortamento. Il test sull'esportazione ha trovato subito un difetto reale: `openpyxl` salta l'assegnazione quando si passa `value=None` a `cell()`, quindi un campo azzerato non ripuliva la cella e l'annuncio esportato ereditava in silenzio il dato di quello che occupava prima quella riga. Corretto assegnando sull'attributo invece che tramite il parametro.

Verifica: trentanove test verdi in due file, workbook rigenerato e riaperto con Excel senza celle in errore, foglio di confronto che ordina correttamente i tre annunci a registro.

## 2026-08-28, costruzione iniziale del progetto

Adozione del sistema di progetto del template nella forma minima: `CLAUDE.md` come indice, regole modulari sotto `.claude/rules/` limitate alle cinque pertinenti, memoria e schede di contesto versionate, nessun pacchetto opzionale. La regola sugli screenshot manuali e' stata esclusa perche' non pertinente a un progetto senza interfaccia.

Ricerca fiscale e normativa aggiornata al 28 agosto 2026. Verificate sulle fonti le imposte di trasferimento, la regola prezzo-valore, i termini dell'agevolazione prima casa incluso il passaggio da uno a due anni per la rivendita della precedente, l'imposta sostitutiva sui mutui, la detrazione degli interessi passivi, gli scaglioni IRPEF con la seconda aliquota ridotta al trentatre' per cento, l'IMU, i regimi di tassazione dei canoni e la plusvalenza.

Risolta una contraddizione fra le fonti sulle locazioni brevi 2026. Diverse ricostruzioni riportavano aliquote progressive con un trenta per cento sulla terza e quarta unita', incompatibile con la contestuale riduzione della soglia a due unita'. La verifica incrociata su piu' fonti, inclusa la guida dell'Agenzia delle Entrate aggiornata ad aprile 2026, ha confermato che le aliquote restano ventuno per cento sulla prima unita' e ventisei sulle altre, e che cio' che e' cambiato e' solo la soglia, da quattro a due unita'.

Scritti `src/immobiliare/parametri.py` con i parametri e le fonti, `calcoli.py` con le funzioni di dominio, `stile.py` con gli stili del workbook, `excel_builder.py` con il generatore a tredici fogli, `annunci.py` con il registro e l'acquisizione, `omi.py` con le quotazioni dell'Osservatorio, `llm_locale.py` con il cliente Ollama.

Scaricati come riferimento, sotto `_notes/riferimenti/coletti/` non versionato, i fogli di calcolo immobiliari di Paolo Coletti. Registrate le date di ultima modifica dichiarate dal server, perche' determinano quali parti siano ancora utilizzabili: i due fogli immobiliari sono del 17 febbraio 2022, quello su mutuo e investimento del 29 settembre 2025. Da essi proviene l'impostazione dell'orizzonte lungo, dello sfitto fra un contratto e l'altro, della ristrutturazione periodica e del confronto con il portafoglio alternativo.

Verifica del workbook con Excel. Il primo file generato non si apriva: la bisezione sui fogli ha isolato la causa in un elemento `dataValidations` vuoto sul foglio Mutuo, prodotto da una validazione dichiarata e mai associata ad alcuna cella. Rimossa la dichiarazione inutile, il file si apre e ricalcola senza errori.

Corretti due difetti sostanziali emersi dal ricalcolo. La differenza fra i due patrimoni nel foglio di confronto puntava alla riga del capitale versato invece che a quella del patrimonio comprando. L'accantonamento per la ristrutturazione compariva sia nel foglio del flusso di cassa sia, indirettamente, nei costi operativi: spostato una sola volta dentro il conto economico della locazione e rimossa la colonna che lo duplicava.

Reso parametrico il tasso marginale IRPEF usato nel confronto con il regime ordinario, che era cablato sulla seconda aliquota.

Scritte le schede di dominio sotto `docs/` e il registro completo delle fonti, con distinzione esplicita fra fonti lette direttamente e fonti solo segnalate.
