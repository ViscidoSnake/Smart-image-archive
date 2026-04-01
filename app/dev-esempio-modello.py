import os
import shutil

import importlib.resources
import sqlite3

from insightface.app import FaceAnalysis
import cv2

import numpy as np
from PIL.ExifTags import TAGS

from PySide6.QtCore import Slot, Signal, QObject

from img_data_processing_class import img_data_processing


def c_draw_bbox(img, faces):
    for face in faces:
        x1, y1, x2, y2 = face.bbox.astype(int)

        # bounding box
        cv2.rectangle(img, (x1, y1), (x2, y2), (0, 255, 0), 2)

        # keypoints
        # for x, y in face.kps:
        #     cv2.circle(img, (int(x), int(y)), 2, (0, 0, 255), -1)

    return img

def hammingDistance(a, b):
    if a is None or b is None:
        return None
    ai = int.from_bytes(a, "big", signed=False)
    bi = int.from_bytes(b, "big", signed=False)
    return (ai ^ bi).bit_count()



def recognition_faces(imgPath):

    app = FaceAnalysis(name="buffalo_l", providers=["CPUExecutionProvider"], det_thresh=0.5, det_size=(960, 960))
    # ctx_id=-1 forza uso della CPU
    app.prepare(ctx_id=-1, det_thresh=0.5, det_size=(960, 960))
    # carica immagine
    img = cv2.imread(imgPath)
    # ottieni volti 
    faces = app.get(img, max_num=0)
    # per ogni volto effettuo estrazione di embedding, bbox area e det_score, questi tre fattori saranno usati nella query al db per cercare una somiglianza tra embedding incognito e quelli presenti nel db

    # connessione al database, generazione del cursore e caricamento del modulo per calcolo vettoriale
    conn = sqlite3.connect("test.db")
    cur = conn.cursor()
    ext_path = importlib.resources.files("sqlite_vector.binaries") / "vector"
    conn.enable_load_extension(True)
    conn.load_extension(str(ext_path))
    conn.enable_load_extension(False)
    
    #spezzo in due execute perche condensando tutto in uno con executescript non avrei la possibilità di vedere come lavora vector_quantize
    # ricorda con executescript non pui ricevere nulla come risposta dal db quindi fetchall non funziona se hai questa necessita usa execute (vedi sotto). la init seguita poi dalla quantize è solo un esempio, questo è un test quindi qui le prestazioni non sono l'obbiettivo, per approfondire quando e come usare la quantize vedi il readme
    cur.executescript("""
    SELECT vector_init('people_embedding', 'embedding', 'dimension=512,type=FLOAT32,distance=cosine');
    SELECT vector_quantize('people_embedding', 'embedding', 'max_memory=50MB');
    """)

    # cur.execute("""
    # SELECT vector_init('people_embedding', 'embedding', 'dimension=512,type=FLOAT32,distance=cosine');
    # """)
    # cur.execute("""
    # SELECT vector_quantize('people_embedding', 'embedding', 'max_memory=50MB');
    # """)
    # print(f"numero di righe della tabella quntizzate: {cur.fetchall()}")
    

    for face in faces:
        detScore = face.det_score

        embedding = face.embedding 

        embeddingNorm = np.linalg.norm(embedding)

        x1, y1, x2, y2 = face.bbox
        larghezza = x2 - x1
        altezza = y2 - y1
        area = max(0, larghezza) * max(0, altezza)

        # print dei dati inerenti al volto
        print("-----face processing data-----")
        # print(f"det_score:{detScore}")
        # print(f"modulo embedding:{embeddingNorm}")
        # print(f"area bbox:{area}")
        # utile per stapare embedding sulla console in modo che poi si possa copiare e poi inserire in delle query fatte con DB brower
        strEmbedding = "[" + ", ".join(map(str, embedding.tolist())) + "]"
        # print(strEmbedding)
        print("------------------------------")

        #sparo la query di recognition, nota ricorda di passare area.item se in fase di registrazione salvi area come area.item
        cur.execute(
        """
            WITH calcCoeff AS (
                SELECT
                    v.rowid,
                    people.name,
                    v.distance,
                    abs(pe.bboxArea - ?) / (pe.embedding_norm) AS coeff
                FROM vector_full_scan_stream(
                        'people_embedding',
                        'embedding',
                        ?
                    ) AS v
                JOIN people_embedding AS pe ON pe.idE = v.rowid
                JOIN people ON people.idP = pe.idP
            ),
            calcWeightedMean AS (
                SELECT
                    name,
                    SUM(distance * coeff) / SUM(coeff) AS distanceWeightedMean
                FROM calcCoeff
                GROUP BY name
            )
            SELECT
                name,
                min(distanceWeightedMean) AS distanceWeightedMean
            FROM calcWeightedMean
            WHERE distanceWeightedMean < 0.6;
        """
        , (area.item(),embedding))

        print(f"risultato query recognition: {cur.fetchall()}")

        c_draw_bbox(img, [face])
        # mostra il file immagine generato e freez fin tanto che non si chiude la finestra
        cv2.imshow("Displayed Image", img)
        cv2.waitKey(0)
        cv2.destroyAllWindows()
    
    conn.close()








