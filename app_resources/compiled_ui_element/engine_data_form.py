from PySide6.QtWidgets import QWidget
from PySide6.QtCore import Slot, Signal

from .ui_engine_data_form import Ui_Engine_data_form

# graficamente è una roba oscena

class Engine_data_form(QWidget, Ui_Engine_data_form):
    def __init__(self):
        super().__init__()
        self.setupUi(self)

        self.data = {
            "det_threshold" : -1,
            "det_size" : (-1,-1)
        }

        self.spinBox_det_size.lineEdit().setReadOnly(True)
        self.doubleSpinBox_det_threshold.lineEdit().setReadOnly(True)

    #public
    # metodo per ottenere i dati inseriti nell'interfaccia, ultra facile non ho voglia di mettermi a modificare i vari segnali con slot appositi
    def get_all_data(self):
        self.data["det_threshold"] = self.doubleSpinBox_det_threshold.value()
        self.data["det_size"] = (self.spinBox_det_size.value(), self.spinBox_det_size.value())
        # restituisco una copia
        return self.data.copy()
