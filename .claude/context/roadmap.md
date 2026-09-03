---
generated-from-commit: a0b3420
generated-from-branch: main
generated-date: 2026-09-01
covers-paths:
  - src/**
last-verified-commit: a0b3420
---

# Direzione

## Principio di selezione

Ogni aggiunta deve rispondere a una domanda che oggi resta senza risposta, non aggiungere una funzione perché è possibile. Lo strumento vale finché resta leggibile: un modello che nessuno riesce più a verificare produce numeri che nessuno dovrebbe usare.

## Prossimo, se serve

Le tre voci che stavano qui sono chiuse al 1 settembre 2026, e restano registrate perché la roadmap serve anche a ricordare cosa si è deciso di fare e non solo cosa manca. La suite di test automatici esiste e conta sessantuno test in due file. Il confronto fra più immobili è il foglio Confronto immobili, alimentato dal registro annunci, che dal 1 settembre porta il blocco delle quotazioni OMI di zona e il regime di acquisto dichiarato per riga. Il tasso variabile con scenario di risalita è il percorso a gradini del foglio Simulatore mutuo, con la misura del rialzo presa dalla serie storica dell'Euribor invece che dall'intuizione, secondo ADR-015 e la voce 11 dello studio didattico.

Non resta quindi nulla in questa sezione, e questo è un fatto sullo stato del progetto e non un invito a riempirla. Le voci qui sotto vanno promosse solo se una domanda concreta le rende necessarie, secondo il principio di selezione in testa a questo documento.

## Più avanti, se il progetto lo giustifica

Ammortamento della surroga. L'estinzione parziale anticipata è invece modellata dal 28 agosto, con il versamento una tantum e le due modalità di imputazione del rimborso; la surroga no, e richiederebbe di modellare due piani in sequenza con il debito residuo del primo come capitale del secondo, più i costi di trasferimento, che sono nulli per legge ma non nella pratica dei tempi. È la voce più vicina a essere utile, perché un rialzo del tasso simulato con il percorso a gradini rende immediata la domanda successiva, cioè quanto convenga surrogare a quel punto del piano.

Riconoscimento semantico dei duplicati fra portali, per cui il cliente del modello locale espone già il calcolo dell'embedding ma manca la procedura che lo applica al registro.

Serie storica delle quotazioni OMI di una zona, per distinguere una zona che si rivaluta da una che si svuota. I dati storici esistono nel mirror open data fino al 2018 e sarebbero sufficienti a mostrare una tendenza decennale.

Una versione parallela per l'agente immobiliare, o per chi lavora con lui. Lo stesso motore di calcolo servirebbe un caso d'uso rovesciato: non un compratore che valuta pochi immobili a fondo, ma un professionista che ne seguono molti in superficie e deve ricordarsi di richiamare le persone. Servirebbero un'anagrafica dei clienti con le loro preferenze di ricerca, l'accoppiamento fra immobili e clienti interessati, e un promemoria con scadenze sui contatti da riprendere. La parte di calcolo, cioè imposte, mutuo, rendimento e confronto, resterebbe identica e riusabile; cambierebbero l'unità di lavoro, che diventa la relazione invece dell'immobile, e il vincolo sui dati, perché un'anagrafica di clienti è un trattamento di dati personali di terzi con basi giuridiche e obblighi che questo progetto, essendo personale, oggi non ha. Va quindi tenuta come progetto separato che condivide i moduli di dominio, non come opzione di questo.

## Deliberatamente fuori perimetro

La ristrutturazione come progetto, con computo metrico, detrazioni edilizie e stato di avanzamento lavori. È una materia a sé che raddoppierebbe la superficie del modello, ed è stata esclusa esplicitamente in fase di definizione dell'obiettivo. Resta dentro la sola ristrutturazione periodica di fine ciclo, come costo ricorrente.

Le aste giudiziarie erano fuori perimetro e non lo sono più dal 31 agosto 2026: il perimetro è stato ampliato su richiesta, e la decisione che lo dichiarava è superata da ADR-012. Restano fuori le vendite nella liquidazione giudiziale, che seguono il codice della crisi d'impresa, le aste con incanto ormai residuali e i beni diversi dalle abitazioni.

Qualunque forma di prelievo automatico che aggiri le protezioni dei portali. Non è una questione di difficoltà tecnica ma di perimetro: si veda ADR-004.
