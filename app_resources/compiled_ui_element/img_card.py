# nota, questa è una classe "grafica" nel senso che serve solo per mostrare i dati nell'interfaccia, non possiede file ui perche non è stata ottenuta dal designer

from PySide6.QtCore import (QCoreApplication, QDate, QDateTime, QLocale,
    QMetaObject, QObject, QPoint, QRect, Signal,
    QSize, QTime, QUrl, Qt)
from PySide6.QtGui import (QBrush, QColor, QConicalGradient, QCursor,
    QFont, QFontDatabase, QGradient, QIcon,
    QImage, QKeySequence, QLinearGradient, QPainter, QPen, QFontMetrics,
    QPalette, QPixmap, QRadialGradient, QTransform)
from PySide6.QtWidgets import (QApplication, QDateEdit, QHBoxLayout, QLabel,
    QLineEdit, QPushButton, QSizePolicy, QVBoxLayout, QTableWidget, QTableWidgetItem,
    QWidget)

import cv2
import numpy as np


from .img_metadata import Img_metadata

# sarebbe la class che effettivamente mostra l'immagine
class img_view(QLabel):

    def __init__(self, cv_img):
        super().__init__()
        self.original_pixmap = None
        self.bboxes = []  # Lista di dict: {'bbox': (x1,y1,x2,y2), 'color': QColor, 'label': str}
        self.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.setStyleSheet("border: 2px solid #cccccc;")

        rgb_image = cv2.cvtColor(cv_img, cv2.COLOR_BGR2RGB)
        
        # Ottieni dimensioni
        height, width, channel = rgb_image.shape
        bytes_per_line = channel * width
        
        # Crea QImage
        q_image = QImage(
            rgb_image.data,
            width,
            height,
            bytes_per_line,
            QImage.Format.Format_RGB888
        )
        
        # Converti a QPixmap
        self.original_pixmap = QPixmap.fromImage(q_image)
        # self.update_display()

    
    def update_display(self):
        if not hasattr(self, "rendered_pixmap"):
            pixmap = self.original_pixmap
        else:
            pixmap = self.rendered_pixmap

        if pixmap is None:
            return

        if self.width() <= 0 or self.height() <= 0:
            return

        scaled = pixmap.scaled(
            self.size(),
            Qt.AspectRatioMode.KeepAspectRatio,
            Qt.TransformationMode.SmoothTransformation
        )
        self.setPixmap(scaled)
    
    def resizeEvent(self, event):
        super().resizeEvent(event)
        self.update_display()

    # slot per gestire disegno bbox e punti del viso
    def draw_faces(self, faces_data):
        self.last_faces_data = faces_data

        if self.original_pixmap is None:
            return

        self.rendered_pixmap = self.original_pixmap.copy()
        painter = QPainter(self.rendered_pixmap)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)

        for face_data in faces_data:
            if not face_data["select"]:
                continue
            
            x1, y1, x2, y2 = map(int, face_data["bbox_coord"])
            # ---- BBOX ----
            painter.setPen(QPen(QColor(0, 255, 0), 3))
            painter.setBrush(Qt.BrushStyle.NoBrush)
            painter.drawRect(x1, y1, x2 - x1, y2 - y1)

            # ---- TESTO ----
            label = "N " + str(face_data["index"])
            # Font più grande e leggibile
            font = QFont()
            font.setPointSize(15)          # prova 12–16
            font.setBold(True)
            painter.setFont(font)
            # Metriche del testo
            metrics = QFontMetrics(font)
            text_width = metrics.horizontalAdvance(label)
            text_height = metrics.height()
            padding = 6
            # Rettangolo nero sotto la bbox
            rect_x = x1
            rect_y = y2 + 5
            rect_w = text_width + padding * 2
            rect_h = text_height + padding * 2
            # Background nero
            painter.setPen(Qt.PenStyle.NoPen)
            painter.setBrush(QColor(0, 0, 0))
            painter.drawRect(rect_x, rect_y, rect_w, rect_h)
            # scrittura Testo
            painter.setPen(QPen(QColor(255, 255, 255)))
            text_x = rect_x + padding
            text_y = rect_y + rect_h - padding - metrics.descent()
            painter.drawText(text_x, text_y, label)

            # ---- PUNTI DEL VISO ----
            painter.setBrush(QBrush(QColor(255, 0, 0)))
            for kp in face_data["kps_coord"]:
                painter.drawEllipse(QPoint(int(kp[0]), int(kp[1])), 4, 4)


        painter.end()
        self.update_display()





