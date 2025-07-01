# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'moduleSelect.ui'
#
# Created by: PyQt5 UI code generator 5.9.2
#
# WARNING! All changes made in this file will be lost!

from PyQt5 import QtCore, QtGui, QtWidgets

from constants import *

class formModuleRemove(QtWidgets.QDialog):
    
    def __init__(self, num_modules, parent = None):
        super(formModuleRemove,self).__init__(parent)
 
        self.num_modules = num_modules
       
        self.parent = parent
        self.ui = parent.ui 
        
        self.setObjectName("formModuleRemove")
        self.resize(320, 200)
        self.bbOkayCancel = QtWidgets.QDialogButtonBox(self)
        self.bbOkayCancel.setGeometry(QtCore.QRect(10, 100, 231, 32))
        self.bbOkayCancel.setOrientation(QtCore.Qt.Horizontal)
        self.bbOkayCancel.setStandardButtons(QtWidgets.QDialogButtonBox.Cancel|QtWidgets.QDialogButtonBox.Ok)
        self.bbOkayCancel.setCenterButtons(True)
        self.bbOkayCancel.setObjectName("bbOkayCancel")

        self.lbModuleNumber = QtWidgets.QLabel(self)
        self.lbModuleNumber.setGeometry(QtCore.QRect(10, 10, 100, 20))
        self.lbModuleNumber.setObjectName("lbModuleNumber")
        self.sbModuleNumber = QtWidgets.QSpinBox(self)
        self.sbModuleNumber.setGeometry(QtCore.QRect(105, 10, 50, 20))
        self.sbModuleNumber.setAlignment(QtCore.Qt.AlignRight|QtCore.Qt.AlignTrailing|QtCore.Qt.AlignVCenter)
        self.sbModuleNumber.setMinimum(0)
        self.sbModuleNumber.setMaximum(num_modules)
        self.sbModuleNumber.setSingleStep(1)
        self.sbModuleNumber.setValue(0)
        self.sbModuleNumber.setObjectName("sbModuleNumber")
        
        self.retranslateUi(self)
        self.bbOkayCancel.accepted.connect(self.deleteModule)
        self.bbOkayCancel.rejected.connect(self.close)
        QtCore.QMetaObject.connectSlotsByName(self)

    def retranslateUi(self, formModuleRemove):
        _translate = QtCore.QCoreApplication.translate
        formModuleRemove.setWindowTitle(_translate("formModuleRemove", "Dialog"))
        self.lbModuleNumber.setText(_translate("formModuleRemove", "Module Number:"))

    def deleteModule(self):
        self.ui.deleteModule(self.sbModuleNumber.value())
        self.close()