# funzione pensata unicamente per lo sviluppo, possiede delle fragilità importanti non essendo presenti vari controlli, in caso di parametri sbagliati crash o ancora peggio rovina del db (in termini di dati inseriti). La funzione registra un soggetto poi punta alla cartella ppath nella quale sono presenti file immagine che devono avere un solo volto, ogni volto viene registrato nel db e associato al soggetto inizialmente registrato. Molto importante garantire che il soggetto non esista già nel db (quindi stesso nome) e anche che il nome dei file processati siano diversi da quelli già presenti nel db, in entrambi questi casi errore lanciato dal db.
# Scenario di utilizzo: riempire con dati di qualità non perfettamente nota il db 
def dev_append_data_in_files_and_people_embedding(ppath, number, pname, pyear):
    conn = sqlite3.connect("db.db")
    cur = conn.cursor()
    # oggetto face analysis con det_size buono per questo particolare dataset dove i volti sono primipiani con volti di circa 400 x 400 
    face_engine = FaceAnalysis(name="buffalo_l", providers=["CPUExecutionProvider"], det_thresh=0.5, det_size=(384, 384))
    # ctx_id=-1 forza uso della CPU
    face_engine.prepare(ctx_id=-1, det_thresh=0.5, det_size=(384, 384))

    # inserimento del soggetto nel db
    cur.execute("""
        INSERT INTO people (name, year)
        VALUES (?, ?)
    """, (pname, pyear))
    conn.commit()
    # query per ottenere idP assegnato al soggetto
    cur.execute("""
        SELECT p.idP
        FROM people AS p
        WHERE p.name == ?;
    """, (pname,))
    idP = cur.fetchone()[0]


    imgs = os.listdir(ppath)
    i=0
    for img in imgs:
        if(i == number-1): break
        # imgsObj.append(img_data_processing(pphath + '/' + img, face_engine))
        imgO = img_data_processing(ppath + '/' + img, face_engine)
        # per sviluppo collego ogni volta il segnale distruzione
        imgO.destroyed.connect(lambda o=None: print("Distrutto oggetto della classe img_data_processing:", o.objectName() if o else o))
        
        # inserimento del file nel db
        cur.execute("""
            INSERT INTO files (name, nickname, dhash, width, height, n_faces, datetime_file)
            VALUES (?, ?, ?, ?, ?, ?, ?)
        """, (imgO.file_name, imgO.file_nickname, imgO.dhash, imgO.width, imgO.height, imgO.n_faces, imgO.datetime_file))
        conn.commit()
        # query per ottenere idF assegnato al file
        cur.execute("""
            SELECT f.idF
            FROM files AS f
            WHERE f.name == ?;
        """, (imgO.file_name,))
        imgO.idF_assigned = cur.fetchone()[0]


        # inserimento del viso nel db 
        face_data = imgO.faces_data[0]
        face_data.idP_assigned = idP
        cur.execute("""
            INSERT INTO people_embedding (idF, idP, embedding, embedding_norm, bbox_area, det_score, bbox_coord)
            VALUES (?, ?, ?, ?, ?, ?, ?)
        """, (imgO.idF_assigned, face_data.idP_assigned, face_data.embedding.tobytes(), float(face_data.embedding_norm), float(face_data.bbox_area), float(face_data.det_score), face_data.bbox_coord.tobytes()))
        conn.commit()

        # (personImg, embedding.tobytes(), embeddingNorm.item(), area.item(),idP)
        i = i + 1

    conn.close()    






