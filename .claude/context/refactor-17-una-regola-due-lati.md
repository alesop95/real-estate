# 17. La stessa regola dalle due parti, scritta una volta

> Deep-dive della voce 17 di [`studio-didattico-master.md`](studio-didattico-master.md). Riguarda `app/src/condiviso/immobile.ts`, `app/src/condiviso/ruoli.ts`, `app/src/condiviso/verifiche.generate.ts`, `src/immobiliare/verifiche.py`, `tools/genera-motore.py` e `app/src/sezioni/immobile/modello.ts`. Il pattern che insegna vale per qualunque confine fra due lati che debbano applicare la stessa regola, e la regola di conservazione che chiude la voce vale per qualunque documento scritto da più autori.

## Il punto di partenza, che era corretto finché c'era un lato solo

Al 13 settembre 2026 l'applicazione web aveva un Worker con cinque rotte autorizzate, cinquantadue prove verdi e nessuna interfaccia. In quello stato `src/server/immobili.ts` conteneva tre cose insieme: la forma di un immobile, la regola che la valida e le interrogazioni al database. Era la scelta giusta, perché l'unico chiamante era una prova automatica e un modulo in più sarebbe stato astrazione senza secondo caso.

La fase tre cambia la premessa, non il codice. Nasce un modulo che compila quei campi e li invia, e da quel momento la forma esiste in due posti: nel Worker, che la pretende, e nell'interfaccia, che la produce. La domanda non è se le due copie divergeranno, è quando, e soprattutto in che direzione.

## Perché la divergenza è del genere peggiore

Le due copie possono divergere in due versi, e non sono simmetrici.

Se l'interfaccia diventa più severa del server, l'utente vede un errore su un valore che sarebbe stato accettato. È un fastidio, si scopre subito, e qualcuno lo segnala.

Se l'interfaccia diventa più permissiva, l'utente compila un modulo che gli dice tutto bene, preme salva, e riceve un rifiuto dal server su un campo che il modulo non gli aveva contestato. Il messaggio arriva dopo un giro di rete, spesso in una forma pensata per un programma e non per una persona, e il modulo non sa quale campo evidenziare perché per lui erano tutti giusti. È lo stesso carattere del difetto della voce 8, cioè un guasto che non fallisce dove lo si guarda.

C'è un terzo caso, che è quello che ha deciso la forma. Il server assegna valori predefiniti a ciò che non riceve: categoria `A/2`, stato `da valutare`. Se l'interfaccia ne scrive di propri, l'immobile creato dal modulo e quello creato da una chiamata diretta nascono diversi, e nessuno dei due è sbagliato. Il predefinito, quindi, non è un dettaglio dell'interfaccia: è parte della forma, e sta dove sta la forma.

## Il salto: il confine non è il posto dove duplicare

La regola si scrive una volta e la importano entrambi.

```ts
// app/src/condiviso/immobile.ts
export function validaImmobile(corpo: unknown): { errori: string[]; valore?: ImmobileInviato } {
  ...
}

export function immobileNuovo(): ImmobileInviato {
  return { titolo: "", comune: "", ..., categoria: "A/2", stato: "da valutare", ipotesi: {} };
}
```

Il Worker la applica per decidere.

```ts
// app/src/server/immobili.ts
import { validaImmobile } from "../condiviso/immobile";

export async function creaImmobile(ctx: Contesto, corpo: unknown, id: string, adesso: string) {
  const { errori, valore } = validaImmobile(corpo);
  if (!valore) return Response.json({ errori }, { status: 422 });
  ...
}
```

La sezione la applica per non far fare un giro di rete inutile.

```tsx
// app/src/sezioni/immobile/sezione.tsx
const corpo = versoInvio(scheda, ipotesiOriginali);
const { errori: problemi } = validaImmobile(corpo);
if (problemi.length) {
  setErrori(problemi);
  return;
}
```

Quel che va capito, e che è la parte che si dimentica dopo tre mesi, è che le due applicazioni non hanno lo stesso statuto. Quella del Worker è la difesa: chiunque può parlare all'interfaccia di programmazione senza passare dalla pagina, quindi un controllo fatto solo nel browser non è un controllo, è un suggerimento. Quella della sezione è cortesia. Condividere la regola non toglie la difesa: toglie la seconda scrittura della stessa regola.

La prova che questo tiene non è nel numero dei test ma nella loro ripartizione. Il contenuto della regola si prova una volta sola, in Node, su una funzione pura; che il Worker la applichi davvero è già provato dentro il runtime di Cloudflare contro un D1 vero. Provarla due volte nello stesso modo non aggiungerebbe niente, mentre provarla nei due modi diversi copre sia la regola sia il collegamento.

