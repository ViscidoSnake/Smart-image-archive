# -*- coding: utf-8 -*-

################################################################################
## Form generated from reading UI file 'engine_data_form.ui'
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
from PySide6.QtWidgets import (QApplication, QDoubleSpinBox, QFormLayout, QLabel,
    QPushButton, QSizePolicy, QSpinBox, QVBoxLayout,
    QWidget)

class Ui_Engine_data_form(object):
    def setupUi(self, Engine_data_form):
        if not Engine_data_form.objectName():
            Engine_data_form.setObjectName(u"Engine_data_form")
        Engine_data_form.resize(486, 183)
        self.verticalLayout_2 = QVBoxLayout(Engine_data_form)
        self.verticalLayout_2.setObjectName(u"verticalLayout_2")
        self.verticalLayout = QVBoxLayout()
        self.verticalLayout.setObjectName(u"verticalLayout")
        self.label_engine_data_form = QLabel(Engine_data_form)
        self.label_engine_data_form.setObjectName(u"label_engine_data_form")
        sizePolicy = QSizePolicy(QSizePolicy.Policy.Preferred, QSizePolicy.Policy.Minimum)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.label_engine_data_form.sizePolicy().hasHeightForWidth())
        self.label_engine_data_form.setSizePolicy(sizePolicy)
        font = QFont()
        font.setPointSize(20)
        self.label_engine_data_form.setFont(font)

        self.verticalLayout.addWidget(self.label_engine_data_form)

        self.formLayout = QFormLayout()
        self.formLayout.setObjectName(u"formLayout")
        self.label_2 = QLabel(Engine_data_form)
        self.label_2.setObjectName(u"label_2")

        self.formLayout.setWidget(0, QFormLayout.ItemRole.LabelRole, self.label_2)

        self.label_23 = QLabel(Engine_data_form)
        self.label_23.setObjectName(u"label_23")

        self.formLayout.setWidget(1, QFormLayout.ItemRole.LabelRole, self.label_23)

        self.spinBox_det_size = QSpinBox(Engine_data_form)
        self.spinBox_det_size.setObjectName(u"spinBox_det_size")
        self.spinBox_det_size.setEnabled(True)
        self.spinBox_det_size.setReadOnly(False)
        self.spinBox_det_size.setMaximum(3000)
        self.spinBox_det_size.setSingleStep(32)
        self.spinBox_det_size.setValue(64)

        self.formLayout.setWidget(1, QFormLayout.ItemRole.FieldRole, self.spinBox_det_size)

        self.doubleSpinBox_det_threshold = QDoubleSpinBox(Engine_data_form)
        self.doubleSpinBox_det_threshold.setObjectName(u"doubleSpinBox_det_threshold")
        self.doubleSpinBox_det_threshold.setMaximum(1.000000000000000)
        self.doubleSpinBox_det_threshold.setSingleStep(0.100000000000000)
        self.doubleSpinBox_det_threshold.setValue(0.500000000000000)

        self.formLayout.setWidget(0, QFormLayout.ItemRole.FieldRole, self.doubleSpinBox_det_threshold)


        self.verticalLayout.addLayout(self.formLayout)

        self.pushButton_applied_params = QPushButton(Engine_data_form)
        self.pushButton_applied_params.setObjectName(u"pushButton_applied_params")

        self.verticalLayout.addWidget(self.pushButton_applied_params)


        self.verticalLayout_2.addLayout(self.verticalLayout)


        self.retranslateUi(Engine_data_form)

        QMetaObject.connectSlotsByName(Engine_data_form)
    # setupUi

    def retranslateUi(self, Engine_data_form):
        Engine_data_form.setWindowTitle(QCoreApplication.translate("Engine_data_form", u"Form", None))
        self.label_engine_data_form.setText(QCoreApplication.translate("Engine_data_form", u"Step 2.0", None))
        self.label_2.setText(QCoreApplication.translate("Engine_data_form", u"Detection threshold", None))
        self.label_23.setText(QCoreApplication.translate("Engine_data_form", u"Applied resizing", None))
        self.pushButton_applied_params.setText(QCoreApplication.translate("Engine_data_form", u"Applied params", None))
    # retranslateUi

