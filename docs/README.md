# Indice della documentazione

> Che cos'è ciascun file di questa cartella, per chi è scritto, e quando si apre. Si legge per primo quando non si sa dove cercare. I documenti sono quindici e non c'è ragione di leggerli tutti: ognuno risponde a una domanda diversa, e la tabella qui sotto serve a capire quale.

## La regola per orientarsi

I documenti si dividono per **tipo di domanda**, non per argomento, e questa è la chiave di tutta la cartella.

Chi si chiede **come si fa** una cosa apre il manuale operativo. Chi si chiede **perché un numero è quel numero** apre una scheda di dominio. Chi si chiede **come è costruito** apre la guida tecnica o la trattazione matematica. Chi deve **spiegarlo a qualcun altro** apre una delle due guide d'uso.

Tenerli separati è una scelta e non un accumulo: la stessa cosa spiegata in due posti diverge, e il modo di evitarlo è che ogni documento risponda a una domanda sola e rimandi agli altri per il resto.

## I quattro percorsi di lettura

**Non ho mai usato lo strumento e devo cominciare.** `da-zero.md`, sette passi dall'ambiente vuoto alla prima valutazione. Poi `guida-non-tecnica.md` per capire il workbook mentre lo si compila.

**Devo usare un comando e non ricordo come.** `manuale-operativo.md`, che copre ogni comando con ogni opzione, ogni campo del registro, ogni foglio e la diagnostica degli errori.

**Devo spiegarlo a chi compra con me.** `guida-per-il-socio.md`, l'unico documento scritto per essere letto da fuori: si manda come file e si legge da solo.

**Devo intervenire sul codice, o verificare un calcolo.** `guida-tecnica(catena-calcolo-e-normativa).md` per l'architettura e il riferimento di ogni voce, `matematica/matematica-finanziaria.tex` per le derivazioni, `metodo-e-metriche.md` per le scelte metodologiche.

## I quindici documenti

### Guide d'uso, per chi usa lo strumento

| File | Per chi | Quando si apre |
|---|---|---|
| `da-zero.md` | chi parte senza niente installato | La prima volta, e mai più. Sette passi dall'ambiente vuoto alla prima valutazione completa. |
| `manuale-operativo.md` | chi usa i comandi | Ogni volta che serve un comando, un'opzione, il significato di un campo del registro o di un errore. È il documento del *come*, e contiene i due diagrammi del percorso. |
| `guida-non-tecnica.md` | chi usa solo il workbook | Mentre si compila. Accompagna foglio per foglio in linguaggio comune, in forma narrativa. |
| `guida-per-il-socio.md` | chi compra insieme e non ha il progetto | Da mandare a un'altra persona. Ripete quanto serve invece di rimandare altrove, e porta le cinquantuno celle di input in tabella più un giro su un immobile reale. |

### Schede di dominio, per il perché di un numero

Sono la parte di conoscenza del progetto: spiegano la materia, non il codice. Si aprono quando si tocca la materia che descrivono, mai tutte insieme.

| File | Che cosa spiega |
|---|---|
| `fiscalita-acquisto.md` | Imposte di trasferimento nei quattro casi, prezzo-valore, agevolazione prima casa, imposta sostitutiva del mutuo, detrazione degli interessi, plusvalenza, IMU. |
| `fiscalita-locazione.md` | I quattro regimi di tassazione del canone a confronto, le novità 2026 sulle locazioni brevi, gli oneri della registrazione, i rischi che il modello non cattura. |
| `due-diligence.md` | Le verifiche per fase, conformità catastale e urbanistica, Salva Casa, clausole della proposta, condominio, garanzie del costruttore. Sta sotto il foglio Checklist. |
| `perizia-pre-acquisto.md` | I documenti da farsi consegnare in trattativa: otto famiglie, chi li rilascia, la norma che li rende dovuti, il costo, come si chiedono. Sta sotto il foglio Dossier tecnico. |
| `aste-immobiliari.md` | La vendita giudiziaria: i quattro rischi che il prezzo deve pagare, come si legge un avviso, quanto sconto serve. Sta sotto il foglio Asta. |
| `comprare-in-piu-persone.md` | Comunione o società, maggioranze, scioglimento, fisco pro quota, quando serve davvero una società. Sta sotto il foglio Comproprietà. |
| `raccolta-annunci.md` | Il registro degli annunci, i vincoli dell'acquisizione automatica, le quotazioni OMI, il riconoscimento dei duplicati. |

### Metodo e costruzione, per chi verifica

| File | Che cosa contiene |
|---|---|
| `metodo-e-metriche.md` | Le scelte metodologiche: quale denominatore usa un rendimento e perché, che cosa dice ciascuna metrica, i limiti dichiarati. Si apre quando si vuole contestare un criterio, non un numero. |
| `guida-tecnica(catena-calcolo-e-normativa).md` | Architettura, catena di calcolo, riferimento di ogni voce con formula, nome definito e norma. Più i punti di intervento e come si verifica. Si apre prima di toccare il codice. |
| `matematica/matematica-finanziaria.tex` | La trattazione completa: ogni formula derivata da zero, con un capitolo iniziale che spiega la notazione a chi non è abituato alle formule e una lettura a parole di ogni formula. Si compila in un PDF di trentadue pagine. |
| `fonti.md` | Da dove viene ogni dato: cosa fornisce ciascuna fonte, dove atterra nel codice o nel workbook, con quale grado di verifica, e le lacune dichiarate. Si apre prima di fidarsi di un numero, e obbligatoriamente prima di modificare un parametro fiscale. |

## Che cosa non sta qui

La memoria di progetto sta sotto `.claude/memory/`: `index.md` dà lo stato corrente, `progress.md` è il work-log in ordine cronologico inverso, `decisions.md` è il registro delle decisioni con la motivazione di ciascuna. Le schede di contesto tecnico stanno sotto `.claude/context/`, insieme al pacchetto `studio-didattico` che racconta perché una scelta è fatta così, prima di rifarla diversamente.

Il materiale personale, cioè il dossier delle trattative e i riferimenti di terzi, sta sotto `_notes/`, non è versionato e non va pubblicato.

## Due sovrapposizioni note

Vanno dichiarate, perché chi legge due documenti che dicono la stessa cosa si chiede quale sia quello giusto.

`guida-non-tecnica.md` e `guida-per-il-socio.md` **hanno lo stesso destinatario**, cioè una persona che deve usare o capire il workbook senza toccare il codice, e coprono lo stesso terreno: i colori delle celle, i fogli uno per uno, che cosa il modello non sa. Differiscono nella forma, narrativa la prima e tabellare la seconda, e la seconda aggiunge un giro completo su un immobile reale. La seconda è nata dopo, per una richiesta specifica, senza verificare che la prima esistesse già: è una duplicazione da chiudere, e la chiusura sensata è tenerne una sola.

`manuale-operativo.md` e `guida-tecnica(catena-calcolo-e-normativa).md` si toccano sulla verifica del workbook e sui punti di intervento. Qui la separazione regge, perché il primo dice quali comandi lanciare e il secondo perché il codice è fatto così, ma il confine va sorvegliato.
