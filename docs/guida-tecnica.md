# Guida tecnica

> Per chi mette le mani nel modello: come è costruito, dove si interviene, e il significato finanziario e fiscale di ogni voce con il riferimento normativo puntuale. I testi degli articoli citati sono stati verificati sul corpus normativo locale del progetto `legal-consultant`, che espone la legislazione italiana consolidata vigente; l'URN riportato è quello con cui l'articolo si recupera. La versione per chi vuole solo usare il file è in `guida-non-tecnica.md`.

## Come è fatto

Tre livelli separati, e la separazione è la ragione per cui il modello si può verificare. I parametri normativi stanno in `src/immobiliare/parametri.py` e non calcolano nulla. Le funzioni di dominio stanno in `src/immobiliare/calcoli.py`, prendono numeri e restituiscono numeri, non conoscono Excel e non leggono file. Il generatore `src/immobiliare/excel_builder.py` scrive il workbook traducendo le stesse regole in formule vive.

Le regole quindi esistono due volte, e questo è voluto: far girare lo stesso caso sul motore Python e sul workbook e confrontare i risultati è il controllo che intercetta l'errore di trascrizione, che nei fogli di calcolo è il più frequente e il meno visibile. Sul caso di riferimento le due implementazioni coincidono su tutte le grandezze di sintesi.

I riferimenti fra fogli passano sempre per nomi definiti, mai per indirizzi di cella, così una formula si legge come `prezzo * reg_prima` e non come `Immobile!$B$15`, e resta valida se una riga si sposta.

## Comandi

```
python tools/valuta.py excel --con-annunci
python tools/valuta.py riepilogo --prezzo 120000 --rendita 450 --mutuo 90000 --canone 500
python tools/valuta.py tassi --tasso 0.032 --mutuo 90000 --durata 25
python tools/valuta.py omi cerca --comune "NOME DEL COMUNE"
python tools/valuta.py annunci elenca
python -m pytest tests
powershell -NoProfile -ExecutionPolicy Bypass -File tools\verifica-excel.ps1
```

Il workbook si rigenera da zero a ogni esecuzione: non è un archivio e non va usato come tale. Lo stato persistente vive in `data/annunci.csv` e nel codice.

## La catena di calcolo, in ordine

Il costo dell'operazione si costruisce in cinque passaggi, ciascuno dei quali è una cella con un nome. Prima si decide se l'agevolazione spetta davvero, perché da lì dipende sia l'aliquota sia il moltiplicatore catastale. Poi si determina la base imponibile. Poi le quattro imposte. Poi i costi accessori. Infine il costo totale e l'esborso.

L'ordine non è cosmetico: metterlo al contrario produce l'errore che il modello aveva prima dei test, cioè applicare il moltiplicatore 110 dell'agevolazione a una categoria che dall'agevolazione è esclusa.

## Riferimento delle voci

Ogni voce è un nome definito nel workbook e, dove esiste, una funzione in `calcoli.py`. La colonna della norma rimanda al testo verificato sul corpus locale.

### Base imponibile e imposte di trasferimento

| Voce | Nome | Formula | Significato e norma |
|---|---|---|---|
| Categoria di lusso | `di_lusso` | `IF(OR(categoria="A/1";"A/8";"A/9");"SI";"NO")` | A/1 signorile, A/8 villa, A/9 castello sono escluse dall'agevolazione prima casa in ogni caso. Nota II-bis all'art. 1 della tariffa parte I allegata al DPR 131/1986 |
| Agevolazione applicabile | `agevolata` | `AND(prima_casa="SI"; di_lusso="NO")` | Distingue l'agevolazione richiesta da quella che spetta. Governa aliquota e moltiplicatore insieme, e in Python è `agevolazione_applicabile()` |
| Valore catastale | `valore_catastale` | `rendita * 1,05 * IF(agevolata; 110; 120)` | Base imponibile alternativa al prezzo. Art. 1 comma 497 legge 266/2005 |
| Base imponibile | `base_registro` | prezzo se IVA o se non si opta; altrimenti valore catastale | Il prezzo-valore vale solo fuori campo IVA, per persone fisiche, su immobili abitativi e pertinenze, e va chiesto in atto |
| IVA | `imp_iva` | `prezzo * 4% / 10% / 22%` | Si applica alla cessione da impresa costruttrice entro cinque anni dall'ultimazione, o oltre con opzione. Base sempre il prezzo, mai il valore catastale |
| Imposta di registro | `imp_registro` | `MAX(base * 2% o 9%; 1.000)` da privato, `200` da impresa | Il minimo di legge diventa vincolante sulle rendite basse: la formula usa un massimo, non una moltiplicazione |
| Ipotecaria e catastale | `imp_ipo`, `imp_cat` | 50 ciascuna da privato, 200 da impresa | Misura fissa in entrambi i regimi |
| Valore del bonus | `valore_bonus` | imposte senza agevolazione meno imposte con | Quantifica cosa si consuma usando l'agevolazione oggi invece che sul prossimo acquisto |

