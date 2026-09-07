# 14. Due implementazioni dello stesso modello, e il presidio che le tiene insieme

> Deep-dive della voce 14 di [`studio-didattico-master.md`](studio-didattico-master.md). Riguarda [`tools/genera-motore.py`](../../tools/genera-motore.py), `app/src/motore/` e `app/test/motore.test.ts`, e la correzione di `_valore_attuale` in [`src/immobiliare/calcoli.py`](../../src/immobiliare/calcoli.py). È la prima voce che nasce dal cantiere dell'applicazione web, e il pattern che descrive vale ogni volta che lo stesso calcolo deve esistere in due linguaggi.

## Il problema, che non è la traduzione

L'applicazione web deve calcolare nel browser, quindi il motore di calcolo va scritto in TypeScript. Il motore esiste già in Python, verificato da settantotto test, ed è il riferimento del progetto da mesi. Tradurlo è un lavoro meccanico e noioso, e il difetto grave non sta nella traduzione: sta in quello che succede dopo.

Due implementazioni dello stesso modello finanziario non divergono il primo giorno. Divergono al terzo mese, quando la legge di bilancio cambia un'aliquota e la si aggiorna in un posto solo; oppure quando si corregge un difetto su un lato e l'altro resta come era. La divergenza non si annuncia: produce due numeri plausibili, e chi guarda uno dei due non ha modo di sapere che l'altro dice diversamente. Il progetto ha già questa forma di rischio fra il motore Python e le formule del workbook, e la tiene sotto controllo con dei test che confrontano i due sullo stesso caso: il salto di questa voce è portare quella disciplina da un caso a un campione, e da un confronto scritto a mano a uno generato.

## Il presidio, in tre pezzi

Il primo pezzo riguarda i parametri, e la regola è che non si traducono. Le aliquote, i moltiplicatori catastali, gli scaglioni IRPEF e le soglie stanno in `parametri.py` dentro dataclass congelate, ciascuna con la sua fonte e la data di verifica. Il generatore le legge per introspezione e le riscrive in TypeScript, con un'intestazione che dice a chi le trova di non toccarle.

```python
for nome_ts, nome_py in GRUPPI.items():
    istanza = getattr(P, nome_py)
    righe.append(f"export const {nome_ts} = {{")
    for campo in dataclasses.fields(istanza):
        valore = getattr(istanza, campo.name)
        righe.append(f"  {_cammello(campo.name)}: {_valore_ts(valore)} as {_tipo_ts(valore)},")
```

Una copia a mano delle stesse cifre avrebbe funzionato oggi e avrebbe smesso di funzionare al primo aggiornamento fiscale. L'introspezione, invece, fa sì che l'aggiornamento annuale resti l'operazione che era, cioè toccare un file solo, e che il lato TypeScript lo erediti rilanciando il generatore. Due dettagli hanno richiesto attenzione perché Python e TypeScript non scrivono i numeri allo stesso modo: `repr` di un infinito in Python è `inf`, che in TypeScript non compila e che negli scaglioni IRPEF compare davvero come soglia dell'ultimo, e un tipo composto va messo fra parentesi prima del suffisso, altrimenti `readonly readonly number[][]` non è codice valido.

Il secondo pezzo sono i vettori di riscontro. Il motore Python viene eseguito su un campione di casi e per ciascuno si registra l'intero esito, un centinaio di grandezze; la suite TypeScript ricalcola gli stessi casi e confronta ogni valore. Il campione non è casuale, ed è la scelta che conta: è il prodotto cartesiano delle sei decisioni che nel codice cambiano ramo, cioè venditore privato o impresa, agevolazione chiesta o no, prezzo-valore attivo o no, categoria ordinaria o di lusso, sei regimi di locazione, mutuo presente o assente, più sedici casi limite aggiunti uno per uno. Fanno duecentoundici casi, e la proprietà che li rende utili è la copertura dei rami, non il loro numero: un campione casuale di mille casi avrebbe probabilmente mancato la combinazione fra impresa e categoria di lusso, che è un ramo vero del calcolo dell'IVA.