class table(QTableWidget):
    #signals
    table_state_changed = Signal(list)

    def __init__(self, faces_data):
        super().__init__()

        # lista visi vuota allora nessun dato da mostrare, niente tabella
        if len(faces_data) == 0: return

        # # modo un po brutto per scrivere intestazione della tabella ovvero prendo le chiavi del dict dove sono scritti i dati
        # ex = faces_data[0]
        # table_h = list(ex.keys())
        # table_h.insert(0, "select")
        # self.table_keys = table_h # chiavi degli oggetti dizionario che la tabella può mostrare

        # self.setColumnCount(len(table_h))
        # self.setHorizontalHeaderLabels(table_h)
        # self.horizontalHeader().setStretchLastSection(True)
        # self.verticalHeader().setVisible(False)

        # caricamento dei dati
        self.load_data(faces_data)

        # ogni volta che cambia un elemento nella riga della tabella trigger di un evento
        self.itemChanged.connect(self.collect_table_state)


    def collect_table_state(self):
        
        state = []
        for row in range(self.rowCount()):
            row_data = {
                "select": self.item(row, 0).checkState() == Qt.CheckState.Checked,
                "index": self.item(row, 1).data(Qt.ItemDataRole.UserRole),
                "bbox_coord" : self.item(row, 2).data(Qt.ItemDataRole.UserRole),
                "kps_coord" : self.item(row, 3).data(Qt.ItemDataRole.UserRole)
            }
            state.append(row_data)

        self.table_state_changed.emit(state)

        return state.copy()
    
    # usata per rimuovere tutte le righe dalla tabella per poi ripopolarla con i dati in faces_data
    def load_data(self, faces_data):
        # blocco il segnale itemChanged altrimenti succede un casino quando rimuvo item dalla tabella
        self.blockSignals(True)
        
        # self.clearContents()

        self.clear()

        # modo un po brutto per scrivere intestazione della tabella ovvero prendo le chiavi del dict dove sono scritti i dati
        ex = faces_data[0]
        table_h = list(ex.keys())
        table_h.insert(0, "select")
        self.table_keys = table_h # chiavi degli oggetti dizionario che la tabella può mostrare

        self.setColumnCount(len(table_h))
        self.setHorizontalHeaderLabels(table_h)
        self.horizontalHeader().setStretchLastSection(True)
        self.verticalHeader().setVisible(False)

        self.setRowCount(len(faces_data))
        
        # un if per ogni key altrimenti questa non viene visualizzata nella tabella, per versioni future da rivedere in modo da permettere all'utente dall'interfaccia quali dati vedere/non vedere
        for i in range (len(faces_data)):
            
            j=0
            for key in self.table_keys:

                if key == "select":
                    item = QTableWidgetItem()
                    item.setFlags(
                        Qt.ItemFlag.ItemIsUserCheckable |
                        Qt.ItemFlag.ItemIsEnabled
                    )
                    item.setCheckState(Qt.CheckState.Checked)
                    self.setItem(i, j, item)

                # inserisce nella tabella come dati, colonna invisibile
                elif(key == "bbox_coord") or (key == "kps_coord"):
                    item = QTableWidgetItem("x")
                    item.setData(Qt.ItemDataRole.UserRole, faces_data[i][key])
                    item.setFlags(Qt.ItemFlag.ItemIsEnabled | Qt.ItemFlag.ItemIsSelectable)
                    self.setItem(i, j, item)
                    self.setColumnHidden(j, True)
                
                # inserisce nella tabella come niente (no dati no testo), colonna invisibile
                elif(key == "embedding"):
                    item = QTableWidgetItem("x")
                    item.setFlags(Qt.ItemFlag.ItemIsEnabled | Qt.ItemFlag.ItemIsSelectable)
                    self.setItem(i, j, item)
                    self.setColumnHidden(j, True)

                # inserisce nella tabella come dato e come testo, colonna visibile
                elif(key == "index"):
                    item = QTableWidgetItem(str(faces_data[i]["index"]))
                    item.setData(Qt.ItemDataRole.UserRole, faces_data[i]["index"])
                    item.setFlags(Qt.ItemFlag.ItemIsEnabled | Qt.ItemFlag.ItemIsSelectable)
                    self.setItem(i, j, item)
                
                # inserisce nella tabella come testo con una certa formattazione, colonna non visibile
                elif(key == "size"):
                    e = faces_data[i]["size"]
                    # print(type(e[0]))
                    e_rounded = (round(e[0], 0), round(e[1], 0))
                    # e_str = f"Raw:{e_rounded[0]:.3f}  Normalized:{e_rounded[1]:.3f}" # troppo lunga, non pratica da mostrare...
                    e_str = f"W:{e_rounded[0]} H:{e_rounded[1]}"
                    item = QTableWidgetItem(e_str)
                    item.setFlags(Qt.ItemFlag.ItemIsEnabled | Qt.ItemFlag.ItemIsSelectable)
                    self.setItem(i, j, item)
                    self.setColumnHidden(j, True)

                # inserisce nella tabella come testo, colonna non visibile
                elif(key == "sat"):
                    e = round(faces_data[i][key], 3)
                    item = QTableWidgetItem(str(e))
                    item.setFlags(Qt.ItemFlag.ItemIsEnabled | Qt.ItemFlag.ItemIsSelectable)
                    self.setItem(i, j, item)
                    self.setColumnHidden(j, True)

                # inserisce nella tabella come testo, colonna visibile
                elif(key == "quality_score"):
                    e = round(faces_data[i][key], 3)
                    item = QTableWidgetItem(str(e))
                    item.setFlags(Qt.ItemFlag.ItemIsEnabled | Qt.ItemFlag.ItemIsSelectable)
                    self.setItem(i, j, item)
                
                # inserisce nella tabella come testo, colonna visibile
                elif(key == "name"):
                    item = QTableWidgetItem(faces_data[i][key])
                    item.setFlags(Qt.ItemFlag.ItemIsEnabled | Qt.ItemFlag.ItemIsSelectable)
                    self.setItem(i, j, item)

                # inserisce nella tabella come testo con una certa formattazione, colonna non visibile
                elif(key == "general_centering") or (key == "mouth_centering") or (key == "yaw") or (key == "roll_deg") or (key == "blur") or (key == "contrast_range"):
                    e = faces_data[i][key]
                    e_rounded = (round(e[0], 3), round(e[1], 3))
                    # e_str = f"Raw:{e_rounded[0]:.3f}  Normalized:{e_rounded[1]:.3f}" # troppo lunga, non pratica da mostrare...
                    e_str = f"N:{e_rounded[1]:.3f}"
                    item = QTableWidgetItem(e_str)
                    item.setFlags(Qt.ItemFlag.ItemIsEnabled | Qt.ItemFlag.ItemIsSelectable)
                    self.setItem(i, j, item)
                    # self.setColumnHidden(j, True)
                
                j=j+1

        self.blockSignals(False)
        self.collect_table_state()




























