# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'networkDialog.ui'
#
# Created by: PyQt5 UI code generator 5.9.2
#
# WARNING! All changes made in this file will be lost!

from PyQt5 import QtCore, QtGui, QtWidgets

from DAQ import DAQ, daq

from dataTypes import *
from networkDialogLine import *

class networkDialog(QtWidgets.QDialog):
    def __init__(self, channelNumber, startTime, duration, maybeEvent, parent = None):
        super(networkDialog,self).__init__(parent)
        
        self.channelNumber = channelNumber
        self.startTime = startTime
        self.duration = duration
        self.maybeEvent = maybeEvent
        
        self.parent = parent
        
        self.label = daq.lines[self.channelNumber].label

        self.width = 410
        self.height = 200

        self.nextLine = 80

        self.setObjectName("networkDialog")
        self.resize(self.width,self.height)
        self.lbStartTime = QtWidgets.QLabel(self)
        self.lbStartTime.setGeometry(QtCore.QRect(10, 10, 100, 20))
        self.lbStartTime.setObjectName("lbStartTime")
        self.sbStartTime = QtWidgets.QSpinBox(self)
        self.sbStartTime.setGeometry(QtCore.QRect(110, 10, 90, 20))
        self.sbStartTime.setAlignment(QtCore.Qt.AlignRight|QtCore.Qt.AlignTrailing|QtCore.Qt.AlignVCenter)
        self.sbStartTime.setMinimum(0)
        self.sbStartTime.setMaximum(maximumStartTime)
        self.sbStartTime.setSingleStep(timeIncrement)
        self.sbStartTime.setValue(startTime)
        self.sbStartTime.setEnabled(False)
        self.sbStartTime.setObjectName("sbStartTime")
        self.lbDuration = QtWidgets.QLabel(self)
        self.lbDuration.setGeometry(QtCore.QRect(210, 10, 100, 20))
        self.lbDuration.setObjectName("lbDuration")
        self.sbDuration = QtWidgets.QSpinBox(self)
        self.sbDuration.setGeometry(QtCore.QRect(310, 10, 90, 20))
        self.sbDuration.setAlignment(QtCore.Qt.AlignRight|QtCore.Qt.AlignTrailing|QtCore.Qt.AlignVCenter)
        self.sbDuration.setMinimum(0)
        self.sbDuration.setMaximum(maximumDuration)
        self.sbDuration.setSingleStep(timeIncrement)
        self.sbDuration.setValue(duration)
        self.sbDuration.setObjectName("sbDuration")
        self.lbChannel = QtWidgets.QLabel(self)
        self.lbChannel.setGeometry(QtCore.QRect(10, 50, 100, 20))
        self.lbChannel.setObjectName("lbChannel")
        self.lbFunction = QtWidgets.QLabel(self)
        self.lbFunction.setGeometry(QtCore.QRect(115, 50, 95, 20))
        self.lbFunction.setObjectName("lbFunction")
        self.lbValue = QtWidgets.QLabel(self)
        self.lbValue.setGeometry(QtCore.QRect(210, 50, 50, 20))
        self.lbValue.setObjectName("lbValue")
        
        self.networkSignal = {}
        self.num_signals = 0
        
        self.networkSignal[self.num_signals] = networkDialogLine(self.channelNumber,self)
        self.networkSignal[self.num_signals].setGeometry(QtCore.QRect(10, self.nextLine, 350, 20))
        self.networkSignal[self.num_signals].setObjectName("networkSignal"+str(self.num_signals))
        
        self.num_signals += 1
        
        self.nextLine += 20
        
        self.pbRemoveLineElement = QtWidgets.QPushButton(self)
        self.pbRemoveLineElement.setGeometry(QtCore.QRect(100,self.nextLine+10,20,20))
        self.pbRemoveLineElement.setObjectName("pbRemoveLineElement")
        self.pbRemoveLineElement.setEnabled(False)
        self.pbAddLineElement = QtWidgets.QPushButton(self)
        self.pbAddLineElement.setGeometry(QtCore.QRect(150,self.nextLine+10,20,20))
        self.pbAddLineElement.setObjectName("pbAddLineElement")

        self.bbOkayCancel = QtWidgets.QDialogButtonBox(self)
        self.bbOkayCancel.setGeometry(QtCore.QRect(30, self.nextLine+60, 166, 20))
        self.bbOkayCancel.setStandardButtons(QtWidgets.QDialogButtonBox.Cancel|QtWidgets.QDialogButtonBox.Ok)
        self.bbOkayCancel.setObjectName("bbOkayCancel")
        
        self.retranslateUi(self)
        self.pbAddLineElement.clicked.connect(self.addLine)
        self.pbRemoveLineElement.clicked.connect(self.removeLine)
        self.bbOkayCancel.accepted.connect(self.update)
        self.bbOkayCancel.rejected.connect(self.close)
        QtCore.QMetaObject.connectSlotsByName(self)
        
        self.populate()

    def retranslateUi(self, networkDialog):
        _translate = QtCore.QCoreApplication.translate
        networkDialog.setWindowTitle(_translate("networkDialog", "Form"))
        self.lbStartTime.setText(_translate("networkDialog", "Start Time (us):"))
        self.lbDuration.setText(_translate("networkDialog", "Duration (us):"))
        self.lbChannel.setText(_translate("networkDialog", "Channel"))
        self.lbFunction.setText(_translate("networkDialog", "Function"))
        self.lbValue.setText(_translate("networkDialog", "Value"))
        self.pbRemoveLineElement.setText(_translate("networkDialog", "-"))
        self.pbAddLineElement.setText(_translate("networkDialog", "+"))
        
    def addLine(self):
        self.networkSignal[self.num_signals] = networkDialogLine(self.channelNumber,self)
        self.networkSignal[self.num_signals].setGeometry(QtCore.QRect(10, self.nextLine, 350, 20))
        self.networkSignal[self.num_signals].setObjectName("networkSignal"+str(self.num_signals))
        self.networkSignal[self.num_signals].show()
        
        self.num_signals += 1
        
        self.nextLine += 20
        
        self.pbRemoveLineElement.setGeometry(QtCore.QRect(100,self.nextLine+10,20,20))
        self.pbRemoveLineElement.setEnabled(True)
        self.pbAddLineElement.setGeometry(QtCore.QRect(150,self.nextLine+10,20,20))

        self.bbOkayCancel.setGeometry(QtCore.QRect(30, self.nextLine+60, 166, 20))
        
        self.height += 20
        
        self.resize(self.width,self.height)

    def removeLine(self):
        self.num_signals -= 1

        self.networkSignal[self.num_signals].hide()
        self.networkSignal[self.num_signals].setParent(None)
        del self.networkSignal[self.num_signals]
        
        self.nextLine -= 20
        
        self.pbRemoveLineElement.setGeometry(QtCore.QRect(100,self.nextLine+10,20,20))
        if self.num_signals < 2:
            self.pbRemoveLineElement.setEnabled(False)
        self.pbAddLineElement.setGeometry(QtCore.QRect(150,self.nextLine+10,20,20))

        self.bbOkayCancel.setGeometry(QtCore.QRect(30, self.nextLine+60, 166, 20))       
       
        self.height -= 20
        
        self.resize(self.width,self.height)
        
    def update(self):
        operations = []

        startTime = self.startTime
        duration = self.sbDuration.value()

        for ii in range(self.num_signals):
            channel = self.networkSignal[ii].cbChannel.currentIndex()
            function = self.networkSignal[ii].cbFunction.currentIndex()
            
            if function == 0:
                value = self.networkSignal[ii].sbFrequency.value()
            else:
                value = self.networkSignal[ii].sbAmplitude.value()
            
            operations.append(Operation(channel,function,value))
            
        event = Network(startTime,duration,operations)
        self.parent.setEvent(event)
        self.close()
        
        self.parent.parent.redoLayout()
    
    def populate(self):
        if self.maybeEvent.is_just():
            event = self.maybeEvent.value()
            self.sbStartTime.setValue(event.startTime)
            self.sbDuration.setValue(event.Duration)
            
            operations = event.operations
            
            for ii in range(len(operations)):
                operation = operations[ii]
                
                if ii > 0:
                    self.addLine()
                
                self.networkSignal[ii].cbChannel.setCurrentIndex(operation.channel)
                self.networkSignal[ii].cbFunction.setCurrentIndex(operation.function)
            
                if operation.function == 0:
                    self.networkSignal[ii].sbFrequency.setValue(operation.value)
                else:
                    self.networkSignal[ii].sbAmplitude.setValue(operation.value)
                