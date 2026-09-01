# 09. Il regime di acquisto torna nella riga, con un terzo stato

> Deep-dive della voce 9 di `studio-didattico-master.md`. Riguarda la dataclass `Annuncio` e la lista `ordine` in `src/immobiliare/annunci.py`, i metodi `foglio_annunci` e `foglio_confronto_immobili` di `excel_builder.py`, e i test `test_regime_di_acquisto_per_riga_nel_confronto` e `test_campi_a_tre_stati_normalizzati`.

## Che cosa faceva l'assunzione globale

Il foglio Confronto immobili applica il modello completo a ogni riga del registro, imposte di trasferimento comprese. Le imposte erano calcolate così, dove `da_impresa`, `agevolata`, `di_lusso` e `usa_prezzo_valore` sono nomi definiti che vivono nel foglio Immobile.

```python
ws.cell(row=r, column=9, value=(
    f'=IF({vuoto},"",IF(da_impresa="SI",'
    f'$D{r}*IF(agevolata="SI",iva_prima,IF(di_lusso="SI",iva_lusso,iva_ord))+3*fisso_impresa,'
    f'MAX(IF(AND(usa_prezzo_valore="SI",$F{r}>0),$F{r}*riv_rendita*IF(agevolata="SI",molt_prima,molt_ord),$D{r})'
    f'*IF(agevolata="SI",reg_prima,reg_ord),reg_min)+ipo_priv+cat_priv))'
))
```

La formula è corretta. Il problema è che i quattro nomi valgono per tutte le righe, e il foglio lo dichiarava in nota: *il regime di acquisto è quello impostato nel foglio Immobile e viene applicato a tutti gli immobili della lista*.

La dichiarazione rendeva il limite onesto e non innocuo, e la differenza va vista sui numeri. Su un prezzo di 72.000 euro, con l'agevolazione prima casa:

```
da privato, con prezzo-valore:  registro 2% sul valore catastale + 100 fissi  =  1.540 EUR
da impresa, con IVA:            IVA 4% su 72.000 + 3 imposte fisse da 200     =  3.480 EUR
```

Il rapporto è più di due, e con il prezzo-valore attivo la base imponibile del registro resta ancorata alla rendita catastale mentre l'IVA colpisce il prezzo intero, quindi la forbice si allarga al crescere del prezzo. In una graduatoria ordinata per rendimento netto sul costo totale, applicare a un nuovo da costruttore le imposte di un usato da privato lo fa risalire di parecchie posizioni. La conseguenza non è un'imprecisione: è un ordinamento invertito, e chi legge una tabella ordinata legge l'ordine, non la nota.

## Il dato torna dove varia

```python
    prima_casa: str = ""
    """SI, NO, oppure vuoto per ereditare il regime del foglio Immobile.

    Non e' una caratteristica dell'immobile ma della posizione di chi compra
    rispetto a quell'immobile: lo stesso appartamento e' prima casa per chi non
    ha altre abitazioni nel Comune e non lo e' per chi ce le ha...
    """
    venditore_impresa: str = ""
```

Sul foglio di confronto le due colonne non sono decorative: sono le celle che le formule leggono.

```python
ws.cell(row=r, column=26, value=f'=IF({vuoto},"",IF(Annunci!$AK{s}="",agevolata,Annunci!$AK{s}))')
ws.cell(row=r, column=27, value=f'=IF({vuoto},"",IF(Annunci!$AL{s}="",da_impresa,Annunci!$AL{s}))')
```

e la formula delle imposte diventa

```python
    f'=IF({vuoto},"",IF($AA{r}="SI",'
    f'$D{r}*IF($Z{r}="SI",iva_prima,IF(di_lusso="SI",iva_lusso,iva_ord))+3*fisso_impresa,'
    f'MAX(IF(AND(usa_prezzo_valore="SI",$F{r}>0),$F{r}*riv_rendita*IF($Z{r}="SI",molt_prima,molt_ord),$D{r})'
    f'*IF($Z{r}="SI",reg_prima,reg_ord),reg_min)+ipo_priv+cat_priv))'
```

Le due colonne restano visibili accanto alle imposte, e questa è una scelta di leggibilità che vale enunciare: una graduatoria in cui una riga paga l'IVA e un'altra il registro va letta sapendolo, non scoprendolo aprendo una formula.