# la classe che contiene effettivamente tutti gli altri oggetti grafici
class img_card(QWidget):
    def __init__(self, cv_img, faces_data, img_metadata):
        super().__init__()
        # layout supremo
        self.layout = QVBoxLayout(self)

        self.setSizePolicy(
            QSizePolicy.Policy.Expanding,  
            QSizePolicy.Policy.Preferred   
        )
        # Imposta dimensioni max e min, con QSizePolicy.Policy.Preferred possono essere assunti tutti i valori intermedi. è una gestione estremamente semplicistica però santa lauren per rendere tutto dinamico è un lavoraccio. Aggiornamento, con expanding sembra funzionare tutto come dovrebbe
        # self.setMinimumSize(500, 500)
        # self.setMaximumSize(1200, 800)

        # inserisco nel layout supremo la scheda di metadati dell'immagine
        self.metadata_box = Img_metadata(img_metadata)
        self.layout.addWidget(self.metadata_box)

        # creo un layout dove metto immagine con affiancata la tabella
        self.img_and_tab_layout = QHBoxLayout()
        self.layout.addLayout(self.img_and_tab_layout)

        # crea effettivamente la zona dove l'imamgine è mostrata
        self.img_view = img_view(cv_img)
        self.img_and_tab_layout.addWidget(self.img_view)
        # creo la tabella
        self.img_table = table(faces_data)
        # con questa connessione ogni volta che si seleziona un volto dalla tabella le bbox sull' immagine vengono ridisegnate 
        self.img_table.table_state_changed.connect(self.img_view.draw_faces)
        # if sotto serve per disegnare i volti nella foto subito dopo la creazione della card, potevo farlo anche chiamando self.img_table.collect_table_state() però è un modo un po improprio perchè sto usando senza troppo controllo un metodo di una classe pensato per gestire internamente l'oggetto.
        if(self.img_table.rowCount() > 0):
            self.img_table.item(0,0).setCheckState(Qt.CheckState.Unchecked)
            self.img_table.item(0,0).setCheckState(Qt.CheckState.Checked)
        self.img_and_tab_layout.addWidget(self.img_table)


    # get che prende tutti i dati in self.metadata_box e li restituisce, valuta se mettere una funzione di filtro
    def get_all_metadata(self):
        return (self.metadata_box.get_all_data()).copy()
    
    # get per prendere i dati nella tabella, filtro supportato semplicissio: tupla con chiave valore come argomenti, se ce corrispondenza viene ineserit nella lista ritornata tutto il dizionario. se nel filtro il primo valore della tupla è 0 allora return di tutti i dati. se nel filtro il primo argomento è una chiave che non esiste nel dizionario allora viene ritornata una lista vuota
    def get_table_data(self, filter):
        all_data = self.img_table.collect_table_state()
        if filter[0] == "0":
            return all_data.copy()

        filtered_data = []
        for data in all_data:
            if data.get(filter[0]) == filter[1]: filtered_data.append(data)
        
        return filtered_data.copy()
    
    def load_table(self, data):
        self.img_table.load_data(data)


    # questo importante, quando si verifica resize dell'interfaccia questo ricalcola tutte le dimensioni che i vari widget dentro devono assumere, avrebbe senso lasciare almeno uno expanding almeno non devo stare li a calcolare i pixel da usare
    def resizeEvent(self, event):
        super().resizeEvent(event)
        self.img_view.setMaximumWidth(self.width() // 3)
    


    
