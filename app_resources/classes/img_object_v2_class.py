from insightface.app.common import Face
import numpy as np
from pathlib import Path
import cv2
import copy

class new_Face(Face):
    def __init__(self, d=None, **kwargs):
        super().__init__(d=None, **kwargs)

        # assegna un indice all'oggetto viso, più per debug
        self.index = kwargs["index"]
        
        self.name = "UNRECOGNIZED"

        # print(self.__dict__)
        
    def getDim(self):
        x1, y1, x2, y2 = self.bbox
        w = x2 - x1
        h = y2 - y1
        return w, h
    
    # metodo per fare la clonazione di un oggetto, necessaria questa implementazione perche deepcopy per qualche motivo fallisce
    def clone(self):
        new_face_o = new_Face(index = self.index)
        new_face_o.name = self.name
        new_face_o.bbox = copy.deepcopy(self.bbox)
        new_face_o.kps = copy.deepcopy(self.kps)
        new_face_o.embedding = copy.deepcopy(self.embedding)
        new_face_o.det_score = self.det_score
        return new_face_o

        
    
 

    
class img_obj():
    def __init__(self, img_path):
        
        self.path = img_path
        self.img_Nch = -1 # canali dell'immagine, non lo metto in metadata

        self.first_detection = []
        self.second_detection = []
        self.recognition = []

        self.second_detection_faces_features = []
        self.first_detection_faces_features = []
        self.recognition_faces_features = []

        # è utile memorizzarla perche con questa posso calcolare in ogni momento il det_size ottimale e anche generare la maschera per seconda detection senza bisogno di memorizzare nulla
        self.first_detection_index_selected = []

        # tutti i valori che vedi sono quelli di default, allora puoi inseire senza problemi voci al vocabolario ma poi se vuoi renderle visibili nella ui devi ritoccare la classe img_metadata
        self.metadata = {
           "file_name": "-",
           "datetime": "1800-01-01",
           "size": (-1,-1),
           "faces_n": -1,
           "new_file_name": "-",
           "nickname": "-",
           "ins_datetime": "1800-01-01",
           "n_ch": -1,
           "idF": -1
        }
    
        # allora non è che sia fondamentale però appena l'oggetto viene creato conviene almeno estrarre metadati basilari come nome del file e dimensioni in px e numero di canali
        p = Path(self.path)
        self.metadata["file_name"] = p.name
        shape = self.get_cv().shape
        self.metadata["size"] = shape[:2]
        l = len(shape)
        if l == 2:
            self.metadata["n_ch"] = 1 #valore dei canali standard per immagine in bianco e nero
        elif l == 3:
            self.metadata["n_ch"] = shape[2]

    def get_cv(self):
        return  copy.deepcopy(cv2.imread(self.path))

    def get_metadata(self):
        return copy.deepcopy(self.metadata)

    # restituisce l'immagine con una maschera applicata, la maschera è molto semplice, in pratica rimpiazza con rettangoli neri i volti non selezionati dopo la prima detection in modo da velocizzare la seconda detection ovvero quella raffinata. La funzione da priorità sempre ai volti selezionati quindi se due volti sono vicini (boundingbox sovrapposte) allora la parte sovrapposta non subisce oscuramento 
    def get_img_masked(self):

        img = self.get_cv()
        if (self.metadata["n_ch"] == 1):
            img = cv2.cvtColor(img, cv2.COLOR_GRAY2BGR)

        # algoritmo molto semplice, estrazione dall'immagine dei volti da mantenere poi oscuramento degli altri e infine ripristino dei volti da mantenere, operazione importante nei casi di volti vicini tra loro
        good_faces = []
        for face in self.first_detection:
            x1, y1, x2, y2 = map(int, face.bbox)
            if face.index in self.first_detection_index_selected:
                face_roi = img[y1:y2, x1:x2].copy()
                good_faces.append({"roi":face_roi, "coord":(x1, y1, x2, y2)})
        
        for face in self.first_detection:
            x1, y1, x2, y2 = map(int, face.bbox)
            if not face.index in self.first_detection_index_selected:
                cv2.rectangle(img, (x1, y1), (x2, y2), (0,0,0), -1)

        for face in good_faces:
            x1, y1, x2, y2 = face["coord"]
            img[y1:y2, x1:x2] = face["roi"]
        

        # cv2.imshow("sd", img)
        # cv2.waitKey(0)
        # cv2.destroyAllWindows()

        # puoi tornare img diretto tanto questa è già una copy di quella originale
        return img
    
    # devi scrivere una funzione che estrae più metadati dall'immagine

    # funzione che carica una lista passata con i dati di bboxes e kpss
    def face_list_loader(self, list, bboxes, kpss):
        if (bboxes.shape[0] != 0):
            
            for i in range(bboxes.shape[0]):
                bbox = bboxes[i, 0:4]

                det_score = bboxes[i, 4]
                
                kps = None
                if kpss is not None:
                    kps = kpss[i]
                
                face = new_Face(bbox=bbox, kps=kps, det_score=det_score, index=i)

                list.append(face)
        else:
            # caso in cui bboxes è vuoto, lascio un print per debug ma di base nell'esecuzione self.raw_face_detection resta vuoto
            print("Nessun volto rilevato nell'immagine")
    def load_faces_list(self, l_type, bboxes=[], kpss=[], original_list=[]):
        l = []
        if(l_type == "first detection"):
            l = self.first_detection
            self.face_list_loader(l, bboxes, kpss)
        elif(l_type == "second detection"):
            l = self.second_detection
            self.face_list_loader(l, bboxes, kpss)
        elif(l_type == "recognition"):
            l = self.recognition
            for e in original_list:
                l.append(e.clone())
            
    # funzione usata per restituire uno dei 3 membri lista conteneti i volti  
    def get_faces_list(self, l_type):
        a = []
        if(l_type == "first detection"):
            a = self.first_detection
        elif(l_type == "second detection"):
            a = self.second_detection
        elif(l_type == "recognition"):
            a = self.recognition

        l = []
        for e in a:
            l.append(e.clone())
        
        return l

    # index_selector_list lista di indici riferita ai volti presenti in self.first_detection
    def get_optimal_det_size(self, index_selector_list):
        self.first_detection_index_selected = index_selector_list
        
        smallest_face_dim = -1
        for face in self.first_detection:
            if face.index in index_selector_list:
                a = min(face.getDim())
                # print(a)
                if (smallest_face_dim < 0) or (a < smallest_face_dim):
                    smallest_face_dim = a
        
        # print(smallest_face_dim)
        
        # calcolo il det size ottimale
        k = smallest_face_dim/80 # rapporto di riduzione
        # print(k)
        smallest_img_dim = min(self.metadata["size"])
        if(k<1):
            print("elaborazione non ottimale, volto con dimensioni minori di 80x80")
            optimal_det_size = int(((smallest_img_dim + 31) // 32) * 32)
        else:
            optimal_det_size = int((((smallest_img_dim/k) + 31) // 32) * 32)
        
        return (optimal_det_size, optimal_det_size)

    # funzione che prende i dati dei visi della seconda detection + i metadati dell'immagine per calcolare le feature di qualità, la get ritorna come deep copy la lista
    def extract_faces_features(self, l_type):
        # apro immagine perche mi serve per il calcolo della nitidezza saturazione e contrasto dei volti
        img_cv = self.get_cv()
        n_ch = len(img_cv.shape)

        a = []
        b = []
        if(l_type == "first detection"):
            a = self.first_detection_faces_features
            b = self.first_detection
        elif(l_type == "second detection"):
            a = self.second_detection_faces_features
            b = self.second_detection
        elif(l_type == "recognition"):
            # è il caso più particolare si può procedere nel modo classico andando a rieseguire i calcoli per gli oggetti presenti nella lista self.recognition però è un spreco di risorse perche tutti gli oggetti presenti in self.recognition sono identici a quelli in self.second_detection tranne per una voce ovvero l'embedding, allora un modo è prendere da recognition gli indici dei volti poi copiare da second_detection_faces_features i dati e aggiungerci la voce embedding, magari anche la voce name, fattibile ma per ora rifaccio i calcoli per sempicità
            a = self.recognition_faces_features
            b = self.recognition
        else: return

        
        for face in b:
            # coordinate della bounding box, mi serve perche poi questi punti dovranno essere usati per il disegno sull'immagine
            bbox_coord = copy.deepcopy(face.bbox)
            # coordinate dei punti di occhi bocca e naso, mi serve perche poi questi punti dovranno essere usati per il disegno sull'immagine
            kps_coord = copy.deepcopy(face.kps)
            # prendo anche index del volto, anche questo molto importante per far capire corrispondenza volto-dati
            index = copy.deepcopy(face.index)

            # ---- INIZIO estrazione e normalizzazione features ----

            # dimensione del viso in px
            x1, y1, x2, y2 = bbox_coord
            w = int(x2-x1)
            h = int(y2-y1)
            size = (w,h)

            # features estratte grazie ai punti di occhi naso e bocca
            le = kps_coord[0]
            re = kps_coord[1]
            n = kps_coord[2]
            lm = kps_coord[3]
            rm = kps_coord[4]
            
            d_eye = np.linalg.norm(le-re)
            # volto centrato
            mid_e = (le[0]+re[0])/2
            general_centering = abs(n[0] - mid_e)/d_eye
            n_general_centering = 1 - np.clip((general_centering - 0.0)/(0.15 - 0.0), 0.0, 1.0)
            weighted_general_centering = 0.15 * n_general_centering

            # simmetria della bocca
            d1 = np.linalg.norm((rm - n))
            d2 = np.linalg.norm((lm - n))
            mouth_centering = abs(d1 - d2) / d_eye
            n_mouth_centering = 1 - np.clip((mouth_centering - 0.0)/(0.20 - 0.0), 0.0, 1.0)
            weighted_mouth_centering = 0.1 * n_mouth_centering

            # stima della rotazione orizzontale
            ya1 = np.linalg.norm((le - n))
            ya2 = np.linalg.norm((re - n))
            yaw = abs(ya1 - ya2) / d_eye
            n_yaw = 1 - np.clip((yaw - 0.0)/(0.20 - 0.0), 0.0, 1.0)
            weighted_yaw = 0.15 * n_yaw

            # stima della rotazione verticale
            roll = np.arctan2(re[1]-le[1], re[0]-le[0])
            roll_deg = np.degrees(roll)
            n_roll = 1 - np.clip((roll_deg - 0.0)/(0.20 - 0.0), 0.0, 1.0) 
            weighted_roll = 0.1 * n_roll


            roi = img_cv[ int(y1):int(y2), int(x1):int(x2) ]
            gray_roi = roi
            if n_ch > 2: gray_roi = cv2.cvtColor(roi, cv2.COLOR_BGR2GRAY)

            # feature nitidezza ottenuta attraverso laplaciano del volto
            lap = cv2.Laplacian(gray_roi, cv2.CV_64F)
            blur = lap.var()
            n_blur = np.clip((blur - 20.0)/(200.0 - 20.0), 0.0, 1.0)
            weighted_blur = 0.2 * n_blur

            #feature saturazione 
            low_sat  = np.mean(gray_roi < 20)
            high_sat = np.mean(gray_roi > 235)
            sat = (low_sat, high_sat)
            n_sat = 1- min(low_sat+high_sat, 1.0)
            weighted_sat = 0.15 * n_sat
            
            #feature contrasto
            p5, p95 = np.percentile(gray_roi, [5, 95])
            contrast_range = p95 - p5
            n_contrast_range = np.clip((contrast_range - 30.0)/(150.0 - 30.0), 0.0, 1.0) 
            weighted_contrast_range = 0.15 * n_contrast_range

            # ---- FINE estrazione e normalizzazione features ----

            # calcolo dello score di qualità
            quality_score = 0.0
            if min(size) > 70: 
                quality_score = weighted_general_centering + weighted_mouth_centering + weighted_roll + weighted_yaw + weighted_contrast_range + weighted_sat + weighted_blur
            

            # metto tutte le feature in un dizionario, ci metto anche index e le coordinate dei punti della bbox e kpss
            features = {
                "index" : index,
                "bbox_coord" : bbox_coord,
                "kps_coord" : kps_coord,
                "size" : size,
                "general_centering" : (general_centering, n_general_centering),
                "mouth_centering" : (mouth_centering, n_mouth_centering),
                "yaw" : (yaw, n_yaw),
                "roll_deg" : (roll_deg, n_roll),
                "blur" : (blur, n_blur),
                "sat" : n_sat, # saturazione è giù normalizzato, mando la tupla come standard
                "contrast_range" : (contrast_range, n_contrast_range),
                "quality_score" :  quality_score
            }

            # se è il caso recognition si aggiungono due voci in più
            if (l_type == "recognition"):
                features["embedding"] = copy.deepcopy(face.embedding)
                features["name"] = copy.deepcopy(face.name)
            
            # a questo punto metto il dizionario features nella lista delle features
            a.append(features)

    def get_faces_features(self, l_type):
        a = []
        if(l_type == "first detection"):
            a = self.first_detection_faces_features
        elif(l_type == "second detection"):
            a = self.second_detection_faces_features
        elif(l_type == "recognition"):
            a = self.recognition_faces_features

        return copy.deepcopy(a)