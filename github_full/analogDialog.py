# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'analogDialog.ui'
#
# Created by: PyQt5 UI code generator 5.9.2
#
# WARNING! All changes made in this file will be lost!

from PyQt5 import QtCore, QtGui, QtWidgets

from DAQ import DAQ, daq

from dataTypes import *
from constants import *

class analogDialog(QtWidgets.QDialog):
    def __init__(self, channelNumber, startTime, duration, maybeEvent, parent = None):
        super(analogDialog,self).__init__(parent)
        
        self.channelNumber = channelNumber
        self.startTime = startTime
        self.maybeEvent = maybeEvent
        
        self.parent = parent
        
        min_val = daq.lines[channelNumber].min_val
        max_val = daq.lines[channelNumber].max_val
        increment = daq.lines[channelNumber].increment
        default = daq.lines[channelNumber].default
        
        self.label = daq.lines[channelNumber].label
        
        self.setObjectName("analogDialog")
        self.resize(420, 205)
        self.lbChannel = QtWidgets.QLabel(self)
        self.lbChannel.setGeometry(QtCore.QRect(10,10,100,20))
        self.lbChannel.setObjectName("lbChannel")
        self.lbStartTime = QtWidgets.QLabel(self)
        self.lbStartTime.setGeometry(QtCore.QRect(10, 40, 100, 20))
        self.lbStartTime.setObjectName("lbStartTime")
        self.sbStartTime = QtWidgets.QSpinBox(self)
        self.sbStartTime.setGeometry(QtCore.QRect(110, 40, 90, 20))
        self.sbStartTime.setAlignment(QtCore.Qt.AlignRight|QtCore.Qt.AlignTrailing|QtCore.Qt.AlignVCenter)
        self.sbStartTime.setObjectName("sbStartTime")
        self.sbStartTime.setMinimum(0)
        self.sbStartTime.setMaximum(maximumStartTime)
        self.sbStartTime.setSingleStep(timeIncrement)
        self.sbStartTime.setValue(startTime)
        self.sbStartTime.setEnabled(False)
        self.lbDuration = QtWidgets.QLabel(self)
        self.lbDuration.setGeometry(QtCore.QRect(210, 40, 90, 20))
        self.lbDuration.setObjectName("lbDuration")
        self.sbDuration = QtWidgets.QSpinBox(self)
        self.sbDuration.setGeometry(QtCore.QRect(310, 40, 90, 20))
        self.sbDuration.setAlignment(QtCore.Qt.AlignRight|QtCore.Qt.AlignTrailing|QtCore.Qt.AlignVCenter)
        self.sbDuration.setMinimum(0)
        self.sbDuration.setMaximum(maximumDuration)
        self.sbDuration.setSingleStep(timeIncrement)
        self.sbDuration.setValue(duration)
        self.sbDuration.setObjectName("sbDuration")
        self.lbInitialValue = QtWidgets.QLabel(self)
        self.lbInitialValue.setGeometry(QtCore.QRect(10, 70, 81, 20))
        self.lbInitialValue.setObjectName("lbInitialValue")
        self.sbInitialValue = QtWidgets.QSpinBox(self)
        self.sbInitialValue.setGeometry(QtCore.QRect(100, 70, 51, 20))
        self.sbInitialValue.setAlignment(QtCore.Qt.AlignRight|QtCore.Qt.AlignTrailing|QtCore.Qt.AlignVCenter)
        self.sbInitialValue.setMinimum(min_val)
        self.sbInitialValue.setMaximum(max_val)
        self.sbInitialValue.setSingleStep(increment)
        self.sbInitialValue.setValue(default)
        self.sbInitialValue.setObjectName("sbInitialValue")
        self.lbFinalValue = QtWidgets.QLabel(self)
        self.lbFinalValue.setEnabled(False)
        self.lbFinalValue.setGeometry(QtCore.QRect(170, 70, 81, 20))
        self.lbFinalValue.setObjectName("lbFinalValue")
        self.sbFinalValue = QtWidgets.QSpinBox(self)
        self.sbFinalValue.setEnabled(False)
        self.sbFinalValue.setGeometry(QtCore.QRect(260, 70, 61, 20))
        self.sbFinalValue.setAlignment(QtCore.Qt.AlignRight|QtCore.Qt.AlignTrailing|QtCore.Qt.AlignVCenter)
        self.sbFinalValue.setMinimum(min_val)
        self.sbFinalValue.setMaximum(max_val)
        self.sbFinalValue.setSingleStep(increment)
        self.sbFinalValue.setValue(default)
        self.sbFinalValue.setObjectName("sbFinalValue")
        self.cbRampType = QtWidgets.QComboBox(self)
        self.cbRampType.setGeometry(QtCore.QRect(10, 100, 141, 20))
        self.cbRampType.setObjectName("cbRampType")
        self.cbRampType.addItem("")
        self.cbRampType.addItem("")
        self.cbRampType.addItem("")
        self.cbRampType.addItem("")
        self.cbRampType.addItem("")
        self.lbRise = QtWidgets.QLabel(self)
        self.lbRise.setEnabled(False)
        self.lbRise.setGeometry(QtCore.QRect(30, 130, 31, 16))
        self.lbRise.setObjectName("lbRise")
        self.sbRise = QtWidgets.QDoubleSpinBox(self)
        self.sbRise.setEnabled(False)
        self.sbRise.setGeometry(QtCore.QRect(70, 130, 51, 23))
        self.sbRise.setAlignment(QtCore.Qt.AlignRight|QtCore.Qt.AlignTrailing|QtCore.Qt.AlignVCenter)
        self.sbRise.setMinimum(min_val)
        self.sbRise.setMaximum(max_val)
        self.sbRise.setSingleStep(increment)
        self.sbRise.setValue(startTime)
        self.sbRise.setObjectName("sbRise")
        self.lbWave = QtWidgets.QLabel(self)
        self.lbWave.setEnabled(False)
        self.lbWave.setGeometry(QtCore.QRect(130, 130, 41, 16))
        self.lbWave.setObjectName("lbWave")
        self.sbWave = QtWidgets.QDoubleSpinBox(self)
        self.sbWave.setEnabled(False)
        self.sbWave.setGeometry(QtCore.QRect(180, 130, 41, 23))
        self.sbWave.setAlignment(QtCore.Qt.AlignRight|QtCore.Qt.AlignTrailing|QtCore.Qt.AlignVCenter)
        self.sbWave.setMinimum(min_val)
        self.sbWave.setMaximum(max_val)
        self.sbWave.setSingleStep(increment)
        self.sbWave.setValue(startTime)
        self.sbWave.setObjectName("sbWave")
        self.lbExponent = QtWidgets.QLabel(self)
        self.lbExponent.setEnabled(False)
        self.lbExponent.setGeometry(QtCore.QRect(240, 130, 71, 16))
        self.lbExponent.setObjectName("lbExponent")
        self.sbExponent = QtWidgets.QDoubleSpinBox(self)
        self.sbExponent.setEnabled(False)
        self.sbExponent.setGeometry(QtCore.QRect(310, 130, 51, 23))
        self.sbExponent.setAlignment(QtCore.Qt.AlignRight|QtCore.Qt.AlignTrailing|QtCore.Qt.AlignVCenter)
        self.sbExponent.setMinimum(-10)
        self.sbExponent.setMaximum(10)
        self.sbExponent.setSingleStep(0.1)
        self.sbExponent.setValue(1)
        self.sbExponent.setObjectName("sbExponent")
        self.bbOkCancel = QtWidgets.QDialogButtonBox(self)
        self.bbOkCancel.setGeometry(QtCore.QRect(100, 170, 166, 24))
        self.bbOkCancel.setStandardButtons(QtWidgets.QDialogButtonBox.Cancel|QtWidgets.QDialogButtonBox.Ok)
        self.bbOkCancel.setCenterButtons(False)
        self.bbOkCancel.setObjectName("bbOkCancel")

        self.retranslateUi(self)
        self.bbOkCancel.accepted.connect(self.update)
        self.bbOkCancel.rejected.connect(self.close)
        self.cbRampType.currentIndexChanged.connect(lambda x:self.typeChanged(x))
        QtCore.QMetaObject.connectSlotsByName(self)
        
        self.populate()

    def retranslateUi(self, analogDialog):
        _translate = QtCore.QCoreApplication.translate
        analogDialog.setWindowTitle(_translate("analogDialog", "Form"))
        self.lbChannel.setText(_translate("analogDialog", self.label))
        self.lbStartTime.setText(_translate("analogDialog", "Start Time (us):"))
        self.lbDuration.setText(_translate("analogDialog", "Duration (us):"))
        self.lbInitialValue.setText(_translate("analogDialog", "Initial Value:"))
        self.lbFinalValue.setText(_translate("analogDialog", "Final Value:"))
        self.cbRampType.setItemText(0, _translate("analogDialog", "Constant"))
        self.cbRampType.setItemText(1, _translate("analogDialog", "Pulse"))
        self.cbRampType.setItemText(2, _translate("analogDialog", "Linear"))
        self.cbRampType.setItemText(3, _translate("analogDialog", "Exponential"))
        self.cbRampType.setItemText(4, _translate("analogDialog", "Lorentzian"))
        self.lbRise.setText(_translate("analogDialog", "Rise:"))
        self.lbWave.setText(_translate("analogDialog", "Wave:"))
        self.lbExponent.setText(_translate("analogDialog", "Exponent:"))

    def update(self):
        i = self.cbRampType.currentIndex()        

        startTime = self.startTime
        duration = self.sbDuration.value()

        if startTime + duration > self.parent.parent.Module.sbStartTime.value() + self.parent.parent.Module.sbDuration.value():
            duration =  self.parent.parent.Module.sbStartTime.value() + self.parent.parent.Module.sbDuration.value() - startTime       
            self.sbDuration.setValue(duration)

        if i == 0:
            initialValue = self.sbInitialValue.value()
            event = Constant(startTime,duration,initialValue)
        elif i == 1:
            initialValue = self.sbInitialValue.value()
            Length = self.sbFinalValue.value()
            event = Pulse(startTime,duration,initialValue,Length)
        elif i == 2:
            initialValue = self.sbInitialValue.value()
            finalValue = self.sbFinalValue.value()
            event = Linear(startTime,duration,initialValue,finalValue)
        elif i == 3:
            initialValue = self.sbInitialValue.value()
            finalValue = self.sbFinalValue.value()
            Amplitude = self.sbRise.value()
            event = Exponential(startTime,duration,initialValue,finalValue,Amplitude)
        else:
            initialValue = self.sbInitialValue.value()
            finalValue = self.sbFinalValue.value()
            riseTime = self.sbRise.value()
            wave = self.sbWave.value()
            exponent = self.sbExponent.value()
            event = Lorentzian(startTime,duration,initialValue,finalValue,riseTime,wave,exponent)

        self.parent.setEvent(event)
        self.close()
    
        self.parent.parent.redoLayout()
        
    def typeChanged(self, i):
        if i == 0:
            self.lbFinalValue.setEnabled(False)
            self.sbFinalValue.setEnabled(False)
            self.lbRise.setEnabled(False)
            self.sbRise.setEnabled(False)
            self.lbWave.setEnabled(False)
            self.sbWave.setEnabled(False)
            self.lbExponent.setEnabled(False)
            self.sbExponent.setEnabled(False)
        elif i == 1:
            self.lbFinalValue.setEnabled(True)
            self.lbFinalValue.setText("Length")
            self.sbFinalValue.setEnabled(True)
            self.lbRise.setEnabled(True)
            self.sbRise.setEnabled(True)
            self.lbWave.setEnabled(False)
            self.sbWave.setEnabled(False)
            self.lbExponent.setEnabled(False)
            self.sbExponent.setEnabled(False)
        elif i == 2:
            self.lbFinalValue.setEnabled(True)
            self.lbFinalValue.setText("Final Value")
            self.sbFinalValue.setEnabled(True)
            self.lbRise.setEnabled(False)
            self.sbRise.setEnabled(False)
            self.lbWave.setEnabled(False)
            self.sbWave.setEnabled(False)
            self.lbExponent.setEnabled(False)
            self.sbExponent.setEnabled(False)
        elif i == 3:
            self.lbFinalValue.setEnabled(True)
            self.lbFinalValue.setText("Final Value")
            self.sbFinalValue.setEnabled(True)
            self.lbRise.setEnabled(True)
            self.lbRise.setText("Amplitude")
            self.sbRise.setEnabled(True)
            self.lbWave.setEnabled(False)
            self.sbWave.setEnabled(False)
            self.lbExponent.setEnabled(False)
            self.sbExponent.setEnabled(False)
        else:
            self.lbFinalValue.setEnabled(True)
            self.lbFinalValue.setText("Final Value")
            self.sbFinalValue.setEnabled(True)
            self.lbRise.setEnabled(True)
            self.lbRise.setText("Rise")
            self.sbRise.setEnabled(True)
            self.lbWave.setEnabled(True)
            self.sbWave.setEnabled(True)
            self.lbExponent.setEnabled(True)
            self.sbExponent.setEnabled(True)
            
    def populate(self):
        if self.maybeEvent.is_just():
            event = self.maybeEvent.value()
            self.sbStartTime.setValue(event.startTime)
            self.sbDuration.setValue(event.Duration)
            self.sbInitialValue.setValue(event.InitialValue)
            if isinstance(event,Constant):
                self.cbRampType.setCurrentIndex(0)
            elif isinstance(event,Pulse):
                self.cbRampType.setCurrentIndex(1)
                self.sbFinalValue.setValue(event.Length)
            elif isinstance(event,Linear):
                self.cbRampType.setCurrentIndex(2)
                self.sbFinalValue.setValue(event.FinalValue)
            elif isinstance(event,Exponential):
                self.cbRampType.setCurrentIndex(3)
                self.sbFinalValue.setValue(event.FinalValue)
                self.sbRise.setValue(event.Amplitude)
            elif isinstance(event,Lorentzian):
                self.cbRampType.setCurrentIndex(4)
                self.sbFinalValue.setValue(event.FinalValue)
                self.sbRise.setValue(event.riseTime)
                self.sbWave.setValue(event.waveTime)
                self.sbExponent.setValue(event.Exponent)
            else:
                pass                