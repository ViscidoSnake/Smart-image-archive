import sys
from PySide6.QtWidgets import QApplication

# allora la MainWindow_ref scritta in main_window_ref.py sarebbe un modello test usato per provare vari widget, invece la gui effettiva si trova in main_window.py quindi basta che il from punti a tale file, non devi modificare altro qui.
from .main_window import MainWindow

app = QApplication(sys.argv)

window = MainWindow(app)
window.show()

app.exec()