## Lo stesso pattern, secondo caso: i ruoli

L'interfaccia deve nascondere il pulsante di salvataggio a chi ha ruolo di sola lettura. La forma naturale, in un componente, è una riga come `ruolo === "amministratore" || ruolo === "membro"`, che funziona.

Funziona e sbaglia esattamente come sbaglia il server quando confronta per uguaglianza, ed è il difetto che la voce 15 aveva già chiuso da un lato: il giorno in cui nasce un ruolo nuovo, o cambia il nome di uno esistente, la gerarchia va aggiornata in due posti e uno dei due resterà indietro. Se resta indietro il browser, si nasconde un pulsante a chi ne aveva diritto, oppure lo si mostra a chi non ne ha: nel secondo caso il server nega, quindi nessun dato esce, ma l'utente vede un rifiuto dove si aspettava un salvataggio.

```ts
// app/src/condiviso/ruoli.ts
const GERARCHIA: Record<Ruolo, number> = { lettore: 1, membro: 2, amministratore: 3 };

export function ruoloSufficiente(posseduto: Ruolo, richiesto: Ruolo): boolean {
  return GERARCHIA[posseduto] >= GERARCHIA[richiesto];
}
```

Da qui in avanti la domanda "questa persona può scrivere?" si fa con la stessa funzione dalle due parti, e un ruolo nuovo si aggiunge in un posto solo.

## Lo stesso pattern, terzo caso: un confine fra due linguaggi

L'area immobile mostra le trenta verifiche da chiudere prima di firmare. Le stesse trenta esistevano già, come lista letterale dentro il metodo che costruisce il foglio Checklist del workbook. Ricopiarle in TypeScript sarebbe stato il lavoro di dieci minuti e la garanzia che, al primo aggiornamento normativo, l'applicazione e il foglio mostrerebbero due elenchi di verifiche legali diversi: il genere di divergenza che si scopre davanti a un notaio.

Qui però i due lati non sono due moduli dello stesso linguaggio, sono Python e TypeScript, e un modulo condiviso non esiste. La risposta era già nel progetto: il presidio che dal 7 settembre emette i parametri fiscali per introspezione dalle dataclass di `parametri.py` è lo stesso che può emettere un catalogo. Il catalogo esce dal metodo del generatore Excel e diventa un modulo proprio, e `tools/genera-motore.py` guadagna una quarta uscita.

```python
# src/immobiliare/verifiche.py
VERIFICHE: tuple[Verifica, ...] = (
    ("Prima della proposta", "Visura catastale aggiornata e planimetria depositata",
     "L'atto è nullo se manca la dichiarazione di conformità fra planimetria e stato di fatto. ...",
     "Agenzia delle Entrate, servizi catastali", "Acquirente o tecnico", "da fare", ""),
    ...
)
```

```python
# tools/genera-motore.py
DESTINAZIONE_VERIFICHE = Path("app/src/condiviso/verifiche.generate.ts")
```

Il foglio Checklist importa il catalogo, l'applicazione riceve la sua traduzione, e `--check` dice che è scaduta appena qualcuno tocca la fonte. Non servono vettori di riscontro, perché qui non c'è un calcolo da verificare: serve che il testo sia lo stesso, e lo si ottiene generandolo.

Una nota sui nomi, perché contraddice in apparenza una regola del progetto. Nel file generato il campo `perché` diventa `percheConta`, senza accento. La regola tipografica vale sulla prosa; qui si tratta di un identificatore, cioè della stessa distinzione per cui gli strumenti di tipografia mascherano gli argomenti delle macro di composizione prima di operare. Il testo delle voci, che è prosa, conserva ogni accento.

L'estrazione ha anche prodotto una piccola correzione che vale citare come metodo. Scrivendo il modulo avevo elencato a mano le fasi del percorso, e ne mancava una: l'elenco scritto accanto al catalogo era già la seconda fonte di verità che il modulo esisteva per evitare. È stato sostituito da una funzione che le ricava dall'ordine di prima comparsa, e due prove lo presidiano nelle due direzioni, cioè che ogni voce dichiari una fase dell'elenco e che ogni fase dell'elenco abbia almeno una voce.

## Il documento scritto da più autori, e la regola di conservazione

