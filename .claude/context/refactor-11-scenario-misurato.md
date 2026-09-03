# 11. Lo scenario di stress si misura, e il piano dichiara se si chiude

> Deep-dive della voce 11 di [`studio-didattico-master.md`](studio-didattico-master.md). Riguarda `risalite_storiche` ed `estremi_storici` in `src/immobiliare/tassi.py`, `RISALITE_EURIBOR` in `parametri.py`, la sezione *Percorso del tasso* e le righe di chiusura dentro `foglio_simulatore_mutuo` di `excel_builder.py`, l'opzione `--risalita` di `tools/valuta.py`, e i test `test_risalita_storica_cerca_la_finestra_e_non_gli_estremi` e `test_risalite_congelate_coerenti_con_la_documentazione`.

## Il punto in cui il modello si arrendeva all'intuizione

```python
r = S.campo(ws, r, "Variazione del tasso", 0.0, S.PERC, input_utente=True,
            nota="Punti percentuali aggiunti o tolti al tasso di partenza. Un punto in piu' su un variabile e' uno scenario ordinario, non estremo.")
r = S.campo(ws, r, "Mese in cui la variazione entra in vigore", 25, S.NUMERO, input_utente=True,
            nota="Prima di questo mese vale il tasso di partenza.")
```

Un gradino singolo, e il valore lasciato a chi compila con un suggerimento che orientava verso un punto percentuale. Tutto il resto del workbook àncora i propri numeri a una fonte citata e datata; qui il numero più importante di un mutuo a tasso variabile era un'opinione, e l'opinione ha un bias prevedibile, perché la cifra che viene in mente è quella che suona prudente.

La serie mensile dell'Euribor a tre mesi era già scaricabile dal modulo dei tassi, e diceva un'altra cosa.

```
12 mesi: +3.78 punti, da 2022-06 (-0.24%) a 2023-06 (3.54%)
24 mesi: +4.54 punti, da 2021-11 (-0.57%) a 2023-11 (3.97%)
36 mesi: +4.49 punti, da 2020-11 (-0.52%) a 2023-11 (3.97%)
```

Chi aveva simulato un punto aveva simulato un quinto dello scenario che si è verificato, e la rata che aveva dichiarato sostenibile non era quella che ha pagato.

## La misura, e perché non è massimo meno minimo

```python
def risalite_storiche(chiave="euribor_3m", finestre=(12, 24, 36), osservazioni=400):
    dati = serie(chiave, osservazioni)
    esito = []
    for mesi in finestre:
        if len(dati) <= mesi:
            continue
        indice = max(range(len(dati) - mesi), key=lambda i: dati[i + mesi][1] - dati[i][1])
        inizio, fine = dati[indice], dati[indice + mesi]
        esito.append(Risalita(mesi=mesi, variazione=fine[1] - inizio[1], ...))
    return esito
```

Una scansione su tutte le posizioni di partenza, per ogni finestra. L'alternativa che viene per prima in mente è più corta da scrivere e dà un numero doppio: il massimo della serie è il 7,58 per cento del marzo 1995, il minimo il meno 0,58 del dicembre 2021, e la loro differenza sono più di otto punti. Non descrive nessuno scenario, perché i due estremi distano ventisei anni e nessun piano di ammortamento li attraversa nella stessa finestra. La finestra di dodici, ventiquattro o trentasei mesi è invece esattamente ciò che un mutuo attraversa.

È una distinzione che vale oltre questo caso. Una misura di stress deve essere commensurabile con l'orizzonte della decisione: un'escursione misurata su un periodo che nessuno vive è un numero grande e inutile, e la sua grandezza lo rende anche persuasivo, che è la parte pericolosa.

## Congelare nel codice, con la data, e un comando per riverificare

Il generatore del workbook non fa rete, per scelta: dipendere da un endpoint per produrre un file sarebbe fragile e renderebbe la generazione non riproducibile. I valori misurati vivono quindi in `parametri.py`, insieme a tutti gli altri numeri datati del progetto.

