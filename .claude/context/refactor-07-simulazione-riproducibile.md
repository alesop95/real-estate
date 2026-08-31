# 07. Simulazione riproducibile e insieme interattiva

> Deep-dive della voce 7 di `studio-didattico-master.md`. Riguarda i metodi `foglio_estrazioni` e `foglio_rischio` di `src/immobiliare/excel_builder.py`, e le costanti `ESTRAZIONI` e `SEME_SIMULAZIONE`.

## Il problema, che è un conflitto fra due requisiti

Passare da tre scenari scelti a mano a una distribuzione di esiti richiede molte estrazioni casuali. In un foglio di calcolo senza macro ci sono due strade, e prese singolarmente nessuna delle due funziona.

La prima è la funzione casuale nativa. È *volatile*, cioè si ricalcola a ogni modifica di qualunque cella del workbook. La conseguenza pratica è che i mille scenari cambiano tutti ogni volta che si tocca qualcosa: il quinto percentile visto un istante prima non è più lo stesso, due letture consecutive dello stesso file danno numeri diversi, e nulla è verificabile. Per uno strumento che deve reggere una decisione da centomila euro è squalificante.

La seconda è pre-calcolare tutto in Python e scrivere i risultati come valori. È stabile e riproducibile, ma perde la proprietà su cui è costruito l'intero progetto, cioè che il workbook sia il modello e non il suo rapporto: cambiando il prezzo, la simulazione resterebbe ferma a mentire sui valori vecchi.

## La separazione

Le due cose che sembravano in conflitto sono in realtà due strati diversi, e vanno separati. Le *estrazioni* sono casuali e devono essere fisse. Il *calcolo* che le trasforma in esiti deve essere vivo.

Il foglio nascosto contiene entrambi gli strati, uno accanto all'altro. Le colonne da B a F sono numeri scritti da Python una volta sola.

```python
generatore = random.Random(SEME_SIMULAZIONE)
...
for k in range(ESTRAZIONI):
    r = prima + k
    ws.cell(row=r, column=1, value=k + 1)
    # Quattro normali standard e una uniforme, fisse.
    for col in range(2, 6):
        ws.cell(row=r, column=col, value=round(generatore.gauss(0, 1), 6))
    ws.cell(row=r, column=6, value=round(generatore.random(), 6))
```

Le colonne da G in poi sono formule che leggono quei numeri insieme agli input dell'utente.

```python
ws.cell(row=r, column=7, value=f"=MAX(0,canone_mese*(1+$B{r}*vol_canone))*12")
ws.cell(row=r, column=8, value=f"=MEDIAN(0,mesi_sfitto+$C{r}*vol_sfitto,12)")
ws.cell(row=r, column=9, value=f"=MAX(0,tasso+$D{r}*vol_tasso)")
```

Il seme è una costante dichiarata nel modulo, non un valore casuale: chiunque rigeneri il workbook ottiene le stesse mille estrazioni, e due persone che discutono lo stesso file guardano gli stessi numeri.

```python
ESTRAZIONI = 1000       # scenari della simulazione probabilistica
SEME_SIMULAZIONE = 20260831   # dichiarato, cosi' la simulazione e' riproducibile
```

Il risultato è una simulazione che non cambia da sola e cambia quando deve. Il costo di ricalcolo, misurato, è sei decimi di secondo per l'intero workbook.

## Due dettagli di implementazione che valgono

Il vincolo dei mesi di sfitto fra zero e dodici si esprime con `MEDIAN(0, valore, 12)`, che restituisce l'elemento centrale dei tre ed è la forma idiomatica del *clamp* in un foglio di calcolo, più leggibile di `MAX(0,MIN(12,valore))` e con lo stesso costo.

L'evento di morosità grave non è una variazione continua ma un salto, e si modella con l'estrazione uniforme confrontata con la probabilità dichiarata.

```python
ws.cell(
    row=r, column=11,
    value=(
        f"=MAX(0,($G{r}-$G{r}/12*$H{r})*(1-morosita_pct)"
        f"-IF($F{r}<prob_morosita_grave,$G{r}/12*mesi_persi_morosita,0))"
    ),
)
```

Tenere separati l'accantonamento ordinario per morosità, che è una percentuale costante, e l'evento grave, che è raro e costoso, evita di rappresentare con una media due fenomeni di natura diversa.

## L'errore di modello, e la correzione

La prima versione applicava la volatilità della rivalutazione così.

```python
ws.cell(row=r, column=10, value=f"=riv_immobile+$E{r}*vol_rivalutazione")
```