Sull'agevolazione prima casa i tre requisiti sono la residenza nel Comune o l'impegno a trasferirla entro diciotto mesi, l'assenza di altra abitazione nello stesso Comune, e l'assenza di altra abitazione agevolata sul territorio nazionale salvo rivenderla entro due anni. Il termine biennale viene dall'art. 1 comma 116 della legge 207/2024 e vale per gli atti dal 1 gennaio 2025; resta di un anno, e va tenuto distinto, il termine per riacquistare dopo una vendita infraquinquennale.

In comunione legale entrambi i coniugi devono intervenire in atto e rendere le dichiarazioni: il beneficio non si estende al coniuge che diventa comproprietario per effetto della comunione senza aver partecipato.

### Costi accessori

| Voce | Nome | Formula | Significato e norma |
|---|---|---|---|
| Provvigione | `provvigione` | `prezzo * provv_pct * 1,22` | Il mediatore ha diritto alla provvigione da ciascuna delle parti se l'affare è concluso per effetto del suo intervento: art. 1755 c.c., URN `urn:nir:stato:regio.decreto:1942-03-16;262`. La conclusione dell'affare è l'accettazione della proposta, non il rogito, e la clausola che esclude il compenso se la condizione non si avvera va scritta |
| Notaio compravendita | `notaio_cv` | input | Con il prezzo-valore l'onorario si riduce del trenta per cento |
| Altri costi | `altri_costi` | input | Visure, relazione preliminare, tecnico di parte, allacci, accatastamento, arredo minimo |
| Costi accessori | `costi_accessori` | somma di imposte, provvigione, notaio, altri, oneri mutuo | |
| Costo totale | `costo_totale` | `prezzo + costi_accessori` | Denominatore di tutti i rendimenti. Vedi ADR-002 |
| Esborso iniziale | `esborso` | `costo_totale - mutuo_importo` | Capitale proprio immobilizzato, denominatore del cash on cash |

### Mutuo

| Voce | Nome | Formula | Significato e norma |
|---|---|---|---|
| Rata mensile | `rata_mensile` | `PMT(tasso/12; durata*12; -mutuo)` | Ammortamento alla francese a rata costante. La convenzione italiana divide il tasso annuo per dodici |
| Imposta sostitutiva | `sostitutiva` | `mutuo * 0,25% o 2%` | Assorbe registro, bollo, ipotecarie e catastali sul finanziamento. L'aliquota ordinaria è lo 0,75 per cento, ridotta allo 0,25 per i finanziamenti dell'art. 16, ed è il 2 per cento quando il finanziamento non riguarda l'acquisto della prima casa: art. 18 DPR 601/1973, URN `urn:nir:stato:decreto.del.presidente.della.repubblica:1973-09-29;601`. La banca la trattiene dall'erogato |
| Loan to value | `ltv` | `mutuo / prezzo` | Oltre l'ottanta per cento servono garanzie ulteriori e le condizioni peggiorano |
| Detrazione interessi | `detrazione_anno` | `MIN(interessi; 4.000 * quota) * 19%` | Detrazione sugli interessi passivi e oneri accessori del mutuo ipotecario per l'acquisto dell'abitazione principale: art. 15 comma 1 lettera b TUIR, URN `urn:nir:stato:decreto.del.presidente.della.repubblica:1986-12-22;917`. Residenza da trasferire entro dodici mesi, termine diverso dai diciotto dell'agevolazione. Il massimale è riferito all'immobile e si ripartisce fra i cointestatari |
| Tasso effettivo | — | `RATE` sui flussi con oneri | Stima interna, non il TAEG di legge, che segue la convenzione della Banca d'Italia sull'inclusione delle voci |
| Rapporto rata reddito | — | `rata / reddito` | Soglia pratica di delibera attorno a un terzo del netto |

