-- Schema iniziale. Tre tabelle e una regola sola: l'organizzazione e' la radice di tutto.
--
-- La scelta discende da ADR-025, cioe' dal fatto che lo strumento non e' personale ma un
-- prodotto che due clienti diversi useranno sugli stessi server. Se l'organizzazione
-- arrivasse dopo, ogni tabella andrebbe migrata e ogni interrogazione riscritta, e nel
-- frattempo esisterebbero righe senza proprietario che nessun filtro puo' recuperare.
--
-- La seconda scelta riguarda che cosa diventa colonna e che cosa resta documento. Sono
-- colonne i campi su cui si filtra, si ordina o si mostra un elenco; e' un documento JSON
-- tutto il resto delle ipotesi di valutazione, che solo il motore legge e che cambia con il
-- modello. Il criterio evita sia una tabella a quaranta colonne da migrare a ogni ipotesi
-- nuova, sia un documento unico su cui non si puo' fare una graduatoria.
--
-- La terza e' che non si salva nessun valore calcolato. Rendimenti, rata, prezzo massimo e
-- flussi si ricavano dagli input e non si conservano: un numero derivato messo in tabella
-- diventa falso in silenzio il giorno in cui cambia un'aliquota o si corregge una formula,
-- e questo progetto ha gia' pagato quel prezzo altrove. Il motore in TypeScript calcola una
-- valutazione completa in una frazione di millisecondo, quindi ricalcolare un elenco intero
-- nel browser costa meno di mantenere coerente una cache.

CREATE TABLE organizzazioni (
  id          TEXT PRIMARY KEY,
  nome        TEXT NOT NULL,
  creata_il   TEXT NOT NULL
);

-- L'appartenenza e' per posta elettronica e non per identificativo utente, perche'
-- l'identita' arriva da Access, che di una persona conosce l'indirizzo con cui ha
-- superato l'accesso. Un utente che non e' membro di nessuna organizzazione esiste,
-- entra, e non vede niente: e' il comportamento voluto.
CREATE TABLE membri (
  organizzazione_id TEXT NOT NULL REFERENCES organizzazioni(id) ON DELETE CASCADE,
  email             TEXT NOT NULL,
  ruolo             TEXT NOT NULL CHECK (ruolo IN ('amministratore', 'membro', 'lettore')),
  aggiunto_il       TEXT NOT NULL,
  PRIMARY KEY (organizzazione_id, email)
);

-- L'indice per posta serve alla domanda che si fa a ogni richiesta, cioe' di quali
-- organizzazioni fa parte chi sta chiamando.
CREATE INDEX membri_per_email ON membri (email);

CREATE TABLE immobili (
  id                TEXT PRIMARY KEY,
  organizzazione_id TEXT NOT NULL REFERENCES organizzazioni(id) ON DELETE CASCADE,
  titolo            TEXT NOT NULL,
  comune            TEXT NOT NULL DEFAULT '',
  indirizzo         TEXT NOT NULL DEFAULT '',
  prezzo            REAL NOT NULL DEFAULT 0,
  superficie_mq     REAL NOT NULL DEFAULT 0,
  categoria         TEXT NOT NULL DEFAULT 'A/2',
  rendita_catastale REAL NOT NULL DEFAULT 0,
  stato             TEXT NOT NULL DEFAULT 'da valutare',
  ipotesi           TEXT NOT NULL,
  creato_il         TEXT NOT NULL,
  aggiornato_il     TEXT NOT NULL
);

-- Ogni interrogazione di elenco filtra per organizzazione e ordina per ultima modifica:
-- l'indice segue quella forma, non l'ordine alfabetico delle colonne.
CREATE INDEX immobili_per_organizzazione ON immobili (organizzazione_id, aggiornato_il DESC);
