# 15. L'autorizzazione in un posto solo, e la forma sbagliata resa impossibile

> Deep-dive della voce 15 di [`studio-didattico-master.md`](studio-didattico-master.md). Riguarda `app/src/server/autorizzazione.ts`, `app/src/server/indice.ts`, `app/migrazioni/0001_schema.sql` e le prove in `app/test/server/`. È la prima voce che nasce da codice di rete invece che da un foglio di calcolo, e il difetto che previene è il più costoso di tutto il progetto: il dato di un cliente visto da un altro.

## Il difetto, e perché cambia natura con la piattaforma

Lo studio dell'architettura aveva scelto Cloudflare al posto di Firebase, e aveva dichiarato il prezzo di quella scelta in una riga che vale rileggere: con un database che applica regole dichiarative una regola dimenticata nega l'accesso, mentre con un'interfaccia di programmazione una rotta che dimentica il controllo lo concede.

La differenza è tutta nel modo in cui l'errore si manifesta. Una regola dimenticata rompe l'applicazione: qualcuno apre una pagina, non vede i propri dati, e lo segnala nel giro di minuti. Una rotta senza controllo non rompe niente: tutto funziona, l'applicazione è più veloce del previsto, e il dato di un cliente è leggibile da un altro finché non lo scopre lui. È lo stesso genere di difetto della voce 8, dove una coordinata sbagliata produceva un numero plausibile invece di un errore, portato dal foglio di calcolo alla rete e moltiplicato per il fatto che qui i danneggiati sono terzi.

Il progetto ha già una risposta a questa forma di rischio, ed è quella delle voci 6 e 8: non raccomandare la forma giusta, rendere impossibile quella sbagliata.

## Come si scrive di solito, e perché è fragile

La forma naturale, quella che si trova in ogni esempio di Hono o di Express, è questa.

```typescript
app.get("/api/organizzazioni/:org/immobili", async (c) => {
  const chi = await identita(c.req.raw, c.env);
  if (!chi) return c.json({ errore: "non autenticato" }, 401);
  const org = c.req.param("org");
  const ruolo = await appartenenza(c.env.DB, org, chi.email);
  if (!ruolo) return c.json({ errore: "non trovata" }, 404);
  return elencaImmobili({ db: c.env.DB, organizzazione: org, ruolo, identita: chi });
});
```

Non c'è niente di sbagliato in queste righe. Il difetto è che sono righe, cioè qualcosa che va ricopiato in ogni rotta, e che la rotta seguente sarà scritta da qualcuno di fretta, magari da noi stessi fra tre mesi, partendo da un copia e incolla in cui la riga del ruolo si perde perché quella rotta "tanto è solo una lettura". Il rischio non è teorico: cinque rotte oggi diventano venti fra sei mesi, e la ventesima è quella che sbaglia.

C'è anche un difetto più sottile. In quella forma il gestore riceve `c`, cioè il contesto grezzo, e può leggere `c.req.param("org")` da solo: significa che una rotta può usare l'organizzazione chiesta dal chiamante senza che nessuno abbia verificato che gli appartenga. La verifica e l'uso sono separati, e ogni volta che una verifica e il suo uso sono separati qualcuno prima o poi userà senza verificare.

## Il salto: la rotta non si registra, si dichiara

La forma adottata sostituisce la registrazione diretta con una funzione che pretende il ruolo minimo come argomento e consegna un contesto già risolto.

```typescript
export function rotta(
  app: Hono<{ Bindings: Ambiente }>,
  metodo: Registrazione["metodo"],
  percorso: string,
  ruoloMinimo: Ruolo,
  gestore: Gestore,
): void {
  registro.push({ metodo, percorso, ruoloMinimo });
  app[metodo](percorso, async (c) => {
    const chi = await identita(c.req.raw, c.env);
    if (!chi) return c.json({ errore: "non autenticato" }, 401);
    const organizzazione = c.req.param("org");
    if (!organizzazione) return c.json({ errore: "organizzazione non indicata" }, 400);
    const ruolo = await appartenenza(c.env.DB, organizzazione, chi.email);
    if (!ruolo) return c.json({ errore: "organizzazione non trovata" }, 404);
    if (!ruoloSufficiente(ruolo, ruoloMinimo)) {
      return c.json({ errore: `serve il ruolo ${ruoloMinimo}, hai ${ruolo}` }, 403);
    }
    return gestore({ identita: chi, organizzazione, ruolo, db: c.env.DB }, c);
  });
}
```

Il file che monta l'applicazione diventa allora una mappa che si legge in dieci righe, dove il ruolo minimo di ogni rotta è visibile senza aprire niente.

```typescript
rotta(app, "get", IMMOBILI, "lettore", (ctx) => elencaImmobili(ctx));
rotta(app, "get", `${IMMOBILI}/:id`, "lettore", (ctx, c) => leggiImmobile(ctx, c.req.param("id")));
rotta(app, "post", IMMOBILI, "membro", async (ctx, c) => { ... });
rotta(app, "put", `${IMMOBILI}/:id`, "membro", async (ctx, c) => { ... });
rotta(app, "delete", `${IMMOBILI}/:id`, "amministratore", (ctx, c) => rimuoviImmobile(ctx, c.req.param("id")));
```

