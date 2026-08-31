# 03. Verificare il workbook aprendolo con Excel

> Deep-dive della voce 3 di `studio-didattico-master.md`. Riguarda `tools/verifica-excel.ps1` e la tecnica di bisezione sui fogli.

## Che cosa non verifica il generatore

La libreria che scrive il file tratta una formula come una stringa che comincia con un uguale. Non sa se il nome che compare dentro esiste, se le parentesi bilanciano, se la funzione ha il numero giusto di argomenti. Questo codice è perfettamente legale e produce un file che si salva senza un avviso.

```python
ws.cell(row=r, column=2, value="=IF(agevolta=\"SI\",reg_prima,reg_ord)")
```

Il refuso in `agevolta` diventa un `#NOME?` visibile solo a chi apre il file. Il generatore termina con successo, i test Python passano perché non toccano il workbook, e l'errore arriva all'utente.

Il caso reale che ha reso il problema evidente è stato peggiore, perché non produceva nemmeno un errore visibile. Due righe come queste, con la validazione dichiarata e mai associata ad alcuna cella:

```python
si_no = DataValidation(type="list", formula1='"SI,NO"', allow_blank=False)
ws.add_data_validation(si_no)
```

producono nel file questo elemento:

```xml
<dataValidations count="0"/>
```

che Excel rifiuta, aprendo il file con un messaggio di contenuto illeggibile oppure non aprendolo affatto. Nessuna parte della catena Python se ne accorge.

## Il verificatore

Lo script apre il workbook, forza un ricalcolo completo, e chiede a Excel stesso quali celle valutano a errore.

```powershell
$wb = Invoca $excel.Workbooks "Open" @($pieno)
$excel.CalculateFullRebuild()

foreach ($ws in $wb.Worksheets) {
    $ur = $ws.UsedRange
    if ($null -eq $ur) { continue }
    $blocco = $null
    # xlCellTypeFormulas = -4123, xlErrors = 16. Solleva eccezione se non trova
    # nulla, che e' il caso buono.
    try { $blocco = $ur.SpecialCells(-4123, 16) } catch { $blocco = $null }
    if ($null -ne $blocco) {
        foreach ($cella in $blocco) {
            Write-Output ("  {0}!{1} = {2}" -f $ws.Name, $cella.Address(0, 0), $cella.Text)
            Write-Output ("      formula: {0}" -f $cella.Formula)
            $errori++
        }
    }
}
```

`SpecialCells` con quei due argomenti restituisce in un colpo solo tutte le celle di formula in errore del foglio, senza scorrere l'intervallo cella per cella: su fogli da migliaia di celle la differenza fra le due strade è fra un secondo e diversi minuti. Che sollevi un'eccezione quando non trova nulla è un comportamento noto della libreria di automazione e va gestito come caso normale, non come errore.

Lo script stampa poi i valori chiave e termina con codice diverso da zero se ha trovato qualcosa, quindi è utilizzabile come cancello prima di un commit.

## Due trappole dell'ambiente

L'automazione di Excel espone i metodi nella lingua di installazione. Su una console italiana la chiamata diretta fallisce con un messaggio che sembra dire che il metodo non esiste, e che è lo stesso messaggio che si ottiene quando il metodo esiste ma il file è malformato: due cause diverse, un errore solo, ore perse. La chiamata va fatta passando esplicitamente la cultura.

```powershell
$ci = [System.Globalization.CultureInfo]::GetCultureInfo("en-US")

function Invoca($oggetto, $metodo, $argomenti) {
    return $oggetto.GetType().InvokeMember($metodo, "InvokeMethod", $null, $oggetto, $argomenti, $ci)
}
```

Lo stesso vale per assegnare un valore a una cella, che va fatto con `InvokeMember` su `SetProperty` e non con l'assegnazione diretta.

La seconda trappola è che Excel resta in memoria se il processo non viene chiuso, e il file resta bloccato: la rigenerazione successiva fallisce con un errore di permesso che sembra un problema di filesystem e non lo è.

## La bisezione, quando il file non si apre affatto

Se Excel rifiuta il workbook, `SpecialCells` non serve a niente perché non c'è nulla da ispezionare. La tecnica è generare workbook progressivi, uno per ogni foglio in più, e provare ad aprirli tutti.

```python
fogli = ["foglio_guida", "foglio_cruscotto", "foglio_parametri", ...]
for i, f in enumerate(fogli, 1):
    c = E.Costruttore()
    for g in fogli[:i]:
        getattr(c, g)()
    c.salva(f"output/_b{i:02d}.xlsx")
```

Il primo file della serie che non si apre identifica il foglio responsabile, e da lì si procede commentando sezioni. È così che è stato trovato l'elemento di validazione vuoto: i primi tre workbook si aprivano, il quarto no, e il quarto era il primo a contenere il foglio Mutuo.

## Il terzo livello: la doppia implementazione

Il verificatore intercetta gli errori che Excel riconosce come errori. Non intercetta una formula che punta alla riga sbagliata e calcola un numero plausibile. Per quello serve un secondo calcolo indipendente, ed è la ragione per cui il motore Python esiste anche se il modello vive nelle formule.

È così che è stato trovato l'errore nel foglio di confronto, dove la differenza fra i due patrimoni sottraeva la riga del capitale versato invece di quella del patrimonio comprando: la cella era verde, il numero era un numero, e solo il confronto con il calcolo Python ha mostrato che valeva meno centotrentanovemila invece di meno ventiduemila.

## Come estendere il pattern

Dopo ogni modifica a `excel_builder.py` si rigenera e si esegue il verificatore, senza eccezioni. Quando si aggiunge un foglio che introduce una struttura nuova, come una validazione o una formattazione condizionale, conviene generarlo isolato e aprirlo prima di integrarlo.

Un foglio che espone grandezze di sintesi merita anche una riga nella sezione dei valori chiave dello script, così che una regressione numerica si veda nell'output del verificatore e non solo aprendo il file.
