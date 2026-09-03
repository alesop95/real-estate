# 10. Il prezzo massimo si risolve, e si autoverifica

> Deep-dive della voce 10 di [`studio-didattico-master.md`](studio-didattico-master.md). Riguarda la sezione *Prezzo massimo sostenibile* dentro `foglio_scenari` in `src/immobiliare/excel_builder.py`, e il test `test_prezzo_massimo_e_esatto_e_si_autoverifica`.

## La formula di prima, e le due cose che teneva ferme

```python
r = S.campo(ws, r, "Costo totale sostenibile a quel rendimento", f"=utile_locazione/B{riga_obiettivo}", S.EURO)
riga_costo_sost = r - 1
r = S.campo(ws, r, "Prezzo massimo corrispondente", f"=B{riga_costo_sost}/(1+incidenza_costi)", S.EURO,
            risultato=True,
            nota="Approssimazione: assume che l'incidenza percentuale dei costi accessori resti quella dello scenario base.")
```

Due passaggi, entrambi ragionevoli a prima vista. Il costo totale che l'operazione può sostenere è l'utile diviso il rendimento obiettivo. Il prezzo che corrisponde a quel costo si ottiene togliendo i costi accessori, e la loro incidenza percentuale è già calcolata altrove come `costi_accessori/prezzo`.

La prima cosa tenuta ferma è l'utile. `utile_locazione` è l'utile netto annuo calcolato al prezzo corrente, e viene usato come se fosse indipendente dal prezzo. Non lo è: la manutenzione ordinaria è `prezzo*manut_pct` e l'accantonamento per la ristrutturazione è `prezzo*ristrutt_pct/ristrutt_anni`, quindi abbassare il prezzo alza l'utile.

La seconda è l'incidenza dei costi accessori, che non è un parametro ma un rapporto. Nel costo accessorio ci sono voci proporzionali al prezzo, cioè la provvigione con la sua IVA e, quando il prezzo-valore non si applica, l'imposta di registro; e voci che non lo sono affatto, cioè notaio, altri costi, oneri del mutuo, imposte ipotecaria e catastale, e con il prezzo-valore l'intera imposta di registro, che resta ancorata al valore catastale. Al calare del prezzo il numeratore scende meno del denominatore, quindi l'incidenza cresce. Sul caso di riferimento l'incidenza al prezzo base è il 9,63 per cento; al prezzo che la formula stessa restituiva sarebbe stata circa il 50.

Le due distorsioni vanno nella stessa direzione, e il risultato lo mostra.

```
vecchia formula:  17.112 / 1,0963  =  15.609 EUR
soluzione esatta:                     43.445 EUR
```

Un fattore prossimo a tre, nella direzione che fa sembrare impossibile qualunque trattativa. Per un numero il cui unico scopo è dire quanto offrire, è il modo peggiore di sbagliare.

## L'algebra, che è di primo grado

Il costo totale in funzione del prezzo `P` è lineare a tratti.

```
costo(P) = P*(1+k) + c

k = quota del prezzo che diventa costo aggiuntivo
    = aliquota IVA, se da impresa
    = aliquota di registro, se da privato senza prezzo-valore
    = 0, se da privato con prezzo-valore, perche' la base resta il valore catastale
    + provvigione * (1 + IVA sulla provvigione)

c = costi indipendenti dal prezzo
    = 3 imposte fisse, se da impresa
    = registro sul valore catastale + ipotecaria + catastale, se prezzo-valore
    = ipotecaria + catastale, se da privato senza prezzo-valore
    + notaio + altri costi + oneri del mutuo
```

L'utile è lineare decrescente.

```
utile(P) = utile_base - (P - prezzo) * m        con m = manut_pct + ristrutt_pct/ristrutt_anni
```

Imporre `utile(P)/costo(P) = obiettivo` dà

```
utile_base + prezzo*m - P*m = obiettivo*(1+k)*P + obiettivo*c
P = (utile_base + prezzo*m - obiettivo*c) / (obiettivo*(1+k) + m)
```

## Tre celle visibili, non tre coefficienti nascosti

```python
riga_k = r
r = S.campo(ws, r, "Quota del prezzo che diventa costo aggiuntivo",
            '=IF(da_impresa="SI",IF(agevolata="SI",iva_prima,IF(di_lusso="SI",iva_lusso,iva_ord)),'
            'IF(AND(usa_prezzo_valore="SI",rendita>0),0,IF(agevolata="SI",reg_prima,reg_ord)))'
            "+provv_pct*(1+iva_provv)", S.PERC_1,
            nota="Per ogni euro di prezzo in piu', quanti centesimi di costi accessori si aggiungono...")
riga_c = r
r = S.campo(ws, r, "Costi che non dipendono dal prezzo", ..., S.EURO, nota="...")
riga_m = r
r = S.campo(ws, r, "Costi annui che scalano col prezzo", "=manut_pct+ristrutt_pct/ristrutt_anni", S.PERC_1, nota="...")
riga_pmax = r
r = S.campo(ws, r, "Prezzo massimo corrispondente",
            f"=IFERROR((utile_locazione+prezzo*B{riga_m}-B{riga_obiettivo}*B{riga_c})/(B{riga_obiettivo}*(1+B{riga_k})+B{riga_m}),\"non calcolabile\")",
            S.EURO, risultato=True, nota="Soluzione esatta, non piu' una proporzione sull'incidenza dei costi...")
```

