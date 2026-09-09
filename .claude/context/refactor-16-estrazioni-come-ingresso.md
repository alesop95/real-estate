# 16. Le estrazioni diventano un ingresso, e la simulazione diventa verificabile

> Deep-dive della voce 16 di [`studio-didattico-master.md`](studio-didattico-master.md). Riguarda `src/immobiliare/rischio.py`, `app/src/motore/rischio.ts`, `tools/genera-motore.py`, `tests/test_rischio.py` e `app/test/rischio.test.ts`. Il pattern che insegna vale per qualunque funzione che contenga una fonte di casualità, e i due difetti che ha fatto emergere valgono per qualunque porto verso un altro linguaggio.

## Il punto di partenza, che non era un difetto di codice

Al 9 settembre 2026 il progetto aveva tre implementazioni del proprio modello e una disciplina per ciascuna coppia. Il motore Python era il riferimento, il workbook lo replicava in formule vive e la verifica consisteva nell'aprirlo con Excel, il motore TypeScript ne era un porto tenuto in riga da duecentoundici vettori di riscontro. Una sola parte del modello stava fuori da tutto questo: la simulazione probabilistica del foglio Rischio, mille scenari con estrazioni congelate, che esisteva soltanto come formule.

Non era un difetto di scrittura, era un difetto di verificabilità. Quelle formule erano state controllate con cura, e la modifica del 4 settembre che vi aveva introdotto il fattore comune era stata misurata dentro Excel con una proprietà forte, cioè la riduzione esatta al caso indipendente a correlazione nulla. Ma la loro correttezza restava dimostrata guardandole, che è esattamente il metodo che questo progetto ha smesso di usare altrove, e per una ragione registrata nella voce 8: nel foglio di calcolo l'errore non si annuncia, produce un numero plausibile.

C'era anche una scadenza. L'applicazione web deve mostrare la distribuzione degli esiti nel browser, quindi la simulazione va scritta in TypeScript comunque: la domanda non era se aggiungere un'implementazione, era se aggiungerne una senza presidio.

## Perché il presidio dei vettori, così com'era, non bastava

Il presidio della voce 14 funziona perché il motore è una funzione deterministica dei suoi input: dato lo stesso ingresso, Python e TypeScript devono produrre lo stesso numero fino all'ultimo bit, e il generatore può quindi scrivere l'ingresso in un file JSON e la suite ricalcolarlo.

Una simulazione non ha questa proprietà. Dipende dagli input e da mille numeri estratti, e i due linguaggi non possono estrarre gli stessi: il generatore di Python è un Mersenne Twister con il proprio stato interno, quello di JavaScript non è nemmeno specificato dallo standard quanto a sequenza. Due implementazioni della stessa simulazione, ciascuna con il proprio generatore, danno risultati diversi anche quando sono entrambe giuste, e distinguere quella differenza da un difetto vero richiede statistica invece di aritmetica: si finirebbe a confrontare percentili con tolleranze larghe, cioè a scrivere una suite che passa anche quando una delle due sbaglia.

La forma sbagliata, quella naturale, è questa.

```python
def simula(base, incertezze, quante=1000, seme=20260831):
    generatore = random.Random(seme)
    esiti = []
    for _ in range(quante):
        estrazione = estrai(generatore)      # la casualità vive qui dentro
        esiti.append(scenario(base, incertezze, estrazione))
    return sintesi(esiti)
```

È comoda da chiamare e impossibile da confrontare. Il seme la rende riproducibile dentro Python, che è già qualcosa, ma non la rende confrontabile con nient'altro: la riproducibilità è una proprietà di quel generatore, non del modello.

## Il salto: la casualità si passa, non si contiene

```python
def simula(base, incertezze=None, estrazioni=None):
    """La simulazione completa: percentili, mediane e le quattro probabilita' che contano."""
    incertezze = incertezze or Incertezze()
    estrazioni = estrazioni if estrazioni is not None else estrazioni_fisse()
    esiti = [scenario(base, incertezze, e) for e in estrazioni]
    ...
```

Le estrazioni sono un parametro. Dentro non c'è nessuna fonte di casualità, quindi `simula` è una funzione pura, e da questo discendono quattro cose che prima non erano possibili.

La prima è il confronto bit per bit fra implementazioni. Il generatore scrive nei vettori anche il campione di estrazioni con cui li ha prodotti, e la suite TypeScript lo passa come ingresso: i cinquantadue casi si confrontano con la stessa tolleranza di un miliardesimo relativo usata per il resto del motore, senza alcuna concessione al fatto che si tratti di una simulazione.

