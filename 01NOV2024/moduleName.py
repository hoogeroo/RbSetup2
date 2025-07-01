# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'moduleName.ui'
#
# Created by: PyQt5 UI code generator 5.9.2
#
# WARNING! All changes made in this file will be lost!

from PyQt5 import QtCore, QtGui, QtWidgets

class Ui_Form(object):
    def setupUi(self, Form):
        Form.setObjectName("Form")
        Form.resize(400, 300)
        self.lbName = QtWidgets.QLabel(Form)
        self.lbName.setGeometry(QtCore.QRect(20, 20, 91, 16))
        self.lbName.setObjectName("lbName")
        self.leName = QtWidgets.QLineEdit(Form)
        self.leName.setGeometry(QtCore.QRect(120, 20, 113, 23))
        self.leName.setObjectName("leName")

        self.retranslateUi(Form)
        QtCore.QMetaObject.connectSlotsByName(Form)

    def retranslateUi(self, Form):
        _translate = QtCore.QCoreApplication.translate
        Form.setWindowTitle(_translate("Form", "Form"))
        self.lbName.setText(_translate("Form", "Module Name:"))