Le tre grandezze avrebbero potuto stare dentro la formula finale. Tenerle come celle costa tre righe di foglio e compra la possibilità di guardare i tre numeri, che sul caso di riferimento sono 3,7 per cento, 7.165 euro e 1,8 per cento: chiunque conosca il dominio riconosce la provvigione nel primo, riconosce nel secondo che il prezzo-valore è attivo perché l'imposta di registro è finita nella parte fissa, e riconosce nel terzo l'uno per cento di manutenzione più lo zero virgola ottanta di accantonamento. Un risultato di cui si possono riconoscere i pezzi è un risultato che si può contestare, ed è la differenza fra un modello e un oracolo.

Coerente con la stessa logica, la riga successiva deriva dal risultato invece di ricalcolarlo.

```python
r = S.campo(ws, r, "Scarto rispetto al prezzo trattato", f"=B{riga_pmax}-prezzo", S.EURO, nota="...")
```

Prima era `=B{riga_costo_sost}/(1+incidenza_costi)-prezzo`, cioè la stessa formula riscritta: due copie che potevano divergere e che non c'era ragione di avere.

## Il controllo di chiusura, e perché non è un test

```python
imposte_pmax = (
    f'IF(da_impresa="SI",B{riga_pmax}*IF(agevolata="SI",iva_prima,IF(di_lusso="SI",iva_lusso,iva_ord))+3*fisso_impresa,'
    f'MAX(IF(AND(usa_prezzo_valore="SI",rendita>0),valore_catastale,B{riga_pmax})*IF(agevolata="SI",reg_prima,reg_ord),reg_min)+ipo_priv+cat_priv)'
)
costo_pmax = f"B{riga_pmax}+{imposte_pmax}+B{riga_pmax}*provv_pct*(1+iva_provv)+notaio_cv+altri_costi+oneri_mutuo"
utile_pmax = f"utile_locazione-(B{riga_pmax}-prezzo)*B{riga_m}"
riga_ver = r
r = S.campo(ws, r, "Verifica: rendimento netto a quel prezzo", f"=IFERROR(({utile_pmax})/({costo_pmax}),\"non calcolabile\")", S.PERC_1, ...)
r = S.campo(ws, r, "Scarto dalla soglia, deve essere zero", f"=IFERROR(B{riga_ver}-B{riga_obiettivo},\"non calcolabile\")", "0.0000%", ...)
```

La verifica ricalcola il rendimento al prezzo trovato usando la formula esatta delle imposte, `MAX` con il minimo di legge compreso, cioè proprio la non linearità che la soluzione chiusa ha ignorato. Sul caso precaricato lo scarto è zero a quattro decimali, letto via automazione COM sul file generato.

Sul perché sta nel foglio e non in un test: la soluzione è esatta solo sul tratto in cui il costo è lineare nel prezzo, e il caso che rompe la linearità è il minimo di legge dell'imposta di registro, che diventa vincolante quando il valore catastale per l'aliquota scende sotto mille euro. Quel caso non si presenta nel caso precaricato, che un test coprirebbe: si presenta quando qualcuno cambia rendita, aliquota o obiettivo a video. La cella dello scarto è presente esattamente nel momento in cui il problema può manifestarsi, ed è il presidio giusto per un artefatto che è anche l'interfaccia con cui si lavora.

## Il test, che presidia la forma e non il valore

```python
    pmax = ws.cell(row=righe["Prezzo massimo corrispondente"], column=2).value
    assert "incidenza_costi" not in pmax
    for etichetta in ("Quota del prezzo che diventa costo aggiuntivo", "Costi che non dipendono dal prezzo",
                      "Costi annui che scalano col prezzo", "Rendimento netto obiettivo"):
        assert f"B{righe[etichetta]}" in pmax
    verifica = ws.cell(row=righe["Verifica: rendimento netto a quel prezzo"], column=2).value
    assert "reg_min" in verifica
```

Non verifica che il prezzo massimo valga 43.445, che dipende da tutti gli input del workbook e cambierebbe a ogni ritocco di un parametro fiscale. Verifica che non si sia tornati alla proporzione, che la formula legga le tre celle della soluzione chiusa, e che la verifica applichi il minimo di legge, cioè le tre proprietà che rendono il numero esatto.

## Come estendere il pattern

Quando serve invertire una relazione del modello, la domanda da porsi è se la grandezza che si sta usando come coefficiente sia un parametro oppure un rapporto fra due grandezze che dipendono entrambe dalla variabile che si muove. Nel secondo caso non è un coefficiente: va scomposta in una parte proporzionale e una parte fissa, e l'inversione diventa un'equazione di primo grado invece di una divisione.

E ogni inversione va accompagnata dal suo controllo diretto, cioè da una cella che riapplica il calcolo in avanti al risultato ottenuto e mostra la differenza. Costa due righe, è l'unico modo di sapere di essere fuori dal dominio di validità nel momento in cui ci si finisce, e vale più di un test perché vive nel file che l'utente sta usando.
