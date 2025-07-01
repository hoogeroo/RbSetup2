# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'digitalDialog.ui'
#
# Created by: PyQt5 UI code generator 5.9.2
#
# WARNING! All changes made in this file will be lost!

from PyQt5 import QtCore, QtGui, QtWidgets

from dataTypes import *

from DAQ import DAQ, daq

class digitalDialog(QtWidgets.QDialog):
    def __init__(self, channelNumber, startTime, duration, maybeEvent, parent = None):
        super(digitalDialog,self).__init__(parent)
        
        self.channelNumber = channelNumber
        self.startTime = startTime
        self.maybeEvent = maybeEvent
        
        self.parent = parent

        default = daq.lines[channelNumber].default
        
        self.label = daq.lines[channelNumber].label

        self.setObjectName("digitalDialog")
        self.resize(320, 140)
        self.lbChannel = QtWidgets.QLabel(self)
        self.lbChannel.setGeometry(QtCore.QRect(10,10,100,20))
        self.lbChannel.setObjectName("lbChannel")
        self.lbStartTime = QtWidgets.QLabel(self)
        self.lbStartTime.setGeometry(QtCore.QRect(10, 40, 100, 20))
        self.lbStartTime.setObjectName("lbStartTime")
        self.sbStartTime = QtWidgets.QSpinBox(self)
        self.sbStartTime.setGeometry(QtCore.QRect(110, 40, 90, 20))
        self.sbStartTime.setAlignment(QtCore.Qt.AlignRight|QtCore.Qt.AlignTrailing|QtCore.Qt.AlignVCenter)
        self.sbStartTime.setMinimum(0)
        self.sbStartTime.setMaximum(100000)
        self.sbStartTime.setSingleStep(100)
        self.sbStartTime.setValue(startTime)
        self.sbStartTime.setEnabled(False)
        self.sbStartTime.setObjectName("sbStartTime")
        self.lbDuration = QtWidgets.QLabel(self)
        self.lbDuration.setGeometry(QtCore.QRect(10, 70, 100, 20))
        self.lbDuration.setObjectName("lbDuration")
        self.sbDuration = QtWidgets.QSpinBox(self)
        self.sbDuration.setGeometry(QtCore.QRect(110, 70, 90, 20))
        self.sbDuration.setAlignment(QtCore.Qt.AlignRight|QtCore.Qt.AlignTrailing|QtCore.Qt.AlignVCenter)
        self.sbDuration.setMinimum(0)
        self.sbDuration.setMaximum(100000)
        self.sbDuration.setSingleStep(100)
        self.sbDuration.setValue(duration)
        self.sbDuration.setObjectName("sbDuration")
        self.gbDigitalValue = QtWidgets.QGroupBox(self)
        self.gbDigitalValue.setGeometry(QtCore.QRect(210, 40, 90, 40))
        self.gbDigitalValue.setObjectName("gbDigitalValue")
        self.rbDigitalZero = QtWidgets.QRadioButton(self.gbDigitalValue)
        self.rbDigitalZero.setGeometry(QtCore.QRect(10, 20, 30, 20))
        self.rbDigitalZero.setChecked(not default)
        self.rbDigitalZero.setObjectName("rbDigitalZero")
        self.rbDigitalOne = QtWidgets.QRadioButton(self.gbDigitalValue)
        self.rbDigitalOne.setGeometry(QtCore.QRect(40, 20, 30, 20))
        self.rbDigitalOne.setChecked(default)
        self.rbDigitalOne.setObjectName("rbDigitalOne")
        self.bbOkCancel = QtWidgets.QDialogButtonBox(self)
        self.bbOkCancel.setGeometry(QtCore.QRect(40, 110, 166, 24))
        self.bbOkCancel.setStandardButtons(QtWidgets.QDialogButtonBox.Cancel|QtWidgets.QDialogButtonBox.Ok)
        self.bbOkCancel.setObjectName("bbOkCancel")

        self.retranslateUi(self)
        self.bbOkCancel.accepted.connect(self.update)
        self.bbOkCancel.rejected.connect(self.close)
        QtCore.QMetaObject.connectSlotsByName(self)
        
        self.populate()

    def retranslateUi(self, digitalDialog):
        _translate = QtCore.QCoreApplication.translate
        digitalDialog.setWindowTitle(_translate("digitalDialog", "Form"))
        self.lbChannel.setText(_translate("digitalDialog",self.label))
        self.lbStartTime.setText(_translate("digitalDialog", "Start Time (us):"))
        self.lbDuration.setText(_translate("digitalDialog", "Duration (us):"))
        self.gbDigitalValue.setTitle(_translate("digitalDialog", "Digital Value"))
        self.rbDigitalZero.setText(_translate("digitalDialog", "0"))
        self.rbDigitalOne.setText(_translate("digitalDialog", "1"))

    def update(self):
        startTime = self.startTime
        duration = self.sbDuration.value()
        if startTime + duration > self.parent.parent.Module.sbStartTime.value() + self.parent.parent.Module.sbDuration.value():
            duration =  self.parent.parent.Module.sbStartTime.value() + self.parent.parent.Module.sbDuration.value() - startTime       
            self.sbDuration.setValue(duration)
        value = self.rbDigitalOne.isChecked()
        event = Digital(startTime,duration,value)
        self.parent.setEvent(event)
        self.close()
        
        self.parent.parent.redoLayout()
        
    def populate(self):
        if self.maybeEvent.is_just():
            event = self.maybeEvent.value()
            self.sbStartTime.setValue(event.startTime)
            self.sbDuration.setValue(event.Duration)
            self.rbDigitalOne.setChecked(event.DigitalValue)
        else:
            pass 