Tre proprietà rendono questa forma diversa da una raccomandazione. Il ruolo non è opzionale, perché è un parametro posizionale della funzione e TypeScript non compila senza. Il gestore riceve un contesto in cui l'organizzazione è già stata verificata, quindi non ha un percorso alternativo per ottenerla non verificata. E scrivere una rotta autorizzata senza passare da qui richiederebbe di chiamare `app.get` direttamente, che è un gesto visibile in una revisione, non una dimenticanza.

Resta un'eccezione, ed è dichiarata nel codice: la rotta che dice a una persona di quali organizzazioni fa parte non può passare dal registro, perché serve proprio a scoprirle e non esiste un'organizzazione su cui verificare l'appartenenza. Espone le sole appartenenze proprie e nessun dato altrui, e per questo l'eccezione è innocua. Un'eccezione dichiarata e motivata è diversa da una dimenticanza: la prima si legge, la seconda no.

## Due dettagli che sembrano minori e non lo sono

Il primo è la gerarchia dei ruoli. La forma sbagliata più comune è confrontare per uguaglianza, `if (ruolo !== "membro") nega`, che nega all'amministratore ciò che concede al membro. La gerarchia sta quindi in una tabella sola, e la funzione che la interroga è l'unica strada.

```typescript
const GERARCHIA: Record<Ruolo, number> = { lettore: 1, membro: 2, amministratore: 3 };
export function ruoloSufficiente(posseduto: Ruolo, richiesto: Ruolo): boolean {
  return GERARCHIA[posseduto] >= GERARCHIA[richiesto];
}
```

Il secondo è il codice di rifiuto, che è una decisione di sicurezza travestita da dettaglio. A chi non è membro si risponde quattrocentoquattro, cioè non esiste, e non quattrocentotre, cioè non ti è permesso. Un divieto esplicito confermerebbe che quell'organizzazione esiste, e su un prodotto venduto a più agenzie l'esistenza di un cliente è già un'informazione che non ci appartiene. Il divieto esplicito resta invece per chi è membro con un ruolo insufficiente, dove non rivela niente che il chiamante non sappia già, e dove un messaggio chiaro evita una segnalazione inutile.

## La difesa che non sta nel codice

L'autorizzazione decide chi può fare cosa. L'integrità decide che cosa può esistere, e sta nello schema, dove nessuna rotta distratta può aggirarla.

```sql
CREATE TABLE membri (
  organizzazione_id TEXT NOT NULL REFERENCES organizzazioni(id) ON DELETE CASCADE,
  email             TEXT NOT NULL,
  ruolo             TEXT NOT NULL CHECK (ruolo IN ('amministratore', 'membro', 'lettore')),
  aggiunto_il       TEXT NOT NULL,
  PRIMARY KEY (organizzazione_id, email)
);
```

Il vincolo di chiave esterna impedisce un'appartenenza a un'organizzazione che non esiste; il controllo sul ruolo impedisce di inventarne uno; la cancellazione a cascata garantisce che eliminando un cliente non restino i suoi immobili orfani in una tabella dove nessun filtro li troverà mai più. Sono tre difese che valgono anche il giorno in cui una rotta sbaglia, ed è la ragione per cui le prove le verificano esplicitamente invece di darle per scontate: tre test scrivono direttamente sul database e pretendono un rifiuto.

## Le prove, e l'ordine in cui sono scritte

La suite delle rotte è organizzata attorno a una domanda sola, cioè che due organizzazioni non si vedano, e ogni gruppo mette il caso negato prima di quello permesso. La ragione è che un test che verifica solo il permesso passa anche su un'applicazione che non controlla niente: è verde per la ragione sbagliata, ed è il modo in cui una suite di sicurezza finisce per non verificare la sicurezza.

Il caso che conta più di tutti è il tentativo diretto sull'identificativo, perché è quello che un attacco vero proverebbe: chi ha visto un identificativo altrove tenta di leggerlo passando dalla propria organizzazione.

```typescript
const diretto = await chiama("GET", `/api/organizzazioni/agenzia-b/immobili/${id}`, "capo@b.invalid");
expect(diretto.status).toBe(404);
```

Funziona perché la clausola sull'organizzazione non sta solo nel controllo che precede, ma dentro ogni singola interrogazione, comprese quelle di aggiornamento e cancellazione. Ripetere quella clausola in ogni `WHERE` sembra ridondante finché non si ricorda che il controllo che precede e l'interrogazione sono due righe diverse, e che qualcuno un giorno le riordinerà.

Il banco di prova, infine, ha due organizzazioni e tre persone con tre ruoli diversi, ed è il minimo che permetta di dimostrare qualcosa: con una sola organizzazione ogni prova passerebbe anche senza filtri, che è il modo più elegante di scrivere una suite che non prova niente.

## Come si estende il pattern

Quando si aggiunge una rotta si passa da `rotta()` e si dichiara il ruolo minimo; se la rotta non riguarda un'organizzazione, cioè se si è tentati di non passare di lì, quella è la domanda da porsi ad alta voce e la risposta va scritta in un commento come per la rotta sulle appartenenze. Si scrivono sempre due prove, quella del permesso e quella del rifiuto, e si scrive prima quella del rifiuto. Ogni interrogazione nuova porta la clausola sull'organizzazione dentro di sé, anche quando un controllo l'ha già verificata. E ogni vincolo che si può esprimere nello schema si esprime lì, perché una difesa nel database vale anche il giorno in cui il codice sbaglia.
