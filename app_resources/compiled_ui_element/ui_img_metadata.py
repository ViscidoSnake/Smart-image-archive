# -*- coding: utf-8 -*-

################################################################################
## Form generated from reading UI file 'img_metadata.ui'
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
from PySide6.QtWidgets import (QApplication, QDateEdit, QFormLayout, QHBoxLayout,
    QLabel, QLineEdit, QSizePolicy, QWidget)

class Ui_Img_metadata(object):
    def setupUi(self, Img_metadata):
        if not Img_metadata.objectName():
            Img_metadata.setObjectName(u"Img_metadata")
        Img_metadata.resize(655, 147)
        self.horizontalLayout_2 = QHBoxLayout(Img_metadata)
        self.horizontalLayout_2.setObjectName(u"horizontalLayout_2")
        self.horizontalLayout = QHBoxLayout()
        self.horizontalLayout.setObjectName(u"horizontalLayout")
        self.formLayout = QFormLayout()
        self.formLayout.setObjectName(u"formLayout")
        self.label = QLabel(Img_metadata)
        self.label.setObjectName(u"label")

        self.formLayout.setWidget(0, QFormLayout.ItemRole.LabelRole, self.label)

        self.lineEdit_file_name = QLineEdit(Img_metadata)
        self.lineEdit_file_name.setObjectName(u"lineEdit_file_name")
        self.lineEdit_file_name.setEnabled(False)

        self.formLayout.setWidget(0, QFormLayout.ItemRole.FieldRole, self.lineEdit_file_name)

        self.label_2 = QLabel(Img_metadata)
        self.label_2.setObjectName(u"label_2")

        self.formLayout.setWidget(1, QFormLayout.ItemRole.LabelRole, self.label_2)

        self.label_3 = QLabel(Img_metadata)
        self.label_3.setObjectName(u"label_3")

        self.formLayout.setWidget(2, QFormLayout.ItemRole.LabelRole, self.label_3)

        self.lineEdit_size = QLineEdit(Img_metadata)
        self.lineEdit_size.setObjectName(u"lineEdit_size")
        self.lineEdit_size.setEnabled(False)

        self.formLayout.setWidget(2, QFormLayout.ItemRole.FieldRole, self.lineEdit_size)

        self.label_7 = QLabel(Img_metadata)
        self.label_7.setObjectName(u"label_7")

        self.formLayout.setWidget(3, QFormLayout.ItemRole.LabelRole, self.label_7)

        self.lineEdit_faces_n = QLineEdit(Img_metadata)
        self.lineEdit_faces_n.setObjectName(u"lineEdit_faces_n")
        self.lineEdit_faces_n.setEnabled(False)

        self.formLayout.setWidget(3, QFormLayout.ItemRole.FieldRole, self.lineEdit_faces_n)

        self.dateEdit_datetime = QDateEdit(Img_metadata)
        self.dateEdit_datetime.setObjectName(u"dateEdit_datetime")
        self.dateEdit_datetime.setEnabled(False)
        self.dateEdit_datetime.setDateTime(QDateTime(QDate(1800, 1, 1), QTime(0, 0, 0)))
        self.dateEdit_datetime.setMinimumDate(QDate(1800, 1, 1))
        self.dateEdit_datetime.setDate(QDate(1800, 1, 1))

        self.formLayout.setWidget(1, QFormLayout.ItemRole.FieldRole, self.dateEdit_datetime)


        self.horizontalLayout.addLayout(self.formLayout)

        self.formLayout_2 = QFormLayout()
        self.formLayout_2.setObjectName(u"formLayout_2")
        self.label_4 = QLabel(Img_metadata)
        self.label_4.setObjectName(u"label_4")

        self.formLayout_2.setWidget(0, QFormLayout.ItemRole.LabelRole, self.label_4)

        self.label_5 = QLabel(Img_metadata)
        self.label_5.setObjectName(u"label_5")

        self.formLayout_2.setWidget(1, QFormLayout.ItemRole.LabelRole, self.label_5)

        self.label_6 = QLabel(Img_metadata)
        self.label_6.setObjectName(u"label_6")

        self.formLayout_2.setWidget(2, QFormLayout.ItemRole.LabelRole, self.label_6)

        self.label_8 = QLabel(Img_metadata)
        self.label_8.setObjectName(u"label_8")

        self.formLayout_2.setWidget(3, QFormLayout.ItemRole.LabelRole, self.label_8)

        self.lineEdit_new_file_name = QLineEdit(Img_metadata)
        self.lineEdit_new_file_name.setObjectName(u"lineEdit_new_file_name")
        self.lineEdit_new_file_name.setEnabled(False)

        self.formLayout_2.setWidget(0, QFormLayout.ItemRole.FieldRole, self.lineEdit_new_file_name)

        self.lineEdit_nickname = QLineEdit(Img_metadata)
        self.lineEdit_nickname.setObjectName(u"lineEdit_nickname")
        self.lineEdit_nickname.setEnabled(False)

        self.formLayout_2.setWidget(1, QFormLayout.ItemRole.FieldRole, self.lineEdit_nickname)

        self.dateEdit_ins_datetime = QDateEdit(Img_metadata)
        self.dateEdit_ins_datetime.setObjectName(u"dateEdit_ins_datetime")
        self.dateEdit_ins_datetime.setEnabled(False)
        self.dateEdit_ins_datetime.setDateTime(QDateTime(QDate(1800, 1, 1), QTime(0, 0, 0)))
        self.dateEdit_ins_datetime.setMinimumDate(QDate(1800, 1, 1))
        self.dateEdit_ins_datetime.setDate(QDate(1800, 1, 1))

        self.formLayout_2.setWidget(2, QFormLayout.ItemRole.FieldRole, self.dateEdit_ins_datetime)

        self.lineEdit_idF = QLineEdit(Img_metadata)
        self.lineEdit_idF.setObjectName(u"lineEdit_idF")
        self.lineEdit_idF.setEnabled(False)

        self.formLayout_2.setWidget(3, QFormLayout.ItemRole.FieldRole, self.lineEdit_idF)


        self.horizontalLayout.addLayout(self.formLayout_2)


        self.horizontalLayout_2.addLayout(self.horizontalLayout)


        self.retranslateUi(Img_metadata)

        QMetaObject.connectSlotsByName(Img_metadata)
    # setupUi

    def retranslateUi(self, Img_metadata):
        Img_metadata.setWindowTitle(QCoreApplication.translate("Img_metadata", u"Form", None))
        self.label.setText(QCoreApplication.translate("Img_metadata", u"Original file name", None))
        self.label_2.setText(QCoreApplication.translate("Img_metadata", u"Datetime", None))
        self.label_3.setText(QCoreApplication.translate("Img_metadata", u"Size", None))
        self.label_7.setText(QCoreApplication.translate("Img_metadata", u"Faces number", None))
        self.dateEdit_datetime.setDisplayFormat(QCoreApplication.translate("Img_metadata", u"yyyy-MM-dd", None))
        self.label_4.setText(QCoreApplication.translate("Img_metadata", u"New file name", None))
        self.label_5.setText(QCoreApplication.translate("Img_metadata", u"File nickname", None))
        self.label_6.setText(QCoreApplication.translate("Img_metadata", u"Insertion Datetime", None))
        self.label_8.setText(QCoreApplication.translate("Img_metadata", u"idF", None))
        self.dateEdit_ins_datetime.setDisplayFormat(QCoreApplication.translate("Img_metadata", u"yyyy-MM-dd", None))
    # retranslateUi

