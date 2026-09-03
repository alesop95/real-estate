# 05. Un costo ricorrente sta in un posto solo

> Deep-dive della voce 5 di [`studio-didattico-master.md`](studio-didattico-master.md). Riguarda il rapporto fra il foglio Locazione e il foglio Cash flow, e la funzione `conto_economico` in `src/immobiliare/calcoli.py`.

## L'origine: una voce che nessuno mette a bilancio

Un immobile tenuto quarant'anni va rifatto almeno una volta, e un rifacimento completo costa un ordine di grandezza pari a un terzo del valore. Trattarlo come un evento futuro fuori dal rendimento corrente è il modo più diffuso di sopravvalutare un investimento immobiliare, e il progetto lo ripartisce come costo annuo ricorrente.

```python
ristrutturazione_su_valore: float = 1.0 / 3.0
anni_fra_ristrutturazioni: int = 40
```

Fin qui la decisione è di modello, ed è documentata come ADR-005. Il difetto è nato da come è stata implementata.

## Com'era: due luoghi, due sottrazioni

Il foglio Cash flow aveva una colonna dedicata.

```python
intest = [
    "Anno", "Ricavo lordo", "Ricavo effettivo", "Costi operativi", "Accant. ristrutt.",
    "Imposta sul reddito", "Rata mutuo", "Detrazione interessi", "Cash flow netto", ...
]
...
ws.cell(row=r, column=5,
        value=f'=IF({attivo},-accantonamento_ristrutturazione*(1+infl)^($A{r}-1),0)')
```

Contemporaneamente il foglio Locazione lo includeva fra i costi del conto economico, e la colonna dei costi operativi del Cash flow era derivata per differenza dal reddito operativo netto della locazione.

```python
ws.cell(row=r, column=4,
        value=f'=IF({attivo},-(ricavo_effettivo-noi_annuo)*(1+infl)^($A{r}-1),0)')
```

`ricavo_effettivo - noi_annuo` è per costruzione la somma di tutti i costi operativi, accantonamento incluso. La colonna 4 lo conteneva già, la colonna 5 lo sottraeva di nuovo. Il flusso di cassa risultava peggiore del vero di mille euro l'anno, per venticinque anni.

Nessuna delle due formule è sbagliata presa da sola, ed è questo che rende il difetto interessante: la revisione riga per riga non lo trova, perché ogni riga è corretta. Si trova solo guardando la relazione fra i due fogli.

## Com'è ora

La colonna scompare dal Cash flow, e il commento nel generatore dichiara perché.

```python
# I costi operativi della colonna D comprendono gia' l'accantonamento per la
# ristrutturazione, perche' quest'ultimo e' una riga del conto economico nel
# foglio Locazione ed entra quindi nel reddito operativo netto. Una colonna
# separata qui lo conterebbe due volte.
intest = [
    "Anno", "Ricavo lordo", "Ricavo effettivo", "Costi operativi",
    "Imposta sul reddito", "Rata mutuo", "Detrazione interessi", "Cash flow netto", ...
]
```

Nel motore Python la stessa disciplina significa che l'accantonamento è un campo della struttura del conto economico, non un valore che il chiamante sottrae dopo.

```python
@dataclass
class ContoEconomico:
    ...
    ristrutturazione: float = 0.0
    """Accantonamento annuo per la ristrutturazione di fine ciclo. Vedi ADR-005:
    e' un costo ricorrente, non un evento futuro da tenere fuori dal rendimento."""

    @property
    def costi_operativi(self) -> float:
        return (
            self.condominio + self.manutenzione + self.assicurazione
            + self.imu + self.gestione + self.ristrutturazione
        )
```

Prima della correzione la riga di comando compensava a mano, con due righe che erano il sintomo del problema.

```python
accantonamento = immobile.prezzo * P.COSTI.ristrutturazione_su_valore / P.COSTI.anni_fra_ristrutturazioni
noi = conto.noi - accantonamento
utile = conto.utile_netto - accantonamento
```

Quel codice è sparito. Quando un chiamante deve correggere il risultato di una funzione, la funzione sta restituendo la cosa sbagliata.

## Il principio, e la prova che ha funzionato

La regola che ne discende è che un costo ha un unico luogo di dichiarazione, il conto economico, e ogni altro foglio lo eredita attraverso una grandezza aggregata come il reddito operativo netto. Nessun foglio a valle somma o sottrae voci singole.

La verifica che il principio si sia sedimentato è arrivata mesi dopo, quando è stato aggiunto il costo figurativo del tempo dedicato alla gestione. La domanda posta è stata immediatamente quella giusta, cioè in quale conto economico entra, e la risposta ha richiesto una riga nel foglio Locazione e nessuna modifica altrove.

```python
riga_conf(
    "Costo figurativo del proprio tempo",
    "=-costo_tempo", "=-costo_tempo", "=-costo_tempo",
    "=-costo_tempo*coefficiente_tempo_breve",
)
```

Il Cash flow, le Metriche, gli Scenari, il foglio Rischio e la Comproprietà l'hanno recepito automaticamente, perché tutti leggono `noi_annuo` e `utile_locazione`.

## L'insidia residua: gli indici di riga

L'aggiunta di una riga al conto economico sposta tutte quelle sotto, e il codice che costruisce quel foglio calcola gli indici per offset da una base.

```python
riga_gest_r = base + 10
riga_noi = base + 11
riga_imp = base + 12
riga_utile = base + 13
```

È il punto più fragile del generatore. Non è stato astratto perché ogni astrazione provata rendeva meno leggibile la costruzione della tabella, ma va conosciuto: chi inserisce una riga in mezzo deve aggiornare i quattro offset, e il segnale che non l'ha fatto è un valore di sintesi che punta alla riga sbagliata, quindi un numero plausibile e falso. Il presidio è la doppia implementazione, che su questo tipo di errore è l'unico controllo che funziona.

## Come estendere il pattern

Una voce di costo ricorrente si aggiunge come riga del conto economico nel foglio Locazione e come campo di `ContoEconomico` in `calcoli.py`, aggiornando `costi_operativi`. Non si aggiunge mai come colonna del Cash flow né come sottrazione in un foglio a valle.

Dopo l'inserimento vanno riallineati gli offset degli indici di riga, rigenerato il workbook, e confrontato il riepilogo della riga di comando con i valori di sintesi del foglio: se i due divergono, l'offset è sbagliato.