```python
@dataclass(frozen=True)
class RisaliteEuribor:
    indice: str = "Euribor 3 mesi"
    serie: str = "FM/M.U2.EUR.RT.MM.EURIBOR3MD_.HSTA"
    verificato_il: date = date(2026, 9, 1)
    copertura: str = "1994-01 / 2026-08, 392 osservazioni mensili"
    livello_corrente: float = 2.51
    massimo_storico: float = 7.58
    ...
    risalita_12_mesi: float = 3.78
    finestra_12_mesi: str = "2022-06 / 2023-06, da -0,24 a 3,54"
```

E il comando che li riverifica confronta la stessa misura calcolata due volte, non due misure diverse.

```
  Confronto con i valori congelati in parametri.py, verificati il 01/09/2026
    12 mesi: nel codice  3.78p, nei dati  3.78p   invariato
    24 mesi: nel codice  4.54p, nei dati  4.54p   invariato
    36 mesi: nel codice  4.49p, nei dati  4.49p   invariato

  Nessuna finestra peggiore di quelle gia' registrate: il workbook e' allineato.
```

Quando una finestra peggiore comparirà, il comando dirà di aggiornare la costante, spostare `verificato_il` e rigenerare il workbook, perché le note del foglio citano quei numeri.

## Il percorso a gradini, e perché la catena di IF è generata

Una risalita reale non è un salto istantaneo, e descriverla come tale sovrastima l'impatto sui primi mesi e sottostima la durata dell'esposizione. Il percorso diventa una tabella di sei gradini, ciascuno con il mese da cui vale e la variazione cumulata.

```python
gradino = "0"
for riga_g in range(prima_perc, ultima_perc + 1):
    gradino = f'IF(AND($B${riga_g}<>"",$A{r}>=$B${riga_g}),$C${riga_g},{gradino})'
ws.cell(row=r, column=3, value=f"=sim_tasso+{gradino}").number_format = S.PERC
```

La catena si costruisce dal primo gradino verso l'ultimo avvolgendo ogni volta la precedente, quindi il test più esterno è quello del gradino più avanzato: vale l'ultimo gradino raggiunto. Il test include `$B<>""`, perché una riga lasciata vuota non deve partecipare.

La scelta di generare la catena invece di usare `CERCA` è deliberata. `CERCA` pretende una colonna ordinata in modo crescente e, sulle righe vuote in coda, si comporta in un modo che nessuno riesce a prevedere leggendo la formula; e una formula il cui comportamento nei casi limite non si legge è, in un file che un utente modificherà, un difetto in attesa. La catena è più lunga e completamente determinata.

Il primo gradino conserva i due nomi definiti che esistevano quando il percorso era un gradino solo.

```python
if indice == 1:
    self.nome("sim_shock_mese", ws, f"B{r}")
    self.nome("sim_shock", ws, f"C{r}")
```

Il gradino singolo non è stato sostituito: è diventato la prima riga del percorso. Un file compilato come prima si comporta come prima, ed è lo stesso principio del terzo stato in `refactor-09`.

## Il difetto trovato usando ciò che si era appena costruito

Prima prova reale: il rialzo del 2022-2023 in tre gradini, un terzo, due terzi e l'intero.

```
B) rialzo 2022-2023 in tre gradini, effetto riduci durata
  Rata massima raggiunta              436,21 EUR
  Interessi totali pagati             206.464 EUR
  Durata effettiva in mesi            480
```

Tre numeri veri, e almeno due che rispondono a una domanda diversa da quella posta. 480 è `MAX_RATE`, cioè il fondo della tabella, non la durata del piano: sotto la modalità di rimborso che tiene ferma la rata e accorcia il piano, un rialzo del tasso produce l'effetto opposto e allunga il piano, e con una risalita di quasi quattro punti il piano non si chiude entro i quarant'anni modellati. Gli interessi totali sono la somma di ciò che sta in tabella, quindi sottostimano il costo del debito. La durata effettiva, calcolata come `COUNTIF(sim_pagato,">0")`, restituisce 480 perché tutte le righe hanno un pagamento, non perché il piano finisca lì.

