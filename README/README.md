# Smart image archive
Il progetto consiste in un applicazione desktop, avente interfaccia grafica realizzata con il framework **PySide6**, che permette di gestire in modo parzialmente automatizzato un archivio personale di immagini. L'applicazione prende immagini e per ciascuna genera un set di tag descrittivi del suo contenuto poi procede alla memorizzazione di questi tag legati all'immagine su un database **sqlite**, a quel punto il file immagine viene spostato in una cartella che l'applicazione gestisce. Avendo la base di dati contenente le corrispondenze immagine-tag è possibile svolgere query che permettono vari tipi di raggruppamento evitando di legare l'immagine a categorie rigide. Tutto il sistema è locale ed è possibile salvare le immagini processate in una cartella posizionata su un supporto di memoria diverso rispetto a quello dove si trova il file database.
Il modello ER di database è rappresentato nella pagina "database generale" nel file `schema.drawio`, è presente anche una rappresentazione in termini di tabelle del database finale, faccio presente che si tratta maggiormente di un prototipo e nello sviluppo è molto probabile che saranno necessarie ulteriori tabelle vista l'aggiunta di relazioni.

Per semplificare molto la gestione dei tag a livello di database un'idea è usare il **modulo FTS5** supportato da sqlite che permette di effetuare ricerche testuali, in pratica per ogni immagine si prevede un attributo stringa e in questa sono presenti i tag, il database che usa fts5 per le ricerche riesce a distinguere facilmente i tag che risultano semplici sottostringhe. Tuttavia, non conoscendo in modo approfondito il modulo, il modello di database usato sarà quello presentato in precedenza.

La parte maggiormente complessa è quella che consiste nel generare i tag durante la fase di processamento dell'immagine, a tale scopo si utilizzano reti neurali preaddestrate, in particolare:
- viene usata la libreria **Insight face** che fornisce sia i modelli che gli strumnenti necessari per compiere detection e recognition di volti in immagini
- viene usata la libreria **YOLO**, anche questa che fornisce strumenti e modelli preaddestrati per analisi ambientale in immagini
Generati i tag è prevista una fase di revisione che permette all'utente di controlalre la coerenza di questi.

## Ambiente di sviluppo e struttura della repository
Il linguaggio di programmazione usato è **Python** che permette di integrare facilmente tutte le varie librerie come pacchetti, è utilizzato *conda* per avere un ambiente completamente isolato dal sistema, in esso è installato Python 3.10 e *pip* attraverso il quale vengono scaricati e gestiti tutti i vari pacchetti, la lista di questi si trova nel file *requirements.txt*, è molto probabile che nello sviluppo potrebbero aggiugersi altri pacchetti. Per eseguire tutto il progetto il comando da usare è `python -m app_v1.main`.

La struttura della cartella di progetto è la seguente:
```
├───app_resources
│   ├───classes
│   ├───compiled_ui_element
│   ├───db-extension
│   ├───procedures
│   └───qt_design_ui_element
│       └───build
│
├───archive
│   ├───app_archive
│   ├───miscellaneous
│   ├───mixed
│   ├───people
│   └───test
│
├───main_window.py
└───main.py
```
In `main_window.py` contiene la struttura della schermata principale dell'applicazione `main.py` è il file di avvio (classico pattern Qt), in `app_resources` si trovano tutti i file legati al funzionamento dell'applicazione quindi classi logiche e anche classi Qt usate per costruire l'intrefaccia grafica, tra queste sono presenti i modelli *.ui* esportati dal designer e poi convertiti in codice python. `db-extension` contiene i file estensione per il database che vengono caricati ed eseguiti in ogni evento di connessione, tra questi ci sono quelli che implementano la ricerca vettoriale. `procedures` contiene i file che rappresentano le operazioni a livello utente che l'applicazione permette, ulteriori dettagli sono descritti nella sezione a seguire. La cartella `archive` contiene prevalentemente immagini usate per effetuare varie prove e test, in modo provvisorio in `app_archive` è presente il file database. Potrebbero essere presenti file con il prefisso *dev*, questi servono come appunti o per testare piccole parti di codice.

### Struttura dell'interfaccia
Descrizione non dettagliata della struttura della UI. L'interfaccia è basata sulla classe *Main_Window*, questa possiede principalmente un widget centrale della classe *QStackedWidget* il quale praticamente permette di gestire la visualizzazione di due schermate:
- Una che mostra dei "riquadri" con un pulsante che rappresentano le procedure che l'utente può avviare, è chiamata *menu_widget*.
- L'altra che invece è usata per gestire la procedura avviata, è chiamata *action_widget*
I riquadri con i bottoni si trovano "scritti" nella *Main_Window* mentre tutta la logica che serve per eseguire le varie procedure si trovano in cartelle specifiche (una per ogni procedura).