## Il terzo stato, che è la parte non ovvia

Un campo booleano in un registro ha la tentazione di essere booleano. Qui è una stringa con tre valori, e il vuoto non significa NO.

```python
IF(Annunci!$AK{s}="", agevolata, Annunci!$AK{s})
```

Il vuoto significa *eredita da dove stava prima*, e serve a rendere l'aggiunta esattamente neutra su ciò che esiste già. La neutralità non è cortesia verso il passato: è una proprietà verificabile e verificata, cioè che un registro non toccato produce gli stessi numeri di prima. L'alternativa, trattare il vuoto come NO, avrebbe cambiato in silenzio le imposte dei dodici annunci a registro, togliendo loro l'agevolazione prima casa che era attiva a livello globale, e nessuno se ne sarebbe accorto perché i numeri restano numeri.

Il costo del terzo stato è un `IF` in più per colonna e una validazione a elenco che ammette il vuoto. È poco, e compra una migrazione senza rischi.

## Il rischio che il campo nuovo ha portato con sé

`venditore_impresa` è entrato nello schema di estrazione del modello locale, perché la vendita diretta dal costruttore sta scritta negli annunci.

```python
"venditore_impresa": "SI se la vendita e' diretta dal costruttore o da un'impresa, o se l'annuncio indica il prezzo soggetto a IVA, altrimenti vuoto",
```

A quel punto un modello linguistico, a una domanda che somiglia a un booleano, risponde volentieri `true`. Excel confronta il testo senza distinguere le maiuscole, quindi `si` funziona; `true` no, risulta diverso da `SI` e viene letto come un NO. Nessun errore, imposte sbagliate su quella riga.

```python
    CAMPI_SI_NO = ("asta", "nuova_costruzione", "prima_casa", "venditore_impresa")

    def __post_init__(self) -> None:
        ...
        affermativi = {"si", "s", "yes", "y", "true", "vero", "1"}
        negativi = {"no", "n", "false", "falso", "0"}
        for campo in self.CAMPI_SI_NO:
            valore = str(getattr(self, campo) or "").strip()
            if not valore:
                setattr(self, campo, "")
            elif valore.casefold() in affermativi:
                setattr(self, campo, "SI")
            elif valore.casefold() in negativi:
                setattr(self, campo, "NO")
```

La normalizzazione sta in `__post_init__` e non nel percorso di importazione, così che valga per ogni annuncio da qualunque origine, CSV incluso. E si ferma dove finisce la certezza: un valore non riconosciuto resta scritto com'è. Tradurre *da chiarire col notaio* in NO significherebbe fingere una risposta che nessuno ha dato; lasciarlo visibile lo fa comportare come un vuoto nel confronto con SI, e chi apre il foglio lo vede.

## Il test, e il punto che presidia

```python
    imposte = ws.cell(row=prima, column=9).value
    assert f"$AA{prima}" in imposte
    assert f"$Z{prima}" in imposte
    assert "da_impresa" not in imposte and "agevolata" not in imposte
```

L'asserzione che conta è la terza, quella negativa. La presenza delle due colonne non protegge da nulla: se la formula delle imposte tornasse a citare i nomi globali, le colonne resterebbero al loro posto, mostrerebbero il regime della riga, e il foglio continuerebbe a calcolare con il regime globale. Sarebbe il difetto originale con l'aggiunta di due colonne che dicono il contrario di ciò che il foglio fa.

## Come estendere il pattern

Per portare nel registro un'altra assunzione oggi globale, per esempio l'opzione prezzo-valore, servono un campo con default vuoto, la voce in coda alla lista `ordine` e la coppia nome-larghezza in coda a `colonne`, una colonna nel foglio di confronto che ricada sul nome globale quando il registro tace, e la sostituzione del nome globale con il riferimento a quella colonna in tutte le formule che lo usano. La colonna va aggiunta in coda e non in mezzo, perché il foglio di confronto cita le colonne del registro per lettera.

La regola generale: quando una nota di un foglio dice *questa assunzione vale per tutte le righe*, la nota è un promemoria che il dato sta nel posto sbagliato. Se l'assunzione non cambia mai, non ha bisogno della nota; se la nota serve, l'assunzione varia, e un dato che varia per riga appartiene alla riga.
