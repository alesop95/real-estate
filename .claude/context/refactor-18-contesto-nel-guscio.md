# 18. Il contesto nel guscio, e la conservazione che smette di essere una raccomandazione

> Deep-dive della voce 18 di [`studio-didattico-master.md`](studio-didattico-master.md). Riguarda `app/src/condiviso/ipotesi.ts`, `app/src/condiviso/predefiniti.generate.ts`, `app/src/interfaccia/sezione.ts`, `app/src/interfaccia/bozza.ts`, `app/src/interfaccia/elenco.tsx`, `app/src/interfaccia/controlli.tsx`, `app/src/sezioni/costo/` e `tools/genera-motore.py`. Il pattern che insegna vale ogni volta che una seconda istanza trasforma una soluzione in un pattern da ricopiare.

## Il punto di partenza, che era corretto con un'area sola

Il 14 settembre l'area immobile era la sola schermata dell'applicazione, e possedeva tutto: caricava l'elenco degli immobili, teneva la selezione, chiamava il server per salvare, e leggeva e riscriveva le proprie due chiavi dentro il documento delle ipotesi conservando le altre. Nessuna di queste scelte era sbagliata. Erano tutte la scelta giusta per una schermata che non ne aveva accanto altre, ed erano tutte, senza eccezione, la scelta sbagliata per la seconda.

La regola generale che questa voce isola è che una soluzione e un pattern non sono la stessa cosa. Finché esiste un'istanza, il codice che risolve un problema è la soluzione di quel problema; dalla seconda in poi diventa un pattern, cioè qualcosa che qualcuno dovrà ricopiare correttamente. La domanda da farsi quando arriva la seconda istanza non è se il codice della prima sia buono, ma quale parte di esso, se ricopiata male, fallirebbe in silenzio.

## Che cosa sarebbe successo copiando

Quattro cose, in ordine crescente di danno.

L'elenco sarebbe stato caricato due volte, una per area, cioè due richieste al server per mostrare la stessa lista. È spreco, si vede, si corregge.

La selezione sarebbe vissuta dentro ciascuna area, quindi passando dall'area immobile a quella del costo ci si sarebbe trovati davanti a un'altra scheda, o a nessuna. È un difetto d'uso: si vede subito, e infastidisce.

La conservazione di ciò che l'area non conosce sarebbe stata una raccomandazione. La prima area la rispettava perché l'avevo scritta apposta; la quarta l'avrebbe dimenticata, e il salvataggio di un costo avrebbe cancellato le assunzioni della messa a reddito senza che nulla fallisse.

E infine l'azzeramento della bozza quando cambia l'immobile aperto, che è quella che fa il danno peggiore. Un'area che se lo dimentica mostra i dati del primo immobile sotto il nome del secondo, e chi salva sovrascrive il secondo con il primo. Non c'è errore, non c'è rifiuto, e su un prodotto multiproprietà il risultato è un dato di trattativa sostituito con un altro.

## Primo salto: la conservazione diventa l'unico modo di scrivere

La forma dell'intero documento delle ipotesi si dichiara in un posto solo, e con essa la sola funzione che produce un documento nuovo.

```ts
// app/src/condiviso/ipotesi.ts
export const SEZIONE = {
  regime: "regime_acquisto",
  verifiche: "verifiche",
  costo: "costo_operazione",
  finanziamento: "finanziamento",
  gestione: "gestione",
} as const;

export function conSezione(ipotesi: Ipotesi, chiave: ChiaveSezione, valore: object): Ipotesi {
  return { ...ipotesi, [chiave]: { ...grezza(ipotesi, chiave), ...valore } };
}
```

Due spargimenti e non uno, ed è la riga che conta. Il primo tiene le sezioni delle altre aree, e sarebbe l'unico se il problema fosse solo quello. Il secondo tiene i campi che un'altra versione dell'applicazione aveva scritto dentro questa sezione e che oggi nessuno legge: è la stessa perdita silenziosa, un piano più in basso, e si manifesta il giorno in cui due persone usano due versioni diverse sulla stessa scheda.

Un'area che volesse cancellare il lavoro delle altre dovrebbe costruire l'oggetto a mano, aggirando questa funzione, che è un gesto visibile in revisione. È lo stesso principio della voce 15, cioè rendere impossibile la forma sbagliata invece di raccomandare quella giusta, applicato a una struttura dati invece che a una rotta.

La proprietà si dichiara in una prova che si legge come l'enunciato, e la più importante è quella del giro completo, perché è l'unica che fallisce quando qualcuno, mesi dopo, aggiunge una chiave e dimentica la copia.