Per ogni procedura sono previsti due slot nella *Main_Window*, uno che viene eseguito alla pressione del pulsante posto nel *menu_widget*, in tale slot viene creato un oggetto procedura il quale viene poi messo nel layout dell' *action_widget* in modo che sia reso visibile, poi si connette un segnale dell'oggetto procedura appena creato con uno slot nella *Main_Window* (il secondo previsto per procedura) che si occupa di rimuovere l'oggetto dal layout di *action_widget* e poi distruggere completamente l'oggetto procedura.

Con questo flusso di lavoro in pratica l'applicazione gestisce una sola procedura alla volta e al termine di ciascuna tutte le risorse usate per l'esecuzione vengono rimosse dalla memoria per dare spazio a altre esecuzioni, inoltre va fatto notare che l'intera logica di funzionamento della procedura si trova in un oggetto dedicato il quale comunica con la *Main_Window* solo attraverso segnali.

Per aggiungere una nuova procedura all'applicazione è necessario creare un nuovo file nella cartella *procedures*, il nome del file deve far capire chiaramente che tipo di procedura implementa. Nel file va definita la classe, come minimo deve essere implementato il segnale usato poi per la distruzione e poi chiaramente tutti i vari slot che serviranno per gestire le varie interazioni utente (inserimento/modifica dati ecc.), molto importante è che tutti gli oggetti istanziati abbiano come parent l'oggetto procedura. Nella scrittura della stessa potrebbe essere necessario usare classi definite in file esterni in tal caso si utilizza *import* sulla cartella *app_resources/classes* (per importare classi pure ovvero che non creano elementi nell'interfaccia) oppure *app_resources/compiled_ui_element* (classi che introducono elementi nell'interfaccia e quindi create con il designer di Qt). 

### Metodo per la Detection e Recognition dei volti
Come detto si utilizza la libreria **Insight face**, attraverso questa, data un immagine è possibile individuare i volti contenuti in essa e poi generare un ebbedding per ciascun volto, l'associazione volto-soggetto avviene grazie al database che memorizza gli emebedding riferiti ad un singolo soggetto e permette di effettuare ricerche vettoriali di similitudine utilizzando l'estensione **sqlite-vector**, il modello ER del database è riportato nella pagina "ER face recognition" nel file `schema.drawio`. Dunque, affinche il sistema riconosca un soggetto presente in un immagine è necessario che questo risulti già presente nel database, questo avviene attraverso un procedura di registrazione che associa ad un nome un set di embedding ottenuti da immagini che ritraggono il viso del soggetto da registrare, tali embedding rappresentano il gold standard e nella ricerca vettoriale sono usati come riferimento per ciascun soggetto. Per aumentare la robustezza del sistema nel riconoscere soggetti, una volta che questi sono registrati e successivamente si processano immagini in cui tali soggetti compaiono, i volti di questi nelle nuove foto vengono memorizzati come embedding associati al particolare soggetto, questo meccanismo permette di avere flessibilità perchè le foto da processare potrebbero avere una qualità lontana da quella delle immagini usate come gold standard e questo potrebbe impedire il riconoscimento del volto, inoltre in questo modo le immagini gold standard da usare per registrare ogni soggetto non dovranno essere molte perchè appunto man mano il sistema aggiungerà embedding associati al soggetto. Un effetto collaterale che può verificarsi è la tendenza del sistema a riconoscere i soggetti che nel database hanno un più elevato numero di embedding, questo dipende da come si gestisce la ricerca vetoriale di similitudine. In alcuni prototipi ho racchiuso tutto il processo di ricerca di similitudine tra embedding del volto incognito e embedding dei volti nel database in una sola query, si calcola la media delle differenze ovvero per ogni embedding incognito nell'immagine, nel database si calcola la differenza tra questo e tutti quelli presenti e la media raggruppa questi calcoli per soggetto, in formule:
   
$$\frac{\sum_{i=1}^{n} cosineDistance(ED_{i}, EI)}{n}$$

