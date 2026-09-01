# 08. Riferimenti per nome, non per coordinata

> Deep-dive della voce 8 di `studio-didattico-master.md`. Riguarda il metodo `foglio_cruscotto` di `excel_builder.py`, il conto economico dentro `foglio_locazione`, la tabella a tre scenari dentro `foglio_scenari`, e i tre test `test_cruscotto_legge_il_confronto_affitto_per_nome`, `test_conto_economico_locazione_somma_le_righe_giuste`, `test_tabella_scenari_non_usa_offset_numerici`.

## Il difetto, in una riga di codice

Il Cruscotto è il primo foglio del workbook e raccoglie i cinque numeri di decisione. Uno di essi è il verdetto fra comprare e restare in affitto, che il Cruscotto non calcola ma legge dal foglio dedicato. La formula era questa.

```python
riga_conf = riga_kpi("Comprare oppure restare in affitto",
                     '=IF(Immobile!$B$21="SI",IF(\'Confronto affitto\'!$B$52>0,"conviene comprare","conviene restare in affitto e investire"),"non pertinente: non e\' abitazione principale")',
                     None, "", "Il confronto ha senso solo se l'immobile e' destinato ad abitazione propria.")
```

Il Cruscotto viene costruito per primo, perché è il primo foglio, e in quel momento le righe del foglio `Confronto affitto` non esistono ancora: la coordinata è stata scritta a mano contandola su un file già generato. Il conteggio era giusto quando è stato fatto. Poi la sezione dell'esito di quel foglio è cambiata, e la riga 52 è diventata *Patrimonio comprando*, mentre la differenza fra i due patrimoni si è spostata alla 56.

```
52 | Patrimonio comprando                          | =INDEX(conf_valore,orizzonte+1)*(1-costi_vendita)-INDEX(conf_debito,orizzonte+1)
53 | Portafoglio lordo affittando                  | =INDEX(conf_portafoglio,orizzonte+1)
54 | Capitale versato nel portafoglio              | =INDEX(conf_versato,orizzonte+1)
55 | Patrimonio affittando, al netto dell'imposta  | =INDEX(conf_portafoglio,orizzonte+1)-...
56 | Differenza a favore dell'acquisto             | =B52-B55
57 | Esito                                        | =IF(B56>0,"Conviene comprare","Conviene restare in affitto...")
```

Il patrimonio comprando è il valore dell'immobile al netto dei costi di vendita meno il debito residuo: è positivo per qualunque immobile che valga più del debito che lo grava, cioè quasi sempre. Il Cruscotto ha quindi risposto *conviene comprare* in modo pressoché indipendente dal confronto che diceva di riportare.

## La misura del danno

La divergenza non è teorica. Con l'immobile marcato come abitazione principale e il rendimento del portafoglio alternativo portato al nove per cento, letto via automazione COM sul file generato:

```
B52 patrimonio comprando:          190.967 EUR
B56 differenza a favore acquisto:  -114.579 EUR
esito del foglio:                  Conviene restare in affitto e investire la differenza
Cruscotto con conf_differenza:     conviene restare in affitto e investire
Cruscotto con B52:                 conviene comprare
```

Due fogli dello stesso file che dicono il contrario, e quello che sbagliava era il primo, cioè quello che si apre per decidere.

Vale registrare che si trattava di una recidiva. Il work-log del 28 agosto riporta: *la differenza fra i due patrimoni nel foglio di confronto puntava alla riga del capitale versato invece che a quella del patrimonio comprando*. Lo stesso errore, nello stesso foglio, quattro giorni prima. Un difetto che si ripresenta nello stesso punto non è una distrazione: è la firma di una forma di codice che rende la distrazione inevitabile.

## La correzione, e perché è una regola e non una toppa

```python
# Nel foglio Confronto affitto, accanto alla cella:
self.nome("conf_differenza", ws, f"B{riga_diff}")

# Nel Cruscotto:
riga_conf = riga_kpi("Comprare oppure restare in affitto",
                     "=IF(abitazione_principale=\"SI\",IF(conf_differenza>0,\"conviene comprare\",...))",
                     None, "", "...Legge il foglio Confronto affitto per nome definito, non per coordinata.")
```

Il nome definito risolve anche il problema dell'ordine di costruzione, che era la ragione per cui la coordinata era stata scritta a mano: Excel risolve i nomi al momento del calcolo, non della scrittura, quindi il Cruscotto può citare una cella di un foglio che non è ancora stato creato, e `openpyxl` deve solo trovare il nome registrato al momento del salvataggio.

## La stessa famiglia, dentro una tabella

Il conto economico del foglio Locazione ha quattro colonne, una per regime fiscale, e diciassette righe. L'helper che scrive una riga incrementava un contatore, e le righe da citare si calcolavano a mano.

```python
riga_conf("Canone o ricavo lordo annuo", ...)
riga_pot = base
riga_conf("Perdita per sfitto", ...)
riga_sf = base + 1
...
riga_gest_r = base + 10
riga_conf("Reddito operativo netto",
          f"=B{riga_eff}+SUM(B{base+4}:B{riga_gest_r})", ...)
riga_noi = base + 11
```

