import os
import shutil
import importlib.resources
import sqlite3
from insightface.app import FaceAnalysis
import cv2
import numpy as np
from PIL.ExifTags import TAGS
from PySide6.QtCore import Slot, Signal, QObject


def face_an(pphath):

    app = FaceAnalysis(name="buffalo_l", providers=["CPUExecutionProvider"], det_thresh=0.5, det_size=(960, 960))
    app.prepare(ctx_id=-1, det_thresh=0.5, det_size=(224, 224))
    # carica immagine
    pimgs = os.listdir(pphath)
    # un po scomodo ma conviene lavorare dentro un unico for essendo tutte operazioni identiche per ogni file immagine
    for pimg in pimgs:
        
        img = cv2.imread(pphath + '/' + pimg)
        faces = app.get(img, max_num=0)
    
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
            print(face)
            # print(f"det_score:{detScore}")
            # print(f"modulo embedding:{embeddingNorm}")
            # print(f"area bbox:{area}")
            # utile per stapare embedding sulla console in modo che poi si possa copiare e poi inserire in delle query fatte con DB brower
            # strEmbedding = "[" + ", ".join(map(str, embedding.tolist())) + "]"
            # print(strEmbedding)
            print("------------------------------")

            
        cv2.imshow("Displayed Image", img)
        cv2.waitKey(0)
        cv2.destroyAllWindows()
    


            















def main():
    # append_data_in_people_embedding("./archive/people/Nicole Kidman",6,10)
    # recognition_faces("./archive/mixed/gr2.jpg")
    # append_data_in_people_embedding("./archive/mixed/gr1.png")
    # extract_metadata_from_img("./archive/miscellaneous/Olympus_C8080WZ.jpg")
    face_an("X:/ProgettazioniPazze/progetto_foto/app_v1/archive/mixed")
    # dev_append_data_in_files_and_people_embedding("./archive/people/Nicole Kidman", 30, "Nicole", "2012-12-12")



if __name__ == "__main__":
    main()