dove $n$ è il numero di embedding associati ad un particolare soggetto registrato nel database,  $ED_{i}$ l'ebedding i-esimo presente nel database e riferito ad un soggetto e $EI$ l'embedding incognito.
Il calcolo sopra viene svolto per ogni soggetto nel database, alla fine nella query si selezionano solo le medie minori della soglia 0.6 (se la distanza coseno è molto vicino a 1 gli embedding confrontati sono siconducibili a visi diversi viceversa se la distanza è vicino a 0, scegliere 0.6 è un compromesso che accetta di avere maggiori falsi positivi) e tra queste la minore di tutte.
Senza aver svolto prove rigorose ho osservato un buon risultato cioè anche per soggetti aventi molti emebedding il riconoscimento non tende in quella direzione, è probabile che questo problema si verifichi se sono presenti nel database soggetti simili oppure un gran numero di soggetti registrati.
 
Per migliorare la precisione di riconoscimento ho considerato una sorta di media pesata, in pratica la differenza calcolata ogni volta viene pesata attraverso un coefficiente calcolato usando caratteristiche che descrivono alcune peculiarità del viso (rappresentato dal particolare embedding) come posa e dimensione, l'idea è quella di dare maggiore peso ai confronti tra embedding che risalgono a volti che si trovano in pose simili. Per svolgere un calcolo di questo tipo nel database è necessario memorizzare pr ogni embedding anche questi dati. In formule 

$$\frac{\sum_{i=1}^{n} cosineDistance(ED_{i}, EI) \cdot K_i}{\sum_{i=1}^{n} K_i}$$
$$ \text{ con } K_i = f(x_{1}ED_i,x_{1}EI,x_{2}ED_i,x_{2}EI, \dddot \space \space,x_{s}ED_i,x_{s}EI)$$

Dove $K_i$ è l'i-esimo coefficiente calcolato, la funzione che lo calcola prende ogni volta tutte le caratteristiche dei due embedding a confronto, $x_{1}ED_i$ è una caratteristica dell'i-esimo embedding associato ad un soggetto nel database (per esempio consideriamo larchezza del volto in pixel) mentre $x_{1}EI$ è la stessa caratteristica ma calcolata per l'embedding incognito, si può vedere che nella formula queste caratteristiche sono in numero s generico, il motivo è che ancora non ho ben inquadrato quali e quante caratteristiche considerare per ogni viso (indicativamente sono dimensioni in px, area del volto rispetto all'area dell'immagine, simmetria occhi naso, simmetria bocca naso, stima imbardata, stima beccheggio, nitidezza, contrasto, saturazione); in alcune prove ho utilizzato la norma dell'embedding ma questa si è rivelata non ottimale perche troppo poco lineare e dipendente da troppi fattori da controllare. Volendo mantenere il significato della distanza coseno (importante altrimenti non si riesce a stabilire se due embedding sono riconducibili ad uno stesso volto) il coefficiente $K$ deve variare tra 0 e 1 ($K$=1 embedding che appartengono a visi che possiedono molte caratteristiche in comune, la distanza calcolata tra i due embeddig ha peso massimo, $K$=0 embedding che appartengono a visi aventi caratteristiche molto diverse, la distanza calcolata tra i due embeddig non ha nessun peso nella media) ma allora la funzione $f$ che prende le caratteristiche dei volti deve prima normalizzarle (oppure si devono memorizzare nel database caratteristiche normalizzate) e questo richiede di definire range entro i quali le singole caratteristiche variano. Sotto è riportata la definizione della funzione $f$

$$ f = \frac{(QE_i+QE)}{2}$$

dove $QE_i$ sarebbe un coefficiente che quantifica la qualità dell'i-esimo embedding nel database definito dalle caratterristiche $(x_{1}ED_i, x_{2}ED_i, \dddot \space \space, x_{s}ED_i)$ e QE un coefficiente che quantifica la qualità dell'embedding incognito definito dalle caratteristiche $(x_{1}EI, x_{2}EI, \dddot \space \space, x_{s}EI)$, entrambi compresi tra 0 e 1 e con medesima definizione del tipo:

$$\frac{\sum_{j=1}^{s} \frac{ x_j - x_{j_{min}}}{x_{j_{max}} - x_{j_{min}}} \cdot w_j}{\sum_{j=1}^{s} w_j}$$