```ts
it("conserva anche i campi sconosciuti dentro la sezione che tocca", () => {
  const prima = { [SEZIONE.costo]: { altri_costi: 900, campo_futuro: "da tenere" } };
  const dopo = conSezione(prima, SEZIONE.costo, { altri_costi: 1_100 });
  expect(dopo[SEZIONE.costo]).toEqual({ altri_costi: 1_100, campo_futuro: "da tenere" });
});
```

## Una sezione con due autori, che non è un difetto se è dichiarata

Il finanziamento lo scrivono due aree. Quella del costo dell'operazione ne governa gli oneri iniziali, cioè importo, istruttoria, perizia e notaio dell'atto di mutuo, perché appartengono alla domanda "quanto serve per comprare"; quella del finanziamento ne governerà tasso e durata, che governano la rata, cioè una domanda diversa. Sono campi della stessa sezione, divisi per uso e non per struttura.

Una sezione con due autori è una fonte di guai solo quando ciascuno dei due la descrive a modo proprio: allora il primo che salva cancella i campi che l'altro conosceva e lui no. Con la forma dichiarata una volta in `condiviso/ipotesi.ts`, entrambi leggono la stessa sezione tipizzata per intero e la riscrivono per intero, e nessun campo si perde perché nessuno dei due ne ignora l'esistenza. La prova lo dice esplicitamente.

```ts
it("conserva i campi del finanziamento che non mostra", () => {
  const immobile = immobileFinto({
    [SEZIONE.finanziamento]: { ...FINANZIAMENTO_PREDEFINITO, tasso_annuo: 0.041, durata_anni: 30 },
  });
  const scheda = conFinanziamento(schedaDa(immobile), "importo", 120_000);
  const sezione = versoInvio(scheda, immobile).ipotesi[SEZIONE.finanziamento] as Record<string, unknown>;
  expect(sezione.tasso_annuo).toBe(0.041);
  expect(sezione.durata_anni).toBe(30);
});
```

## Secondo salto: i predefiniti non si ricopiano nemmeno loro

Scrivendo la lettura tollerante servivano i valori con cui riempire un campo assente: il tasso, la durata, l'istruttoria, il canone. Sono le stesse cifre che le dataclass di `calcoli.py` portano come predefiniti, e ricopiarle sarebbe stato il lavoro di due minuti e la garanzia che un predefinito cambiato in Python restasse vecchio nel browser, senza che nulla fallisse.

Il presidio che dal 7 settembre emette i parametri fiscali per introspezione guadagna perciò una quinta uscita, che emette i predefiniti delle dataclass di ingresso.

```python
INGRESSI = {
    "ACQUIRENTE_PREDEFINITO": ("Acquirente", "Acquirente"),
    "FINANZIAMENTO_PREDEFINITO": ("Finanziamento", "Finanziamento"),
    "GESTIONE_PREDEFINITA": ("Gestione", "Gestione"),
}
```

`Immobile` non compare, e l'assenza è informazione: il suo campo `prezzo` non ha un predefinito per scelta, perché una valutazione senza prezzo non è una valutazione incompleta ma una valutazione che non esiste, e dargliene uno qui significherebbe inventare il numero da cui dipende ogni altro.

Restano fuori dalla generazione tre valori, cioè i predefiniti degli argomenti di `costoOperazione`, perché sono predefiniti di funzione e non campi di una dataclass, e l'introspezione non li vede. Non si trascrivono lo stesso: si ricavano da dove il progetto li dichiara comunque, cioè la provvigione tipica fra i parametri e l'onorario del notaio come punto medio dell'intervallo registrato in `parametri.py`, che è precisamente il numero che il motore usa. La coincidenza non è lasciata all'occhio, ed è questo il punto.

```ts
it("i costi predefiniti coincidono con quelli che il motore usa quando non glieli si passa", () => {
  const senza = costoOperazione(IMMOBILE, acquirente, FINANZIAMENTO_PREDEFINITO);
  const con = costoOperazione(IMMOBILE, acquirente, FINANZIAMENTO_PREDEFINITO,
    COSTI_PREDEFINITI.provvigione_aliquota,
    COSTI_PREDEFINITI.notaio_compravendita,
    COSTI_PREDEFINITI.altri_costi);
  expect(con).toEqual(senza);
});
```

La regola generale: quando una cosa non si può generare, non la si trascrive, la si deriva da dove è già dichiarata e si scrive la prova che la derivazione regge. Una costante ricavata da un'altra e presidiata da un'asserzione è una fonte sola; la stessa costante ricopiata è due.

## Terzo salto: il contesto appartiene al guscio

Un'area riceve tre cose e non ne cerca nessuna.

```ts
// app/src/interfaccia/sezione.ts
export interface ProprietaSezione {
  immobile: Immobile | null;
  ruolo: Ruolo;
  salva: (corpo: ImmobileInviato) => Promise<Immobile>;
  rimuovi: (() => Promise<void>) | null;
}
```

