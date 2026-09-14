# -*- coding: utf-8 -*-
"""Catalogo delle verifiche da chiudere prima di firmare.

Sta in un modulo proprio e non dentro il generatore del workbook per la ragione che
vale in tutto questo progetto: dal 14 settembre 2026 le stesse trenta voci servono a
due destinatari, cioè il foglio Checklist e l'area immobile dell'applicazione web, e
un catalogo scritto due volte è un catalogo che dopo il primo aggiornamento esiste in
due versioni diverse senza che nessuno se ne accorga. Qui è scritto una volta; il
foglio lo importa e `tools/genera-motore.py` lo emette in TypeScript per il browser,
esattamente come fa con i parametri fiscali.

Ogni voce porta sette campi, nell'ordine: la fase del percorso in cui la verifica si
colloca, che cosa si verifica, perché conta, il documento o la fonte su cui la si
chiude, chi materialmente la esegue, lo stato iniziale e le note. Lo stato iniziale
non è "da fare" per tutte: le voci della nuova costruzione e la portabilità del mutuo
nascono non applicabili, perché riguardano casi che non tutti gli acquisti
attraversano, e farle nascere aperte produrrebbe un contatore di verifiche mancanti
che segnala un problema inesistente.
"""

from __future__ import annotations

#: Gli stati ammessi, nello stesso ordine della convalida a elenco del foglio. Due di
#: essi dicono la stessa cosa, cioè "non applicabile" e la sua abbreviazione, e la
#: duplicazione è ereditata dal foglio: si toglierà quando si migreranno i dati, non
#: adesso, perché cambiarla qui renderebbe non più leggibile un workbook già compilato.
STATI = ("da fare", "in corso", "fatto", "non applicabile", "n.a.")

#: fase, verifica, perché conta, documento o fonte, chi la fa, stato iniziale, note.
Verifica = tuple