Con una volatilità del quattro per cento annuo, un'estrazione a due deviazioni standard produce una rivalutazione dell'otto virgola sei per cento, che composta su venticinque anni moltiplica il valore per quasi otto. Il novantacinquesimo percentile del patrimonio finale usciva a novecentodiciottomila euro su un immobile da centoventimila: matematicamente coerente e finanziariamente assurdo.

L'errore concettuale è trattare una singola estrazione come un *regime permanente* invece che come la media di venticinque realizzazioni annue. La dispersione della media di N osservazioni indipendenti scende con la radice di N, e la correzione è una divisione.

```python
# La rivalutazione si compone su tutto l'orizzonte, quindi l'estrazione
# non e' la variazione di un anno ma la media dell'intero periodo, e la
# sua dispersione scende con la radice del numero di anni. Senza questa
# correzione un'estrazione verrebbe trattata come un regime permanente e
# la coda alta produrrebbe patrimoni finali fuori scala.
ws.cell(row=r, column=10,
        value=f"=riv_immobile+$E{r}*vol_rivalutazione/SQRT(MAX(orizzonte,1))")
```

La correzione non si applica alle altre variabili, ed è una scelta motivata: per il canone e per il tasso l'estrazione rappresenta l'errore nella stima del livello medio, che è persistente e non si media via, mentre per la rivalutazione rappresenta la variazione annua di una grandezza che si compone. Confondere i due tipi di incertezza è l'errore più comune in questo genere di simulazione.

## Il montante, e la simmetria del confronto

La prima versione del montante sommava i flussi di cassa a valore nominale, il che rendeva incomparabile il confronto con l'alternativa finanziaria: chi compra e ha flusso negativo deve versare quella somma ogni anno prendendola da altrove, e quel denaro ha un costo opportunità che l'alternativa invece cattura.

```python
# Il montante confronta due strade che partono dallo stesso esborso. Chi
# compra, se il flusso di cassa e' negativo, deve versare quella somma ogni
# anno prendendola da altrove, e quel denaro ha un costo opportunita': i
# flussi vanno quindi capitalizzati al rendimento del portafoglio
# alternativo, non sommati a valore nominale.
ws.cell(
    row=r, column=19,
    value=f"=$R{r}+IF(rend_port=0,$O{r}*orizzonte,$O{r}*((1+rend_port)^orizzonte-1)/rend_port)",
)
```

Con questa forma le due strade partono dallo stesso esborso, e la differenza sta solo in cosa ci si fa: il confronto diventa simmetrico.

## Il tornado, che risponde a una domanda diversa

La simulazione dice quanto è dispersa la distribuzione degli esiti. Non dice quale ipotesi la disperde. Il blocco a tornado muove una variabile per volta del dieci per cento in meno e in più, tenendo ferme le altre, e ordina per ampiezza dello scostamento.

Serve a una decisione operativa precisa: dove spendere tempo a raccogliere un dato migliore. Sul caso di riferimento la variabile con l'ampiezza maggiore è l'importo del mutuo, seguita dal canone; le spese condominiali muovono un decimo del canone. Sapere che dedicare mezza giornata a stimare meglio le spese condominiali non cambierà la decisione è un'informazione utile quanto il numero stesso.

## Il limite, dichiarato nel foglio

Le estrazioni assumono le variabili indipendenti, e nella realtà non lo sono: quando i tassi salgono i prezzi tendono a scendere, quando il mercato del lavoro peggiora aumentano insieme sfitto e morosità. Introdurre una struttura di correlazione sarebbe possibile con una decomposizione di Cholesky sui fattori, ma richiederebbe di stimare una matrice di correlazione che nessuno ha, e sostituirebbe un'assunzione dichiarata con una nascosta.

La scelta è quindi di restare indipendenti e dirlo nel foglio, precisando che la distribuzione va letta come misura della dispersione degli esiti e non come probabilità oggettiva.

## Come estendere il pattern

Una variabile aleatoria nuova richiede una colonna di estrazione fissa in `_Estrazioni`, un parametro di incertezza nel foglio Rischio con il suo nome definito, e una colonna di calcolo vivo. Va deciso esplicitamente se la sua incertezza è di livello, e allora non si scala, oppure di variazione annua di una grandezza che si compone, e allora si divide per la radice dell'orizzonte.

Il numero di estrazioni si cambia da `ESTRAZIONI`, tenendo presente che il costo cresce linearmente e che oltre qualche migliaio di righe il guadagno statistico è trascurabile rispetto all'incertezza sui parametri di ingresso, che è di gran lunga la fonte di errore dominante.
