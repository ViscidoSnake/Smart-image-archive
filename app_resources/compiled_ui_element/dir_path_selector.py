from PySide6.QtWidgets import QWidget, QFileDialog
from PySide6.QtCore import Slot, Signal

from .ui_dir_path_selector import Ui_Dir_path_selector

# graficamente è una roba oscena

class Dir_path_selector(QWidget, Ui_Dir_path_selector):
    def __init__(self):
        super().__init__()
        self.setupUi(self)

        # per test---
        self.le_dir_path_selected.setText(r"X:\ProgettazioniPazze\progetto_foto\app_v1\archive\mixed")
        # -----

        self.btn_dir_path_selector.clicked.connect(self.dir_selector)

    
    def dir_selector(self):
        # Apre la finestra di dialogo per selezionare solo cartelle
        directory = QFileDialog.getExistingDirectory(
            self,
            "Seleziona la cartella di destinazione",
            "", # Lasciando vuoto parte dalla cartella dell'utente o dall'ultima usata
            QFileDialog.ShowDirsOnly | QFileDialog.DontResolveSymlinks
        )

        if directory:
            # Se l'utente non ha annullato, facciamo qualcosa con il percorso
            self.le_dir_path_selected.setText(directory)
    
        
        
    
    #scrivi qui gli slot
        