Non riceve il cliente, ed è deliberato: con il cliente in mano un'area potrebbe caricarsi l'elenco, scegliersi l'immobile e parlare al server per conto proprio, che è esattamente ciò che produrrebbe sei elenchi caricati sei volte e sei selezioni che si perdono cambiando schermata. L'immobile aperto è una proprietà della sessione di lavoro e non di una vista, come nel workbook il foglio Immobile alimenta tutti gli altri.

`rimuovi` è null quando non c'è nulla di aperto, e non una funzione che non fa niente. La differenza è che con null il compilatore obbliga l'area a distinguere, mentre con una funzione inerte il gesto resterebbe offerto e il compito di ricordarsene tornerebbe a chi scrive la schermata.

## Il ciclo di bozza, e la trappola che ci ho trovato dentro

Le cinque cose che ogni area rifarebbe attorno alla propria materia stanno in un hook solo.

```ts
export function useBozza<S>(
  immobile: Immobile | null,
  daImmobile: (immobile: Immobile | null) => S,
  versoInvio: (bozza: S, immobile: Immobile | null) => ImmobileInviato,
  salvaSulServer: (corpo: ImmobileInviato) => Promise<Immobile>,
): Bozza<S>
```

Due dettagli meritano di essere scritti perché sono il genere di cosa che si riscopre a caro prezzo.

Il primo è su che cosa si osserva per decidere quando ripartire. Non l'oggetto, che cambia identità a ogni ricarica dell'elenco e butterebbe via ciò che si sta scrivendo; e non il solo identificativo, perché dopo un salvataggio l'immobile è lo stesso ma il contenuto no, e la bozza deve ripartire da ciò che il server ha davvero accettato. Si osserva l'impronta, cioè identificativo e data di ultima modifica insieme.

Il secondo l'ho scoperto scrivendo la prova e non leggendo il codice: il salvataggio fa arrivare un immobile nuovo, quindi l'impronta cambia, quindi l'effetto che riazzera la bozza spegneva il messaggio di conferma appena mostrato. L'utente avrebbe visto un lampo e nessuna conferma. La difesa è ricordare l'impronta dell'ultimo salvataggio riuscito e non azzerare il messaggio quando le due coincidono.

```ts
const salvato = await salvaOra.current(corpo);
appenaSalvato.current = impronta(salvato);
setMessaggio(`Salvato alle ${quando(salvato.aggiornato_il)}.`);
```

## Lo stato che non può esistere non si rappresenta

L'area del costo non può lavorare su un immobile che non c'è, perché i suoi numeri partono dal prezzo, che appartiene all'altra schermata. La forma naturale sarebbe riempire il componente di controlli sul nulla; quella scelta divide invece il componente in due, e quello interno riceve un immobile che esiste per il compilatore e non solo per convinzione.

```tsx
export function SezioneCosto({ immobile, ruolo, salva }: ProprietaSezione) {
  if (!immobile) return <section className="scheda">...</section>;
  return <CostoAperto immobile={immobile} ruolo={ruolo} salva={salva} />;
}
```

È la stessa idea del `rimuovi` a null: uno stato che non ha senso non si rappresenta con un valore neutro, si rappresenta con un tipo che lo esclude, e ciò che resta dentro non ha bisogno di difendersi.

## Un confine dichiarato invece che difeso

L'area del costo legge il regime di acquisto e non lo scrive: prima casa, prezzo-valore e venditore impresa cambiano il numero più grande della sua tabella, perché decidono fra IVA e imposta di registro, e pure appartengono all'area immobile. La tentazione di metterne una copia modificabile anche qui è forte ed è sbagliata, perché un valore modificabile da due schermate è un valore di cui nessuno sa più dove si cambia.

La soluzione non è nascondere l'informazione ma dichiararne la provenienza: il regime si mostra accanto al risultato, con scritto dove si cambia. Un'interfaccia che mostra un numero senza dire da dove viene costringe chi la usa a indovinare, e chi indovina sbaglia.

## Come si estende il pattern

Quando arriva la seconda istanza di qualcosa, non ci si chiede se il codice della prima sia buono: ci si chiede quale sua parte, ricopiata male, fallirebbe in silenzio. Quella parte va spostata dove non si possa ricopiare male, e le altre si possono lasciare dove sono.

Una regola che tutte le istanze devono rispettare non si documenta, si rende l'unica strada. Se esiste un modo di scrivere che la viola e non fallisce, prima o poi qualcuno lo prenderà, e non sarà per distrazione: sarà perché quel modo era più corto.

Una costante che non si può generare si deriva da dove è già dichiarata, e la derivazione si presidia con una prova. Trascriverla è l'unica opzione da escludere sempre.

E l'interfaccia non ha diritti che il modello non le dia: un'area riceve ciò che le serve e nient'altro, perché ciò che ha in mano finirà per usarlo.