Fra gli oneri accessori detraibili rientrano onorario notarile dell'atto di mutuo, perizia, istruttoria, commissione di intermediazione, penale per estinzione anticipata e imposta sostitutiva. Non rientrano l'assicurazione dell'immobile neppure se richiesta dalla banca, la mediazione immobiliare, l'onorario notarile della compravendita e le imposte di trasferimento.

### Simulatore del mutuo

Il foglio `Simulatore mutuo` è indipendente da `Mutuo` e serve alle due domande che il piano di ammortamento semplice non copre: che succede se verso denaro in anticipo, e che succede se il tasso si muove. L'impianto riprende il calcolatore di Paolo Coletti, che ricalcola la rata mese per mese sul debito residuo effettivo.

La ricorsione è `debito = debito_precedente + interessi - pagato`, con `interessi = debito_precedente * tasso_mensile` e `pagato = rata + versamento volontario`, limitato a quanto serve per chiudere. La rata è costante nella modalità che accorcia il piano, ed è `PMT` sui mesi residui in quella che abbassa la rata.

La distinzione fra le due modalità non è un dettaglio: sullo stesso versamento di cento euro al mese, ridurre la durata fa risparmiare circa undicimila euro di interessi contro i seimilacinquecento della riduzione della rata, e la scelta si dichiara alla banca. Per simulare un rialzo su un tasso variabile va usata la modalità che riduce la rata, perché il variabile italiano tiene ferma la scadenza e sposta l'aumento sulla rata.

Il foglio espone anche la conversione del tasso mensile come cella: `tasso/12` è la convenzione dei contratti italiani, `(1+tasso)^(1/12)-1` è il tasso equivalente finanziariamente esatto. La differenza è piccola e non nulla, e vederla è meglio che subirla.

Sul quando convenga rimborsare, la regola è una sola e non è quella che si sente ripetere. Non conta che all'inizio si paghino soprattutto interessi: il denaro è fungibile e ogni mese la scelta è identica, cioè estinguere adesso oppure pagare gli interessi del mese per rimandare la decisione. Conviene rimborsare se non si trova un impiego che renda, al netto delle imposte, almeno quanto il tasso del mutuo. Restano fuori dal conto due argomenti veri ma non finanziari: non avere debiti fa dormire meglio, e un mutuo estinto oggi non si riottiene domani.

### Locazione

| Voce | Nome | Formula | Significato e norma |
|---|---|---|---|
| Ricavo effettivo | `ricavo_effettivo` | `(canone - sfitto) * (1 - morosità)` | Sfitto e morosità si sottraggono prima dell'imposta, perché l'imposta si paga sul percepito |
| Cedolare libero | `ced_libero` | 21% | Imposta sostitutiva di IRPEF, addizionali, registro e bollo sul contratto: art. 3 d.lgs. 23/2011, URN `urn:nir:stato:decreto.legislativo:2011-03-14;23`. Comporta la rinuncia all'aggiornamento ISTAT |
| Cedolare concordato | `ced_conc` | 10% | Aliquota ridotta per i contratti degli artt. 2 comma 3 e 8 della legge 431/1998 nei Comuni ad alta tensione abitativa, stesso art. 3 d.lgs. 23/2011 |
| Locazione breve | `ced_breve1`, `ced_breve2` | 21% e 26% | Contratti non superiori a trenta giorni stipulati da persone fisiche fuori dall'esercizio d'impresa. L'aliquota è il 26 per cento, ridotta al 21 per i redditi relativi a una unità immobiliare individuata in dichiarazione: art. 4 DL 50/2017, URN `urn:nir:stato:decreto.legge:2017-04-24;50`. Il testo non prevede alcuna aliquota del 30 per cento |
| Abbattimento IRPEF | `abbatt_ord`, `abbatt_conc` | 5% e 25% | Imponibile al 95 o al 75 per cento nel regime ordinario |
| Registro locazione | `reg_loc` | 2% del canone, minimo 67 | Solo in regime ordinario, per metà a ciascuna parte salvo patto. Base ridotta del trenta per cento per il concordato |
| IMU | — | `rendita * 1,05 * 160 * aliquota` | Abitazione principale esente salvo A/1, A/8, A/9. Aliquota base 0,86 per cento, modulabile dai Comuni fino all'1,06: va letta nella delibera comunale dell'anno |
| Accantonamento ristrutturazione | `accantonamento_ristrutturazione` | `prezzo / 3 / 40` | Un rifacimento completo ogni quarant'anni, ripartito. Vedi ADR-005 |

