# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'moduleAnalogLine.ui'
#
# Created by: PyQt5 UI code generator 5.9.2
#
# WARNING! All changes made in this file will be lost!

from PyQt5 import QtCore, QtGui, QtWidgets

from Either import *
from Parsers import *

from dataTypes import *

from DAQ import DAQ, daq

class networkDDSLine(QtWidgets.QWidget):
    
    frequencyChanged = QtCore.pyqtSignal(int, int, name = "frequencyChanged")
    amplitudeChanged = QtCore.pyqtSignal(int, int, name = "amplitudeChanged")
    
    def __init__(self, channel,subchannel,label,parent = None):
        super(networkDDSLine,self).__init__(parent)

        self.channel = channel
        self.subchannel = subchannel
        self.label = label
        
        self.parent = parent

        self.freq_min_val = daq.lines[self.channel].freq_min
        self.freq_max_val = daq.lines[self.channel].freq_max
        self.freq_increment = daq.lines[self.channel].freq_increment
        self.freq_default = daq.lines[self.channel].freq_default
        
        self.amp_min_val = daq.lines[self.channel].amp_min
        self.amp_max_val = daq.lines[self.channel].amp_max
        self.amp_increment = daq.lines[self.channel].amp_increment
        self.amp_default = daq.lines[self.channel].amp_default

        self.setObjectName("NetworkDDSLine")
        self.resize(400, 20)
        self.lbChannel = QtWidgets.QLabel(self)
        self.lbChannel.setGeometry(QtCore.QRect(0, 0, 80, 20))
        self.lbChannel.setText(self.label)
        self.lbChannel.setObjectName("lbChannel")
        self.sbAmplitude = QtWidgets.QSpinBox(self)
        self.sbAmplitude.setGeometry(QtCore.QRect(90, 0, 100, 20))
        self.sbAmplitude.setAlignment(QtCore.Qt.AlignRight|QtCore.Qt.AlignTrailing|QtCore.Qt.AlignVCenter)
        self.sbAmplitude.setMinimum(self.amp_min_val)
        self.sbAmplitude.setMaximum(self.amp_max_val)
        self.sbAmplitude.setSingleStep(self.amp_increment)
        self.sbAmplitude.setProperty("value", self.amp_default)
        self.sbAmplitude.setObjectName("sbAmplitude")
        self.lbAmplitudeUnits = QtWidgets.QLabel(self)
        self.lbAmplitudeUnits.setGeometry(QtCore.QRect(200, 0, 30, 20))
        self.lbAmplitudeUnits.setText("arb.")
        self.lbAmplitudeUnits.setObjectName("lbAmplitudeUnits")
        self.sbFrequency = QtWidgets.QSpinBox(self)
        self.sbFrequency.setGeometry(QtCore.QRect(240, 0, 100, 20))
        self.sbFrequency.setAlignment(QtCore.Qt.AlignRight|QtCore.Qt.AlignTrailing|QtCore.Qt.AlignVCenter)
        self.sbFrequency.setMinimum(self.freq_min_val)
        self.sbFrequency.setMaximum(self.freq_max_val)
        self.sbFrequency.setSingleStep(self.freq_increment)
        self.sbFrequency.setProperty("value", self.freq_default)
        self.sbFrequency.setObjectName("sbFrequency")
        self.lbFrequencyUnits = QtWidgets.QLabel(self)
        self.lbFrequencyUnits.setGeometry(QtCore.QRect(350,0,30,20))
        self.lbFrequencyUnits.setText("kHz")
        self.lbFrequencyUnits.setObjectName("lbFrequencyUnits")

        self.sbFrequency.valueChanged.connect(self.changeFrequency)
        self.sbAmplitude.valueChanged.connect(self.changeAmplitude)
        QtCore.QMetaObject.connectSlotsByName(self)
        
    def getFrequency(self):
        return self.sbFrequency.value()

    def setFrequency(self,value):
        self.sbFrequency.setValue(value)
        
    def getAmplitude(self):
        return self.sbAmplitude.value()
        
    def setAmplitude(self,value):
        self.sbAmplitude.setValue(value)
        
    def changeFrequency(self):
        self.frequencyChanged.emit(self.subchannel,self.sbFrequency.value())
        
    def changeAmplitude(self):
        self.amplitudeChanged.emit(self.subchannel,self.sbAmplitude.value())
        
class networkDDS(QtWidgets.QWidget):
        
    frequencyChanged = QtCore.pyqtSignal(int, int, name = "frequencyChanged")
    amplitudeChanged = QtCore.pyqtSignal(int, int, name = "amplitudeChanged")

    def __init__(self, channel, labels, parent = None):
        super(networkDDS,self).__init__(parent)
        
        self.channel = channel
        self.labels = labels
        
        self.parent = parent

        self.channels = {}

        self.cursor = 0

        self.freq_min_val = daq.lines[self.channel].freq_min
        self.freq_max_val = daq.lines[self.channel].freq_max
        self.freq_increment = daq.lines[self.channel].freq_increment
        self.freq_default = daq.lines[self.channel].freq_default
        
        self.amp_min_val = daq.lines[self.channel].amp_min
        self.amp_max_val = daq.lines[self.channel].amp_max
        self.amp_increment = daq.lines[self.channel].amp_increment
        self.amp_default = daq.lines[self.channel].amp_default

        self.setObjectName("NetworkDDS")
        self.resize(400, 80)

        for ii in range(channelsPerDDS):
            self.channels[ii] = networkDDSLine(self.channel,ii,self.labels[ii],self)
            self.channels[ii].setGeometry(0,self.cursor,400,20)
            self.channels[ii].setObjectName("NetworkDDSLine"+str(ii))
            self.channels[ii].frequencyChanged.connect(self.changeFrequency)
            self.channels[ii].amplitudeChanged.connect(self.changeAmplitude)
            
            self.cursor += 20

        self.retranslateUi(self)
        QtCore.QMetaObject.connectSlotsByName(self)

    def retranslateUi(self, fNetworkDialogLine):
        _translate = QtCore.QCoreApplication.translate
        fNetworkDialogLine.setWindowTitle(_translate("fNetworkDDS", "NetworkDDS"))

    def getFrequency(self,subchannel):
        return self.channels[subchannel].getFrequency()
        
    def setFrequency(self,subchannel,value):
        self.channels[subchannel].setFrequency(value)
        
    def setAmplitude(self,subchannel,value):
        self.channels[subchannel].setAmplitude(value)
        
    def changeFrequency(self,subchannel):
        val = self.channels[subchannel].sbFrequency.value()
        if val < self.freq_min_val:
            val = self.freq_min_val
        elif val > self.freq_max_val:
            val = self.freq_max_val
                
        self.frequencyChanged.emit(subchannel,val)

    def changeAmplitude(self,subchannel):
        val = self.channels[subchannel].sbAmplitude.value()
        if val < self.amp_min_val:
            val = self.amp_min_val
        elif val > self.amp_max_val:
            val = self.amp_max_val

        self.amplitudeChanged.emit(subchannel,val) 