Lo schema tiene in colonne i campi su cui si filtra e si ordina, e in un documento JSON tutto il resto delle ipotesi di valutazione. È la forma giusta, perché evita di migrare una tabella ogni volta che il modello cresce. Introduce però un problema che con le colonne non esisterebbe: quel documento lo scrivono sei aree diverse, e ciascuna ne conosce solo la propria parte.

La forma naturale è che un'area, salvando, scriva ciò che sa.

```ts
// La forma sbagliata: salva le proprie chiavi e cancella quelle di tutti gli altri.
ipotesi: {
  regime_acquisto: { ...scheda.regime },
  verifiche: { ...scheda.verifiche },
}
```

Non produce nessun errore. Produce che chi apre l'area del finanziamento il giorno dopo trova i valori predefiniti al posto delle proprie assunzioni, senza che nulla glielo dica. È lo stesso carattere del riferimento per coordinata di cella della voce 8: un guasto che non fallisce.

La regola è che ciò che non si conosce si conserva.

```ts
export function versoInvio(scheda: Scheda, ipotesiOriginali: Ipotesi = {}): ImmobileInviato {
  return {
    ...
    ipotesi: {
      ...ipotesiOriginali,
      [CHIAVE_REGIME]: { ...scheda.regime },
      [CHIAVE_VERIFICHE]: { ...scheda.verifiche },
    },
  };
}
```

Ne discende la simmetrica, sulla lettura: ciò che non si riconosce non rompe. Un documento è scritto da versioni diverse dell'applicazione nel tempo, quindi la lettura sostituisce con il predefinito ciò che non riconosce, e scarta gli esiti di verifiche che il catalogo non contiene più, invece di pretendere una forma perfetta e rendere illeggibile un immobile salvato il mese prima.

Le due proprietà sono coperte da prove che dichiarano l'enunciato, e la più importante delle tre è quella del giro completo.

```ts
it("un giro completo non perde e non inventa nulla", () => {
  const primo = versoInvio(schedaDa(immobileFinto(originali)), originali);
  const secondo = versoInvio(schedaDa({ ...immobileFinto(primo.ipotesi) }), primo.ipotesi);
  expect(secondo.ipotesi).toEqual(primo.ipotesi);
});
```

## Un difetto trovato dalla prova, e la ragione per cui era prevedibile

L'area mostra le imposte di trasferimento mentre si digita, e la prima scrittura dell'anteprima leggeva la base imponibile così.

```ts
imponibile: baseImponibileRegistro(immobile, acquirente),
```

La prova sul venditore impresa l'ha respinta: attesi centottantamila, trovati settantunomilaseicentodieci. Il prezzo-valore è una regola dell'imposta di registro, e quando il venditore è un'impresa la vendita è soggetta a IVA, quindi la base torna a essere il prezzo pattuito. `baseImponibileRegistro` risponde correttamente alla domanda del registro e non sa dell'IVA: chiamarla lì mostrava il valore catastale accanto a un'IVA calcolata sul prezzo, cioè due numeri entrambi giusti nel proprio contesto e incoerenti fra loro.

La correzione è una riga, e la lezione è più larga di essa. Il motore aveva già deciso quella base e la restituiva dentro il proprio esito; l'anteprima l'ha ricalcolata invece di leggerla. È la stessa regola che questo progetto applica alle formule del workbook, cioè non ricalcolare ciò che un'altra parte ha già stabilito, portata dentro l'interfaccia.

```ts
// La base si prende da `imposte` e non da `baseImponibileRegistro`, e la differenza non e'
// di stile.
imponibile: imposte.imponibile,
```

## Come si estende il pattern

Quando nasce una regola che due lati devono applicare, la domanda da farsi non è dove scriverla ma se i due lati condividono un linguaggio. Se lo condividono, la regola sta in un modulo che entrambi importano, e la prova del contenuto si scrive una volta sola mentre l'applicazione si prova dove ha una conseguenza. Se non lo condividono, la regola sta dove sta la fonte e si genera verso l'altro lato, con un controllo di scadenza che fallisce quando la fonte cambia.

Quando una struttura dati ha più autori, ogni autore scrive le proprie chiavi e conserva tutte le altre, e legge tollerando ciò che non conosce. Le due proprietà si dichiarano in due prove, di cui una dev'essere il giro completo: è l'unica che fallisce quando qualcuno, mesi dopo, aggiunge una chiave e dimentica la copia.

E quando un'interfaccia mostra un numero, quel numero si legge dall'esito del motore, non si ricalcola con la funzione che sembra giusta. Le funzioni che rispondono a domande vicine hanno nomi vicini, e la prova che le distingue è la sola cosa che separa un'anteprima esatta da una plausibile.