Dal 2026 il regime delle locazioni brevi si applica a un massimo di due unità per periodo d'imposta: dalla terza scatta la presunzione di attività d'impresa con obbligo di partita IVA. Restano gli obblighi del codice identificativo nazionale in ogni annuncio, della comunicazione degli alloggiati e dei dispositivi di sicurezza. Va inoltre verificato il regolamento condominiale, perché se è di natura contrattuale può vietare la destinazione turistica.

Va segnalata un'asimmetria del regime ordinario che il modello non simula per intero ma che pesa: i canoni non percepiti restano imponibili fino alla convalida di sfratto, quindi in caso di morosità si pagano imposte su denaro mai incassato. È un argomento a favore della cedolare che non compare nel confronto fra aliquote.

### Metriche

| Voce | Formula | Che cosa dice |
|---|---|---|
| Rendimento lordo | `canone annuo / prezzo` | Il numero degli annunci, il meno informativo. Serve a scremare |
| Rendimento netto | `utile netto / costo totale` | Il numero per decidere. Fra lordo e netto si perdono di norma due punti e mezzo |
| Cap rate | `NOI / costo totale` | Confronta immobili fra loro a prescindere dal finanziamento |
| Cash on cash | `cash flow anno 1 / esborso` | Se l'immobile mette o toglie cassa. Con la leva può essere negativo in un'operazione sana |
| DSCR | `NOI / rata annua` | Sotto 1 il reddito non copre la rata |
| TIR | `IRR(flussi_tir)` | Include l'uscita. È l'unico numero commensurabile con un investimento finanziario |
| VAN | `NPV(tasso_sconto; flussi) - esborso` | Positivo se l'operazione batte il costo opportunità scelto |

### Uscita

La plusvalenza è imponibile se fra acquisto e cessione passano meno di cinque anni, salvo che l'immobile sia stato adibito ad abitazione principale del cedente o dei suoi familiari per la maggior parte del periodo, o sia pervenuto per successione: art. 67 comma 1 lettera b TUIR, URN `urn:nir:stato:decreto.del.presidente.della.repubblica:1986-12-22;917`. In atto si può chiedere l'imposta sostitutiva del ventisei per cento in luogo dell'IRPEF. Per gli immobili con interventi agevolati da superbonus conclusi da meno di dieci anni la finestra si estende a dieci anni.

### Voci contrattuali e di due diligence

| Voce | Norma | Perché è nel modello |
|---|---|---|
| Caparra confirmatoria | Art. 1385 c.c., URN `urn:nir:stato:regio.decreto:1942-03-16;262` | Chi la riceve ed è inadempiente deve il doppio; chi la dà ed è inadempiente la perde. L'acconto non ha questo effetto, e la differenza esiste solo se è scritta |
| Trascrizione del preliminare | Art. 2645-bis c.c. | Prevale sulle trascrizioni e iscrizioni eseguite contro il promittente alienante dopo la trascrizione del preliminare. Gli effetti cessano se entro un anno dalla data convenuta, e comunque entro tre anni, non si trascrive il definitivo |
| Conformità catastale | Art. 29 comma 1-bis legge 52/1985, URN `urn:nir:stato:legge:1985-02-27;52` | Gli atti tra vivi di trasferimento di diritti reali su fabbricati esistenti devono contenere, a pena di nullità, identificazione catastale, riferimento alle planimetrie depositate e dichiarazione di conformità allo stato di fatto resa dagli intestatari |
| Menzioni urbanistiche | Art. 46 DPR 380/2001 e art. 40 legge 47/1985 | Nullità dell'atto in assenza delle dichiarazioni sul titolo edilizio |
| Tolleranze costruttive | Art. 34-bis DPR 380/2001 | Il mancato rispetto dei parametri non costituisce violazione entro il due per cento; il comma 1-bis introdotto dal Salva Casa amplia la soglia per gli interventi realizzati entro il 24 maggio 2024 |
| Fideiussione del costruttore | Art. 2 d.lgs. 122/2005, URN `urn:nir:stato:decreto.legislativo:2005-06-20;122` | Obbligo a pena di nullità del contratto, azionabile solo dall'acquirente, di consegnare fideiussione per le somme riscosse e da riscuotere prima del trasferimento |
| Polizza decennale postuma | Art. 4 d.lgs. 122/2005 | Obbligo a pena di nullità di consegnare all'atto una polizza indennitaria decennale per rovina e gravi difetti ex art. 1669 c.c., con menzione degli estremi nel rogito |
| Spese condominiali | Art. 63 disp. att. c.c. | L'acquirente è obbligato in solido per le spese dell'anno in corso e del precedente |

