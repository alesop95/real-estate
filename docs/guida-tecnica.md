# Guida tecnica

> Per chi mette le mani nel modello: come è costruito, dove si interviene, e il significato finanziario e fiscale di ogni voce con il riferimento normativo puntuale. I testi degli articoli citati sono stati verificati sul corpus normativo locale del progetto `legal-consultant`, che espone la legislazione italiana consolidata vigente; l'URN riportato è quello con cui l'articolo si recupera. La versione per chi vuole solo usare il file è in `guida-non-tecnica.md`.

## Come è fatto

Tre livelli separati, e la separazione è la ragione per cui il modello si può verificare. I parametri normativi stanno in `src/immobiliare/parametri.py` e non calcolano nulla. Le funzioni di dominio stanno in `src/immobiliare/calcoli.py`, prendono numeri e restituiscono numeri, non conoscono Excel e non leggono file. Il generatore `src/immobiliare/excel_builder.py` scrive il workbook traducendo le stesse regole in formule vive.

Le regole quindi esistono due volte, e questo è voluto: far girare lo stesso caso sul motore Python e sul workbook e confrontare i risultati è il controllo che intercetta l'errore di trascrizione, che nei fogli di calcolo è il più frequente e il meno visibile. Sul caso di riferimento le due implementazioni coincidono su tutte le grandezze di sintesi.

I riferimenti fra fogli passano sempre per nomi definiti, mai per indirizzi di cella, così una formula si legge come `prezzo * reg_prima` e non come `Immobile!$B$15`, e resta valida se una riga si sposta.

## L'indice navigabile, e il suo invariante

Il primo foglio del workbook è l'indice. Non è una pagina di presentazione: è costruito dalla tupla `Costruttore.PERCORSO`, che raggruppa i venti fogli visibili per fase del percorso e per ciascuno dichiara se si compila o si legge, quando lo si apre e che cosa ne esce. La stessa tupla è la sorgente unica: la usa il foglio per scrivere le righe, e un test la confronta con i fogli davvero presenti nel workbook, in entrambe le direzioni.

L'invariante conta perché il difetto che presidia è invisibile. Un foglio rinominato lascia nell'indice un collegamento sintatticamente valido verso una destinazione che non esiste più, e Excel lo apre senza errore: semplicemente non va da nessuna parte. Il test verifica anche la forma del collegamento, cioè che sia interno: `openpyxl` registra come destinazione esterna un collegamento assegnato come stringa a `cell.hyperlink`, e la forma corretta è un oggetto `Hyperlink` con `location`, costruito dall'helper `stile.collegamento`. La differenza si vede nel file, dove la forma esterna finisce fra le relazioni verso l'esterno, e a seconda della versione Excel la apre chiedendo conferma o la segnala come non attendibile.

Il ritorno all'indice lo scrive `stile.titolo`, nella riga che quella funzione lasciava vuota fra il titolo e il primo contenuto, in colonna A. La posizione sta lì e non accanto al titolo perché il titolo occupa da quattro a ventisei colonne a seconda del foglio, e un ritorno posizionato dopo di esso sarebbe finito fuori dalla vista sui fogli larghi. E sta in `titolo` e non nei singoli fogli perché ogni foglio comincia chiamando quella funzione, quindi un foglio nuovo non può nascere senza via di ritorno.

## Comandi