# allora elenco dei passi da seguire:
# 0) passare alla funzione nome anno e cartella (come percorso assoluto) dove sono le immagini del volto da registrare
# 1) query al db per verificare se il nome inserito esiste già registrato nel db, se esiste INTERROMPO il processo, verifico anche che la cartella puntata abbia al suo interno almeno 1 file.
# 2) per ogni immagine estrazione dei metadati con exiftool quindi h w data scatto e nome del file
# 3) per ogni immagine generazione dei dati embedding, bboxArea norma embedding e numero di visi(modulo insightface)
# 4) per ogni immagine generazione dhash
# 5) per ogni immagine query vettoriale nella tabella files sul campo phash per verificare la presenza di immagini molto simili a quella processata tra quelle presenti nel database, come risultato della query ci sono varie opzioni, se non esiste somiglianza allora scrivo nessuna somiglianza se invece è sospetta quindi hamming_distance tra 1 e 10 potrei pensare di lasciare la lista di foto in termini ovviamente di idF in modo tale che in implementazioni future poi da questi idF si possa rifare una query per vedere tali immagini
# 6) per ogni immagine query vettoriale nella tabella people sul campo embedding per verificare la possibile somiglianza con gli embedding presenti nel database, anche qui il risultato potrebbe essere fornito in termini di idP se esistono somiglianze
# 7) completamento dei dati legati al file, quindi scrittura del file_nickname (in questo caso è GOLDSAMPLE_<nome del nuovo soggetto inserito>)

# 8)dopo tutta questa lavorazione fatta per ciascuna immagine è necessario mostrare i dati prodotti all'utente, nota che non deve essere permessa nessuna modifica dei dati!

# 9) l'utente conferma o annulla tutto il processo
    # 9.1-conferma) la prima cosa è creare il record nella tabella people e poi rieffetuare una query per ottenere idP assegnato dal db, (questo viene salvato in un menbro della classe)
    # 9.2-conferma) per ogni immagine è necessario creare un record nella tabella files e poi rieffetuare una query per ottenere idF assegnato dal db, predi anche la data di inserimeto assegnata, IMPORTANTE in questa operazione potrebbero sorgere problemi con il nome del file essendo questo UNIQUE nel db. Pertanto è necessario trovare un nome unique accettato dal db che poi però dovrà essere sovrascritto al nome del file. (idF e nuovo nome del file vanno salvati in un menbro della classe).
    # 9.3-conferma) creare per ogni immagine un record nella tabella people_embedding, nel fare questo vengono utilizzati anche idP e idF precedentemente ottenuti
    # 9.1-annulla) tutti gli oggetti creati vengono ditrutti
# 10-conferma) per ogni immagine si procede allo spostamento nella cartella applicazione, nel fare questo viene controllato se il particolare file deve essere rinominato
# 11-conferma) per ogni immagine print dei dati finali che permettono individuazione nel db


