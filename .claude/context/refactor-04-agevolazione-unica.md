# 04. Una sola fonte di verità per l'agevolazione

> Deep-dive della voce 4 di `studio-didattico-master.md`. Riguarda `src/immobiliare/calcoli.py`, funzioni `agevolazione_applicabile`, `base_imponibile_registro` e `imposte_acquisto`, e le celle di controllo del foglio Immobile.

## La regola fiscale, e perché si presta all'errore

L'agevolazione prima casa produce due effetti distinti sulla stessa operazione. Abbassa l'aliquota dell'imposta di registro dal nove al due per cento, e abbassa il moltiplicatore catastale da centoventi a centodieci. Chi implementa il calcolo tende a trattarli come due cose, perché stanno in due punti diversi del conto: il moltiplicatore serve a determinare la base imponibile, l'aliquota si applica alla base già determinata.

Sono però governati dalla stessa condizione, e la condizione non è banale, perché l'agevolazione richiesta non coincide con l'agevolazione spettante: le categorie catastali A/1, A/8 e A/9 ne sono escluse per legge a prescindere da cosa dichiari l'acquirente.

## Com'era

Il calcolo della base guardava alla volontà dell'acquirente.

```python
def base_imponibile_registro(immobile: Immobile, acquirente: Acquirente) -> float:
    if not acquirente.prezzo_valore or immobile.rendita_catastale <= 0:
        return immobile.prezzo
    return valore_catastale(immobile.rendita_catastale, acquirente.prima_casa)
```

Il calcolo dell'imposta guardava alla condizione completa.

```python
di_lusso = immobile.categoria in t.categorie_escluse_prima_casa
prima_casa = acquirente.prima_casa and not di_lusso
```

Su un immobile in categoria A/2 o A/3 le due espressioni valgono lo stesso e il difetto non si manifesta. Su una A/8, con l'acquirente che chiede comunque l'agevolazione, la base veniva calcolata con il moltiplicatore 110 e poi tassata correttamente al nove per cento. Il risultato è un'imposta sottostimata di circa un dodicesimo, su una categoria dove gli importi sono grandi.

La cosa che rende il caso istruttivo è che il difetto era identico nelle formule Excel:

```python
r = S.campo(ws, r, "Valore catastale",
            '=rendita*riv_rendita*IF(prima_casa="SI",molt_prima,molt_ord)', S.EURO)
```

La doppia implementazione, che è il presidio principale del progetto, non ha protetto: entrambe le versioni erano state scritte dallo stesso ragionamento, e il ragionamento era sbagliato. La doppia implementazione protegge dagli errori di trascrizione, non da un errore concettuale replicato fedelmente.

## Com'è ora

La condizione diventa una funzione con un nome che dice esattamente cosa distingue.

```python
def agevolazione_applicabile(immobile: Immobile, acquirente: Acquirente) -> bool:
    """Vero se l'agevolazione prima casa spetta davvero.

    Non basta che l'acquirente la chieda: le categorie A/1, A/8 e A/9 ne sono escluse
    per definizione, e l'esclusione si riflette anche sul moltiplicatore catastale,
    che torna a centoventi. Tenere la verifica in una funzione sola evita che il
    moltiplicatore e l'aliquota si disallineino, che e' il modo tipico in cui questo
    errore si presenta.
    """
    di_lusso = immobile.categoria in IMPOSTE_LUSSO
    return acquirente.prima_casa and not di_lusso
```

Tutti i punti che ne dipendono la chiamano, nessuno la ricalcola.

```python
def base_imponibile_registro(immobile: Immobile, acquirente: Acquirente) -> float:
    if not acquirente.prezzo_valore or immobile.rendita_catastale <= 0:
        return immobile.prezzo
    return valore_catastale(immobile.rendita_catastale,
                            agevolazione_applicabile(immobile, acquirente))
```

## Nel workbook: l'ordine diventa parte della correttezza

La stessa struttura si traduce in due celle di controllo con un nome, calcolate prima di tutto ciò che ne dipende. Il commento nel generatore documenta perché l'ordine non è cosmetico.

```python
# L'ordine conta: il moltiplicatore catastale dipende dall'agevolazione
# effettivamente applicabile, non da quella richiesta, quindi le due celle di
# controllo vanno calcolate prima del valore catastale. Usare la prima casa
# richiesta darebbe il moltiplicatore 110 anche su una categoria di lusso, che
# dall'agevolazione e' esclusa, e sottostimerebbe l'imposta.
riga_lusso = r
r = S.campo(ws, r, "Categoria di lusso",
            '=IF(OR(categoria="A/1",categoria="A/8",categoria="A/9"),"SI","NO")')
self.nome("di_lusso", ws, f"B{riga_lusso}")
riga_agev = r
r = S.campo(ws, r, "Agevolazione effettivamente applicabile",
            '=IF(AND(prima_casa="SI",di_lusso="NO"),"SI","NO")')
self.nome("agevolata", ws, f"B{riga_agev}")
```

Da lì in avanti nessuna formula scrive più `prima_casa` per decidere un'aliquota o un moltiplicatore: scrive `agevolata`. La cella `prima_casa` resta un input, cioè la volontà dichiarata dall'acquirente, e la cella `agevolata` è il fatto giuridico che ne deriva. La distinzione fra i due è visibile nel foglio, ed è didatticamente utile perché è esattamente la distinzione che il notaio farà in atto.

## Il test che lo blocca

```python
def test_categoria_di_lusso_esclusa_dall_agevolazione():
    immobile = C.Immobile(prezzo=500_000, rendita_catastale=3_000, categoria="A/8")
    acquirente = C.Acquirente(prima_casa=True, prezzo_valore=True)
    imposte = C.imposte_acquisto(immobile, acquirente)
    # Il moltiplicatore torna a 120 e l'aliquota al 9 per cento.
    assert imposte.imponibile == 3_000 * 1.05 * 120
    assert imposte.registro == imposte.imponibile * P.IMPOSTE_TRASFERIMENTO.registro_ordinario
```

Il test verifica la base *e* l'aliquota nello stesso caso, che è il punto: un test che avesse controllato solo l'aliquota sarebbe passato anche con il difetto presente.

## Come estendere il pattern

Ogni volta che due grandezze dipendono dalla stessa condizione, la condizione va calcolata una volta e riferita. Il segnale d'allarme è trovarsi a scrivere la stessa espressione booleana in due punti: non è duplicazione da eliminare per eleganza, è una divergenza futura garantita, e divergerà nel caso raro, cioè quello che nessuno prova a mano.

Nel workbook la regola operativa è che una condizione condivisa merita una cella con un nome, anche se la cella contiene solo `"SI"` o `"NO"`. Costa una riga e rende visibile all'utente un passaggio del ragionamento che altrimenti resterebbe sepolto dentro una formula annidata.
