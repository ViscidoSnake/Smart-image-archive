# -*- coding: utf-8 -*-

################################################################################
## Form generated from reading UI file 'dir_path_selector.ui'
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
from PySide6.QtWidgets import (QApplication, QLineEdit, QPushButton, QSizePolicy,
    QVBoxLayout, QWidget)

class Ui_Dir_path_selector(object):
    def setupUi(self, Dir_path_selector):
        if not Dir_path_selector.objectName():
            Dir_path_selector.setObjectName(u"Dir_path_selector")
        Dir_path_selector.resize(388, 139)
        self.verticalLayout_2 = QVBoxLayout(Dir_path_selector)
        self.verticalLayout_2.setObjectName(u"verticalLayout_2")
        self.verticalLayout = QVBoxLayout()
        self.verticalLayout.setObjectName(u"verticalLayout")
        self.btn_dir_path_selector = QPushButton(Dir_path_selector)
        self.btn_dir_path_selector.setObjectName(u"btn_dir_path_selector")

        self.verticalLayout.addWidget(self.btn_dir_path_selector)

        self.le_dir_path_selected = QLineEdit(Dir_path_selector)
        self.le_dir_path_selected.setObjectName(u"le_dir_path_selected")

        self.verticalLayout.addWidget(self.le_dir_path_selected)

        self.btn_confirm = QPushButton(Dir_path_selector)
        self.btn_confirm.setObjectName(u"btn_confirm")

        self.verticalLayout.addWidget(self.btn_confirm)

        self.btn_abort = QPushButton(Dir_path_selector)
        self.btn_abort.setObjectName(u"btn_abort")

        self.verticalLayout.addWidget(self.btn_abort)


        self.verticalLayout_2.addLayout(self.verticalLayout)


        self.retranslateUi(Dir_path_selector)

        QMetaObject.connectSlotsByName(Dir_path_selector)
    # setupUi

    def retranslateUi(self, Dir_path_selector):
        Dir_path_selector.setWindowTitle(QCoreApplication.translate("Dir_path_selector", u"Form", None))
        self.btn_dir_path_selector.setText(QCoreApplication.translate("Dir_path_selector", u"Select directory", None))
        self.btn_confirm.setText(QCoreApplication.translate("Dir_path_selector", u"Confirm", None))
        self.btn_abort.setText(QCoreApplication.translate("Dir_path_selector", u"Abort", None))
    # retranslateUi