```json
{
 "semeEstrazioni": 20260831,
 "estrazioni": [[0.202201, 0.613942, -1.097567, -0.091461, 1.133257, 0.787717], ...],
 "vettori": [{"n": 1, "ingresso": {"base": {...}, "incertezze": {...}}, "atteso": {...}}]
}
```

La seconda è la prova delle proprietà con estrazioni scelte a mano, che con un generatore interno richiederebbe di cercare fra mille scenari quello che serve. Per verificare che i mesi di sfitto restino dentro il loro intervallo basta un'estrazione assurda, e la prova si legge come l'enunciato.

```python
def test_mesi_di_sfitto_restano_fra_zero_e_dodici():
    giu = R.scenario(base, inc, R.Estrazione(0, 0, -50, 0, 0, 0.5))
    su = R.scenario(base, inc, R.Estrazione(0, 0, 50, 0, 0, 0.5))
    assert giu.mesi_sfitto == 0.0
    assert su.mesi_sfitto == 12.0
```

La terza è il confronto con il workbook. La funzione `estrazioni_fisse` rigenera i numeri con lo stesso seme e lo stesso ordine di chiamata del generatore del foglio, quindi Python e Excel lavorano sugli stessi mille valori: le prime cinque righe del foglio nascosto coincidono a scarto nullo, e sulle diciannove colonne calcolate lo scarto massimo è dell'ordine di dieci alla meno dodici. Su ciò che il foglio mostra, cioè quindici percentili, quattro probabilità e ventiquattro celle di tornado, lo scarto massimo è 1,5 su dieci alla tredicesima. Quei numeri sono ora congelati in `tests/test_rischio.py`, e questo è il punto che vale ricordare: un test del progetto contiene il risultato di una misura fatta con un altro programma, così che l'accordo fra le due implementazioni non resti la fotografia di un giorno.

La quarta è che l'uso interattivo resta possibile senza inquinare la parte verificata. Il browser ha bisogno di estrarre, e lo fa con una funzione dichiaratamente fuori dal confronto.

```typescript
/**
 * Estrazioni riproducibili a partire da un seme, per l'uso nel browser.
 *
 * Sta fuori dalla parte verificata contro Python, e va detto perche': le estrazioni di
 * Python vengono dal suo Mersenne Twister e queste da un generatore diverso, quindi le due
 * sequenze non coincidono ne' possono. Cio' che deve coincidere e' l'esito a estrazioni
 * date, e quello i vettori lo verificano.
 */
export function estrazioniDaSeme(quante: number, seme: number): Estrazione[] {
```

Il confine è la parte interessante. Non si pretende che due generatori coincidano, si sposta la casualità fuori dal contratto e si verifica ciò che il contratto contiene: dato un campione di estrazioni, le due implementazioni devono dire lo stesso numero. Della funzione che estrae si prova l'unico requisito che ha davvero, cioè che lo stesso seme dia sempre la stessa sequenza, perché una simulazione che cambia risposta a ogni ridisegno dell'interfaccia non è uno strumento di decisione.

## Il primo difetto trovato: il mezzo arrotondato al pari

Il confronto con Excel, alla prima corsa, ha dato scarti dell'ordine di dieci alla meno tredici su trenta valori e uno scarto del venticinque per cento su uno solo: il lato sinistro della riga del tornado che riduce la durata del mutuo del dieci per cento. Il foglio diceva meno 4.848 euro, il modulo meno 5.019.

La causa è una differenza di convenzione fra due funzioni che portano lo stesso nome. Venticinque anni ridotti del dieci per cento fanno ventidue e mezzo; `ROUND` di Excel allontana il mezzo da zero e restituisce ventitre, `round` di Python lo porta al pari e restituisce ventidue. Un anno di durata in meno su un mutuo di novantamila euro vale centosettanta euro di rata annua, che non è nel rumore.

```python
def arrotonda(valore: float) -> int:
    """L'arrotondamento di Excel, che sul mezzo si allontana da zero."""
    if valore >= 0:
        return int(valore + 0.5)
    return -int(-valore + 0.5)
```