I casi limite sono quelli che in questo dominio rompono le formule, e vale elencarli perché sono trasferibili: rendita catastale a zero, che disattiva il prezzo-valore; tasso a zero, che nella rata alla francese annullerebbe un denominatore; durata a zero; mutuo pari all'intero prezzo; canone a zero; dodici mesi di sfitto su dodici; morosità al cento per cento; prezzo di un euro; reddito da lavoro a zero e a duecentocinquantamila, che sono i due capi degli scaglioni IRPEF; orizzonte di un anno e di quaranta; inflazione a zero e al dieci per cento.

Il terzo pezzo è la tolleranza, e la regola è che si dichiara prima di guardare gli scarti. Vale 1e-9 in termini relativi sopra l'unità e 1e-9 assoluti sotto, ed è una scelta severa e non di comodo: le due implementazioni fanno le stesse operazioni nello stesso ordine su numeri in doppia precisione, quindi devono coincidere quasi all'ultimo bit, e uno scarto maggiore significa che una delle due fa qualcosa di diverso. Una tolleranza scelta dopo aver visto i risultati non verifica il modello, certifica gli scarti che ha trovato.

## La regola che rende la severità sostenibile

La tolleranza a 1e-9 regge solo se la traduzione conserva l'ordine delle operazioni, e questa è la parte che si scopre sbagliando. La somma in virgola mobile non è associativa: sommare tre voci di costo in un ordine diverso può spostare l'ultima cifra, e su un totale di centotrentamila euro l'ultima cifra è dell'ordine di 1e-11, quindi sotto la tolleranza, ma la stessa differenza propagata dentro una bisezione o dentro venticinque anni di capitalizzazione cresce oltre.

Dove l'originale somma in un ordine dettato dalla leggibilità, il porto conserva quell'ordine e lo dichiara.

```typescript
// Ordine dei termini identico alla proprieta' `costi_accessori` dell'originale.
const costiAccessori =
  imposte.totale + provvigione + notaioCompravendita + notaioMutuo + sostitutivaMutuo + istruttoria + perizia + altriCosti;
```

Il commento non spiega che cosa fa la riga, che è ovvio: spiega perché non va riordinata. È lo stesso genere di annotazione della voce 8 sui riferimenti per nome, dove il commento serve a impedire una scorciatoia che sembra innocua.

## Il difetto che il presidio ha trovato prima di essere finito

Il generatore, alla prima corsa, non ha prodotto i vettori: è morto con una divisione per zero dentro `tir`, chiamato da `taeg_approssimato`. Il difetto era nel motore Python, cioè nel riferimento, e c'era da sempre.

La bisezione del tasso interno valuta il valore attuale ai due capi di un intervallo ampio, meno 0,9999 e dieci. Con flussi annuali, che sono venticinque o quaranta termini, entrambi i capi si calcolano senza problemi. Con i flussi mensili di un mutuo, che sono trecentouno, il fattore di sconto esce dai numeri rappresentabili ai due estremi: a meno 0,9999 vale 1e-4 elevato a trecento, che scende sotto il minimo e diventa zero esatto, quindi la divisione solleva un errore; a dieci vale undici elevato a trecento, che supera il massimo e fa fallire l'elevamento a potenza.

```python
def van(tasso: float) -> float:
    return sum(f / (1 + tasso) ** k for k, f in enumerate(flussi))
```

Nessuno se ne era accorto per una ragione che vale registrare: `taeg_approssimato` non era chiamato da nessuno. Il workbook calcola il TAEG con una formula di Excel, la riga di comando non lo espone, e nessun test lo copriva. Era codice corretto nell'intenzione, morto nell'uso, e rotto nel fatto. Il primo strumento che lo ha chiamato su un caso realistico lo ha fatto cadere, e quello strumento è stato il generatore dei vettori: il presidio ha ripagato il proprio costo prima di essere completo.

