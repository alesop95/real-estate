-- I livelli di piattaforma: chi amministra il prodotto, che non e' chi lo usa.
--
-- Fino al 14 settembre 2026 l'applicazione conosceva tre livelli, tutti dentro
-- un'organizzazione: amministratore, membro e lettore. Bastavano a descrivere un'agenzia e non
-- bastano a descrivere un prodotto venduto a piu' agenzie, perche' lasciavano fuori una domanda
-- che qualcuno deve pur poter fare: chi crea l'organizzazione di un cliente nuovo, e chi le da'
-- il suo primo amministratore. Fino a oggi la risposta era "si inserisce a mano nel database",
-- che va bene una volta e non va bene mai piu'.
--
-- La scelta che conta non e' l'esistenza di questa tabella ma il suo perimetro, ed e' registrata
-- in ADR-029: un livello di piattaforma amministra le organizzazioni e le appartenenze, e non
-- legge i dati che vivono dentro un'organizzazione. Un superamministratore che voglia vedere gli
-- immobili di un cliente deve aggiungersi fra i suoi membri, e quell'aggiunta lascia una riga
-- che si puo' leggere. Non e' impossibilita', e' tracciabilita': la differenza va detta, perche'
-- chi compra il prodotto ha diritto di sapere quale delle due gli si sta promettendo.
--
-- L'appartenenza e' per posta elettronica come in `membri`, e per la stessa ragione: l'identita'
-- arriva da Access, che di una persona conosce l'indirizzo con cui ha superato l'accesso.

CREATE TABLE gestori (
  email       TEXT PRIMARY KEY,
  -- Due livelli e non uno, e la ragione non e' la previsione di un bisogno futuro. Un livello
  -- solo non e' una gerarchia: e' un valore booleano travestito, e la prima volta che servisse
  -- distinguere fra chi guarda e chi cambia andrebbe migrata la tabella. I due si distinguono su
  -- cio' che questo registro consente: `supporto` legge quali organizzazioni esistono e chi ne
  -- fa parte, `superamministratore` le crea, le rimuove e ne nomina gli amministratori.
  livello     TEXT NOT NULL CHECK (livello IN ('supporto', 'superamministratore')),
  aggiunto_il TEXT NOT NULL
);