```
python tools/valuta.py excel --con-annunci
python tools/valuta.py riepilogo --prezzo 120000 --rendita 450 --mutuo 90000 --canone 500
python tools/valuta.py tassi --tasso 0.032 --mutuo 90000 --durata 25
python tools/valuta.py omi importa --file "fornitura.zip"
python tools/valuta.py omi zone --comune "NOME DEL COMUNE"
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

Il percorso del tasso è a gradini, sei al massimo, e ogni gradino dichiara da quale mese vale quale variazione cumulata rispetto al tasso di partenza. La formula del tasso di periodo è una catena di `IF` generata dal costruttore dal gradino più avanzato verso il primo, con il test `AND(mese<>""; mese_corrente>=mese)`, così che valga l'ultimo gradino raggiunto e le righe vuote non partecipino. La scelta di generare la catena invece di usare `CERCA` è deliberata: `CERCA` pretende una colonna ordinata, e sulle righe lasciate vuote si comporta in modo che nessuno riesce a prevedere leggendo la formula. Il primo gradino conserva i nomi definiti `sim_shock_mese` e `sim_shock` che esistevano quando il percorso era un gradino solo, quindi il gradino singolo non è stato sostituito: è diventato la prima riga del percorso, e un file compilato come prima si comporta come prima.

Quanto far salire il tasso non è una domanda di opinione, e il foglio non la lascia all'intuizione. Le note riportano le peggiori risalite contenute nella serie mensile dell'Euribor a tre mesi pubblicata dalla Banca centrale europea, che copre da gennaio 1994 e vale 392 osservazioni: 3,78 punti nella peggiore finestra di dodici mesi, fra giugno 2022 e giugno 2023, 4,54 su ventiquattro mesi e 4,49 su trentasei. I valori stanno congelati in `parametri.py` sotto `RISALITE_EURIBOR`, con data di verifica, perché il generatore del workbook non deve dipendere dalla rete; si rileggono sulla serie corrente con `python tools/valuta.py tassi --risalita`, che li ricalcola e dice se sono ancora quelli. La misura è la peggiore finestra di durata fissata e non il massimo meno il minimo della serie: quest'ultimo darebbe più di otto punti, un numero grande e senza significato, perché il massimo del 7,58 per cento è del marzo 1995 e il minimo del meno 0,58 del dicembre 2021, e nessun piano di ammortamento attraversa ventisei anni nella stessa finestra.

Due righe di esito chiudono il foglio e vanno lette insieme alla durata. La tabella modella 480 mesi, cioè quarant'anni di rate, e sotto l'effetto che riduce la durata un rialzo forte allunga il piano invece di alzare la rata: con la risalita del 2022-2023 applicata al caso precaricato il piano arriva al fondo della tabella con 87.082 euro di debito non estinto, mentre la durata effettiva mostra 480 mesi e gli interessi totali 206.464 euro. Sono due numeri veri che rispondono a una domanda diversa da quella posta, perché il piano non si è chiuso. La riga `Debito residuo alla fine del piano` e la riga `Il piano si chiude` lo dichiarano, la seconda con evidenza a colore quando la risposta non è sì. Lo stesso scenario sotto l'effetto che riduce la rata, cioè il funzionamento del variabile italiano, chiude in 300 mesi con la rata che passa da 436,21 a 625,52 euro e gli interessi totali a 94.602: è quello il numero da confrontare con il proprio reddito.

Sul quando convenga rimborsare, la regola è una sola e non è quella che si sente ripetere. Non conta che all'inizio si paghino soprattutto interessi: il denaro è fungibile e ogni mese la scelta è identica, cioè estinguere adesso oppure pagare gli interessi del mese per rimandare la decisione. Conviene rimborsare se non si trova un impiego che renda, al netto delle imposte, almeno quanto il tasso del mutuo. Restano fuori dal conto due argomenti veri ma non finanziari: non avere debiti fa dormire meglio, e un mutuo estinto oggi non si riottiene domani.

### Prezzo massimo sostenibile

Il numero risponde alla domanda della trattativa: quale prezzo, al massimo, giustifica l'operazione al rendimento netto che si è dichiarato accettabile. Fino a questa revisione era calcolato dividendo il costo totale sostenibile per uno più l'incidenza percentuale dei costi accessori dello scenario base, e sbagliava per due ragioni indipendenti che si sommavano nella stessa direzione.

La prima è che l'incidenza percentuale dei costi accessori non è costante al variare del prezzo. Notaio, altri costi, oneri del mutuo, imposte ipotecaria e catastale sono importi fissi, e con l'opzione prezzo-valore lo è anche l'intera imposta di registro, che resta ancorata al valore catastale: la loro incidenza cresce quando il prezzo scende. La seconda è che l'utile netto annuo non è indipendente dal prezzo, perché manutenzione ordinaria e accantonamento per la ristrutturazione di fine ciclo sono quote del valore, quindi un prezzo più basso alza l'utile. La vecchia formula teneva ferme entrambe le cose.

La soluzione esatta è algebra elementare e sta in quattro celle visibili. Il costo totale in funzione del prezzo è `P*(1+k)+c`, dove *k* raccoglie quanto scala col prezzo, cioè l'aliquota IVA oppure quella di registro quando il prezzo-valore non si applica, più la provvigione con la sua IVA, e *c* raccoglie quanto non scala. L'utile è `utile_base-(P-prezzo)*m`, con *m* pari a `manut_pct + ristrutt_pct/ristrutt_anni`. Imporre `utile(P)/costo(P) = obiettivo` dà un'equazione di primo grado in *P*, la cui soluzione è `(utile_base + prezzo*m - obiettivo*c) / (obiettivo*(1+k) + m)`.

Sul caso precaricato la differenza fra le due formule è di quasi trentamila euro: la vecchia dava 15.609 euro, l'esatta ne dà 43.445. L'errore andava sistematicamente nella direzione che fa sembrare impossibile qualunque trattativa, il che è il modo peggiore di sbagliare per un numero che serve a decidere quanto offrire. Il foglio porta accanto un controllo di chiusura che ricalcola il rendimento netto a quel prezzo con le formule esatte delle imposte, minimo di legge compreso, e mostra lo scarto dalla soglia: sul caso precaricato è zero a quattro decimali. Lo scarto è diverso da zero soltanto quando un'assunzione della linearizzazione non tiene, e il caso noto è il minimo di legge dell'imposta di registro, che su prezzi molto bassi diventa vincolante e rende il costo totale non più lineare nel prezzo. È scritto nel foglio e non lasciato a un test, perché chi cambia gli input a video deve vederlo nel momento in cui succede.

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
| Costo figurativo del tempo | `costo_tempo` | `ore_gestione * valore_ora` | Il tempo speso a gestire e' un costo reale che quasi nessuna analisi mette a bilancio. Sulla locazione breve e' moltiplicato per `coefficiente_tempo_breve`, perche' non e' un investimento passivo. Predefinito a zero, quindi neutro finche' non lo si valorizza |
| Polizza incendio | `polizza` | annua, oppure premio unico ripartito sulla durata | Obbligatoria per legge ma non necessariamente della banca. Il premio unico anticipato entra fra gli oneri iniziali, perche' e' cassa che esce al rogito, e se finanziato dentro il mutuo produce interessi |

Dal 2026 il regime delle locazioni brevi si applica a un massimo di due unità per periodo d'imposta: dalla terza scatta la presunzione di attività d'impresa con obbligo di partita IVA. Restano gli obblighi del codice identificativo nazionale in ogni annuncio, della comunicazione degli alloggiati e dei dispositivi di sicurezza. Va inoltre verificato il regolamento condominiale, perché se è di natura contrattuale può vietare la destinazione turistica.

Va segnalata un'asimmetria del regime ordinario che il modello non simula per intero ma che pesa: i canoni non percepiti restano imponibili fino alla convalida di sfratto, quindi in caso di morosità si pagano imposte su denaro mai incassato. È un argomento a favore della cedolare che non compare nel confronto fra aliquote.

### Concentrazione del patrimonio

Non riguarda l'immobile ma chi lo compra, e sta in `Metriche` perche' e' il rischio che nessun rendimento mostra. Si dichiarano patrimonio complessivo e valore immobiliare complessivo dopo l'acquisto, e il foglio restituisce la quota con tre fasce di lettura: entro un terzo, oltre un terzo, oltre due terzi.

La soglia di un terzo viene dalla pratica della consulenza patrimoniale, dove si osserva che i portafogli privati arrivano abitualmente al settanta per cento di immobiliare. Va tenuto presente che l'immobiliare non decorrela dall'azionario nelle recessioni, perche' e' la stessa contrazione del credito e della domanda a colpire entrambi, e che l'abitazione principale, per quanto fiscalmente privilegiata, e' capitale che non si puo' diversificare ne' rendere liquido e va quindi contata.

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

### Comproprietà

Il foglio `Comproprietà` ripartisce l'operazione fino a otto acquirenti e calcola per ciascuno l'imposta personale, perché in comunione il fisco non è un fatto dell'immobile ma delle persone: l'opzione per la cedolare secca si esercita disgiuntamente e vale solo per chi l'ha esercitata, e l'aliquota marginale IRPEF è individuale.

| Voce | Norma | Che cosa impone |
|---|---|---|
| Nessuna società necessaria | Art. 2248 c.c. | La comunione costituita o mantenuta al solo scopo del godimento è regolata dalle norme sulla comunione, non dal contratto di società |
| Confine con la società | Art. 2247 c.c. | La società presuppone il conferimento per l'esercizio in comune di un'attività economica. Scivolare nell'impresa senza atto costitutivo genera una società di fatto, con responsabilità illimitata e solidale |
| Quote e ripartizione | Art. 1101 c.c. | Le quote si presumono uguali; vantaggi e pesi sono in proporzione. Se gli apporti sono diversi le quote vanno scritte diverse in atto |
| Cessione della quota | Art. 1103 c.c. | Ciascuno può disporre della propria quota: senza patto di prelazione si finisce in comunione con un terzo |
| Contribuzione alle spese | Art. 1104 c.c. | Obbligo pro quota, con facoltà di liberarsi rinunciando al diritto; il cessionario risponde in solido dei contributi non versati |
| Amministrazione ordinaria | Art. 1105 c.c. | Maggioranza calcolata per valore delle quote, vincolante per la minoranza, con obbligo di informativa preventiva. In assenza di maggioranza provvede il giudice, che può nominare un amministratore |
| Regolamento e delega | Art. 1106 c.c. | A maggioranza si può adottare un regolamento e delegare l'amministrazione a un partecipante o a un terzo |
| Innovazioni e atti eccedenti | Art. 1108 c.c. | Maggioranza dei due terzi del valore. Unanimità per alienare, costituire diritti reali e locare oltre nove anni. Ipoteca ai due terzi se garantisce somme per ricostruzione o miglioramento |
| Scioglimento | Art. 1111 c.c. | Ciascuno può sempre domandarlo. Il patto di indivisione è valido, opponibile agli aventi causa, e dura al massimo dieci anni |
| Opposizione dei creditori | Art. 1113 c.c. | I creditori possono intervenire nella divisione e devono essere chiamati perché essa abbia effetto nei loro confronti |

Sul piano fiscale la ripartizione è pro quota per reddito, IMU e detrazione degli interessi, il cui massimale è riferito all'immobile. Sull'agevolazione prima casa il requisito di non possidenza guarda anche a con chi si condivide un'eventuale altra quota nello stesso Comune: con un fratello, un genitore o un estraneo non preclude, con il coniuge sì.

### Fasi contrattuali

Sono gli articoli che governano il passaggio da proposta a rogito, e sono la ragione per cui la checklist è organizzata per fasi.

| Voce | Norma | Che cosa impone |
|---|---|---|
| Conclusione del contratto | Art. 1326 c.c. | Il contratto è concluso quando il proponente ha conoscenza dell'accettazione: è il momento in cui la proposta accettata diventa vincolante |
| Proposta irrevocabile | Art. 1329 c.c. | Se il proponente si obbliga a mantenere ferma la proposta per un tempo, la revoca è senza effetto in quel periodo |
| Forma del preliminare | Art. 1351 c.c. | Il preliminare è nullo se non è fatto nella stessa forma prescritta per il definitivo, quindi per iscritto |
| Condizione | Artt. 1353-1354 c.c. | Le parti possono subordinare efficacia o risoluzione a un evento futuro e incerto: è la base della clausola sul mutuo |
| Caparra confirmatoria | Art. 1385 c.c. | Chi la riceve ed è inadempiente deve il doppio; chi la dà e è inadempiente la perde. L'acconto non ha questo effetto |
| Contratto per persona da nominare | Artt. 1401-1403 c.c. | Consente di riservarsi di nominare il soggetto che acquista, con la dichiarazione da comunicare nel termine |
| Trascrizione del preliminare | Art. 2645-bis c.c. | Prevale sulle trascrizioni e iscrizioni successive contro il promittente alienante; gli effetti cessano se il definitivo non si trascrive entro un anno dalla data convenuta e comunque entro tre anni |
| Privilegio sul credito restitutorio | Art. 2775-bis c.c. | I crediti del promissario acquirente per mancata esecuzione del preliminare trascritto hanno privilegio speciale sull'immobile |
| Ipoteca e preliminare | Art. 2825-bis c.c. | Disciplina il rapporto fra l'ipoteca iscritta sul bene e il preliminare trascritto |
| Esecuzione in forma specifica | Art. 2932 c.c. | Se chi è obbligato a concludere il contratto non lo fa, l'altra parte può ottenere una sentenza che produce gli effetti del contratto non concluso |
| Garanzia per vizi | Artt. 1490, 1495, 1497 c.c. | Il venditore risponde dei vizi che rendono la cosa inidonea o ne diminuiscono il valore, con termini di denuncia brevi |

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

### Documentazione tecnica pre-acquisto

Il foglio Dossier tecnico elenca sessantasei documenti in nove famiglie, con peso, chi li rilascia, la norma e il costo indicativo. È costruito da `foglio_dossier()` a partire da una lista di tuple, e i due nomi definiti `documenti_bloccanti_aperti` e `documenti_completamento` alimentano il Cruscotto. La scheda estesa è `docs/perizia-pre-acquisto.md`; qui stanno le sole norme che governano il fascicolo.

| Voce | Norma | Perché è nel modello |
|---|---|---|
| Stato legittimo | Art. 9-bis c. 1-bis DPR 380/2001 | È il titolo che ha previsto la costruzione o ha disciplinato l'ultimo intervento sull'intera unità, integrato dai titoli successivi che hanno abilitato interventi parziali. Per gli immobili costruiti quando il titolo non era obbligatorio si desume dalle informazioni catastali di primo impianto o da altri documenti probanti |
| Autonomia fra unità e parti comuni | Art. 9-bis c. 1-ter DPR 380/2001 | Ai fini dello stato legittimo della singola unità non rilevano le difformità sulle parti comuni ex art. 1117 c.c., e viceversa. Delimita il perimetro della verifica sull'appartamento |
| Tolleranze e dichiarazione asseverata | Art. 34-bis cc. 1, 1-bis e 3 DPR 380/2001 | Soglia generale del due per cento; per gli interventi entro il 24 maggio 2024 il cinque per cento sotto i cento metri quadrati di superficie utile, il quattro fra cento e trecento, il tre fra trecento e cinquecento, il due oltre. Le tolleranze vanno dichiarate dal tecnico con atto asseverato allegato al trasferimento |
| Attestazione sismica delle tolleranze | Art. 34-bis c. 3-bis DPR 380/2001 | In zona sismica non a bassa sismicità il tecnico attesta il rispetto delle norme tecniche vigenti al momento dell'intervento, con trasmissione allo sportello unico ai fini dell'autorizzazione regionale |
| Opere iniziate prima del 1 settembre 1967 | Art. 40 c. 3 legge 47/1985 | In luogo degli estremi della licenza può essere prodotta dichiarazione sostitutiva di atto notorio del proprietario che attesti l'inizio anteriore a quella data, ricevuta nell'atto o allegata |
| Certificato di destinazione urbanistica | Art. 30 c. 2 DPR 380/2001 | Nullità dell'atto avente ad oggetto terreni senza CDU allegato; esclusione per l'area di pertinenza di fabbricati censiti al catasto urbano inferiore a cinquemila metri quadrati |
| Agibilità | Art. 24 DPR 380/2001 | Sicurezza, igiene, salubrità, risparmio energetico e conformità dell'opera al progetto sono attestati con segnalazione certificata, corredata dall'asseverazione del direttore dei lavori e dal collaudo statico |
| Autorizzazione sismica | Artt. 93 e 94 DPR 380/2001 | In zona sismica preavviso allo sportello unico con progetto; fuori dalla bassa sismicità i lavori non possono iniziare senza autorizzazione preventiva dell'ufficio tecnico regionale |
| Accesso agli atti | Art. 22 legge 241/1990 | Via per ottenere titoli edilizi ed eventuali procedimenti sanzionatori dall'archivio comunale. Richiede delega del proprietario o interesse qualificato: è la ragione tecnica per cui la proposta si presenta condizionata |
| Tutela dei beni culturali | Artt. 59-62 d.lgs. 42/2004 | Denuncia del trasferimento e prelazione dello Stato nel termine di legge. Sotto tutela non si applicano le tolleranze esecutive del comma 2 dell'art. 34-bis |
| Impianti | DM 37/2008 | Dichiarazione di conformità; per gli impianti anteriori al 2008 la dichiarazione di rispondenza rilasciata da soggetto con i requisiti dell'art. 7 c. 6 |
| Prestazione energetica | D.lgs. 192/2005 | APE in corso di validità, da allegare all'atto e indicare nell'annuncio |
| Locazione opponibile | Art. 1599 c.c., legge 431/1998 | La locazione con data certa anteriore all'alienazione è opponibile all'acquirente, che subentra nel contratto fino alla scadenza |
| Provenienza donativa | Artt. 561 e 563 c.c. | Azione di restituzione contro i terzi acquirenti nel termine ventennale dalla trascrizione della donazione; si neutralizza con rinuncia degli aventi diritto o polizza dedicata |
| Cosa gravata da garanzie reali o vincoli | Art. 1482 c.c. | Il compratore può sospendere il prezzo, far fissare un termine per la liberazione e ottenere la risoluzione con il danno, ma solo se i gravami non erano dichiarati dal venditore ed erano da lui ignorati; se li conosceva resta la sola garanzia per evizione. È la norma che rende la dichiarazione di libertà da gravami un presidio e non una formalità |
| Oneri e diritti di terzi non apparenti | Art. 1489 c.c. | Servitù non apparenti, comodati, diritti personali di godimento e oneri reali non si trascrivono e non compaiono in ispezione: se non dichiarati nel contratto e ignorati dal compratore, danno risoluzione o riduzione del prezzo |
| Cancellazione dell'ipoteca | Art. 2882 c.c., art. 40-bis d.lgs. 385/1993 | La cancellazione richiede l'atto di assenso del creditore; nella procedura semplificata la banca rilascia quietanza e comunica al conservatore entro trenta giorni senza oneri, ma l'estinzione non si verifica se comunica entro lo stesso termine che l'ipoteca permane per giustificato motivo ostativo. Si verifica la cancellazione nei registri, non la quietanza |
| Prelazione dei coeredi | Art. 732 c.c. | Il coerede che aliena la quota a un estraneo deve notificare la proposta agli altri, che hanno due mesi; in mancanza di notificazione possono riscattare la quota dall'acquirente e da ogni successivo avente causa finché dura la comunione ereditaria |
| Esenzione da revocatoria del preliminare trascritto | Art. 166 c. 3 d.lgs. 14/2019 | Non sono soggetti a revocatoria le vendite e i preliminari trascritti ex art. 2645-bis, i cui effetti non siano cessati, conclusi a giusto prezzo e aventi ad oggetto immobili ad uso abitativo destinati ad abitazione principale dell'acquirente o di parenti e affini entro il terzo grado. Tre condizioni congiunte |
| Revocatoria ordinaria | Art. 2901 c.c. | Il creditore può far dichiarare inefficace nei suoi confronti l'atto di disposizione pregiudizievole, nel termine di cinque anni. Rileva comprando da un venditore esposto |
| Vincoli di destinazione trascritti | Artt. 167 e 2645-ter c.c. | Fondo patrimoniale, trust e atti di destinazione limitano la disponibilità del bene e possono richiedere consensi o autorizzazione del giudice, con effetti sui tempi del rogito |
| Dichiarazione sostitutiva di atto di notorietà | Artt. 47 e 76 DPR 445/2000 | Riguarda stati, qualità e fatti a diretta conoscenza del dichiarante; chi rende dichiarazioni mendaci o forma atti falsi è punito ai sensi del codice penale. È la forma che dà peso a una dichiarazione privata |
| Dichiarazione su mediazione e mezzi di pagamento | Art. 35 c. 22 DL 223/2006 | Le parti dichiarano in atto le analitiche modalità di pagamento, se si sono avvalse di un mediatore, e importi e mezzi di pagamento della provvigione |
| Capacità e legittimazione delle parti | Artt. 320, 374 e 2384 c.c. | Minori, interdetti e beneficiari di amministrazione di sostegno richiedono l'autorizzazione del giudice; per una società vanno verificati i poteri del firmatario |
| Continuità delle trascrizioni | Artt. 2648 e 2650 c.c. | Senza accettazione dell'eredità trascritta la continuità si interrompe e l'atto successivo non produce effetto verso i terzi |

### Diritti del cliente nel rapporto con la banca

Vengono dalla guida ufficiale della Banca d'Italia sul mutuo ipotecario e sono nella checklist perché quasi nessuno li usa. La banca deve consegnare gratuitamente il PIES, prospetto europeo standardizzato con condizioni personalizzate, ed è l'unico modo per confrontare offerte sulla stessa base. Ricevuta l'offerta vincolante il consumatore ha almeno sette giorni di riflessione, durante i quali l'offerta resta ferma per la banca. La portabilità è per legge gratuita in entrambe le gambe e non richiede il consenso della banca di partenza. Il tasso non può superare la soglia d'usura costruita sul tasso effettivo globale medio pubblicato trimestralmente. La polizza si può presentare reperita altrove purché di protezione equivalente, e se si accetta quella della banca si ha diritto di conoscere la provvigione che la compagnia le paga. L'accesso ai propri dati in Centrale dei Rischi è gratuito.

Sulla surroga vale un'avvertenza pratica che nessuna norma scrive ma che la pratica conferma: se ne ottiene realisticamente una nella vita di un mutuo, perché la banca subentrante parte in perdita pagando il notaio e identifica chi surroga ripetutamente, e le surroghe hanno spesso spread più alti.

## Dove si interviene

Le quotazioni OMI aggiornate non sono automatizzabili e la ragione va detta: la fornitura ufficiale passa da un'autenticazione personale ai servizi telematici, che uno script non deve simulare, e il servizio di consultazione a video non espone una API documentata ne' un `robots.txt`, quindi in assenza di permesso esplicito ci si astiene. La via supportata e' quindi scaricare la fornitura a mano una volta per semestre e ingerirla con `python tools/valuta.py omi importa --file <archivio>`, che accetta lo zip cosi' come arriva o i CSV gia' estratti; `omi zone --comune` elenca poi le zone omogenee per scegliere quella giusta. Il mirror open data resta per la serie storica e si ferma al 2018.

Per l'aggiornamento fiscale annuale si tocca solo `src/immobiliare/parametri.py`, si sposta la costante `REVISIONE`, si aggiornano le schede di dominio impattate e si rieseguono test e verifica. I test congelano gli scaglioni IRPEF, il minimo di legge del registro e i moltiplicatori catastali, che sono le tre cose che cambiano più spesso e che passerebbero inosservate.

Per aggiungere un foglio si scrive un metodo `foglio_*` nella classe `Costruttore` e lo si registra in `costruisci()`, tenendo conto che l'ordine conta solo per la leggibilità e per i fogli che leggono da altri, come `Confronto immobili` che ha bisogno di `self.riga_annunci`.

Per aggiungere una voce a una tabella costruita da un helper, come il conto economico del foglio `Locazione` o la tabella a tre scenari del foglio `Scenari`, la regola è che la riga non si calcola: si chiede a chi la scrive. Entrambi gli helper restituiscono la riga che hanno occupato, e le formule che devono citare altre righe usano quel valore. La versione precedente calcolava gli indici come una riga di ancoraggio più una costante scritta a mano accanto a ogni chiamata, e il difetto era latente: inserendo una voce in mezzo, tutte le righe successive si spostavano di uno e le costanti restavano dov'erano, quindi il reddito operativo netto sommava un intervallo traslato e l'utile netto leggeva la riga sbagliata. Il file si apriva, nessuna cella andava in errore, i valori di sintesi restavano plausibili. Nella tabella degli scenari la stessa disciplina è irrigidita ancora un poco: ogni riga si registra in un dizionario sotto una chiave breve e le formule citano le chiavi, così che una chiave assente sollevi un `KeyError` alla generazione invece di produrre un riferimento valido a una riga diversa. Il vincolo che ne consegue è dichiarato e desiderabile: una formula può citare solo righe già scritte.

Per aggiungere una colonna al registro annunci si tocca la dataclass `Annuncio`, la lista `ordine` in `esporta_in_excel` e la lista `colonne` in `foglio_annunci`: sono tre punti che devono restare allineati per posizione, e il test `test_intestazione_annunci_allineata_all_esportazione` fallisce se divergono. La colonna nuova si aggiunge in coda e non in mezzo, perche' il foglio `Confronto immobili` cita le colonne del registro per lettera e un'inserzione intermedia le sposterebbe tutte in silenzio.

Un riferimento da un foglio a un altro si scrive per nome definito, mai per coordinata. La regola non e' stilistica: la formula del Cruscotto che dava il verdetto fra comprare e affittare citava `'Confronto affitto'!$B$52`, che nel frattempo era diventata la riga del patrimonio comprando invece di quella della differenza fra i due patrimoni. Il patrimonio comprando e' positivo per qualunque immobile di valore, quindi il verdetto risultava "conviene comprare" anche quando il foglio, quattro righe sotto, concludeva l'opposto: con il rendimento del portafoglio alternativo al nove per cento la differenza vale meno centoquattordicimila euro e il Cruscotto diceva ancora di comprare. Nessuna cella in errore, nessun segnale, e il numero sbagliato esposto sul primo foglio del workbook, cioe' quello che si legge per decidere. Il presidio e' il nome definito `conf_differenza`, e il test `test_cruscotto_legge_il_confronto_affitto_per_nome` verifica non solo che la formula lo usi ma che il nome punti alla riga la cui etichetta e' quella attesa.

## Come si verifica

Quattro livelli. La verifica formale del workbook con `tools/verifica-excel.ps1`, che lo apre con Excel, forza il ricalcolo e segnala ogni cella in errore. La bisezione sui fogli quando il file non si apre, generando workbook progressivi. I test automatici, sessantuno in due file, quarantadue sul motore di calcolo e sui moduli di dominio e diciannove sulla struttura del workbook, sull'acquisizione e sulla graduatoria. E il confronto fra motore Python e workbook sullo stesso caso.

Due trappole dell'ambiente che fanno perdere tempo. L'automazione COM di Excel espone i metodi nella lingua di installazione, quindi con una console italiana il late binding non risolve `Open` e la chiamata va fatta con `InvokeMember` passando la cultura `en-US`; lo stesso vale per assegnare un valore a una cella. E `openpyxl` ignora l'assegnazione quando si passa `value=None` a `cell()`, per cui azzerare un campo richiede di assegnare sull'attributo.

Il simulatore del mutuo ha una proprietà utile come test: con versamenti volontari a zero e variazione di tasso a zero deve riprodurre esattamente il piano base, cioè stessa rata, stessi interessi totali, stessa durata e tasso interno pari al nominale. Se non lo fa, la ricorsione è rotta.

## Che cosa il modello dichiaratamente non fa

Il tasso interno di rendimento non pesa il rischio, e un immobile porta rischio di sfitto, morosità, deterioramento, illiquidità e concentrazione su un singolo bene. Il modello non prezza il lavoro di gestione. Il confronto fra comprare e affittare assume disciplina perfetta di chi investe la differenza. Il foglio `Confronto immobili` legge il regime di acquisto riga per riga dalle due colonne in coda al registro, e ricade su quello di `Immobile` solo dove il registro tace: restano invece globali l'opzione prezzo-valore e la qualifica di immobile di lusso, quindi un immobile in categoria A/1, A/8 o A/9 accanto a immobili ordinari va valutato a parte. La tabella sul prezzo del foglio `Scenari` resta un'approssimazione dichiarata nella sola riga delle imposte propagate al resto, mentre il prezzo massimo sostenibile è ora esatto.

Resta fuori un effetto che le fonti di community segnalano con insistenza e che il modello tratta come indipendente: tassi e prezzi si muovono in senso opposto, perché quando i tassi scendono la domanda e i prezzi salgono. Il foglio `Scenari` fa variare tasso e canone su assi separati, e questo è corretto per una sensibilità meccanica ma sottostima il costo dell'attesa: rimandare l'acquisto per aspettare tassi più bassi significa competere con tutti quelli che hanno aspettato, a prezzi più alti.