# di base contiene il codice per effettuare la registrazione di un soggetto nel db, nota che non sono imposti limiti minimi di immagini e anche dimensioni delle immagini, considerando i settaggi attuali del motore di ricerca volti una dimensione ottimale è 400x400. si possono ritrovare tutti gli 11 step sopra desctitti, nell'integrazione con interfaccia grafica potrebbero verificarsi modifiche ma minime, il core della logica è scritto qui
def register_person_in_db(pname, pbirthday, pphath):
    # APERTURA CONNESSIONE AL DB
    conn = sqlite3.connect("db.db")
    # carico nel db la funzione per il calcolo della distanza hamming
    conn.create_function("hammingDistance", 2, hammingDistance)
    # varie righe per attivazione del modulo per la ricerca vettoriale
    ext_path = importlib.resources.files("sqlite_vector.binaries") / "vector"
    conn.enable_load_extension(True)
    conn.load_extension(str(ext_path))
    conn.enable_load_extension(False)
    # creazione cursore
    cur = conn.cursor()
    cur.executescript("""
    SELECT vector_init('people_embedding', 'embedding', 'dimension=512,type=FLOAT32,distance=cosine');
    SELECT vector_quantize('people_embedding', 'embedding', 'max_memory=50MB');
    """)
    # INIZIALIZZAZIONE DEL MODELLO PER ESTRAZIONE FEATURES FACCIALI, questa operazione è svolta in questo punto del codice e non dentro la classe img_data_processing essendo che è abbastanza pesante e sarebbe uno spreco di tempo enorme se questa venisse eseguita per processare una singola immagine (cosa che acadrebbe se fosse scritta nella classe img_data_processing) va detto che passare il modello in fase di istanza può limitare le prestazioni in quanto non è garantito che il modello abbia settaggi adeguati a processare la particolare immagine, per questo potrebbe essere utile inizializzare in questo punto più modelli con settaggi diversi oppure imporre nel progetto degli standard fissi per le immagini 
    face_engine = FaceAnalysis(name="buffalo_l", providers=["CPUExecutionProvider"], det_thresh=0.5, det_size=(384, 384))
    # ctx_id=-1 forza uso della CPU
    face_engine.prepare(ctx_id=-1, det_thresh=0.5, det_size=(384, 384))

    # step 1
    cur.execute(
        """
            SELECT name
            FROM people AS p
            WHERE p.name == ?;
        """, (pname,))
    
    imgs = os.listdir(pphath)
    
    if((len(cur.fetchall()) != 0) or (len(imgs) == 0)):
        # chiusura della connessione e stop esecuzione
        conn.close()
        return
    
    # un po scomodo ma conviene lavorare dentro un unico for essendo tutte operazioni identiche per ogni file immagine
    imgsObj = []
    for img in imgs:
        # step 2 - 3 - 4
        # imgsObj.append(img_data_processing(pphath + '/' + img, face_engine))
        imgO = img_data_processing(pphath + '/' + img, face_engine)
        # per sviluppo collego ogni volta il segnale distruzione
        imgO.destroyed.connect(lambda o=None: print("Distrutto oggetto della classe " \
        "img_data_processing:", o.objectName() if o else o))

        # prima di continuare ha senso impostare il membro selected_for_processing, qui il discrimanate è il numero di volti trovati nell' immagine quindi solo se l'oggetto possiede esattamente n_faces == 1 allora il file è idoneo ed ha senso procedere per questo con gli step successivi, in caso contrario selected_for_processing resta False viene aggiunto alla lista di oggetti immagine e il ciclo for viene forzato ad adare avanti
        if(imgO.n_faces == 1):
            imgO.selected_for_processing = True
        else:
            imgsObj.append(imgO)
            continue
            

        # step 5
        # il valore della soglia impostato a 10 è stato scelto senza fare prove con immagini reali ma solo piccoli test di qualche immagine con variazioni della luminosità, per dataset grandi è chiaro che conviene diminuire la soglia
        cur.execute(
            """
                SELECT 
                    f.idF,
                    hammingDistance(f.dhash, ?) AS hammdist
                FROM files AS f
                WHERE hammdist <= 10;
            """, (imgO.dhash,))
        
        imgO.idF_similarity = cur.fetchall()
        

        # step 6
        # è chiaro che serve un for ulteriore che cicla su ogni oggetto della lista in imgO.faces_data
        for face_data in imgO.faces_data:
            
            cur.execute(
            """
                WITH calcCoeff AS (
                    SELECT
                        p.name,
                        p.idP,
                        pe.idE,
                        pe.idF,
                        v.rowid,
                        v.distance,
                        (abs(pe.bbox_area - ?)/248400)+(abs(pe.det_score - ?)) / (((pe.embedding_norm + ?)-34)/45-34) AS coeff
                    FROM vector_full_scan_stream(
                            'people_embedding',
                            'embedding',
                            ?
                        ) AS v
                    JOIN people_embedding AS pe ON pe.idE = v.rowid
                    JOIN people AS p ON p.idP = pe.idP
                ),
                calcWeightedMean AS (
                    SELECT
                        name,
                        SUM(distance * coeff) / SUM(coeff) AS distanceWeightedMean
                    FROM calcCoeff
                    GROUP BY idP
                )
                SELECT *
                FROM calcWeightedMean
                WHERE distanceWeightedMean < 0.6
                ORDER BY distanceWeightedMean;
            """
            , (float(face_data.bbox_area), float(face_data.det_score), float(face_data.embedding_norm), face_data.embedding.tobytes()))
            
            face_data.people_name_similarity = cur.fetchall()

        
        # step 7
        imgO.file_nickname = "GOLDSAMPLE_" + pname


        imgsObj.append(imgO)


    #step 8 uso un ciclo for su imgsObj per creare card grafiche che mostrano i dati nell'interfaccia, in effetti si può sfruttare il for sopra ma è una rottura e concettualmente si mescolano le fasi di estrazioni dati con quella di output a schermo
    for imgO in imgsObj:
        imgO.printData()
        # ....


    # ------
    # molto probabile che questo codice finirà in un blocco a parte, uno slot che risponde agli eventi all'interfaccia

    # 9.1-conferma) grazie al controllo effetuato inizialmente sul nome il processo di inserimento può avveniore in modo diretto
    cur.execute("""
        INSERT INTO people (name, year)
        VALUES (?, ?)
    """, (pname, pbirthday))
    conn.commit()
    # query per ottenere idP assegnato al soggetto
    cur.execute("""
        SELECT p.idP
        FROM people AS p
        WHERE p.name == ?;
    """, (pname,))
    idP = cur.fetchone()[0]
    

    # 9.2-conferma)
    # per come viene gestito qui il new_file_name in pratica se i membri file_name e new_file_name sono uguali nell'oggetto imgO allora significa che non si è verificata eccezione e quindi il file non deve essere successivamente rinominato altrimenti si
    for imgO in imgsObj:
        # blocco try except per sfruttare l'errore emesso dal db in caso di file avente nome identico a uno tra quelli già registrati nel db
        original_file_name = imgO.file_name
        new_file_name = original_file_name
        success = False
        i = 1
        while success == False:
            try:
                # tentativo di inserimento del file nel db
                cur.execute("""
                    INSERT INTO files (name, nickname, dhash, width, height, n_faces, datetime_file)
                    VALUES (?, ?, ?, ?, ?, ?, ?)
                """, (new_file_name, imgO.file_nickname, imgO.dhash, imgO.width, imgO.height, imgO.n_faces, imgO.datetime_file))
                conn.commit()

                imgO.new_file_name = new_file_name
                
                success = True

            except sqlite3.IntegrityError:
                # modifico il file name concatenando un numero
                # file_name = file_name + '_' + str(i)
                # i = i + 1
                f = original_file_name.split(".")
                new_file_name = f[0] + "_" + str(i) + "." + f[1]
                i = i + 1
                # nota importante: per la scelta del nuovo nome da dare al file una volta spostato nella cartella applicazione l'approccio sopra funziona perchè viene processata una sola immagine alla volta ovvero quindi il database si aggiorna dopo ogni inserimento di file. Questo funzionamento evita di gestire situazioni come nomi dei file spostati identici nella cartella di sistema (chiaramente sarebbe un grosso problema) essendo che dopo ogni immagine il db si aggiorna e quindi ogni file è come se vedesse lo stato in tempo reale dei file nella cartella applicazione

        
        # query per ottenere idF assegnato al file e anche data di inserimento
        cur.execute("""
            SELECT f.idF, f.datetime_insertion
            FROM files AS f
            WHERE f.name == ?;
        """, (imgO.new_file_name,))
        imgO.idF_assigned, imgO.datetime_insertion = cur.fetchone()



        # 9.3-conferma)
        # metto un for nidificato ma in realtà non serve in questo caso perche tanto per una singola immagine ho un solo volto, comunque
        for face_data in imgO.faces_data:
            cur.execute("""
                INSERT INTO people_embedding (idF, idP, embedding, embedding_norm, bbox_area, det_score, bbox_coord)
                VALUES (?, ?, ?, ?, ?, ?, ?)
            """, (imgO.idF_assigned, idP, face_data.embedding.tobytes(), float(face_data.embedding_norm), float(face_data.bbox_area), float(face_data.det_score), face_data.bbox_coord.tobytes()))
            conn.commit()


        # step 10
        # move del file nella directory applicazione e rinominazione usando new_file_name, tecnicamente la funzione move fa copia del file nella cartella di destinazione, poi rinomina di questo con new_file_name e alla fine rimozione del file dalla cartella di origine, questa pipeline va bene, sarebbe stata probblematica se la copia e poi rinomina fossero avvenute nella stessa cartella sorgente. 
        dst_path = shutil.move(imgO.img_path, "X:/ProgettazioniPazze/progetto_foto/logic-app-v1/archive/app_archive/" + imgO.new_file_name)

        # step 11, anche qui dipende molto da come strutturo interfaccia grafica, tutti i dati interessanti da mostrare si trovano memorizzati nell'oggetto, in più si potrebbe mettere anche dst_path che riporta il percorso completo al file processato spostato nella cartella di applicazione
        # ....


    # ------
    

    conn.close()
    
    
    


def main():
    # append_data_in_people_embedding("./archive/people/Nicole Kidman",6,10)
    # recognition_faces("./archive/mixed/gr2.jpg")
    # append_data_in_people_embedding("./archive/mixed/gr1.png")
    # extract_metadata_from_img("./archive/miscellaneous/Olympus_C8080WZ.jpg")
    register_person_in_db("jonny","2002-11-11","X:/ProgettazioniPazze/progetto_foto/logic-app-v1/archive/test")
    # dev_append_data_in_files_and_people_embedding("./archive/people/Nicole Kidman", 30, "Nicole", "2012-12-12")


if __name__ == "__main__":
    main()

