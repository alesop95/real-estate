# 02. Il denominatore dei rendimenti

> Deep-dive della voce 2 di `studio-didattico-master.md`. Riguarda `src/immobiliare/calcoli.py`, in particolare `CostoOperazione` e `metriche`, e le celle di sintesi del foglio Metriche.

## Il problema, che non è di codice

Ogni indicatore di rendimento è una frazione, e in una frazione il denominatore è una scelta di modello. La convenzione corrente, quella degli annunci e delle conversazioni, mette al denominatore il prezzo. Nessuno la dichiara, perché sembra ovvia.

Non lo è. Comprare un immobile a centoventimila euro non costa centoventimila euro: costa il prezzo più le imposte di trasferimento, la provvigione con IVA, l'onorario del notaio, gli oneri del mutuo e le voci accessorie. Sul caso di riferimento del progetto questi sono 11.557 euro, cioè il 9,6 per cento in più. Sono denaro uscito dal conto corrente che non tornerà al momento della rivendita.

Un rendimento calcolato sul prezzo è quindi gonfiato di quella percentuale, sempre nella stessa direzione. Un modello che sbaglia in modo sistematico è più pericoloso di uno rumoroso, perché non si autocorregge confrontando più casi: tutti i casi sono ottimistici nella stessa misura.

## La struttura che rende la scelta esplicita

Il costo non è un numero ma una struttura con le sue componenti, e le grandezze derivate sono proprietà calcolate.

```python
@dataclass
class CostoOperazione:
    """Fabbisogno di cassa complessivo per portare a termine l'acquisto."""

    prezzo: float
    imposte: ImposteAcquisto
    provvigione: float
    notaio_compravendita: float
    notaio_mutuo: float
    sostitutiva_mutuo: float
    istruttoria: float
    perizia: float
    altri_costi: float
    mutuo: float

    @property
    def costo_totale(self) -> float:
        """Prezzo piu' tutti i costi: e' il denominatore corretto dei rendimenti."""
        return self.prezzo + self.costi_accessori

    @property
    def esborso_iniziale(self) -> float:
        """Cassa che serve davvero al netto della parte finanziata dalla banca."""
        return self.costo_totale - self.mutuo
```

Il commento sulla proprietà non è decorativo: è il punto in cui la convenzione viene dichiarata, nell'unico posto dove qualcuno che modifica il codice la incontrerà.

## Due denominatori, non uno di compromesso

La tentazione, avendo capito il problema, è sceglierne uno migliore e usarlo ovunque. Sarebbe un errore diverso, perché le metriche rispondono a domande diverse.

```python
def metriche(costo: CostoOperazione, conto: ContoEconomico, rata_annua: float) -> Metriche:
    cash_flow = conto.utile_netto - rata_annua
    return Metriche(
        rendimento_lordo=conto.canone_potenziale / costo.prezzo if costo.prezzo else 0.0,
        rendimento_netto=conto.utile_netto / costo.costo_totale if costo.costo_totale else 0.0,
        cap_rate=conto.noi / costo.costo_totale if costo.costo_totale else 0.0,
        cash_on_cash=cash_flow / costo.esborso_iniziale if costo.esborso_iniziale else 0.0,
        ...
    )
```

Il rendimento lordo mantiene il prezzo al denominatore, deliberatamente: è il numero che si legge negli annunci, e lasciarlo confrontabile con quelli è più utile che correggerlo. Nella documentazione è dichiarato per quello che è, cioè uno strumento di scrematura e non di decisione.

Il rendimento netto e il cap rate usano il costo totale, perché misurano l'immobile. Il cash on cash usa l'esborso, perché misura l'operazione così com'è finanziata: è il rendimento del denaro proprio.

Tenere separati i due denominatori è ciò che rende leggibile la leva. Un immobile con cap rate del due per cento e cash on cash negativo non è una contraddizione: è la fotografia esatta di un bene che rende poco comprato con molto debito.

## Il corollario che è finito nel workbook

Se i costi accessori pesano abbastanza da cambiare il denominatore, la loro incidenza merita di essere un indicatore. Nel foglio Immobile è una riga con una regola di formattazione condizionale.

```python
riga_inc = r
r = S.campo(ws, r, "Incidenza dei costi sul prezzo", "=costi_accessori/prezzo", S.PERC,
            nota="Sotto il sei per cento e' un'operazione leggera, sopra il dieci va capito quale voce pesa.")
ws.conditional_formatting.add(
    f"B{riga_inc}",
    CellIsRule(operator="greaterThan", formula=["0.10"], fill=S.FILL_ATTENZIONE),
)
```

La soglia del dieci per cento non è arbitraria in senso stretto: sopra quella misura, su un immobile residenziale ordinario, una voce specifica sta pesando in modo anomalo, e nella pratica è quasi sempre la provvigione o l'imposta sostitutiva al due per cento sui mutui non prima casa. L'indicatore serve a mandare a cercarla.

## Come estendere il pattern

Ogni indicatore nuovo che sia una frazione deve dichiarare il proprio denominatore nel nome o nel commento, e la scelta deve rispondere a una domanda formulabile a parole. Se non si sa dire a quale domanda risponde, l'indicatore non serve.

Quando si aggiunge una voce di costo di ingresso, va aggiunta a `CostoOperazione` e non altrove: entra automaticamente in `costi_accessori`, quindi in `costo_totale`, quindi in tutti i rendimenti. È lo stesso principio della voce 5 del racconto, applicato ai costi una tantum invece che a quelli ricorrenti.
