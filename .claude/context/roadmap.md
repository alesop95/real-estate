---
generated-from-commit: da assegnare al primo commit
generated-from-branch: main
generated-date: 2026-08-28
covers-paths:
  - src/**
last-verified-commit: da assegnare al primo commit
---

# Direzione

## Principio di selezione

Ogni aggiunta deve rispondere a una domanda che oggi resta senza risposta, non aggiungere una funzione perche' e' possibile. Lo strumento vale finche' resta leggibile: un modello che nessuno riesce piu' a verificare produce numeri che nessuno dovrebbe usare.

## Prossimo, se serve

Suite di test automatici sotto `tests/`, che congeli il caso di riferimento e le verifiche di dominio elencate in `dev-testing.md`. E' la sola voce che considero dovuta a prescindere: senza, ogni aggiornamento annuale dei parametri e' un salto nel buio.

Confronto fra piu' immobili sullo stesso foglio, cioe' una colonna per immobile con le metriche affiancate, alimentato dal registro annunci. Oggi il workbook valuta un immobile alla volta e il confronto si fa a mano; e' il limite che si sente per primo quando gli annunci da valutare superano la decina.

Tasso variabile con scenario di risalita, che oggi si simula solo con la tabella di sensibilita' sul tasso. Servirebbe una proiezione con Euribor che evolve, sul modello del calcolatore mutuo di Coletti che porta la serie storica.

## Piu' avanti, se il progetto lo giustifica

Ammortamento della surroga e dell'estinzione parziale anticipata, che oggi non sono modellati e che sono decisioni ricorrenti nella vita di un mutuo.

Riconoscimento semantico dei duplicati fra portali, per cui il cliente del modello locale espone gia' il calcolo dell'embedding ma manca la procedura che lo applica al registro.

Serie storica delle quotazioni OMI di una zona, per distinguere una zona che si rivaluta da una che si svuota. I dati storici esistono nel mirror open data fino al 2018 e sarebbero sufficienti a mostrare una tendenza decennale.

## Deliberatamente fuori perimetro

La ristrutturazione come progetto, con computo metrico, detrazioni edilizie e stato di avanzamento lavori. E' una materia a se' che raddoppierebbe la superficie del modello, ed e' stata esclusa esplicitamente in fase di definizione dell'obiettivo. Resta dentro la sola ristrutturazione periodica di fine ciclo, come costo ricorrente.

Le aste giudiziarie, che seguono regole proprie su perizia, custode, decreto di trasferimento e liberazione dell'immobile, e che meriterebbero uno strumento separato.

Qualunque forma di prelievo automatico che aggiri le protezioni dei portali. Non e' una questione di difficolta' tecnica ma di perimetro: si veda ADR-004.
