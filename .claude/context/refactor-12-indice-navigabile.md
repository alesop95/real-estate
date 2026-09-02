# 12. L'indice navigabile, e i due errori che si fanno una volta

> Deep-dive della voce 12 di `studio-didattico-master.md`. Riguarda `FOGLIO_INDICE`, `collegamento` e `titolo` in `src/immobiliare/stile.py`, la tupla `Costruttore.PERCORSO` e il metodo `foglio_guida` di `excel_builder.py`, `STATI_ANNUNCIO` in `annunci.py`, e i test `test_indice_copre_tutti_i_fogli_e_i_collegamenti_esistono` e `test_ogni_foglio_visibile_torna_all_indice`.

## Il difetto, che nessun test avrebbe trovato

Tutte le altre voci di questo racconto partono da un numero sbagliato o da una forma di codice che può produrne uno. Questa parte da una frase d'uso: i fogli sono tanti, sono probabilmente tutti necessari, ma si perde il flusso.

È un difetto reale e non ha un test possibile, perché la proprietà violata non è la correttezza di un valore ma la percorribilità dello strumento. Il progetto aveva già un principio che lo copriva, scritto nel principio di selezione della roadmap: lo strumento vale finché resta leggibile, e un modello che nessuno riesce più a verificare produce numeri che nessuno dovrebbe usare. Venti fogli navigabili solo dalle linguette in basso violano quel principio, e nessuno se ne accorge finché non lo apre qualcuno che non lo ha costruito.

Il foglio di presentazione esisteva, era il primo e si apriva per primo. Portava questo.

```python
r = S.sezione(ws, r, "Come si usa")
passi = [
    ("1. Immobile", "Prezzo, rendita catastale, tipo di venditore e agevolazione..."),
    ("2. Mutuo", "Importo, tasso e durata..."),
    ...
    ("11. Annunci", "Registro degli immobili in valutazione..."),
]
```

Undici voci su venti fogli, nessuna cliccabile, e la numerazione non corrispondeva né all'ordine delle linguette né a un percorso dichiarato. Le nove voci mancanti non erano una dimenticanza singola: erano il segnale che quell'elenco veniva aggiornato a mano e quindi non lo era.

## Che cosa deve dire un indice

Le linguette in basso già elencano i fogli. Un indice che si limita a rielencarli non aggiunge niente. Le tre informazioni che le linguette non danno, e che sono quelle che servono davvero, sono se in quel foglio si scrive o si legge, quando lo si apre nel percorso, e se riguarda il proprio caso.

La terza è la meno ovvia e la più utile. Fogli come Asta e Comproprietà servono solo in situazioni particolari, e chi apre il file senza saperlo non sa se stia dimenticando di compilarli: un foglio pieno di celle gialle che restano vuote è indistinguibile, a vista, da un foglio che si è dimenticato.

```python
PERCORSO = (
    ("Da dove si comincia", (
        ("Cruscotto", "Si legge", "Sempre, per primo e per ultimo",
         "I numeri che decidono, con accanto la soglia oltre la quale sono un problema, e il conto di cosa manca ancora"),
    )),
    ("I dati dell'operazione, cioe' le celle gialle", (
        ("Immobile", "Si compila", "Quando c'e' un immobile candidato",
         "Imposte di trasferimento, costo totale dell'operazione, cassa necessaria al rogito"),
        ...
        ("Comproprieta", "Si compila", "Solo se si compra in piu' di uno",
         "Ripartizione per quote di esborso, rata e imposte, e l'avvertenza su cosa serve mettere per iscritto"),
    )),
    ...
)
```

L'ordine è quello di lettura consigliata e non quello delle linguette. I due coincidono quasi sempre, e la divergenza è deliberata: Parametri e Fonti stanno fra le prime linguette perché ci si arriva per consultazione, e in fondo al percorso perché non è da lì che si comincia.

