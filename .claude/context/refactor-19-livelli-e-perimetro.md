# 19. I livelli di accesso, e il perimetro che si definisce per sottrazione

> Deep-dive della voce 19 di [`studio-didattico-master.md`](studio-didattico-master.md). Riguarda `app/migrazioni/0002_gestori.sql`, `app/src/condiviso/ruoli.ts`, `app/src/condiviso/organizzazione.ts`, `app/src/server/autorizzazione.ts`, `app/src/server/membri.ts`, `app/src/server/piattaforma.ts`, `app/src/sezioni/amministrazione/` e `app/test/server/accessi.test.ts`. Il pattern che insegna vale ogni volta che un sistema acquista un secondo genere di autorità, e la regola sul come si scrive un presidio vale sempre.

## Due domande che il modello a tre ruoli non sapeva fare

Al 14 settembre 2026 l'applicazione conosceva tre ruoli, tutti dentro un'organizzazione: amministratore, membro e lettore, ordinati, dichiarati a ogni rotta, provati sul permesso e sul negato. Era un modello coerente e descriveva bene un'agenzia. Non descriveva un prodotto venduto a più agenzie, e la prova è che due domande pratiche non avevano risposta dentro l'applicazione.

Chi crea l'organizzazione di un cliente nuovo e le dà il suo primo amministratore? La risposta era un comando SQL, scritto nel passo 8 della procedura di messa in rete, con accanto la promessa di sostituirlo "quando ci sarà un pannello di amministrazione con un ruolo che la protegge".

Chi, dentro un'agenzia, invita un collega o gli revoca l'accesso? Qui la risposta era più imbarazzante, perché il ruolo che lo consentirebbe esisteva dal 7 settembre: mancavano le rotte. L'amministratore era un ruolo che poteva cancellare un immobile e non poteva decidere chi fosse un collega.

## La decisione che conta non è aggiungere un livello, è dargli un perimetro

Aggiungere un livello sopra i tre esistenti è l'unica mossa possibile e non è la parte interessante. La parte interessante è che cosa quel livello consente, e qui la forma naturale è anche quella sbagliata.

La forma naturale è che il livello più alto possa tutto. In pratica si scrive così, ed è una riga.

```ts
// La forma naturale, e la ragione per cui non e' qui.
const ruolo = (await appartenenza(db, organizzazione, chi.email))
  ?? (await eSuperamministratore(db, chi.email) ? "amministratore" : null);
```

Funziona, è comoda, e regala al fornitore la lettura silenziosa delle trattative di ogni cliente. Il giorno in cui un'agenzia chiedesse chi può vedere i suoi dati, la risposta onesta sarebbe "io, sempre, senza che resti traccia", e sarebbe una risposta che nessuna clausola contrattuale rende meno vera.

Il perimetro scelto si definisce quindi per sottrazione: il livello di piattaforma amministra le organizzazioni e le appartenenze, e non legge i dati che vivono dentro un'organizzazione. Le due famiglie non si sommano e non si implicano.

```ts
export type Requisito =
  | { tipo: "organizzazione"; ruoloMinimo: Ruolo }
  | { tipo: "piattaforma"; livelloMinimo: LivelloPiattaforma };
```

L'unione discriminata non è estetica. Con due campi entrambi facoltativi esisterebbe la forma in cui nessuno dei due è valorizzato, cioè una rotta registrata senza requisito, e il registro smetterebbe di essere la prova che non ne esistono. Con l'unione quella forma non compila.

## Il limite della difesa, detto per intero

Un superamministratore può aggiungersi da solo fra i membri di qualunque organizzazione. La protezione, quindi, non è impossibilità: è tracciabilità. L'aggiunta lascia una riga, e quella riga si può leggere.

Dirlo è parte della decisione e non una nota a margine, perché la differenza fra le due promesse è enorme e si confondono con facilità. La forma che renderebbe impossibile la lettura, cioè cifrare i dati con una chiave che il fornitore non possiede, è una scelta diversa, più costosa, e che questo progetto non ha preso. Scriverlo nel codice, nell'ADR e nelle prove serve a che nessuno, fra sei mesi, prometta a un cliente la cosa sbagliata in buona fede.

La prova che tiene in piedi il perimetro è una sola, ed è la più importante del file.

```ts
it("un superamministratore non vede gli immobili di un'organizzazione di cui non e' membro", async () => {
  await nominaGestore("io@piattaforma.invalid", "superamministratore");
  const elenco = await chiama("GET", "/api/organizzazioni/agenzia-a/immobili", "io@piattaforma.invalid");
  expect(elenco.status).toBe(404);
});
```