Come si vede, questo coefficiente è ottenuto come media pesata delle caratteristiche descrittrici del volto normalizzate e i pesi sono attribuiti in base a quanto la caratteristica è forte nel determinare la qualità del viso. Il concetto di qualità del viso fa riferimento al fatto che la fase di recognition produce per ogni volto un embeddig, questo dato, privato di uteriori dettagli riguardo il viso nell'immagine, diventa poco iterpretabile perchè anche se racchiude in parte le informazioni di un viso per un certo soggetto in esso potrebbero essere presenti anche fenomeni di sfocatura oppure lo stesso volto potrebbe essere parzialmente occluso, l'uico modo per considerare questi fenomeni è misurarli nel volto nell'immagine e poi legarli nel database all'embedding. Oltre a questo lo stesso modello di recognition possiede dei limiti, infatti se nel viso non sono presenti alcune features importanti come naso o bocca oppure queste sono disposte in modo molto anomalo (visi molto ruotati e deformati) è molto probabile ottenere embedding completamente errati (con nessun significato, non descrivono un volto) quindi diventa fondamentale ricavare dal volto caratteristiche chiave anche per garantire un efficacia massima del modello di riconoscimento. Stabilire $w_j$, il peso di ogni caratteristica, è una fase fondamentale e non    

### Aggiunta di soggetti nel database
Un punto non completamente risolto è come gestire il caso di soggetti inseriti dopo che nell'archivio sono state già registrate diverse foto, infatti il problema che si verifica è che 
per le immagini inserite precedentemente all'inserimento di soggetti nel dataabase non è possibile avere corrispondenza volto-soggetto (perchè il soggetto era incognito), per evitare questa situazione che porta ad avere dati non molto affidabili si può procedere in vari modi:
- timestamp delle immagini e dei soggetti registrati, in questo modo se la data di inserimento dell'immagine è minore di quella di registrazione dei soggetti allora in quella immagine non è possibile garantire la presenza o l'assenza di tali soggetti; non si risolve il problema ma si trovano gli elementi nel database per cui determinate query non possono valere.
- registrare a priori tutti gli embedding di ogni viso in ogni immagine, o meglio solo gli embedding di buona qualità, quando un nuovo soggetto viene registrato e l'embedding è molto simile a quello dei volti sconosciti nel database si verifica una modifica che associa ad alcuni dei volti sconosciuti un nome ovvero quello del nuovo soggetto registrato; forse è la soluzione kmigliore ma richiede attenzione perchè il database cresce velocemente e si rischia di tenere in memoria molti dati inutili se poi i volti incogniti non vengono mai attribuiti ad un soggetto.
- prima di iniziare a registrare immagini è necessario registrare i soggetti da riconoscere; semplice ma poco realistico.
- ogni volta che un nuovo soggetto viene aggiunto al database tutte le immagini archiviate vengono rianalizzate per verificare se il volto è presente nelle immagini e nel caso si procede alla modifica del record registrato nel database; molto costoso, avendo molte immagini significa riprocessare completamente tutto l'archivio, come ripartire da 0. 

La scelta di una delle soluzioni comporta variazioni sulla struttura del database, forse il modo più semplice è quello descritto nel primo punto dove è sufficiente creare un attributo del tipo data di inserimento sia per l'entità soggetto che per l'entità Immagine.


## Approccio e stato attuale del progetto
Ho iniziato con lo studio e implementazione della libreria **Insight face**, essendo che nella face analysis è importante garantire un interfaccia grafica anche solo per debug, ho anche scritto una la UI dell'applicazione con il modulo **PySide6** anche se in realtà è ancora molto scarna ma la struttura mi permette di espanderla ed aggiornarla facilmente. Allo stato attuale l'applicazione permette di processare immagini ed estrarre le caratteristiche dei volti manca tuttavia la parte di database che consiste nel salvataggio dei dati e che permette anche il riconoscimento dei volti (parti già parzialmente testate ma da reimplementare per cambiamenti di struttura del database e caratteristiche dei volti per calcolo dei coefficienti); realiazzata questa parte passerò allo studio di quella che si occupa della object detection.

## Note sul progetto
Il progetto è iniziato nell'ottobre 2025 come passatempo. Lo sviluppo non ha seguito un versionamento Git fin dall'inizio, principalmente per 3 motivi: scarsa familiarità con lo strumento, un approccio iniziale molto esplorativo, fatto di esperimenti su singole parti, senza mai avere una struttura stabile e l'intenzione di pubblicare solo dopo aver raggiunto qualcosa di effettivamente funzionante, soglia che non è ancora del tutto raggiunta, ma ho deciso di condividere il progetto comunque, anche solo per mostrare lo stato dei lavori.
Solo recentemente ho cercato di dare una struttura più definita in modo da avere qualcosa di più concreto, comprensibile e aggiornabile e su cui poter continuare a costruire man mano.