Inserire una voce di costo in mezzo sposta di uno tutte le righe successive e lascia `base+4`, `base+10`, `base+11` dov'erano. Il reddito operativo netto somma un intervallo traslato di una riga, quindi include l'ultima riga dei ricavi e perde l'ultimo costo; l'utile netto legge una riga che non è più quella dell'imposta. Nessuna cella va in errore. I valori restano dell'ordine di grandezza giusto.

La correzione è che la riga non si calcola, si chiede.

```python
def riga_conf(etichetta, f_lib, f_conc, f_irp, f_brev, formato=S.EURO, risultato=False):
    nonlocal r
    scritta = r
    ...
    r += 1
    return scritta

riga_pot = riga_conf("Canone o ricavo lordo annuo", ...)
riga_sf = riga_conf("Perdita per sfitto", ...)
riga_primo_costo = riga_conf("Spese condominiali a carico", ...)
...
riga_ultimo_costo = riga_conf("Gestione e costi variabili", ...)
riga_noi = riga_conf("Reddito operativo netto",
                     f"=B{riga_eff}+SUM(B{riga_primo_costo}:B{riga_ultimo_costo})", ...)
```

Il blocco dei costi si delimita catturando la prima e l'ultima riga, quindi una voce aggiunta in mezzo entra da sola nella somma. La variabile di ancoraggio `base` è stata rimossa perché non aveva più usi: è il segnale che la trasformazione è completa e non parziale.

## Un grado in più di rigidità, dove la tabella nasce da un ciclo

La tabella a tre scenari del foglio Scenari ha lo stesso problema, ma le formule vengono generate da un ciclo su una lista di voci, e citano righe scritte dallo stesso ciclo. Passare i riferimenti in un dizionario che cresce mentre il ciclo procede fa di più che correggere: rende impossibile la classe di errore.

```python
posizioni = {}
posizioni["ca"] = riga_scenario("Canone mensile", [...])
...
for etichetta, chiave, formula, formato, risultato in [
    ("Ricavo effettivo", "ric", "({c}{ca}*12-{c}{ca}*{c}{sf})*(1-{c}{mo})", S.EURO, False),
    ("Reddito operativo netto", "noi", "{c}{ric}-{c}{cos}", S.EURO, False),
    ...
]:
    valori = ["=" + formula.format(c=c, **posizioni) for c in colonne]
    posizioni[chiave] = riga_scenario(etichetta, valori, formato, risultato=risultato)
```

Una formula che citasse una riga non ancora scritta cercherebbe una chiave non ancora presente, e `str.format` solleverebbe `KeyError` alla generazione. Il vincolo che ne discende, cioè che una formula può citare solo righe precedenti, era già vero di fatto in questa tabella: adesso è imposto dal linguaggio invece che dall'attenzione, e la sua violazione costa un'eccezione invece di un numero sbagliato.

## I test, e perché sono scritti in termini di etichette

```python
destinazioni = list(wb.defined_names["conf_differenza"].destinations)
foglio, coordinata = destinazioni[0]
riga_nome = int("".join(c for c in coordinata if c.isdigit()))
etichetta = wb[foglio].cell(row=riga_nome, column=1).value
assert etichetta == "Differenza a favore dell'acquisto"
```

L'asserzione non è che il nome punti alla riga 56, che sarebbe la stessa fragilità in forma di test, ma che punti alla riga la cui etichetta è quella attesa. Sopravvive a un riordino del foglio e falla soltanto se il nome smette di indicare la grandezza giusta, che è esattamente il difetto originale.

Lo stesso principio nel test del conto economico: si costruisce una mappa da etichetta a riga leggendo la colonna A, e si verifica che il primo costo stia subito sotto il ricavo effettivo, che l'ultimo stia subito sopra il reddito operativo, e che la formula del reddito operativo contenga `SUM` esattamente su quell'intervallo, su tutte e quattro le colonne dei regimi e non solo sulla prima.

Nel test della tabella degli scenari il controllo è generico e non enumera le formule: per ogni riga si estraggono con un'espressione regolare tutti i riferimenti di colonna B, C e D, e si verifica che ciascuno cada dentro la tabella e prima della riga che lo cita.

```python
for citata in re.findall(r"\$?[BCD](\d+)", formula):
    citata = int(citata)
    assert prima <= citata <= ultima
    assert citata < riga
```

## Come estendere il pattern

Per un riferimento fra fogli si registra un nome con `self.nome` accanto alla cella e lo si cita per nome, sempre, anche quando la coordinata sarebbe comoda perché il foglio è già stato scritto. Per una riga di una tabella costruita da un helper si usa il valore restituito dall'helper, e se la tabella nasce da un ciclo si passano i riferimenti in un dizionario a chiavi.

La regola generale che vale oltre questo progetto: quando esistono più modi di scrivere un riferimento, la scelta non va fatta sul modo più leggibile ma sul modo in cui l'errore si manifesta. Un riferimento simbolico che sbaglia produce un'eccezione o un `#NOME?`; un riferimento posizionale che sbaglia produce un valore. Il primo costa cinque minuti a chi genera il file, il secondo costa una decisione a chi lo legge.
