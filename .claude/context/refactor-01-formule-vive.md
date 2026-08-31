# 01. Formule vive invece di valori calcolati

> Deep-dive della voce 1 di `studio-didattico-master.md`. Riguarda `src/immobiliare/excel_builder.py` e il rapporto fra questo e `src/immobiliare/calcoli.py`.

## La forma ingenua

Un generatore di fogli di calcolo scritto senza pensarci fa questo. Calcola in Python e scrive il numero.

```python
costo = calcoli.costo_operazione(immobile, acquirente, finanziamento)
ws["B33"] = costo.imposte.totale
ws["B40"] = costo.costo_totale
ws["B42"] = costo.esborso_iniziale
```

È corretto, si testa banalmente, e produce un file che si apre ovunque. Il difetto non sta in nessuna di queste righe: sta in cosa il file *è*. Con i valori scritti, il foglio è la fotografia di una singola combinazione di input. Per sapere cosa succede alzando il prezzo di cinquemila euro bisogna tornare al terminale, ricordare i quindici parametri della riga di comando, rigenerare, riaprire.

Nella pratica questo significa che le ipotesi non si provano. Chi valuta un acquisto ne prova una, quella che aveva in testa quando ha lanciato il comando, e il foglio gliela conferma. Uno strumento di valutazione che rende costoso il *cosa succede se* non sta valutando.

## La forma adottata

Il generatore scrive formule, e i riferimenti fra fogli passano per nomi definiti registrati in un dizionario dal costruttore.

```python
def nome(self, chiave: str, ws, cella: str) -> str:
    """Registra un nome definito che punta a una cella e lo restituisce."""
    riferimento = f"'{ws.title}'!${cella[0]}${cella[1:]}" if cella[1:].isdigit() else f"'{ws.title}'!{cella}"
    self.wb.defined_names.add(DefinedName(chiave, attr_text=riferimento))
    self.nomi[chiave] = chiave
    return chiave
```

La cella delle imposte diventa allora questa, e si legge come si legge la norma.

```python
riga_reg = r
r = S.campo(
    ws, r, "Imposta di registro",
    '=IF(da_impresa="SI",fisso_impresa,'
    'MAX(base_registro*IF(agevolata="SI",reg_prima,reg_ord),reg_min))',
    S.EURO,
)
self.nome("imp_registro", ws, f"B{riga_reg}")
```

Non c'è un solo indirizzo di cella nel testo della formula. `da_impresa`, `agevolata`, `reg_prima`, `reg_min` sono nomi che puntano a celle in tre fogli diversi, e la formula resta valida se una riga si sposta perché una sezione cresce.

## Perché i nomi definiti e non gli indirizzi

Un generatore che compone formule con indirizzi calcolati produce codice come `f"=B{riga_base}*B{riga_aliquota}"`, dove `riga_base` e `riga_aliquota` sono variabili locali che vivono nel metodo che costruisce quel foglio. Nel momento in cui una formula deve riferirsi a un valore di un altro foglio, quelle variabili non sono in scope, e la soluzione istintiva è passarle in giro o memorizzarle in attributi. Si costruisce così un grafo di dipendenze fra metodi che replica, malamente, il grafo di dipendenze che il foglio di calcolo già sa gestire da solo.

I nomi definiti sono di livello workbook, quindi la registrazione e l'uso possono stare in metodi diversi e in qualsiasi ordine. L'unico vincolo residuo è di leggibilità: si costruiscono prima i parametri, poi gli input, poi il calcolo, poi la sintesi.

## Il costo, dichiarato

Le formule non vengono valutate alla scrittura. La libreria le tratta come stringhe che iniziano con un uguale, e non ha modo di sapere se `reg_prima` esiste, se le parentesi bilanciano, se `PMT` ha il numero giusto di argomenti. Il generatore può quindi terminare senza errori e produrre un file rotto.

Questo costo è la ragione per cui esiste `tools/verifica-excel.ps1` e la voce 3 del racconto. Va tenuto presente come proprietà strutturale della scelta, non come incidente: chi aggiunge un foglio deve sapere che il suo test non è `python tools/valuta.py excel` ma l'apertura con Excel.

## Il motore Python non è ridondante

Se il calcolo vive nelle formule, `calcoli.py` sembra inutile. Non lo è, per due ragioni distinte.

La prima è che le funzioni pure si testano, e le formule no. `test_calcoli.py` congela il caso di riferimento e le regole che cambiano ogni anno, e lo fa in un linguaggio dove un errore è un'eccezione e non una cella verde con dentro un numero sbagliato.

La seconda è che le due implementazioni si controllano a vicenda. Lo stesso caso passa per `python tools/valuta.py riepilogo` e per il workbook, e i risultati devono coincidere. È il controllo che intercetta l'errore di trascrizione, che in un foglio di calcolo è il più frequente e il meno visibile. Va però conosciuto il suo limite, che la voce 4 del racconto documenta: protegge dalla trascrizione sbagliata, non da un ragionamento sbagliato replicato fedelmente in entrambe.

## Come estendere il pattern

Un foglio nuovo si aggiunge scrivendo un metodo `foglio_*` nella classe `Costruttore` e registrandolo in `costruisci()`. Ogni valore che altri fogli dovranno leggere riceve un nome con `self.nome(...)` o, se è un intervallo, con `self.nome_intervallo(...)`. Ogni valore derivato è una formula, mai un numero calcolato in Python: se ci si trova a scrivere `ws.cell(...).value = qualcosa_di_calcolato`, la domanda da farsi è perché quel calcolo non può stare nella cella.

L'eccezione legittima è il foglio `_Estrazioni`, dove i numeri casuali *devono* essere costanti perché la simulazione sia riproducibile. È l'unico posto del progetto dove Python scrive valori invece che formule, ed è documentato nel proprio deep-dive.
