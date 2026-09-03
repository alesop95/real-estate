# 06. Il contratto posizionale fra registro e foglio

> Deep-dive della voce 6 di [`studio-didattico-master.md`](studio-didattico-master.md). Riguarda `src/immobiliare/annunci.py`, funzione `esporta_in_excel`, il metodo `foglio_annunci` di `excel_builder.py`, e il test `test_esportazione_scrive_nelle_colonne_giuste`.

## Tre elenchi che devono restare paralleli

Il registro degli annunci è una dataclass. Il foglio Annunci è una tabella con intestazioni. L'esportazione scrive per posizione di colonna, perché deve saltare le tre colonne che contengono formule e non vanno mai sovrascritte.

```python
ordine = [
    "id", "data", "stato", "fonte", "agenzia", "contatto", "link", "comune",
    "provincia", "zona_omi", "indirizzo", "tipologia", "destinazione_uso",
    "nuova_costruzione", "data_consegna", "mq", "prezzo_richiesto",
    "prezzo_obiettivo", None, "quotazione_omi_min", "quotazione_omi_max", None,
    "rendita_catastale", "categoria", "piano", "classe_energetica",
    "spese_condominio_anno", "canone_atteso_mese", None, "punteggio", "note",
]
colonne_calcolate = {i for i, campo in enumerate(ordine, start=1) if campo is None}
```

I `None` sono le colonne di formula, e derivare `colonne_calcolate` da `ordine` invece di scriverlo a mano elimina una delle tre liste da tenere allineate. Restano però l'ordine dei campi della dataclass, questa lista, e l'elenco delle intestazioni nel generatore: tre elenchi in due file, legati solo dall'attenzione.

Un campo aggiunto in mezzo alla dataclass senza aggiornare la lista fa scivolare tutto di una posizione. Il file si apre, le celle contengono valori, i prezzi finiscono nella colonna delle note. Nessun errore, nessun avviso, un foglio che sembra funzionare.

## Il test che esegue il contratto invece di documentarlo

```python
def test_esportazione_scrive_nelle_colonne_giuste(tmp_path=None):
    """Esporta un annuncio noto e rilegge le celle una per una."""
    cartella = Path(tmp_path) if tmp_path else Path(tempfile.mkdtemp())
    destinazione = cartella / "esportazione.xlsx"
    E.genera(str(destinazione))

    registro = A.Registro(cartella / "annunci.csv")
    registro.aggiungi(A.Annuncio(
        id="house_9", stato="visitata", fonte="immobiliare.it", agenzia="Agenzia Prova",
        contatto="333 1112223", link="https://esempio.invalid/1", comune="Comune di esempio",
        provincia="XX", indirizzo="via Prova 1", tipologia="bilocale",
        destinazione_uso="abitazione", nuova_costruzione="SI", data_consegna="2027-06",
        mq=60, prezzo_richiesto=100_000, prezzo_obiettivo=93_000,
        rendita_catastale=500, categoria="A/3", canone_atteso_mese=520, note="prova",
    ))
    A.esporta_in_excel(registro, str(destinazione))

    ws = load_workbook(destinazione)["Annunci"]
    ...
    atteso = {
        1: "house_9", 3: "visitata", 5: "Agenzia Prova", 6: "333 1112223",
        8: "Comune di esempio", 9: "XX", 12: "bilocale", 13: "abitazione",
        14: "SI", 15: "2027-06", 16: 60, 17: 100_000, 18: 93_000,
        21: None, 23: 500, 24: "A/3", 28: 520, 31: "prova",
    }
    for colonna, valore in atteso.items():
        effettivo = ws.cell(row=riga, column=colonna).value
        assert effettivo == valore, f"colonna {colonna}: atteso {valore!r}, trovato {effettivo!r}"

    # Le tre colonne calcolate devono essere rimaste formule, non valori.
    for colonna in (19, 22, 29):
        contenuto = ws.cell(row=riga, column=colonna).value
        assert isinstance(contenuto, str) and contenuto.startswith("=")
```

Il valore del test sta nella scelta dei dati: ogni campo ha un valore diverso e riconoscibile, così uno scivolamento di una posizione produce un confronto che fallisce con un messaggio che dice esattamente quale colonna contiene cosa. Un test con valori tutti uguali, o con molti campi vuoti, sarebbe passato anche con l'errore presente.

La riga `21: None` verifica il caso opposto e più insidioso, cioè che una colonna non compilata resti vuota. È quella che ha trovato il difetto seguente.

## Il difetto che il test ha trovato al primo colpo

L'esportazione scriveva così.

```python
ws.cell(row=riga, column=colonna, value=valore if valore != 0 else None)
```

Sembra corretto e non lo è, per un comportamento della libreria che non è documentato in modo evidente: il metodo `cell()` assegna il valore solo se non è nullo.

```python
def cell(self, row, column, value=None):
    ...
    cell = self._get_cell(row, column)
    if value is not None:
        cell.value = value
    return cell
```

Passare `None` non azzera la cella: la lascia com'era. Poiché il foglio generato contiene una riga di esempio e le esportazioni successive riscrivono le stesse righe, un campo lasciato vuoto ereditava in silenzio il valore dell'annuncio che occupava prima quella riga. Il test ha fallito con `colonna 21: atteso None, trovato 1450`, dove 1450 era la quotazione OMI massima della riga di esempio.

La correzione è di una riga, e il commento serve a impedire che qualcuno la riscriva nella forma comoda.

```python
# L'assegnazione va fatta sull'attributo e non passando `value` a
# `cell()`, perche' quella scorciatoia salta l'assegnazione quando il
# valore e' None e lascerebbe in cella il contenuto precedente: un
# campo azzerato non si ripulirebbe e l'annuncio esportato erediterebbe
# in silenzio il dato di quello che occupava prima la riga.
ws.cell(row=riga, column=colonna).value = valore if valore != 0 else None
```

## Il secondo test, sul contratto strutturale

Accanto al test di comportamento c'è un test di forma, che confronta il numero di colonne con il numero di campi e verifica che le tre di formula stiano dove devono.

```python
campi_registro = [f.name for f in fields(A.Annuncio)]
# Tre colonne del foglio sono calcolate e non hanno un campo corrispondente.
assert len(titoli) == len(campi_registro) + 3
for atteso, effettivo in ((19, "Prezzo al mq"), (22, "Scarto su OMI"), (29, "Rendimento lordo")):
    assert titoli[atteso - 1] == effettivo
```

Fallisce appena qualcuno aggiunge un campo alla dataclass senza toccare il foglio, con un messaggio che dice quante colonne ci sono e quanti campi, quindi indirizza subito alla causa.

## Come estendere il pattern

Aggiungere una colonna al registro richiede tre modifiche coordinate: il campo in `Annuncio`, la voce in `ordine` dentro `esporta_in_excel`, la coppia nome e larghezza in `colonne` dentro `foglio_annunci`. I test falliscono se una delle tre manca, ed è il motivo per cui esistono.

Più in generale: ogni volta che due moduli si accordano su un ordine posizionale senza un tipo che lo imponga, quel contratto va reso eseguibile da un test che scrive dati distinguibili e li rilegge. Un commento che dice *tenere allineato con* non è un presidio, è un desiderio.