### Diritti del cliente nel rapporto con la banca

Vengono dalla guida ufficiale della Banca d'Italia sul mutuo ipotecario e sono nella checklist perché quasi nessuno li usa. La banca deve consegnare gratuitamente il PIES, prospetto europeo standardizzato con condizioni personalizzate, ed è l'unico modo per confrontare offerte sulla stessa base. Ricevuta l'offerta vincolante il consumatore ha almeno sette giorni di riflessione, durante i quali l'offerta resta ferma per la banca. La portabilità è per legge gratuita in entrambe le gambe e non richiede il consenso della banca di partenza. Il tasso non può superare la soglia d'usura costruita sul tasso effettivo globale medio pubblicato trimestralmente. La polizza si può presentare reperita altrove purché di protezione equivalente, e se si accetta quella della banca si ha diritto di conoscere la provvigione che la compagnia le paga. L'accesso ai propri dati in Centrale dei Rischi è gratuito.

Sulla surroga vale un'avvertenza pratica che nessuna norma scrive ma che la pratica conferma: se ne ottiene realisticamente una nella vita di un mutuo, perché la banca subentrante parte in perdita pagando il notaio e identifica chi surroga ripetutamente, e le surroghe hanno spesso spread più alti.

## Dove si interviene

Per l'aggiornamento fiscale annuale si tocca solo `src/immobiliare/parametri.py`, si sposta la costante `REVISIONE`, si aggiornano le schede di dominio impattate e si rieseguono test e verifica. I test congelano gli scaglioni IRPEF, il minimo di legge del registro e i moltiplicatori catastali, che sono le tre cose che cambiano più spesso e che passerebbero inosservate.

Per aggiungere un foglio si scrive un metodo `foglio_*` nella classe `Costruttore` e lo si registra in `costruisci()`, tenendo conto che l'ordine conta solo per la leggibilità e per i fogli che leggono da altri, come `Confronto immobili` che ha bisogno di `self.riga_annunci`.

Per aggiungere una colonna al registro annunci si tocca la dataclass `Annuncio`, la lista `ordine` in `esporta_in_excel` e la lista `colonne` in `foglio_annunci`: sono tre punti che devono restare allineati per posizione, e il test `test_intestazione_annunci_allineata_all_esportazione` fallisce se divergono.

## Come si verifica

Quattro livelli. La verifica formale del workbook con `tools/verifica-excel.ps1`, che lo apre con Excel, forza il ricalcolo e segnala ogni cella in errore. La bisezione sui fogli quando il file non si apre, generando workbook progressivi. I test automatici, trentanove in due file. E il confronto fra motore Python e workbook sullo stesso caso.

Due trappole dell'ambiente che fanno perdere tempo. L'automazione COM di Excel espone i metodi nella lingua di installazione, quindi con una console italiana il late binding non risolve `Open` e la chiamata va fatta con `InvokeMember` passando la cultura `en-US`; lo stesso vale per assegnare un valore a una cella. E `openpyxl` ignora l'assegnazione quando si passa `value=None` a `cell()`, per cui azzerare un campo richiede di assegnare sull'attributo.

Il simulatore del mutuo ha una proprietà utile come test: con versamenti volontari a zero e variazione di tasso a zero deve riprodurre esattamente il piano base, cioè stessa rata, stessi interessi totali, stessa durata e tasso interno pari al nominale. Se non lo fa, la ricorsione è rotta.

## Che cosa il modello dichiaratamente non fa

Il tasso interno di rendimento non pesa il rischio, e un immobile porta rischio di sfitto, morosità, deterioramento, illiquidità e concentrazione su un singolo bene. Il modello non prezza il lavoro di gestione. Il confronto fra comprare e affittare assume disciplina perfetta di chi investe la differenza. Il foglio `Confronto immobili` applica a tutte le righe il regime di acquisto impostato in `Immobile`, quindi non è valido fra un usato da privato e un nuovo da costruttore. La tabella sul prezzo del foglio `Scenari` è un'approssimazione dichiarata.

Resta fuori un effetto che le fonti di community segnalano con insistenza e che il modello tratta come indipendente: tassi e prezzi si muovono in senso opposto, perché quando i tassi scendono la domanda e i prezzi salgono. Il foglio `Scenari` fa variare tasso e canone su assi separati, e questo è corretto per una sensibilità meccanica ma sottostima il costo dell'attesa: rimandare l'acquisto per aspettare tassi più bassi significa competere con tutti quelli che hanno aspettato, a prezzi più alti.