La correzione tratta i due estremi per quello che sono. Il valore matematicamente corretto quando il fattore di sconto va a zero non è zero, è un infinito con il segno del flusso; quando il fattore supera il massimo, il flusso attualizzato è indistinguibile da zero e il termine non contribuisce. Alla bisezione di quei due capi serve solo il segno, quindi entrambe le risposte bastano.

```python
totale = 0.0
for k, f in enumerate(flussi):
    try:
        fattore = (1 + tasso) ** k
    except OverflowError:
        continue
    if fattore == 0.0:
        if f == 0.0:
            continue
        return float("inf") if f > 0 else float("-inf")
    totale += f / fattore
return totale
```

L'aritmetica sui tassi ordinari resta identica termine per termine, quindi i valori già verificati non si sono mossi, e un test di regressione copre le tre durate che attraversano le due soglie. Il porto TypeScript riproduce la stessa logica, con una differenza da conoscere: in JavaScript nessuno dei due estremi solleva un'eccezione, l'uno dà zero e l'altro infinito, quindi senza lo stesso trattamento si otterrebbe un NaN dalla divisione di infinito per infinito, che è peggio di un errore perché si propaga in silenzio.

## Il controllo negativo, che non è una formalità

I duecentoundici casi sono passati alla prima esecuzione, e un verde così va sospettato prima di essere creduto. Se il confronto fosse scivolato in un ramo sbagliato, o se i vettori fossero arrivati vuoti, il risultato sarebbe stato indistinguibile da quello vero.

La suite contiene quindi un test che verifica il confronto invece del modello: prende un vettore, ne altera l'atteso di poco più della tolleranza su un valore numerico e su una stringa, e pretende che vengano riportati esattamente due scarti, ciascuno con il percorso della voce; poi ripete il confronto sul vettore intatto e pretende che non trovi nulla.

```typescript
attesoGuasto.conto.imposta = attesoGuasto.conto.imposta + 0.001;
attesoGuasto.imposte.regime = "un regime che non esiste";
confronta(attesoGuasto, trovato, "", scarti, ...);
expect(scarti.length).toBe(2);
```

Il percorso nel messaggio è la parte utile. Su duecento casi e un centinaio di grandezze ciascuno, un errore che dice soltanto quale numero non torna costringe a cercare a mano la voce; uno che dice `conto.imposta` indica la funzione da aprire.

## Come si estende il pattern

Quando lo stesso calcolo deve esistere in due posti, l'ordine è questo. I parametri si generano da un'unica fonte e il file generato lo dichiara in testa. I casi si costruiscono come prodotto delle decisioni che cambiano ramo, non come campione casuale, e i limiti si aggiungono uno per uno con il nome di ciò che rompono. La tolleranza si scrive prima. L'ordine delle operazioni si conserva, e dove lo si conserva per questa ragione lo si commenta. La funzione verificata è quella che l'applicazione usa davvero, non una scritta per il test: qui `esitoCompleto` è la stessa che l'interfaccia chiamerà a ogni cambio di input, ed è il motivo per cui la verifica non è su codice morto. E la suite contiene sempre un caso che deve fallire, perché una verifica che non sa fallire non è una verifica.

Un'ultima cosa, che riguarda la scadenza. I vettori sono un'istantanea del riferimento, quindi invecchiano appena il riferimento cambia: `python tools/genera-motore.py --check` esce con codice diverso da zero quando i file su disco non corrispondono a quello che il motore Python produrrebbe adesso, e la suite TypeScript confronta per prima cosa la revisione dei parametri con quella dei vettori. Sono due allarmi per la stessa cosa, e servono entrambi: il primo si accorge del cambiamento, il secondo si accorge che il primo non è stato eseguito.
