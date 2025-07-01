# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'module.ui'
#
# Created by: PyQt5 UI code generator 5.9.2
#
# WARNING! All changes made in this file will be lost!

from PyQt5 import QtCore, QtGui, QtWidgets

class Ui_moduleForm(object):
    def setupUi(self, moduleForm):
        moduleForm.setObjectName("moduleForm")
        moduleForm.resize(400, 309)
        self.fModule = QtWidgets.QFrame(moduleForm)
        self.fModule.setGeometry(QtCore.QRect(10, 40, 381, 251))
        self.fModule.setFrameShape(QtWidgets.QFrame.StyledPanel)
        self.fModule.setFrameShadow(QtWidgets.QFrame.Raised)
        self.fModule.setObjectName("fModule")
        self.line = QtWidgets.QFrame(self.fModule)
        self.line.setGeometry(QtCore.QRect(7, 80, 371, 16))
        self.line.setFrameShape(QtWidgets.QFrame.HLine)
        self.line.setFrameShadow(QtWidgets.QFrame.Sunken)
        self.line.setObjectName("line")
        self.line_2 = QtWidgets.QFrame(self.fModule)
        self.line_2.setGeometry(QtCore.QRect(7, 170, 371, 16))
        self.line_2.setFrameShape(QtWidgets.QFrame.HLine)
        self.line_2.setFrameShadow(QtWidgets.QFrame.Sunken)
        self.line_2.setObjectName("line_2")
        self.frame = QtWidgets.QFrame(self.fModule)
        self.frame.setGeometry(QtCore.QRect(0, 0, 371, 80))
        self.frame.setFrameShape(QtWidgets.QFrame.StyledPanel)
        self.frame.setFrameShadow(QtWidgets.QFrame.Raised)
        self.frame.setObjectName("frame")
        self.frame_2 = QtWidgets.QFrame(self.fModule)
        self.frame_2.setGeometry(QtCore.QRect(0, 90, 371, 80))
        self.frame_2.setFrameShape(QtWidgets.QFrame.StyledPanel)
        self.frame_2.setFrameShadow(QtWidgets.QFrame.Raised)
        self.frame_2.setObjectName("frame_2")
        self.frame_3 = QtWidgets.QFrame(self.fModule)
        self.frame_3.setGeometry(QtCore.QRect(0, 180, 371, 71))
        self.frame_3.setFrameShape(QtWidgets.QFrame.StyledPanel)
        self.frame_3.setFrameShadow(QtWidgets.QFrame.Raised)
        self.frame_3.setObjectName("frame_3")
        self.lbStartTime = QtWidgets.QLabel(moduleForm)
        self.lbStartTime.setGeometry(QtCore.QRect(10, 10, 71, 16))
        self.lbStartTime.setObjectName("lbStartTime")
        self.leStartTime = QtWidgets.QLineEdit(moduleForm)
        self.leStartTime.setGeometry(QtCore.QRect(80, 10, 61, 23))
        self.leStartTime.setAlignment(QtCore.Qt.AlignRight|QtCore.Qt.AlignTrailing|QtCore.Qt.AlignVCenter)
        self.leStartTime.setObjectName("leStartTime")
        self.lbDuration = QtWidgets.QLabel(moduleForm)
        self.lbDuration.setGeometry(QtCore.QRect(150, 10, 59, 15))
        self.lbDuration.setObjectName("lbDuration")
        self.leDuration = QtWidgets.QLineEdit(moduleForm)
        self.leDuration.setGeometry(QtCore.QRect(220, 10, 51, 23))
        self.leDuration.setAlignment(QtCore.Qt.AlignRight|QtCore.Qt.AlignTrailing|QtCore.Qt.AlignVCenter)
        self.leDuration.setObjectName("leDuration")

        self.retranslateUi(moduleForm)
        self.leStartTime.textChanged['QString'].connect(moduleForm.update)
        self.leDuration.textChanged['QString'].connect(moduleForm.update)
        QtCore.QMetaObject.connectSlotsByName(moduleForm)

    def retranslateUi(self, moduleForm):
        _translate = QtCore.QCoreApplication.translate
        moduleForm.setWindowTitle(_translate("moduleForm", "Form"))
        self.lbStartTime.setText(_translate("moduleForm", "Start Time:"))
        self.leStartTime.setText(_translate("moduleForm", "0"))
        self.lbDuration.setText(_translate("moduleForm", "Duration:"))
        self.leDuration.setText(_translate("moduleForm", "1"))

