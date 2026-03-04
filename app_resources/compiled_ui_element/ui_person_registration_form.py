# -*- coding: utf-8 -*-

################################################################################
## Form generated from reading UI file 'person_registration_form.ui'
##
## Created by: Qt User Interface Compiler version 6.10.1
##
## WARNING! All changes made in this file will be lost when recompiling UI file!
################################################################################

from PySide6.QtCore import (QCoreApplication, QDate, QDateTime, QLocale,
    QMetaObject, QObject, QPoint, QRect,
    QSize, QTime, QUrl, Qt)
from PySide6.QtGui import (QBrush, QColor, QConicalGradient, QCursor,
    QFont, QFontDatabase, QGradient, QIcon,
    QImage, QKeySequence, QLinearGradient, QPainter,
    QPalette, QPixmap, QRadialGradient, QTransform)
from PySide6.QtWidgets import (QApplication, QDateEdit, QHBoxLayout, QLabel,
    QLineEdit, QPushButton, QSizePolicy, QVBoxLayout,
    QWidget)

class Ui_Person_registration_form(object):
    def setupUi(self, Person_registration_form):
        if not Person_registration_form.objectName():
            Person_registration_form.setObjectName(u"Person_registration_form")
        Person_registration_form.resize(434, 202)
        self.verticalLayout_2 = QVBoxLayout(Person_registration_form)
        self.verticalLayout_2.setObjectName(u"verticalLayout_2")
        self.verticalLayout = QVBoxLayout()
        self.verticalLayout.setObjectName(u"verticalLayout")
        self.label_data_entry = QLabel(Person_registration_form)
        self.label_data_entry.setObjectName(u"label_data_entry")
        sizePolicy = QSizePolicy(QSizePolicy.Policy.Preferred, QSizePolicy.Policy.Fixed)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.label_data_entry.sizePolicy().hasHeightForWidth())
        self.label_data_entry.setSizePolicy(sizePolicy)
        font = QFont()
        font.setPointSize(14)
        self.label_data_entry.setFont(font)

        self.verticalLayout.addWidget(self.label_data_entry)

        self.horizontalLayout = QHBoxLayout()
        self.horizontalLayout.setObjectName(u"horizontalLayout")
        self.label_sample_path = QLabel(Person_registration_form)
        self.label_sample_path.setObjectName(u"label_sample_path")

        self.horizontalLayout.addWidget(self.label_sample_path)

        self.lineEdit_sample_path = QLineEdit(Person_registration_form)
        self.lineEdit_sample_path.setObjectName(u"lineEdit_sample_path")

        self.horizontalLayout.addWidget(self.lineEdit_sample_path)


        self.verticalLayout.addLayout(self.horizontalLayout)

        self.horizontalLayout_2 = QHBoxLayout()
        self.horizontalLayout_2.setObjectName(u"horizontalLayout_2")
        self.label_name = QLabel(Person_registration_form)
        self.label_name.setObjectName(u"label_name")

        self.horizontalLayout_2.addWidget(self.label_name)

        self.lineEdit_name = QLineEdit(Person_registration_form)
        self.lineEdit_name.setObjectName(u"lineEdit_name")

        self.horizontalLayout_2.addWidget(self.lineEdit_name)

        self.label_birth = QLabel(Person_registration_form)
        self.label_birth.setObjectName(u"label_birth")

        self.horizontalLayout_2.addWidget(self.label_birth)

        self.dateEdit_birth = QDateEdit(Person_registration_form)
        self.dateEdit_birth.setObjectName(u"dateEdit_birth")

        self.horizontalLayout_2.addWidget(self.dateEdit_birth)


        self.verticalLayout.addLayout(self.horizontalLayout_2)

        self.pushButton_send_data = QPushButton(Person_registration_form)
        self.pushButton_send_data.setObjectName(u"pushButton_send_data")

        self.verticalLayout.addWidget(self.pushButton_send_data)

        self.pushButton_abort = QPushButton(Person_registration_form)
        self.pushButton_abort.setObjectName(u"pushButton_abort")

        self.verticalLayout.addWidget(self.pushButton_abort)


        self.verticalLayout_2.addLayout(self.verticalLayout)


        self.retranslateUi(Person_registration_form)

        QMetaObject.connectSlotsByName(Person_registration_form)
    # setupUi

    def retranslateUi(self, Person_registration_form):
        Person_registration_form.setWindowTitle(QCoreApplication.translate("Person_registration_form", u"Form", None))
        self.label_data_entry.setText(QCoreApplication.translate("Person_registration_form", u"New person registration form", None))
        self.label_sample_path.setText(QCoreApplication.translate("Person_registration_form", u"Sample face path", None))
        self.label_name.setText(QCoreApplication.translate("Person_registration_form", u"Name and Surname", None))
        self.lineEdit_name.setPlaceholderText("")
        self.label_birth.setText(QCoreApplication.translate("Person_registration_form", u"birthday", None))
        self.pushButton_send_data.setText(QCoreApplication.translate("Person_registration_form", u"Send", None))
        self.pushButton_abort.setText(QCoreApplication.translate("Person_registration_form", u"Abort operation", None))
    # retranslateUi