```python
riga_res = r
r = S.campo(ws, r, "Debito residuo alla fine del piano", "=MIN(sim_debito)", S.EURO,
            nota=f"Deve essere zero. La tabella modella {MAX_RATE} mesi, cioe' quarant'anni di rate.")
r = S.campo(ws, r, "Il piano si chiude",
            f'=IF(B{riga_res}>0.005,"NO: il debito non si estingue entro i {MAX_RATE} mesi modellati, quindi durata effettiva e interessi totali sono troncati e non risolti","SI")',
            risultato=True, nota="...")
ws.conditional_formatting.add(f"B{r-1}:B{r-1}", CellIsRule(operator="notEqual", formula=['"SI"'], fill=S.FILL_ATTENZIONE))
```

Il nome `sim_debito` è stato aggiunto alla colonna del debito residuo perché la sezione dell'esito viene scritta prima della tabella, ed è la stessa ragione per cui `refactor-08` esiste: un nome definito permette di citare in avanti senza conoscere coordinate.

Il valore letto dopo la correzione, sullo stesso scenario, è 87.082 euro di debito non estinto. E lo stesso scenario sotto la modalità corretta per il variabile italiano, quella che tiene ferma la scadenza e alza la rata, chiude regolarmente.

```
C) stesso rialzo, effetto riduci rata, cioe' il variabile italiano
  Rata massima raggiunta              625,52 EUR
  Interessi totali pagati             94.602 EUR
  Durata effettiva in mesi            300
  Il piano si chiude                  SI
```

Da 436,21 a 625,52 euro, più quarantatré per cento: è quello il numero da confrontare con il proprio reddito, ed è il numero che il foglio non era in grado di mostrare finché il percorso era un gradino solo e la misura del gradino era un'opinione.

## Il test, sintetico e senza rete

```python
    originale = T.serie
    T.serie = lambda chiave="euribor_3m", osservazioni=400: finta
    try:
        risalite = {r.mesi: r for r in T.risalite_storiche(finestre=(6, 12))}
        estremi = T.estremi_storici()
    finally:
        T.serie = originale
```

La serie sintetica è costruita perché finestra ed escursione totale divergano: minimo all'inizio, massimo in coda, distanti fra loro più della finestra. L'asserzione centrale è `risalite[6].variazione < 6.0` con l'escursione totale pari a 6, cioè che la funzione non stia calcolando massimo meno minimo. Sostituire la funzione di download è l'unico punto di contatto con la rete, quindi il test resta deterministico.

Il secondo test verifica la coerenza interna della costante, che è tutto ciò che si può verificare senza rete: che la finestra lunga non sia inferiore alla corta, che nessuna finestra superi l'escursione totale, che il livello corrente stia fra gli estremi, e che i valori siano in punti percentuali e non in frazione. L'ultima asserzione sembra pedante e non lo è: un 3,78 riscritto come 0,0378 supererebbe ogni altro controllo e produrrebbe note del workbook che parlano di zero punti di rialzo.

## Come estendere il pattern

Per aggiungere una misura empirica a un parametro oggi lasciato all'intuizione servono quattro cose, nell'ordine: una funzione nel modulo di dominio che la calcoli dalla fonte, con la definizione della misura motivata nella docstring perché la scelta della misura è metà del risultato; una costante datata in `parametri.py` che la congeli, così che il generatore resti offline e riproducibile; un comando che ricalcoli e confronti, dicendo se il codice è ancora allineato; e le note del foglio interpolate dalla costante, così che non possano divergere da essa.

La regola generale: in un modello che àncora ogni numero a una fonte, il parametro lasciato al giudizio dell'utente è il punto in cui il modello smette di valere, e i punti così vanno cercati e chiusi uno a uno. Quando un dato esiste, il valore di default non deve essere quello che suona ragionevole, ma quello che è stato osservato.
