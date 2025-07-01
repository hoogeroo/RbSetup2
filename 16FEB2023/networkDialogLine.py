# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'moduleAnalogLine.ui'
#
# Created by: PyQt5 UI code generator 5.9.2
#
# WARNING! All changes made in this file will be lost!

from PyQt5 import QtCore, QtGui, QtWidgets

from Either import *
from Parsers import *

from DAQ import DAQ, daq

from dataTypes import *

class networkDialogLine(QtWidgets.QWidget):
        
    valueChanged = QtCore.pyqtSignal(int, int, float, name="valueChanged")

    def __init__(self, channel, parent = None):
        super(networkDialogLine,self).__init__(parent)
        
        self.channel = channel
        
        self.parent = parent

        self.freq_min_val = daq.lines[self.channel].freq_min
        self.freq_max_val = daq.lines[self.channel].freq_max
        self.freq_increment = daq.lines[self.channel].freq_increment
        self.freq_default = daq.lines[self.channel].freq_default
        
        self.amp_min_val = daq.lines[self.channel].amp_min
        self.amp_max_val = daq.lines[self.channel].amp_max
        self.amp_increment = daq.lines[self.channel].amp_increment
        self.amp_default = daq.lines[self.channel].amp_default
        
        self.chan0 = daq.lines[self.channel].labels[0]
        self.chan1 = daq.lines[self.channel].labels[1]
        self.chan2 = daq.lines[self.channel].labels[2]
        self.chan3 = daq.lines[self.channel].labels[3]
 
        self.left = 50
        self.width = 30

        self.setObjectName("NetworkDialogLine")
        self.resize(300, 20)
        self.cbChannel = QtWidgets.QComboBox(self)
        self.cbChannel.setGeometry(QtCore.QRect(0, 0, 100, 20))
        self.cbChannel.setObjectName("cbChannel")
        self.cbFunction = QtWidgets.QComboBox(self)
        self.cbFunction.setGeometry(QtCore.QRect(100, 0, 100, 20))
        self.cbFunction.setObjectName("cbFunction")
        self.sbAmplitude = QtWidgets.QSpinBox(self)
        self.sbAmplitude.setGeometry(QtCore.QRect(200, 0, 100, 20))
        self.sbAmplitude.setMinimum(self.amp_min_val)
        self.sbAmplitude.setMaximum(self.amp_max_val)
        self.sbAmplitude.setSingleStep(self.amp_increment)
        self.sbAmplitude.setProperty("value", self.amp_default)
        self.sbAmplitude.setObjectName("sbAmplitude")
        self.sbFrequency = QtWidgets.QSpinBox(self)
        self.sbFrequency.setGeometry(QtCore.QRect(200, 0, 100, 20))
        self.sbFrequency.setMinimum(self.freq_min_val)
        self.sbFrequency.setMaximum(self.freq_max_val)
        self.sbFrequency.setSingleStep(self.freq_increment)
        self.sbFrequency.setProperty("value", self.freq_default)
        self.sbFrequency.setObjectName("sbFrequency")
        self.lbUnits = QtWidgets.QLabel(self)
        self.lbUnits.setGeometry(QtCore.QRect(305,0,30,20))
        self.lbUnits.setObjectName("lbUnits")
        
        self.cbChannel.insertItem(0,self.chan0)
        self.cbChannel.insertItem(1,self.chan1)
        self.cbChannel.insertItem(2,self.chan2)
        self.cbChannel.insertItem(3,self.chan3)
        
        self.cbFunction.insertItem(0,"Frequency")
        self.cbFunction.insertItem(1,"Amplitude")
        
        self.sbAmplitude.hide()

        self.retranslateUi(self)
        self.cbFunction.currentIndexChanged.connect(lambda item: self.chooseFunction(item))
        self.sbFrequency.valueChanged.connect(self.changeValue)
        self.sbAmplitude.valueChanged.connect(self.changeValue)
        QtCore.QMetaObject.connectSlotsByName(self)

    def retranslateUi(self, fNetworkDialogLine):
        _translate = QtCore.QCoreApplication.translate
        fNetworkDialogLine.setWindowTitle(_translate("fNetworkDialogLine", "Form"))
        self.lbUnits.setText(_translate("fNetorkDialogLine", "MHz"))
        
    def changeValue(self,value):
        if self.cbFunction.currentIndex() == 0:
            val = self.sbFrequency.value()
            if val < self.freq_min_val:
                val = self.freq_min_val
            elif val > self.freq_max_val:
                val = self.freq_max_val
        else:
            val = self.sbAmplitude.value()
            if val < self.amp_min_val:
                val = self.amp_min_val
            elif val > self.amp_max_val:
                val = self.amp_max_val
                
        self.valueChanged.emit(self.cbChannel.currentIndex(),self.cbFunction.currentIndex(),val)
                
    def chooseFunction(self, item):
        if item == 0:
            self.sbAmplitude.hide()
            self.sbFrequency.show()
            self.lbUnits.setText("kHz")
        else: # item == 1
            self.sbAmplitude.show()
            self.sbFrequency.hide()
            self.lbUnits.setText("uV")
    
    def populateEvents(self, events):
        
        self.pbModuleElements[0].setEvent(events.pop(0))
        while events:
            self.addEvent()
            self.pbModuleElements[self.num_moduleElements-1].setEvent(events.pop(0))
            
        self.redoLayout()
    
    def convertToSequence(self):
        
        sequence = []
        
        for ii in range(self.num_moduleElements):
            event = self.pbModuleElements[ii].getEvent()
            if event.is_just():
                value = event.value()
                event_list = value.createList()
                sequence.append(event_list)
        
        number = self.getChannelNumber()
        
        return number, sequence
    
    def toString(self):
        output = 'A'+' '+str(self.getChannelNumber())
        
        for ii in range(self.num_moduleElements):
            event = self.pbModuleElements[ii].getEvent()
            if event.is_just():
                output += ' '
                output += event.value().toString()
            
        output += '\n'    
            
        return output 
