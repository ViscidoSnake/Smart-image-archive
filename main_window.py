from PySide6.QtWidgets import QMainWindow, QPushButton, QLabel, QWidget, QStackedWidget, QVBoxLayout, QStatusBar
from PySide6.QtCore import Slot, Signal


# from ui_model_compiled.form import Form
# from ui_model_compiled.action_bar import Action_bar 
# from ui_model_compiled.person_registration_form import Person_registration_form 


from .app_resources.procedures.analyze_photos import Analyze_photos_procedure




class MainWindow(QMainWindow):
    def __init__ (self, app):
        super().__init__()
        #passaggio delicato, non molto chiaro
        self.app = app

        self.setWindowTitle("Bozza1")


        # ---------------------setting del menu bar---------------------
        # è un bonus, permette la personalizzazione di tutta l'applicazione ma soprattutto contiene una voce che specifica a quale directory deve puntare l'applicazione per lavorare con le immagini registrate nel database e anche il file database associato, potrebbe avere senso mettere fisso file db dentro la directory dove sono presenti le immagini registrate tuttavia per certe operazioni che effetuano ricerche di dati sul db questo aspetto non è necessario.  
        # metto menubar attraverso mainWindow
        menuBar = self.menuBar()
        menuFile = menuBar.addMenu("&Select data scope")
        # qAction molto interessanti, si possono usare per veicolare più azioni verso un unico slot
        actionQuit = menuFile.addAction("Quit app")
        # lego il signal dell'azione a una funzione che esegue la chiusura dell'applicazione
        actionQuit.triggered.connect(self.quit_app)

        #interessante anche la toolbar anche se mi sembra un po molto professionale come roba
        # ...




        # ---------------------setting della schermata centrale---------------------
        # un menu con pulsanti, l'evento di pressione deve molto probabilmente cambiare la schermata centrale con una coerente alla scelta selezionata, prevedere un pulsante nella nuova schermata che consente di ritornare a quella principale ovvero dove è presente il menu

        # pattern super basilare, 2 widget, uno mostra il menu e l'altro viene disegnato in funzione della voce scelta nel menu, nella seconda va messo un pulsante che fa ritornare al menu però distruggendo tutto quello contenuto nel widget stesso

        self.menu_widget = QWidget(self)
        self.menu_layout  = QVBoxLayout(self.menu_widget)
        self.action_widget  = QWidget(self)
        self.action_layout  = QVBoxLayout(self.action_widget)
        
        self.organizer_widget = QStackedWidget(self)
        self.organizer_widget.addWidget(self.menu_widget)
        self.organizer_widget.addWidget(self.action_widget)

        #---Aggiunta di un soggetto al database
        btn_add_person_in_db = QPushButton()
        btn_add_person_in_db.setText("button 1")
        btn_add_person_in_db.clicked.connect(self.start_person_processing)
        self.menu_layout.addWidget(btn_add_person_in_db)

        #---Apri una cartella e analizza (detection+recognitio) le foto all'interno---
        btn_analize_photos = QPushButton()
        btn_analize_photos.setText("button analize photos")
        btn_analize_photos.clicked.connect(self.start_analize_photos)
        self.menu_layout.addWidget(btn_analize_photos)



        # bt2 = QPushButton()
        # bt2.setText("button 2")
        # bt2.clicked.connect(self.button2_clicked)
        # self.menu_layout.addWidget(bt2)

        # bt3 = QPushButton()
        # bt3.setText("button 3")
        # self.menu_layout.addWidget(bt3) 

        # bt4 = QPushButton()
        # bt4.setText("button 4")
        # self.menu_layout.addWidget(bt4)





        # # Widget contenitore
        # central_widget = QWidget(self)
        # # Layout sul widget contenitore
        # layout = QVBoxLayout(central_widget)


        # prova = Form()
        # layout.addWidget(prova)



        # self.setCentralWidget(central_widget)

        self.setCentralWidget(self.organizer_widget)









        # ---------------------setting della status bar---------------------
        # rappresenta un elemento molto importante nell'interfaccia in quanto da notifiche di vario genere sullo stato delle operazioni svolte nella schermata centrale, potrebbe essere usata anche per dare notifiche più generiche però in tal caso conviene scrivere una stringa che faccia capire da quale oggetto proviene la notifica
        self.setStatusBar(QStatusBar(self))





    # SLOT
        

    # occhio che la funzione è lo slot di un seganale e quindi tale slot va definito con parametri che sono in egual numero a quelli restituiti dal signal, indipendentemente se verranno usati o meno all'interno
    @Slot()
    def start_person_processing(self):

        # k = 23

        # a = Person_registration_procedure(k)
        # self.action_layout.addWidget(a)

        # a.abort_procedure.connect(lambda: self.stop_person_processing(a))

        # self.organizer_widget.setCurrentWidget(self.action_widget)
        print("ciao")

    @Slot()
    def start_analize_photos(self):
        a = Analyze_photos_procedure()
        self.action_layout.addWidget(a)

        a.abort_procedure.connect(lambda: self.stop_person_processing(a))

        self.organizer_widget.setCurrentWidget(self.action_widget)


    @Slot()
    def stop_person_processing(self,obj):

        self.action_layout.removeWidget(obj)
        self.action_layout.update()
        obj.deleteLater()

        self.organizer_widget.setCurrentWidget(self.menu_widget)

    










    def quit_app(self):
        self.app.quit()



# per convertire in codice .py interfaccia disegnata
# pyside6-uic .\app_v1\app_resources\qt_design_ui_element\dir_path_selector.ui > .\app_v1\app_resources\compiled_ui_element\ui_dir_path_selector.py