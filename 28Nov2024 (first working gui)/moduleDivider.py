# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'moduleDivider.ui'
#
# Created by: PyQt5 UI code generator 5.9.2
#
# WARNING! All changes made in this file will be lost!

from PyQt5 import QtCore, QtGui, QtWidgets

class fmDivider(QtWidgets.QWidget):
    def __init__(self, parent = None):
        super(fmDivider,self).__init__(parent)
        
        self.setObjectName("fmDivider")
        super(fmDivider,self).resize(400, 20)
        self.lbHeading = QtWidgets.QLabel(self)
        self.lbHeading.setGeometry(QtCore.QRect(0, 0, 60, 20))
        self.lbHeading.setObjectName("lbHeading")
        self.line = QtWidgets.QFrame(self)
        self.line.setGeometry(QtCore.QRect(60, 0, 400, 20))
        self.line.setFrameShape(QtWidgets.QFrame.HLine)
        self.line.setFrameShadow(QtWidgets.QFrame.Sunken)
        self.line.setObjectName("line")

        self.retranslateUi(self)
        QtCore.QMetaObject.connectSlotsByName(self)

    def retranslateUi(self, fmDivider):
        _translate = QtCore.QCoreApplication.translate
        fmDivider.setWindowTitle(_translate("fmDivider", "Form"))
        self.lbHeading.setText(_translate("fmDivider", "TextLabel"))

    def setText(self, text):
        self.lbHeading.setText(text)

    def resize(self, width, height):
        if width < 60:
            return
        else:
            super(fmDivider,self).resize(width,height)
            rest = width - 60
            self.lbHeading.setGeometry(0,0,60,height)
            self.line.setGeometry(60,0,rest,height)