Tre cose rendono questo difetto istruttivo. Si presentava su un lato solo del tornado, perché al più dieci per cento il numero è ventisette e mezzo, che le due convenzioni arrotondano entrambe a ventotto: una divergenza che compare in metà dei casi somiglia a un difetto del modello e non a una differenza di convenzione. Non lo avrebbe trovato nessun test scritto guardando una sola implementazione, perché entrambe erano internamente coerenti. E si è presentato di nuovo, con il segno cambiato, nel porto TypeScript: `Math.round` in JavaScript arrotonda il mezzo verso l'alto, quindi su meno ventidue e mezzo dà meno ventidue dove Excel dà meno ventitre. La stessa funzione, tre linguaggi, tre convenzioni diverse, e nessuno dei tre lo dichiara nel nome.

## Il secondo difetto trovato: una divisione per zero che il foglio non sa evitare

Il debito residuo, nel foglio nascosto, è una formula chiusa che divide per la differenza fra due montanti.

```
=IF(mutuo_importo>0,mutuo_importo*((1+$O2/12)^(durata*12)-(1+$O2/12)^(MIN(orizzonte,durata)*12))/((1+$O2/12)^(durata*12)-1),0)
```

A tasso nullo quel denominatore è zero esatto, e la cella diventa un errore di divisione che si propaga a patrimonio finale e montante, cioè a due delle cinque distribuzioni. Un mutuo a tasso zero è raro ma non impossibile, e la simulazione può arrivarci anche da un tasso positivo, perché lo scarto sul tasso è limitato inferiormente a zero e con un'incertezza larga una coda di scenari finisce esattamente là.

Nei due moduli il caso è trattato per quello che è, cioè il limite in cui il capitale si rimborsa in parti uguali.

```python
    i = tasso_annuo / 12
    if i == 0:
        return importo * (1 - pagate / n)
```

È lo stesso genere di scoperta della voce 14, dove il generatore dei vettori aveva fatto emergere la divisione per zero nel tasso interno di rendimento: scrivere una seconda implementazione costringe a guardare i casi limite di quella vecchia, perché in un linguaggio di programmazione un caso limite va deciso mentre in un foglio di calcolo resta una cella che nessuno ha ancora fatto diventare rossa. Il difetto del foglio non è stato corretto in questa sessione, ed è dichiarato: correggerlo significa cambiare le formule di mille righe e rigenerare il workbook, che è un intervento a sé e non un dettaglio da infilare in un porto.

## La terza cosa emersa, che è un'approssimazione e non un difetto

La simulazione tassa il ricavo effettivo con la cedolare secca sul canone libero anche quando il regime scelto nel foglio Locazione è un altro, perché la formula del foglio nascosto cita quella cella e non quella del regime selezionato. Nessuno lo aveva scritto da nessuna parte, e si vede solo scrivendo la stessa cosa in un linguaggio dove ogni valore ha un nome e una provenienza.

La scelta fatta nei due moduli è di portare l'aliquota come parametro con lo stesso valore predefinito. Il confronto con Excel resta quindi esatto, cioè misura il foglio e non una sua correzione, e l'applicazione potrà passare l'aliquota del regime scelto senza che nessuno debba ricordarsi di questa storia. È il modo in cui si porta un'approssimazione: la si rende visibile e opzionale, invece di ereditarla in silenzio o di correggerla di nascosto cambiando i numeri che l'utente si aspetta.

## Come si estende il pattern

Ogni volta che una funzione di questo progetto conterrà una fonte di casualità, di tempo o di ambiente, quella fonte va spostata fra i parametri. La forma è sempre la stessa: la funzione riceve ciò che non può controllare, un helper accanto lo produce con il proprio comportamento predefinito, e la verifica lavora sulla funzione e non sull'helper. Vale per le estrazioni, vale per la data odierna in una scadenza fiscale, vale per l'orologio di un token.

Sul confronto fra implementazioni, la regola che questa voce aggiunge alle precedenti è di sospettare le funzioni omonime. Percentile, mediana e arrotondamento esistono in tutti e tre gli ambienti con lo stesso nome e convenzioni diverse, e la convenzione non è mai nella firma: `percentile` di Excel interpola linearmente fra i due valori adiacenti, ma esistono almeno sei convenzioni in uso, e chi porta un modello da un foglio a un linguaggio deve scegliere quella del foglio e scrivere accanto perché. Nel modulo Python le tre funzioni sono riscritte per questa ragione, con il commento che dice quale convenzione replicano e che uno scarto piccolo e sistematico è il modo peggiore di sbagliare, perché somiglia a un errore di arrotondamento e non lo è.