## La sorgente unica, e il test nelle due direzioni

La tupla è ciò da cui il foglio si costruisce, ed è anche ciò che il test confronta con la realtà.

```python
    visibili = {ws.title for ws in wb.worksheets if ws.sheet_state == "visible"}
    dichiarati = [nome for _, fogli in E.Costruttore.PERCORSO for nome, *_ in fogli]
    attesi = visibili - {indice}
    assert set(dichiarati) == attesi, (
        f"indice e workbook divergono. Nell'indice e non nel workbook: "
        f"{sorted(set(dichiarati) - attesi)}. Nel workbook e non nell'indice: "
        f"{sorted(attesi - set(dichiarati))}"
    )
```

Il confronto è nelle due direzioni, e servono entrambe. Un foglio nell'indice e non nel workbook è un collegamento rotto; un foglio nel workbook e non nell'indice è un foglio che nessuno troverà, che è esattamente il difetto da cui si è partiti. Il messaggio dell'asserzione dice quale delle due cose è successa, perché la correzione è diversa.

Il test non si ferma alla tupla: rilegge le celle del foglio generato, perché fra la tupla e le celle sta il codice che le scrive, e anche quello può sbagliare.

```python
    for nome, link in collegati.items():
        assert link.location == f"'{nome}'!A1"
        assert not link.target
```

## Primo errore: la posizione del ritorno

La prima versione metteva il ritorno all'indice accanto al titolo, nella colonna successiva a quelle che il titolo occupa.

```python
    ws.merge_cells(start_row=riga, start_column=1, end_row=riga, end_column=larghezza)
    if ws.title != FOGLIO_INDICE:
        ritorno = ws.cell(row=riga, column=larghezza + 1, value="<< Indice")
```

Sembra corretto, e sui primi fogli lo è. Il problema si vede solo rileggendo il file generato: `larghezza` è un parametro che ogni foglio passa a `titolo` e vale da quattro a ventisei a seconda della larghezza del contenuto, quindi il ritorno finiva alla colonna 5 sul Cruscotto e alla 27 sul foglio Annunci, cioè fuori dalla vista. La mia stessa ispezione lo confermava per sottrazione: cercando la cella entro la ventesima colonna, su Annunci e Comproprietà non la trovava, e la prima lettura del risultato era che su quei due fogli mancasse.

```
  Comproprieta           None
  Annunci                None
```

La posizione giusta è la riga che `titolo` lasciava vuota fra il titolo e il primo contenuto, in colonna A: identica su tutti i fogli, sempre in vista, e a costo zero perché quella riga era già lì.

```python
    # Il ritorno all'indice occupa la riga che questa funzione lasciava vuota fra
    # il titolo e il primo contenuto, in colonna A. La posizione e' scelta perche'
    # sia la stessa su tutti i fogli...
    if ws.title != FOGLIO_INDICE:
        collegamento(ws, riga, 1, "<< Indice", FOGLIO_INDICE)
    return riga + 1
```

Il posto in cui scriverlo è a sua volta una scelta con una ragione: sta in `titolo`, che ogni foglio chiama come prima cosa, quindi un foglio nuovo non può nascere senza via di ritorno. Metterlo nei singoli fogli avrebbe fatto dipendere la navigabilità dalla memoria di chi aggiunge un foglio, che è la stessa forma di fragilità di `refactor-06`.

## Secondo errore: la forma del collegamento

La scorciatoia che si trova per prima è assegnare una stringa.

```python
link.hyperlink = f"#'{nome}'!A1"
```

Funziona, nel senso che Excel apre il file e il collegamento porta dove deve. Ma la lettura del file generato mostra che cosa è stato scritto davvero.

```
r7   Cruscotto  -> target="#'Cruscotto'!A1"  location=None
```

`openpyxl` ha interpretato la stringa come destinazione esterna, e nel file quel collegamento finisce fra le relazioni verso l'esterno del documento. Un collegamento interno non ha una destinazione esterna: ha una posizione dentro il file, ed è ciò che `location` esprime.

