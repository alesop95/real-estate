# Work-log

> Append-only, in ordine cronologico inverso. Ogni voce riporta data, file toccati, motivo.

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
