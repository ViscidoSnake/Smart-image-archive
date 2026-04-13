from PySide6.QtCore import Qt
from PySide6.QtWidgets import QWidget, QVBoxLayout, QScrollArea, QSizePolicy, QLabel, QPushButton
from PySide6.QtCore import Slot, Signal

import cv2
import insightface
import os

import numpy as np
from numpy.linalg import norm

# from ..app_resources.classes.img_object_class import img_obj
from ..classes.img_object_v2_class import img_obj


# import assets ui
from ..compiled_ui_element.dir_path_selector import Dir_path_selector
from ..compiled_ui_element.img_card import img_card
from ..compiled_ui_element.engine_data_form import Engine_data_form


class Analyze_photos_procedure(QScrollArea):
    
    #signals
    abort_procedure = Signal()
    
    def __init__(self):
        super().__init__()

        # per sviluppo collego il segnale distruzione
        self.destroyed.connect(lambda: print("Distrutto oggetto della classe Analyze_photos_procedure"))

        self.setWidgetResizable(True)

        # variabili importante per processamento oggetti foto
        self.imgs_o_list = []

        # Container per i contenuti
        self.container = QWidget()
        self.layout = QVBoxLayout(self.container)
        self.setWidget(self.container)

        # genero blocco per inserire il percorso alla cartella immagini
        self.dir_selector = Dir_path_selector()
        self.layout.addWidget(self.dir_selector)
        #connessioni ai bottoni che permettono di procedere oppure interrompere il processo
        self.dir_selector.btn_confirm.clicked.connect(self.set_raw_detection_engine)
        self.dir_selector.btn_abort.clicked.connect(self.abort_procedure.emit)

    def set_raw_detection_engine(self):
        # disabilito il form per inserimento dei dati
        self.dir_selector.setDisabled(True)
        # genero il blocco per inseriemento dei dati per inizializzazione del motore di detection
        self.det_raw_engine_form = Engine_data_form()
        self.layout.addWidget(self.det_raw_engine_form)
        # collego il segnale del pulsante presente nell'oggetto appena creato in modo da passare allo step successivo
        self.det_raw_engine_form.pushButton_applied_params.clicked.connect(self.start_raw_detection)
        

    def start_raw_detection(self):
        # disabilito il form per inserimento parametri detector
        self.det_raw_engine_form.setDisabled(True)

        # widget contenitore dentro al quale vanno poi tutti gli oggetti Img_card, metti insomma un titolo per far capire, un contorno anche. Un idea potrebbe essere includere nella label una numerazione tipo 1.0 per raw detection e poi 1.1 e cosi via, stello oggetto ma ridisegnato ogni volta, a differenza della prassi classica che ho scelto ovvero quello di lasciare disable gli step precedenti a quello attuale
        self.imgs_container = QWidget()
        self.imgs_container_layout = QVBoxLayout(self.imgs_container)
        self.layout.addWidget(self.imgs_container)
        # memorizzo come membro la label, è utile così non ce il problema di dover fare mille giri per ripescarlo oltre poi a evitarmi di decidere il nome dell'oggetto roba critica in questa interfaccia essendoci molti elementi
        self.imgs_container_label  = QLabel("Step 2.1")
        self.imgs_container_label.setStyleSheet("font-size: 20pt;")
        self.imgs_container_layout.addWidget(self.imgs_container_label)

        # prendo dal form dove sono stati inseriti i parametri di inizializzazione e creo oggetto per la detection
        raw_engine_params = self.det_raw_engine_form.get_all_data()
        # modello per la prima detection (raw)
        det_raw_model_option = {
        'providers':['AzureExecutionProvider','CPUExecutionProvider'],
        }

        # per sviluppo linux
        det_raw_model_path = r"/home/viscidosnake/.insightface/models/buffalo_l/det_10g.onnx"
        
        # per sviluppo windows
        # det_raw_model_path = r"C:\Users\snake\.insightface\models\buffalo_l\det_10g.onnx"

        det_raw_h = insightface.model_zoo.get_model(det_raw_model_path, **det_raw_model_option)
        det_raw_h.prepare(ctx_id=-1,
                    det_thresh = raw_engine_params["det_threshold"],
                    input_size = raw_engine_params["det_size"])
        
        # prendo il percorso alla cartella scritto nella label dell'oggetto Ui_dir_path_selector, apro la cartella e inizio a processare un immagine alla volta
        dir_path = self.dir_selector.le_dir_path_selected.text()
        imgs = os.listdir(dir_path)
        i=0
        for img in imgs:

            img_path = dir_path + '/' + img
            # creo subito oggetto immagine, attenzione non la card ma l'oggetto logico contenente i dati, questo è da mantenere in memoria perche servirà poi per gli step successivi
            img_o = img_obj(img_path)
            self.imgs_o_list.append(img_o)

            # detection dei volti
            bboxes, kpss = det_raw_h.detect(img_o.get_cv(), max_num=0, metric='default')
            img_o.load_faces_list("first detection", bboxes, kpss)
            
            # creo oggetto card passando metadati, dati volti e immagine da oggetto img_o, allora img_card è un oggetto della classe qwidget quindi ha una gestione particolare, in pratica non mi serve mantenere esplicitamente un riferimento a ogni oggetto perchè posso accedere a questo attraverso gli oggetti dell'interfaccia in particolare attraverso il layout di self.imgs_container

            # img_o_card = img_card(img_o.get_cv(), img_o.get_faces_list("first detection"), img_o.get_metadata())
            
            img_o.extract_faces_features("first detection")
            img_o_card = img_card(img_o.get_cv(), img_o.get_faces_features("first detection"), img_o.get_metadata()) 
            self.imgs_container_layout.addWidget(img_o_card)

        # creo 2 pulsanti per permettere di decidere cosa fare: proseguire con la fase dopo oppure ripetere questa o meglio a partire da quella di selezione dei params usati per inizializzare oggetto di detection. anche questi li traccio lasciando un riferimento nell'oggetto in modo che ho accesso immediato e non devo definire un object name all'oggetto
        self.imgs_container_button_repeat = QPushButton("Repeat raw detection")
        self.imgs_container_layout.addWidget(self.imgs_container_button_repeat)
        self.imgs_container_button_repeat.clicked.connect(self.repeat_raw_detection)
        
        self.imgs_container_button_proceed = QPushButton("Proceed the analysis")
        self.imgs_container_layout.addWidget(self.imgs_container_button_proceed)
        self.imgs_container_button_proceed.clicked.connect(self.start_raffined_detection)

        


    def repeat_raw_detection(self):
        # allora devi eliminare varie cose dall'interfaccia oltre poi a svuotare completamente self.imgs_o_list (con svuotare intendo distruggere completamente tutti gli oggetti che contiene)
        self.det_raw_engine_form.deleteLater()
        self.imgs_container.deleteLater()
        self.imgs_o_list.clear()
        # a questo punto puoi ricominciare dalla selezione dei parametri
        self.set_raw_detection_engine()
        # nota per ottimizzare puoi evitare di distruggere self.det_raw_engine_form e semplicemente sbloccarlo però poi non puoi fare diretto self.set_raw_detection_engine() a meno di modificare il metodo stesso mettendo un controllo che riguarda l'esistenza di un oggetto Engine_data_form, mi sembra più lineare così però


    def start_raffined_detection(self):
        # modifico il testo della label da 2.1 a 2.2
        self.imgs_container_label.setText("Step 2.2")
        
        # inizializzo il modello per fare la detection raffinata, nota bene che è esattamente a questo livello che poni un limite inferiore di qualità del viso (per dettagli vedi appunti) e lo fai con det_thresh  
        det_model_option = {
        'providers':['AzureExecutionProvider','CPUExecutionProvider'],
        }

        # per windows
        # det_model_path = r"C:\Users\snake\.insightface\models\buffalo_l\det_10g.onnx"
        # per linux
        det_model_path = r"/home/viscidosnake/.insightface/models/buffalo_l/det_10g.onnx"
        
        det_h = insightface.model_zoo.get_model(det_model_path, **det_model_option)
        det_h.prepare(ctx_id=-1,
                    det_thresh = 0.75)
        
        # lavora dentro un ciclo for, per ogni oggetto img_o devi calcolare il det size ottimale tenendo anche presente dei volti selezionati per quella stessa immagine, ora il punto è questo, bisogna trovare corrispondenza tra le card nella gui e quelli in self.imgs_o_list, la cosa più facile è considerare l'ordine cioè self.imgs_o_list è stato costruito con lo stesso ordine con cui è stato riempito il layout dove si trovano le card quidi potrebbe funzionare però da l'idea di essere fragile, magari per qualche motivo l'ordine si altera o magari in un futuro metto dei filtri particolari che quindi modificano il modo in cui si presentano le card. un modo robusto è confrontare il nome del file scritto nella card con quello scritto negli oggetti img_o

        for i in range(self.imgs_container_layout.count()):
            # card_item = self.conimg_card_items.itemAt(i)
            card_item = self.imgs_container_layout.itemAt(i)
            card_widget = card_item.widget()

            # salta se non è un elemento della classe img_card
            if not (isinstance(card_widget, img_card)): continue
            
            cwn = card_widget.get_all_metadata()["file_name"]
            for img_o in self.imgs_o_list:
                # salta se l'oggetto non ha metadata["file_name"] identico a quello del widget
                if img_o.get_metadata()["file_name"] != cwn: continue
                # print(img_o.metadata["file_name"])
                # prendo dall'interfaccia gli item della tabella per capire quali volti sono stati effettivamente selezionati, nota non prendo effettivamente gli item ma dizionari che riportano lo stato di ogni item, questo è dovuto a come è implementato il metodo della classe custom table (la trovi nel file qt_img_display). Filtro gli oggetti che hanno select == True e per questi get del face index

                
                table_selected_faces_data = card_widget.get_table_data(filter=("select",True))
                # prima controllo che la prima detection abbia dato almeno dei volti, per fare questo controllo lista delle features della prima detection, se falso passo diretto avanti essendo che non è presente nessun volto da analizzare e blocco completamente la card corrente, facendo in questo modo l'immagine salta tutte le fasi successive e l'utente pur vedendola non può interagirci, l'altro controllo serve a vedere quanti volti sono stati selezionati per il raffinamento, anche qui, se nessun vlto è stato selezionato allora opero sulla card nel medesimo modo. Nota, basta controllare table_selected_faces_data perche la tabella viene creata sempre, anche quando non sono presenti dati in essa.
                if( len(table_selected_faces_data) == 0 ): 
                    card_widget.setEnabled(False)
                    continue
                
                selected_faces_index = [(face["index"]) for face in table_selected_faces_data]
                # equivale a questo
                # selected_faces_index = []
                # for selected_faces_data in table_selected_faces_data:
                #     selected_faces_index.append(int(selected_faces_data["Face_index"]))

                # calcolo del det_size ottimale, detection nuova e inserimento dei nuovi dati volti in img_o.load_final_detection_data
                optimal_det_size = img_o.get_optimal_det_size(selected_faces_index)
                # print(f"{cwn} - {optimal_det_size}")
                bboxes, kpss = det_h.detect(img_o.get_img_masked(), max_num=0, metric='default', input_size=optimal_det_size)
                img_o.load_faces_list("second detection", bboxes, kpss)
                # print(img_o.final_faces_detection)

                img_o.extract_faces_features("second detection")
                # ora qui la parte importante, a differenza di prima non devo creare nuovamente un oggetto img_card ma invece mi basta modificarlo, in particolare cambio solo i dati nella tabella
                card_widget.load_table(img_o.get_faces_features("second detection"))
        
        # ora devo togliere self.imgs_container_button_repeat poi devo scollegare self.imgs_container_button_proceed da start_raffined_detection e collegarlo invece alla funzione che realizza lo step successivo ovvero la recognition effettiva dei volti ovvero quindi la produzione degli embedding
        self.imgs_container_button_repeat.deleteLater()

        self.imgs_container_button_proceed.clicked.disconnect(self.start_raffined_detection)
        self.imgs_container_button_proceed.clicked.connect(self.start_recognition)
        
                
    def start_recognition(self):
        # ora devo effettuare la recognition dei volti, inizializzo il modello per recognition
        rec_model_option = {
        'providers':['AzureExecutionProvider','CPUExecutionProvider'],
        }


        # per windows
        # rec_model_path = r"C:\Users\snake\.insightface\models\buffalo_l\w600k_r50.onnx"
        # per linux
        rec_model_path = r"/home/viscidosnake/.insightface/models/buffalo_l/w600k_r50.onnx"

        
        rec_h = insightface.model_zoo.get_model(rec_model_path, **rec_model_option)
        rec_h.prepare(ctx_id=-1)

        # pos_model_option = {
        # 'providers':['AzureExecutionProvider','CPUExecutionProvider'],
        # }
        # pos_model_path = r"C:\Users\snake\.insightface\models\buffalo_l\1k3d68.onnx"
        # pos_h = insightface.model_zoo.get_model(pos_model_path, **pos_model_option)
        # pos_h.prepare(ctx_id=-1)

        # ancora una volta è necassario fare il lavoro di prendere dall'interfaccia i soli volti selezionati e poi per questi eseguire elaborazione, come fatto per la seconda recognition per trovare corrispondenza tra dati nella card presente nella gui e dati scritti nell'oggetto img_o uso il file name e poi elaboro solo i volti che hanno Select_for_the_next_step == True
        for i in range(self.imgs_container_layout.count()):
            # card_item = self.conimg_card_items.itemAt(i)
            card_item = self.imgs_container_layout.itemAt(i)
            card_widget = card_item.widget()

            # salta se non è un elemento della classe img_card
            if not (isinstance(card_widget, img_card)): continue
            
            cwn = card_widget.get_all_metadata()["file_name"]
            for img_o in self.imgs_o_list:
                # salta se l'oggetto non ha metadata["file_name"] identico a quello del widget
                if img_o.get_metadata()["file_name"] != cwn: continue
                # print(img_o.metadata["file_name"])
                # prendo dall'interfaccia gli item della tabella per capire quali volti sono stati effettivamente selezionati, nota non prendo effettivamente gli item ma dizionari che riportano lo stato di ogni item, questo è dovuto a come è implementato il metodo della classe custom table (la trovi nel file qt_img_display). Filtro gli oggetti che hanno Select_for_the_next_step == True e per questi get del face index da riportare a intero

                # # prima controllo che la seconda detection abbia dato almeno dei volti, per fare questo controllo lista delle features della prima detection
                # if(len(img_o.get_faces_features("second detection")) == 0): continue
                # table_selected_faces_data = card_widget.get_table_data(filter=("select",True))
                # if(len(table_selected_faces_data) == 0): continue


                table_selected_faces_data = card_widget.get_table_data(filter=("select",True))
                # prima controllo che la prima detection abbia dato almeno dei volti, per fare questo controllo lista delle features della prima detection, se falso passo diretto avanti essendo che non è presente nessun volto da analizzare e blocco completamente la card corrente, facendo in questo modo l'immagine salta tutte le fasi successive e l'utente pur vedendola non può interagirci, l'altro controllo serve a vedere quanti volti sono stati selezionati per il raffinamento, anche qui, se nessun vlto è stato selezionato allora opero sulla card nel medesimo modo. Nota, basta controllare table_selected_faces_data perche la tabella viene creata sempre, anche quando non sono presenti dati in essa. Aggiungo che questo è un caso abbastanza particolare perche in teoria la detection raffinata dovrebbe migliorare la prima e quindi dovrebbero esserci sempre lo stesso numero di volti o anche più ma mai meno, ho registrato anomalie solo per volti molto ruotati 
                if( len(table_selected_faces_data) == 0 ): 
                    card_widget.setEnabled(False)
                    continue



                selected_faces_index = [(face["index"]) for face in table_selected_faces_data]
                # ora prendo la lista completa della second detection e la filtro per indici, per ogni elemento con indice idoneo faccio recognition e salvo nella lista
                l = []
                for face in img_o.get_faces_list("second detection"):
                    if face.index in selected_faces_index:
                        rec_h.get(img_o.get_cv(), face)

                        # pos_h.get(img_o.get_cv(), face)

                        # print(face)

                        l.append(face)
                # passaggio finale, devo memorizzare in img_o la lista dei volti con emedding
                img_o.load_faces_list("recognition", original_list = l)

                img_o.extract_faces_features("recognition")



                # !!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!
                # in realtà ora qui ci sarebbe la parte con il database, infatti avendo per ogni volto un ebedding questo dovrebbe andare confrontato con quelli presenti nel database e attraverso la query dovrebbe essere possibile compiere riconoscimento
                # !!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!





                # ancora una cosa fondamentale, devo mettere nell'interfaccia i buovi dati o meglio mostrare i soli volti selezionati dalla second detection con in più embedding (in realt mostrerò la norma dell'embedding) quindi in modo molto simile a prima:
                card_widget.load_table(img_o.get_faces_features("recognition"))





        
        # a questo punto dentro img_o.final_faces_selected ho la lista di volti selezionati con embeddig ottimo e quindi posso procedere con le varie operazioni, dal salvataggio nel db fino al riconoscimenti con ricerca vettoriale
        print("sdas")           
        


    #scrivi qui gli slot
        