VERIFICHE: tuple[Verifica, ...] = (
    ("Prima della proposta", "Visura catastale aggiornata e planimetria depositata",
     "L'atto è nullo se manca la dichiarazione di conformità fra planimetria e stato di fatto. Non ogni difformità però produce nullità: la Cassazione distingue le irregolarità significative dai difetti minori.",
     "Agenzia delle Entrate, servizi catastali", "Acquirente o tecnico", "da fare", ""),
    ("Prima della proposta", "Conformità urbanistica ed edilizia",
     "È la corrispondenza fra lo stato di fatto e tutti i titoli edilizi della storia del fabbricato. È cosa diversa dalla conformità catastale e va verificata separatamente: è la difformità che blocca davvero la vendita e il mutuo.",
     "Accesso agli atti in Comune, titoli edilizi", "Tecnico di parte", "da fare", ""),
    ("Prima della proposta", "Stato legittimo e tolleranze costruttive",
     "Il decreto Salva Casa ha ampliato le tolleranze dell'articolo 34-bis del DPR 380/2001 per le difformità realizzate prima del 24 maggio 2024, e ha dato valore probatorio alle dichiarazioni del tecnico. Sapere in quale regime ricade l'immobile cambia il costo della regolarizzazione.",
     "Relazione del tecnico, DL 69/2024 convertito in legge 105/2024", "Tecnico di parte", "da fare", ""),
    ("Prima della proposta", "Visura ipotecaria ventennale",
     "Rivela ipoteche, pignoramenti, sequestri, diritti di terzi, servitu' e trascrizioni pregiudizievoli. L'ipoteca del venditore va cancellata prima o contestualmente al rogito.",
     "Conservatoria dei registri immobiliari", "Notaio o visurista", "da fare", ""),
    ("Prima della proposta", "Atto di provenienza e continuità delle trascrizioni",
     "Dice come il venditore è diventato proprietario. Una provenienza per donazione è un rischio concreto per il mutuo, perché l'immobile è aggredibile dai legittimari lesi.",
     "Atto notarile di acquisto o successione", "Notaio", "da fare", ""),
    ("Prima della proposta", "Quotazioni OMI della zona e comparabili reali",
     "Ancora il prezzo a un riferimento verificabile invece che alla richiesta dell'agenzia. Le quotazioni OMI sono semestrali, gratuite e pubbliche.",
     "Osservatorio del mercato immobiliare, Agenzia delle Entrate", "Acquirente", "da fare", ""),
    ("Prima della proposta", "Spese condominiali e liberatoria dell'amministratore",
     "L'acquirente risponde in solido con il venditore delle spese dell'anno in corso e di quello precedente. Vanno letti anche i verbali delle ultime assemblee, per i lavori deliberati e non ancora pagati.",
     "Consuntivi, riparti, verbali, regolamento", "Amministratore", "da fare", ""),
    ("Nella proposta", "Condizione sospensiva o risolutiva legata al mutuo",
     "Senza clausola, se la banca non delibera si perde la caparra e si deve comunque la provvigione. Con la sospensiva il contratto non produce effetti finché la banca non eroga; con la risolutiva il contratto si scioglie se la condizione non si avvera entro il termine.",
     "Testo della proposta, articoli 1353 e seguenti del codice civile", "Acquirente e legale", "da fare", ""),
    ("Nella proposta", "Provvigione dell'agenzia legata all'avveramento della condizione",
     "La provvigione matura alla conclusione dell'affare. Se la condizione non si avvera e nulla è stato pattuito, l'agenzia può comunque pretenderla: va escluso espressamente per iscritto.",
     "Testo della proposta", "Acquirente e legale", "da fare", ""),
    ("Nella proposta", "Termine per la stipula del definitivo",
     "Senza un termine, l'obbligo di concludere resta indeterminato e diventa difficile far valere l'inadempimento della controparte.",
     "Testo della proposta", "Acquirente e legale", "da fare", ""),
    ("Nella proposta", "Stato di fatto e di diritto e garanzia di libertà da gravami",
     "Va scritto che l'immobile è trasferito libero da ipoteche, pesi, vincoli, pegni e da qualsivoglia gravame, e che il venditore garantisce la conformità urbanistica e catastale.",
     "Testo della proposta", "Acquirente e legale", "da fare", ""),
    ("Nella proposta", "Natura delle somme versate, acconto o caparra confirmatoria",
     "La caparra confirmatoria da' diritto al doppio in caso di inadempimento del venditore; l'acconto no. La differenza va scritta, non lasciata implicita.",
     "Articolo 1385 del codice civile", "Acquirente e legale", "da fare", ""),
    ("Mutuo", "Farsi consegnare il PIES di ogni banca interpellata",
     "Il Prospetto Informativo Europeo Standardizzato è il documento personalizzato che la banca deve consegnare gratuitamente prima che il cliente sia vincolato, ed è l'unico modo per confrontare offerte diverse sulla stessa base. Contiene anche una tabella di ammortamento esemplificativa.",
     "Banca d'Italia, guida al mutuo ipotecario", "Acquirente", "da fare", ""),
    ("Mutuo", "Usare i sette giorni di riflessione sull'offerta vincolante",
     "Ricevuta l'offerta vincolante il consumatore ha diritto ad almeno sette giorni di riflessione, durante i quali l'offerta resta ferma per la banca e può essere accettata in qualsiasi momento. Sono giorni per confrontare, non per aspettare.",
     "Banca d'Italia, guida al mutuo ipotecario", "Acquirente", "da fare", ""),
    ("Mutuo", "Verificare che il tasso non sia usurario",
     "Al momento della firma il tasso non può superare la soglia d'usura, determinata sul tasso effettivo globale medio pubblicato trimestralmente. È un controllo di un minuto che si fa una volta sola.",
     "Banca d'Italia, tassi effettivi globali medi", "Acquirente", "da fare", ""),
    ("Mutuo", "Confrontare la polizza della banca con il mercato",
     "La polizza incendio e scoppio è obbligatoria ma il cliente può presentarne una reperita altrove, purchè di protezione equivalente, e la banca deve accettarla. Se si accetta quella proposta dalla banca, il cliente ha diritto di sapere quanta provvigione la compagnia paga alla banca stessa.",
     "Banca d'Italia, guida al mutuo ipotecario", "Acquirente", "da fare", ""),
    ("Mutuo", "Controllare la propria posizione in Centrale dei Rischi",
     "L'accesso ai propri dati è gratuito e si fa online. Una segnalazione dimenticata o una pratica ancora aperta presso un mediatore creditizio pesa sulla delibera: l'incarico di mediazione si può revocare per iscritto, e con esso decade la richiesta in corso.",
     "Banca d'Italia, accesso alla Centrale dei Rischi", "Acquirente", "da fare", ""),
    ("Mutuo", "Sapere che la portabilità è gratuita per legge",
     "Trasferire il mutuo a un'altra banca, cioè la surroga, è per legge senza spese né penali, e non richiede il consenso della banca di partenza. In pratica se ne ottiene una nella vita del mutuo: le banche identificano il surrogatore seriale e negano la delibera, e le surroghe hanno spesso spread più alti proprio per questo.",
     "Banca d'Italia, guida al mutuo ipotecario", "Acquirente", "n.a.", ""),
    ("Prima del rogito", "Attestato di prestazione energetica",
     "È obbligatorio allegarlo all'atto e va indicato negli annunci. Determina anche la classe da cui partire per ogni valutazione di adeguamento futuro.",
     "APE in corso di validità", "Venditore", "da fare", ""),
    ("Prima del rogito", "Dichiarazione di conformità o rispondenza degli impianti",
     "Per gli impianti realizzati dopo il 2008 serve la dichiarazione di conformità ai sensi del DM 37/2008; per i più vecchi può bastare la dichiarazione di rispondenza rilasciata da un tecnico abilitato.",
     "Dichiarazione dell'installatore o del tecnico", "Venditore", "da fare", ""),
    ("Prima del rogito", "Trascrizione del preliminare se i tempi sono lunghi",
     "La trascrizione ai sensi dell'articolo 2645-bis protegge da ipoteche e pignoramenti iscritti dopo la firma e da' privilegio sul credito restitutorio. Ha un costo, e su tempi lunghi o su venditori a rischio lo vale.",
     "Preliminare in forma notarile", "Notaio", "da fare", ""),
    ("Prima del rogito", "Verifica dei requisiti prima casa e delle dichiarazioni in atto",
     "Residenza nel Comune o impegno a trasferirla entro diciotto mesi, assenza di altra abitazione nel Comune, assenza di altra prima casa agevolata in Italia salvo rivendita entro due anni. In comunione legale entrambi i coniugi devono intervenire in atto e rendere le dichiarazioni.",
     "Guida dell'Agenzia delle Entrate sulle agevolazioni prima casa", "Notaio", "da fare", ""),
    ("Prima del rogito", "Opzione prezzo-valore richiesta espressamente",
     "Va chiesta in atto e comporta la tassazione sul valore catastale, il blocco dell'accertamento di valore e la riduzione del trenta per cento dell'onorario notarile.",
     "Articolo 1 comma 497 legge 266/2005", "Notaio", "da fare", ""),
    ("Nuova costruzione", "Fideiussione a garanzia degli acconti",
     "Il decreto legislativo 122/2005 impone al costruttore di consegnare una fideiussione bancaria o assicurativa a garanzia di tutte le somme versate prima del trasferimento. La tutela non è rinunciabile e ogni patto contrario è nullo.",
     "Decreto legislativo 122/2005", "Notaio", "n.a.", ""),
    ("Nuova costruzione", "Polizza indennitaria decennale postuma",
     "Copre i danni materiali da rovina totale o parziale e da gravi difetti costruttivi per dieci anni dall'ultimazione. Va consegnata all'atto e gli estremi vanno indicati nel rogito.",
     "Decreto legislativo 122/2005, articolo 4", "Notaio", "n.a.", ""),
    ("Nuova costruzione", "Permesso di costruire, agibilità e accatastamento",
     "La banca non delibera prima dell'accatastamento definitivo. Vanno verificati il titolo edilizio, il collaudo, l'agibilita' e la corrispondenza fra progetto approvato e stato realizzato.",
     "Titoli edilizi e certificato di agibilità", "Tecnico di parte", "n.a.", ""),
    ("Nuova costruzione", "Capitolato, extracapitolato e cronoprogramma",
     "Distinguere cosa è incluso nel prezzo da cosa è extra evita la sorpresa più cara dell'acquisto sulla carta. Il cronoprogramma con le penali per il ritardo va scritto.",
     "Contratto di appalto e capitolato", "Acquirente", "n.a.", ""),
    ("Se si affitta", "Codice identificativo nazionale e adempimenti della locazione breve",
     "Dal 2026 il CIN va indicato in ogni annuncio e comunicazione. Servono inoltre la comunicazione alla questura degli alloggiati, i dispositivi di sicurezza obbligatori e il rispetto dei regolamenti comunali e condominiali.",
     "Ministero del turismo, banca dati strutture ricettive", "Proprietario", "n.a.", ""),
    ("Se si affitta", "Accordo territoriale e attestazione, se canone concordato",
     "Il canone concordato richiede l'attestazione di conformità rilasciata da un'associazione firmataria dell'accordo territoriale del Comune, senza la quale i benefici fiscali decadono.",
     "Accordo territoriale del Comune", "Proprietario", "n.a.", ""),
    ("Se si affitta", "Verifica del regolamento condominiale",
     "Un regolamento contrattuale può vietare la locazione turistica o l'uso diverso dall'abitazione. Va letto prima di costruire un piano su affitti brevi.",
     "Regolamento condominiale trascritto", "Proprietario", "n.a.", ""),
)


def fasi() -> tuple[str, ...]:
    """Le fasi nell'ordine in cui compaiono nel catalogo, senza ripetizioni.

    Si ricava invece di essere scritta, e la ragione non è l'eleganza: una tupla
    scritta a mano accanto a un catalogo che cresce è la seconda fonte di verità che
    questo modulo esiste per evitare, e sbaglierebbe in silenzio dimenticando una
    fase aggiunta in fondo. L'ordine di prima comparsa è informazione: un'interfaccia
    che ordinasse alfabeticamente metterebbe il rogito prima della proposta.
    """
    viste: list[str] = []
    for voce in VERIFICHE:
        if voce[0] not in viste:
            viste.append(voce[0])
    return tuple(viste)
