from PySide6.QtWidgets import QWidget
from PySide6.QtCore import Slot, Signal, QDate

from .ui_img_metadata import Ui_Img_metadata

# graficamente è una roba oscena

class Img_metadata(QWidget, Ui_Img_metadata):
    def __init__(self, img_metadata):
        super().__init__()
        self.setupUi(self)
        
        # appena creato provo subito a impostare i valori da mostrare
        self.update_text_fields(img_metadata)
        
        # strategia per mostrare un testo di default diverso da una data, questo accade quando la data è pari al minimo ovvero 01/01/1800
        self.dateEdit_datetime.setSpecialValueText("-")
    
    # questo metodo carica nell'oggetto presente nella ui tutti i valori passati attravers il dizionario img_metadata
    def update_text_fields(self, img_metadata):
        # appena creato provo subito a impostare i valori da mostrare
        self.lineEdit_file_name.setText(img_metadata["file_name"])
    
        if(img_metadata["datetime"] != "1800-01-01"):
            # se entro qui do per scontato che la data sia nel formato corretto quindi nienete verifica
            date = QDate.fromString(img_metadata["datetime"], "yyyy-MM-dd")
            self.dateEdit_datetime.setDate(date)

        w = img_metadata["size"][0]
        h =img_metadata["size"][1]
        self.lineEdit_size.setText(f"{str(w)} x {str(h)}")

        self.lineEdit_faces_n.setText(str(img_metadata["faces_n"]))

        self.lineEdit_new_file_name.setText(img_metadata["new_file_name"])
    
        self.lineEdit_nickname.setText(img_metadata["nickname"])

        if(img_metadata["ins_datetime"] != "1800-01-01"):
            # se entro qui do per scontato che la data sia nel formato corretto quindi nienete verifica
            date = QDate.fromString(img_metadata["ins_datetime"], "yyyy-MM-dd")
            self.dateEdit_ins_datetime.setDate(date)

        self.lineEdit_idF.setText(str(img_metadata["idF"]))

    # questo metodo restituisce come vocabolario tutti i dati scritti nel widget quindi praticamente nei text input, i dati che in origine erano di tipo numerico sono riconvertiti, le date sono riportate a modi stringa seguendo la formattazione standard yyyy-MM-dd. nota invece di creare un vocabolario nuovo potevi memorizzare img_metadata nell'oggetto e poi usarlo come scheletro essendo esso un dizionario però alla fine poi lo avresti dovuto comunque aggiornare come fatto sotto quindi non cambia molto 
    def get_all_data(self):
        data = {
           "file_name": self.lineEdit_file_name.text(),
           "datetime": self.dateEdit_datetime.date().toString("yyyy-MM-dd"),
           "size": (-1,-1),
           "faces_n": int(self.lineEdit_faces_n.text()),
           "new_file_name": self.lineEdit_new_file_name.text(),
           "nickname": self.lineEdit_nickname.text(),
           "ins_datetime": self.dateEdit_datetime.date().toString("yyyy-MM-dd"),
           "idF": int(self.lineEdit_idF.text()),
        }
        return data 

        


        
    
        
        
    
    #scrivi qui gli slot