Fallirebbe se qualcuno aggiungesse la scorciatoia di sopra. Nessuna altra prova se ne accorgerebbe, perché tutte le altre passerebbero identiche: è esattamente il genere di difetto che ADR-024 descrive, cioè quello che con un'interfaccia di programmazione concede invece di negare.

## L'invariante che lo schema non sa esprimere

Un'organizzazione non deve restare senza amministratori. Non è una condizione su una riga ma su un insieme di righe, quindi la chiave esterna e il vincolo di controllo non la possono esprimere; e non la può garantire il browser, perché chiunque può parlare all'interfaccia di programmazione senza passarci.

Vive quindi nel server, e vive scritta una volta sola, perché le operazioni che possono violarla sono due.

```ts
async function restaSenzaAmministratori(ctx: Contesto, email: string): Promise<boolean> {
  const riga = await ctx.db.prepare("SELECT ruolo FROM membri WHERE organizzazione_id = ? AND email = ?")
    .bind(ctx.organizzazione, email).first<{ ruolo: string }>();
  if (!riga || riga.ruolo !== "amministratore") return false;
  return (await amministratori(ctx, email)) === 0;
}
```

Il caso concreto da cui nasce non è teorico: l'unico amministratore si retrocede a membro per vedere come si presenta l'applicazione con meno permessi, e poi non può più rimettersi amministratore, perché per farlo servirebbe il ruolo che si è appena tolto. È un vicolo cieco da cui si esce solo con una scrittura a mano nel database, cioè esattamente ciò che queste rotte tolgono di mezzo.

## Il bootstrap, che è il difetto più facile da introdurre

Il primo superamministratore, prima di creare qualunque organizzazione, non appartiene a nessuna. Il guscio, scritto il giorno prima, fermava chi non appartiene a nulla con una schermata che glielo spiega: quindi la sola persona che può creare un'organizzazione non avrebbe mai raggiunto il pannello con cui crearne una.

```tsx
if (!io || (io.organizzazioni.length === 0 && !io.livello)) {
  return <main className="avvio">...</main>;
}
```

Vale la pena isolare perché è una specie: un difetto di avviamento si manifesta una volta sola, all'inizio, quando non c'è ancora nessuno che possa accorgersene, e poi non si ripresenta più. Non lo trova l'uso, non lo trova una prova scritta guardando il codice che c'è: lo trova soltanto chiedersi che cosa succede la prima volta.

## Due contratti invece di uno

La schermata di amministrazione non lavora su un immobile: lavora su chi può vederli. Ha quindi un contratto proprio, e la tentazione era allargare quello delle sei aree per farcela stare.

Allargarlo avrebbe significato consegnare il cliente dell'interfaccia di programmazione anche alle sei aree, cioè disfare ADR-028 il giorno dopo averla presa: con il cliente in mano un'area può caricarsi l'elenco e scegliersi l'immobile per conto proprio, e ciò che un'area ha in mano finisce per usarlo. Due contratti distinti costano un'interfaccia in più e conservano il vincolo dove serve.

## Un difetto di accessibilità trovato da una prova

Due prove non trovavano un campo per nome, e la causa non era il test.

```tsx
<label>
  <span>Ruolo</span>
  <select .../>
  <small>{COSA_PUO_FARE[nuovoRuolo]}</small>
</label>
```

Quando un `label` avvolge il proprio controllo, il nome accessibile del controllo diventa tutto il testo contenuto: il campo "Ruolo" si chiamava "Ruolo Tutto quello che fa un membro, più invitare e revocare colleghi ed eliminare immobili." Non lo trovava la prova, e non lo trova nemmeno chi naviga con un lettore di schermo, che se lo sente leggere per intero a ogni tabulazione. Il testo di aiuto è uscito dall'etichetta per tutti i controlli condivisi.

Vale come regola generale: una prova che non trova un elemento per il suo nome sta quasi sempre dicendo che quel nome non è quello che credi, e il nome che una prova vede è lo stesso che sente chi non guarda lo schermo.

## Come si estende il pattern

Quando un sistema acquista un secondo genere di autorità, la domanda da porsi non è quale nome darle ma che cosa esattamente non consente. Un livello definito per addizione tende a crescere fino a poter tutto, e l'addizione successiva non si nota mai; un livello definito per sottrazione ha un confine che si può scrivere in una prova, e quella prova è l'unica cosa che lo tiene.

Quando il confine non è impossibilità ma tracciabilità, si dice. La differenza fra le due promesse è enorme, si confondono con facilità, e chi compra il prodotto ha diritto di sapere quale delle due gli si sta dando.

E quando si aggiunge un modo di entrare, ci si chiede che cosa succede la prima volta, quando non c'è ancora nessuno dentro. È l'unico momento in cui quel codice gira, ed è l'unico che nessun uso successivo esercita.