# # INIZIALIZZAZIONE DEL MODELLO PER ESTRAZIONE FEATURES FACCIALI, questa operazione è svolta in questo punto del codice e non dentro la classe img_data_processing essendo che è abbastanza pesante e sarebbe uno spreco di tempo enorme se questa venisse eseguita per processare una singola immagine (cosa che acadrebbe se fosse scritta nella classe img_data_processing) va detto che passare il modello in fase di istanza può limitare le prestazioni in quanto non è garantito che il modello abbia settaggi adeguati a processare la particolare immagine, per questo potrebbe essere utile inizializzare in questo punto più modelli con settaggi diversi oppure imporre nel progetto degli standard fissi per le immagini 
        # face_engine = FaceAnalysis(name="buffalo_l", providers=["CPUExecutionProvider"], det_thresh=0.5, det_size=(384, 384))
        # # ctx_id=-1 forza uso della CPU
        # face_engine.prepare(ctx_id=-1, det_thresh=0.5, det_size=(384, 384))


        # h = img_data_processing("X:/ProgettazioniPazze/progetto_foto/app_v1/archive/people/Angelina Jolie/001_fe3347c0.jpg", face_engine)
        # h.destroyed.connect(lambda o=None: print("Distrutto oggetto della classe img_data_processing. ", o.objectName() if o else o))






        # name = self.entry_form.lineEdit_name.text()
        # birthday = self.entry_form.dateEdit_birth.text()
        # # per simulare smp lo creo a mano ma nella realtà questo è prodotto da un elaborazione da parte di insightface
        # smp1 = 1
        


        # generazione del widgt nell'interfaccia che porta i dati prodotti dal processamento
        # self.person_data = Person_data(name, birthday, smp1)
        # self.layout.addWidget(self.person_data)