```python
def collegamento(ws, riga: int, colonna: int, testo: str, foglio: str, cella: str = "A1"):
    c = ws.cell(row=riga, column=colonna, value=testo)
    c.font = LINK
    c.alignment = SINISTRA
    c.hyperlink = Hyperlink(ref=c.coordinate, location=f"'{foglio}'!{cella}")
    return c
```

Due dettagli dentro l'helper. Il nome del foglio va fra apici singoli, perché diversi fogli di questo workbook hanno uno spazio nel nome e senza apici la destinazione non si risolve. E si punta a una cella e non al foglio nudo, perché un collegamento senza cella lascia il foglio dove era stato lasciato scrollato: su un piano di ammortamento di 480 righe significa arrivarci in fondo.

La verifica è stata fatta in Excel, non solo rileggendo il file, perché la domanda era proprio come si comporta il programma che interpreta il documento.

```
Guida                  collegamenti  19   con destinazione esterna 0
...
Fonti                  collegamenti  40   con destinazione esterna 39
totale collegamenti: 77, senza destinazione interna: 39

seguito 'Scenari' dall'indice, foglio attivo: Scenari, cella $A$1
seguito il ritorno, foglio attivo: Guida, cella $A$1
```

I trentanove con destinazione esterna sono i collegamenti alle fonti istituzionali nel foglio Fonti, che esterni devono essere: il conto torna esattamente.

## Il difetto trovato scrivendo la documentazione

Il manuale operativo doveva elencare i valori ammessi per lo stato di un annuncio, e sono stati trovati in due posti che dicevano cose diverse.

```python
# in tools/valuta.py
p.add_argument("--stato", help="da contattare, contattata, visitata, scartata, in trattativa")

# in excel_builder.py
stato = DataValidation(type="list", formula1='"da contattare,contattato,visita fissata,visitata,proposta fatta,scartato,acquistato"', allow_blank=True)
```

Tre dei cinque valori offerti dalla riga di comando non esistono nel foglio. La conseguenza è concreta e silenziosa: un valore scritto dalla riga di comando finisce nella cella senza passare per la validazione, quindi resta lì senza errore, ma il menu a tendina non lo contiene e un filtro per stato non lo trova dove chi lo ha scritto lo cerca.

```python
STATI_ANNUNCIO = (
    "da contattare", "contattato", "visita fissata", "visitata",
    "proposta fatta", "scartato", "acquistato",
)
```

L'ordine è quello dell'avanzamento della trattativa e non alfabetico, perché è l'ordine in cui il menu li presenta e in cui una trattativa li attraversa. Vale registrare come il difetto è emerso: non da un test e non da un uso, ma dal tentativo di scrivere in un documento quali fossero i valori ammessi. Documentare una cosa costringe a guardarla in un punto solo, ed è la ragione per cui la documentazione trova difetti che il codice non segnala.

## Come estendere il pattern

Per aggiungere un foglio al workbook servono due modifiche, il metodo `foglio_*` registrato in `costruisci()` e la voce nella tupla `PERCORSO` sotto la fase giusta, e il test impone la seconda invece di lasciarla alla memoria. Il ritorno all'indice non richiede nulla, perché lo scrive `titolo`.

Per un collegamento interno si usa `stile.collegamento` e non si assegna una stringa. Per un elenco di valori ammessi consumato da più di un posto si definisce una tupla accanto al dato che la usa e la si importa, perché due copie divergono e la loro divergenza non produce un errore ma un valore che c'è e non si trova.

E la lezione più generale della voce: un artefatto che è anche l'interfaccia con cui si lavora ha requisiti d'uso oltre a quelli di correttezza, e quei requisiti non li trova nessun test. Li trova chi lo apre senza averlo costruito, e vanno chiesti.
